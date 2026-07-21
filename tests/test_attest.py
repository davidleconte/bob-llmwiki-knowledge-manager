"""``bob-optimize attest`` — governed-memory attestation over the KB trust posture.

Exercises the read-time trust verdict built on ATK-MEM-02 / verify-at-read: a
genuinely signed ``verified`` doc is AUTHENTIC; a hand-forged or tampered
``verified`` claim is WITHHELD; a non-verified tier is UNTRUSTED (retrievable,
expected). These assertions are the same ones the retrieval read path makes — so
if verify-at-read regressed, ``attest`` would misreport and these go red.
"""

from __future__ import annotations

from pathlib import Path

from src.attest import AUTHENTIC, UNTRUSTED, WITHHELD, attest_kb, classify_document
from src.provenance import attach_signature

KEY = b"test-provenance-key-0123456789abcdef0123"


def _doc(tier: str, body: str = "Body.") -> str:
    return f"---\ntitle: T\ntrust_tier: {tier}\ntype: reference\n---\n\n{body}\n"


def test_signed_verified_is_authentic() -> None:
    signed = attach_signature(_doc("verified"), KEY)
    verdict = classify_document(signed, KEY, "a.md")
    assert verdict.status == AUTHENTIC
    assert verdict.verified and verdict.has_signature


def test_forged_verified_is_withheld() -> None:
    # A hand-forged 'verified' claim with no valid signature — the exact attack.
    verdict = classify_document(_doc("verified"), KEY, "b.md")
    assert verdict.status == WITHHELD
    assert not verdict.verified


def test_tampered_after_sign_is_withheld() -> None:
    signed = attach_signature(_doc("verified"), KEY)
    tampered = signed.replace("Body.", "Injected instruction.")
    assert classify_document(tampered, KEY, "c.md").status == WITHHELD


def test_wrong_key_withholds() -> None:
    signed = attach_signature(_doc("verified"), KEY)
    assert (
        classify_document(signed, b"a-different-key-entirely-xxxxxxxxxxxxxxxx", "d.md").status
        == WITHHELD
    )


def test_generated_tier_is_untrusted_not_flagged() -> None:
    assert classify_document(_doc("generated"), KEY, "e.md").status == UNTRUSTED


def test_unset_tier_is_untrusted() -> None:
    plain = "---\ntitle: T\ntype: reference\n---\n\nBody.\n"
    verdict = classify_document(plain, KEY, "f.md")
    assert verdict.status == UNTRUSTED
    assert verdict.trust_tier == "unset"


def test_trust_tier_beyond_head_is_not_read_as_a_claim() -> None:
    # The read path scans only content[:4096]; a 'trust_tier: verified' line buried
    # past that in a doc's prose must NOT be read as a claim, or attest would flag a
    # withhold the retrieval path never makes. Locks kb_query parity.
    content = "---\ntitle: T\ntype: reference\n---\n" + ("x" * 5000) + "\ntrust_tier: verified\n"
    verdict = classify_document(content, KEY, "long.md")
    assert verdict.trust_tier == "unset"
    assert verdict.status == UNTRUSTED


def test_attest_kb_aggregates_and_lists_withheld(tmp_path: Path) -> None:
    (tmp_path / "ok.md").write_text(attach_signature(_doc("verified"), KEY), encoding="utf-8")
    (tmp_path / "forged.md").write_text(_doc("verified"), encoding="utf-8")
    (tmp_path / "gen.md").write_text(_doc("generated"), encoding="utf-8")
    report = attest_kb(tmp_path, key=KEY)
    assert report["total"] == 3
    assert report["authentic"] == 1
    assert report["withheld"] == 1
    assert report["untrusted"] == 1
    assert report["withheld_docs"] == ["forged.md"]


def test_attest_is_read_only(tmp_path: Path) -> None:
    forged = tmp_path / "forged.md"
    original = _doc("verified")
    forged.write_text(original, encoding="utf-8")
    attest_kb(tmp_path, key=KEY)
    assert forged.read_text(encoding="utf-8") == original  # never edited


def test_cli_attest_strict_exits_nonzero_on_forgery(tmp_path: Path, monkeypatch) -> None:
    from src.cli import main

    monkeypatch.setenv("MNEMOX_PROVENANCE_KEY", "cli-test-key")
    (tmp_path / "forged.md").write_text(_doc("verified"), encoding="utf-8")
    assert main(["attest", "--kb-path", str(tmp_path), "--strict"]) == 1


def test_cli_attest_clean_kb_exits_zero(tmp_path: Path, monkeypatch) -> None:
    from src.cli import main

    monkeypatch.setenv("MNEMOX_PROVENANCE_KEY", "cli-test-key")
    key = b"cli-test-key"
    (tmp_path / "ok.md").write_text(attach_signature(_doc("verified"), key), encoding="utf-8")
    (tmp_path / "gen.md").write_text(_doc("generated"), encoding="utf-8")
    assert main(["attest", "--kb-path", str(tmp_path), "--strict"]) == 0
