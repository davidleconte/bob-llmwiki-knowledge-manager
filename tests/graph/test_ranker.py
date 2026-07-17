"""Tests for src/graph/ranker.py — GraphRanker."""

from __future__ import annotations

import pytest

from src.graph.graph import KnowledgeGraph
from src.graph.ranker import PAGERANK_SCALE, GraphRanker


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _hub_graph() -> KnowledgeGraph:
    """All spokes point to hub.md — hub has highest PageRank."""
    g = KnowledgeGraph()
    g.add_node("concepts/hub.md", title="Hub Doc", category="concepts")
    for i in range(4):
        spoke = f"guides/spoke-{i}.md"
        g.add_node(spoke, title=f"Spoke {i}", category="guides")
        g.add_edge(spoke, "concepts/hub.md", "explicit", 1.0)
    return g


def _make_result(file: str, score: float) -> dict:
    return {"file": file, "score": score, "title": file}


# --------------------------------------------------------------------------- #
# pagerank_scores
# --------------------------------------------------------------------------- #


class TestPageRankScores:
    def test_returns_dict_for_all_nodes(self):
        g = _hub_graph()
        ranker = GraphRanker(g)
        pr = ranker.pagerank_scores()
        assert set(pr.keys()) == {doc_id for doc_id, _ in g.nodes()}

    def test_cached_on_second_call(self):
        g = _hub_graph()
        ranker = GraphRanker(g)
        pr1 = ranker.pagerank_scores()
        pr2 = ranker.pagerank_scores()
        assert pr1 is pr2  # exact same object (cached)

    def test_hub_has_highest_score(self):
        g = _hub_graph()
        pr = GraphRanker(g).pagerank_scores()
        assert pr["concepts/hub.md"] == max(pr.values())


# --------------------------------------------------------------------------- #
# rerank
# --------------------------------------------------------------------------- #


class TestRerank:
    def test_weight_zero_leaves_scores_unchanged(self):
        g = _hub_graph()
        results = [
            _make_result("concepts/hub.md", 10.0),
            _make_result("guides/spoke-0.md", 8.0),
        ]
        reranked = GraphRanker(g).rerank(results, weight=0.0)
        assert reranked[0]["score"] == pytest.approx(10.0)
        assert reranked[1]["score"] == pytest.approx(8.0)

    def test_weight_zero_returns_same_order(self):
        g = _hub_graph()
        results = [_make_result("guides/spoke-0.md", 5.0), _make_result("concepts/hub.md", 3.0)]
        reranked = GraphRanker(g).rerank(results, weight=0.0)
        assert reranked[0]["file"] == "guides/spoke-0.md"

    def test_hub_doc_rises_with_positive_weight(self):
        """Hub doc should be promoted when weight > 0."""
        g = _hub_graph()
        # spoke-0 has higher similarity but hub has higher PageRank
        results = [
            _make_result("guides/spoke-0.md", 10.0),
            _make_result("concepts/hub.md", 5.0),
        ]
        # At weight=0.0 spoke wins; at high weight hub should overtake
        reranked = GraphRanker(g).rerank(results, weight=0.9)
        scores = {r["file"]: r["score"] for r in reranked}
        # Hub has 4 inbound edges → much higher PR than spokes with 0
        assert scores["concepts/hub.md"] > scores["guides/spoke-0.md"]

    def test_graph_score_field_added(self):
        g = _hub_graph()
        results = [_make_result("concepts/hub.md", 5.0)]
        reranked = GraphRanker(g).rerank(results, weight=0.3)
        assert "graph_score" in reranked[0]
        assert reranked[0]["graph_score"] >= 0.0

    def test_results_sorted_descending(self):
        g = _hub_graph()
        # weight > 0 so rerank actually runs the sort
        results = [
            _make_result("guides/spoke-0.md", 2.0),
            _make_result("concepts/hub.md", 1.0),
            _make_result("guides/spoke-1.md", 3.0),
        ]
        reranked = GraphRanker(g).rerank(results, weight=0.01)
        scores = [r["score"] for r in reranked]
        assert scores == sorted(scores, reverse=True)

    def test_empty_results_returns_empty(self):
        g = _hub_graph()
        assert GraphRanker(g).rerank([], weight=0.5) == []

    def test_doc_not_in_graph_gets_zero_pr(self):
        g = _hub_graph()
        results = [_make_result("research/unknown.md", 5.0)]
        reranked = GraphRanker(g).rerank(results, weight=0.5)
        assert reranked[0]["graph_score"] == pytest.approx(0.0)

    def test_chunk_suffix_stripped_from_file_key(self):
        """File keys with #slug suffix must still match graph nodes."""
        g = KnowledgeGraph()
        g.add_node("concepts/a.md", title="A")
        g.add_node("concepts/b.md", title="B")
        g.add_edge("concepts/b.md", "concepts/a.md", "explicit", 1.0)

        results = [_make_result("concepts/a.md#section-one", 5.0)]
        reranked = GraphRanker(g).rerank(results, weight=0.3)
        # a.md has 1 inbound edge → positive PR; graph_score should be > 0
        assert reranked[0]["graph_score"] > 0.0


# --------------------------------------------------------------------------- #
# neighbourhood_context
# --------------------------------------------------------------------------- #


class TestNeighbourhoodContext:
    def test_direct_neighbours_returned(self):
        g = _hub_graph()
        ranker = GraphRanker(g)
        ctx = ranker.neighbourhood_context("concepts/hub.md", depth=1)
        # No outbound from hub; hub only has inbound
        assert ctx == []

    def test_spoke_has_hub_as_neighbour(self):
        g = _hub_graph()
        ctx = GraphRanker(g).neighbourhood_context("guides/spoke-0.md", depth=1)
        assert len(ctx) == 1
        assert ctx[0]["doc_id"] == "concepts/hub.md"
        assert ctx[0]["distance"] == 1
        assert ctx[0]["edge_type"] == "explicit"

    def test_depth_2_includes_transitive(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md", title="A", category="concepts")
        g.add_node("concepts/b.md", title="B", category="concepts")
        g.add_node("guides/c.md", title="C", category="guides")
        g.add_edge("concepts/a.md", "concepts/b.md", "explicit", 1.0)
        g.add_edge("concepts/b.md", "guides/c.md", "explicit", 1.0)

        ctx = GraphRanker(g).neighbourhood_context("concepts/a.md", depth=2)
        ids = [item["doc_id"] for item in ctx]
        assert "concepts/b.md" in ids
        assert "guides/c.md" in ids

    def test_output_sorted_by_distance_then_id(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("guides/z.md")
        g.add_node("guides/a.md")
        g.add_edge("concepts/a.md", "guides/z.md", "explicit", 1.0)
        g.add_edge("concepts/a.md", "guides/a.md", "explicit", 1.0)

        ctx = GraphRanker(g).neighbourhood_context("concepts/a.md", depth=1)
        ids = [item["doc_id"] for item in ctx]
        assert ids == sorted(ids)  # alphabetical within same distance

    def test_title_populated_from_graph(self):
        g = _hub_graph()
        ctx = GraphRanker(g).neighbourhood_context("guides/spoke-0.md", depth=1)
        assert ctx[0]["title"] == "Hub Doc"
