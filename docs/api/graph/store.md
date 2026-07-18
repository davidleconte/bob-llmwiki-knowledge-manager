# store

GraphStore — atomic JSON persistence for :class:`~src.graph.graph.KnowledgeGraph`.

Mirrors the atomic write pattern of :class:`~src.embeddings.store.FileBackedVectorStore`
(write-to-temp-then-rename) so a crash mid-write leaves the previous version intact.

Design decisions: ADR-017 Decision 4.

## Constants

- `DEFAULT_GRAPH_PATH`

## Classes

### `GraphStore`

Atomic read/write of :class:`~src.graph.graph.KnowledgeGraph` to JSON.

Storage layout (ADR-017)::

    .bob/kb-graph.json   — single flat JSON file
        {
          "nodes": {doc_id: NodeProps dict, ...},
          "edges": [Edge dict, ...],
          "metadata": {...}
        }

Writes are atomic: data goes to a temp file in the same directory then
``os.replace()`` (rename) so no partial file is ever visible.

#### Methods

##### `load(graph_path: Path) -> Optional[KnowledgeGraph]`

Load a :class:`~src.graph.graph.KnowledgeGraph` from *graph_path*.

Returns ``None`` if the file does not exist or is corrupt.

Args:
    graph_path: Path to the ``kb-graph.json`` file.

Returns:
    Loaded :class:`~src.graph.graph.KnowledgeGraph` or ``None``.


##### `save(graph_path: Path, graph: KnowledgeGraph, metadata: Optional[Dict[str, Any]]) -> None`

Atomically write *graph* to *graph_path*.

Creates parent directories if they do not exist.

Args:
    graph_path: Target ``kb-graph.json`` path.
    graph: Graph to serialise.
    metadata: Optional dict stored under the ``"metadata"`` key
        (e.g. build timestamp, kb_path, semantic_threshold).

Raises:
    OSError: If the directory cannot be created or the rename fails.


##### `delete(graph_path: Path) -> None`

Remove *graph_path*. No-op if absent.

Args:
    graph_path: Path to the ``kb-graph.json`` file.


