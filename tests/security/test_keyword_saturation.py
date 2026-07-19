"""ATK-MEM-03 regression: per-document keyword-score saturation.

A single document must not be able to dominate keyword ranking by
* flooding a query term (unbounded raw term-frequency), or
* stacking the query into many headings (unbounded +3.0 bonus).

Both vectors were unbounded in ``_keyword_score``:
  * ``score += count * 0.5 * (1 + position_weight)`` with raw ``count`` (kb_query.py:463)
  * ``score += 3.0`` per query-bearing heading, no cap (kb_query.py:474-476)

These tests are RED on the unbounded scorer (a term-flood attacker outranks a
legitimate title match; a flooded doc scores in the hundreds) and GREEN once TF
is BM25-saturated and heading matches are capped.
"""

from src.tools.kb_query import KnowledgeBaseQuery
from tests.security.conftest import plant_document

QUERY = "quantization"


def _kb(tmp_path):
    kb = tmp_path / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    return kb


def test_term_flood_cannot_outrank_title_match(tmp_path):
    """A body that repeats the query 500x must not beat a genuine title match."""
    kb = _kb(tmp_path)
    plant_document(
        kb,
        "concepts",
        "legit.md",
        "# Quantization Guide\n\nA short honest overview of quantization.\n",
        frontmatter={"title": "Quantization Guide", "trust_tier": "verified"},
    )
    flood = " ".join([QUERY] * 500)
    plant_document(
        kb,
        "references",
        "attacker.md",
        f"# Unrelated Title\n\n{flood}\n",
        frontmatter={"title": "Unrelated Title", "trust_tier": "verified"},
    )

    result = KnowledgeBaseQuery(str(kb)).query(QUERY, max_results=10)
    order = [r["file"] for r in result["results"]]
    assert any("legit.md" in f for f in order), order
    legit_i = next(i for i, f in enumerate(order) if "legit.md" in f)
    atk_i = next((i for i, f in enumerate(order) if "attacker.md" in f), len(order))
    assert legit_i < atk_i, f"term-flood attacker outranked legit title match: {order}"


def test_keyword_score_is_bounded_under_repetition(tmp_path):
    """A pure body flood must stay below the legitimate title-match weight (10.0)."""
    kbq = KnowledgeBaseQuery(str(_kb(tmp_path)))
    flood = " ".join([QUERY] * 1000)
    score = kbq._keyword_score(QUERY, flood, "attacker.md")
    assert score < 10.0, f"unbounded TF: {score}"


def test_heading_flood_is_capped(tmp_path):
    """100 query-bearing headings must not stack unbounded +3.0 bonuses."""
    kbq = KnowledgeBaseQuery(str(_kb(tmp_path)))
    content = "# Overview\n\n" + "\n".join(f"## {QUERY} note {i}" for i in range(100))
    score = kbq._keyword_score(QUERY, content, "attacker.md")
    assert score < 20.0, f"unbounded heading bonus: {score}"


def test_single_occurrence_scoring_is_preserved(tmp_path):
    """Saturation must not change scoring for a single, honest occurrence."""
    kbq = KnowledgeBaseQuery(str(_kb(tmp_path)))
    # One occurrence: BM25 saturation with any k1 returns count unchanged at 1,
    # so an honest single mention scores exactly as before the fix.
    content = "Some prose mentioning quantization once, early on."
    score = kbq._keyword_score(QUERY, content, "doc.md")
    assert score > 0.0
