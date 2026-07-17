"""MarkdownChunker — structure-aware chunking for KB ``.md`` files.

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
"""

from __future__ import annotations

import re
from typing import Generator, Tuple

# Minimum body length in characters for a chunk to be indexed.
MIN_CHUNK_CHARS = 50

# Matches a GFM table: one or more consecutive lines starting with ``|``.
_TABLE_RE = re.compile(r"(\|.+\n)+", re.MULTILINE)


def _slugify(heading: str) -> str:
    """Convert *heading* text to a URL-safe slug.

    Rules (mirrors GitHub Markdown anchor generation):
    - Lowercase
    - Replace spaces and non-alphanumeric sequences with ``-``
    - Strip leading/trailing ``-``

    Examples::

        >>> _slugify("Performance Targets")
        'performance-targets'
        >>> _slugify("L1 / L2 Cache")
        'l1-l2-cache'
    """
    slug = heading.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


class MarkdownChunker:
    """Split a Markdown document into embeddable chunks.

    Each chunk is a ``(slug, text)`` pair where *slug* is suitable for
    appending to the file path as a fragment identifier.

    Two special cases are handled beyond simple ``##``-splitting:

    1. **Preamble** — text before the first ``##`` heading (often the intro
       paragraph after the ``#`` title) becomes a ``"preamble"`` chunk if it
       meets the minimum length requirement.
    2. **GFM tables** — a contiguous table block within a section is extracted
       as an extra ``"<section-slug>-table"`` chunk alongside the parent section.
    """

    def __init__(self, min_chunk_chars: int = MIN_CHUNK_CHARS) -> None:
        self._min_chars = min_chunk_chars

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk(self, _file_path: str, content: str) -> Generator[Tuple[str, str], None, None]:
        """Yield ``(slug, text)`` pairs from *content*.

        Args:
            _file_path: The KB-relative file path (e.g. ``concepts/caching.md``).
                Not used in chunking logic; kept for signature clarity.
            content: Raw Markdown text to chunk.

        Yields:
            ``(slug, text)`` pairs.  *slug* is a URL-safe string (no ``#``
            prefix).  *text* is the chunk body (may include the heading line).
        """
        sections = self._split_sections(content)
        seen_slugs: dict[str, int] = {}

        for heading, body in sections:
            slug = _slugify(heading) if heading else "preamble"

            # Deduplicate identical slugs (e.g. two ``## See Also`` headings)
            if slug in seen_slugs:
                seen_slugs[slug] += 1
                slug = f"{slug}-{seen_slugs[slug]}"
            else:
                seen_slugs[slug] = 0

            # Full section text (heading + body)
            if heading:
                section_text = f"## {heading}\n\n{body.strip()}"
            else:
                section_text = body.strip()

            if len(section_text) >= self._min_chars:
                yield slug, section_text

            # Extract GFM tables as standalone sub-chunks
            yield from self._extract_tables(slug, body)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _split_sections(self, content: str) -> Generator[Tuple[str | None, str], None, None]:
        """Split *content* on ``##`` heading boundaries.

        Yields ``(heading_text_or_None, body)`` pairs.  The first item has
        ``heading=None`` when there is preamble text before the first ``##``.
        """
        # Split on lines that start with exactly ``## `` (level-2 heading).
        # ``###`` and deeper are NOT treated as section boundaries.
        pattern = re.compile(r"^## (.+)$", re.MULTILINE)
        positions: list[tuple[int, str]] = [
            (m.start(), m.group(1).strip()) for m in pattern.finditer(content)
        ]

        if not positions:
            # No level-2 headings — yield the whole document as preamble.
            yield None, content
            return

        # Preamble (before first ## heading)
        preamble = content[: positions[0][0]]
        if preamble.strip():
            yield None, preamble

        # Section by section
        for i, (pos, heading) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(content)
            # Body = text after the heading line up to the next ## heading.
            line_end = content.index("\n", pos) if "\n" in content[pos:] else len(content)
            body = content[line_end:end]
            yield heading, body

    def _extract_tables(
        self, section_slug: str, body: str
    ) -> Generator[Tuple[str, str], None, None]:
        """Yield standalone table chunks found within *body*.

        Each table block produces a ``(slug, text)`` pair with slug
        ``"<section_slug>-table"`` (``"-table-2"``, ``"-table-3"`` for
        subsequent tables in the same section).
        """
        # Use finditer directly — findall with a capturing group returns only the
        # last captured repetition per match (AF-3 fix).
        for i, match in enumerate(_TABLE_RE.finditer(body)):
            table_text = match.group(0).strip()
            if len(table_text) < self._min_chars:
                continue
            suffix = "" if i == 0 else f"-{i + 1}"
            table_slug = f"{section_slug}-table{suffix}"
            yield table_slug, table_text
