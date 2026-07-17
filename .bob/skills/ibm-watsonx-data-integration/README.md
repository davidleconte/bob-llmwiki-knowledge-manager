# IBM watsonx.data integration — Agent Skill

Equip any skills-compatible Bob AI agent  to build, run, and operationalize **data integration
pipelines** on [IBM watsonx.data integration](https://www.ibm.com/products/watsonx-data-integration)
from natural language. Describe the data requirement; the agent authors a flow,
you review and approve it, then it runs, monitors, and (optionally) schedules a job.

> Runs through the **Agentic Data Integration MCP** (cloud-hosted) and the
> **`data-intg-mcp` SDK server**. Built on the verified watsonx DI agent skills
> and the `ibm-watsonx-data-integration` SDK (1.3.x).

## What it does

| Capability | Use it for |
|------------|------------|
| **Flow authoring** | Build batch (DataStage) or streaming (StreamSets) flows — pyflow DSL first, the engine SDK when needed |
| **Query generation** | Turn a natural-language query into a validated **Substrait** plan (JSON / Elyra) |
| **Jobs & runs** | Create, run, monitor, and schedule jobs; read logs and metrics |
| **Engine knowledge** | DataStage parallel-engine tuning (partitioning/sorting/memory) and StreamSets engine/environment/job ops |
| **Diagnostics** | Honest run diagnosis from logs, safe versioning/backup, and a session bug-report for escalation |

## Why it's reliable

- **Looks up, never guesses.** Stage types, property names, enum values, and
  schemas come from the MCP discovery tools and the project assets — the #1 cause
  of flows that won't compile or crash at runtime.
- **Review before run.** Authoring and running are separate acts; the human
  approves the flow (via the returned `flow_link`) before any job consumes compute
  or writes to a destination.
- **Carries the traps.** Nullability must be preserved (DataStage crashes on NULLs
  into non-nullable fields); no BOOLEAN column type (use BIT); fetch flows by
  `flow_id` not name; bundle all edits into one submission; pyflow has no
  imports/`print` and StreamSets is a single linear chain.
- **pyflow first.** The compact DSL is built for high LLM authoring reliability;
  the verbose SDK is the fallback for what pyflow can't express.

## Install

Copy the `watsonx-data-integration/` folder into your agent's skills directory
(e.g. `~/.bob/skills/`), then register the watsonx DI MCP server(s) with your
agent.

```bash
cp -r watsonx-data-integration ~/.bob/skills/
```

SDK MCP server (no install, via `uvx`):
```jsonc
{
  "mcpServers": {
    "data-intg-mcp": {
      "command": "uvx",
      "args": ["--python", "3.12", "--from", "ibm_watsonx_data_integration_mcp", "data-intg-mcp"],
      "env": { "WATSONX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

For the cloud Agentic Data Integration MCP, follow IBM's
[Integrating data with the MCP server](https://www.ibm.com/docs/en/watsonx/wdi/saas?topic=integration-agentic-data).

## Structure

```
watsonx-data-integration/
├── SKILL.md                              # the skill — 11 sections, loaded by the agent
├── README.md                             # this listing
└── references/                           # loaded on demand
    ├── mcp-tools-reference.md             # both MCP servers' tools
    ├── pyflow-spec.md                     # the pyflow DSL spec
    ├── datastage-sdk-conventions.md       # DataStage batch SDK conventions
    ├── substrait-dsl.md                   # Substrait query-plan generation
    ├── datastage-engine.md                # DataStage engine + optimization
    ├── streamsets-engine.md               # StreamSets engines/environments/jobs
    └── jobs-and-diagnostics.md            # job lifecycle + bug-report recipe
```

## Requirements

- An agent that supports Agent Skills and MCP.
- A watsonx.data integration account/project with the MCP server(s) connected.
- Auth: IAM API key or bearer token (SaaS), or Zen API key / ICP4D (on-prem).
  SDK MCP server needs Python 3.11–3.12.

## License

Adapted from IBM's `ibm-watsonx-data-integration-skills` and SDK (see their repos
for the upstream license).
