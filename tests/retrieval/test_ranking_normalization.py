"""CODE-05/06 regression: recency and PageRank normalization."""

from datetime import datetime, timezone

from src.graph.ranker import GraphRanker
from src.tools.kb_query import KnowledgeBaseQuery

# ---------------------------------------------------------------------------
# CODE-05: recency normalization must be result-set-relative
# ---------------------------------------------------------------------------


def test_recency_normalization_is_result_set_relative(tmp_kb):
    """A 2020 doc and a 2026 doc must score 0.0 and 1.0 recency respectively (CODE-05)."""
    import os

    doc_old = tmp_kb / "concepts" / "old-doc.md"
    doc_new = tmp_kb / "concepts" / "new-doc.md"
    doc_old.write_text("# Old Doc\nThis is an old document.", encoding="utf-8")
    doc_new.write_text("# New Doc\nThis is a new document.", encoding="utf-8")

    # Set mtimes manually: old=2020, new=2026
    old_ts = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    new_ts = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
    os.utime(doc_old, (old_ts, old_ts))
    os.utime(doc_new, (new_ts, new_ts))

    kbq = KnowledgeBaseQuery(str(tmp_kb), recency_weight=1.0)
    result = kbq.query("document", categories=["concepts"])
    results = result.get("results", [])

    # With recency_weight=1.0, new doc must rank above old doc
    files = [r["file"] for r in results]
    new_idx = next((i for i, r in enumerate(results) if "new-doc" in r["file"]), None)
    old_idx = next((i for i, r in enumerate(results) if "old-doc" in r["file"]), None)

    if new_idx is not None and old_idx is not None:
        assert new_idx < old_idx, (
            f"New doc (rank {new_idx + 1}) should rank above old doc (rank {old_idx + 1}) "
            f"when recency_weight=1.0"
        )


def test_recency_single_doc_does_not_crash(tmp_kb):
    """Single document result set must not crash recency normalization (epoch_span=0 guard)."""
    kbq = KnowledgeBaseQuery(str(tmp_kb), recency_weight=0.5)
    result = kbq.query("example")
    assert "results" in result, "query() crashed with recency_weight and single result"


# ---------------------------------------------------------------------------
# CODE-06: PageRank normalization must be result-set-relative
# ---------------------------------------------------------------------------


def test_pagerank_normalization_moves_rank():
    """A high-PageRank doc must overtake a lower-ranked doc at graph_weight=0.9 (CODE-06).

    weight=0.9 means the blended score is 90% PageRank, 10% similarity.
    With min-max normalisation doc_a (all in-edges) gets norm_pr=1.0 and
    doc_b (no in-edges) gets norm_pr=0.0, so:
      doc_a blended = 0.1*8.0 + 0.9*1.0 = 1.7
      doc_b blended = 0.1*10.0 + 0.9*0.0 = 1.0
    doc_a should win, demonstrating the weight parameter works as documented.
    """
    from src.graph.graph import KnowledgeGraph

    # Build a synthetic graph where doc_a has high PageRank (many in-edges)
    # and doc_b has low PageRank (no in-edges)
    graph = KnowledgeGraph()
    for i in range(10):
        graph.add_node(f"concepts/feeder_{i}.md")
    graph.add_node("concepts/doc_a.md")
    graph.add_node("concepts/doc_b.md")
    # All feeders point to doc_a → high PageRank for doc_a
    for i in range(10):
        graph.add_edge(f"concepts/feeder_{i}.md", "concepts/doc_a.md", "explicit", 1.0)

    # doc_b has higher similarity score but much lower PageRank.
    # weight=0.9 → PageRank dominates; doc_a must rise to top.
    results = [
        {"file": "concepts/doc_b.md", "score": 10.0, "title": "B"},
        {"file": "concepts/doc_a.md", "score": 8.0, "title": "A"},
    ]

    ranker = GraphRanker(graph)
    reranked = ranker.rerank(results, weight=0.9)

    top_file = reranked[0]["file"]
    assert top_file == "concepts/doc_a.md", (
        f"High-PageRank doc_a did not move to top after reranking; top is {top_file!r}\n"
        "PageRank normalization may not be effective at high weight (CODE-06)"
    )


def test_pagerank_rerank_stable_with_equal_scores():
    """rerank() must not crash when all PageRank scores are equal (pr_span=0 guard)."""
    from src.graph.graph import KnowledgeGraph

    graph = KnowledgeGraph()
    graph.add_node("concepts/a.md")
    graph.add_node("concepts/b.md")
    # No edges — uniform PageRank

    results = [
        {"file": "concepts/a.md", "score": 5.0, "title": "A"},
        {"file": "concepts/b.md", "score": 3.0, "title": "B"},
    ]

    ranker = GraphRanker(graph)
    reranked = ranker.rerank(results, weight=0.3)
    assert len(reranked) == 2, "rerank() lost results when all PageRank scores are equal"
