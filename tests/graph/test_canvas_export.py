"""Tests for scripts/canvas_export.py — build_canvas()."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from canvas_export import build_canvas  # noqa: E402

# ---------------------------------------------------------------------------
# Shared mini graph fixture
# ---------------------------------------------------------------------------

MINI_GRAPH = {
    "nodes": {
        "concepts/alpha.md": {
            "title": "Alpha",
            "category": "concepts",
            "tags": ["cache", "perf"],
        },
        "concepts/beta.md": {
            "title": "Beta",
            "category": "concepts",
            "tags": ["cache"],
        },
        "guides/gamma.md": {
            "title": "Gamma",
            "category": "guides",
            "tags": ["setup"],
        },
        "research/delta.md": {
            "title": "Delta",
            "category": "research",
            "tags": ["perf"],
        },
    },
    "edges": [
        {
            "source": "concepts/alpha.md",
            "target": "concepts/beta.md",
            "type": "explicit",
            "weight": 1.0,
            "label": "see Beta",
        },
        {
            "source": "concepts/alpha.md",
            "target": "guides/gamma.md",
            "type": "semantic",
            "weight": 0.42,
            "label": None,
        },
        {
            "source": "concepts/beta.md",
            "target": "research/delta.md",
            "type": "broken",
            "weight": 0.0,
            "label": None,
        },
    ],
}


# ---------------------------------------------------------------------------
# Helper to build the canvas and return it (does not write to disk)
# ---------------------------------------------------------------------------


def _canvas(tmp_path: Path) -> dict:
    out = tmp_path / "test.canvas"
    return build_canvas(MINI_GRAPH, out)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_canvas_has_nodes_and_edges(tmp_path: Path) -> None:
    canvas = _canvas(tmp_path)
    assert "nodes" in canvas
    assert "edges" in canvas


def test_node_count_matches_graph(tmp_path: Path) -> None:
    canvas = _canvas(tmp_path)
    assert len(canvas["nodes"]) == len(MINI_GRAPH["nodes"])


def test_edge_colours(tmp_path: Path) -> None:
    canvas = _canvas(tmp_path)

    # Build a lookup: (fromNode, toNode) -> color — but we match by the
    # edge entry's color against the source/target pair using node ids.
    import hashlib

    def nid(doc_id: str) -> str:
        return hashlib.md5(doc_id.encode()).hexdigest()[:8]

    color_by_pair = {
        (e["fromNode"], e["toNode"]): e["color"] for e in canvas["edges"]
    }

    explicit_pair = (nid("concepts/alpha.md"), nid("concepts/beta.md"))
    semantic_pair = (nid("concepts/alpha.md"), nid("guides/gamma.md"))
    broken_pair = (nid("concepts/beta.md"), nid("research/delta.md"))

    assert color_by_pair[explicit_pair] == "2", "explicit edge should be green ('2')"
    assert color_by_pair[semantic_pair] == "4", "semantic edge should be blue ('4')"
    assert color_by_pair[broken_pair] == "1", "broken edge should be red ('1')"


def test_semantic_edge_label_format(tmp_path: Path) -> None:
    """Semantic edge label must be the weight rounded to 2 dp as a string."""
    canvas = _canvas(tmp_path)
    import hashlib

    def nid(doc_id: str) -> str:
        return hashlib.md5(doc_id.encode()).hexdigest()[:8]

    semantic_pair = (nid("concepts/alpha.md"), nid("guides/gamma.md"))
    label_by_pair = {
        (e["fromNode"], e["toNode"]): e.get("label") for e in canvas["edges"]
    }
    assert label_by_pair[semantic_pair] == "0.42"


def test_explicit_edge_label_preserved(tmp_path: Path) -> None:
    """Explicit edge with a label string keeps that label unchanged."""
    canvas = _canvas(tmp_path)
    import hashlib

    def nid(doc_id: str) -> str:
        return hashlib.md5(doc_id.encode()).hexdigest()[:8]

    explicit_pair = (nid("concepts/alpha.md"), nid("concepts/beta.md"))
    label_by_pair = {
        (e["fromNode"], e["toNode"]): e.get("label") for e in canvas["edges"]
    }
    assert label_by_pair[explicit_pair] == "see Beta"


def test_subclustering_same_tag_adjacent(tmp_path: Path) -> None:
    """Nodes sharing the same first tag ("cache": alpha & beta) land in the
    same column and their y values are exactly _VERT_SPACING (140) apart."""
    from canvas_export import _VERT_SPACING

    canvas = _canvas(tmp_path)
    import hashlib

    def nid(doc_id: str) -> str:
        return hashlib.md5(doc_id.encode()).hexdigest()[:8]

    alpha_id = nid("concepts/alpha.md")
    beta_id = nid("concepts/beta.md")

    node_map = {n["id"]: n for n in canvas["nodes"]}
    alpha = node_map[alpha_id]
    beta = node_map[beta_id]

    # Both live in the "concepts" column — same x
    assert alpha["x"] == beta["x"], "alpha and beta should share the same x column"
    # Adjacent within sub-cluster — y differs by exactly _VERT_SPACING
    assert abs(alpha["y"] - beta["y"]) == _VERT_SPACING


def test_output_is_valid_json(tmp_path: Path) -> None:
    """Canvas file written to disk is valid JSON with matching node/edge counts."""
    out = tmp_path / "graph.canvas"
    canvas = build_canvas(MINI_GRAPH, out)

    raw = out.read_text(encoding="utf-8")
    parsed = json.loads(raw)

    assert len(parsed["nodes"]) == len(canvas["nodes"])
    assert len(parsed["edges"]) == len(canvas["edges"])
