# base

Base Sub-Agent Class
Foundation for all specialized sub-agents

## Constants

- `PENDING`
- `RUNNING`
- `SUCCESS`
- `FAILED`
- `CANCELLED`
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## Functions

### `_get_shared_token_counter() -> 'TokenCounter'`

Return the lazily-constructed process-wide TokenCounter.


## Classes

### `SubAgentStatus(Enum)`

Sub-agent execution status


### `SubAgentPriority(Enum)`

Sub-agent priority levels


### `SubAgentResult`

Result from sub-agent execution

#### Methods

##### `is_success() -> bool`

Check if execution was successful


##### `has_errors() -> bool`

Check if there were errors


##### `has_warnings() -> bool`

Check if there were warnings


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary



### `SubAgentTask`

Task to be executed by sub-agent

#### Methods

##### `can_execute(completed_tasks: set) -> bool`

Check if all dependencies are completed


##### `should_retry() -> bool`

Check if task should be retried



### `SubAgent(ABC)`

Base class for all sub-agents

Sub-agents are specialized workers that perform specific analysis tasks
in parallel. Each sub-agent has its own cache and operates independently.

#### Methods

##### `__init__(agent_id: str, agent_type: str, cache_enabled: bool, max_cache_size: int, token_counter: Optional['TokenCounter'])`

Initialize sub-agent

Args:
    agent_id: Unique identifier for this agent instance
    agent_type: Type of agent (e.g., "security", "performance")
    cache_enabled: Whether to enable caching
    max_cache_size: Maximum cache entries
    token_counter: TokenCounter for result token counts; defaults to the
        shared process-wide counter (B3 single counting home).


##### `analyze(task: SubAgentTask) -> SubAgentResult`

Perform analysis task

Args:
    task: Task to execute

Returns:
    SubAgentResult with analysis results


##### `get_capabilities() -> List[str]`

Get list of capabilities this agent provides

Returns:
    List of capability names


##### `execute(task: SubAgentTask) -> SubAgentResult`

Execute a task with error handling and caching

Args:
    task: Task to execute

Returns:
    SubAgentResult with execution results


##### `count_tokens(data: Any) -> int`

Count tokens in *data* via the shared TokenCounter (single home, B3).

Replaces the per-agent ``len(str(data)) // 4`` heuristic so delegation
token totals are model-correct and route through one counter. Non-string
data is stringified with ``str()`` before counting.


##### `clear_cache()`

Clear agent's cache


##### `get_status() -> SubAgentStatus`

Get current status


##### `get_statistics() -> Dict[str, Any]`

Get agent statistics


##### `reset()`

Reset agent state


