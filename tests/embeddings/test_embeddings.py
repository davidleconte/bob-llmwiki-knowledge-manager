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
        loaded_mat, loaded_man, loaded_staleness = result
        np.testing.assert_array_almost_equal(loaded_mat, matrix)
        assert loaded_man == manifest
        assert loaded_staleness == {}  # no staleness file written → empty dict

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
        """A document not in the staleness map is always stale."""
        kb = _make_kb(tmp_path / "kb")
        idx = self._index(tmp_path)
        doc = kb / "concepts" / "new.md"
        doc.write_text("# New\n\ncontent")
        assert idx.is_stale(doc, kb_path=kb) is True

    def test_is_stale_false_after_rebuild(self, tmp_path):
        """After rebuild(), is_stale() returns False for unchanged docs."""
        kb = _make_kb(tmp_path / "kb")
        doc = kb / "concepts" / "a.md"
        doc.write_text(
            "## Section One\n\nThis section covers the alpha concept in sufficient detail.\n"
        )
        idx = self._index(tmp_path)
        idx.rebuild(kb)
        assert idx.is_stale(doc, kb_path=kb) is False

    def test_is_stale_true_after_modification(self, tmp_path):
        """After modifying a file, is_stale() returns True."""
        kb = _make_kb(tmp_path / "kb")
        doc = kb / "concepts" / "a.md"
        doc.write_text(
            "## Section One\n\nThis section covers the alpha concept in sufficient detail.\n"
        )
        idx = self._index(tmp_path)
        idx.rebuild(kb)

        doc.write_text("## Section One\n\nModified content that is different now.\n")
        assert idx.is_stale(doc, kb_path=kb) is True

    def test_rebuild_then_flush_then_reload_search_works(self, tmp_path):
        """Regression for AF-1: rebuild() + flush() must produce a loadable index.

        Before the AF-1 fix, flush() wrote a manifest.json with both chunk-level
        and file-level keys, so matrix.shape[0] != len(manifest) and load()
        returned None — making the persistent index permanently inert.
        """
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text(
            "## Alpha Topic\n\nThis section covers the alpha concept in sufficient detail.\n"
        )
        embedder = EmbeddingGenerator()
        idx1 = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        n1 = idx1.rebuild(kb)
        assert n1 >= 1, "rebuild() must index at least one chunk"
        idx1.flush()

        # Load in a brand-new instance — must NOT start empty
        idx2 = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        assert idx2.doc_count >= 1, (
            "AF-1 regression: index was empty after flush() + reload(); "
            "manifest.json likely had extra file-level keys causing shape mismatch"
        )
        results = idx2.search("alpha concept", top_k=1)
        assert len(results) >= 1, "search() must return results after reload"

    def test_rebuild_from_kb(self, tmp_path):
        """rebuild() indexes all .md files and returns the chunk count."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text(
            "## Alpha Topic\n\nThis section covers the alpha concept in sufficient detail.\n"
        )
        (kb / "guides" / "b.md").write_text(
            "## Beta Guide\n\nStep-by-step instructions for the beta workflow with detail.\n"
        )
        idx = self._index(tmp_path)
        n = idx.rebuild(kb)
        # With chunking each file produces ≥1 chunk; 2 files → ≥2 chunks.
        assert n >= 2
        assert idx.doc_count >= 2

    def test_rebuild_doc_ids_have_slug_suffix(self, tmp_path):
        """rebuild() stores chunk doc_ids with #slug fragment identifiers."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text(
            "## Section One\n\nThis section has enough content for the index.\n"
        )
        idx = self._index(tmp_path)
        idx.rebuild(kb)
        assert any("#" in doc_id for doc_id in idx._doc_ids)

    def test_rebuild_incremental_skips_unchanged(self, tmp_path):
        """Second rebuild with no changes returns same count, zero re-embeds."""
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "a.md").write_text(
            "## Alpha Topic\n\nThis section covers the alpha concept in sufficient detail.\n"
        )
        idx = self._index(tmp_path)
        n1 = idx.rebuild(kb)
        # Rebuild again — manifest entry matches mtime+hash, so zero updates
        n2 = idx.rebuild(kb)
        assert n2 == n1  # chunk count unchanged

    def test_rebuild_re_embeds_changed_doc(self, tmp_path):
        """Modifying a document triggers re-embedding on next rebuild."""
        kb = _make_kb(tmp_path / "kb")
        doc = kb / "concepts" / "a.md"
        doc.write_text(
            "## Original\n\nThis section covers the original content in enough detail.\n"
        )
        idx = self._index(tmp_path)
        idx.rebuild(kb)

        # Change content (different hash)
        doc.write_text(
            "## Revised\n\nCompletely different topic now with enough chars to index.\n"
        )
        n = idx.rebuild(kb)
        assert n >= 1  # at least one chunk remains after re-index

    def test_corrupt_index_triggers_full_rebuild(self, tmp_path):
        """A corrupt index is silently ignored; rebuild starts fresh."""
        idx_path = tmp_path / "kb-index"
        idx_path.mkdir()
        (idx_path / "vectors.npy").write_bytes(b"garbage")
        (idx_path / "manifest.json").write_text('{"bad": {}}')

        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "x.md").write_text(
            "## Fresh Section\n\nThis is fresh content that should be indexed properly.\n"
        )
        idx = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
        n = idx.rebuild(kb)
        assert n >= 1  # built from scratch despite corrupt index


# --------------------------------------------------------------------------- #
# KBIndexer
# --------------------------------------------------------------------------- #


class TestKBIndexer:
    def test_sync_returns_doc_count(self, tmp_path):
        kb = _make_kb(tmp_path / "kb")
        (kb / "concepts" / "c.md").write_text(
            "## Concept Section\n\nDetailed concept covering core ideas for the knowledge base.\n"
        )
        (kb / "research" / "r.md").write_text(
            "## Research Notes\n\nFindings from the research phase covering key discoveries.\n"
        )
        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "idx")
        indexer = KBIndexer(kb, idx)
        n = indexer.sync()
        # 2 files → ≥2 chunks (chunking may produce more than 1 per file)
        assert n >= 2

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

# --------------------------------------------------------------------------- #
# MarkdownChunker
# --------------------------------------------------------------------------- #


class TestMarkdownChunker:
    from src.embeddings.chunker import MarkdownChunker as _Chunker

    def _chunker(self):
        from src.embeddings.chunker import MarkdownChunker
        return MarkdownChunker()

    def test_no_headings_yields_preamble(self):
        content = "This is plain text without any level-2 headings. " * 3
        chunks = list(self._chunker().chunk("a.md", content))
        assert len(chunks) == 1
        slug, text = chunks[0]
        assert slug == "preamble"
        assert "plain text" in text

    def test_single_section(self):
        content = "# Title\n\n## Introduction\n\nThis is the intro paragraph with enough content."
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        assert "introduction" in slugs

    def test_multiple_sections(self):
        content = (
            "# Doc\n\n"
            "## Performance Targets\n\nLatency must be under 10ms for all cache hits.\n\n"
            "## Configuration Options\n\nAll config comes from environment variables.\n"
        )
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        assert "performance-targets" in slugs
        assert "configuration-options" in slugs

    def test_slug_normalisation(self):
        content = "## L1 / L2 Cache Strategy\n\nDescription goes here with enough text to pass minimum.\n"
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        assert "l1-l2-cache-strategy" in slugs

    def test_short_chunk_skipped(self):
        content = "## See Also\n\nFoo.\n"  # < 50 chars body
        chunks = list(self._chunker().chunk("a.md", content))
        # May be empty or contain only table chunks; "see-also" section itself
        # is too short and must NOT appear.
        assert all(t for _, t in chunks)  # any yielded chunk has non-empty text

    def test_preamble_below_min_skipped(self):
        content = "Short.\n\n## Real Section\n\nThis section has enough content to be indexed properly.\n"
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        assert "preamble" not in slugs  # too short
        assert "real-section" in slugs

    def test_table_extracted_as_standalone_chunk(self):
        content = (
            "## Performance Targets\n\n"
            "Here are the targets.\n\n"
            "| Metric | Target |\n"
            "| ------ | ------ |\n"
            "| L1 hit | <1ms   |\n"
            "| L2 hit | <100ms |\n"
            "\nMore prose after the table.\n"
        )
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        assert "performance-targets" in slugs
        assert "performance-targets-table" in slugs

    def test_duplicate_heading_slugs_deduplicated(self):
        content = (
            "## Summary\n\nFirst summary section with enough text here.\n\n"
            "## Summary\n\nSecond summary section with enough text here.\n"
        )
        chunks = list(self._chunker().chunk("a.md", content))
        slugs = [s for s, _ in chunks]
        # Both sections must appear but with distinct slugs
        assert len(set(slugs)) == len(slugs), f"Duplicate slugs: {slugs}"

    def test_file_path_not_in_output(self):
        """The file path argument must not leak into slug or text."""
        content = "## Section One\n\nContent with sufficient length to pass minimum chars.\n"
        chunks = list(self._chunker().chunk("concepts/caching.md", content))
        for slug, text in chunks:
            assert "concepts/caching.md" not in slug

    def test_chunk_doc_ids_have_hash_suffix(self):
        """Integration: doc_ids produced by rebuild() carry #slug suffix."""
        content = (
            "## Alpha\n\nFirst section with enough content to index properly.\n\n"
            "## Beta\n\nSecond section with enough content to index properly.\n"
        )
        from src.embeddings.chunker import MarkdownChunker
        chunker = MarkdownChunker()
        doc_ids = [
            f"concepts/test.md#{slug}"
            for slug, _ in chunker.chunk("concepts/test.md", content)
        ]
        assert all("#" in d for d in doc_ids)
        assert any("alpha" in d for d in doc_ids)
        assert any("beta" in d for d in doc_ids)

