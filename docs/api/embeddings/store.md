# store

FileBackedVectorStore — low-level NumPy .npy + JSON manifest persistence.

This module handles only I/O. Business logic (rebuild, staleness, search) lives
in ``PersistentEmbeddingIndex``. Nothing in this file imports from ``src/cache/``.

## Constants

- `VECTORS_FILE`
- `MANIFEST_FILE`
- `STALENESS_FILE`

## Classes

### `FileBackedVectorStore`

Atomic read/write of a (matrix, manifest, staleness) triple to disk.

Storage layout (ADR-015)::

    <index_path>/vectors.npy      float32 matrix  [N × embedding_dim]
    <index_path>/manifest.json    {chunk_doc_id: {path, mtime, hash}}
                                  — one entry per vector row (chunks only)
    <index_path>/staleness.json   {file_doc_id: {path, mtime, hash}}
                                  — file-level staleness sentinels only

All writes are atomic: data is written to a temp file in the same directory
then renamed, so a crash mid-write leaves the previous version intact.

#### Methods

##### `load(index_path: Path) -> Optional[Tuple[np.ndarray, Dict[str, Any], Dict[str, Any]]]`

Load (matrix, chunk_manifest, staleness) from *index_path*.

Returns ``None`` if the index does not exist or is corrupt (caller
should treat this as a cache-miss and trigger a full rebuild).

Args:
    index_path: Directory containing ``vectors.npy``,
        ``manifest.json``, and optionally ``staleness.json``.

Returns:
    ``(matrix, chunk_manifest, staleness)`` tuple, or ``None`` on
    any error.  *staleness* is an empty dict when ``staleness.json``
    is absent (graceful upgrade from old index layout).


##### `save(index_path: Path, matrix: np.ndarray, manifest: Dict[str, Any], staleness: Optional[Dict[str, Any]]) -> None`

Atomically write *matrix*, *manifest*, and *staleness* to *index_path*.

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


##### `delete(index_path: Path) -> None`

Remove the entire index directory (used by corruption-recovery path).

Args:
    index_path: Directory to remove. No-op if absent.


