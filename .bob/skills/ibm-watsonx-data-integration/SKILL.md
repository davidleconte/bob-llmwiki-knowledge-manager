---
name: watsonx-data-integration
description: >-
  Build, run, monitor, and operationalize data integration pipelines on IBM
  watsonx.data integration (watsonx DI / "Agentic Data Integration") from natural
  language. Use this whenever the user mentions watsonx.data integration, watsonx
  DI, Agentic Data Integration, a data flow / pipeline / ETL / ELT job, DataStage
  (batch) or StreamSets (streaming), pyflow, the watsonx DI SDK
  (`ibm-watsonx-data-integration`), the `data-intg-mcp` server, Substrait query
  plans, or asks to "create / edit a data flow", "build a pipeline", "move /
  transform / join / aggregate data", "ingest from <source> to <target>", "run /
  schedule / monitor a job", "generate a Substrait plan", "why did my flow fail",
  or to author flows against a project's connections and data assets. Covers
  authoring (pyflow DSL first, the engine-specific SDK when needed), query
  generation (Substrait DSL), job lifecycle and scheduling, DataStage /
  StreamSets engine knowledge, asset discovery, safe versioning, and session bug
  reports.
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.0.0"
---

# IBM watsonx.data integration — Author · Run · Operate Data Flows

Authoritative, end-to-end guide for delivering production data pipelines on **IBM
watsonx.data integration** through **Agentic Data Integration**: you describe the
data requirement in natural language, the agent authors a flow, the human reviews
and approves it, then the agent runs, monitors, and (optionally) schedules a job.
Grounded in the real watsonx DI agent skills, the `ibm-watsonx-data-integration`
SDK (1.3.x), and its MCP servers — not guesswork.

> **Golden rule #1 — never guess the platform's vocabulary.** Stage types,
> property names, enum/accepted values, and column schemas are *looked up*, never
> invented. Use `recommend_datastage_stages` / `datastage_property_lookup` (or the
> SDK MCP `list_available_*_stages` / `get_model_reference` / `search_sdk_documentation`)
> for stages and properties, and `list_project_assets` + `inspect_project_asset`
> for schemas. A guessed stage type, property name, enum value, or nullability
> flag is the #1 cause of flows that won't compile or crash at runtime.
>
> **Golden rule #2 — review before you run.** Authoring a flow and running a job
> are different acts. Build and compile the flow, surface the returned
> `flow_link`, and let the human review/approve **before** you create or start a
> job — only run when the user explicitly asks. Treat anything that writes to a
> destination or consumes compute as requiring that approval.

---

## 1. Mental model — what you are building

watsonx.data integration runs **flows** (pipelines) inside a **project**, against
**connections** and **data assets**, executed as **jobs** on an **engine**.

| Object | What it is | Worked with via |
|--------|-----------|-----------------|
| **Project** | The container for assets, flows, jobs, engines, environments | `get_projects`, `list_project_assets` |
| **Connection** | Stored credentials/config for an external datasource (Db2, BigQuery, Snowflake, Kafka…) — itself a project asset | `list_connections` |
| **Data asset** | A file/dataset stored in the project (uploaded CSV, Parquet…). **Database tables are NOT data assets** — they're referenced by path on a stage | `list_data_assets`, `inspect_project_asset` |
| **Flow** | The pipeline. **Batch → DataStage**; **streaming → StreamSets** | `create_pyflow`, `create_or_update_datastage_flow` |
| **Stage** | A node in a flow (source, processor, destination) | stage lookup tools |
| **Link** | A typed edge between stages; carries a **schema** | SDK link/schema API |
| **Job** | A runnable wrapper around a flow | job lifecycle tools |
| **Job run** | One execution of a job, with status, logs, metrics | `get_job_run_logs` |
| **Environment / Engine** | The compute that executes a flow (DataStage parallel engine; StreamSets Data Collector containers) | engine/env knowledge skills |

Two authoring surfaces, one decision (see §4):
- **pyflow** — IBM's compact, LLM-friendly Python DSL. **Bootstrap here first.**
- **engine-specific SDK** — verbose, exhaustive (DataStage / StreamSets). Fall
  back to it only when pyflow can't express a needed feature, or to edit/optimize
  an existing SDK flow.

---

## 2. Connect & authenticate

watsonx DI is driven through **MCP servers**. Two exist; know which you're on:

1. **Agentic Data Integration MCP** (cloud-hosted, the primary "Bob" surface).
   High-level tools that author/run flows for you: `create_pyflow`,
   `create_or_update_datastage_flow`, `recommend_datastage_stages`,
   `datastage_property_lookup`, `list_project_assets`, `inspect_project_asset`,
   the Substrait tools, and the job/diagnostic tools. Register the server with the
   agent, then add these skills. Setup: see IBM docs, "Integrating data with the
   MCP server."
2. **SDK MCP server** (`data-intg-mcp`, package `ibm_watsonx_data_integration_mcp`,
   Python 3.11–3.12). For authoring/validating raw SDK code and looking up the SDK:
   `search_sdk_documentation`, `get_model_reference`, `execute_script`,
   `list_available_batch_stages` / `list_available_streaming_stages`, etc.

```jsonc
// SDK MCP server (uvx — no install). Add to your client's MCP config.
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

**Authentication** (used by the SDK / SDK MCP; the cloud Agentic MCP handles its
own auth on registration):
- **SaaS (IAM)** — generate an API key at https://cloud.ibm.com/iam/apikeys; the
  SDK uses `IAMAuthenticator(api_key=…, base_auth_url="https://cloud.ibm.com")`.
- **SaaS (bearer)** — `BearerTokenAuthenticator(bearer_token=…)`.
- **On-prem (CP4D)** — `ZenApiKeyAuthenticator(username=…, zen_api_key=…)` or
  `ICP4DAuthenticator(username=…, url=…)`.

> Keep the API key in the environment / a secret store, never in flow code or
> chat. Region matters for some tools (`region_name` from the IBMCloudRegion enum:
> `TORONTO`, `DALLAS`, `FRANKFURT`, `LONDON`, `TOKYO`, `SYDNEY`).

Full tool catalog for both servers: **[references/mcp-tools-reference.md](references/mcp-tools-reference.md)**.

---

## 3. The canonical lifecycle

Follow this order. Dependencies must exist before the thing that references them.

```
discover assets (project, connections, schemas)
   → choose engine + authoring surface (pyflow first)
   → author the flow
   → compile / validate
   → REVIEW with the human (surface flow_link)  ← approval gate
   → create job → run job (only when asked)
   → monitor run (status, logs, metrics)
   → (optionally) schedule
```

### 3.1 Discover assets (skip what the user already named)

```
get_projects()                          # find the project
list_connections(project_id=…)          # connection IDs (never to find tables inside)
list_data_assets(project_id=…)          # files/datasets — returns 0 for DB tables
list_project_assets(…) / inspect_project_asset(asset_ids=[…])   # authoritative schema
```
- **Schemas come from the assets, not from memory or examples.** Map asset column
  types to DSL/SDK types and **carry nullability** (`nullable: true` → append `?`
  in DSL; set `field.nullable=True` in the SDK). DataStage crashes at runtime if
  NULLs land in a non-nullable field.
- **`data_asset` vs connector tables:** uploaded files are `data_asset`s;
  database tables (Db2, BigQuery, Snowflake, Oracle…) are referenced by path on
  the stage (e.g. Db2 `/SALES/ORDERS` → `schema_name="/SALES"`, `table_name="ORDERS"`).
  The **connection** is the asset, not the table.

### 3.2 Choose engine + surface

Batch large-volume ETL/ELT → **DataStage**. Continuous/streaming → **StreamSets**.
Then pick the authoring surface per §4 (pyflow first).

### 3.3 Author the flow

- **pyflow:** write the DSL and submit via `create_pyflow(engine=…, bindings=…)`.
  The runtime provides `q`; no imports, no `print()`. Spec:
  **[references/pyflow-spec.md](references/pyflow-spec.md)**.
- **DataStage SDK:** write flat SDK code and submit via
  `create_or_update_datastage_flow`. Look up every stage's skill file and property
  names first. Conventions: **[references/datastage-sdk-conventions.md](references/datastage-sdk-conventions.md)**.
- **StreamSets:** engine/environment/job specifics in
  **[references/streamsets-engine.md](references/streamsets-engine.md)**.

### 3.4 Compile / validate

- pyflow and `create_or_update_datastage_flow` handle persistence + compilation
  for you — **do not** append `update_flow`/`compile` calls in submitted code.
- If you ever drive the raw SDK: `project.update_flow(flow)` then `flow.compile()`
  for batch (there is no `project.validate_flow`).

### 3.5 Review (the approval gate)

Surface the returned **`flow_link`** as a clickable link and summarize what the
flow does (sources, transforms, sink, write mode). Let the human approve before
any job is created or run. Do not auto-run.

### 3.6 Run, monitor, schedule

Only after approval / explicit request. Create a job, start a run, poll status,
read logs/metrics, and schedule if asked. See **§6** and
**[references/jobs-and-diagnostics.md](references/jobs-and-diagnostics.md)**.

---

## 4. Authoring surface — pyflow vs the engine SDK

**Default to pyflow.** Its compact surface is built for high LLM authoring
reliability. Reach for the verbose SDK only when pyflow can't express a feature,
or to edit/optimize an existing SDK-authored flow.

| | pyflow | engine SDK (DataStage / StreamSets) |
|---|--------|-------------------------------------|
| Best for | Bootstrapping new batch or streaming flows fast | Features pyflow lacks; editing/optimizing existing flows; exhaustive stage/property control |
| Engine | DataStage or StreamSets (`create_pyflow(engine=…)`) | DataStage (`create_or_update_datastage_flow`) / StreamSets |
| Surface | Small DSL: `q.source/output/write/col/...`, Frame ops | Full SDK: stages, links, schemas, connections |
| Constraints | No imports/`print`; engine gates which ops are allowed | Flat syntax only — no loops/conditionals/functions/classes |

**pyflow essentials** (full spec in the reference):
- Declare sources with `q.source()` (only referenced columns, exact names/types),
  call `q.name("snake_case")` once, end with exactly one sink — `q.output(frame)`
  or `q.write(frame, "symbol", operation="insert"|"overwrite"|"update")`.
- Engine gating: DataStage allows joins/group-by/union/`.head()`; StreamSets is a
  single linear chain with `.lookup()` and one windowed agg (`.tumble()`/`.slide()`,
  `.sum()` only) and exactly one `q.source()`.
- Expressions use `&`/`|`/`~` (never `and`/`or`/`not`), parenthesize comparisons.
- Symbols passed to `q.source/.lookup/.write` are bound to catalog assets via
  `create_pyflow(bindings=…)`.

**DataStage SDK essentials** (full conventions in the reference):
- `flow = project.create_flow(name=…, environment=None, flow_type='batch')` — those
  exact params. `flow.add_stage(type='Row Generator', label='…')`.
- Set `stage.configuration.runtime_column_propagation = True` where available, or
  schemas won't propagate. Every **input** link needs a schema with fields; if a
  field maps from upstream, set its `source=` or compilation fails.
- Connections must be a **variable**, never a string literal:
  `conn = project.connections.get(name=…)` then `stage.use_connection(conn)`.
- No `BOOLEAN` column type (use `BIT` 0/1). Collections use `.get_all()`, not
  `.list()`. Fetch flows by `flow_id`, never by name.

---

## 5. Query generation — Substrait DSL

When the user wants a **query plan** (not a full visual flow) — "generate a
Substrait plan / functional plan", "convert this query to Substrait JSON" — use
the Substrait DSL workflow. Full recipe: **[references/substrait-dsl.md](references/substrait-dsl.md)**.

Pipeline: fetch examples (`get_substrait_dsl_examples`) → **verify schema from
assets** (`list_project_assets` + `inspect_project_asset`; asset schema wins over
any user- or example-provided schema) → study the spec (`get_substrait_dsl_spec`,
mandatory) → write DSL → `compile_substrait_dsl` → self-correct up to 3 times →
then **execute only if asked** (`run_substrait_dsl` / `run_substrait_dsl_static`,
retry the other on failure) or convert (`convert_substrait_dsl_to_elyra`).

Key rules: nullable columns MUST carry the `?` suffix; `Select` keeps only listed
columns, `Project` keeps all plus new; aggregation measures are never wrapped in
`cast()`; output column names must not contain dots; use `left.`/`right.` prefixes
only inside join conditions.

---

## 6. Jobs, runs, and scheduling

A flow is authored; a **job** runs it. Only create/run after the §3.5 approval
gate. Full lifecycle, monitoring, and scheduling:
**[references/jobs-and-diagnostics.md](references/jobs-and-diagnostics.md)**.

Raw-SDK shape (the MCP tools wrap this):
```python
job = project.create_job(name='My Job', flow=flow)
job_run = job.start(name='Run 1')
job_run.refresh_status(); print(job_run.state)
for line in job_run.logs: print(line)
job_run.cancel()
job.edit_configuration(environment='default_datastage_px', retention_amount=100, warn_limit=50)
```

- **Monitor honestly.** Job-run status reports only `completed`/`failed` + a short
  summary — for real diagnosis pull `get_job_run_logs` (row counts per stage, type
  conversions, partition counts).
- **An empty result is not automatically a failure** — the source may legitimately
  be empty, or the flow logic may yield zero rows. Distinguish "succeeded,
  vacuously empty" from "silently dropped rows".
- **Schedule** only when asked; confirm cadence and timezone.

---

## 7. Engines & environments

Pick the engine by workload (§3.2). Conceptual depth lives in the knowledge
references:

- **DataStage parallel engine** — partitioning, nodes, APT config, concurrent
  execution, restart/recovery, disk/resource tuning, flow optimization
  (partitioning/sorting/memory), per-stage semantics. See
  **[references/datastage-engine.md](references/datastage-engine.md)**.
- **StreamSets Data Collector** — container-based engines (Docker/Podman) in your
  network, environments, tunneling vs direct, continuous jobs, offsets,
  HA/failover, resource thresholds. See
  **[references/streamsets-engine.md](references/streamsets-engine.md)**.

Use these for conceptual "why/how does the engine behave" questions and for
optimization, independent of the authoring tool.

---

## 8. Critical constraints (these cause silent failures — internalize them)

**Lookups, not guesses**
- ✅ Never invent stage types, property names, enum/accepted values, or schemas.
  Look them up (`recommend_datastage_stages`, `datastage_property_lookup`,
  `list_available_*_stages`, `get_model_reference`, `inspect_project_asset`).
- ✅ When a property has `accepted_values`, use one **exactly**. Enums use the
  `STAGE.Property.value` form (e.g. `PEEK.Dataset.false`).
- ✅ Show users the **user-friendly** property name in prose (e.g. "Number of rows
  (per partition)"), the internal id (`nrecs`) only in code.

**Schemas & types**
- ✅ Schemas come from assets; carry nullability (`?` in DSL; `field.nullable` in
  SDK). DataStage crashes if NULLs hit a non-nullable field.
- ✅ DataStage has **no BOOLEAN** column type — use `BIT` with 0/1.
- ✅ Every input link needs a schema with ≥1 field; mapped fields need `source=`.

**pyflow**
- ✅ No imports, no `print()`. End with exactly one sink. Use `&`/`|`/`~`.
- ✅ Respect engine gating (StreamSets = single linear chain, one source, `.sum()`-only windows).

**DataStage SDK**
- ✅ Flat syntax only — no loops/conditionals/functions/classes/try/decorators.
- ✅ `environment=None`, `flow_type='batch'` exactly. `.get_all()` not `.list()`.
  `project_id=` not `id=`. Connection is a variable, not a string.
- ✅ Don't append `update_flow`/`compile` to submitted code — the tool does it.
  Bundle **all** changes into one submission (successive submissions overwrite).

**Operations**
- ✅ Fetch flows by `flow_id`, never by name (name returns incomplete stage data).
- ✅ On a create name collision, ask to overwrite or rename — never retry blindly.
- ✅ Surface the returned `flow_link` after every successful create/update.
- ✅ Review before run; run only when asked.

---

## 9. Debugging playbook

| Symptom | Likely cause → fix |
|---------|--------------------|
| Flow won't compile | Guessed stage type/property/enum, or an input link missing a schema/`source=`. Look it up; add schemas; set `source=`. |
| "Property/enum not accepted" | Value not in `accepted_values`. Re-run `datastage_property_lookup` / `list_all_available_stage_configurations_*` and use an exact value. |
| Runtime crash on NULLs | A nullable source column declared non-nullable. Re-`inspect_project_asset`; add `?` (DSL) / `field.nullable=True` (SDK). |
| `list_data_assets` returns 0 | The target is a database table, not a data asset. Reference it by path on the stage; use `list_connections` for the connection ID. |
| Changes vanished after edit | Successive submissions overwrite. Bundle all changes into one submission. |
| Fetched flow has incomplete stages | Fetched by name. Re-fetch by `flow_id`. |
| `.list()` / `project.validate_flow` errors | Use `.get_all()` / `flow.compile()`. Param is `project_id=`. |
| Connection error at runtime | `use_connection` got a string or inline call. Assign to a variable first. |
| Run "failed" or output looks wrong | Don't diagnose from the summary. Pull `get_job_run_logs` (+ `retrieve_datastage_flow_code`) for per-stage row counts and errors. |
| Empty output | Not necessarily a failure — confirm whether the source is empty or the logic legitimately yields zero rows before calling it a bug. |

Iterate: look up → author → compile → fix from the compiler/log evidence → re-test.
Never pass a raw error through; diagnose and propose the fix.

**Bug report (escalation).** When you've genuinely **exhausted** recovery paths
(consulted the knowledge skills, used the lookup/diagnostic tools, retried the
obvious fix) and the failure stands, you may *propose* a session bug report —
**once per session, then wait for explicit yes**. The user can also request one
anytime. It captures the session (PII-masked) plus `get_session_info`,
`get_job_run_logs`, and `retrieve_datastage_flow_code` into a Markdown file. Recipe
and template: **[references/jobs-and-diagnostics.md](references/jobs-and-diagnostics.md)**.

---

## 10. Safe versioning

Editing or iterating on a flow can break it. Use `duplicate_asset` as a safety net.

- **Editing an existing flow:** first `duplicate_asset(asset_id=…, asset_type="datastage_flow", project_id=…)` with a timestamped name (`"{name} [backup YYYY-MM-DD]"`). Work on the original; the backup is your rollback. Keep at most one backup per flow (`delete_asset` old ones).
- **Iterating on a new flow:** after a successful create, snapshot the working
  state before further edits.
- **Restore:** delete the broken flow, then duplicate the backup back to the
  original name (or point the user to the backup).
- **Caveats:** duplicating does **not** copy jobs/schedules or cross-flow
  references. Be careful editing flows with active runs.

---

## 11. References (load on demand)

| File | Contents |
|------|----------|
| [references/mcp-tools-reference.md](references/mcp-tools-reference.md) | Both MCP servers' tools (Agentic DI cloud + `data-intg-mcp` SDK server), grouped by job |
| [references/pyflow-spec.md](references/pyflow-spec.md) | Full pyflow DSL: `q` namespace, types, expressions, Frame methods, engine gating, worked examples |
| [references/datastage-sdk-conventions.md](references/datastage-sdk-conventions.md) | DataStage batch SDK: flow/stage/link/schema API, connection binding, column types, job lifecycle, key rules, foot-guns |
| [references/substrait-dsl.md](references/substrait-dsl.md) | Substrait query-plan generation: asset-type mapping, schema verification, compile/self-correct loop, execute/convert |
| [references/datastage-engine.md](references/datastage-engine.md) | DataStage parallel engine: partitioning, config, concurrency, restart/recovery, optimization, per-stage lookup |
| [references/streamsets-engine.md](references/streamsets-engine.md) | StreamSets engines/environments/jobs: deployment, communication, offsets, HA/failover, resources |
| [references/jobs-and-diagnostics.md](references/jobs-and-diagnostics.md) | Job lifecycle, scheduling, monitoring, diagnostic tools, and the session bug-report recipe + template |

### Canonical external resources (you have internet access — use them)
- **watsonx DI docs / MCP setup:** https://www.ibm.com/docs/en/watsonx/wdi/saas?topic=integration-agentic-data
- **SDK docs (models, auth, jobs):** the `ibm-watsonx-data-integration` SDK documentation site
- **SDK source / skills repos:** `ibm-watsonx-data-integration-sdk`, `ibm-watsonx-data-integration-skills`

When a stage, property, schema, or SDK signature is in doubt, **look it up with
the MCP tools** rather than guessing — that is the core discipline of this skill.
