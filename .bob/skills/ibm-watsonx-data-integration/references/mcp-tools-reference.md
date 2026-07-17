# watsonx.data integration — MCP Tool Catalog

Two MCP server surfaces. Know which one a tool belongs to.

## A. Agentic Data Integration MCP (cloud-hosted — the primary "Bob" surface)

High-level tools that author, run, and diagnose flows on your behalf.

### Asset discovery
| Tool | Purpose |
|------|---------|
| `get_projects()` | List projects |
| `list_connections(project_id=…)` | Connection IDs (the connection is the asset — not the tables inside it) |
| `list_data_assets(project_id=…)` | Files/datasets in the project (**returns 0 for DB tables**) |
| `list_datastage_flows(project_id=…)` / `list_streamsets_flows(project_id=…)` | Existing flows |
| `list_project_assets(…)` | All project assets by name |
| `inspect_project_asset(asset_ids=[…], asset_type=…)` | Authoritative column names, types, nullability (`asset_ids` is always a list) |

### Flow authoring
| Tool | Purpose |
|------|---------|
| `create_pyflow(engine=…, bindings=…)` | Author a batch/streaming flow from pyflow DSL; runtime provides `q` |
| `create_or_update_datastage_flow(...)` | Submit DataStage batch SDK code (auth, persist, compile handled for you) |
| `recommend_datastage_stages(subutterances=[…])` | Pick the right DataStage stage(s) for a sub-task |
| `datastage_property_lookup(requests=[{"stage":"…"}])` | Verified property names + accepted values for a stage |

### Query generation (Substrait)
| Tool | Purpose |
|------|---------|
| `get_substrait_dsl_examples(query=…, collection=…, n=…)` | Few-shot DSL examples |
| `get_substrait_dsl_spec()` | The authoritative DSL spec (study before writing — mandatory) |
| `compile_substrait_dsl(substrait_dsl_code=…, read_tables=[…])` | Validate/compile DSL → Substrait JSON |
| `run_substrait_dsl(...)` / `run_substrait_dsl_static(...)` | Execute (retry the other on failure) |
| `convert_substrait_dsl_to_elyra(...)` | Convert DSL → Elyra pipeline JSON |
| `load_test_entry(...)` | Load a JSONL test entry |

### Versioning & ops
| Tool | Purpose |
|------|---------|
| `duplicate_asset(asset_id=…, asset_type=…, project_id=…)` | Backup/snapshot a flow before edits |
| `delete_asset(...)` | Delete an asset (e.g. an old backup) |

### Jobs & diagnostics
| Tool | Purpose |
|------|---------|
| `get_job_run_logs(...)` | Full log stream for the latest run (per-stage row counts, type conversions, errors) |
| `retrieve_datastage_flow_code(...)` | The stored definition of the submitted flow |
| `get_session_info()` | Session metadata for bug reports |

## B. SDK MCP server (`data-intg-mcp`, package `ibm_watsonx_data_integration_mcp`)

For authoring/validating raw SDK code and looking up the SDK. Python 3.11–3.12.
Run via `uvx`, `uv tool`, or pip (see SKILL.md §2). Some tools are stdio-only and
require auth; `--disable-execution-tools` turns off execution + stage discovery.

### Documentation
| Tool | Purpose |
|------|---------|
| `search_sdk_documentation(query=…, top_k=…)` | Semantic search across SDK docs |
| `get_model_reference(class_name=…)` | Authoritative fields/enums/method signatures for an SDK model (e.g. `JobRun`, `BatchFlow`, `Schedule`) |

### Version / resources
| Tool | Purpose |
|------|---------|
| `get_mcp_version()` / `get_sdk_version()` | Versions |
| `list_resources()` / `read_resource(uri=…)` | Best-practices, intent templates, server-side skills (`skill://platform/SKILL.md`, `intent://batch-flow`, `watsonx://best_practices`, …) |

### Execution & stage discovery (stdio only, requires auth)
| Tool | Purpose |
|------|---------|
| `execute_script(code=…)` | Run a generated SDK script (60s timeout; rejects private-attr access `\._[a-zA-Z]`) |
| `list_available_batch_stages(project_id=…, flow_id=…)` | All batch stages for a flow |
| `list_all_available_stage_configurations_batch(project_id=…, flow_id=…, stage_labels=[…])` | Config fields, types, defaults, accepted values |
| `list_available_streaming_stages(...)` / `list_all_available_stage_configurations_streaming(...)` | Streaming equivalents |

Common params on discovery/execution tools: `project_id`, `flow_id`,
`base_api_url`, `base_url` (default `https://cloud.ibm.com`), `region_name`
(IBMCloudRegion: `TORONTO`/`DALLAS`/`FRANKFURT`/`LONDON`/`TOKYO`/`SYDNEY`).

## Which surface for what

- Building/running flows from natural language, asset discovery, Substrait,
  job diagnostics → **Agentic DI MCP** (A).
- Writing or validating raw SDK Python, looking up exact model fields/enums,
  executing a script → **SDK MCP server** (B).
