# StreamSets Engine — Environments, Engines & Jobs

Conceptual reference for StreamSets Data Collector engines, environments, and
streaming jobs (SKILL.md §7). Covers infrastructure and operations; for building
streaming flows use pyflow (StreamSets engine) or the streaming SDK skill.

## When to use StreamSets

Continuous/streaming processing where data is processed as it arrives, kept inside
your own network, with high availability across engines.

## Engine characteristics

- **Container-based** — runs as Docker/Podman containers in your network.
- **Data ownership** — all processing occurs in your infrastructure; engines send
  only status/metrics to watsonx.data integration.
- **Continuous processing** — jobs run continuously.
- **High availability** — multiple engines support failover and load distribution
  (automatic failover 6.4+).
- **Flexible communication** — tunneling (default) or direct connection.

Architecture: **Browser ↔ watsonx.data integration ↔ Engine (in your network)**.
Resource thresholds prevent engine overload.

## Key concepts

- **Environments** — configure engines and compute resources for a project.
- **Engines** — Data Collector containers that execute flows.
- **Jobs** — flow executions that run continuously on engines.
- **Offsets** — track processing progress for resumable execution.
- **VPCs** — virtual CPUs allocated to engine containers.

## Quick start

1. **Create environment** — configure engines/compute for the project.
2. **Run engine** — deploy a Data Collector container (Docker/Podman).
3. **Execute job** — run the flow continuously.

## Prerequisites (once per account, plus per workstation)

- **Task credentials** — a user-generated API key (stored in Vault) that
  authorizes long-running jobs; reusable across all StreamSets jobs.
- **Cloud account API key** — required for engine authorization when running the
  engine command (IBM Cloud: Administration → Access (IAM) → API keys; AWS:
  Personal API keys).
- A created StreamSets environment and at least one running engine.

## Job model

- **One job per flow**; **one active run at a time**.
- **Lifecycle:** first run creates the job → runs continuously → stop records the
  last-read **offset** → next run resumes from it → optional **reset** reprocesses
  from the beginning.
- **Offset management** makes runs resumable; **automatic failover** moves a job
  to another engine (6.4+).
- Start a job from the flow canvas (quick start) or job details (full control).

## Deeper topics (in the IBM knowledge skill)

Engine deployment commands, tunneling vs direct communication, HA/failover setup,
resource thresholds, monitoring, and offset reset specifics live in
`di-agent-knowledge-engine-streamsets/` (`environments.md`, `engines.md`,
`jobs.md`, `reference.md`). This file is the orientation map.
