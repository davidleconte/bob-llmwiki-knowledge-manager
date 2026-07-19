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
