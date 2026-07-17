# indexer

KBIndexer — drives PersistentEmbeddingIndex over a KB directory tree.

Provides a single ``sync()`` method that performs an incremental mtime/hash-based
rebuild: only documents that are new or changed since the last index flush are
re-embedded. Unchanged documents are skipped in O(1) per file (manifest lookup).

Typical usage::

    from pathlib import Path
    from src.cache.embeddings import EmbeddingGenerator
    from src.embeddings.index import PersistentEmbeddingIndex
    from src.embeddings.indexer import KBIndexer

    embedder = EmbeddingGenerator()
    index = PersistentEmbeddingIndex(embedder)
    indexer = KBIndexer(Path("docs/knowledge-base"), index)
    n_updated = indexer.sync()   # re-embeds only changed docs

See ADR-015 for design decisions.

## Constants

- `CATEGORIES`

## Classes

### `KBIndexer`

Incremental sync driver for :class:`PersistentEmbeddingIndex`.

Args:
    kb_path: Root of the knowledge base (e.g. ``docs/knowledge-base``).
    index: The persistent index to keep up-to-date.

#### Methods

##### `__init__(kb_path: Path, index: PersistentEmbeddingIndex) -> None`


##### `sync() -> int`

Incremental sync: re-embed only new or changed documents.

Walks all ``*.md`` files across the four KB category directories.
Delegates staleness detection and re-embedding to
:meth:`PersistentEmbeddingIndex.rebuild`, which handles the
mtime/hash comparison and atomic disk flush.

Returns:
    Total number of documents in the index after sync.


##### `query(query_text: str, top_k: int, embedding_weight: float) -> list`

Convenience method: sync index then search.

Builds a :class:`~src.tools.kb_query.KnowledgeBaseQuery` with the
persistent index injected and ``embedding_weight=0.7`` (the A/B
validated default, see ADR-014).

Args:
    query_text: Search query.
    top_k: Maximum results to return.
    embedding_weight: Blend weight passed to ``KnowledgeBaseQuery``
        (default 0.7 per A/B validation results 2026-07-16).

Returns:
    Result dict from ``KnowledgeBaseQuery.query()``.


