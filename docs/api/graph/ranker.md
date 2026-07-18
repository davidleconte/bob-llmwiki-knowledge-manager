# ranker

GraphRanker — PageRank-based re-ranking for KnowledgeBaseQuery results.

Blends graph PageRank importance into the similarity scores returned by
:class:`~src.tools.kb_query.KnowledgeBaseQuery`, following the same score-blending
formula used for ``embedding_weight`` (ADR-017 Decision 7).

Design decisions: ADR-017.

## Constants

- `PAGERANK_SCALE`

## Classes

### `GraphRanker`

Re-rank search results by blending PageRank into similarity scores.

Args:
    graph: The :class:`~src.graph.graph.KnowledgeGraph` to use for PageRank
        and neighbourhood queries.

#### Methods

##### `__init__(graph: KnowledgeGraph) -> None`


##### `pagerank_scores() -> Dict[str, float]`

Return PageRank scores for all nodes, computed lazily and cached.

Scores are computed on first call and cached for the lifetime of this
:class:`GraphRanker` instance (graph topology is immutable after build).

Returns:
    ``{doc_id: pagerank_score}`` — scores sum to 1.0.


##### `rerank(results: List[Dict[str, Any]], weight: float) -> List[Dict[str, Any]]`

Blend PageRank into result scores and re-sort.

The blend formula (ADR-017 Decision 7)::

    blended = (1 - weight) * similarity_score
            + weight       * pagerank_score * PAGERANK_SCALE

Each result dict gains a ``"graph_score"`` field (the raw PageRank
score before scaling) for transparency.

Args:
    results: List of result dicts from ``KnowledgeBaseQuery.query()``.
        Each dict must have a ``"score"`` key and a ``"file"`` key.
    weight: Blend weight ∈ [0.0, 1.0].  ``0.0`` leaves scores unchanged.

Returns:
    The same list of dicts with updated ``"score"`` and added
    ``"graph_score"`` fields, re-sorted descending by ``"score"``.


##### `neighbourhood_context(doc_id: str, depth: int, edge_types: Optional[List[str]]) -> List[Dict[str, Any]]`

BFS neighbourhood of *doc_id* formatted for display.

Args:
    doc_id: Starting document.
    depth: Number of hops (default 1 = direct neighbours only).
    edge_types: Restrict traversal to these edge types (default: all).

Returns:
    List of dicts, each with keys:
    ``doc_id``, ``title``, ``category``, ``distance``, ``edge_type``,
    ``edge_weight``, sorted by (distance, doc_id).


