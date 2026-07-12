"""
Sub-Agent Registry
Manages registration and discovery of sub-agents
"""

from typing import Dict, List, Optional, Set
from .base import SubAgent, SubAgentTask


class SubAgentRegistry:
    """
    Registry for managing sub-agents
    
    Provides agent discovery and task routing
    """
    
    def __init__(self):
        """Initialize registry"""
        self._agents: Dict[str, SubAgent] = {}
        self._agents_by_type: Dict[str, List[SubAgent]] = {}
        self._capabilities: Dict[str, Set[str]] = {}  # agent_id -> capabilities
    
    def register(self, agent: SubAgent):
        """
        Register a sub-agent
        
        Args:
            agent: Sub-agent to register
        """
        # Store by ID
        self._agents[agent.agent_id] = agent
        
        # Store by type
        if agent.agent_type not in self._agents_by_type:
            self._agents_by_type[agent.agent_type] = []
        self._agents_by_type[agent.agent_type].append(agent)
        
        # Store capabilities
        self._capabilities[agent.agent_id] = set(agent.get_capabilities())
    
    def unregister(self, agent_id: str):
        """
        Unregister a sub-agent
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id not in self._agents:
            return
        
        agent = self._agents[agent_id]
        
        # Remove from type mapping
        if agent.agent_type in self._agents_by_type:
            self._agents_by_type[agent.agent_type] = [
                a for a in self._agents_by_type[agent.agent_type]
                if a.agent_id != agent_id
            ]
        
        # Remove from main registry
        del self._agents[agent_id]
        
        # Remove capabilities
        if agent_id in self._capabilities:
            del self._capabilities[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[SubAgent]:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            SubAgent or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[SubAgent]:
        """
        Get all agents of a specific type
        
        Args:
            agent_type: Agent type
            
        Returns:
            List of agents
        """
        return self._agents_by_type.get(agent_type, [])
    
    def get_agent_for_task(self, task: SubAgentTask) -> Optional[SubAgent]:
        """
        Find best agent for a task
        
        Args:
            task: Task to execute
            
        Returns:
            SubAgent or None if no suitable agent found
        """
        # First try to find agent by exact type match
        agents = self.get_agents_by_type(task.task_type)
        
        if agents:
            # Return least busy agent
            return min(agents, key=lambda a: a.get_statistics()["tasks_completed"])
        
        # Try to find agent with required capability
        required_capability = task.parameters.get("capability")
        if required_capability:
            for agent_id, capabilities in self._capabilities.items():
                if required_capability in capabilities:
                    return self._agents[agent_id]
        
        return None
    
    def get_all_agents(self) -> List[SubAgent]:
        """Get all registered agents"""
        return list(self._agents.values())
    
    def get_agent_types(self) -> List[str]:
        """Get all registered agent types"""
        return list(self._agents_by_type.keys())
    
    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        return {
            "total_agents": len(self._agents),
            "agent_types": len(self._agents_by_type),
            "agents_by_type": {
                agent_type: len(agents)
                for agent_type, agents in self._agents_by_type.items()
            }
        }
    
    def clear(self):
        """Clear all registrations"""
        self._agents.clear()
        self._agents_by_type.clear()
        self._capabilities.clear()
