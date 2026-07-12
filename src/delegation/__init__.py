"""
Sub-Agent Delegation Framework
Enables parallel analysis through specialized sub-agents
"""

from .base import SubAgent, SubAgentResult, SubAgentTask, SubAgentPriority, SubAgentStatus
from .coordinator import DelegationCoordinator
from .registry import SubAgentRegistry

__all__ = [
    "SubAgent",
    "SubAgentResult",
    "SubAgentTask",
    "SubAgentPriority",
    "SubAgentStatus",
    "DelegationCoordinator",
    "SubAgentRegistry",
]

__version__ = "1.0.0"
