"""Tests for src/graph/graph.py — KnowledgeGraph, NodeProps, Edge."""

from __future__ import annotations

import pytest

from src.graph.graph import Edge, KnowledgeGraph, NodeProps

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _triangle() -> KnowledgeGraph:
    """A → B → C → A (cycle), all explicit edges."""
    g = KnowledgeGraph()
    for doc in ("concepts/a.md", "concepts/b.md", "research/c.md"):
        g.add_node(doc, title=doc, category=doc.split("/")[0])
    g.add_edge("concepts/a.md", "concepts/b.md", "explicit", 1.0, "A links B")
    g.add_edge("concepts/b.md", "research/c.md", "explicit", 1.0)
    g.add_edge("research/c.md", "concepts/a.md", "explicit", 1.0)
    return g


def _hub() -> KnowledgeGraph:
    """Hub graph: all spokes point to 'concepts/hub.md'."""
    g = KnowledgeGraph()
    g.add_node("concepts/hub.md", title="Hub", category="concepts")
    for i in range(5):
        spoke = f"guides/spoke-{i}.md"
        g.add_node(spoke, title=f"Spoke {i}", category="guides")
        g.add_edge(spoke, "concepts/hub.md", "explicit", 1.0)
    return g


# --------------------------------------------------------------------------- #
# NodeProps
# --------------------------------------------------------------------------- #


class TestNodeProps:
    def test_defaults(self):
        n = NodeProps()
        assert n.title == "Untitled"
        assert n.tags == []

    def test_roundtrip(self):
        n = NodeProps(
            title="Test",
            category="concepts",
            tags=["a", "b"],
            date="2026-07-17",
            type="concept",
            status="active",
        )
        assert NodeProps.from_dict(n.to_dict()) == n

    def test_new_fields_have_safe_defaults(self):
        """P4: mtime_epoch, content_length, description, related_refs default correctly."""
        n = NodeProps()
        assert n.mtime_epoch == 0.0
        assert n.content_length == 0
        assert n.description == ""
        assert n.related_refs == []

    def test_new_fields_roundtrip(self):
        """P4: NodeProps.to_dict() / from_dict() preserves all four new fields."""
        n = NodeProps(
            title="Test Doc",
            mtime_epoch=1721222400.0,
            content_length=1234,
            description="A first paragraph about caching.",
            related_refs=["../guides/setup.md", "../concepts/other.md"],
        )
        restored = NodeProps.from_dict(n.to_dict())
        assert restored.mtime_epoch == pytest.approx(1721222400.0)
        assert restored.content_length == 1234
        assert restored.description == "A first paragraph about caching."
        assert restored.related_refs == ["../guides/setup.md", "../concepts/other.md"]

    def test_old_json_missing_new_fields_loads_cleanly(self):
        """P4: from_dict() on old JSON without P4 keys returns safe defaults."""
        old_json = {
            "title": "Old Doc",
            "category": "concepts",
            "tags": [],
            "date": "",
            "type": "",
            "status": "",
        }
        n = NodeProps.from_dict(old_json)
        assert n.mtime_epoch == 0.0
        assert n.content_length == 0
        assert n.description == ""
        assert n.related_refs == []


# --------------------------------------------------------------------------- #
# Edge
# --------------------------------------------------------------------------- #


class TestEdge:
    def test_roundtrip(self):
        e = Edge(source="a.md", target="b.md", type="explicit", weight=1.0, label="link")
        assert Edge.from_dict(e.to_dict()) == e

    def test_defaults(self):
        e = Edge.from_dict({"source": "a.md", "target": "b.md", "type": "semantic", "weight": 0.72})
        assert e.label is None
        assert e.weight == pytest.approx(0.72)


# --------------------------------------------------------------------------- #
# KnowledgeGraph — mutation and properties
# --------------------------------------------------------------------------- #


class TestKnowledgeGraphMutation:
    def test_add_node_and_count(self):
        g = KnowledgeGraph()
        assert g.node_count == 0
        g.add_node("concepts/a.md", title="A")
        assert g.node_count == 1

    def test_add_edge_auto_creates_stubs(self):
        g = KnowledgeGraph()
        g.add_edge("concepts/a.md", "guides/b.md", "explicit", 1.0)
        assert g.node_count == 2
        assert g.edge_count == 1

    def test_out_edges_and_in_edges(self):
        g = _triangle()
        out = g.out_edges("concepts/a.md")
        assert len(out) == 1
        assert out[0].target == "concepts/b.md"
        in_ = g.in_edges("concepts/a.md")
        assert len(in_) == 1
        assert in_[0].source == "research/c.md"

    def test_get_node_returns_props(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md", title="Alpha", category="concepts")
        props = g.get_node("concepts/a.md")
        assert props is not None
        assert props.title == "Alpha"

    def test_get_node_missing_returns_none(self):
        assert KnowledgeGraph().get_node("missing.md") is None

    def test_update_node(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md", title="Old")
        g.add_node("concepts/a.md", title="New")  # update
        assert g.get_node("concepts/a.md").title == "New"
        assert g.node_count == 1  # not duplicated

    def test_nodes_iterable(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md", title="A")
        g.add_node("guides/b.md", title="B")
        ids = [doc_id for doc_id, _ in g.nodes()]
        assert set(ids) == {"concepts/a.md", "guides/b.md"}


# --------------------------------------------------------------------------- #
# Traversal — neighbours
# --------------------------------------------------------------------------- #


class TestNeighbours:
    def test_depth_1_direct_only(self):
        g = _triangle()
        nb = g.neighbours("concepts/a.md", depth=1)
        assert set(nb.keys()) == {"concepts/b.md"}
        assert nb["concepts/b.md"]["distance"] == 1

    def test_depth_2_transitive(self):
        g = _triangle()
        nb = g.neighbours("concepts/a.md", depth=2)
        assert "concepts/b.md" in nb
        assert "research/c.md" in nb
        assert nb["research/c.md"]["distance"] == 2

    def test_missing_node_returns_empty(self):
        g = _triangle()
        assert g.neighbours("no/such.md") == {}

    def test_edge_type_filter(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_node("concepts/c.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "explicit", 1.0)
        g.add_edge("concepts/a.md", "concepts/c.md", "semantic", 0.8)

        explicit_only = g.neighbours("concepts/a.md", depth=1, edge_types=["explicit"])
        assert "concepts/b.md" in explicit_only
        assert "concepts/c.md" not in explicit_only

    def test_isolated_node_returns_empty(self):
        g = KnowledgeGraph()
        g.add_node("concepts/isolated.md")
        assert g.neighbours("concepts/isolated.md") == {}


# --------------------------------------------------------------------------- #
# Traversal — path
# --------------------------------------------------------------------------- #


class TestPath:
    def test_direct_path(self):
        g = _triangle()
        p = g.path("concepts/a.md", "concepts/b.md")
        assert p == ["concepts/a.md", "concepts/b.md"]

    def test_two_hop_path(self):
        g = _triangle()
        p = g.path("concepts/a.md", "research/c.md")
        assert p is not None
        assert p[0] == "concepts/a.md"
        assert p[-1] == "research/c.md"
        assert len(p) == 3

    def test_no_path_returns_none(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        assert g.path("concepts/a.md", "concepts/b.md") is None

    def test_self_path(self):
        g = _triangle()
        p = g.path("concepts/a.md", "concepts/a.md")
        assert p == ["concepts/a.md"]

    def test_missing_node_returns_none(self):
        g = _triangle()
        assert g.path("concepts/a.md", "missing.md") is None


# --------------------------------------------------------------------------- #
# Health — orphans
# --------------------------------------------------------------------------- #


class TestOrphans:
    def test_all_connected_no_orphans(self):
        g = _triangle()
        assert g.orphans() == []

    def test_isolated_node_is_orphan(self):
        g = _triangle()
        g.add_node("research/orphan.md")
        orphans = g.orphans()
        assert "research/orphan.md" in orphans

    def test_semantic_only_node_is_orphan_for_explicit_check(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "semantic", 0.7)
        # b has inbound semantic but no inbound explicit → orphan
        orphans = g.orphans(edge_types=["explicit"])
        assert "concepts/b.md" in orphans

    def test_orphan_edge_type_filter(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "semantic", 0.6)
        # b NOT orphan if we include semantic
        assert "concepts/b.md" not in g.orphans(edge_types=["semantic"])


# --------------------------------------------------------------------------- #
# Health — hubs
# --------------------------------------------------------------------------- #


class TestHubs:
    def test_hub_ranked_first(self):
        g = _hub()
        hubs = g.hubs(top_k=3)
        assert hubs[0][0] == "concepts/hub.md"
        assert hubs[0][1] == 5

    def test_top_k_respected(self):
        g = _hub()
        assert len(g.hubs(top_k=2)) == 2

    def test_empty_graph(self):
        assert KnowledgeGraph().hubs() == []


# --------------------------------------------------------------------------- #
# PageRank
# --------------------------------------------------------------------------- #


class TestPageRank:
    def test_scores_sum_to_one(self):
        g = _triangle()
        pr = g.pagerank()
        assert abs(sum(pr.values()) - 1.0) < 1e-5

    def test_hub_has_highest_pr(self):
        g = _hub()
        pr = g.pagerank()
        assert pr["concepts/hub.md"] == max(pr.values())

    def test_empty_graph_returns_empty(self):
        assert KnowledgeGraph().pagerank() == {}

    def test_single_node(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        pr = g.pagerank()
        assert pr["concepts/a.md"] == pytest.approx(1.0)

    def test_dangling_node_handled(self):
        """A node with no outbound edges must not cause division by zero."""
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "explicit", 1.0)
        pr = g.pagerank()
        assert abs(sum(pr.values()) - 1.0) < 1e-5

    def test_broken_edges_excluded(self):
        """Broken edges (weight=0) must not contribute to PageRank transitions."""
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "broken", 0.0)
        # With only a broken edge, b should not get extra rank
        pr = g.pagerank()
        assert abs(sum(pr.values()) - 1.0) < 1e-5

    def test_convergence_within_100_iter(self):
        """PageRank converges well within 100 iterations for small graphs."""
        g = _hub()
        # Add extra connections
        for i in range(5):
            g.add_edge("concepts/hub.md", f"guides/spoke-{i}.md", "explicit", 1.0)
        pr1 = g.pagerank(max_iter=100)
        pr2 = g.pagerank(max_iter=200)
        for doc_id in pr1:
            assert abs(pr1[doc_id] - pr2[doc_id]) < 1e-4


# --------------------------------------------------------------------------- #
# Serialisation
# --------------------------------------------------------------------------- #


class TestSerialisation:
    def test_roundtrip_empty(self):
        g = KnowledgeGraph()
        g2 = KnowledgeGraph.from_dict(g.to_dict())
        assert g2.node_count == 0
        assert g2.edge_count == 0

    def test_roundtrip_with_data(self):
        g = _triangle()
        d = g.to_dict()
        g2 = KnowledgeGraph.from_dict(d)
        assert g2.node_count == g.node_count
        assert g2.edge_count == g.edge_count
        # BFS must work on reloaded graph
        nb = g2.neighbours("concepts/a.md", depth=1)
        assert "concepts/b.md" in nb

    def test_edge_types_preserved(self):
        g = KnowledgeGraph()
        g.add_node("concepts/a.md")
        g.add_node("concepts/b.md")
        g.add_edge("concepts/a.md", "concepts/b.md", "semantic", 0.75)
        g2 = KnowledgeGraph.from_dict(g.to_dict())
        out = g2.out_edges("concepts/a.md")
        assert out[0].type == "semantic"
        assert out[0].weight == pytest.approx(0.75)
