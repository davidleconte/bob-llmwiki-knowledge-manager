"""D2/MEM-10/11/12: curation — archived tier exclusion + generated→verified promotion.

- ``archived`` docs are excluded from the retrieval set entirely (like quarantined)
  but stay on disk — marketing/process artifacts stop polluting retrieval.
- ``kb-promote`` flips a doc's trust tier, records the promoter, and re-signs
  provenance so the promotion is attestable (a hand-edited tier fails verification).
"""

from __future__ import annotations

from pathlib import Path

from src.cli import main
from src.provenance import (
    attach_signature,
    load_or_create_key,
    promote_document,
    verify_document,
)
from src.tools.kb_query import KnowledgeBaseQuery


def _make_kb(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    return kb


def _doc(title: str, tier: str, body: str) -> str:
    return f"---\ntitle: {title}\ntrust_tier: {tier}\n---\n\n# {title}\n\n{body}\n"


# ---- archived tier exclusion ---- #


def test_archived_tier_excluded_from_retrieval_but_kept_on_disk(tmp_path):
    kb = _make_kb(tmp_path)
    live = kb / "concepts" / "live.md"
    archived = kb / "concepts" / "old.md"
    live.write_text(_doc("Live", "verified", "cache eviction and ttl strategies"), encoding="utf-8")
    archived.write_text(
        _doc("Old", "archived", "cache eviction and ttl strategies"), encoding="utf-8"
    )

    result = KnowledgeBaseQuery(str(kb)).query("cache eviction", include_content=True)
    files = {r["file"] for r in result["results"]}

    assert "concepts/live.md" in files, "verified doc should be retrievable"
    assert "concepts/old.md" not in files, "archived doc must be excluded from retrieval"
    assert archived.exists(), "archived doc must remain on disk"


def test_quarantined_still_excluded(tmp_path):
    """Adding archived must not regress the quarantined exclusion."""
    kb = _make_kb(tmp_path)
    (kb / "concepts" / "q.md").write_text(
        _doc("Q", "quarantined", "cache eviction"), encoding="utf-8"
    )
    result = KnowledgeBaseQuery(str(kb)).query("cache eviction", include_content=True)
    assert all(r["file"] != "concepts/q.md" for r in result["results"])


# ---- generated → verified promotion ---- #


def _signed_generated_doc(key: bytes) -> str:
    raw = (
        "---\ntitle: Finding\nstatus: generated\ntrust_tier: generated\n"
        "generated_by: delegation-pipeline\nsource: delegation-pipeline\n---\n\n"
        "# Finding\n\nA cache eviction insight.\n"
    )
    return attach_signature(raw, key)


def test_promote_resigns_provenance(tmp_path, monkeypatch):
    monkeypatch.delenv("MNEMOX_PROVENANCE_KEY", raising=False)
    key = b"k" * 32
    signed = _signed_generated_doc(key)
    assert verify_document(signed, key)

    promoted = promote_document(signed, "verified", "alice", key)

    assert "trust_tier: verified" in promoted
    assert "promoted_by: alice" in promoted
    assert verify_document(promoted, key), "promoted doc must carry a valid signature"


def test_promote_hand_edited_tier_fails_verification(tmp_path):
    key = b"k" * 32
    promoted = promote_document(_signed_generated_doc(key), "verified", "bob", key)
    # A forged promotion — hand-editing the signed trust_tier field without
    # re-signing — must not verify (trust_tier is covered by the HMAC).
    forged = promoted.replace("trust_tier: verified", "trust_tier: generated")
    assert not verify_document(forged, key)


def test_kb_promote_cli(tmp_path, monkeypatch):
    monkeypatch.delenv("MNEMOX_PROVENANCE_KEY", raising=False)
    root = tmp_path / "repo"
    (root / ".bob").mkdir(parents=True)  # marks the repo root for key resolution
    doc = root / "docs" / "knowledge-base" / "research" / "finding.md"
    doc.parent.mkdir(parents=True)
    key = load_or_create_key(doc)
    doc.write_text(_signed_generated_doc(key), encoding="utf-8")

    rc = main(["kb-promote", str(doc), "--to", "verified", "--by", "carol"])
    assert rc == 0

    promoted = doc.read_text(encoding="utf-8")
    assert "trust_tier: verified" in promoted
    assert "promoted_by: carol" in promoted
    assert verify_document(promoted, key)


def test_kb_promote_cli_missing_doc(tmp_path):
    assert main(["kb-promote", str(tmp_path / "nope.md")]) == 1
