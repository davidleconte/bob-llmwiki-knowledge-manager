"""
Code Quality Analysis Sub-Agent
Specialized agent for code quality and maintainability assessment
"""

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.utils.component_analyzer import ComponentAnalyzer
from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask


class QualityAgent(SubAgent):
    """
    Code quality specialist
    
    Capabilities:
    - Complexity analysis
    - Code duplication detection
    - Maintainability scoring
    - Function length analysis
    - Code smell detection
    """

    def __init__(self, agent_id: str, cache_enabled: bool = True):
        super().__init__(
            agent_id=agent_id,
            agent_type="quality",
            cache_enabled=cache_enabled,
            max_cache_size=500
        )
        self.analyzer = ComponentAnalyzer()

    def get_capabilities(self) -> List[str]:
        return [
            "complexity_analysis",
            "duplication_detection",
            "maintainability_scoring",
            "function_analysis",
            "code_smell_detection",
            "naming_conventions",
            "documentation_coverage"
        ]

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        target = task.target
        depth = task.parameters.get("depth", "shallow")

        try:
            analysis = self.analyzer.analyze_component(
                target,
                analysis_type="quality",
                depth=depth
            )

            if "error" in analysis:
                return SubAgentResult(
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    status=SubAgentStatus.FAILED,
                    data={},
                    errors=[analysis["error"]]
                )

            quality_data = analysis.get("quality", {})

            # Calculate quality score
            quality_score = self._calculate_quality_score(quality_data)

            result_data = {
                "target": target,
                "line_count": quality_data.get("total_lines", quality_data.get("line_count", 0)),
                "function_count": quality_data.get("total_functions", quality_data.get("function_count", 0)),
                "long_functions": quality_data.get("long_functions", 0),
                "quality_score": quality_score,
                "quality_grade": self._get_quality_grade(quality_score),
                "recommendations": self._generate_recommendations(quality_data),
                "analysis_depth": depth
            }

            warnings = []
            if quality_data.get("long_functions", 0) > 5:
                warnings.append(f"Found {quality_data['long_functions']} long functions (>50 lines)")

            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.SUCCESS,
                data=result_data,
                warnings=warnings,
                token_count=len(str(result_data)) // 4
            )

        except Exception as e:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"Quality analysis failed: {str(e)}"]
            )

    def _calculate_quality_score(self, quality_data: Dict) -> float:
        """Calculate quality score (0-100)"""
        score = 100.0

        # Penalize long functions
        long_funcs = quality_data.get("long_functions", 0)
        score -= min(long_funcs * 5, 30)

        # Penalize high average line length
        avg_line_len = quality_data.get("avg_line_length", 0)
        if avg_line_len > 100:
            score -= 10

        return max(0, score)

    def _get_quality_grade(self, score: float) -> str:
        """Get quality grade from score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, quality_data: Dict) -> List[str]:
        recommendations = []

        if quality_data.get("long_functions", 0) > 0:
            recommendations.append("Refactor long functions into smaller, focused units")
            recommendations.append("Apply Single Responsibility Principle")

        recommendations.append("Maintain consistent code style")
        recommendations.append("Add comprehensive documentation")
        recommendations.append("Implement automated code quality checks")

        return recommendations
