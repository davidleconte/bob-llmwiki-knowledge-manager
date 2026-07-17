# store

`GraphStore` — atomic JSON persistence for `KnowledgeGraph`.

Reads and writes a single `.bob/kb-graph.json` file using an
atomic `os.replace()` pattern: the graph is serialised to a temp file in
the same directory, then atomically renamed over the target. This prevents
a partial write from corrupting the stored graph.

Design decisions: ADR-017 (`docs/adr/017-knowledge-graph-layer.md`).

## Constants

- `DEFAULT_GRAPH_PATH` — Default path for the persisted graph file:
  `Path(".bob/kb-graph.json")`.

## Classes

### `GraphStore`

Atomic JSON persistence for `KnowledgeGraph`.

**Constructor:**

```python
GraphStore()
```

No arguments — the path is passed to each method call.

**Methods:**

#### `load(graph_path: Path = DEFAULT_GRAPH_PATH) -> Optional[KnowledgeGraph]`

Load a `KnowledgeGraph` from `graph_path`.

Returns `None` (with a warning log) if the file does not exist, cannot be
parsed as JSON, or cannot be deserialised into a `KnowledgeGraph`. The caller
should treat `None` as "graph not yet built" and call `save()` after a fresh
build.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `graph_path` | `Path` | `DEFAULT_GRAPH_PATH` | Path to `kb-graph.json` |

#### `save(graph_path: Path, graph: KnowledgeGraph, metadata: Optional[Dict[str, Any]] = None) -> None`

Atomically write `graph` to `graph_path`.

Creates parent directories if they do not exist. The `metadata` dict
(e.g. `built_at`, `kb_path`, `semantic_threshold`) is stored under
the `"metadata"` key alongside the graph nodes and edges.

Raises `OSError` if the directory cannot be created or the rename fails.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `graph_path` | `Path` | required | Target `kb-graph.json` path |
| `graph` | `KnowledgeGraph` | required | Graph to serialise |
| `metadata` | `Optional[Dict[str, Any]]` | `None` | Optional build metadata |

#### `delete(graph_path: Path = DEFAULT_GRAPH_PATH) -> None`

Remove `graph_path`. No-op if the file is absent.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `graph_path` | `Path` | `DEFAULT_GRAPH_PATH` | Path to remove |
