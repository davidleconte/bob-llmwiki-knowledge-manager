# chunker

MarkdownChunker — structure-aware chunking for KB ``.md`` files.

Splits a Markdown document on ``##`` (level-2) heading boundaries and extracts
GitHub-Flavoured Markdown (GFM) table blocks as independent chunks.  Each
chunk gets a stable *slug* derived from its heading text so that doc IDs are
deterministic and meaningful (e.g. ``concepts/caching.md#performance-targets``).

Why level-2 only?
    The ``#`` title is the document heading — it names the whole file, not a
    section.  ``##`` headings are the natural section boundaries in KB documents.
    ``###`` headings are left inside their parent ``##`` section (they don't
    create their own chunk).

Minimum chunk length (50 chars):
    Stubs like ``## See Also`` with no body text produce near-zero information
    and pollute the embedding index.  Chunks shorter than ``MIN_CHUNK_CHARS``
    after stripping are skipped.

GFM table extraction:
    A contiguous block of pipe-delimited lines (``|…|``) is extracted as a
    standalone chunk with a ``#<heading>-table`` slug.  Tables are valuable for
    retrieval because they concentrate structured data (e.g. "performance
    targets", "configuration options") into a small surface.

Usage::

    from src.embeddings.chunker import MarkdownChunker

    chunker = MarkdownChunker()
    for slug, text in chunker.chunk("concepts/caching.md", content):
        doc_id = f"concepts/caching.md#{slug}"
        index.index_document(doc_id, text)

## Constants

- `MIN_CHUNK_CHARS`
- `_TABLE_RE`

## Functions

### `_slugify(heading: str) -> str`

Convert *heading* text to a URL-safe slug.

Rules (mirrors GitHub Markdown anchor generation):
- Lowercase
- Replace spaces and non-alphanumeric sequences with ``-``
- Strip leading/trailing ``-``

Examples::

    >>> _slugify("Performance Targets")
    'performance-targets'
    >>> _slugify("L1 / L2 Cache")
    'l1-l2-cache'


## Classes

### `MarkdownChunker`

Split a Markdown document into embeddable chunks.

Each chunk is a ``(slug, text)`` pair where *slug* is suitable for
appending to the file path as a fragment identifier.

Two special cases are handled beyond simple ``##``-splitting:

1. **Preamble** — text before the first ``##`` heading (often the intro
   paragraph after the ``#`` title) becomes a ``"preamble"`` chunk if it
   meets the minimum length requirement.
2. **GFM tables** — a contiguous table block within a section is extracted
   as an extra ``"<section-slug>-table"`` chunk alongside the parent section.

#### Methods

##### `__init__(min_chunk_chars: int) -> None`


##### `chunk(_file_path: str, content: str) -> Generator[Tuple[str, str], None, None]`

Yield ``(slug, text)`` pairs from *content*.

Args:
    _file_path: The KB-relative file path (e.g. ``concepts/caching.md``).
        Not used in chunking logic; kept for signature clarity.
    content: Raw Markdown text to chunk.

Yields:
    ``(slug, text)`` pairs.  *slug* is a URL-safe string (no ``#``
    prefix).  *text* is the chunk body (may include the heading line).


