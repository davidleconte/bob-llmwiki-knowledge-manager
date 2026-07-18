# kb_query

Knowledge Base Query Utility.

Semantic search across knowledge base documents.

Scoring is keyword-based by default.  Pass an optional
:class:`~src.cache.embeddings.EmbeddingGenerator` to blend in cosine-similarity
scores via the ``embedding_weight`` parameter (0.0 = keyword only; 1.0 = embedding
only; values in between blend both scorers).

The embedding path is **opt-in** and defaults to pure keyword scoring
(``embedding_weight=0.0``) so existing callers are unaffected.  Before raising
the weight above 0, run an A/B validation test per ADR-014 to confirm that
embedding scores improve ``precision@3`` for your KB corpus.

Optionally pass a :class:`~src.graph.graph.KnowledgeGraph` together with a
``graph_weight`` to blend PageRank importance into result scores (ADR-017
Decision 7).  ``graph=None`` or ``graph_weight=0.0`` leaves behaviour identical
to today.

See ADR-014 (``docs/adr/014-kb-query-embedding-scorer.md``) for embedding
rationale and ADR-017 (``docs/adr/017-knowledge-graph-layer.md``) for graph
design decisions.

## Constants

- `_DATE_FIELD_RE`

## Functions

### `_doc_date_matches(file_key: str, kb_path: 'Path', date_filter: str) -> bool`

Return True if the document's frontmatter ``date:`` field starts with *date_filter*.

Reads the file from ``kb_path / file_key``.  Returns ``True`` when the
``date:`` field is absent or the file cannot be read (fail-open: don't drop
documents we can't inspect).

Args:
    file_key: KB-relative path (e.g. ``"research/notes.md"``).
    kb_path: Path object for the KB root.
    date_filter: ISO prefix to match against (e.g. ``"2026-07"``).

Returns:
    ``True`` if the document matches or cannot be determined.


### `main()`

CLI interface for knowledge base query


## Classes

### `KnowledgeBaseQuery`

Query knowledge base with keyword, embedding, and optional graph scoring.

Four-tier scoring chain (ADR-014, ADR-015, ADR-017)::

    PersistentEmbeddingIndex   →  EmbeddingGenerator (P1-1)  →  keyword scorer
        (fastest, persists)          (per-query, accurate)       (original)
                            ↓  (post-processing)
                      GraphRanker re-ranking (P3, optional)

Pass *index* for the P2 persistent path.  Pass *embedder* + *embedding_weight*
for the P1 per-query path.  Leave both ``None`` for pure keyword scoring.
Pass *graph* + *graph_weight* > 0 to enable PageRank re-ranking (P3).

Args:
    kb_path: Path to the knowledge base root directory.
    embedder: Optional :class:`~src.cache.embeddings.EmbeddingGenerator`
        instance.  When ``None`` (default) the scorer is keyword-only.
    embedding_weight: Blend weight for the embedding scorer in the range
        [0.0, 1.0].  ``0.0`` (default) means keyword-only; ``1.0`` means
        embedding-only.  Has no effect when *embedder* is ``None``.
    index: Optional :class:`~src.embeddings.index.PersistentEmbeddingIndex`.
        When provided, ``query()`` calls ``index.search()`` for the ranking
        pass instead of per-document embedding computation, then re-ranks
        the top-k candidates using the keyword scorer as a tie-breaker.
        Falls back to the embedder/keyword path if the index is empty.
    graph: Optional :class:`~src.graph.graph.KnowledgeGraph`.  When provided
        along with *graph_weight* > 0, a :class:`~src.graph.ranker.GraphRanker`
        post-processes the result list to blend PageRank importance into scores.
        ``None`` (default) disables graph re-ranking entirely.
    graph_weight: Blend weight for the graph PageRank scorer in [0.0, 1.0].
        ``0.0`` (default) means no graph re-ranking.  Has no effect when
        *graph* is ``None``.  See ADR-017 Decision 7 for the blend formula.

#### Methods

##### `__init__(kb_path: str)`


##### `query(query: str, categories: Optional[List[str]], max_results: int, include_content: bool, date_filter: Optional[str]) -> Dict`

Query the knowledge base.

When a :class:`~src.embeddings.index.PersistentEmbeddingIndex` was
injected at construction, the query is answered by:

1. ``index.search(query, top_k=max_results * 3)`` — fast semantic lookup
2. Load each returned document and apply the keyword scorer as a
   tie-breaker (blended at ``embedding_weight``).
3. Fall back silently to the full scan if the index returns nothing
   (empty or not yet built).

Args:
    query: Search query
    categories: Categories to search (``None`` = all)
    max_results: Maximum number of results
    include_content: Include full content in results
    date_filter: Optional ISO date prefix (e.g. ``"2026-07"``).  When
        set, only results whose frontmatter ``date:`` field starts with
        this string are returned.  ``None`` (default) disables filtering.

Returns:
    Dictionary with search results


##### `list_documents(category: Optional[str]) -> Dict`

List all documents in knowledge base


##### `get_cross_references(file_path: str) -> Dict`

Get cross-references for a document


##### `get_statistics() -> Dict`

Get knowledge base statistics


