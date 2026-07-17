"""Knowledge graph layer for KB document relationship analysis.

Provides a lightweight pure-Python property graph over the KB document corpus
with the following capabilities:

- Multi-hop traversal (BFS neighbourhood)
- Structural health (orphan detection, hub ranking)
- PageRank-based re-ranking for search results
- Persistence to ``.bob/kb-graph.json`` (atomic JSON)

Design decisions: ADR-017 (``docs/adr/017-knowledge-graph-layer.md``).

Consumers
---------
- ``src/tools/kb_query.KnowledgeBaseQuery`` — optional graph injection (P3)
- ``src/cli`` — ``graph-build``, ``graph-query``, ``graph-health`` commands

Cross-package dependencies:
- ``src/graph/`` → ``src/embeddings/`` (optional, only for semantic edges)
- ``src/graph/`` is NOT imported by ``src/embeddings/`` (no circular dependency)
"""

from src.graph.builder import KnowledgeGraphBuilder
from src.graph.graph import Edge, KnowledgeGraph, NodeProps
from src.graph.ranker import GraphRanker
from src.graph.store import DEFAULT_GRAPH_PATH, GraphStore

__all__ = [
    "KnowledgeGraph",
    "NodeProps",
    "Edge",
    "KnowledgeGraphBuilder",
    "GraphStore",
    "GraphRanker",
    "DEFAULT_GRAPH_PATH",
]
