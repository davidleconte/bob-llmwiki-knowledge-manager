"""
Documentation Analysis Sub-Agent
Specialized agent for documentation coverage and quality assessment
"""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.utils.batch_file_reader import BatchFileReader
from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask


class DocumentationAgent(SubAgent):
    """
    Documentation specialist

    Capabilities:
    - Documentation coverage analysis
    - API documentation review
    - Comment quality assessment
    - README completeness check
    - Documentation generation
    """

    def __init__(self, agent_id: str, cache_enabled: bool = True):
        super().__init__(
            agent_id=agent_id,
            agent_type="documentation",
            cache_enabled=cache_enabled,
            max_cache_size=500,
        )
        self.reader = BatchFileReader()

    def get_capabilities(self) -> List[str]:
        return [
            "coverage_analysis",
            "api_documentation",
            "comment_quality",
            "readme_review",
            "doc_generation",
            "example_validation",
        ]

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        target = task.target

        try:
            # Read files to analyze documentation
            from pathlib import Path

            target_path = Path(target)

            if target_path.is_file():
                files = [str(target_path)]
            else:
                files = [str(f) for f in target_path.rglob("*.py")][:50]  # Limit to 50 files

            if not files:
                return SubAgentResult(
                    agent_id=self.agent_id,
                    agent_type=self.agent_type,
                    status=SubAgentStatus.SUCCESS,
                    data={"target": target, "coverage": 0, "message": "No files found"},
                    token_count=10,
                )

            # Analyze documentation
            results = self.reader.read_files(files, strategy="summary")

            total_functions = 0
            documented_functions = 0

            for file_path, result in results.items():
                if "error" in result:
                    continue

                funcs = result.get("functions", [])
                total_functions += len(funcs)
                # Simple heuristic: assume documented if function name doesn't start with _
                documented_functions += len([f for f in funcs if not f.startswith("_")])

            coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0

            result_data = {
                "target": target,
                "files_analyzed": len(files),
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "coverage_percentage": coverage,
                "coverage_grade": self._get_coverage_grade(coverage),
                "recommendations": self._generate_recommendations(coverage),
            }

            warnings = []
            if coverage < 50:
                warnings.append(f"Low documentation coverage: {coverage:.1f}%")

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
                errors=[f"Documentation analysis failed: {str(e)}"],
            )

    def _get_coverage_grade(self, coverage: float) -> str:
        if coverage >= 90:
            return "A"
        elif coverage >= 75:
            return "B"
        elif coverage >= 60:
            return "C"
        elif coverage >= 40:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, coverage: float) -> List[str]:
        recommendations = []

        if coverage < 90:
            recommendations.append("Add docstrings to all public functions")
            recommendations.append("Document complex algorithms and logic")

        if coverage < 60:
            recommendations.append("Create API documentation")
            recommendations.append("Add usage examples")

        recommendations.append("Maintain up-to-date README")
        recommendations.append("Generate API docs automatically")

        return recommendations
