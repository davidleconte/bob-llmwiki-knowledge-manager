"""GraphRanker — PageRank-based re-ranking for KnowledgeBaseQuery results.

Blends graph PageRank importance into the similarity scores returned by
:class:`~src.tools.kb_query.KnowledgeBaseQuery`, following the same score-blending
formula used for ``embedding_weight`` (ADR-017 Decision 7).

Design decisions: ADR-017.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.graph.graph import KnowledgeGraph

logger = logging.getLogger(__name__)

# Scale factor to bring PageRank scores into the same magnitude range as
# keyword scores (0–15+) and rescaled embedding scores (cosine × 15).
# PageRank scores are typically 1/N ≈ 0.013 for 78 docs; × 15 ≈ 0.2.
# The blend formula accounts for this via the weight parameter.
PAGERANK_SCALE = 15.0


class GraphRanker:
    """Re-rank search results by blending PageRank into similarity scores.

    Args:
        graph: The :class:`~src.graph.graph.KnowledgeGraph` to use for PageRank
            and neighbourhood queries.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph
        self._pr_cache: Optional[Dict[str, float]] = None

    def pagerank_scores(self) -> Dict[str, float]:
        """Return PageRank scores for all nodes, computed lazily and cached.

        Scores are computed on first call and cached for the lifetime of this
        :class:`GraphRanker` instance (graph topology is immutable after build).

        Returns:
            ``{doc_id: pagerank_score}`` — scores sum to 1.0.
        """
        if self._pr_cache is None:
            self._pr_cache = self._graph.pagerank()
        return self._pr_cache

    def rerank(
        self,
        results: List[Dict[str, Any]],
        weight: float,
    ) -> List[Dict[str, Any]]:
        """Blend PageRank into result scores and re-sort.

        The blend formula (ADR-017 Decision 7)::

            blended = (1 - weight) * similarity_score
                    + weight       * pagerank_score * PAGERANK_SCALE

        Each result dict gains a ``"graph_score"`` field (the raw PageRank
        score before scaling) for transparency.

        Args:
            results: List of result dicts from ``KnowledgeBaseQuery.query()``.
                Each dict must have a ``"score"`` key and a ``"file"`` key.
            weight: Blend weight ∈ [0.0, 1.0].  ``0.0`` leaves scores unchanged.

        Returns:
            The same list of dicts with updated ``"score"`` and added
            ``"graph_score"`` fields, re-sorted descending by ``"score"``.
        """
        if weight == 0.0 or not results:
            return results

        pr = self.pagerank_scores()

        # CODE-06 fix: min-max normalize PageRank scores within the result set.
        # Raw PageRank 1/N ≈ 0.013 for a 78-doc KB; ×15 ≈ 0.2 — still 75× smaller
        # than a 15-point keyword score at equal weight. Normalizing to [0,1] within
        # the candidate set makes the weight parameter behave as documented.
        pr_values = [pr.get(r.get("file", "").split("#")[0], 0.0) for r in results]
        pr_min = min(pr_values) if pr_values else 0.0
        pr_max = max(pr_values) if pr_values else 1.0
        pr_span = pr_max - pr_min or 1.0

        for result, pr_score in zip(results, pr_values):
            result["graph_score"] = pr_score
            norm_pr = (pr_score - pr_min) / pr_span  # 0.0 → 1.0 within result set

            similarity = result.get("score", 0.0)
            result["score"] = (1.0 - weight) * similarity + weight * norm_pr

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def neighbourhood_context(
        self,
        doc_id: str,
        depth: int = 1,
        edge_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """BFS neighbourhood of *doc_id* formatted for display.

        Args:
            doc_id: Starting document.
            depth: Number of hops (default 1 = direct neighbours only).
            edge_types: Restrict traversal to these edge types (default: all).

        Returns:
            List of dicts, each with keys:
            ``doc_id``, ``title``, ``category``, ``distance``, ``edge_type``,
            ``edge_weight``, sorted by (distance, doc_id).
        """
        neighbourhood = self._graph.neighbours(doc_id, depth=depth, edge_types=edge_types)

        output = []
        for neighbour_id, info in neighbourhood.items():
            node = self._graph.get_node(neighbour_id)
            # Pick the first edge in info["edges"] for display
            edges = info.get("edges", [])
            first_edge = edges[0] if edges else None

            output.append(
                {
                    "doc_id": neighbour_id,
                    "title": node.title if node else neighbour_id,
                    "category": node.category if node else "",
                    "distance": info["distance"],
                    "edge_type": first_edge.type if first_edge else "",
                    "edge_weight": round(first_edge.weight, 4) if first_edge else 0.0,
                }
            )

        output.sort(key=lambda x: (x["distance"], x["doc_id"]))
        return output
