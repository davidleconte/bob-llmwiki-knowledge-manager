# quality_agent

Code Quality Analysis Sub-Agent
Specialized agent for code quality and maintainability assessment

## Classes

### `QualityAgent(SubAgent)`

Code quality specialist

Capabilities:
- Complexity analysis
- Code duplication detection
- Maintainability scoring
- Function length analysis
- Code smell detection

#### Methods

##### `__init__(agent_id: str, cache_enabled: bool, base_path: str)`


##### `get_capabilities() -> List[str]`


##### `analyze(task: SubAgentTask) -> SubAgentResult`


