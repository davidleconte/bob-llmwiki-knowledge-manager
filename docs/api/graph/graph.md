# graph

Knowledge graph core — in-memory property graph over KB documents.

Nodes represent source files at `category/filename.md` granularity.
Edges are either `explicit` (author-stated: frontmatter `related:` or inline
markdown links) or `semantic` (similarity-derived from the embedding index).

All methods are pure — no filesystem I/O, no embedding computation.
I/O is handled by `GraphStore`. Building is handled by `KnowledgeGraphBuilder`.

Design decisions: ADR-017 (`docs/adr/017-knowledge-graph-layer.md`).

## Classes

### `NodeProps`

Properties attached to a KB document node.

All fields are optional so callers can add nodes with partial metadata.
Defaults ensure the graph is always traversable even on partial data.

**Fields:**

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | `"Untitled"` | Document title (from frontmatter or first `# heading`) |
| `category` | `str` | `""` | KB category directory (`concepts`, `guides`, `references`, `research`) |
| `tags` | `List[str]` | `[]` | Frontmatter tag list |
| `date` | `str` | `""` | Frontmatter date string |
| `type` | `str` | `""` | Frontmatter document type |
| `status` | `str` | `""` | Frontmatter status |

**Methods:**

#### `to_dict() -> Dict[str, Any]`

Serialise to a JSON-compatible dict.

#### `from_dict(d: Dict[str, Any]) -> NodeProps` *(classmethod)*

Deserialise from a dict produced by `to_dict()`.

---

### `Edge`

A directed, weighted, typed edge between two KB document nodes.

**Edge types:**
- `"explicit"` — author-stated (frontmatter `related:` or inline link); `weight = 1.0`
- `"semantic"` — similarity-derived (cosine ≥ threshold); `weight = cosine_score`
- `"broken"` — explicit link whose target file does not exist; `weight = 0.0`

**Fields:**

| Field | Type | Description |
|---|---|---|
| `source` | `str` | Source doc_id (`category/filename.md`) |
| `target` | `str` | Target doc_id |
| `type` | `str` | `"explicit"`, `"semantic"`, or `"broken"` |
| `weight` | `float` | Edge weight (see edge types above) |
| `label` | `Optional[str]` | Human-readable label (link text for explicit edges) |

**Methods:**

#### `to_dict() -> Dict[str, Any]`

Serialise to a JSON-compatible dict.

#### `from_dict(d: Dict[str, Any]) -> Edge` *(classmethod)*

Deserialise from a dict produced by `to_dict()`.

---

### `KnowledgeGraph`

In-memory property graph over KB documents.

Nodes are `category/filename.md` keys with `NodeProps`.
Edges are directed, weighted, typed; stored in an adjacency list
(`source → list[Edge]`) and a reverse index (`target → list[Edge]`)
for O(1) inbound-edge lookup.

All public methods are pure (no I/O). Thread-safety: not thread-safe;
build once with `KnowledgeGraphBuilder`, then read-only.

**Methods:**

#### `add_node(doc_id: str, **props: Any) -> None`

Add or update a node. Props are forwarded to `NodeProps`.

#### `add_edge(source: str, target: str, edge_type: str, weight: float = 1.0, label: Optional[str] = None) -> None`

Add a directed edge. Auto-creates node stubs if either endpoint is absent.

#### `node_count: int` *(property)*

Number of nodes in the graph.

#### `edge_count: int` *(property)*

Total number of edges (all types).

#### `nodes() -> Iterable[Tuple[str, NodeProps]]`

Iterate over `(doc_id, props)` pairs.

#### `out_edges(doc_id: str) -> List[Edge]`

Outbound edges from `doc_id`.

#### `in_edges(doc_id: str) -> List[Edge]`

Inbound edges into `doc_id`.

#### `get_node(doc_id: str) -> Optional[NodeProps]`

Return the `NodeProps` for `doc_id`, or `None` if absent.

#### `neighbours(doc_id: str, depth: int = 1, edge_types: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]`

BFS neighbourhood of `doc_id` up to `depth` hops.

Returns `{doc_id: {"distance": int, "edges": [Edge]}}` for all reachable nodes
(excluding the starting node itself).

#### `path(source: str, target: str) -> Optional[List[str]]`

Shortest path from `source` to `target` (BFS, unweighted).

Returns a list of doc_ids from `source` to `target` inclusive, or `None` if
no path exists.

#### `orphans(edge_types: Optional[List[str]] = None) -> List[str]`

Documents with zero inbound edges of the specified types.

Defaults to `["explicit"]`. Returns sorted list of orphan doc_ids.

#### `hubs(top_k: int = 10, edge_types: Optional[List[str]] = None) -> List[Tuple[str, int]]`

Documents ranked by inbound edge count (descending).

Returns list of `(doc_id, inbound_count)` tuples.

#### `pagerank(damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> Dict[str, float]`

Iterative power-method PageRank over all nodes.

Broken-link edges (`weight=0.0`) are excluded from the transition matrix.
Dangling nodes (no outbound edges with positive weight) distribute their score
uniformly. Returns `{doc_id: pagerank_score}` — scores sum to 1.0.

#### `to_dict() -> Dict[str, Any]`

Serialise the graph to a JSON-compatible dict (used by `GraphStore`).

#### `from_dict(d: Dict[str, Any]) -> KnowledgeGraph` *(classmethod)*

Deserialise from a dict produced by `to_dict()`.
