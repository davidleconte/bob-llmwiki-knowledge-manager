"""
Architecture Analysis Sub-Agent
Specialized agent for architecture and design pattern analysis
"""

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.utils.component_analyzer import ComponentAnalyzer
from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask


class ArchitectureAgent(SubAgent):
    """
    Architecture analysis specialist
    
    Capabilities:
    - Dependency analysis
    - Design pattern detection
    - Module coupling analysis
    - Architecture documentation
    - Component relationships
    """

    def __init__(self, agent_id: str, cache_enabled: bool = True):
        super().__init__(
            agent_id=agent_id,
            agent_type="architecture",
            cache_enabled=cache_enabled,
            max_cache_size=500
        )
        self.analyzer = ComponentAnalyzer()

    def get_capabilities(self) -> List[str]:
        return [
            "dependency_analysis",
            "pattern_detection",
            "coupling_analysis",
            "cohesion_analysis",
            "layering_analysis",
            "component_mapping",
            "architecture_documentation"
        ]

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        target = task.target
        depth = task.parameters.get("depth", "shallow")

        try:
            analysis = self.analyzer.analyze_component(
                target,
                analysis_type="architecture",
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

            arch_data = analysis.get("architecture", {})

            result_data = {
                "target": target,
                "total_files": arch_data.get("total_files", 0),
                "unique_imports": arch_data.get("unique_imports", arch_data.get("import_count", 0)),
                "imports": arch_data.get("imports", []),
                "dependencies": arch_data.get("dependencies", {}),
                "architecture_score": self._calculate_architecture_score(arch_data),
                "recommendations": self._generate_recommendations(arch_data),
                "analysis_depth": depth
            }

            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.SUCCESS,
                data=result_data,
                token_count=len(str(result_data)) // 4
            )

        except Exception as e:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"Architecture analysis failed: {str(e)}"]
            )

    def _calculate_architecture_score(self, arch_data: Dict) -> float:
        """Calculate architecture quality score (0-100)"""
        score = 100.0

        # Penalize excessive dependencies
        imports = arch_data.get("unique_imports", arch_data.get("import_count", 0))
        if imports > 50:
            score -= min((imports - 50) * 0.5, 20)

        return max(0, score)

    def _generate_recommendations(self, arch_data: Dict) -> List[str]:
        recommendations = []

        imports = arch_data.get("unique_imports", arch_data.get("import_count", 0))

        if imports > 50:
            recommendations.append("Consider reducing dependencies")
            recommendations.append("Review dependency injection patterns")

        recommendations.append("Document architecture decisions (ADRs)")
        recommendations.append("Maintain architecture diagrams")
        recommendations.append("Review module boundaries regularly")

        return recommendations
