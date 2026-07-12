"""
Security Analysis Sub-Agent
Specialized agent for security audits and vulnerability detection
"""

from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.delegation.base import SubAgent, SubAgentTask, SubAgentResult, SubAgentStatus
from scripts.utils.component_analyzer import ComponentAnalyzer


class SecurityAgent(SubAgent):
    """
    Security analysis specialist
    
    Capabilities:
    - Vulnerability detection
    - Hardcoded secrets scanning
    - Authentication/authorization review
    - Cryptography analysis
    - Input validation checks
    """
    
    def __init__(self, agent_id: str, cache_enabled: bool = True):
        """Initialize security agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type="security",
            cache_enabled=cache_enabled,
            max_cache_size=500
        )
        self.analyzer = ComponentAnalyzer()
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "vulnerability_detection",
            "secret_scanning",
            "authentication_review",
            "authorization_review",
            "cryptography_analysis",
            "input_validation",
            "sql_injection_detection",
            "xss_detection",
            "security_best_practices"
        ]
    
    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        """
        Perform security analysis
        
        Args:
            task: Security analysis task
            
        Returns:
            SubAgentResult with security findings
        """
        target = task.target
        depth = task.parameters.get("depth", "shallow")
        
        try:
            # Use component analyzer for security analysis
            analysis = self.analyzer.analyze_component(
                target,
                analysis_type="security",
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
            
            # Extract security data
            security_data = analysis.get("security", {})
            
            # Categorize issues by severity
            issues_by_severity = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for issue in security_data.get("issues", []):
                severity = issue.get("severity", "low")
                issues_by_severity[severity].append(issue)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(security_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(security_data)
            
            result_data = {
                "target": target,
                "total_issues": security_data.get("total_issues", 0),
                "issues_by_severity": {
                    "critical": security_data.get("critical", 0),
                    "high": security_data.get("high", 0),
                    "medium": security_data.get("medium", 0),
                    "low": security_data.get("low", 0)
                },
                "issues": issues_by_severity,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "recommendations": recommendations,
                "analysis_depth": depth
            }
            
            # Add warnings for high-risk findings
            warnings = []
            if security_data.get("critical", 0) > 0:
                warnings.append(f"Found {security_data['critical']} critical security issues")
            if security_data.get("high", 0) > 5:
                warnings.append(f"Found {security_data['high']} high-severity issues")
            
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.SUCCESS,
                data=result_data,
                warnings=warnings,
                token_count=self._estimate_tokens(result_data)
            )
            
        except Exception as e:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"Security analysis failed: {str(e)}"]
            )
    
    def _calculate_risk_score(self, security_data: Dict) -> float:
        """Calculate overall risk score (0-100)"""
        critical = security_data.get("critical", 0)
        high = security_data.get("high", 0)
        medium = security_data.get("medium", 0)
        low = security_data.get("low", 0)
        
        # Weighted scoring
        score = (critical * 25) + (high * 10) + (medium * 3) + (low * 1)
        
        # Cap at 100
        return min(score, 100.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score >= 75:
            return "CRITICAL"
        elif risk_score >= 50:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, security_data: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        critical = security_data.get("critical", 0)
        high = security_data.get("high", 0)
        
        if critical > 0:
            recommendations.append("URGENT: Address critical security issues immediately")
            recommendations.append("Consider security code review by expert")
            recommendations.append("Implement automated security scanning in CI/CD")
        
        if high > 0:
            recommendations.append("Prioritize high-severity security issues")
            recommendations.append("Review authentication and authorization logic")
            recommendations.append("Audit input validation and sanitization")
        
        if security_data.get("medium", 0) > 10:
            recommendations.append("Schedule security refactoring sprint")
            recommendations.append("Update security dependencies")
        
        # Always recommend best practices
        recommendations.append("Follow OWASP security guidelines")
        recommendations.append("Enable security linting in development")
        recommendations.append("Conduct regular security audits")
        
        return recommendations
    
    def _estimate_tokens(self, data: Dict) -> int:
        """Estimate token count for result"""
        import json
        # Rough estimate: 1 token per 4 characters
        return len(json.dumps(data)) // 4
