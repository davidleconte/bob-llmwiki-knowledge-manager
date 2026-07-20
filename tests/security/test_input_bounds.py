"""A7 — global input-bound caps (DoS-surface hardening).

RED→GREEN regression for the four ceilings in ``src/limits.py``. Each test
exercises the boundary that enforces a cap and fails if the enforcement is
reverted:

  * ``test_oversized_file_skipped``   — MAX_FILE_BYTES  (embedding-index ingest)
  * ``test_chunks_per_doc_capped``    — MAX_CHUNKS_PER_DOC (chunker)
  * ``test_query_length_capped``      — MAX_QUERY_CHARS (query entry)
  * ``test_graph_nodes_capped``       — MAX_GRAPH_NODES (graph builder)

Limits are referenced through ``limits.*`` — never re-declared as literals — so a
change to the single home reflows every assertion automatically.
"""

from __future__ import annotations

import logging

from src import limits
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.chunker import MarkdownChunker
from src.embeddings.index import PersistentEmbeddingIndex
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.graph import KnowledgeGraph
from src.tools.kb_query import KnowledgeBaseQuery


def test_oversized_file_skipped(tmp_path, caplog):
    """A file larger than MAX_FILE_BYTES is skipped at ingest with a warning,
    and the rebuild still completes over the remaining docs."""
    kb = tmp_path / "kb"
    (kb / "concepts").mkdir(parents=True)
    (kb / "concepts" / "small.md").write_text(
        "# Small\n\n## Section\n\n" + "real searchable content here. " * 20,
        encoding="utf-8",
    )
    oversized = "# Big\n\n## Section\n\n" + ("x" * (limits.MAX_FILE_BYTES + 4096))
    (kb / "concepts" / "big.md").write_text(oversized, encoding="utf-8")

    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / ".bob" / "idx")
    with caplog.at_level(logging.WARNING):
        total = idx.rebuild(kb)

    indexed_files = {doc_id.split("#")[0] for doc_id in idx._doc_ids}
    assert "concepts/small.md" in indexed_files, "the normal doc must still index"
    assert "concepts/big.md" not in indexed_files, "the oversized doc must be skipped"
    assert total >= 1, "rebuild must complete over the remaining docs"
    assert "big.md" in caplog.text and "too_large" in caplog.text


def test_chunks_per_doc_capped(caplog):
    """A document with thousands of headings yields at most MAX_CHUNKS_PER_DOC
    chunks, with a warning."""
    n_headings = limits.MAX_CHUNKS_PER_DOC * 10
    body = "\n\n".join(
        f"## Heading number {i}\n\nEnough body text on this section to clear the min floor."
        for i in range(n_headings)
    )
    content = "# Doc\n\n" + body

    chunker = MarkdownChunker()
    with caplog.at_level(logging.WARNING):
        chunks = list(chunker.chunk("concepts/heading_bomb.md", content))

    assert len(chunks) <= limits.MAX_CHUNKS_PER_DOC, (
        f"chunker emitted {len(chunks)} chunks; cap is {limits.MAX_CHUNKS_PER_DOC}"
    )
    assert "max_chunks" in caplog.text


def test_query_length_capped(tmp_path, caplog):
    """A query longer than MAX_QUERY_CHARS is truncated at entry (not searched
    whole) with a warning."""
    kb = tmp_path / "kb"
    (kb / "concepts").mkdir(parents=True)
    (kb / "concepts" / "doc.md").write_text(
        "# Doc\n\n## Section\n\nHello world content for the scan.", encoding="utf-8"
    )

    seen: dict[str, str] = {}

    class _RecordingIndex:
        doc_count = 1

        def search(self, query: str, top_k: int):
            seen["query"] = query
            return []

    kbq = KnowledgeBaseQuery(str(kb), index=_RecordingIndex())
    long_query = "a" * (limits.MAX_QUERY_CHARS + 5000)

    with caplog.at_level(logging.WARNING):
        result = kbq.query(long_query)

    assert "error" not in result, result
    assert "truncated" in caplog.text
    # If the semantic path ran, the string it received must already be truncated.
    if "query" in seen:
        assert len(seen["query"]) <= limits.MAX_QUERY_CHARS


def test_graph_nodes_capped(tmp_path, caplog):
    """The graph builder admits at most MAX_GRAPH_NODES nodes, with a warning.

    Uses a small monkeypatched cap so the test stays fast while still exercising
    the real enforcement branch in ``builder._add_nodes``.
    """
    import src.graph.builder as builder_mod

    kb = tmp_path / "kb"
    (kb / "concepts").mkdir(parents=True)
    cap = 5
    for i in range(cap + 8):
        (kb / "concepts" / f"doc_{i:03d}.md").write_text(
            f"# Doc {i}\n\nBody {i}.", encoding="utf-8"
        )

    builder = KnowledgeGraphBuilder(kb)
    graph = KnowledgeGraph()
    original = limits.MAX_GRAPH_NODES
    builder_mod.MAX_GRAPH_NODES = cap
    try:
        with caplog.at_level(logging.WARNING):
            builder._add_nodes(graph)
    finally:
        builder_mod.MAX_GRAPH_NODES = original

    assert graph.node_count <= cap, f"admitted {graph.node_count} nodes; cap was {cap}"
    assert "nodes_capped" in caplog.text
