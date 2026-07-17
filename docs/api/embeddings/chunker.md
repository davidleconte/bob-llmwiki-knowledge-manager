# chunker

`MarkdownChunker` — structure-aware chunking for KB `.md` files.

Splits a Markdown document on `##` (level-2) heading boundaries and extracts
GitHub-Flavoured Markdown (GFM) table blocks as independent chunks. Each
chunk gets a stable *slug* derived from its heading text so that doc IDs are
deterministic and meaningful (e.g. `concepts/caching.md#performance-targets`).

**Why level-2 only?**
The `#` title is the document heading — it names the whole file, not a
section. `##` headings are the natural section boundaries in KB documents.
`###` headings are left inside their parent `##` section.

**Minimum chunk length (50 chars):**
Stubs like `## See Also` with no body text produce near-zero information
and pollute the embedding index. Chunks shorter than `MIN_CHUNK_CHARS`
after stripping are skipped.

**GFM table extraction:**
A contiguous block of pipe-delimited lines (`|…|`) is extracted as a
standalone chunk with a `#<heading>-table` slug. Tables concentrate structured
data (e.g. performance targets, configuration options) into a small surface,
making them valuable for retrieval.

## Constants

- `MIN_CHUNK_CHARS` — Minimum body length in characters for a chunk to be
  indexed (default: `50`).

## Classes

### `MarkdownChunker`

Structure-aware Markdown document chunker.

**Constructor:**

```python
MarkdownChunker()
```

No arguments.

**Methods:**

#### `chunk(doc_id: str, content: str) -> Generator[Tuple[str, str], None, None]`

Split *content* into `(slug, text)` pairs.

Yields one tuple per chunk. Chunks shorter than `MIN_CHUNK_CHARS` are skipped.

| Parameter | Type | Description |
|---|---|---|
| `doc_id` | `str` | KB-relative file path (e.g. `concepts/caching.md`). Used only for logging; does not affect output. |
| `content` | `str` | Full Markdown document text. |

**Yields:** `(slug, text)` tuples where:
- `slug` is a URL-safe heading slug (e.g. `"performance-targets"` or `"performance-targets-table"`)
- `text` is the chunk body including the `## Heading` line

**Example:**

```python
from src.embeddings.chunker import MarkdownChunker

chunker = MarkdownChunker()
for slug, text in chunker.chunk("concepts/caching.md", content):
    doc_id = f"concepts/caching.md#{slug}"
    index.index_document(doc_id, text)
```
