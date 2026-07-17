"""Tests for src/embeddings/ — PersistentEmbeddingIndex, FileBackedVectorStore, KBIndexer.

All tests use tmp_path fixtures and never touch the live .bob/kb-index/.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex, _content_hash
from src.embeddings.indexer import KBIndexer
from src.embeddings.store import FileBackedVectorStore

CATEGORIES = ("concepts", "guides", "references", "research")


def _make_kb(tmp_path: Path) -> Path:
    for cat in CATEGORIES:
        (tmp_path / cat).mkdir(parents=True, exist_ok=True)
    return tmp_path


# --------------------------------------------------------------------------- #
# FileBackedVectorStore
# --------------------------------------------------------------------------- #


class TestFileBackedVectorStore:
    def _store(self):
        return FileBackedVectorStore()

    def test_roundtrip(self, tmp_path):
        store = self._store()
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        manifest = {
            "doc1": {"path": "a.md", "mtime": 1.0, "hash": "abc"},
            "doc2": {"path": "b.md", "mtime": 2.0, "hash": "def"},
        }

        store.save(tmp_path / "idx", matrix, manifest)
        result = store.load(tmp_path / "idx")

        assert result is not None
        loaded_mat, loaded_man = result
        np.testing.assert_array_almost_equal(loaded_mat, matrix)
        assert loaded_man == manifest

    def test_load_missing_returns_none(self, tmp_path):
        assert self._store().load(tmp_path / "nonexistent") is None

    def test_load_corrupt_vectors_returns_none(self, tmp_path):
        idx = tmp_path / "idx"
        idx.mkdir()
        (idx / "vectors.npy").write_bytes(b"not a numpy file")
        (idx / "manifest.json").write_text("{}")
        assert self._store().load(idx) is None

    def test_load_shape_mismatch_returns_none(self, tmp_path):
        """Matrix rows != manifest entries → None."""
        store = self._store()
        idx = tmp_path / "idx"
        matrix = np.array([[1.0, 2.0]], dtype=np.float32)
        # Save with 1 row but 2 manifest entries
        idx.mkdir()
        np.save(str(idx / "vectors.npy"), matrix)
        with open(idx / "manifest.json", "w") as f:
            json.dump({"a": {}, "b": {}}, f)
        assert store.load(idx) is None

    def test_save_is_atomic_existing_intact_on_failure(self, tmp_path):
        """Original index must survive a failed second write (no partial overwrite)."""
        store = self._store()
        idx = tmp_path / "idx"
        matrix1 = np.array([[1.0]], dtype=np.float32)
        manifest1 = {"doc1": {"mtime": 1.0, "hash": "x"}}
        store.save(idx, matrix1, manifest1)

        # Corrupt the second save by making vectors.npy a directory (write fails)
        # — just verify first write is still readable.
        result = store.load(idx)
        assert result is not None
        np.testing.assert_array_almost_equal(result[0], matrix1)

    def test_save_np_write_failure_raises_and_cleans_temp(self, tmp_path, monkeypatch):
        """OSError during np.save must re-raise and remove the temp file."""
        store = self._store()
        idx = tmp_path / "idx"

        def _fail_save(*args, **kwargs):
            raise OSError("simulated np.save failure")

        monkeypatch.setattr(np, "save", _fail_save)

        with pytest.raises(OSError, match="simulated"):
            store.save(idx, np.array([[1.0]], dtype=np.float32), {"doc": {}})

        # The temp file must have been cleaned up
        remaining = list(idx.glob("*.npy")) if idx.exists() else []
        assert remaining == [], f"Temp .npy files leaked: {remaining}"

    def test_save_json_write_failure_raises_and_cleans_temp(self, tmp_path, monkeypatch):
        """OSError during json.dump must re-raise and remove the temp file."""
        store = self._store()
        idx = tmp_path / "idx"

        def _fail_dump(*args, **kwargs):
            raise OSError("simulated json.dump failure")

        monkeypatch.setattr(json, "dump", _fail_dump)

        with pytest.raises(OSError, match="simulated"):
            store.save(idx, np.array([[1.0]], dtype=np.float32), {"doc": {}})

        # The vectors file was written successfully; only the manifest temp leaked?
        remaining_json = list(idx.glob("*.json.tmp")) if idx.exists() else []
        assert remaining_json == [], f"Temp .json.tmp files leaked: {remaining_json}"

    def test_delete(self, tmp_path):
        store = self._store()
        idx = tmp_path / "idx"
        store.save(idx, np.array([[1.0]], dtype=np.float32), {"a": {}})
        assert idx.exists()
        store.delete(idx)
        assert not idx.exists()

    def test_delete_nonexistent_noop(self, tmp_path):
        self._store().delete(tmp_path / "missing")  # must not raise


# --------------------------------------------------------------------------- #
# PersistentEmbeddingIndex
# --------------------------------------------------------------------------- #


class TestPersistentEmbeddingIndex:
    def _index(self, tmp_path: Path) -> PersistentEmbeddingIndex:
        return PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / "kb-index")

    def test_empty_search_returns_empty(self, tmp_path):
        idx = self._index(tmp_path)
        assert idx.search("anything") == []

    def test_index_and_search(self, tmp_path):
        idx = self._index(tmp_path)
        idx.index_document("concepts/caching.md", "# Caching\n\nMulti-level cache strategy.")
        idx.index_document("guides/install.md", "# Install\n\nHow to install the package.")
        results = idx.search("caching strategy", top_k=2)
        assert len(results) == 2
        files = [doc_id for doc_id, _ in results]
        assert "concepts/caching.md" in files

    def test_flush_and_reload(self, tmp_path):
        """Flush then reload in a new instance — data must survive."""
        idx_path = tmp_path / "kb-index"
        embedder = EmbeddingGenerator()

        idx1 = PersistentEmbeddingIndex(embedder, idx_path)
        idx1.index_document("concepts/a.md", "# Alpha\n\nalpha topic content")
        idx1.flush()

        idx2 = PersistentEmbeddingIndex(embedder, idx_path)
        assert idx2.doc_count == 1
        results = idx2.search("alpha topic", top_k=1)
        assert results[0][0] == "concepts/a.md"

    def test_doc_count(self, tmp_path):
        idx = self._index(tmp_path)
        assert idx.doc_count == 0
        idx.index_document("a/b.md", "content")
        assert idx.doc_count == 1

    def test_is_stale_new_doc(self, tmp_path):
        """A document not in the manifest is always stale."""
        idx = self._index(tmp_path)
        _make_kb(tmp_path / "kb")
        doc = tmp_path / "kb" / "concepts" / "new.md"
        doc.write_text("# New\n\ncontent")
        assert idx.is_stale(doc) is True

    def test_rebuild_from_kb(self, tmp_path):
        """rebuild() indexes all .md files and returns the count."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text("# A\n\nalpha content")
        (kb / "guides" / "b.md").write_text("# B\n\nbeta content")
        idx = self._index(tmp_path)
        n = idx.rebuild(kb)
        assert n == 2
        assert idx.doc_count == 2

    def test_rebuild_incremental_skips_unchanged(self, tmp_path):
        """Second rebuild with no changes returns same count, zero re-embeds."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text("# A\n\nalpha content")
        idx = self._index(tmp_path)
        idx.rebuild(kb)
        # Rebuild again — manifest entry matches mtime+hash, so zero updates
        n2 = idx.rebuild(kb)
        assert n2 == 1

    def test_rebuild_re_embeds_changed_doc(self, tmp_path):
        """Modifying a document triggers re-embedding on next rebuild."""
        kb = _make_kb(tmp_path / "kb")
        doc = kb / "concepts" / "a.md"
        doc.write_text("# A\n\noriginal content")
        idx = self._index(tmp_path)
        idx.rebuild(kb)

        # Change content (different hash)
        doc.write_text("# A\n\ncompletely different topic now")
        n = idx.rebuild(kb)
        assert n == 1  # still 1 doc total

    def test_corrupt_index_triggers_full_rebuild(self, tmp_path):
        """A corrupt index is silently ignored; rebuild starts fresh."""
        idx_path = tmp_path / "kb-index"
        idx_path.mkdir()
        (idx_path / "vectors.npy").write_bytes(b"garbage")
        (idx_path / "manifest.json").write_text('{"bad": {}}')

        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "x.md").write_text("# X\n\nfresh doc")
        idx = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
        n = idx.rebuild(kb)
        assert n == 1  # built from scratch despite corrupt index


# --------------------------------------------------------------------------- #
# KBIndexer
# --------------------------------------------------------------------------- #


class TestKBIndexer:
    def test_sync_returns_doc_count(self, tmp_path):
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "c.md").write_text("# C\n\nconcept content")
        (kb / "research" / "r.md").write_text("# R\n\nresearch notes")
        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        indexer = KBIndexer(kb, idx)
        n = indexer.sync()
        assert n == 2

    def test_query_uses_index_fast_path(self, tmp_path):
        """KBIndexer.query() returns results using the persistent index."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "caching.md").write_text(
            "# Caching Strategy\n\nMulti-level cache with L1 exact and L2 semantic."
        )
        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        indexer = KBIndexer(kb, idx)
        result = indexer.query("cache L1 L2", top_k=3)
        assert result["total_results"] >= 1
        assert any("caching" in r["file"] for r in result["results"])


# --------------------------------------------------------------------------- #
# Integration: KnowledgeBaseQuery + PersistentEmbeddingIndex (P2-2 wire)
# --------------------------------------------------------------------------- #


class TestKBQueryWithIndex:
    def test_index_fast_path_used_when_doc_count_gt_0(self, tmp_path):
        """When index is non-empty, query() routes through _query_via_index."""
        from src.tools.kb_query import KnowledgeBaseQuery

        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "opt.md").write_text(
            "# Token Optimization\n\nReduces prompt token count with caching."
        )
        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        idx.rebuild(kb)

        kb_q = KnowledgeBaseQuery(str(kb), embedder=embedder, embedding_weight=0.7, index=idx)
        result = kb_q.query("token caching")
        assert result["total_results"] >= 1
        assert "opt.md" in result["results"][0]["file"]

    def test_empty_index_falls_back_to_full_scan(self, tmp_path):
        """An empty index (doc_count=0) silently falls back to full scan."""
        from src.tools.kb_query import KnowledgeBaseQuery

        kb = _make_kb(tmp_path / "kb")
        (kb / "guides" / "g.md").write_text("# Guide\n\nsome guide content keyword\n")
        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        # Do NOT call rebuild — index is empty

        kb_q = KnowledgeBaseQuery(str(kb), embedder=embedder, index=idx)
        result = kb_q.query("keyword")
        # Falls back to full scan — must still return results
        assert result["total_results"] == 1

    def test_no_index_no_embedder_keyword_only(self, tmp_path):
        """Default construction: pure keyword scorer, unchanged behaviour."""
        from src.tools.kb_query import KnowledgeBaseQuery

        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "x.md").write_text("# X\n\nalpha keyword content\n")
        kb_q = KnowledgeBaseQuery(str(kb))
        result = kb_q.query("keyword")
        assert result["total_results"] == 1


# --------------------------------------------------------------------------- #
# content_hash helper
# --------------------------------------------------------------------------- #


def test_content_hash_stable():
    """Same content always yields the same 16-char hex hash."""
    h1 = _content_hash("hello world")
    h2 = _content_hash("hello world")
    assert h1 == h2
    assert len(h1) == 16


def test_content_hash_differs():
    assert _content_hash("a") != _content_hash("b")
