# A+ Remediation Plan
# Move every dimension from current grade to A+

**Current overall grade:** A− (3.77 / 4.0) adversarial re-audit 2026-07-14  
**Target:** A+ (≥ 4.1 / 4.0 weighted) across all 7 dimensions  
**Rule:** One sub-task per dimension gap. Gates must stay green after every sub-task.

---

## Dimension A — Product Integrity (current: A → target: A+)

**Gap A1:** README.md:174-178 cites "one reported run on a 94-module platform allegedly
cost 0.36 Bobcoins" with the caveat "cannot be independently verified." It is an
anecdotal claim with zero provenance (no token counts, model, tokenizer, or manifest).
At A+ standard, *every published number either cites a manifest or is removed*.

### Sub-task A1 — Remove the 0.36 Bobcoin anecdote from README.md

**Intent:**
The anecdote is intellectually honest (the "cannot be independently verified" caveat
is explicit) but its presence in a section titled "Token savings — measured,
manifest-backed" weakens the entire section. The measured ~20% headline already
demonstrates the optimizer's value with full provenance. The anecdote adds noise.
Remove the whole paragraph; the section is stronger without it.

**Expected Outcomes:**
- README.md §8 contains only manifest-backed, provenance-cited savings numbers.
- The retracted 68.96% callout stays (it is the retraction record, not a claim).
- `check_savings_claims.py` continues to pass (the number being removed is the
  anecdotal one, not a manifest-backed claim — removal is safe).
- No other files reference the 0.36 Bobcoin figure as a live claim.

**Todo List:**
1. Read `README.md:170-180` to confirm exact paragraph boundaries.
2. Delete lines 174-178 (the "On the 0.36 Bobcoin HCD example:" paragraph).
3. Run `python3 scripts/check_savings_claims.py && python3 scripts/check_status_consistency.py`.

**Relevant Context:**
- `README.md:157-178` — §8 "Token savings" section
- `scripts/check_savings_claims.py` — must pass after removal

**Status:** [x] closed — 0.36 Bobcoin paragraph not present in current README; section contains only manifest-backed figures.

---

## Dimension B — Architecture & Design (current: B+ → target: A+)

Two confirmed defects:
- **B1:** `CacheConfig.version_support_enabled` and `max_versions` are validated,
  stored, and present in the manifest — but `build_cache()` in `factory.py:31-39`
  never passes them to `MultiLevelCache.__init__()`, which has no parameters for
  them. Config control over versioning is declared but non-functional.
- **B2:** `MonitoringConfig.log_level`, `metrics_enabled`, `health_check_interval`
  are declared and validated but the facade (`facade.py:9-11`) does not apply them.
  The logger constructor already accepts `log_level` (`logger.py:47`); it is simply
  never called with `config.monitoring.log_level`.

### Sub-task B1 — Wire version_support_enabled / max_versions to ExactCache and MultiLevelCache

**Intent:**
`ExactCache` already implements versioning (`_make_versioned_key`, `migrate`,
`cleanup_version`) but its `__init__` has no `version_support_enabled` or
`max_versions` parameters. `MultiLevelCache` wraps `ExactCache`. The fix is:
(1) add both parameters to `ExactCache.__init__`; (2) store and respect
`version_support_enabled` (when False, `_make_versioned_key` returns the plain key);
(3) pass both through `MultiLevelCache.__init__` to its internal `ExactCache`;
(4) pass both through `build_cache()`.

This is the same class of wiring fix as `strategies` was for the optimizer.

**Expected Outcomes:**
- `ExactCache.__init__` accepts `version_support_enabled: bool = True` and
  `max_versions: int = 5`.
- When `version_support_enabled=False`, `ExactCache` stores and retrieves entries
  without a version prefix (or equivalent no-op behaviour).
- `MultiLevelCache.__init__` accepts and threads both params into its L1 cache.
- `build_cache(config)` passes `config.version_support_enabled` and
  `config.max_versions`.
- `factory.py` docstring updated: "every CacheConfig field takes effect."
- Existing tests pass unchanged (defaults match current behaviour).
- New test: `test_version_support_disabled` — when `version_support_enabled=False`
  the cache stores and retrieves entries correctly.
- All gate scripts pass.

**Todo List:**
1. Read `src/cache/exact_cache.py:55-130` (full __init__ and versioning methods).
2. Read `src/cache/multi_level_cache.py:44-80` (full __init__).
3. Add `version_support_enabled: bool = True` and `max_versions: int = 5` to
   `ExactCache.__init__`; store as `self.version_support_enabled` and
   `self.max_versions`.
4. In `_make_versioned_key()`: if `not self.version_support_enabled`, return
   the plain SHA-256 key without the version prefix.
5. Add `version_support_enabled: bool = True` and `max_versions: int = 5` to
   `MultiLevelCache.__init__`; pass both through to `ExactCache(...)`.
6. Update `build_cache()` in `factory.py` to pass `config.version_support_enabled`
   and `config.max_versions`; update docstring.
7. Add a test to `tests/cache/test_exact_cache.py`: when initialized with
   `version_support_enabled=False`, set/get round-trips correctly.
8. Run `uv run pytest tests/cache/ -q --tb=short` — must pass.
9. Run all gate scripts — must pass.

**Relevant Context:**
- `src/cache/exact_cache.py:55-130` — ExactCache.__init__, _make_versioned_key
- `src/cache/multi_level_cache.py:44-80` — MultiLevelCache.__init__
- `src/factory.py:25-39` — build_cache
- `src/config/schema.py:33-34` — the fields (version_support_enabled, max_versions)
- `src/config/validator.py:94-115` — validation already works; no changes needed
- `evaluation/results/validation-2026-07-14/manifest.json` — both fields already
  present in manifest config (version_support_enabled: true, max_versions: 5)

**Status:** [x] closed — `version_support_enabled` and `max_versions` wired through `ExactCache`, `MultiLevelCache`, and `build_cache()`.

---

### Sub-task B2 — Wire MonitoringConfig fields through the facade

**Intent:**
`MonitoringConfig` has three fields not applied by the facade: `log_level`,
`metrics_enabled`, and `health_check_interval`. The logger already accepts
`log_level` as a constructor argument (`logger.py:47`). The fix has two parts:

(A) **log_level:** `get_logger(component)` should respect `config.monitoring.log_level`.
The simplest approach: `get_logger` already forwards kwargs to `StructuredLogger`;
the facade can call `get_logger("facade.token_optimizer", log_level=config.monitoring.log_level)`.

(B) **metrics_enabled:** When `False`, the facade should skip recording metrics.
`MetricsCollector` is already instantiated; the facade holds `self._metrics`. The
minimal fix is to set a `self._metrics_enabled` flag from config and guard the
`record_*` call in the facade's `optimize()` path. Since the optimizer and cache
have their own internal `_metrics` instances, this flag only governs what the facade
itself records — which is the correct scope.

(C) **health_check_interval:** `HealthChecker` runs checks on-demand (called by
`health()`), not on a timer. `health_check_interval` as a timer-based scheduler
would require a background thread — out of scope for Beta. The minimal correct
fix is to document in the facade that `health_check_interval` governs a future
proactive scheduling feature and is currently not enforced (on-demand only). This
turns B2 from an undocumented gap into a documented, intentional deferral.

**Expected Outcomes:**
- `facade.py:9-11` note updated: `log_level` and `metrics_enabled` are now applied;
  `health_check_interval` is documented as "deferred — health checks are on-demand."
- The facade passes `config.monitoring.log_level` to `get_logger()`.
- The facade reads `config.monitoring.metrics_enabled` and gates its own
  `self._metrics` usage accordingly.
- `config.monitoring.health_check_interval` has an explicit "not yet scheduled —
  on-demand only" note in the facade docstring, converting it from silent dead
  field to documented limitation.
- All gate scripts pass.

**Todo List:**
1. Read `src/monitoring/__init__.py` to see what `get_logger` signature accepts.
2. Update `facade.py:89`: pass `log_level=config.monitoring.log_level` to
   `get_logger("facade.token_optimizer", ...)`.
3. Add `self._metrics_enabled: bool = config.monitoring.metrics_enabled` after
   `self._metrics = get_metrics_collector()` in `facade.__init__`.
4. Update `facade.py:9-11` note: state what is now applied, and document
   `health_check_interval` as deferred (on-demand only, background scheduler
   is a future enhancement).
5. Add a test to `tests/` verifying that when `MonitoringConfig(log_level="WARNING")`
   is passed, the facade's logger is at WARNING level.
6. Run all gate scripts — must pass.

**Relevant Context:**
- `src/facade.py:9-11, 89-98` — the gap and where to wire
- `src/monitoring/logger.py:44-65` — StructuredLogger accepts log_level
- `src/monitoring/__init__.py` — get_logger factory
- `src/config/schema.py:70-81` — MonitoringConfig fields

**Status:** [x] closed — `log_level` passed to `LoggerFactory.get_logger()`; `metrics_enabled` stored as `_metrics_enabled` and gates facade metric recording; `health_check_interval` documented as deferred in facade docstring.

---

## Dimension C — Code Correctness (current: A → target: A+)

No confirmed defects. All known bugs (C1–C8, RLock) are fixed with behavioral
regression tests. TTL is enforced on-read. Thread safety is real (RLocks, not
asserted). No deserialization. The only residuals are accepted by design.

**The path to A+ is:** confirm the manifest-backed validation null test is still
passing and add a one-line note in the ARCHITECTURE.md §5 quality scenarios listing
the C-dimension baseline as verified.

### Sub-task C1 — Add quality scenario for correctness baseline to ARCHITECTURE.md

**Intent:**
The arc42 §8 quality scenarios in `docs/architecture/ARCHITECTURE.md` cover
performance and availability. They do not explicitly cite the C1–C8 correctness
baseline as a verifiable quality requirement with a test reference. Adding it makes
the correctness posture auditable by an external reviewer without reading test files.

**Expected Outcomes:**
- `docs/architecture/ARCHITECTURE.md §8` (quality scenarios) gains one scenario:
  "Correctness: all C1–C8 correctness bugs fixed; each has a behavioral regression
  test that fails on revert. Verified by `uv run pytest tests/ -k regression -v`."
- No code changes.

**Todo List:**
1. Read `docs/architecture/ARCHITECTURE.md §8` quality scenarios section.
2. Append one correctness quality scenario with the C1–C8 citation and the test command.
3. Run `python3 scripts/generate_api_docs.py --check` — docs-only change; must pass.

**Relevant Context:**
- `docs/architecture/ARCHITECTURE.md` — §8 quality scenarios
- `CHANGELOG.md` — C1–C8 fix record

**Status:** [x] closed — QS-5 row added to ARCHITECTURE.md §8 quality scenarios table citing C1–C8 and the regression test command.

---

## Dimension D — Testing & Verification (current: B− → target: A+)

**Gap D1:** Three wall-clock latency tests run in the default unit suite without
any marker. They assert `avg_latency_ms < 1.0` (ExactCache) and `< 100.0`
(SemanticCache, MultiLevelCache) using `time.time()` — a wall-clock measurement
that is flaky under CI load. `pytest-benchmark` is already in `pyproject.toml`
dependencies. The `slow` marker is already defined.

### Sub-task D1 — Quarantine wall-clock latency tests from the default suite

**Intent:**
The three tests each prove valid performance requirements (L1 < 1ms, L2 < 100ms).
The problem is not the assertions — it is that wall-clock tests live in the default
suite alongside unit tests. The fix is to mark them `@pytest.mark.slow` (already
defined in pyproject.toml) so they are excluded from the default `pytest` run
(`-m "not slow"` is the standard deselect pattern documented in pyproject.toml)
but still runnable explicitly. No test logic changes.

An alternative (stronger) fix is to convert them to `pytest-benchmark` fixtures,
which provides statistical stability. This is noted as an enhancement but not
required for A+.

**Expected Outcomes:**
- `tests/cache/test_exact_cache.py:262` decorated with `@pytest.mark.slow`.
- `tests/cache/test_semantic_cache.py:312` decorated with `@pytest.mark.slow`.
- `tests/cache/test_multi_level_cache.py:317` decorated with `@pytest.mark.slow`.
- The default `uv run pytest tests/ -q` run still passes all tests (the slow tests
  still run — they are marked, not skipped, unless `-m "not slow"` is passed).
- CI `pytest` step is either unaffected (tests still run) or the CI yml is updated
  to pass `-m "not slow"` in the unit test matrix step so flaky latency tests do
  not block PRs on slow runners.
- All gate scripts pass.

**Todo List:**
1. Read `tests/cache/test_exact_cache.py:260-280` to confirm exact method signature.
2. Read `tests/cache/test_semantic_cache.py:310-332` to confirm exact method signature.
3. Read `tests/cache/test_multi_level_cache.py:315-338` to confirm exact method signature.
4. Add `@pytest.mark.slow` decorator to all three methods.
5. Read `.github/workflows/ci.yml` test step to decide whether to add `-m "not slow"`
   to the CI pytest invocation (recommended for the matrix test job; keep slow tests
   in a dedicated job or in the benchmark job).
6. Run `uv run pytest tests/cache/ -q --tb=short` — must pass.
7. Run `uv run pytest tests/cache/ -m slow -v` — must show the three tests only.
8. Run all gate scripts — must pass.

**Relevant Context:**
- `tests/cache/test_exact_cache.py:262-279`
- `tests/cache/test_semantic_cache.py:312-329`
- `tests/cache/test_multi_level_cache.py:317-335`
- `pyproject.toml:84` — `slow` marker already defined
- `.github/workflows/ci.yml` — test matrix step

**Status:** [x] closed — `@pytest.mark.slow` already on all three wall-clock latency tests (`test_exact_cache.py:262`, `test_semantic_cache.py:312`, `test_multi_level_cache.py:317`).

---

## Dimension E — Build, Release & Supply-Chain (current: A → target: A+)

No defects. The supply chain is already at the institutional bar: locked deps,
matrix CI, 0 CVEs (pip-audit blocking), SAST (bandit medium+), SBOM (CycloneDX),
`uv lock --check` in CI.

**The path to A+:** confirm CI pins the test step to `uv sync --frozen` (not
`pip install -e .`) and add a `pip-audit --strict` step that fails if *any* new
CVE appears. Currently `pip-audit` blocks on existing CVEs in the lock file;
`--strict` would also catch advisory notes.

### Sub-task E1 — Harden pip-audit to --strict and confirm uv --frozen in CI

**Intent:**
`pip-audit` in CI currently uses default flags. Adding `--strict` means the build
fails if pip-audit itself encounters an error (e.g. package metadata unavailable)
rather than silently passing. This is the difference between "no CVEs today" and
"we will know immediately if the audit tooling can't run."

**Expected Outcomes:**
- `.github/workflows/ci.yml` pip-audit step gains `--strict` flag.
- `uv sync --frozen` (not `pip install`) is confirmed as the install step for the
  test matrix jobs (verify it is already the case; if not, correct it).
- All CI jobs pass with the updated flags.

**Todo List:**
1. Read `.github/workflows/ci.yml` pip-audit step (grep for `pip-audit`).
2. Read the install step for the test matrix to confirm `uv sync --frozen`.
3. Add `--strict` to the pip-audit invocation.
4. If any matrix step uses `pip install` instead of `uv sync --frozen`, correct it.
5. Commit; confirm CI passes.

**Relevant Context:**
- `.github/workflows/ci.yml` — pip-audit step, test matrix install steps

**Status:** [x] closed — `pip-audit --strict` and `uv sync --frozen` confirmed in `.github/workflows/ci.yml`.

---

## Dimension F — Documentation (current: A → target: A+)

No live stale claims. Diátaxis structure in place. API docs drift-checked.
Two authoritative arc42 documents. All 170+ files at standard.

**The path to A+:** one gap — `docs/tutorials/optimize-a-prompt.md` (the only
tutorial) lacks a "Prerequisites" section and does not link to the Python version
requirement. At A+ every tutorial has a self-contained prerequisites block so a
new user can determine suitability without reading multiple docs.

### Sub-task F1 — Add Prerequisites block to the tutorial

**Intent:**
`docs/tutorials/optimize-a-prompt.md` is the primary tutorial but starts with code
immediately. A Tier-1 tutorial always opens with: what you need installed, what
version, what prior knowledge. The prerequisite is minimal (Python 3.11+, uv or pip)
but its absence is the one gap between A and A+.

**Expected Outcomes:**
- Tutorial gains a "Prerequisites" section after the title/purpose block, before
  §1 Setup: Python ≥3.11, uv (recommended) or pip, the repo cloned. 3–5 lines.
- No other content changed.
- All gate scripts pass.

**Todo List:**
1. Read `docs/tutorials/optimize-a-prompt.md:1-40` to find the exact insertion point.
2. Insert a "## Prerequisites" section with: Python ≥3.11 (link to pyproject.toml),
   uv recommended (`pip install uv`), this repo cloned and installed.
3. Run `python3 scripts/generate_api_docs.py --check` — must pass (docs-only).

**Relevant Context:**
- `docs/tutorials/optimize-a-prompt.md`
- `pyproject.toml:9` — Python ≥3.11 (the single home)

**Status:** [x] closed — `## Prerequisites` section already present in `docs/tutorials/optimize-a-prompt.md` (Python ≥3.11, uv/pip, clone instructions).

---

## Dimension G — Governance & Compliance (current: A− → target: A+)

**Gap G1:** The TOCTOU check-then-use window is documented as residual-4 in
`THREAT_MODEL.md:158-179`. The named mitigation is "open the file descriptor
immediately after `resolve_within` and pass the `fd` rather than re-opening by
path." This mitigation eliminates the window entirely. At A+ the security posture
moves from "named residual" to "eliminated."

### Sub-task G1 — Eliminate the TOCTOU window in all three tool paths

**Intent:**
The classic mitigation for a TOCTOU window between validation and `open()` is to
merge them: `open()` the file immediately after `resolve_within()` returns the
validated path, then pass the open file handle down instead of the path. This
collapses the three-step pattern (resolve → exists → open) to two (resolve+open →
use) and eliminates the window. The three tools and the patterns:

- `src/tools/batch_file_reader.py:45-71`:
  `resolve_within` → `full_path.exists()` → `_read_full(full_path, ...)` → `open(file_path)`
  Fix: pass `full_path` to `_read_full`, open inside `_read_full` using the
  validated path (it already does this — `open(file_path, ...)` where
  `file_path: Path` IS `full_path`). Verify and add a regression test.

- `src/tools/component_analyzer.py:42-50` → `_analyze_file(file_path: Path, ...)`:
  The `file_path` passed to `_analyze_file` at line 120 comes from the
  `_contained_files()` rglob already filtered through `resolve_within`. Already safe.
  Add a regression test confirming this.

- `src/tools/kb_query.py:251-259`:
  Already opens `full_path` at line 259. Already safe.

Given personal code verification confirms `batch_file_reader` and `component_analyzer`
already use validated paths, the actual remaining TOCTOU gap is purely temporal
(resolve → exists check → open in separate syscalls). The `open()` calls already use
the validated `full_path`. The remaining window is: a symlink could be swapped between
`resolve_within()` and `open()`. The mitigation is to remove the `exists()` check
entirely (let `open()` raise `FileNotFoundError` and convert it to an error dict)
— this reduces the window to a single syscall.

**Expected Outcomes:**
- All three tools: the `full_path.exists()` check is replaced by a `try/except
  FileNotFoundError` around the `open()` call, collapsing the validate→exists→open
  three-step into validate→open two-step.
- `THREAT_MODEL.md` residual-4 updated: window narrowed from three-step to two-step;
  residual downgraded from accepted-open to accepted-minimal.
- Regression tests added for each tool confirming the new pattern.
- All gate scripts pass.

**Todo List:**
1. Read `src/tools/batch_file_reader.py:38-75` fully.
2. Read `src/tools/component_analyzer.py:38-60` fully.
3. Read `src/tools/kb_query.py:245-265` fully.
4. In each tool: replace `if not full_path.exists(): return {"error": "File not found"}`
   with a `try/except (FileNotFoundError, OSError)` wrapping the `open()` call,
   returning the same error dict on exception.
5. Update `docs/security/THREAT_MODEL.md` residual-4: note the window is now
   two-step (resolve → open); the TOCTOU window cannot be fully eliminated without
   `O_NOFOLLOW` semantics, but swapping a valid path between resolve and open now
   requires replacing the target within a single syscall context — a significantly
   higher bar than the prior three-step window.
6. Add regression tests: `tests/tools/test_batch_file_reader.py` and
   `tests/tools/test_kb_query.py` — confirm that a file deleted after resolution
   but before open returns the expected error dict (not an unhandled exception).
7. Run all gate scripts — must pass.
8. Run `uv run pytest tests/tools/ -q --tb=short` — must pass.

**Relevant Context:**
- `src/tools/batch_file_reader.py:45-75`
- `src/tools/component_analyzer.py:38-60`
- `src/tools/kb_query.py:245-265`
- `docs/security/THREAT_MODEL.md:158-179` — residual-4 to update

**Status:** [x] closed — TOCTOU 3-step→2-step narrowed in all three tools; `THREAT_MODEL.md` residual-4 updated; regression tests added.

---

## Execution Order

Sub-tasks are independent within dimensions. Recommended order:

```
A1  → trivial (3 lines deleted)
D1  → trivial (3 markers added)
E1  → trivial (1 flag added to CI)
F1  → trivial (5 lines added)
C1  → trivial (1 paragraph added to arch doc)
B1  → moderate (ExactCache + MultiLevelCache wiring + test)
B2  → moderate (facade wiring for log_level + metrics_enabled)
G1  → moderate (3 tools: replace exists() with try/except + tests + threat model)
```

Trivial tasks (A1, D1, E1, F1, C1) in one commit.
Code tasks (B1, B2, G1) each in their own commit.

---

## Expected grade after all sub-tasks complete

| Dim | Current | After |
|:---:|:-------:|:-----:|
| A | A (3.9) | **A+** |
| B | B+ (3.3) | **A** → **A+** after B1+B2 |
| C | A (3.95) | **A+** |
| D | B− (2.5) | **A** → **A+** after D1 |
| E | A (4.0) | **A+** |
| F | A (4.0) | **A+** |
| G | A− (3.7) | **A** → **A+** after G1 |

**Projected overall: A+ (≥ 4.1 / 4.0)**
