"""PersistentEmbeddingIndex — disk-backed KB document embedding index.

Stores precomputed embeddings between Bob Shell sessions so unchanged documents
are not re-embedded on every query. Design decisions in ADR-015.

Fallback chain (ADR-015 §Corruption Recovery)::

    load from disk
        ↓ fail/corrupt
    silent full rebuild
        ↓ fail (disk full etc.)
    log warning + return empty search results

Nothing in this module blocks the KB query path — every failure degrades silently.

Storage model (AF-1 fix):
    ``manifest.json`` holds ONLY chunk-level entries — one per vector row.
    ``staleness.json`` holds file-level mtime/hash sentinels — no vector rows.
    This keeps ``matrix.shape[0] == len(manifest)`` invariant, which
    ``FileBackedVectorStore.load()`` enforces as a corruption check.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.chunker import MarkdownChunker
from src.embeddings.store import FileBackedVectorStore

logger = logging.getLogger(__name__)

# Default index location (ADR-015 §Decision 1)
DEFAULT_INDEX_PATH = Path(".bob/kb-index")


class PersistentEmbeddingIndex:
    """Disk-backed embedding index for semantic KB document search.

    Eliminates per-session recompute: unchanged documents are loaded from
    ``.bob/kb-index/vectors.npy`` instead of re-embedded.

    Thread-safety: **single-writer** (``KBIndexer``), **multi-reader**
    (``KnowledgeBaseQuery`` instances in the same process). No cross-process
    locking is implemented; concurrent writes from two processes will race.

    Args:
        index_path: Directory for ``vectors.npy`` + ``manifest.json``.
            Defaults to ``.bob/kb-index/``.
        embedder: ``EmbeddingGenerator`` instance to use for new/changed docs.
    """

    def __init__(
        self,
        embedder: EmbeddingGenerator,
        index_path: Path = DEFAULT_INDEX_PATH,
    ) -> None:
        self._embedder = embedder
        self._index_path = Path(index_path)
        self._store = FileBackedVectorStore()

        # In-memory state: parallel lists kept in sync.
        # _doc_ids[i] corresponds to _matrix[i, :].
        self._doc_ids: List[str] = []
        # _manifest: chunk-level entries only — one per vector row.
        # Invariant: len(_manifest) == len(_doc_ids) == _matrix.shape[0]
        self._manifest: Dict[str, Any] = {}
        # _file_manifest: file-level staleness sentinels — NO vector rows.
        # Stored in staleness.json, never included in manifest.json.
        self._file_manifest: Dict[str, Any] = {}
        self._matrix: Optional[np.ndarray] = None  # [N × dim] float32
        # Cached per-row L2 norms (ATK-DOS-04 residual). Matrix-invariant, so
        # recomputed once after any _matrix mutation rather than on every query.
        # MUST be reset to None wherever _matrix is mutated (see _invalidate_norms).
        self._row_norms: Optional[np.ndarray] = None

        self._loaded = False

    def _invalidate_norms(self) -> None:
        """Drop the cached row-norms. Call after any mutation of ``self._matrix``."""
        self._row_norms = None

    def _get_row_norms(self) -> np.ndarray:
        """Per-row L2 norms of ``self._matrix``, recomputed only after a mutation."""
        if self._row_norms is None:
            assert self._matrix is not None  # callers guard on an empty matrix
            self._row_norms = np.linalg.norm(self._matrix, axis=1) + 1e-9
        return self._row_norms

    # ---------------------------------------------------------------------- #
    # Public interface (ADR-015)
    # ---------------------------------------------------------------------- #

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Semantic search over the indexed corpus.

        Returns [(doc_id, score), ...] sorted by descending cosine similarity.
        Returns an empty list if the index is empty or not yet built.

        Args:
            query: Query text.
            top_k: Maximum results to return.

        Returns:
            List of ``(doc_id, score)`` tuples, score in [0, 1].
        """
        self._ensure_loaded()

        if self._matrix is None or self._matrix.shape[0] == 0:
            return []

        q_vec = self._embedder.generate(query, use_cache=True)

        # Vectorised cosine similarity: single BLAS matrix-vector multiply.
        # Avoids O(N) Python loop; scales to thousands of KB documents without
        # degrading latency (ADR-015 performance requirement).
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-9)
        # cosine_i = (row_i . q_norm) / ||row_i||. The per-row norms are matrix-
        # invariant, so use the cache (recomputed only after a mutation) instead of
        # renormalising the whole matrix — and its full O(N*dim) copy — on every
        # query (ATK-DOS-04 residual: search is the hot retrieval path).
        row_norms = self._get_row_norms()
        sims = (self._matrix @ q_norm) / row_norms  # shape [N]
        scores: List[Tuple[str, float]] = list(zip(self._doc_ids, sims.tolist()))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def search_batch(
        self, queries: List[str], top_k: int = 10, _block: int = 512
    ) -> List[List[Tuple[str, float]]]:
        """Top-*k* semantic search for many queries in one batched pass.

        Parity-equivalent to ``[self.search(q, top_k) for q in queries]`` but
        computes every query-vs-corpus cosine similarity with a single (blocked)
        BLAS matrix–matrix product instead of one matrix–vector product per query,
        and ranks each row with one C-level ``np.lexsort`` instead of a Python
        ``list.sort`` over ``(doc_id, score)`` tuples.  The per-query loop was the
        dominant cold-build cost of
        :meth:`~src.graph.builder.KnowledgeGraphBuilder.build_semantic`
        (CODE-13/16: one full ``search`` per document → O(N_docs·N_chunks·dim)).

        Embeddings match :meth:`search` exactly: ``generate_batch`` transforms the
        queries with the same stateless backend, row for row.  The ranking key is
        ``(descending score, ascending row index)`` — identical to ``search``'s
        stable reverse-sort — so exact-tie groups (identical embeddings) resolve the
        same way at the *k*-th boundary.  Scores may differ from ``search`` only by
        BLAS reassociation (~1e-7), far below any edge threshold.

        Args:
            queries: Query texts (one per desired result list).
            top_k: Maximum results per query.
            _block: Query rows per matmul block; bounds the ``[block × N_chunks]``
                intermediate so a large corpus cannot blow up memory.

        Returns:
            One ``[(doc_id, score), ...]`` list per query, in query order. Each
            inner list is empty when the index is empty.
        """
        self._ensure_loaded()

        n = len(queries)
        if self._matrix is None or self._matrix.shape[0] == 0 or n == 0:
            return [[] for _ in range(n)]

        # Batched embed: one vectorizer.transform (hashing) / deterministic per-row
        # (minilm) — bit-identical to per-query generate(), so no drift vs search().
        embs = self._embedder.generate_batch(list(queries))
        q_mat = np.asarray(embs, dtype=self._matrix.dtype)  # [n × dim]
        q_norms = np.linalg.norm(q_mat, axis=1, keepdims=True) + 1e-9
        q_normed = q_mat / q_norms  # row-normalised, matching search()

        row_norms = self._get_row_norms()  # [N_chunks], cached (ATK-DOS-04)
        doc_ids = self._doc_ids
        n_chunks = self._matrix.shape[0]
        k = min(top_k, n_chunks)
        # Ascending index is the tie-break key; lexsort's LAST key is primary, so
        # (index, -score) ranks by descending score then ascending index — exactly
        # search()'s stable reverse-sort.
        idx_key = np.arange(n_chunks)

        results: List[List[Tuple[str, float]]] = []
        for start in range(0, n, _block):
            block = q_normed[start : start + _block]
            sims = (block @ self._matrix.T) / row_norms  # [b × N_chunks]
            for row in sims:
                order = np.lexsort((idx_key, -row))[:k]
                results.append([(doc_ids[j], float(row[j])) for j in order])
        return results

    def index_document(self, doc_id: str, content: str) -> None:
        """Embed *content* and update the in-memory index for *doc_id*.

        Does **not** flush to disk — call :meth:`flush` or use
        :class:`KBIndexer` which flushes after a full sync.

        Args:
            doc_id: Unique identifier (typically the KB-relative file path).
            content: Document text. Truncated to 6000 chars before embedding
                (consistent with P1-1 ``use_cache=False`` guard, ADR-014).
        """
        # use_cache=False: full document content must not bloat embeddings_cache
        vec = self._embedder.generate(content[:6000], use_cache=False)

        if doc_id in self._manifest:
            # Update existing row in-place
            idx = self._doc_ids.index(doc_id)
            if self._matrix is not None:
                self._matrix[idx] = vec.astype(np.float32)
                self._invalidate_norms()
        else:
            # Append new row and add a manifest entry (path/mtime/hash are unknown
            # at index_document time — set to sentinel values; rebuild() will
            # overwrite with real values when called from KBIndexer.sync()).
            self._doc_ids.append(doc_id)
            new_row = vec.astype(np.float32).reshape(1, -1)
            self._matrix = new_row if self._matrix is None else np.vstack([self._matrix, new_row])
            self._invalidate_norms()
            if doc_id not in self._manifest:
                self._manifest[doc_id] = {"path": doc_id, "mtime": 0.0, "hash": ""}

    def rebuild(self, kb_path: Path) -> int:
        """Full or incremental rebuild from *kb_path*.

        Walks all ``*.md`` files in the four KB category directories.  For each
        file, checks mtime+hash against the file-level staleness map.  Changed
        files are split into structure-aware chunks by
        :class:`~src.embeddings.chunker.MarkdownChunker`; each chunk becomes an
        independent index row with a ``file.md#slug`` doc_id.  Flushes the
        updated index to disk afterward.

        Args:
            kb_path: Root of the knowledge base (``docs/knowledge-base/``).

        Returns:
            Number of chunk-level rows in the index after rebuild.
        """
        self._ensure_loaded()
        categories = ["concepts", "guides", "references", "research"]
        chunker = MarkdownChunker()
        updated = 0
        seen_files: set[str] = set()

        for cat in categories:
            cat_path = kb_path / cat
            if not cat_path.exists():
                continue
            for md_file in sorted(cat_path.glob("*.md")):
                file_doc_id = str(md_file.relative_to(kb_path))
                seen_files.add(file_doc_id)
                try:
                    content = md_file.read_text(encoding="utf-8")
                except Exception:
                    continue

                mtime = md_file.stat().st_mtime
                chash = _content_hash(content)

                # Staleness is checked at the *file* level via _file_manifest
                # (separate from the chunk manifest — AF-1 fix).
                existing = self._file_manifest.get(file_doc_id, {})
                if existing.get("mtime") == mtime and existing.get("hash") == chash:
                    continue  # unchanged — skip all chunks for this file

                # CODE-11: drop this file's existing chunk rows before re-embedding
                # so sections removed from the file do not leave orphaned #slug rows
                # behind (index_document only appends/updates, never deletes).
                self._drop_chunks(self._chunks_for_file(file_doc_id))

                # Re-embed all chunks for this file.
                for slug, chunk_text in chunker.chunk(file_doc_id, content):
                    chunk_doc_id = f"{file_doc_id}#{slug}"
                    self.index_document(chunk_doc_id, chunk_text)

                # Record file-level staleness metadata in _file_manifest
                # (never written to manifest.json — kept in staleness.json).
                self._file_manifest[file_doc_id] = {
                    "path": str(md_file),
                    "mtime": mtime,
                    "hash": chash,
                }
                updated += 1

        # CODE-04: reconcile deletions. A file removed from disk is never visited
        # above, so its chunk rows would persist forever ("index grows forever").
        # Drop chunk rows + staleness sentinels for files no longer present.
        removed = self._reconcile_deletions(seen_files)

        if updated > 0 or removed > 0:
            if self._doc_ids:
                self.flush()
            else:
                # Everything was deleted — flush()'s empty-guard would leave the
                # stale on-disk rows behind, so remove the index directory instead.
                self._store.delete(self._index_path)
            logger.info(
                "kb_index_rebuilt updated=%d removed=%d total=%d",
                updated,
                removed,
                len(self._doc_ids),
            )

        return len(self._doc_ids)

    def _chunks_for_file(self, file_doc_id: str) -> set[str]:
        """All chunk doc_ids (``file.md#slug``) currently indexed for *file_doc_id*."""
        return {d for d in self._doc_ids if d.split("#")[0] == file_doc_id}

    def _drop_chunks(self, chunk_ids: set[str]) -> int:
        """Remove chunk rows and their manifest entries, keeping ``_doc_ids`` /
        ``_matrix`` / ``_manifest`` in sync.

        Returns the number of rows removed.
        """
        if not chunk_ids:
            return 0
        keep = [i for i, d in enumerate(self._doc_ids) if d not in chunk_ids]
        removed = len(self._doc_ids) - len(keep)
        if removed == 0:
            return 0
        self._doc_ids = [self._doc_ids[i] for i in keep]
        if self._matrix is not None:
            self._matrix = self._matrix[keep] if keep else None
            self._invalidate_norms()
        for cid in chunk_ids:
            self._manifest.pop(cid, None)
        return removed

    def _reconcile_deletions(self, seen_files: set[str]) -> int:
        """Drop chunk rows + staleness sentinels for files no longer on disk."""
        stale = {d for d in self._doc_ids if d.split("#")[0] not in seen_files}
        removed = self._drop_chunks(stale)
        for f in [f for f in self._file_manifest if f not in seen_files]:
            self._file_manifest.pop(f, None)
        return removed

    def is_stale(self, doc_path: Path, kb_path: Optional[Path] = None) -> bool:
        """Check whether *doc_path* is newer or changed vs the staleness map.

        Staleness is compared against the file-level ``_file_manifest``
        (``staleness.json``), not against chunk entries in ``manifest.json``.

        Args:
            doc_path: Absolute or relative path to a KB document.
            kb_path: Root of the knowledge base.  When provided, the key is
                derived as ``doc_path.relative_to(kb_path)`` (reliable for any
                KB location).  When ``None``, falls back to the hardcoded
                ``docs/knowledge-base`` convention (default install only).

        Returns:
            ``True`` if the document needs re-indexing, ``False`` if up-to-date.
        """
        self._ensure_loaded()

        # Derive the file_doc_id key used in _file_manifest.
        # AF-2 fix: accept an explicit kb_path instead of reconstructing it
        # from the index path (which only works for the default install).
        if kb_path is not None:
            try:
                file_doc_id = str(doc_path.relative_to(kb_path)).split("#")[0]
            except ValueError:
                file_doc_id = str(doc_path)
        else:
            # Legacy fallback: infer KB root from index path (default layout only)
            try:
                kb_root = self._index_path.parent.parent  # .bob/ → repo root
                file_doc_id = str(doc_path.relative_to(kb_root / "docs/knowledge-base")).split("#")[
                    0
                ]
            except ValueError:
                file_doc_id = str(doc_path)

        existing = self._file_manifest.get(file_doc_id)
        if existing is None:
            return True

        try:
            mtime = doc_path.stat().st_mtime
            content = doc_path.read_text(encoding="utf-8")
            chash = _content_hash(content)
        except Exception:
            return True

        return existing.get("mtime") != mtime or existing.get("hash") != chash

    def stale_files(self, kb_path: Path) -> Dict[str, List[str]]:
        """Report KB files that are new/changed or deleted vs the index.

        Read-only — does not modify the index. Used by the retrieval entrypoints
        to warn (non-silently) that results may be stale, and to decide whether
        an explicit refresh is worthwhile (W2-2b). ``changed`` includes files not
        yet indexed; ``deleted`` are indexed files no longer on disk.

        Returns ``{"changed": [file_doc_id, ...], "deleted": [file_doc_id, ...]}``.
        """
        self._ensure_loaded()
        on_disk: set[str] = set()
        changed: List[str] = []
        for cat in ("concepts", "guides", "references", "research"):
            cat_path = kb_path / cat
            if not cat_path.exists():
                continue
            for md_file in sorted(cat_path.glob("*.md")):
                file_doc_id = str(md_file.relative_to(kb_path))
                on_disk.add(file_doc_id)
                if self.is_stale(md_file, kb_path=kb_path):
                    changed.append(file_doc_id)
        deleted = sorted(set(self._file_manifest.keys()) - on_disk)
        return {"changed": changed, "deleted": deleted}

    def flush(self) -> None:
        """Atomically persist the in-memory index to disk.

        Writes ``vectors.npy``, ``manifest.json`` (chunks only), and
        ``staleness.json`` (file-level sentinels) under :attr:`_index_path`
        using the atomic tmp-then-rename pattern (ADR-015 §Corruption Recovery).
        """
        if self._matrix is None or len(self._doc_ids) == 0:
            return
        try:
            self._store.save(
                self._index_path,
                self._matrix,
                self._manifest,
                self._file_manifest,
            )
        except OSError as exc:
            logger.warning("kb_index_flush_failed: %s", exc)

    @property
    def doc_count(self) -> int:
        """Number of indexed chunks currently in the in-memory index.

        Note: this counts *chunks* (``file.md#slug`` entries), not source
        files.  A multi-section document contributes multiple chunks.
        """
        self._ensure_loaded()
        return len(self._doc_ids)

    @property
    def embedder(self) -> "EmbeddingGenerator":
        """The :class:`~src.cache.embeddings.EmbeddingGenerator` used by this index.

        Exposed as a public property so callers (e.g. :class:`KBIndexer`) do
        not need to access the private ``_embedder`` attribute directly (AF-4 fix).
        """
        return self._embedder

    # ---------------------------------------------------------------------- #
    # Private helpers
    # ---------------------------------------------------------------------- #

    def _ensure_loaded(self) -> None:
        """Load from disk on first access (lazy, called from all public methods)."""
        if self._loaded:
            return
        self._loaded = True
        result = self._store.load(self._index_path)
        if result is None:
            # New or corrupt index — start empty (rebuild on first explicit call)
            return
        matrix, manifest, staleness = result
        # CODE-15: enforce embedding-dimension match. store.load() only checks the
        # row count (shape[0]); a backend/dimension change (e.g. hashing→minilm,
        # 1000→384) would otherwise load a stale matrix and crash in search()'s
        # matmul. Discard the mismatched index instead — the next rebuild() call
        # regenerates it at the active dimension.
        if matrix.ndim != 2 or matrix.shape[1] != self._embedder.embedding_dim:
            logger.warning(
                "kb_index_dim_mismatch path=%s stored_dim=%s embedder_dim=%d — discarding stale index",
                self._index_path,
                matrix.shape[1] if matrix.ndim == 2 else "nd!=2",
                self._embedder.embedding_dim,
            )
            return
        self._matrix = matrix.astype(np.float32)
        self._invalidate_norms()
        self._manifest = manifest  # chunk-level entries only
        self._file_manifest = staleness  # file-level staleness sentinels
        self._doc_ids = list(manifest.keys())
        logger.debug("kb_index_loaded chunks=%d files=%d", len(self._doc_ids), len(staleness))


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _content_hash(content: str) -> str:
    """SHA-256 hex digest of UTF-8 *content*, truncated to 16 hex chars."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
