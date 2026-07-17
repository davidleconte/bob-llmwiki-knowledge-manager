# Jobs, Monitoring & Session Bug Reports

Job lifecycle, monitoring, and the escalation bug-report recipe (SKILL.md §6, §9).

## Job lifecycle

A flow is authored; a **job** runs it. Create/run only after the review gate
(SKILL.md §3.5) or an explicit request.

Raw-SDK shape (the MCP tools wrap this; don't append `update_flow`/`compile` to
submitted code):
```python
job = project.create_job(name='My Job', flow=flow)
job_run = job.start(name='Run 1')
job_run.refresh_status(); print(job_run.state)
for line in job_run.logs: print(line)
job_run.cancel()
job.edit_configuration(environment='default_datastage_px', retention_amount=100, warn_limit=50)
```
Look up exact fields/enums for `Job`, `JobRun`, `Schedule` via the SDK MCP
`get_model_reference`.

- **Batch (DataStage):** a run executes once and completes.
- **Streaming (StreamSets):** one job per flow, one active run; runs continuously,
  records an **offset** on stop, resumes on next run, can be **reset** to
  reprocess from the start.

## Monitoring honestly

- Run status reports only `completed`/`failed` + a short summary — not enough to
  diagnose. Pull **`get_job_run_logs`** for per-stage `in → out` row counts,
  implicit type conversions, partition counts, and errors. Use
  **`retrieve_datastage_flow_code`** to confirm what actually ran.
- **An empty result is not automatically a failure.** Distinguish:
  - *Success — produced rows.*
  - *Success — vacuously empty* (the source has 0 rows).
  - *Success — expected zero output* (anti-join/filter legitimately yields none).
  - *Failure* (errors in logs, rows silently dropped given a non-empty source, an
    invalid flow, or the agent looping/misusing a tool).

## Scheduling

Schedule only when asked. Confirm cadence and timezone, and that the flow has been
reviewed. Look up the `Schedule` model fields via `get_model_reference`.

## Session bug report (escalation)

A Markdown report capturing the session so skill authors can debug. **Manual:** the
user asks → proceed. **Automatic:** only *propose* it after genuinely **exhausting**
recovery (consulted knowledge skills, used lookup/diagnostic tools, retried the
obvious fix, failure still stands) — **once per session**, then wait for an explicit
yes. The proposal slot is consumed whether the user accepts, declines, or ignores.

A session counts as watsonx DI-related if a `di-agent-*` skill was used, a watsonx
DI MCP tool was called, or the user asked to create/edit/run/debug a flow/job.

### Workflow

1. **Resolve metadata** — date/time; a short slug of the user's intent; the host
   agent's session id (try the runtime transcript/log file; never invent — record
   `null` if unknown); `get_session_info()` (render its fields verbatim; `_tool
   unavailable._` if it errors); the LLM name-version the runtime states.
2. **Build the transcript** — one chronological numbered sequence; user/assistant
   turns verbatim (PII-redacted, no paraphrase), skill/tool calls with one-line
   input + truncated output. Skip assistant turns that were tool-calls-only.
3. **Gather deeper signal (required)** — `get_job_run_logs` and
   `retrieve_datastage_flow_code` whenever inputs exist; record each attempt as a
   transcript entry; never block on failure. The diagnosis must be informed by
   these, not the surface status.
4. **Diagnose** — classify (success: produced rows / vacuously empty / expected
   zero; or failure) with a **5–6 sentence hard cap**, citing transcript entries
   (`entry N`).
5. **Write the file** — under `agent/bug_reports/`. PII masked before writing
   (do NOT redact skill/tool names, error messages, schema/column names, user/
   project/asset/flow/job IDs, or public dataset names — those aid debugging).
   First line must be the H1 `# IBM watsonx.data integration Agent Bug Report`; no
   frontmatter, no `---` rules, only `#`/`##` headings; section order Session Info
   → Description → Transcript. Default name
   `watsonx_di_agent_bug_report_<YYYY-MM-DD>_<HH-MM-SS>_<slug>.md` (or `--name`).
   Ask before overwriting an existing file.
6. **Confirm** — print the absolute path, outcome, and transcript-entry count;
   don't echo the full report.

### Template

```markdown
# IBM watsonx.data integration Agent Bug Report

**Outcome:** [success | failure]

## Session Info

- **Agent Session ID:** `[uuid or null]`
- **LLM:** `[name-version or null]`
- **`get_session_info`:** [one bullet per returned field, verbatim, or `_tool unavailable._`]
- **Generated at:** [ISO-8601]

## Description

[5–6 sentences max. Outcome + direct reason; cite `entry N`. No background, no fixes.]

## Transcript

**1. turn — User**

​```text
[PII-redacted, verbatim]
​```

**2. [skill | tool] — `[name]` — status: [ok | error | unknown]**

- **Input:** [one-line summary]
- **Output:**

  ​```text
  [result, ~2000 chars; `_No output._` if none]
  ​```

[...continue numbering chronologically; turns and tool calls interleave...]
```
