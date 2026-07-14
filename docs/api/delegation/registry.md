# registry

Sub-Agent Registry
Manages registration and discovery of sub-agents

## Classes

### `SubAgentRegistry`

Registry for managing sub-agents

Provides agent discovery and task routing

#### Methods

##### `__init__()`

Initialize registry


##### `register(agent: SubAgent)`

Register a sub-agent

Args:
    agent: Sub-agent to register


##### `unregister(agent_id: str)`

Unregister a sub-agent

Args:
    agent_id: ID of agent to unregister


##### `get_agent(agent_id: str) -> Optional[SubAgent]`

Get agent by ID

Args:
    agent_id: Agent ID

Returns:
    SubAgent or None if not found


##### `get_agents_by_type(agent_type: str) -> List[SubAgent]`

Get all agents of a specific type

Args:
    agent_type: Agent type

Returns:
    List of agents


##### `get_agent_for_task(task: SubAgentTask) -> Optional[SubAgent]`

Find best agent for a task

Args:
    task: Task to execute

Returns:
    SubAgent or None if no suitable agent found


##### `get_all_agents() -> List[SubAgent]`

Get all registered agents


##### `get_agent_types() -> List[str]`

Get all registered agent types


##### `get_statistics() -> Dict`

Get registry statistics


##### `clear()`

Clear all registrations


