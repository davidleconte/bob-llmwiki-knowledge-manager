"""
Research Sub-Agent
Specialized agent for knowledge base research and information gathering
"""

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.utils.kb_query import KnowledgeBaseQuery
from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask


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
            self.kb = KnowledgeBaseQuery(kb_path)
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
