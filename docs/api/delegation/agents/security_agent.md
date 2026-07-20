# security_agent

Security Analysis Sub-Agent
Specialized agent for security audits and vulnerability detection

## Classes

### `SecurityAgent(SubAgent)`

Security analysis specialist

Capabilities:
- Vulnerability detection
- Hardcoded secrets scanning
- Authentication/authorization review
- Cryptography analysis
- Input validation checks

#### Methods

##### `__init__(agent_id: str, cache_enabled: bool, base_path: str)`

Initialize security agent


##### `get_capabilities() -> List[str]`

Get agent capabilities


##### `analyze(task: SubAgentTask) -> SubAgentResult`

Perform security analysis

Args:
    task: Security analysis task

Returns:
    SubAgentResult with security findings


