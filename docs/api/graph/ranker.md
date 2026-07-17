# ranker

`GraphRanker` — PageRank-based re-ranking for `KnowledgeBaseQuery` results.

Blends graph PageRank importance into the similarity scores returned by
`KnowledgeBaseQuery`, following the same score-blending formula used for
`embedding_weight` (ADR-017 Decision 7).

Design decisions: ADR-017 (`docs/adr/017-knowledge-graph-layer.md`).

## Constants

- `PAGERANK_SCALE` — Scale factor (`15.0`) to bring PageRank scores into the
  same magnitude range as keyword scores (0–15+) and rescaled embedding scores
  (cosine × 15). PageRank scores are typically `1/N ≈ 0.013` for 80 docs;
  `× 15 ≈ 0.2`. The blend formula accounts for this via the weight parameter.

## Classes

### `GraphRanker`

Re-rank search results by blending PageRank into similarity scores.

**Constructor:**

```python
GraphRanker(graph: KnowledgeGraph)
```

| Parameter | Type | Description |
|---|---|---|
| `graph` | `KnowledgeGraph` | The graph to use for PageRank and neighbourhood queries. |

**Methods:**

#### `pagerank_scores() -> Dict[str, float]`

Return PageRank scores for all nodes, computed lazily and cached.

Scores are computed on first call and cached for the lifetime of this
`GraphRanker` instance (graph topology is immutable after build).

Returns `{doc_id: pagerank_score}` — scores sum to 1.0.

#### `rerank(results: List[Dict[str, Any]], weight: float) -> List[Dict[str, Any]]`

Blend PageRank into result scores and re-sort.

Blend formula (ADR-017 Decision 7):

```
blended = (1 - weight) * similarity_score
        + weight       * pagerank_score * PAGERANK_SCALE
```

Each result dict gains a `"graph_score"` field (the raw PageRank score before
scaling) for transparency. The list is re-sorted descending by `"score"`.

| Parameter | Type | Description |
|---|---|---|
| `results` | `List[Dict[str, Any]]` | Result dicts from `KnowledgeBaseQuery.query()`. Each must have `"score"` and `"file"` keys. |
| `weight` | `float` | Blend weight ∈ [0.0, 1.0]. `0.0` leaves scores unchanged. Validated default: `0.0`. |

Returns the same list with updated `"score"` and added `"graph_score"` fields.

#### `neighbourhood_context(doc_id: str, depth: int = 1, edge_types: Optional[List[str]] = None) -> List[Dict[str, Any]]`

BFS neighbourhood of `doc_id` formatted for display.

Returns list of dicts, each with keys:
`doc_id`, `title`, `category`, `distance`, `edge_type`, `edge_weight`,
sorted by `(distance, doc_id)`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `doc_id` | `str` | required | Starting document |
| `depth` | `int` | `1` | Number of hops (1 = direct neighbours only) |
| `edge_types` | `Optional[List[str]]` | `None` | Restrict traversal to these edge types (`None` = all) |
