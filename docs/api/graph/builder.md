# builder

`KnowledgeGraphBuilder` — builds a `KnowledgeGraph` from the KB filesystem.

Parses frontmatter `related:` lists and inline `[text](path)` markdown links
to produce `explicit` edges, then optionally derives `semantic` edges from
the `PersistentEmbeddingIndex`.

This is the only graph module that touches the filesystem or the embedding index.

Design decisions: ADR-017 (`docs/adr/017-knowledge-graph-layer.md`).

## Functions

### `build_graph_metadata(kb_path: Path, semantic_threshold: float, built_at: Optional[str] = None) -> Dict[str, Any]`

Produce the `metadata` dict written alongside the graph in `kb-graph.json`.

Returns a dict with `built_at`, `kb_path`, and `semantic_threshold` keys.

## Classes

### `KnowledgeGraphBuilder`

Build a `KnowledgeGraph` from the KB filesystem.

**Constructor:**

```python
KnowledgeGraphBuilder(
    kb_path: Path,
    index: Optional[PersistentEmbeddingIndex] = None,
    semantic_threshold: float = 0.3,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kb_path` | `Path` | required | Root of the knowledge base (`docs/knowledge-base`) |
| `index` | `Optional[PersistentEmbeddingIndex]` | `None` | When provided, semantic edges are derived from this index. When `None`, only explicit edges are added. |
| `semantic_threshold` | `float` | `0.3` | Minimum cosine similarity for a semantic edge (ADR-017 Decision 6; validated on 80-doc corpus). |

**Methods:**

#### `build() -> KnowledgeGraph`

Full build: add all nodes, explicit edges, and (if index is set) semantic edges.

Calls `_add_nodes()`, `build_explicit()`, and optionally `build_semantic()`.

#### `build_explicit(graph: KnowledgeGraph) -> int`

Parse frontmatter `related:` lists and inline markdown links → explicit edges.

Returns the number of explicit edges added. Nodes must already be in the graph.

Processes two sources per document:
1. Frontmatter `related:` list entries
2. Inline `[text](path)` links in the document body (after stripping frontmatter)

Links are normalised via `_normalise_kb_link()` to `category/filename.md` keys.
Missing targets produce `"broken"` edges (weight=0.0).

#### `build_semantic(graph: KnowledgeGraph, index: PersistentEmbeddingIndex) -> int`

Derive semantic edges from the embedding index.

For each document, queries the index for the top-50 most similar chunks.
Aggregates chunk-level cosine scores to a per-document score using **max**
(ADR-017 Decision 2). Adds a bidirectional semantic edge if the aggregated
score ≥ `semantic_threshold`.

Returns number of semantic edges added (each bidirectional pair counts as 1).
