# graph

Knowledge graph core — in-memory property graph over KB documents.

Nodes represent source files at ``category/filename.md`` granularity.
Edges are either ``explicit`` (author-stated: frontmatter ``related:`` or inline
markdown links) or ``semantic`` (similarity-derived from the embedding index).

All methods are pure — no filesystem I/O, no embedding computation.
I/O is handled by :class:`~src.graph.store.GraphStore`.
Building is handled by :class:`~src.graph.builder.KnowledgeGraphBuilder`.

Design decisions: ADR-017 (``docs/adr/017-knowledge-graph-layer.md``).

## Classes

### `NodeProps`

Properties attached to a KB document node.

All fields are optional so callers can add nodes with partial metadata.
Defaults ensure the graph is always traversable even on partial data.

P4 additions (backward-compatible — old ``kb-graph.json`` files load cleanly):
    mtime_epoch: File modification time as a Unix epoch float (0.0 = unknown).
    content_length: Document character count (0 = unknown).
    description: First non-heading paragraph, ≤ 200 chars (empty = none found).
    related_refs: Raw ``related:`` list from frontmatter (strings, not resolved).

#### Methods

##### `to_dict() -> Dict[str, Any]`


##### `from_dict(cls, d: Dict[str, Any]) -> 'NodeProps'`



### `Edge`

A directed, weighted, typed edge between two KB document nodes.

Edge types:
    ``explicit``  — author-stated (frontmatter ``related:`` or inline link)
    ``semantic``  — similarity-derived (cosine ≥ threshold)
    ``broken``    — explicit link whose target file does not exist

Weight:
    Explicit/broken edges carry ``weight = 1.0`` (or ``0.0`` for broken).
    Semantic edges carry the cosine similarity score ∈ (threshold, 1.0].

#### Methods

##### `to_dict() -> Dict[str, Any]`


##### `from_dict(cls, d: Dict[str, Any]) -> 'Edge'`



### `KnowledgeGraph`

In-memory property graph over KB documents.

**Nodes** — ``category/filename.md`` keys with :class:`NodeProps`.
**Edges** — directed, weighted, typed; stored in an adjacency list
(``source → list[Edge]``) and a reverse index (``target → list[Edge]``)
for O(1) inbound-edge lookup.

All public methods are pure (no I/O).

Thread-safety: not thread-safe; build once, then read-only.

#### Methods

##### `__init__() -> None`


##### `add_node(doc_id: str) -> None`

Add or update a node.

Args:
    doc_id: KB-relative file path (e.g. ``concepts/caching.md``).
    **props: Keyword arguments forwarded to :class:`NodeProps`.


##### `add_edge(source: str, target: str, edge_type: str, weight: float, label: Optional[str]) -> None`

Add a directed edge from *source* to *target*.

Auto-creates node stubs if either endpoint is not yet in the graph.

Args:
    source: Source doc_id.
    target: Target doc_id.
    edge_type: ``"explicit"``, ``"semantic"``, or ``"broken"``.
    weight: Edge weight (0.0–1.0 for semantic; 1.0 for explicit; 0.0 for broken).
    label: Optional human-readable label (link text for explicit edges).


##### `node_count() -> int`

Number of nodes in the graph.


##### `edge_count() -> int`

Total number of edges (all types) in the graph.


##### `nodes() -> Iterable[Tuple[str, NodeProps]]`

Iterate over (doc_id, props) pairs.


##### `out_edges(doc_id: str) -> List[Edge]`

Outbound edges from *doc_id*.


##### `in_edges(doc_id: str) -> List[Edge]`

Inbound edges into *doc_id*.


##### `get_node(doc_id: str) -> Optional[NodeProps]`

Return the :class:`NodeProps` for *doc_id*, or ``None`` if absent.


##### `neighbours(doc_id: str, depth: int, edge_types: Optional[List[str]]) -> Dict[str, Dict[str, Any]]`

BFS neighbourhood of *doc_id* up to *depth* hops.

Returns a dict mapping each reachable doc_id (excluding *doc_id*
itself) to ``{"distance": int, "edges": [Edge]}``.

Args:
    doc_id: Starting node.
    depth: Number of hops (1 = direct neighbours only).
    edge_types: Restrict traversal to these edge types. ``None`` = all types.

Returns:
    ``{doc_id: {"distance": int, "edges": [Edge]}}``


##### `path(source: str, target: str) -> Optional[List[str]]`

Shortest path from *source* to *target* (BFS, unweighted).

Returns a list of doc_ids from *source* to *target* inclusive,
or ``None`` if no path exists.

Args:
    source: Start node doc_id.
    target: End node doc_id.


##### `orphans(edge_types: Optional[List[str]]) -> List[str]`

Documents with zero inbound edges of the specified types.

Args:
    edge_types: Restrict check to these edge types (default: explicit only).

Returns:
    Sorted list of orphan doc_ids.


##### `hubs(top_k: int, edge_types: Optional[List[str]]) -> List[Tuple[str, int]]`

Documents ranked by inbound edge count (descending).

Args:
    top_k: Maximum results to return.
    edge_types: Restrict count to these edge types (default: all types).

Returns:
    List of ``(doc_id, inbound_count)`` tuples, descending.


##### `pagerank(damping: float, max_iter: int, tol: float) -> Dict[str, float]`

Iterative power-method PageRank over all nodes.

Broken-link edges (``weight=0.0``) are excluded from the transition
matrix. Semantic edge weights are used as transition weights (see ADR-017).

Args:
    damping: Damping factor (default 0.85 per ADR-017 Decision 5).
    max_iter: Maximum iterations before returning unconverged result.
    tol: L∞ convergence tolerance (max absolute per-node delta).

Returns:
    ``{doc_id: pagerank_score}`` — scores sum to 1.0.


##### `to_dict() -> Dict[str, Any]`

Serialise the graph to a JSON-compatible dict.


##### `from_dict(cls, d: Dict[str, Any]) -> 'KnowledgeGraph'`

Deserialise from a JSON-compatible dict (produced by :meth:`to_dict`).


