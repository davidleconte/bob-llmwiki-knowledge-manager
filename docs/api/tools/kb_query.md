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

See ADR-014 (``docs/adr/014-kb-query-embedding-scorer.md``) for the design
rationale, quality trade-offs, and the ``use_cache=False`` memory-safety
requirement.

## Functions

### `main()`

CLI interface for knowledge base query


## Classes

### `KnowledgeBaseQuery`

Query knowledge base with keyword and optional embedding scoring.

Three-tier fallback chain (ADR-014, ADR-015)::

    PersistentEmbeddingIndex   →  EmbeddingGenerator (P1-1)  →  keyword scorer
        (fastest, persists)          (per-query, accurate)       (original)

Pass *index* for the P2 persistent path.  Pass *embedder* + *embedding_weight*
for the P1 per-query path.  Leave both ``None`` for pure keyword scoring.

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

#### Methods

##### `__init__(kb_path: str)`


##### `query(query: str, categories: Optional[List[str]], max_results: int, include_content: bool) -> Dict`

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

Returns:
    Dictionary with search results


##### `list_documents(category: Optional[str]) -> Dict`

List all documents in knowledge base


##### `get_cross_references(file_path: str) -> Dict`

Get cross-references for a document


##### `get_statistics() -> Dict`

Get knowledge base statistics


