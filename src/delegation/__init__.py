"""
Sub-Agent Delegation Framework
Enables parallel analysis through specialized sub-agents
"""

from .base import SubAgent, SubAgentPriority, SubAgentResult, SubAgentStatus, SubAgentTask
from .coordinator import DelegationCoordinator
from .pipeline import AnalysisPipelineResult, analyze_and_ingest
from .registry import SubAgentRegistry

__all__ = [
    "SubAgent",
    "SubAgentResult",
    "SubAgentTask",
    "SubAgentPriority",
    "SubAgentStatus",
    "DelegationCoordinator",
    "SubAgentRegistry",
    "analyze_and_ingest",
    "AnalysisPipelineResult",
]

__version__ = "1.2.0"
