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

Storage model (AF-1 fix):
    ``manifest.json`` holds ONLY chunk-level entries — one per vector row.
    ``staleness.json`` holds file-level mtime/hash sentinels — no vector rows.
    This keeps ``matrix.shape[0] == len(manifest)`` invariant, which
    ``FileBackedVectorStore.load()`` enforces as a corruption check.

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
    content: Document text. Truncated to 6000 chars before embedding
        (consistent with P1-1 ``use_cache=False`` guard, ADR-014).


##### `rebuild(kb_path: Path) -> int`

Full or incremental rebuild from *kb_path*.

Walks all ``*.md`` files in the four KB category directories.  For each
file, checks mtime+hash against the file-level staleness map.  Changed
files are split into structure-aware chunks by
:class:`~src.embeddings.chunker.MarkdownChunker`; each chunk becomes an
independent index row with a ``file.md#slug`` doc_id.  Flushes the
updated index to disk afterward.

Args:
    kb_path: Root of the knowledge base (``docs/knowledge-base/``).

Returns:
    Number of chunk-level rows in the index after rebuild.


##### `is_stale(doc_path: Path, kb_path: Optional[Path]) -> bool`

Check whether *doc_path* is newer or changed vs the staleness map.

Staleness is compared against the file-level ``_file_manifest``
(``staleness.json``), not against chunk entries in ``manifest.json``.

Args:
    doc_path: Absolute or relative path to a KB document.
    kb_path: Root of the knowledge base.  When provided, the key is
        derived as ``doc_path.relative_to(kb_path)`` (reliable for any
        KB location).  When ``None``, falls back to the hardcoded
        ``docs/knowledge-base`` convention (default install only).

Returns:
    ``True`` if the document needs re-indexing, ``False`` if up-to-date.


##### `stale_files(kb_path: Path) -> Dict[str, List[str]]`

Report KB files that are new/changed or deleted vs the index.

Read-only — does not modify the index. Used by the retrieval entrypoints
to warn (non-silently) that results may be stale, and to decide whether
an explicit refresh is worthwhile (W2-2b). ``changed`` includes files not
yet indexed; ``deleted`` are indexed files no longer on disk.

Returns ``{"changed": [file_doc_id, ...], "deleted": [file_doc_id, ...]}``.


##### `flush() -> None`

Atomically persist the in-memory index to disk.

Writes ``vectors.npy``, ``manifest.json`` (chunks only), and
``staleness.json`` (file-level sentinels) under :attr:`_index_path`
using the atomic tmp-then-rename pattern (ADR-015 §Corruption Recovery).


##### `doc_count() -> int`

Number of indexed chunks currently in the in-memory index.

Note: this counts *chunks* (``file.md#slug`` entries), not source
files.  A multi-section document contributes multiple chunks.


##### `embedder() -> 'EmbeddingGenerator'`

The :class:`~src.cache.embeddings.EmbeddingGenerator` used by this index.

Exposed as a public property so callers (e.g. :class:`KBIndexer`) do
not need to access the private ``_embedder`` attribute directly (AF-4 fix).


