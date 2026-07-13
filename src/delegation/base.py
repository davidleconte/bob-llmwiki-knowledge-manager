"""
Base Sub-Agent Class
Foundation for all specialized sub-agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum


class SubAgentStatus(Enum):
    """Sub-agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubAgentPriority(Enum):
    """Sub-agent priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SubAgentResult:
    """Result from sub-agent execution"""
    
    agent_id: str
    agent_type: str
    status: SubAgentStatus
    data: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    token_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == SubAgentStatus.SUCCESS
    
    def has_errors(self) -> bool:
        """Check if there were errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there were warnings"""
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "execution_time_ms": self.execution_time_ms,
            "token_count": self.token_count,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class SubAgentTask:
    """Task to be executed by sub-agent"""
    
    task_id: str
    task_type: str
    target: str  # Component, file, or directory to analyze
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: SubAgentPriority = SubAgentPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    timeout_seconds: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3
    
    def can_execute(self, completed_tasks: set) -> bool:
        """Check if all dependencies are completed"""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def should_retry(self) -> bool:
        """Check if task should be retried"""
        return self.retry_count < self.max_retries


class SubAgent(ABC):
    """
    Base class for all sub-agents
    
    Sub-agents are specialized workers that perform specific analysis tasks
    in parallel. Each sub-agent has its own cache and operates independently.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        cache_enabled: bool = True,
        max_cache_size: int = 1000
    ):
        """
        Initialize sub-agent
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (e.g., "security", "performance")
            cache_enabled: Whether to enable caching
            max_cache_size: Maximum cache entries
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size
        
        # Local cache for this agent
        self._cache: Dict[str, Any] = {}
        self._status = SubAgentStatus.PENDING
        self._current_task: Optional[SubAgentTask] = None
        
        # Statistics
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._total_execution_time_ms = 0.0
        self._total_tokens = 0
    
    @abstractmethod
    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        """
        Perform analysis task
        
        Args:
            task: Task to execute
            
        Returns:
            SubAgentResult with analysis results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this agent provides
        
        Returns:
            List of capability names
        """
        pass
    
    def execute(self, task: SubAgentTask) -> SubAgentResult:
        """
        Execute a task with error handling and caching
        
        Args:
            task: Task to execute
            
        Returns:
            SubAgentResult with execution results
        """
        self._status = SubAgentStatus.RUNNING
        self._current_task = task
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Check cache if enabled
            if self.cache_enabled:
                cache_key = self._get_cache_key(task)
                if cache_key in self._cache:
                    cached_result = self._cache[cache_key]
                    cached_result.metadata["from_cache"] = True
                    return cached_result
            
            # Execute analysis
            result = self.analyze(task)
            
            # Update statistics
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            
            self._tasks_completed += 1
            self._total_execution_time_ms += execution_time
            self._total_tokens += result.token_count
            
            # Cache result if successful
            if self.cache_enabled and result.is_success():
                self._add_to_cache(task, result)
            
            self._status = SubAgentStatus.SUCCESS
            return result
            
        except Exception as e:
            self._tasks_failed += 1
            self._status = SubAgentStatus.FAILED
            
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=[str(e)],
                execution_time_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
        finally:
            self._current_task = None
    
    def _get_cache_key(self, task: SubAgentTask) -> str:
        """Generate cache key for task"""
        import hashlib
        import json
        
        # Create deterministic key from task
        key_data = {
            "type": task.task_type,
            "target": task.target,
            "params": task.parameters
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _add_to_cache(self, task: SubAgentTask, result: SubAgentResult):
        """Add result to cache"""
        cache_key = self._get_cache_key(task)
        
        # Evict oldest entry if cache is full
        if len(self._cache) >= self.max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[cache_key] = result
    
    def clear_cache(self):
        """Clear agent's cache"""
        self._cache.clear()
    
    def get_status(self) -> SubAgentStatus:
        """Get current status"""
        return self._status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self._status.value,
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "total_execution_time_ms": self._total_execution_time_ms,
            "total_tokens": self._total_tokens,
            "cache_size": len(self._cache),
            "cache_enabled": self.cache_enabled,
            "current_task": self._current_task.task_id if self._current_task else None
        }
    
    def reset(self):
        """Reset agent state"""
        self._status = SubAgentStatus.PENDING
        self._current_task = None
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._total_execution_time_ms = 0.0
        self._total_tokens = 0
        self.clear_cache()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id} type={self.agent_type} status={self._status.value}>"
