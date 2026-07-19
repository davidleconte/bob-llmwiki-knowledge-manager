# builder

KnowledgeGraphBuilder — builds a KnowledgeGraph from the KB filesystem.

Parses frontmatter ``related:`` lists and inline ``[text](path)`` markdown links
to produce ``explicit`` edges, then optionally derives ``semantic`` edges from
the :class:`~src.embeddings.index.PersistentEmbeddingIndex`.

This is the only graph module that touches the filesystem or the embedding index.

Design decisions: ADR-017.

## Constants

- `_CATEGORIES`
- `_FRONTMATTER_RE`
- `_RELATED_ITEM_RE`
- `_FM_FIELD_RE`
- `_FM_TAGS_INLINE_RE`
- `_FM_TAGS_BLOCK_RE`
- `_LINK_RE`
- `_MAX_EXPLICIT_EDGES_PER_NODE`
- `_MAX_EXPLICIT_TOTAL_EDGES`
- `_QUARANTINE_TIER`
- `_DEFAULT_MAX_EDGES_PER_NODE`
- `_DEFAULT_MAX_TOTAL_EDGES`
- `_SEMANTIC_BUILD_MAX_DOCS`

## Functions

### `_parse_frontmatter(content: str) -> Dict[str, Any]`

Extract scalar and list fields from YAML frontmatter.

Returns an empty dict if no frontmatter block is found.
Only parses: title, date, type, status, tags, related.


### `_normalise_kb_link(raw_link: str, source_doc_id: str) -> Optional[str]`

Convert a raw link path to a KB-relative ``category/filename.md`` key.

Handles:
- Absolute KB-relative paths: ``concepts/caching.md``
- Relative paths with ``../``: ``../concepts/caching.md``
- Fragment links: ``../concepts/caching.md#section`` → ``concepts/caching.md``

Returns ``None`` for external URLs or unresolvable paths.


### `_extract_h1(content: str) -> str`

Extract the ``# Title`` line from a markdown document.


### `_extract_description(content: str) -> str`

Extract the first non-heading, non-blank paragraph from *content*.

Strips the YAML frontmatter block first, then skips blank lines and lines
that start with ``#``.  Returns the first non-empty paragraph truncated to
200 characters.  Returns ``""`` if nothing qualifies.

Args:
    content: Raw Markdown document text.

Returns:
    A short description string (≤ 200 chars) or ``""``.


### `build_graph_metadata(kb_path: Path, semantic_threshold: float, built_at: Optional[str]) -> Dict[str, Any]`

Produce the ``metadata`` dict written alongside the graph in ``kb-graph.json``.


## Classes

### `KnowledgeGraphBuilder`

Build a :class:`~src.graph.graph.KnowledgeGraph` from the KB filesystem.

Args:
    kb_path: Root of the knowledge base (``docs/knowledge-base``).
    index: Optional :class:`~src.embeddings.index.PersistentEmbeddingIndex`
        for semantic edge derivation.  When ``None``, only explicit edges
        are added.
    semantic_threshold: Minimum cosine similarity for a semantic edge
        (default 0.3 per ADR-017 Decision 6).

#### Methods

##### `__init__(kb_path: Path, index: Optional['PersistentEmbeddingIndex'], semantic_threshold: float) -> None`


##### `build() -> KnowledgeGraph`

Full build: add all nodes, explicit edges, and (if index is set) semantic edges.

Returns:
    A fully populated :class:`~src.graph.graph.KnowledgeGraph`.


##### `build_explicit(graph: KnowledgeGraph, max_edges_per_node: int, max_total_edges: int) -> int`

Parse frontmatter ``related:`` lists and inline links → explicit edges.

ATK-MEM-05: the explicit path is fully author-controlled, so a crafted
document could otherwise mint unbounded (and duplicate) edges and skew
PageRank. Targets are de-duplicated per source, per-source / global caps
mirror the semantic-edge caps (ATK-DOS-02), and quarantined documents
neither emit nor receive explicit edges.

Args:
    graph: Graph to populate (nodes must already be added).
    max_edges_per_node: Maximum explicit edges emitted by one source.
    max_total_edges: Global cap on explicit edges added.

Returns:
    Number of explicit edges added.


##### `build_semantic(graph: KnowledgeGraph, index: 'PersistentEmbeddingIndex', max_edges_per_node: int, max_total_edges: int) -> int`

Derive semantic edges from the embedding index.

For each document, queries the index for the top-k most similar chunks.
Aggregates chunk-level cosine scores to a per-document score using ``max``
(ADR-017 Decision 2).  Adds a bidirectional semantic edge if the
aggregated score ≥ ``self._semantic_threshold``.

ATK-DOS-02: *max_edges_per_node* and *max_total_edges* caps prevent an
O(N²) edge explosion when many documents are mutually similar.

Args:
    graph: Graph to populate.
    index: Pre-built :class:`~src.embeddings.index.PersistentEmbeddingIndex`.
    max_edges_per_node: Maximum outbound semantic edges per source node.
    max_total_edges: Global cap on total semantic edges added.

Returns:
    Number of semantic edges added (each bidirectional pair counts as 1).


