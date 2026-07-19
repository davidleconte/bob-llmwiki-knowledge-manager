"""
Research Sub-Agent
Specialized agent for knowledge base research and information gathering
"""

from pathlib import Path
from typing import Dict, List

from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask
from src.tools.kb_query import KnowledgeBaseQuery


class ResearchAgent(SubAgent):
    """
    Research specialist

    Capabilities:
    - Knowledge base querying
    - Cross-reference analysis
    - Information synthesis
    - Gap identification
    - Research documentation
    """

    def __init__(
        self, agent_id: str, kb_path: str = "docs/knowledge-base", cache_enabled: bool = True
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="research",
            cache_enabled=cache_enabled,
            max_cache_size=1000,
        )
        try:
            # CODE-02: load the canonical index and graph so the validated
            # p@3=0.88 stack is used instead of keyword-only search.
            from src.cache.embeddings import EmbeddingGenerator
            from src.embeddings.index import PersistentEmbeddingIndex
            from src.graph.store import GraphStore
            from src.kb_paths import resolve_graph_path, resolve_index_path

            _ra_kb_path = Path(kb_path)
            _ra_index = None
            _ra_graph = None
            _ra_embedding_weight = 0.0
            _ra_graph_weight = 0.0
            try:
                _ra_index_path = resolve_index_path(_ra_kb_path)
                if _ra_index_path.exists():
                    _ra_index = PersistentEmbeddingIndex(
                        EmbeddingGenerator(), index_path=_ra_index_path
                    )
                    if _ra_index.doc_count > 0:
                        _ra_embedding_weight = 0.7
            except Exception:
                _ra_index = None
            try:
                _ra_graph_path = resolve_graph_path(_ra_kb_path)
                if _ra_graph_path.exists():
                    _ra_graph = GraphStore().load(_ra_graph_path)
                    if _ra_graph is not None and _ra_graph.node_count > 0:
                        _ra_graph_weight = 0.3
            except Exception:
                _ra_graph = None

            self.kb: KnowledgeBaseQuery | None = KnowledgeBaseQuery(
                kb_path,
                index=_ra_index,
                graph=_ra_graph,
                embedding_weight=_ra_embedding_weight,
                graph_weight=_ra_graph_weight,
            )
        except ValueError:
            self.kb = None

    def get_capabilities(self) -> List[str]:
        return [
            "knowledge_base_query",
            "cross_reference_analysis",
            "information_synthesis",
            "gap_identification",
            "research_documentation",
            "topic_exploration",
        ]

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        if not self.kb:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=["Knowledge base not available"],
            )

        query = task.parameters.get("query", "")
        categories = task.parameters.get("categories")
        max_results = task.parameters.get("max_results", 10)

        try:
            # Query knowledge base
            results = self.kb.query(
                query=query, categories=categories, max_results=max_results, include_content=False
            )

            # Get statistics
            stats = self.kb.get_statistics()

            result_data = {
                "query": query,
                "total_results": results.get("total_results", 0),
                "results": results.get("results", []),
                "kb_statistics": stats,
                "recommendations": self._generate_recommendations(results),
            }

            warnings = []
            if results.get("total_results", 0) == 0:
                warnings.append(f"No results found for query: {query}")

            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.SUCCESS,
                data=result_data,
                warnings=warnings,
                token_count=len(str(result_data)) // 4,
            )

        except Exception as e:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"Research failed: {str(e)}"],
            )

    def _generate_recommendations(self, results: Dict) -> List[str]:
        recommendations = []

        total = results.get("total_results", 0)

        if total == 0:
            recommendations.append("Create new documentation for this topic")
            recommendations.append("Research external sources")
        elif total < 3:
            recommendations.append("Expand existing documentation")
            recommendations.append("Add more examples and use cases")
        else:
            recommendations.append("Review and consolidate existing documentation")
            recommendations.append("Update cross-references")

        return recommendations
