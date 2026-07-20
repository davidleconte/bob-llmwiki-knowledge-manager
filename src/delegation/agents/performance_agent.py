"""
Performance Analysis Sub-Agent
Specialized agent for performance optimization and bottleneck detection
"""

from typing import Dict, List

from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask
from src.tools.component_analyzer import ComponentAnalyzer


class PerformanceAgent(SubAgent):
    """
    Performance analysis specialist

    Capabilities:
    - Bottleneck detection
    - Algorithm complexity analysis
    - Database query optimization
    - Memory usage analysis
    - Concurrency issues
    """

    def __init__(self, agent_id: str, cache_enabled: bool = True, base_path: str = "."):
        super().__init__(
            agent_id=agent_id,
            agent_type="performance",
            cache_enabled=cache_enabled,
            max_cache_size=500,
        )
        self.analyzer = ComponentAnalyzer(base_path=base_path)

    def get_capabilities(self) -> List[str]:
        return [
            "bottleneck_detection",
            "complexity_analysis",
            "query_optimization",
            "memory_profiling",
            "concurrency_analysis",
            "caching_opportunities",
            "n_plus_one_detection",
        ]

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        target = task.target
        depth = task.parameters.get("depth", "shallow")

        try:
            analysis = self.analyzer.analyze_component(
                target, analysis_type="performance", depth=depth
            )

            if "error" in analysis:
                return SubAgentResult(
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    status=SubAgentStatus.FAILED,
                    data={},
                    errors=[analysis["error"]],
                )

            perf_data = analysis.get("performance", {})

            result_data = {
                "target": target,
                "total_issues": perf_data.get("total_issues", 0),
                "issues": perf_data.get("issues", []),
                "optimization_score": self._calculate_optimization_score(perf_data),
                "recommendations": self._generate_recommendations(perf_data),
                "analysis_depth": depth,
            }

            warnings = []
            if perf_data.get("total_issues", 0) > 10:
                warnings.append(f"Found {perf_data['total_issues']} performance issues")

            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.SUCCESS,
                data=result_data,
                warnings=warnings,
                token_count=self.count_tokens(result_data),
            )

        except Exception as e:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"Performance analysis failed: {str(e)}"],
            )

    def _calculate_optimization_score(self, perf_data: Dict) -> float:
        """Calculate optimization score (0-100, higher is better)"""
        issues = perf_data.get("total_issues", 0)
        # Inverse scoring - fewer issues = higher score
        return max(0, 100 - (issues * 5))

    def _generate_recommendations(self, perf_data: Dict) -> List[str]:
        recommendations = []
        issues = perf_data.get("total_issues", 0)

        if issues > 0:
            recommendations.append("Profile application to identify hotspots")
            recommendations.append("Consider caching frequently accessed data")
            recommendations.append("Optimize database queries and add indexes")
            recommendations.append("Review algorithm complexity")

        recommendations.append("Implement performance monitoring")
        recommendations.append("Set performance budgets")

        return recommendations
