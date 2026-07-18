# Gap Fix Plan — Integration, Delegation Pipeline, Architecture Docs

**Status:** Ready for implementation
**Scope:** Three structural gaps identified in the adversarial + deep analysis audit.
**Principle:** Every change is additive. No existing behaviour is altered. Every new path has a regression test.

---

## Overview

| Gap | What | Approach | Risk |
|-----|------|----------|------|
| Gap 1 | Opt-in integration is silent — users get p@3=0.60 when p@3=0.88 is available | `setup.sh` + `kb-status` CLI subcommand | Low — purely additive |
| Gap 2A | Delegation module is dead weight with no production use | `src/delegation/pipeline.py` connector (~60 lines) + `bob-optimize analyze` CLI subcommand | Medium — new module, needs tests + ADR |
| Gap 2B | Delegation coverage floor at 52% with no path to raise it | Integration tests for `pipeline.py`, raise floor to 70% | Low |
| Gap 3 | Two `ARCHITECTURE.md` files in overlapping paths cause navigation confusion | Rename `docs/ARCHITECTURE.md` → `docs/kb-manager/ARCHITECTURE.md` + update all cross-references | Low — file rename + reference updates |

---

## Sub-Task 1 — `kb-status` CLI subcommand

**Intent:** Expose the integration health of the full stack (embedding backend, index freshness, compression availability) as a machine-readable and human-readable `bob-optimize kb-status` command. Converts silent degradation into an observable, actionable state.

**Expected Outcomes:**
- `bob-optimize kb-status` prints a health table (human mode) or a JSON dict (--json mode)
- Reports: embedding backend (minilm | hashing), index doc count + staleness, compression availability, graph availability
- Returns exit code 0 if all tiers active, exit code 0 even if optional tiers absent (status, not error)
- Test in `tests/cli/test_cli.py` confirms subcommand is registered and returns expected keys

**Relevant context:**
- Add parser in `src/cli.py:build_parser()` after `kb-search` block (currently ends ~line 146)
- Add handler `elif args.command == "kb-status":` in `main()` after `kb-search` block (~line 313)
- Pattern to follow: `graph-health` (lines 111–117 parser, lines 251–285 handler) — same "import inside handler, emit structured dict" pattern
- `PersistentEmbeddingIndex` default path: `DEFAULT_INDEX_PATH = Path(".bob/kb-index")` (`src/embeddings/index.py` line 39)
- `GraphStore` default path: `DEFAULT_GRAPH_PATH` (`src/graph/store.py` line 23)
- `EmbeddingGenerator(backend="minilm")` resolution chain: mlx-embeddings → sentence-transformers → hashing (report which resolved)
- Test fixture: `_reset_config()` autouse fixture in `tests/cli/test_cli.py` lines 19–28

**Todo list:**
- [ ] Add `kb-status` subparser in `src/cli.py:build_parser()`:
  - Arguments: `--kb-path` (default `"docs/knowledge-base"`), `--index-path` (default `".bob/kb-index"`), `--graph-path` (default `".bob/kb-graph.json"`)
- [ ] Add handler in `src/cli.py:main()`:
  - Import inside handler (lazy): `EmbeddingGenerator`, `PersistentEmbeddingIndex`, `GraphStore`, `DEFAULT_INDEX_PATH`, `DEFAULT_GRAPH_PATH`
  - Build status dict with these keys: `embedding_backend` (str), `index_doc_count` (int), `index_path_exists` (bool), `index_stale_docs` (int — count of stale docs by walking KB and calling `is_stale()`), `graph_exists` (bool), `graph_node_count` (int or 0), `graph_edge_count` (int or 0), `compression_available` (bool — check `TokenOptimizer` importable and instantiable), `kb_path_exists` (bool), `kb_doc_count` (int — count .md files in four category dirs)
  - Human-readable output: aligned table, emoji indicators (✓/✗/⚠)
  - JSON output: raw dict
- [ ] Add test `test_kb_status_json` in `tests/cli/test_cli.py::TestCli`:
  - Call `_run_json(capsys, ["kb-status", "--json"])` (pass `--kb-path docs/knowledge-base` pointing to real KB dir)
  - Assert result has all required keys
  - Assert `compression_available` is bool, `index_doc_count` is int ≥ 0
- [ ] Ensure `test_parser_exposes_all_subcommands` still passes (it checks `parser._actions` subcommand choices)

**Status:** `[ ] pending`

---

## Sub-Task 2 — `setup.sh` full-stack integration script

**Intent:** Provide a single idempotent script that sequences install → KB index build → status confirmation. Replaces the silent opt-in with an explicit, observable first-run experience. Users who run `setup.sh` get the full p@3=0.88 system with one command.

**Expected Outcomes:**
- Running `./scripts/setup.sh` from repo root:
  1. Checks Python ≥ 3.11 availability; skips Python steps with clear message if absent
  2. Installs TOS: `pip install -e ".[dev,monitoring]"` (or `uv pip install -e ".[dev,monitoring]"` if `uv` available)
  3. Runs `bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic` (builds index + graph)
  4. Runs `bob-optimize kb-status` and prints the status table
  5. Prints "✅ Full stack active" or "⚠️ Partial stack — see status above"
- Script is idempotent: running twice does not error or double-install
- Script exits 0 even if Python is absent (Bob Shell CLI path still works)
- If `bob-optimize` install fails, KB Manager mode still works (fallback-safe contract maintained)

**Relevant context:**
- Existing `scripts/install.sh` handles Bob Shell CLI mode install; `setup.sh` is a complementary script
- `scripts/init-project.sh` handles KB directory creation in a target project
- Bob Shell KB Manager "no Python required" constraint (docs/ARCHITECTURE.md §2) must remain true
- Python detection: `command -v python3 && python3 --version | grep -E "3\.(11|12)"` pattern
- `uv` detection: `command -v uv`
- Graph build requires `--with-semantic` to get MiniLM embeddings; without it falls back to hashing (acceptable for first-run)

**Todo list:**
- [ ] Create `scripts/setup.sh` with `set -e` and the following logic:
  ```
  detect_python() — check python3 ≥ 3.11, return 0/1
  install_tos() — pip/uv install, export bob-optimize to PATH check
  build_index() — bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic (fallback: without --with-semantic if sentence-transformers absent)
  print_status() — bob-optimize kb-status (human-readable)
  main() — call detect_python; if 0 run install_tos+build_index+print_status; else print skip message; always exit 0
  ```
- [ ] Add `chmod +x scripts/setup.sh` note in the file header comment
- [ ] Add `setup.sh` to `README.md §5` (Get started in 5 minutes) as the recommended first step alongside `scripts/install.sh`
- [ ] Add `setup.sh` to `AGENTS.md` "Bob Shell Knowledge Manager — Installation" section

**Status:** `[ ] pending`

---

## Sub-Task 3 — `src/delegation/pipeline.py` — Analysis Pipeline connector

**Intent:** Activate the delegation module as the parallel analysis engine for repository analysis. Connects `DelegationCoordinator` → `TokenOptimizer` (compression) → KB ingestion in ~60 lines. This is the single highest-value integration: parallel analysis + compounding KB + token savings composing together.

**Expected Outcomes:**
- `src/delegation/pipeline.py` exposes one public function: `analyze_and_ingest(target_dir, kb_path, output_dir)` → `AnalysisPipelineResult`
- `ResearchAgent` runs first (priority HIGH) to load prior KB findings before other agents start
- All 6 agents run in parallel under `DelegationCoordinator(max_workers=5)`
- Each successful agent report is passed through `TokenOptimizer.optimize()` before being written to `output_dir/` as a structured KB research doc
- Returns a result dataclass with: per-agent status, compression ratios, total token savings, wall-clock time
- All filesystem writes are path-contained (use `src/tools/safe_paths.resolve_within`)

**Technical specification:**

```python
# src/delegation/pipeline.py

@dataclass
class AnalysisPipelineResult:
    target_dir: str
    agents_run: int
    agents_succeeded: int
    agents_failed: int
    compression_ratios: Dict[str, float]   # task_id -> ratio
    total_tokens_saved: int
    wall_clock_ms: float
    output_files: List[str]                # paths written
    coordinator_stats: Dict[str, Any]      # DelegationCoordinator.get_statistics()

def analyze_and_ingest(
    target_dir: str,
    kb_path: str = "docs/knowledge-base",
    output_dir: str = "docs/knowledge-base/research",
    max_workers: int = 5,
    depth: str = "shallow",
    *,
    compress: bool = True,   # pass results through TokenOptimizer
) -> AnalysisPipelineResult:
```

**Task ID scheme and dependency graph:**

```
research-task  (priority=CRITICAL, no deps)      <- ResearchAgent
    ↓ all others depend on research-task completing first
security-task  (priority=HIGH,   deps=[research-task])
quality-task   (priority=MEDIUM, deps=[research-task])
perf-task      (priority=MEDIUM, deps=[research-task])
arch-task      (priority=MEDIUM, deps=[research-task])
docs-task      (priority=LOW,    deps=[research-task])
```

**ResearchAgent task parameters:**
```python
SubAgentTask(
    task_id="research-task",
    task_type="research",
    target=target_dir,
    priority=SubAgentPriority.CRITICAL,
    parameters={
        "query": f"prior findings security quality performance architecture {Path(target_dir).name}",
        "max_results": 5,
    },
)
```

**Output file naming:** Each successful agent result writes to:
`{output_dir}/delegation-{agent_type}-{target_dir_slug}-{YYYY-MM-DD}.md`

**Output file format** (KB research doc template):
```markdown
---
title: "{AgentType} Analysis: {target_dir}"
date: {ISO date}
type: research
status: generated
tags: [delegation, {agent_type}, analysis]
generated_by: delegation-pipeline
target: {target_dir}
compression_ratio: {float}
---

# {AgentType} Analysis: {target_dir}

{agent result JSON formatted as markdown sections}
```

**Compression step:**
```python
if compress:
    result_text = _result_to_markdown(task_id, agent_type, result.data, target_dir)
    optimized = optimizer.optimize(result_text)
    content_to_write = optimized["optimized_text"]
    compression_ratio = optimized["compression_ratio"]
else:
    content_to_write = _result_to_markdown(...)
    compression_ratio = 1.0
```

**Relevant context:**
- `DelegationCoordinator` — `src/delegation/coordinator.py`; constructor `(max_workers, timeout_seconds=600, enable_retry=True)`
- `SubAgentPriority` enum: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4 (but CRITICAL not yet defined — use HIGH for research, or add CRITICAL to enum)
- `SubAgentTask.dependencies: List[str]` — list of task_id strings
- `TokenOptimizer.optimize(text)` → `{"optimized_text": str, "compression_ratio": float, ...}`
- `safe_paths.resolve_within(base, path)` — containment check, raises `ValueError` on escape
- Agent imports from `src/delegation/agents/__init__.py`
- `ResearchAgent` constructor: `(agent_id, kb_path="docs/knowledge-base", cache_enabled=True)`
- Other agents: `(agent_id, cache_enabled=True)`

**Todo list:**
- [ ] Add `CRITICAL = 5` to `SubAgentPriority` enum in `src/delegation/base.py` (or use `HIGH` for research — HIGH is sufficient since wave ordering handles the dependency anyway via `dependencies=[]`)
- [ ] Create `src/delegation/pipeline.py` with `AnalysisPipelineResult` dataclass and `analyze_and_ingest()` function per spec above
- [ ] Implement `_result_to_markdown(task_id, agent_type, data, target_dir) -> str` helper — renders agent result dict as KB research doc markdown with frontmatter
- [ ] Implement `_safe_write(output_dir, filename, content)` helper — uses `resolve_within` before writing
- [ ] Add `from src.delegation.pipeline import analyze_and_ingest, AnalysisPipelineResult` to `src/delegation/__init__.py` exports
- [ ] Ensure `src/tools/safe_paths` is imported inside the function (not at module top) to avoid circular imports — check import graph

**Status:** `[ ] pending`

---

## Sub-Task 4 — `bob-optimize analyze` CLI subcommand

**Intent:** Expose the delegation pipeline as a first-class CLI subcommand so users can run `bob-optimize analyze src/cache` and get structured KB research docs in one command.

**Expected Outcomes:**
- `bob-optimize analyze <target> [--kb-path] [--output-dir] [--workers] [--depth] [--no-compress] [--json]`
- Prints pipeline result summary (human) or JSON dict with all keys from `AnalysisPipelineResult`
- On error (target not found, pipeline failure), emits JSON error dict and exits 1
- Test in `tests/cli/test_cli.py` confirms subcommand parses correctly; integration test in `tests/delegation/test_pipeline.py` confirms end-to-end

**CLI parser spec:**
```python
# in build_parser(), after kb-search block
analyze_p = sub.add_parser(
    "analyze",
    help="Run parallel delegation analysis and ingest results into the KB",
)
analyze_p.add_argument(
    "target",
    help="Directory or file to analyze (e.g. 'src/cache' or 'src/optimizer/prompt_optimizer.py')",
)
analyze_p.add_argument("--kb-path", default="docs/knowledge-base", metavar="PATH",
                        help="Knowledge base root for ResearchAgent context lookup")
analyze_p.add_argument("--output-dir", default="docs/knowledge-base/research", metavar="PATH",
                        help="Directory to write generated research docs")
analyze_p.add_argument("--workers", type=int, default=5, metavar="N",
                        help="Maximum parallel analysis workers (default: 5)")
analyze_p.add_argument("--depth", choices=["shallow", "deep"], default="shallow",
                        help="Analysis depth passed to each agent")
analyze_p.add_argument("--no-compress", action="store_true",
                        help="Skip TokenOptimizer compression step (write raw reports)")
```

**Handler spec (in `main()`):**
```python
elif args.command == "analyze":
    from src.delegation.pipeline import analyze_and_ingest
    try:
        pipeline_result = analyze_and_ingest(
            target_dir=args.target,
            kb_path=args.kb_path,
            output_dir=args.output_dir,
            max_workers=args.workers,
            depth=args.depth,
            compress=not args.no_compress,
        )
        _emit(pipeline_result.__dict__, as_json)
    except Exception as exc:
        _emit({"error": str(exc)}, as_json)
        return 1
```

**Todo list:**
- [ ] Add `analyze` subparser to `build_parser()` in `src/cli.py`
- [ ] Add `elif args.command == "analyze":` handler in `main()`
- [ ] Add `test_analyze_json` in `tests/cli/test_cli.py::TestCli` — mock `analyze_and_ingest` and verify CLI wiring
- [ ] Ensure `test_parser_exposes_all_subcommands` still passes

**Status:** `[ ] pending`

---

## Sub-Task 5 — Tests for `src/delegation/pipeline.py`

**Intent:** Bring the delegation pipeline to tested quality with unit and integration tests. Raise the `src/delegation` per-package coverage floor from 52% to 70%.

**Expected Outcomes:**
- `tests/delegation/test_pipeline.py` with ≥ 8 test functions
- All tests pass, no real filesystem writes (use `tmp_path` pytest fixture)
- `scripts/check_coverage_by_package.py` floor for `src/delegation` updated from 52 to 70
- CI green on `pytest tests/delegation/`

**Test specification:**

```python
# tests/delegation/test_pipeline.py

class TestAnalyzeAndIngest:
    def test_returns_pipeline_result_dataclass(self, tmp_path):
        # Arrange: create minimal target dir with one .py file
        # Mock DelegationCoordinator.execute_parallel() to return SUCCESS results
        # Mock TokenOptimizer.optimize() to return {"optimized_text": "...", "compression_ratio": 0.8}
        # Act: analyze_and_ingest(str(tmp_path/"src"), output_dir=str(tmp_path/"out"))
        # Assert: result is AnalysisPipelineResult, agents_run == 6

    def test_research_agent_runs_with_no_deps(self, tmp_path):
        # Assert research task has empty dependencies list
        # Assert all other tasks have dependencies=["research-task"]

    def test_output_files_written_to_output_dir(self, tmp_path):
        # Assert written files exist under output_dir
        # Assert filenames match delegation-{agent_type}-*-*.md pattern

    def test_compression_applied_when_compress_true(self, tmp_path):
        # Mock optimizer.optimize — assert it is called once per successful agent
        # Assert compression_ratios dict is populated

    def test_compression_skipped_when_no_compress(self, tmp_path):
        # compress=False — assert optimizer.optimize NOT called

    def test_path_traversal_blocked(self, tmp_path):
        # Pass target_dir="../../../etc" — assert ValueError raised or returns error result

    def test_failed_agents_not_written(self, tmp_path):
        # Mock coordinator to return 2 SUCCESS + 1 FAILED
        # Assert output_files has 2 entries, not 3

    def test_coordinator_stats_included_in_result(self, tmp_path):
        # Assert result.coordinator_stats is a dict with "total_tasks" key
```

**Mocking pattern** (follow existing delegation test pattern in `tests/delegation/test_coordinator.py`):
```python
from unittest.mock import patch, MagicMock
from src.delegation.pipeline import analyze_and_ingest, AnalysisPipelineResult
```

**Coverage floor update:**
- File: `scripts/check_coverage_by_package.py`
- Change: `"src/delegation": 52` → `"src/delegation": 70`
- This is the single home for the floor value (per "one home per value" rule)

**Todo list:**
- [ ] Create `tests/delegation/test_pipeline.py` with the 8 test functions specified above
- [ ] Update `scripts/check_coverage_by_package.py`: change delegation floor from 52 to 70
- [ ] Run `pytest tests/delegation/ --cov=src/delegation` locally to verify floor is met before pushing

**Status:** `[ ] pending`

---

## Sub-Task 6 — ADR-019: Delegation Pipeline Activation

**Intent:** Document the decision to activate the delegation module as an analysis pipeline, per the project's ADR culture (append-only, decisions never rewritten). This closes the architectural limbo of "maintained but not actively developed."

**Expected Outcomes:**
- `docs/adr/019-delegation-pipeline-activation.md` exists and is valid ADR format
- `docs/adr/README.md` updated to list ADR-019
- `src/delegation/EXPERIMENTAL.md` status section updated to reflect "now integrated as pipeline"

**ADR content spec:**
```markdown
---
id: ADR-019
title: Activate Delegation Module as Analysis Pipeline
date: {date}
status: Accepted
---

## Context
The delegation module (src/delegation/) was built in Phase 2 as a parallel sub-agent
framework for repository analysis. Since Phase 4 it has been marked EXPERIMENTAL and
held at a 52% coverage floor. Three integration scenarios were evaluated in
delegation-integration-analysis-2026-07-13.md. The Phase-8 sign-off identified the
module as "dead weight" — maintained but delivering no user value.

## Decision
Activate the delegation module as the parallel analysis engine for repo analysis, via
a thin pipeline.py connector (~60 lines). The connector sequences:
  1. DelegationCoordinator fans out 6 agents in parallel
  2. ResearchAgent runs first (dependency ordering) to load prior KB findings
  3. Each agent result is compressed via TokenOptimizer before KB write
  4. Results land in docs/knowledge-base/research/ as structured research docs

The facade (TokenOptimizer) is NOT modified. The delegation module remains in
src/delegation/ but is no longer "experimental" — it has a production use case.

## Consequences
- src/delegation/pipeline.py is the new integration surface (~60 lines)
- Coverage floor raised from 52% to 70%
- bob-optimize analyze CLI subcommand exposes the pipeline
- The "three systems in one repo" characterisation no longer applies: delegation
  is now the parallel analysis backend for the repo-analyzer use case
```

**Todo list:**
- [ ] Create `docs/adr/019-delegation-pipeline-activation.md` with content above
- [ ] Add ADR-019 entry to `docs/adr/README.md` table
- [ ] Update `src/delegation/EXPERIMENTAL.md` status header: change "Experimental / Not Integrated" to "Integrated — Analysis Pipeline" and update the status checklist

**Status:** `[ ] pending`

---

## Sub-Task 7 — Rename `docs/ARCHITECTURE.md` → `docs/kb-manager/ARCHITECTURE.md`

**Intent:** Eliminate the filename collision between the two ARCHITECTURE.md files. Zero content changes — purely a structural rename + cross-reference update.

**Expected Outcomes:**
- `docs/ARCHITECTURE.md` no longer exists
- `docs/kb-manager/ARCHITECTURE.md` exists with identical content
- All cross-references updated (README.md, AGENTS.md, docs/INDEX.md, docs/README.md)
- `grep -r "docs/ARCHITECTURE.md" .` returns 0 results (except git history)
- Navigation: `docs/README.md` has a clear "Documentation map" routing contributors to the correct file

**Files to update:**
- `README.md` line 26: `[KB Manager — docs/ARCHITECTURE.md]` → `[KB Manager — docs/kb-manager/ARCHITECTURE.md]`
- `AGENTS.md` documentation table: update `docs/ARCHITECTURE.md` reference
- `docs/INDEX.md`: update entry for KB Manager architecture
- `docs/README.md`: add "Documentation map" section routing to both architecture docs
- `docs/architecture/ARCHITECTURE.md` line 15: update the "Not to be confused with" cross-reference
- `docs/kb-manager/ARCHITECTURE.md` (the renamed file) line 10: update the self-reference

**Todo list:**
- [ ] Create `docs/kb-manager/` directory
- [ ] Move `docs/ARCHITECTURE.md` to `docs/kb-manager/ARCHITECTURE.md` (content unchanged)
- [ ] Update internal self-reference in `docs/kb-manager/ARCHITECTURE.md` line 10 (path to architecture/ARCHITECTURE.md is still valid as relative path `../architecture/ARCHITECTURE.md`)
- [ ] Update `README.md` line 26 cross-reference
- [ ] Update `AGENTS.md` documentation table cross-reference
- [ ] Update `docs/INDEX.md` entry
- [ ] Update `docs/README.md` — add "Documentation Map" section
- [ ] Update `docs/architecture/ARCHITECTURE.md` line 15 cross-reference: `[docs/ARCHITECTURE.md]` → `[docs/kb-manager/ARCHITECTURE.md]`
- [ ] Run `grep -r "docs/ARCHITECTURE.md" --include="*.md" .` to confirm no remaining references

**Status:** `[ ] pending`

---

## Sub-Task 8 — CI gate updates and final validation

**Intent:** Ensure CI passes cleanly after all changes. Update the API docs freshness gate (new public module), update community health check (new script), confirm all coverage floors are met.

**Expected Outcomes:**
- `python scripts/generate_api_docs.py --check` passes (regenerate docs/api/ to include new modules)
- `python scripts/check_coverage_by_package.py coverage.json` passes with new 70% delegation floor
- `python scripts/check_community_health.py` passes (setup.sh counted as a script)
- `python scripts/check_layering.py src` passes (no src → scripts imports introduced)
- `python scripts/check_value_homes.py` passes (no new duplicated literals)
- `bandit -r src/ -ll` clean (pipeline.py has no subprocess, no eval, no shell=True)
- All existing tests still pass (no regressions)
- `test_parser_exposes_all_subcommands` passes with `kb-status` and `analyze` added

**Todo list:**
- [ ] Regenerate `docs/api/` by running `python scripts/generate_api_docs.py` (adds pipeline module)
- [ ] Confirm `python scripts/check_layering.py src` passes
- [ ] Confirm `python scripts/check_value_homes.py` passes
- [ ] Confirm `bandit -r src/ -ll` clean
- [ ] Run full test suite: `pytest tests/ --cov=src` — confirm ≥ 80% overall, delegation ≥ 70%
- [ ] Confirm `test_parser_exposes_all_subcommands` enumerates `kb-status` and `analyze`

**Status:** `[ ] pending`

---

## Execution Order

Sub-tasks are ordered so each is independently reviewable:

```
Sub-Task 7 (file rename)        — zero risk, no deps, do first
Sub-Task 1 (kb-status CLI)      — additive to cli.py, no deps on delegation
Sub-Task 2 (setup.sh)           — depends on Sub-Task 1 (calls kb-status)
Sub-Task 3 (pipeline.py)        — core delegation activation
Sub-Task 4 (analyze CLI)        — depends on Sub-Task 3
Sub-Task 5 (pipeline tests)     — depends on Sub-Task 3
Sub-Task 6 (ADR-019)            — depends on Sub-Task 3 (documents what was built)
Sub-Task 8 (CI validation)      — depends on all above
```

## Files Changed Summary

| File | Change |
|------|--------|
| `src/cli.py` | Add `kb-status` and `analyze` subcommand parsers + handlers |
| `src/delegation/pipeline.py` | New file — analysis pipeline connector |
| `src/delegation/__init__.py` | Export `analyze_and_ingest`, `AnalysisPipelineResult` |
| `src/delegation/EXPERIMENTAL.md` | Update status header |
| `scripts/setup.sh` | New file — full-stack setup script |
| `scripts/check_coverage_by_package.py` | Raise delegation floor 52 → 70 |
| `tests/cli/test_cli.py` | Add `test_kb_status_json`, `test_analyze_json` |
| `tests/delegation/test_pipeline.py` | New file — 8 pipeline tests |
| `docs/adr/019-delegation-pipeline-activation.md` | New ADR |
| `docs/adr/README.md` | Add ADR-019 entry |
| `docs/ARCHITECTURE.md` | Deleted (renamed) |
| `docs/kb-manager/ARCHITECTURE.md` | New location (moved, content unchanged) |
| `README.md` | Update cross-reference line 26, add setup.sh to §5 |
| `AGENTS.md` | Update architecture doc reference |
| `docs/INDEX.md` | Update KB Manager architecture entry |
| `docs/README.md` | Add Documentation Map section |
| `docs/architecture/ARCHITECTURE.md` | Update cross-reference line 15 |
| `docs/api/` | Regenerated (adds pipeline module) |
