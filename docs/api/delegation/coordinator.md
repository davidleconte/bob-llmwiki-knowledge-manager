# coordinator

Delegation Coordinator
Orchestrates parallel execution of sub-agents

## Classes

### `DelegationCoordinator`

Coordinates parallel execution of sub-agents

Manages task distribution, dependency resolution, and result aggregation

#### Methods

##### `__init__(max_workers: int, timeout_seconds: int, enable_retry: bool)`

Initialize coordinator

Args:
    max_workers: Maximum number of parallel workers
    timeout_seconds: Global timeout for all tasks
    enable_retry: Whether to retry failed tasks


##### `register_agent(agent: SubAgent)`

Register a sub-agent


##### `add_task(task: SubAgentTask)`

Add a task to be executed


##### `add_tasks(tasks: List[SubAgentTask])`

Add multiple tasks


##### `execute_parallel() -> Dict[str, SubAgentResult]`

Execute all tasks in parallel with dependency resolution

Returns:
    Dictionary mapping task IDs to results


##### `get_results() -> Dict[str, SubAgentResult]`

Get all results


##### `get_successful_results() -> Dict[str, SubAgentResult]`

Get only successful results


##### `get_failed_results() -> Dict[str, SubAgentResult]`

Get only failed results


##### `get_statistics() -> Dict`

Get execution statistics


##### `generate_report() -> str`

Generate execution report


##### `reset()`

Reset coordinator state


