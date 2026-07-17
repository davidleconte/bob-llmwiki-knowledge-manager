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


class FileBackedVectorStore:
    """Atomic read/write of a (matrix, manifest) pair to disk.

    Storage layout (ADR-015)::

        <index_path>/vectors.npy      float32 matrix  [N × embedding_dim]
        <index_path>/manifest.json    {doc_id: {path, mtime, content_hash}}

    All writes are atomic: data is written to a temp file in the same directory
    then renamed, so a crash mid-write leaves the previous version intact.
    """

    # ---------------------------------------------------------------------- #
    # Load
    # ---------------------------------------------------------------------- #

    def load(
        self, index_path: Path
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """Load (matrix, manifest) from *index_path*.

        Returns ``None`` if the index does not exist or is corrupt (caller
        should treat this as a cache-miss and trigger a full rebuild).

        Args:
            index_path: Directory containing ``vectors.npy`` and
                ``manifest.json``.

        Returns:
            ``(matrix, manifest)`` tuple, or ``None`` on any error.
        """
        vectors_path = index_path / VECTORS_FILE
        manifest_path = index_path / MANIFEST_FILE

        if not vectors_path.exists() or not manifest_path.exists():
            return None

        try:
            matrix = np.load(str(vectors_path), allow_pickle=False)
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest: Dict[str, Any] = json.load(f)
        except Exception as exc:
            logger.warning("kb_index_load_failed path=%s error=%s", index_path, exc)
            return None

        # Sanity check: rows must match manifest entries
        if matrix.ndim != 2 or matrix.shape[0] != len(manifest):
            logger.warning(
                "kb_index_shape_mismatch path=%s rows=%s manifest_entries=%d",
                index_path,
                matrix.shape[0] if matrix.ndim == 2 else "nd!=2",
                len(manifest),
            )
            return None

        return matrix, manifest

    # ---------------------------------------------------------------------- #
    # Save
    # ---------------------------------------------------------------------- #

    def save(
        self,
        index_path: Path,
        matrix: np.ndarray,
        manifest: Dict[str, Any],
    ) -> None:
        """Atomically write *matrix* and *manifest* to *index_path*.

        Uses a write-to-temp-then-rename pattern so a crash mid-write leaves
        the previous index intact (ADR-015 §Corruption Recovery).

        Args:
            index_path: Target directory (created if absent).
            matrix: float32 embedding matrix [N × dim].
            manifest: ``{doc_id: {path, mtime, content_hash}}`` mapping.

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

        # Write manifest atomically
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

        logger.debug("kb_index_saved docs=%d path=%s", len(manifest), index_path)

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
