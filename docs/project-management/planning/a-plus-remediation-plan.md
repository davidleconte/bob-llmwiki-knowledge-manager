# A+ Remediation Plan — Institutional Standard Gap Closure
<!-- Owner: Architecture Review 2026-07-16 · Branch: fix-multilevel-cache-race -->
<!-- Status: PENDING — awaiting user approval before implementation -->

## Top-Level Overview

**Goal:** Close all remaining gaps between the current A (4.09/4.30) grade and institutional
A+ (4.30/4.30) by addressing every finding from the architecture review that was confirmed
live in the codebase. Strictly no scope creep — each sub-task maps 1:1 to a confirmed
code defect or governance gap.

**What this plan does NOT touch:**
- The delegation module internals (intentionally experimental, separate subsystem)
- Any existing tests that are already passing
- Documentation that already carries valid retraction banners
- Any ADR content or architecture decisions

**Approach:** Minimal, surgical edits. Every change is the smallest possible fix that closes
its specific finding. No refactors, no new features, no cleanup of adjacent code.

**Validation gate:** After all sub-tasks, a full `pytest --cov=src --cov-report=json:coverage.json`
+ all `scripts/check_*.py` gates + `ruff check` + `mypy` must all pass clean.

---

## Sub-Task 1 — Fix ruff F401 Unused Imports (P0 — Blocks CI)

**Intent:** Two auto-fixable lint errors prevent `ruff check` from passing in CI. These
are stale imports that were never cleaned up after code changed around them.

**Root cause:**
- `src/cache/multi_level_cache.py:26` — `List` is imported from `typing` but never used in
  the module body (all list annotations now use the built-in `list` lowercase form).
- `src/embeddings/index.py:21` — `time` is imported at top level but never called in this
  file (timing is done in `indexer.py`, not `index.py`).

**Expected Outcomes:**
- `ruff check src/` exits 0 with no F401 errors.
- No other behaviour changes.

**Todo List:**
1. In `src/cache/multi_level_cache.py` line 26: remove `List` from the `typing` import
   (keep `TYPE_CHECKING, Any, Dict, Optional, Tuple`).
2. In `src/embeddings/index.py` line 21: remove `import time` entirely.
3. Run `ruff check src/` and confirm clean.

**Relevant Context:**
- `src/cache/multi_level_cache.py:26` — `from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple`
- `src/embeddings/index.py:21` — `import time`
- CI lint job: `.github/workflows/ci.yml:76-78` — `ruff check src tests scripts`

**Status:** [ ] pending

---

## Sub-Task 2 — Fix mypy Type Errors in src/embeddings/indexer.py (P0 — Blocks CI)

**Intent:** Three mypy errors in `src/embeddings/indexer.py` prevent the type gate from
passing. They are caused by: (a) using `logging.Logger.info()` with keyword arguments it
does not accept (it only takes `*args`), and (b) the `query()` method's return annotation
saying `list` when the actual return value from `KnowledgeBaseQuery.query()` is a `dict`.

**Root cause:**
- Line 61-65: `logger = logging.getLogger(__name__)` returns a standard `logging.Logger`.
  `logger.info("msg", total_docs=total, elapsed_ms=...)` passes keyword args to the
  `logging.Logger.info(msg, *args, **kwargs)` signature — but `**kwargs` in the stdlib
  logger is for `extra=`, `stack_info=`, `stacklevel=` only. Keyword arguments that are
  not recognized log keywords produce a mypy error.
  **Fix:** convert the structured kwargs to a formatted string message. The rest of the
  codebase uses `LoggerFactory` for structured logging; `indexer.py` uses the stdlib
  `logging.getLogger` directly (a P3 inconsistency but not the P0 fix). The minimal fix
  is to use positional format args or an f-string.
- Line 73: `def query(...) -> list:` but `kb.query()` at line 97 returns a `dict`
  (per `KnowledgeBaseQuery.query()` signature and docstring). The annotation must be `dict`.

**Expected Outcomes:**
- `mypy` exits 0 with 0 errors (currently 3 errors in 1 file).
- `indexer.py` behaviour is identical — the log message content is unchanged.

**Todo List:**
1. In `src/embeddings/indexer.py` line 61-65: replace the keyword-arg `logger.info` call
   with a plain formatted string call: `logger.info("kb_indexer_sync_complete total_docs=%d elapsed_ms=%.1f", total, round(elapsed_ms, 1))`
2. In `src/embeddings/indexer.py` line 73: change the return annotation from `list` to `dict`.
3. Run `mypy src/` and confirm 0 errors.

**Relevant Context:**
- `src/embeddings/indexer.py:30` — `logger = logging.getLogger(__name__)`
- `src/embeddings/indexer.py:61-65` — the info() call with kwargs
- `src/embeddings/indexer.py:73` — `def query(...) -> list:`
- `src/embeddings/indexer.py:97` — `return kb.query(query_text, max_results=top_k)`
- `src/tools/kb_query.py` — `KnowledgeBaseQuery.query()` returns a `dict`

**Status:** [ ] pending

---

## Sub-Task 3 — Bound _lookup_times with deque to Prevent Unbounded Memory Growth (P1)

**Intent:** `MultiLevelCache._lookup_times` is a plain `list[float]` that grows by one
entry on every cache operation (get hit, miss, or L2 lookup). Under sustained load this
is an unbounded memory sink. The monitoring module already uses `deque(maxlen=1000)` for
the same pattern in `LatencyStats.recent` — apply the same bound here.

**Root cause:**
- `src/cache/multi_level_cache.py:118` — `self._lookup_times: list[float] = []`
- Every `get()` call appends to this list (lines ~152, 185, 199) via
  `self._lookup_times.append(time.time() - start_time)`.
- `stats()` and `average_lookup_time_ms()` both compute `sum(self._lookup_times) / len(...)`.
- With `maxlen=10_000`, the deque automatically drops the oldest entries while preserving
  accurate rolling statistics. The `sum()` computation is O(maxlen) rather than O(all-time).

**Expected Outcomes:**
- `_lookup_times` is a `deque[float]` with `maxlen=10_000`.
- `clear()` still works (calls `.clear()` on the deque — same API).
- `reset_stats()` still works (calls `.clear()` on the deque).
- `stats()` and `average_lookup_time_ms()` produce identical results for workloads
  under 10k entries; bounded to the rolling window above that.
- All existing tests pass unchanged (the deque is API-compatible with list for `.append`,
  `.clear`, `len()`, and `sum()`).

**Todo List:**
1. In `src/cache/multi_level_cache.py`, add `from collections import deque` to the imports.
2. Change line 118: `self._lookup_times: list[float] = []` →
   `self._lookup_times: deque[float] = deque(maxlen=10_000)`.
3. Update the type annotation in the class if it is declared elsewhere (check for any
   `_lookup_times` type hints in comments or docstrings).
4. Run `pytest tests/cache/` and confirm all cache tests pass.

**Relevant Context:**
- `src/cache/multi_level_cache.py:118` — the field definition
- `src/cache/multi_level_cache.py:152,185,199` — `.append()` call sites
- `src/cache/multi_level_cache.py:330-334` — `stats()` average computation
- `src/cache/multi_level_cache.py:429-437` — `average_lookup_time_ms()` computation
- `src/cache/multi_level_cache.py:261-269` — `clear()` method calls `.clear()`
- `src/cache/multi_level_cache.py:489-494` — `reset_stats()` calls `.clear()`
- `src/monitoring/metrics.py:28` — `deque(maxlen=1000)` precedent in `LatencyStats`

**Decision:** `maxlen=10_000` confirmed (10x the `LatencyStats` precedent, appropriate for
the cache operation frequency which is higher than per-request latency sampling).

**Status:** [ ] pending

---

## Sub-Task 4 — Add Per-Package Coverage Floor for src/embeddings (P3)

**Intent:** `src/embeddings/store.py` currently measures 79.3% — below the global 80%
gate if the rest of the suite were not compensating. The `src/embeddings/` package has no
declared per-package floor, so this cannot silently regress. Adding targeted tests for the
uncovered OSError branches and declaring a floor at 80% (the global gate level) makes the
coverage enforceable per-package.

**Root cause:**
- `scripts/check_coverage_by_package.py:45-50` — `FLOORS` dict has no entry for
  `src/embeddings`.
- `src/embeddings/store.py` — 79.3% (lines 117-122, 130-135 are the uncovered error paths
  in the atomic tmp-then-rename flush operation).
- The correct approach: add tests for the `OSError` paths in `FileBackedVectorStore.save()`
  and `load()`, then declare the floor.

**Expected Outcomes:**
- `src/embeddings/` coverage reaches ≥ 80% (matching the global gate level).
- `scripts/check_coverage_by_package.py` includes `"src/embeddings": 80.0` in `FLOORS`.
- Tests for the `OSError` / `FileNotFoundError` paths in `store.py` exist and pass.
- CI `check_coverage_by_package.py` gate enforces the new floor.

**Todo List:**
1. Read `src/embeddings/store.py` in full to understand the uncovered branches
   (lines 117-122 and 130-135 — the `except Exception` blocks around `np.save` /
   `json.dump` and the temp-file rename).
2. Add tests to `tests/embeddings/` (create the file if it does not exist) that:
   - Mock `np.save` or the file write to raise `OSError` and assert graceful handling.
   - Mock `json.load` / `np.load` in `load()` to raise and assert `None` is returned.
3. Run `pytest tests/embeddings/ --cov=src/embeddings --cov-report=term-missing` and
   confirm `src/embeddings/store.py` reaches ≥ 80%.
4. Add `"src/embeddings": 80.0` to `FLOORS` in `scripts/check_coverage_by_package.py`
   with a rationale comment matching the existing pattern.
5. Run the full `check_coverage_by_package.py` gate and confirm it passes.

**Relevant Context:**
- `src/embeddings/store.py:117-122` and `130-135` — uncovered OSError branches
- `scripts/check_coverage_by_package.py:45-50` — `FLOORS` dict to extend
- `tests/embeddings/` — may need to be created; check if it exists already
- Existing test pattern for similar error-path coverage: `tests/tools/test_safe_paths.py`

**Status:** [ ] pending

---

## Sub-Task 5 — Document the Facade Config-Cache Design Gap (P2 Architecture)

**Intent:** The current `TokenOptimizer` facade builds a config-driven `MultiLevelCache`
but shares only the L1 (`ExactCache`) with the optimizer. This means `config.cache.l2*`
settings (L2 size, threshold, TTL) have zero effect on the `optimize()` hot path. This
is architecturally correct by design (semantic cache must not return a different prompt's
optimization), but it is undisclosed in the public docstrings and produces a
"dead config field" experience for operators who configure L2 settings expecting them
to affect optimization.

**This sub-task is documentation-only — no code changes.** The correct resolution is
to document the behaviour explicitly, not to wire L2 into the optimizer (which would
be wrong by design).

**Expected Outcomes:**
- `src/facade.py` docstring clearly states that `config.cache.l2*` governs only the
  `cache.get()` / `cache_stats()` surface, not `optimize()`.
- `src/factory.py` `build_optimizer()` docstring references this distinction.
- An ADR entry or inline note explains WHY this is intentional (semantic cache safety).

**Todo List:**
1. In `src/facade.py`, extend the class-level docstring `config.monitoring` section
   to add a `config.cache` section explaining: L1 governs `optimize()` caching (shared
   instance); L2 governs only the `cache` surface (separate namespace by design — an
   L2 hit could return a different prompt's optimization, which is unsafe).
2. In `src/facade.py` `Attributes` section for `cache`, add a note that `config.cache.l2*`
   fields affect this attribute's behaviour, not `optimizer`.
3. In `src/factory.py` `build_optimizer()` docstring, add a one-line note: "L2 is
   intentionally not shared with the optimizer — see the facade class docstring."
4. Run `python scripts/generate_api_docs.py --check` to confirm the API docs remain
   in sync, then regenerate if needed with `python scripts/generate_api_docs.py`.

**Relevant Context:**
- `src/facade.py:44-157` — the class docstring and Attributes section
- `src/facade.py:80-93` — the `build_cache` / `build_optimizer` composition
- `src/factory.py:45-63` — `build_optimizer()` docstring
- `docs/api/` — auto-generated; regenerate after docstring changes
- `scripts/generate_api_docs.py --check` — CI enforces drift

**Status:** [ ] pending

---

## Validation Plan

After all five sub-tasks are complete, run the full validation suite in order:

```bash
# 1. Lint gate (P0 fixes verified)
ruff check src tests scripts
ruff format --check src tests scripts

# 2. Type gate (P0 fixes verified)
mypy

# 3. Full test suite + coverage gate
pytest --cov=src --cov-report=json:coverage.json --cov-report=term-missing

# 4. Per-package coverage floors (includes new src/embeddings floor)
python scripts/check_coverage_by_package.py coverage.json

# 5. All governance and consistency gates
python scripts/check_layering.py
python scripts/check_savings_claims.py
python scripts/check_value_homes.py
python scripts/check_status_consistency.py
python scripts/check_community_health.py

# 6. API docs freshness (verify sub-task 5 docstring changes are in sync)
python scripts/generate_api_docs.py --check
```

All gates must exit 0. No new warnings, no skipped tests that were previously passing.

---

## Out of Scope (Explicitly Not in This Plan)

The following findings from the architecture review are **accepted residuals** or
**already fixed** and are not part of this plan:

| Finding | Disposition |
|---|---|
| `documentation_agent.py` rglob not using `resolve_within` | **Already fixed** — `resolve_within` is present at line 56; Phase-8 finding was stale |
| Versioned-key colon collision in `ExactCache` | **Already fixed** — `escape_version()` is called in `exact_cache.py:146` |
| `ConfigManager.load_from_env()` skips validation | **Already fixed** — `_validator.validate(candidate)` is present at `manager.py:177` |
| `INSTALLATION.md` broken clone URL | **Already fixed** — no broken URL in current file |
| `README.md` "Full transcript" overstatement | **Already fixed** — not present in current file |
| Wall-clock latency assertions in tests | **Accepted residual** — documented in `tests/README.md:90`; no clock injection added |
| `evaluation/requirements.txt` second unpinned manifest | **Accepted residual** — low risk; out of scope |
| `pip-audit` non-blocking | **Not applicable** — `ci.yml:242` already has `--strict` and no `continue-on-error` |
| CI installs on `>=` floors | **Not applicable** — `ci.yml` already uses `uv sync --frozen` |
| `MonitoringConfig.health_check_interval` dead config | **Accepted residual** — documented in facade docstring |
| `README.md §5` "Proof point" | **Already fixed** — section removed/corrected in current file |
