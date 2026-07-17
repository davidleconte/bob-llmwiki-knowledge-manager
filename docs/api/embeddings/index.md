# index

PersistentEmbeddingIndex — disk-backed KB document embedding index.

Stores precomputed embeddings between Bob Shell sessions so unchanged documents
are not re-embedded on every query. Design decisions in ADR-015.

Fallback chain (ADR-015 §Corruption Recovery)::

    load from disk
        ↓ fail/corrupt
    silent full rebuild
        ↓ fail (disk full etc.)
    log warning + return empty search results

Nothing in this module blocks the KB query path — every failure degrades silently.

## Constants

- `DEFAULT_INDEX_PATH`

## Functions

### `_content_hash(content: str) -> str`

SHA-256 hex digest of UTF-8 *content*, truncated to 16 hex chars.


## Classes

### `PersistentEmbeddingIndex`

Disk-backed embedding index for semantic KB document search.

Eliminates per-session recompute: unchanged documents are loaded from
``.bob/kb-index/vectors.npy`` instead of re-embedded.

Thread-safety: **single-writer** (``KBIndexer``), **multi-reader**
(``KnowledgeBaseQuery`` instances in the same process). No cross-process
locking is implemented; concurrent writes from two processes will race.

Args:
    index_path: Directory for ``vectors.npy`` + ``manifest.json``.
        Defaults to ``.bob/kb-index/``.
    embedder: ``EmbeddingGenerator`` instance to use for new/changed docs.

#### Methods

##### `__init__(embedder: EmbeddingGenerator, index_path: Path) -> None`


##### `search(query: str, top_k: int) -> List[Tuple[str, float]]`

Semantic search over the indexed corpus.

Returns [(doc_id, score), ...] sorted by descending cosine similarity.
Returns an empty list if the index is empty or not yet built.

Args:
    query: Query text.
    top_k: Maximum results to return.

Returns:
    List of ``(doc_id, score)`` tuples, score in [0, 1].


##### `index_document(doc_id: str, content: str) -> None`

Embed *content* and update the in-memory index for *doc_id*.

Does **not** flush to disk — call :meth:`flush` or use
:class:`KBIndexer` which flushes after a full sync.

Args:
    doc_id: Unique identifier (typically the KB-relative file path).
    content: Document text. Truncated to 2000 chars before embedding
        (consistent with P1-1 ``use_cache=False`` guard, ADR-014).


##### `rebuild(kb_path: Path) -> int`

Full or incremental rebuild from *kb_path*.

Walks all ``*.md`` files in the four KB category directories.  For each
file, re-embeds if the mtime or content hash differs from the manifest.
Flushes the updated index to disk afterward.

Args:
    kb_path: Root of the knowledge base (``docs/knowledge-base/``).

Returns:
    Number of documents indexed (total corpus size after rebuild).


##### `is_stale(doc_path: Path) -> bool`

Check whether *doc_path* is newer or changed vs the manifest.

Args:
    doc_path: Absolute or relative path to a KB document.

Returns:
    ``True`` if the document needs re-indexing, ``False`` if up-to-date.


##### `flush() -> None`

Atomically persist the in-memory index to disk.

Writes ``vectors.npy`` and ``manifest.json`` under :attr:`_index_path`
using the atomic tmp-then-rename pattern (ADR-015 §Corruption Recovery).


##### `doc_count() -> int`

Number of documents currently in the in-memory index.


