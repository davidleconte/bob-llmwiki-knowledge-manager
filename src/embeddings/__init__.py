"""Persistent embedding layer for KB document search.

This package provides a disk-backed embedding index (``PersistentEmbeddingIndex``)
that stores precomputed document embeddings between Bob Shell sessions, eliminating
per-session recompute for unchanged documents.

Design decisions are recorded in ADR-015
(``docs/adr/015-persistent-embedding-index.md``).

Consumers
---------
- ``src/tools/kb_query.KnowledgeBaseQuery`` — optional index injection (P2-2)
- ``src/cache/multi_level_cache.MultiLevelCache`` — optional L3 (P2-3, future)

Cross-package dependency: ``src/embeddings/`` → ``src/cache/embeddings.EmbeddingGenerator``
This is legal under the layering gate (``src/ → scripts/`` only is forbidden).
"""

from src.embeddings.chunker import MarkdownChunker
from src.embeddings.index import PersistentEmbeddingIndex
from src.embeddings.indexer import KBIndexer
from src.embeddings.store import FileBackedVectorStore

__all__ = ["MarkdownChunker", "PersistentEmbeddingIndex", "KBIndexer", "FileBackedVectorStore"]
