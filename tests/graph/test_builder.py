"""Tests for src/graph/builder.py — KnowledgeGraphBuilder."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.graph.builder import (
    KnowledgeGraphBuilder,
    _normalise_kb_link,
    _parse_frontmatter,
)
from src.graph.graph import KnowledgeGraph

CATEGORIES = ("concepts", "guides", "references", "research")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _make_kb(tmp_path: Path) -> Path:
    for cat in CATEGORIES:
        (tmp_path / cat).mkdir(parents=True, exist_ok=True)
    return tmp_path


def _write_doc(kb: Path, doc_id: str, content: str) -> Path:
    path = kb / doc_id
    path.write_text(content, encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# _parse_frontmatter
# --------------------------------------------------------------------------- #


class TestParseFrontmatter:
    def test_no_frontmatter_returns_empty(self):
        assert _parse_frontmatter("# Title\n\nBody") == {}

    def test_basic_fields(self):
        content = "---\ntitle: My Title\ndate: 2026-07-17\ntype: concept\nstatus: active\n---\nBody"
        fm = _parse_frontmatter(content)
        assert fm["title"] == "My Title"
        assert fm["date"] == "2026-07-17"
        assert fm["type"] == "concept"
        assert fm["status"] == "active"

    def test_related_list(self):
        content = (
            "---\ntitle: X\nrelated:\n"
            "  - ../guides/setup.md\n"
            "  - ../concepts/caching.md\n"
            "---\nBody\n"
        )
        fm = _parse_frontmatter(content)
        assert "../guides/setup.md" in fm["related"]
        assert "../concepts/caching.md" in fm["related"]

    def test_tags_inline(self):
        content = "---\ntitle: X\ntags: [caching, architecture, p2]\n---\n"
        fm = _parse_frontmatter(content)
        assert "caching" in fm["tags"]
        assert "architecture" in fm["tags"]


# --------------------------------------------------------------------------- #
# _normalise_kb_link
# --------------------------------------------------------------------------- #


class TestNormaliseKBLink:
    def test_relative_parent_link(self):
        result = _normalise_kb_link("../guides/setup.md", "concepts/caching.md")
        assert result == "guides/setup.md"

    def test_absolute_category_link(self):
        result = _normalise_kb_link("concepts/caching.md", "guides/setup.md")
        assert result == "concepts/caching.md"

    def test_external_url_returns_none(self):
        assert _normalise_kb_link("https://example.com/page", "concepts/a.md") is None

    def test_non_md_link_returns_none(self):
        assert _normalise_kb_link("../images/diagram.png", "concepts/a.md") is None

    def test_fragment_stripped(self):
        result = _normalise_kb_link("../concepts/caching.md#performance", "guides/setup.md")
        assert result == "concepts/caching.md"

    def test_bare_filename_resolves_to_same_category(self):
        result = _normalise_kb_link("other.md", "concepts/first.md")
        assert result == "concepts/other.md"

    def test_invalid_category_returns_none(self):
        result = _normalise_kb_link("unknown/file.md", "concepts/a.md")
        assert result is None


# --------------------------------------------------------------------------- #
# KnowledgeGraphBuilder — _add_nodes
# --------------------------------------------------------------------------- #


class TestAddNodes:
    def test_nodes_created_for_all_md_files(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "---\ntitle: Alpha\ntype: concept\nstatus: active\n---\n# Alpha\n")
        _write_doc(kb, "guides/b.md", "# Beta\n\nContent")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        assert graph.get_node("concepts/a.md") is not None
        assert graph.get_node("guides/b.md") is not None

    def test_node_title_from_frontmatter(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "---\ntitle: Exact Title\n---\n# H1 Title\n")
        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        assert graph.get_node("concepts/a.md").title == "Exact Title"

    def test_node_category_inferred(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "guides/g.md", "# Guide\n\nContent")
        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        assert graph.get_node("guides/g.md").category == "guides"

    def test_empty_kb_builds_empty_graph(self, tmp_path):
        kb = _make_kb(tmp_path)
        graph = KnowledgeGraphBuilder(kb).build()
        assert graph.node_count == 0


# --------------------------------------------------------------------------- #
# KnowledgeGraphBuilder — build_explicit (frontmatter related:)
# --------------------------------------------------------------------------- #


class TestBuildExplicitFrontmatter:
    def test_related_frontmatter_produces_explicit_edge(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md",
                   "---\ntitle: A\nrelated:\n  - ../guides/b.md\n---\n# A\n")
        _write_doc(kb, "guides/b.md", "# B\n\nContent")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        out = graph.out_edges("concepts/a.md")
        assert any(e.target == "guides/b.md" and e.type == "explicit" for e in out)

    def test_broken_link_recorded_as_broken_edge(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md",
                   "---\ntitle: A\nrelated:\n  - ../guides/nonexistent.md\n---\n# A\n")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        out = graph.out_edges("concepts/a.md")
        broken = [e for e in out if e.type == "broken"]
        assert len(broken) == 1
        assert broken[0].weight == 0.0


# --------------------------------------------------------------------------- #
# KnowledgeGraphBuilder — build_explicit (inline markdown links)
# --------------------------------------------------------------------------- #


class TestBuildExplicitInlineLinks:
    def test_inline_link_produces_explicit_edge(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "guides/setup.md",
                   "# Setup\n\nSee [Caching Concepts](../concepts/caching.md) for details.")
        _write_doc(kb, "concepts/caching.md", "# Caching\n\nContent")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        out = graph.out_edges("guides/setup.md")
        assert any(e.target == "concepts/caching.md" and e.type == "explicit" for e in out)

    def test_inline_link_label_preserved(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "guides/setup.md",
                   "# Setup\n\nSee [Caching Concepts](../concepts/caching.md).")
        _write_doc(kb, "concepts/caching.md", "# Caching\n\nContent")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        out = graph.out_edges("guides/setup.md")
        explicit = [e for e in out if e.target == "concepts/caching.md"]
        assert explicit[0].label == "Caching Concepts"

    def test_external_link_ignored(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "guides/setup.md",
                   "# Setup\n\nSee [GitHub](https://github.com/example).")
        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        assert graph.edge_count == 0

    def test_duplicate_link_not_added_twice(self, tmp_path):
        """A link that appears in both frontmatter and body must only create one edge."""
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md",
                   "---\ntitle: A\nrelated:\n  - ../guides/b.md\n---\n"
                   "# A\n\nSee [B](../guides/b.md).\n")
        _write_doc(kb, "guides/b.md", "# B\n\nContent")

        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        edges_to_b = [e for e in graph.out_edges("concepts/a.md") if e.target == "guides/b.md"]
        assert len(edges_to_b) == 1, "Duplicate edge should not be added"

    def test_self_link_ignored(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "# A\n\nSee [Self](../concepts/a.md).")
        builder = KnowledgeGraphBuilder(kb)
        graph = builder.build()
        assert graph.edge_count == 0


# --------------------------------------------------------------------------- #
# KnowledgeGraphBuilder — build_semantic
# --------------------------------------------------------------------------- #


class TestBuildSemantic:
    def _mock_index(self, doc_id_scores: dict) -> MagicMock:
        """Return a mock PersistentEmbeddingIndex whose search() returns canned results."""
        mock = MagicMock()
        mock.doc_count = 10  # non-empty

        def _search(content, top_k=50):
            return doc_id_scores.get(content[:20], [])

        mock.search.side_effect = _search
        return mock

    def test_semantic_edge_above_threshold(self, tmp_path):
        kb = _make_kb(tmp_path)
        content_a = "# A\n\nAlpha content for caching strategy."
        content_b = "# B\n\nBeta content"
        _write_doc(kb, "concepts/a.md", content_a)
        _write_doc(kb, "concepts/b.md", content_b)

        # Mock: when a.md content is queried, b.md chunk is returned with score 0.7
        mock_index = MagicMock()
        mock_index.doc_count = 5

        def _search(content, top_k=50):
            if "Alpha" in content:
                return [("concepts/b.md#preamble", 0.70)]
            return []

        mock_index.search.side_effect = _search

        builder = KnowledgeGraphBuilder(kb, index=mock_index, semantic_threshold=0.3)
        graph = builder.build()
        out = graph.out_edges("concepts/a.md")
        semantic = [e for e in out if e.type == "semantic"]
        assert len(semantic) >= 1
        assert semantic[0].target == "concepts/b.md"

    def test_semantic_edge_below_threshold_excluded(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "# A\n\nAlpha content.")
        _write_doc(kb, "concepts/b.md", "# B\n\nBeta content")

        mock_index = MagicMock()
        mock_index.doc_count = 5

        def _search(content, top_k=50):
            return [("concepts/b.md#preamble", 0.10)]  # below threshold

        mock_index.search.side_effect = _search

        builder = KnowledgeGraphBuilder(kb, index=mock_index, semantic_threshold=0.3)
        graph = builder.build()
        out = graph.out_edges("concepts/a.md")
        semantic = [e for e in out if e.type == "semantic"]
        assert len(semantic) == 0

    def test_empty_index_skips_semantic(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "# A\n\nContent")
        mock_index = MagicMock()
        mock_index.doc_count = 0  # empty index

        builder = KnowledgeGraphBuilder(kb, index=mock_index, semantic_threshold=0.3)
        graph = builder.build()
        semantic_edges = [
            e for _, edges in [(d, graph.out_edges(d)) for d, _ in graph.nodes()]
            for e in edges if e.type == "semantic"
        ]
        assert len(semantic_edges) == 0

    def test_no_index_no_semantic_edges(self, tmp_path):
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "# A\n\nContent")
        graph = KnowledgeGraphBuilder(kb, index=None).build()
        semantic = [
            e for _, edges in [(d, graph.out_edges(d)) for d, _ in graph.nodes()]
            for e in edges if e.type == "semantic"
        ]
        assert len(semantic) == 0


# --------------------------------------------------------------------------- #
# P4 NodeProps enrichment — builder populates new fields
# --------------------------------------------------------------------------- #


class TestBuilderNodePropsEnrichment:
    """P4 Sub-Task 3: verify _add_nodes() populates mtime_epoch, content_length,
    description, and related_refs on each node."""

    def test_builder_populates_mtime_epoch(self, tmp_path):
        """mtime_epoch is set to the file's actual mtime, not 0.0."""
        kb = _make_kb(tmp_path)
        doc = _write_doc(kb, "concepts/a.md", "# A\n\nSome content here.")
        import time
        before = time.time() - 1  # slightly before write
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert props.mtime_epoch > before, "mtime_epoch must reflect actual file mtime"

    def test_builder_populates_content_length(self, tmp_path):
        """content_length matches the character count of the file content."""
        kb = _make_kb(tmp_path)
        body = "---\ntitle: Alpha\n---\n# Alpha\n\nThis is the body of the document.\n"
        _write_doc(kb, "concepts/a.md", body)
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert props.content_length == len(body)

    def test_builder_populates_description(self, tmp_path):
        """description is the first non-heading, non-blank line after frontmatter."""
        kb = _make_kb(tmp_path)
        content = (
            "---\ntitle: Guide\n---\n"
            "\n"
            "# Guide Title\n"
            "\n"
            "This is the introductory paragraph of the guide.\n"
        )
        _write_doc(kb, "guides/g.md", content)
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("guides/g.md")
        assert props is not None
        assert props.description == "This is the introductory paragraph of the guide."

    def test_builder_description_truncated_to_200(self, tmp_path):
        """description is truncated to 200 characters."""
        kb = _make_kb(tmp_path)
        long_para = "x" * 300
        _write_doc(kb, "concepts/a.md", f"# A\n\n{long_para}\n")
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert len(props.description) == 200

    def test_builder_description_empty_when_no_body(self, tmp_path):
        """description is '' when document has no qualifying paragraph."""
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "# Heading Only\n\n## Section\n\n")
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert props.description == ""

    def test_builder_populates_related_refs(self, tmp_path):
        """related_refs contains the raw related: list from frontmatter."""
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", (
            "---\ntitle: A\nrelated:\n"
            "  - ../guides/setup.md\n"
            "  - ../research/notes.md\n"
            "---\n# A\n\nBody.\n"
        ))
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert "../guides/setup.md" in props.related_refs
        assert "../research/notes.md" in props.related_refs

    def test_builder_related_refs_empty_when_no_frontmatter_related(self, tmp_path):
        """related_refs is [] when the document has no related: list."""
        kb = _make_kb(tmp_path)
        _write_doc(kb, "concepts/a.md", "---\ntitle: A\n---\n# A\n\nBody.\n")
        graph = KnowledgeGraphBuilder(kb).build()
        props = graph.get_node("concepts/a.md")
        assert props is not None
        assert props.related_refs == []
