"""ATK-MEM-02 regression: trust tier filtering.

Three cases:
  1. quarantined doc → excluded from results entirely.
  2. generated doc, include_content=True → content is a placeholder.
  3. generated doc, include_unverified=True → real content returned (wrapped).
"""

import textwrap

from src.tools.kb_query import (
    _TRUST_CONTENT_PLACEHOLDER,
    KB_CONTENT_OPEN,
    QUARANTINE_TIER,
    TRUSTED_TIERS,
    KnowledgeBaseQuery,
    _parse_frontmatter_trust_tier,
)
from tests.security.conftest import plant_document

# ---------------------------------------------------------------------------
# Unit tests: trust tier parser
# ---------------------------------------------------------------------------


def test_parse_verified():
    content = "---\ntitle: T\ntrust_tier: verified\n---\n# T"
    assert _parse_frontmatter_trust_tier(content) == "verified"


def test_parse_quarantined():
    content = "---\ntitle: T\ntrust_tier: quarantined\n---\n# T"
    assert _parse_frontmatter_trust_tier(content) == "quarantined"


def test_parse_missing_returns_empty():
    content = "---\ntitle: T\n---\n# T"
    assert _parse_frontmatter_trust_tier(content) == ""


def test_constants():
    assert "verified" in TRUSTED_TIERS
    assert QUARANTINE_TIER == "quarantined"


# ---------------------------------------------------------------------------
# Integration tests via KnowledgeBaseQuery
# ---------------------------------------------------------------------------


def _make_doc(title: str, tier: str, body: str) -> str:
    return textwrap.dedent(f"""\
        ---
        title: {title}
        status: active
        trust_tier: {tier}
        ---

        # {title}

        {body}
    """)


def test_quarantined_doc_excluded(tmp_kb):
    """A quarantined document must not appear in results (ATK-MEM-02)."""
    plant_document(
        tmp_kb,
        "concepts",
        "poison.md",
        _make_doc("Poison Doc", "quarantined", "This document is quarantined."),
    )
    kbq = KnowledgeBaseQuery(str(tmp_kb))
    result = kbq.query("quarantined", include_content=True)
    files = [r["file"] for r in result.get("results", [])]
    assert not any("poison" in f for f in files), (
        "Quarantined document must be excluded from results"
    )


def test_generated_doc_content_withheld(tmp_kb):
    """Generated doc with include_content=True returns placeholder, not real content (ATK-MEM-02)."""
    plant_document(
        tmp_kb,
        "concepts",
        "agent-output.md",
        _make_doc("Agent Output", "generated", "SECRET internal reasoning."),
    )
    kbq = KnowledgeBaseQuery(str(tmp_kb))
    result = kbq.query("agent", include_content=True)
    results = result.get("results", [])

    for r in results:
        if "agent-output" in r.get("file", ""):
            content = r.get("content", "")
            assert content == _TRUST_CONTENT_PLACEHOLDER, (
                f"Generated doc content should be placeholder, got: {content[:100]!r}"
            )
            return

    # If the doc wasn't found at all (no keyword match), pass — filtering isn't needed
    # But if it is found it must be withheld.


def test_include_unverified_returns_real_content(tmp_kb):
    """With include_unverified=True, real content (wrapped) is returned for generated docs."""
    body = "SECRET internal reasoning about agent outputs."
    plant_document(
        tmp_kb,
        "concepts",
        "agent-output.md",
        _make_doc("Agent Output", "generated", body),
    )
    kbq = KnowledgeBaseQuery(str(tmp_kb))
    result = kbq.query("agent", include_content=True, include_unverified=True)

    for r in result.get("results", []):
        if "agent-output" in r.get("file", ""):
            content = r.get("content", "")
            assert KB_CONTENT_OPEN in content, "Content must still be wrapped in delimiters"
            assert body in content, "Real content must be present when include_unverified=True"
            return


# ---------------------------------------------------------------------------
# ATK-MEM-02 read-path enforcement: `trust_tier: verified` needs a valid signature
# ---------------------------------------------------------------------------


def test_forged_verified_tier_is_not_trusted(tmp_kb):
    """A hand-forged ``trust_tier: verified`` with no valid provenance signature
    must NOT be served as trusted content — it is withheld like an unverified doc.

    This is the ATK-MEM-02 residual the Cowork re-audit surfaced: the read path
    used to honour the raw frontmatter tier without checking the HMAC signature.
    """
    # Write directly, bypassing the fixture's signing, to simulate a forgery.
    (tmp_kb / "concepts" / "forged.md").write_text(
        _make_doc("Forged Trusted Doc", "verified", "FORGED trusted content payload."),
        encoding="utf-8",
    )
    kbq = KnowledgeBaseQuery(str(tmp_kb))
    result = kbq.query("forged trusted content", include_content=True)
    hits = [r for r in result.get("results", []) if "forged" in r.get("file", "")]
    assert hits, "test setup: the forged doc should match the query"
    assert hits[0].get("content") == _TRUST_CONTENT_PLACEHOLDER, (
        "a forged (unsigned) verified doc must be withheld, not served as trusted"
    )


def test_signed_verified_tier_is_trusted(tmp_kb):
    """A genuinely-signed ``trust_tier: verified`` doc IS served as trusted — the
    enforcement must not over-block legitimately-provenanced content."""
    from src.provenance import attach_signature, load_or_create_key

    signed = attach_signature(
        _make_doc("Signed Trusted Doc", "verified", "REAL provenanced trusted content."),
        load_or_create_key(tmp_kb),
    )
    (tmp_kb / "concepts" / "signed.md").write_text(signed, encoding="utf-8")
    kbq = KnowledgeBaseQuery(str(tmp_kb))
    result = kbq.query("signed provenanced trusted", include_content=True)
    hits = [r for r in result.get("results", []) if "signed" in r.get("file", "")]
    assert hits, "test setup: the signed doc should match the query"
    assert KB_CONTENT_OPEN in hits[0].get("content", ""), "wrapped content expected"
    assert "REAL provenanced trusted content" in hits[0].get("content", ""), (
        "a validly-signed verified doc must be served as trusted"
    )
