"""Tests for src/graph/store.py — GraphStore."""

from __future__ import annotations

import json
import os

import pytest

from src.graph.graph import KnowledgeGraph
from src.graph.store import GraphStore


def _simple_graph() -> KnowledgeGraph:
    g = KnowledgeGraph()
    g.add_node("concepts/a.md", title="Alpha", category="concepts")
    g.add_node("guides/b.md", title="Beta", category="guides")
    g.add_edge("concepts/a.md", "guides/b.md", "explicit", 1.0, "See Beta")
    return g


class TestGraphStore:
    def _store(self) -> GraphStore:
        return GraphStore()

    def test_roundtrip(self, tmp_path):
        g = _simple_graph()
        path = tmp_path / "kb-graph.json"
        self._store().save(path, g, metadata={"kb_path": "docs/knowledge-base"})
        g2 = self._store().load(path)
        assert g2 is not None
        assert g2.node_count == g.node_count
        assert g2.edge_count == g.edge_count

    def test_roundtrip_preserves_props(self, tmp_path):
        g = _simple_graph()
        path = tmp_path / "kb-graph.json"
        self._store().save(path, g)
        g2 = self._store().load(path)
        assert g2 is not None
        node = g2.get_node("concepts/a.md")
        assert node is not None
        assert node.title == "Alpha"
        assert node.category == "concepts"

    def test_load_missing_returns_none(self, tmp_path):
        path = tmp_path / "no-such-graph.json"
        assert self._store().load(path) is None

    def test_load_corrupt_json_returns_none(self, tmp_path):
        path = tmp_path / "kb-graph.json"
        path.write_text("not valid json {{{", encoding="utf-8")
        assert self._store().load(path) is None

    def test_load_invalid_structure_returns_none(self, tmp_path):
        path = tmp_path / "kb-graph.json"
        path.write_text(json.dumps({"unexpected": "structure"}), encoding="utf-8")
        # Should not raise — just returns an empty graph
        result = self._store().load(path)
        assert result is not None  # from_dict handles missing keys gracefully
        assert result.node_count == 0

    def test_save_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "graph.json"
        self._store().save(path, _simple_graph())
        assert path.exists()

    def test_save_is_atomic_temp_cleaned_on_failure(self, tmp_path, monkeypatch):
        """An OSError during json.dump must remove the temp file."""
        original_dump = json.dump

        def _fail_dump(*args, **kwargs):
            raise OSError("simulated failure")

        monkeypatch.setattr(json, "dump", _fail_dump)
        path = tmp_path / "graph.json"

        with pytest.raises(OSError, match="simulated"):
            self._store().save(path, _simple_graph())

        # No temp file leaked
        remaining = list(tmp_path.glob("*.json.tmp"))
        assert remaining == [], f"Leaked temp files: {remaining}"

    def test_metadata_written_to_file(self, tmp_path):
        path = tmp_path / "kb-graph.json"
        self._store().save(path, _simple_graph(), metadata={"semantic_threshold": 0.3})
        with open(path) as f:
            raw = json.load(f)
        assert raw["metadata"]["semantic_threshold"] == pytest.approx(0.3)
        assert raw["metadata"]["node_count"] == 2
        assert raw["metadata"]["edge_count"] == 1

    def test_delete_existing(self, tmp_path):
        path = tmp_path / "graph.json"
        self._store().save(path, _simple_graph())
        assert path.exists()
        self._store().delete(path)
        assert not path.exists()

    def test_delete_nonexistent_noop(self, tmp_path):
        self._store().delete(tmp_path / "missing.json")  # must not raise

    def test_roundtrip_empty_graph(self, tmp_path):
        path = tmp_path / "empty.json"
        self._store().save(path, KnowledgeGraph())
        g2 = self._store().load(path)
        assert g2 is not None
        assert g2.node_count == 0
        assert g2.edge_count == 0
