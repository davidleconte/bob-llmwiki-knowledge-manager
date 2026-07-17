"""FileBackedVectorStore — low-level NumPy .npy + JSON manifest persistence.

This module handles only I/O. Business logic (rebuild, staleness, search) lives
in ``PersistentEmbeddingIndex``. Nothing in this file imports from ``src/cache/``.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Filenames inside the index directory (ADR-015 §Decision 1)
VECTORS_FILE = "vectors.npy"
MANIFEST_FILE = "manifest.json"
STALENESS_FILE = "staleness.json"


class FileBackedVectorStore:
    """Atomic read/write of a (matrix, manifest, staleness) triple to disk.

    Storage layout (ADR-015)::

        <index_path>/vectors.npy      float32 matrix  [N × embedding_dim]
        <index_path>/manifest.json    {chunk_doc_id: {path, mtime, hash}}
                                      — one entry per vector row (chunks only)
        <index_path>/staleness.json   {file_doc_id: {path, mtime, hash}}
                                      — file-level staleness sentinels only

    All writes are atomic: data is written to a temp file in the same directory
    then renamed, so a crash mid-write leaves the previous version intact.
    """

    # ---------------------------------------------------------------------- #
    # Load
    # ---------------------------------------------------------------------- #

    def load(self, index_path: Path) -> Optional[Tuple[np.ndarray, Dict[str, Any], Dict[str, Any]]]:
        """Load (matrix, chunk_manifest, staleness) from *index_path*.

        Returns ``None`` if the index does not exist or is corrupt (caller
        should treat this as a cache-miss and trigger a full rebuild).

        Args:
            index_path: Directory containing ``vectors.npy``,
                ``manifest.json``, and optionally ``staleness.json``.

        Returns:
            ``(matrix, chunk_manifest, staleness)`` tuple, or ``None`` on
            any error.  *staleness* is an empty dict when ``staleness.json``
            is absent (graceful upgrade from old index layout).
        """
        vectors_path = index_path / VECTORS_FILE
        manifest_path = index_path / MANIFEST_FILE
        staleness_path = index_path / STALENESS_FILE

        if not vectors_path.exists() or not manifest_path.exists():
            return None

        try:
            matrix = np.load(str(vectors_path), allow_pickle=False)
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest: Dict[str, Any] = json.load(f)
        except Exception as exc:
            logger.warning("kb_index_load_failed path=%s error=%s", index_path, exc)
            return None

        # Sanity check: rows must match chunk manifest entries exactly.
        # staleness.json entries are NOT counted here — they are file-level
        # sentinels and have no corresponding vector row.
        if matrix.ndim != 2 or matrix.shape[0] != len(manifest):
            logger.warning(
                "kb_index_shape_mismatch path=%s rows=%s manifest_entries=%d",
                index_path,
                matrix.shape[0] if matrix.ndim == 2 else "nd!=2",
                len(manifest),
            )
            return None

        staleness: Dict[str, Any] = {}
        if staleness_path.exists():
            try:
                with open(staleness_path, "r", encoding="utf-8") as f:
                    staleness = json.load(f)
            except Exception as exc:
                logger.warning("kb_index_staleness_load_failed path=%s error=%s", index_path, exc)
                # Non-fatal: a missing staleness map causes a full re-index on
                # next rebuild, which is safe.

        return matrix, manifest, staleness

    # ---------------------------------------------------------------------- #
    # Save
    # ---------------------------------------------------------------------- #

    def save(
        self,
        index_path: Path,
        matrix: np.ndarray,
        manifest: Dict[str, Any],
        staleness: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Atomically write *matrix*, *manifest*, and *staleness* to *index_path*.

        Uses a write-to-temp-then-rename pattern so a crash mid-write leaves
        the previous index intact (ADR-015 §Corruption Recovery).

        Args:
            index_path: Target directory (created if absent).
            matrix: float32 embedding matrix [N × dim].  Rows must correspond
                1-to-1 with *manifest* entries (chunk-level only).
            manifest: ``{chunk_doc_id: {path, mtime, hash}}`` mapping.
                Must contain exactly ``matrix.shape[0]`` entries.
            staleness: ``{file_doc_id: {path, mtime, hash}}`` mapping of
                file-level staleness sentinels (no vector rows).  Written to
                ``staleness.json`` when provided.

        Raises:
            OSError: If the directory cannot be created or the rename fails.
        """
        index_path.mkdir(parents=True, exist_ok=True)

        # Write vectors atomically: write to a temp file in the same directory
        # then os.replace() (atomic rename) to avoid a torn write.
        # suffix=".npy" so np.save doesn't silently append ".npy" again
        vec_fd, vec_tmp = tempfile.mkstemp(dir=str(index_path), suffix=".npy")
        try:
            os.close(vec_fd)
            # allow_pickle=False: safe deterministic format
            np.save(vec_tmp, matrix.astype(np.float32), allow_pickle=False)
            os.replace(vec_tmp, str(index_path / VECTORS_FILE))
        except Exception:
            try:
                os.unlink(vec_tmp)
            except OSError:
                pass
            raise

        # Write chunk manifest atomically
        man_fd, man_tmp = tempfile.mkstemp(dir=str(index_path), suffix=".json.tmp")
        try:
            with os.fdopen(man_fd, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            os.replace(man_tmp, str(index_path / MANIFEST_FILE))
        except Exception:
            try:
                os.unlink(man_tmp)
            except OSError:
                pass
            raise

        # Write file-level staleness sentinels atomically (separate file)
        if staleness is not None:
            sta_fd, sta_tmp = tempfile.mkstemp(dir=str(index_path), suffix=".json.tmp")
            try:
                with os.fdopen(sta_fd, "w", encoding="utf-8") as f:
                    json.dump(staleness, f, indent=2)
                os.replace(sta_tmp, str(index_path / STALENESS_FILE))
            except Exception:
                try:
                    os.unlink(sta_tmp)
                except OSError:
                    pass
                raise

        logger.debug(
            "kb_index_saved chunks=%d files=%d path=%s",
            len(manifest),
            len(staleness) if staleness else 0,
            index_path,
        )

    # ---------------------------------------------------------------------- #
    # Delete
    # ---------------------------------------------------------------------- #

    def delete(self, index_path: Path) -> None:
        """Remove the entire index directory (used by corruption-recovery path).

        Args:
            index_path: Directory to remove. No-op if absent.
        """
        if index_path.exists():
            shutil.rmtree(index_path, ignore_errors=True)
            logger.info("kb_index_deleted path=%s", index_path)
