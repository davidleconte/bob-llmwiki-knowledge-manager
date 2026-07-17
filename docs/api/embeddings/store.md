# store

FileBackedVectorStore — low-level NumPy .npy + JSON manifest persistence.

This module handles only I/O. Business logic (rebuild, staleness, search) lives
in ``PersistentEmbeddingIndex``. Nothing in this file imports from ``src/cache/``.

## Constants

- `VECTORS_FILE`
- `MANIFEST_FILE`

## Classes

### `FileBackedVectorStore`

Atomic read/write of a (matrix, manifest) pair to disk.

Storage layout (ADR-015)::

    <index_path>/vectors.npy      float32 matrix  [N × embedding_dim]
    <index_path>/manifest.json    {doc_id: {path, mtime, content_hash}}

All writes are atomic: data is written to a temp file in the same directory
then renamed, so a crash mid-write leaves the previous version intact.

#### Methods

##### `load(index_path: Path) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]`

Load (matrix, manifest) from *index_path*.

Returns ``None`` if the index does not exist or is corrupt (caller
should treat this as a cache-miss and trigger a full rebuild).

Args:
    index_path: Directory containing ``vectors.npy`` and
        ``manifest.json``.

Returns:
    ``(matrix, manifest)`` tuple, or ``None`` on any error.


##### `save(index_path: Path, matrix: np.ndarray, manifest: Dict[str, Any]) -> None`

Atomically write *matrix* and *manifest* to *index_path*.

Uses a write-to-temp-then-rename pattern so a crash mid-write leaves
the previous index intact (ADR-015 §Corruption Recovery).

Args:
    index_path: Target directory (created if absent).
    matrix: float32 embedding matrix [N × dim].
    manifest: ``{doc_id: {path, mtime, content_hash}}`` mapping.

Raises:
    OSError: If the directory cannot be created or the rename fails.


##### `delete(index_path: Path) -> None`

Remove the entire index directory (used by corruption-recovery path).

Args:
    index_path: Directory to remove. No-op if absent.


