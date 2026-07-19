"""Tests for scripts/dataview_export.py — inject_dataview()."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from dataview_export import inject_dataview  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FM_TEMPLATE = """\
---
title: "{title}"
category: "concepts"
tags: [test]
---
# {title}

Body of {title}.
"""


def _make_kb(export_path: Path, docs: list[str]) -> None:
    """Populate export_path with .md files that have frontmatter."""
    export_path.mkdir(parents=True, exist_ok=True)
    for doc_id in docs:
        file_path = export_path / doc_id
        file_path.parent.mkdir(parents=True, exist_ok=True)
        title = Path(doc_id).stem.capitalize()
        file_path.write_text(_FM_TEMPLATE.format(title=title), encoding="utf-8")


# ---------------------------------------------------------------------------
# Shared graph fixture for most tests
# ---------------------------------------------------------------------------

_DOC_IDS = ["concepts/alpha.md", "concepts/beta.md", "guides/gamma.md"]

_MINI_GRAPH: dict = {
    "nodes": {
        "concepts/alpha.md": {"title": "Alpha", "category": "concepts"},
        "concepts/beta.md": {"title": "Beta", "category": "concepts"},
        "guides/gamma.md": {"title": "Gamma", "category": "guides"},
    },
    "edges": [
        {
            "source": "concepts/alpha.md",
            "target": "concepts/beta.md",
            "type": "semantic",
            "weight": 0.80,
        },
        {
            "source": "concepts/alpha.md",
            "target": "guides/gamma.md",
            "type": "semantic",
            "weight": 0.60,
        },
        {
            "source": "concepts/beta.md",
            "target": "concepts/alpha.md",
            "type": "semantic",
            "weight": 0.75,
        },
    ],
}


@pytest.fixture
def kb_export(tmp_path: Path) -> Path:
    """Return a tmp kb-export/knowledge-base/ tree pre-populated with docs."""
    export = tmp_path / "kb-export" / "knowledge-base"
    _make_kb(export, _DOC_IDS)
    return export


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_semantic_links_injected(kb_export: Path) -> None:
    """After inject_dataview, every .md file has 'semantic_links:' in its frontmatter."""
    inject_dataview(kb_export, _MINI_GRAPH)

    for doc_id in _DOC_IDS:
        content = (kb_export / doc_id).read_text(encoding="utf-8")
        assert "semantic_links:" in content, (
            f"{doc_id} is missing 'semantic_links:' after injection"
        )


def test_live_kb_not_modified(tmp_path: Path) -> None:
    """inject_dataview raises ValueError if export_path is inside docs/knowledge-base/."""
    live_kb = Path("docs/knowledge-base").resolve()
    with pytest.raises(ValueError, match="live KB"):
        inject_dataview(live_kb, _MINI_GRAPH)


def test_top_n_zero_returns_all(kb_export: Path) -> None:
    """top_n=0 (default) injects ALL semantic edges above min_weight — no cap."""
    inject_dataview(kb_export, _MINI_GRAPH, top_n=0, min_weight=0.50)

    # alpha has two semantic neighbours above 0.50 (beta at 0.80, gamma at 0.60)
    content = (kb_export / "concepts/alpha.md").read_text(encoding="utf-8")
    assert content.count('- doc:') == 2


def test_top_n_positive_caps(tmp_path: Path) -> None:
    """top_n=1 keeps only the highest-weight neighbour per document."""
    export = tmp_path / "kb-export" / "knowledge-base"
    docs = [
        "concepts/a.md",
        "concepts/b.md",
        "concepts/c.md",
        "concepts/d.md",
        "concepts/e.md",
    ]
    _make_kb(export, docs)

    # "a" has 4 semantic neighbours — all above default threshold
    graph: dict = {
        "nodes": {d: {} for d in docs},
        "edges": [
            {"source": "concepts/a.md", "target": "concepts/b.md", "type": "semantic", "weight": 0.90},
            {"source": "concepts/a.md", "target": "concepts/c.md", "type": "semantic", "weight": 0.85},
            {"source": "concepts/a.md", "target": "concepts/d.md", "type": "semantic", "weight": 0.80},
            {"source": "concepts/a.md", "target": "concepts/e.md", "type": "semantic", "weight": 0.75},
        ],
    }

    inject_dataview(export, graph, top_n=2, min_weight=0.30)

    content = (export / "concepts/a.md").read_text(encoding="utf-8")
    assert content.count('- doc:') == 2


def test_min_weight_filters(kb_export: Path) -> None:
    """Edge with weight=0.25 is excluded when min_weight=0.30."""
    low_weight_graph: dict = {
        "nodes": {
            "concepts/alpha.md": {},
            "concepts/beta.md": {},
        },
        "edges": [
            {
                "source": "concepts/alpha.md",
                "target": "concepts/beta.md",
                "type": "semantic",
                "weight": 0.25,
            }
        ],
    }

    inject_dataview(kb_export, low_weight_graph, min_weight=0.30)

    content = (kb_export / "concepts/alpha.md").read_text(encoding="utf-8")
    # The edge was below threshold — the block must be present but empty
    assert "semantic_links: []" in content


def test_no_semantic_edges_writes_empty_list(kb_export: Path) -> None:
    """A doc with no semantic edges in the graph gets 'semantic_links: []'."""
    empty_graph: dict = {
        "nodes": {"concepts/alpha.md": {}, "concepts/beta.md": {}},
        "edges": [],  # no semantic edges at all
    }

    inject_dataview(kb_export, empty_graph)

    for doc_id in _DOC_IDS:
        content = (kb_export / doc_id).read_text(encoding="utf-8")
        assert "semantic_links: []" in content, (
            f"{doc_id} should have 'semantic_links: []' when there are no edges"
        )
