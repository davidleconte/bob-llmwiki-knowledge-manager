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
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.cache.embeddings import EmbeddingGenerator, cosine_similarity_vectors
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
        self._manifest: Dict[str, Any] = {}  # doc_id → {path, mtime, hash}
        self._matrix: Optional[np.ndarray] = None  # [N × dim] float32

        self._loaded = False

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

        scores: List[Tuple[str, float]] = []
        for i, doc_id in enumerate(self._doc_ids):
            sim = cosine_similarity_vectors(q_vec, self._matrix[i])
            scores.append((doc_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def index_document(self, doc_id: str, content: str) -> None:
        """Embed *content* and update the in-memory index for *doc_id*.

        Does **not** flush to disk — call :meth:`flush` or use
        :class:`KBIndexer` which flushes after a full sync.

        Args:
            doc_id: Unique identifier (typically the KB-relative file path).
            content: Document text. Truncated to 2000 chars before embedding
                (consistent with P1-1 ``use_cache=False`` guard, ADR-014).
        """
        # use_cache=False: full document content must not bloat embeddings_cache
        vec = self._embedder.generate(content[:2000], use_cache=False)

        if doc_id in self._manifest:
            # Update existing row in-place
            idx = self._doc_ids.index(doc_id)
            if self._matrix is not None:
                self._matrix[idx] = vec.astype(np.float32)
        else:
            # Append new row and add a manifest entry (path/mtime/hash are unknown
            # at index_document time — set to sentinel values; rebuild() will
            # overwrite with real values when called from KBIndexer.sync()).
            self._doc_ids.append(doc_id)
            new_row = vec.astype(np.float32).reshape(1, -1)
            self._matrix = new_row if self._matrix is None else np.vstack([self._matrix, new_row])
            if doc_id not in self._manifest:
                self._manifest[doc_id] = {"path": doc_id, "mtime": 0.0, "hash": ""}

    def rebuild(self, kb_path: Path) -> int:
        """Full or incremental rebuild from *kb_path*.

        Walks all ``*.md`` files in the four KB category directories.  For each
        file, re-embeds if the mtime or content hash differs from the manifest.
        Flushes the updated index to disk afterward.

        Args:
            kb_path: Root of the knowledge base (``docs/knowledge-base/``).

        Returns:
            Number of documents indexed (total corpus size after rebuild).
        """
        self._ensure_loaded()
        categories = ["concepts", "guides", "references", "research"]
        updated = 0

        for cat in categories:
            cat_path = kb_path / cat
            if not cat_path.exists():
                continue
            for md_file in sorted(cat_path.glob("*.md")):
                doc_id = str(md_file.relative_to(kb_path))
                try:
                    content = md_file.read_text(encoding="utf-8")
                except Exception:
                    continue

                mtime = md_file.stat().st_mtime
                chash = _content_hash(content)

                existing = self._manifest.get(doc_id, {})
                if existing.get("mtime") == mtime and existing.get("hash") == chash:
                    continue  # unchanged — skip

                self.index_document(doc_id, content)
                self._manifest[doc_id] = {
                    "path": str(md_file),
                    "mtime": mtime,
                    "hash": chash,
                }
                updated += 1

        if updated > 0:
            self.flush()
            logger.info("kb_index_rebuilt updated=%d total=%d", updated, len(self._doc_ids))

        return len(self._doc_ids)

    def is_stale(self, doc_path: Path) -> bool:
        """Check whether *doc_path* is newer or changed vs the manifest.

        Args:
            doc_path: Absolute or relative path to a KB document.

        Returns:
            ``True`` if the document needs re-indexing, ``False`` if up-to-date.
        """
        self._ensure_loaded()
        # Normalise to the relative path stored in the manifest
        try:
            kb_root = self._index_path.parent.parent  # .bob/ → repo root
            doc_id = str(doc_path.relative_to(kb_root / "docs/knowledge-base"))
        except ValueError:
            doc_id = str(doc_path)

        existing = self._manifest.get(doc_id)
        if existing is None:
            return True

        try:
            mtime = doc_path.stat().st_mtime
            content = doc_path.read_text(encoding="utf-8")
            chash = _content_hash(content)
        except Exception:
            return True

        return existing.get("mtime") != mtime or existing.get("hash") != chash

    def flush(self) -> None:
        """Atomically persist the in-memory index to disk.

        Writes ``vectors.npy`` and ``manifest.json`` under :attr:`_index_path`
        using the atomic tmp-then-rename pattern (ADR-015 §Corruption Recovery).
        """
        if self._matrix is None or len(self._doc_ids) == 0:
            return
        try:
            self._store.save(self._index_path, self._matrix, self._manifest)
        except OSError as exc:
            logger.warning("kb_index_flush_failed: %s", exc)

    @property
    def doc_count(self) -> int:
        """Number of documents currently in the in-memory index."""
        self._ensure_loaded()
        return len(self._doc_ids)

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
        matrix, manifest = result
        self._matrix = matrix.astype(np.float32)
        self._manifest = manifest
        self._doc_ids = list(manifest.keys())
        logger.debug("kb_index_loaded docs=%d", len(self._doc_ids))


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _content_hash(content: str) -> str:
    """SHA-256 hex digest of UTF-8 *content*, truncated to 16 hex chars."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
