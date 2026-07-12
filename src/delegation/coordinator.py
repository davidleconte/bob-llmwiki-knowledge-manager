"""
Delegation Coordinator
Orchestrates parallel execution of sub-agents
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import time

from .base import SubAgent, SubAgentTask, SubAgentResult, SubAgentStatus, SubAgentPriority
from .registry import SubAgentRegistry


class DelegationCoordinator:
    """
    Coordinates parallel execution of sub-agents
    
    Manages task distribution, dependency resolution, and result aggregation
    """
    
    def __init__(
        self,
        max_workers: int = 5,
        timeout_seconds: int = 600,
        enable_retry: bool = True
    ):
        """
        Initialize coordinator
        
        Args:
            max_workers: Maximum number of parallel workers
            timeout_seconds: Global timeout for all tasks
            enable_retry: Whether to retry failed tasks
        """
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.enable_retry = enable_retry
        
        self.registry = SubAgentRegistry()
        
        # Execution state
        self._tasks: Dict[str, SubAgentTask] = {}
        self._results: Dict[str, SubAgentResult] = {}
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        
        # Statistics
        self._total_execution_time_ms = 0.0
        self._total_tokens = 0
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
    
    def register_agent(self, agent: SubAgent):
        """Register a sub-agent"""
        self.registry.register(agent)
    
    def add_task(self, task: SubAgentTask):
        """Add a task to be executed"""
        self._tasks[task.task_id] = task
    
    def add_tasks(self, tasks: List[SubAgentTask]):
        """Add multiple tasks"""
        for task in tasks:
            self.add_task(task)
    
    def execute_parallel(self) -> Dict[str, SubAgentResult]:
        """
        Execute all tasks in parallel with dependency resolution
        
        Returns:
            Dictionary mapping task IDs to results
        """
        self._start_time = datetime.utcnow()
        self._results.clear()
        self._completed_tasks.clear()
        self._failed_tasks.clear()
        
        # Sort tasks by priority
        sorted_tasks = sorted(
            self._tasks.values(),
            key=lambda t: t.priority.value,
            reverse=True
        )
        
        # Execute tasks in waves based on dependencies
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            remaining_tasks = set(task.task_id for task in sorted_tasks)
            
            while remaining_tasks:
                # Find tasks that can be executed (dependencies met)
                executable_tasks = [
                    self._tasks[task_id]
                    for task_id in remaining_tasks
                    if self._tasks[task_id].can_execute(self._completed_tasks)
                ]
                
                if not executable_tasks:
                    # Deadlock - circular dependencies or all remaining tasks failed
                    for task_id in remaining_tasks:
                        self._results[task_id] = SubAgentResult(
                            agent_id="coordinator",
                            agent_type="system",
                            status=SubAgentStatus.FAILED,
                            data={},
                            errors=["Task dependencies not met or circular dependency detected"]
                        )
                        self._failed_tasks.add(task_id)
                    break
                
                # Submit executable tasks
                future_to_task = {
                    executor.submit(self._execute_task, task): task
                    for task in executable_tasks
                }
                
                # Wait for completion
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result(timeout=task.timeout_seconds)
                        self._results[task.task_id] = result
                        
                        if result.is_success():
                            self._completed_tasks.add(task.task_id)
                        else:
                            self._failed_tasks.add(task.task_id)
                            
                            # Retry if enabled
                            if self.enable_retry and task.should_retry():
                                task.retry_count += 1
                                continue  # Don't remove from remaining_tasks
                        
                        remaining_tasks.discard(task.task_id)
                        
                        # Update statistics
                        self._total_execution_time_ms += result.execution_time_ms
                        self._total_tokens += result.token_count
                        
                    except Exception as e:
                        self._results[task.task_id] = SubAgentResult(
                            agent_id="coordinator",
                            agent_type="system",
                            status=SubAgentStatus.FAILED,
                            data={},
                            errors=[f"Execution error: {str(e)}"]
                        )
                        self._failed_tasks.add(task.task_id)
                        remaining_tasks.discard(task.task_id)
        
        self._end_time = datetime.utcnow()
        return self._results
    
    def _execute_task(self, task: SubAgentTask) -> SubAgentResult:
        """Execute a single task"""
        # Find appropriate agent
        agent = self.registry.get_agent_for_task(task)
        
        if not agent:
            return SubAgentResult(
                agent_id="coordinator",
                agent_type="system",
                status=SubAgentStatus.FAILED,
                data={},
                errors=[f"No agent available for task type: {task.task_type}"]
            )
        
        # Execute task
        return agent.execute(task)
    
    def get_results(self) -> Dict[str, SubAgentResult]:
        """Get all results"""
        return self._results.copy()
    
    def get_successful_results(self) -> Dict[str, SubAgentResult]:
        """Get only successful results"""
        return {
            task_id: result
            for task_id, result in self._results.items()
            if result.is_success()
        }
    
    def get_failed_results(self) -> Dict[str, SubAgentResult]:
        """Get only failed results"""
        return {
            task_id: result
            for task_id, result in self._results.items()
            if not result.is_success()
        }
    
    def get_statistics(self) -> Dict:
        """Get execution statistics"""
        total_time_ms = 0.0
        if self._start_time and self._end_time:
            total_time_ms = (self._end_time - self._start_time).total_seconds() * 1000
        
        return {
            "total_tasks": len(self._tasks),
            "completed_tasks": len(self._completed_tasks),
            "failed_tasks": len(self._failed_tasks),
            "success_rate": len(self._completed_tasks) / len(self._tasks) if self._tasks else 0,
            "total_execution_time_ms": total_time_ms,
            "parallel_execution_time_ms": self._total_execution_time_ms,
            "parallelization_factor": self._total_execution_time_ms / total_time_ms if total_time_ms > 0 else 0,
            "total_tokens": self._total_tokens,
            "registered_agents": len(self.registry.get_all_agents()),
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None
        }
    
    def generate_report(self) -> str:
        """Generate execution report"""
        stats = self.get_statistics()
        
        lines = []
        lines.append("=" * 80)
        lines.append("Sub-Agent Delegation Report".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"Total Tasks: {stats['total_tasks']}")
        lines.append(f"Completed: {stats['completed_tasks']}")
        lines.append(f"Failed: {stats['failed_tasks']}")
        lines.append(f"Success Rate: {stats['success_rate']:.1%}")
        lines.append("")
        
        lines.append(f"Total Execution Time: {stats['total_execution_time_ms']:.0f}ms")
        lines.append(f"Parallel Execution Time: {stats['parallel_execution_time_ms']:.0f}ms")
        lines.append(f"Parallelization Factor: {stats['parallelization_factor']:.1f}x")
        lines.append("")
        
        lines.append(f"Total Tokens: {stats['total_tokens']:,}")
        lines.append(f"Registered Agents: {stats['registered_agents']}")
        lines.append("")
        
        # Agent statistics
        lines.append("Agent Statistics:")
        for agent in self.registry.get_all_agents():
            agent_stats = agent.get_statistics()
            lines.append(f"  {agent_stats['agent_type']} ({agent_stats['agent_id']}):")
            lines.append(f"    Completed: {agent_stats['tasks_completed']}")
            lines.append(f"    Failed: {agent_stats['tasks_failed']}")
            lines.append(f"    Tokens: {agent_stats['total_tokens']:,}")
            lines.append(f"    Cache Size: {agent_stats['cache_size']}")
        
        lines.append("")
        
        # Failed tasks details
        if self._failed_tasks:
            lines.append("Failed Tasks:")
            for task_id in self._failed_tasks:
                result = self._results.get(task_id)
                if result:
                    lines.append(f"  {task_id}:")
                    for error in result.errors:
                        lines.append(f"    - {error}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset coordinator state"""
        self._tasks.clear()
        self._results.clear()
        self._completed_tasks.clear()
        self._failed_tasks.clear()
        self._total_execution_time_ms = 0.0
        self._total_tokens = 0
        self._start_time = None
        self._end_time = None
        
        # Reset all agents
        for agent in self.registry.get_all_agents():
            agent.reset()
