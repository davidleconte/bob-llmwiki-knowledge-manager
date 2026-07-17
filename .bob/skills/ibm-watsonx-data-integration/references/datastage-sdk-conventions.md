# DataStage Batch SDK Conventions

Reference for DataStage (batch) flows authored as SDK-style Python and submitted
via `create_or_update_datastage_flow`. Auth, project context, persistence, and
compilation are handled by the MCP tool — the patterns below apply to the flow
code you write (SKILL.md §4). Use pyflow first; drop to the SDK for features
pyflow can't express or to edit/optimize an existing flow.

## CRITICAL — look up the stage before writing it

Before writing any code that includes a stage, read its stage knowledge file
(`di-agent-knowledge-engine-datastage/stages/<UserFriendlyName>Stage.md`) and
verify properties via `datastage_property_lookup`. The **link cardinality rules**
in those files must be followed. Never guess stage types, property names, or enum
values — use `recommend_datastage_stages` and `datastage_property_lookup`.

## Asset discovery

```python
get_projects()                         # list projects
list_data_assets(project_id=…)         # files/datasets (0 for DB tables)
list_connections(project_id=…)         # connection IDs
list_datastage_flows(project_id=…)     # batch flows
list_streamsets_flows(project_id=…)    # streaming flows
inspect_project_asset(asset_ids=[…])   # schema + metadata (asset_ids always a list)
```
Skip discovery when the user already named the connection/table. **`data_asset`**
= files in the project; **database tables** are referenced by path on the stage
(Db2 `/SALES/ORDERS` → `schema_name="/SALES"`, `table_name="ORDERS"`); the
**connection** is the asset, not the tables inside it. Asset types: `data_asset`,
`connection`, `datastage_flow`, `streamsets_flow`, `job`.

## Flow creation

```python
flow = project.create_flow(name='My Flow', environment=None, flow_type='batch')
project.update_flow(flow)   # persist every change (NOT needed in submitted code — the tool does it)
```
Include these exact named params: `environment=None`, `flow_type='batch'`.

## Stages

```python
stage = flow.add_stage(type='Row Generator', label='my_row_gen')
# type = exact stage type string (case-sensitive); label = UI display name
```
Set `stage.configuration.runtime_column_propagation = True` on stages that have it,
or schemas won't propagate and downstream compilation fails. Verify property names
with `datastage_property_lookup` first. Both access styles work:
```python
stage.configuration['key_capture_mode'] = 'RECORD_HEADER'
stage.configuration.key_capture_mode = 'RECORD_HEADER'
```
When `accepted_values` is non-empty, use one exactly.

**Property value types:** primitives (`int`/`str`/`bool`); enums as
`STAGENAME.PropertyName.value` (e.g. `PEEK.Dataset.true`); lists/dicts for complex
props (`key_properties`).

**Execmode** needs the stage-specific enum class:
```python
from ibm_watsonx_data_integration.services.datastage import PEEK, ROW_GENERATOR
row_gen.configuration.execmode = ROW_GENERATOR.Execmode.par   # parallel
peek.configuration.execmode = PEEK.Execmode.seq               # sequential
peek.configuration.dataset = PEEK.Dataset.false
```
Other common props: `auto_column_propagation`, `combinability`.

## Connecting stages

```python
origin.connect_output_to(destination)
destination.connect_input_to(origin)                 # equivalent
origin.connect_output_to(processor).connect_output_to(destination)  # chaining returns destination
# fan-out: call separately per destination
link_a = origin.connect_output_to(proc1)
link_b = origin.connect_output_to(proc2)
```
`connect_output_to` returns a link object you can name and attach a schema to.

**Link types** (default `PRIMARY`; chained assignment NOT supported):
```python
# WRONG: link = transformer.connect_output_to(join_stage).primary()
link = rg2.connect_output_to(join_stage)
link.name = "Link_RG2_Join"
link.reference()     # or .primary() / .reject()
```

## Link schemas

Every **input** link needs a schema or the flow won't compile. Output stages
usually don't need explicit schemas — `runtime_column_propagation` handles them.

```python
link = origin.connect_output_to(dest)
link.name = "Link_1"
schema = link.create_schema()
schema.add_field("VARCHAR", "my_col", length=100)
schema.add_field("DECIMAL", "my_num", length=10, precision=2)
schema.add_field("INTEGER", "my_int", source="OtherLink.other_int")   # propagate from upstream
schema.add_field("DECIMAL", "derived", length=10, precision=2,
                 derivation="Link_1.my_num * 2")                      # computed
```
**If a field maps from an upstream column, `source=` MUST be set** or compilation
fails. Every schema needs ≥1 field (use plausible mock fields if columns aren't
specified). `derivation` must be passed as a kwarg to `add_field`, not set
post-hoc. Field props: `field.nullable`, `field.key`, `field.length`,
`field.scale`, `field.description`. Some props use the `FIELD` enum (in scope, no
import): `schema.add_field("VARCHAR", "col", delimiter=FIELD.Delim.comma)`.

## Column types

```
BIGINT, BINARY, BIT, CHAR, DATE, DECIMAL, DOUBLE, FLOAT, INTEGER,
LONGNVARCHAR, LONGVARBINARY, LONGVARCHAR, NCHAR, NUMERIC, NVARCHAR,
REAL, SMALLINT, TIME, TIMESTAMP, TINYINT, UNKNOWN, VARBINARY, VARCHAR
```
**No BOOLEAN** — use `BIT` with 0/1. Carry nullability from the asset metadata;
DataStage crashes at runtime if NULLs read into a non-nullable field.

## Connection binding

Local (stage-scoped):
```python
stage.configuration.connection.property_name_1 = value_1
```
Project-level (retrieve, then attach — **connection must be a variable**):
```python
conn = project.connections.get(name='my-db-connection')
# create new: datasource_type = platform.datasources.get(name='IBM Db2')
#             project.create_connection(name=…, datasource_type=datasource_type, properties={…})
stage = flow.add_stage(type='IBM Db2', label='db2_source')
stage.use_connection(conn)             # NEVER use_connection("string") or an inline call
stage.configuration.schema_name = 'MYSCHEMA'
stage.configuration.table_name = 'MYTABLE'
```

## Validation & job lifecycle

```python
flow.compile()                         # batch validation (no project.validate_flow)
job = project.create_job(name='My Job', flow=flow)
job_run = job.start(name='Run 1')
job_run.refresh_status(); print(job_run.state)
for line in job_run.logs: print(line)
job_run.cancel()
job.edit_configuration(environment='default_datastage_px', retention_amount=100, warn_limit=50)
```
Always `project.update_flow(flow)` before validating (outside submitted code).

## Key rules

1. Code is **not** run in a full Python environment — generate simple, flat syntax only.
2. Do not hallucinate methods not listed here.
3. Do not append `update_flow`/`compile` to a submission — the tool handles them.
   Bundle all changes into one submission (successive submissions overwrite).
4. **No complex Python:** no loops, conditionals, functions, classes, try/except,
   with, decorators, assert, del, augmented assignment, return/yield/break/continue/pass.
5. Stage types and datasource types match exactly (case-sensitive).
6. Avoid modifying user-supplied code unless necessary.
7. Always include every required property; guess plausible mock values when unspecified.
8. Adhere to per-stage cardinality rules.
9. Mapped fields need `source=`.

## Foot-guns

- **`.list()` doesn't exist** — always `.get_all()`.
- **`project_id=`, not `id=`** — `platform.projects.get(project_id='abc-123')`.
- **Fetch batch flows by `flow_id`, not by name** (name returns incomplete data).
- **No BOOLEAN** — `BIT` with 0/1.
- **Never guess enums** — inspect `accepted_values`, use one exactly.
- **`project.validate_flow` doesn't exist** — use `flow.compile()`.
- **Connection must be a variable**, never a string literal or inline call.
