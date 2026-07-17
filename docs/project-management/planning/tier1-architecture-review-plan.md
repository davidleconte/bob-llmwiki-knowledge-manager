# Tier-1 Architecture Review — Full Project
## Institutional Top-Tier Software Vendor Excellence Standards

**Review date:** 2026-07-16  
**Branch:** `fix-multilevel-cache-race`  
**Standard:** ISO/IEC 25010 · OpenSSF Scorecard / SLSA · arc42 + ADR + Diátaxis · Keep-a-Changelog / SemVer · CHAOSS  
**Framework:** 7-dimension MECE scorecard (same as institutional audit 2026-07-13 and adversarial re-audit 2026-07-14)  
**Basis:** Evidence-grounded against actual code, CI config, scripts, and three prior audit records

> **IMPORTANT — Re-verification note (2026-07-16):** Every finding in the Phase-8
> adversarial audit (2026-07-14) was re-checked against the _current_ code on
> this branch before being included below. Several of the Phase-8 "Path to GO"
> items have already been closed by the gap-closure work that followed. Only
> findings confirmed as still open in the current codebase appear in the
> sub-tasks below. Closed items are documented in the "Verified Closed" section
> of each dimension for the record.

---

## How to read this document

Each dimension section contains:
- **Current grade** — estimated from evidence; Phase-8 score + confirmed gap-closure delta
- **Verified Closed** — Phase-8 gaps confirmed closed in current code (do not re-open)
- **Remaining Gaps** — defects confirmed still open with exact `file:line` citations
- **Sub-Tasks** — ordered remediation steps (self-contained, one at a time)
- **Acceptance Criteria** — the observable bar for A/A+ on that dimension

All sub-tasks must leave the full CI gate suite **green** after they are applied.

---

## MECE Scorecard — Current Estimated State

| # | Dimension | Weight | Est. Grade | Target | Remaining work |
|---|-----------|:---:|:---:|:---:|---|
| A | Product Integrity & Claims | 20% | **A** | A+ | README overclaim (minor) |
| B | Architecture & Design | 15% | **A** | A+ | Disjoint-cache undocumented; no truncation ADR |
| C | Code Correctness & Reliability | 20% | **A** | A+ | All verified bugs already fixed ✓ |
| D | Testing & Verification | 15% | **A** | A+ | Wall-clock timing assertions in 3 test files |
| E | Build / Supply-Chain | 12% | **A** | A+ | `evaluation/requirements.txt` second unpinned manifest |
| F | Documentation | 10% | **A** | A+ | AGENTS.md floor value; stale test count; broken clone URL |
| G | Governance & Compliance | 8% | **A** | A+ | TOCTOU unnamed in threat model |

**Estimated weighted grade: ≈ A (4.0+ / 4.3).**
Remaining gaps are all documentation and minor hygiene — no re-architecture, no code correctness issues.

---

## Cross-Cutting Validation Gates

Run this full suite before marking any sub-task `[x] done`:

```bash
ruff check src/ tests/ scripts/
ruff format --check src/ tests/ scripts/
mypy src/
uv run pytest tests/ -q --tb=short --cov=src --cov-report=term-missing
python3 scripts/check_coverage_by_package.py coverage.json
python3 scripts/check_status_consistency.py
python3 scripts/check_savings_claims.py
python3 scripts/check_value_homes.py
python3 scripts/check_layering.py
python3 scripts/check_community_health.py
python3 scripts/generate_api_docs.py --check
bandit -r src/ -ll
```

---

## Dimension A — Product Integrity & Claims Substantiation

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **A-GAP-1 CLOSED:** `check_savings_claims.py` is now **tree-wide**, not a 5-file
  allowlist. It scans all `docs/**/*.md`, top-level status docs, and all `src/**/*.py`.
  The banner exception preserves frozen planning and audit-trail docs verbatim.
  The self-test (`--selftest`) verifies detector correctness.
- Fabricated "68.96% / 89.3% / 91.80%" figures: all live doc surfaces are either
  retracted, bannered, or excluded as frozen dated records.
- `evaluation/VALIDATION_DISCLAIMER.md` present and honest.
- Null test (≈0% on shuffled text) passes; three mechanisms reported separately.

### Remaining Gap

**A-GAP-2 (Low):** `README.md §5` frames a "Proof point" that links a "Full
transcript." `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md:8` explicitly states the full
transcript does not exist. A minor overclaim at the A/A+ margin.

### Sub-Task A1 — Remove or qualify the "Full transcript" link in README

**Intent:** At A+ standard, every link points to something real or is removed.
The Proof Point section's measured ~20% headline already demonstrates the
optimizer's value with full provenance. The anecdotal transcript reference weakens
the section.

**Expected Outcomes:**
- `README.md` no longer references a non-existent "Full transcript."
- The Proof Point section either links directly to `LIVE_EXAMPLE_HCD_ANALYSIS.md`
  (with a note that it is an illustrative analysis, not a verbatim transcript) or
  the transcript link is removed.
- `check_savings_claims.py` passes (the change does not affect any manifest-backed
  number).
- All other gates pass unchanged.

**Todo List:**
1. Read `README.md:105-130` to identify the exact "Proof point" paragraph and
   transcript link.
2. Remove the transcript link or replace with a direct link to
   `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md` with the note: "(illustrative
   analysis, not a verbatim transcript)".
3. Run: `python3 scripts/check_savings_claims.py && uv run pytest tests/ -q`.

**Relevant Context:**
- `README.md:109-124` — Proof Point section
- `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md:8` — "no full transcript" statement

**Status:** [x] done

---

## Dimension B — Architecture & Design

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **B-GAP (layering) CLOSED:** `src/ → scripts/` imports blocked by AST-based
  `check_layering.py`; verified by gate-slip test.
- **B-GAP (pricing single home) CLOSED:** `src/pricing.py` is the single home for
  model rates; enforced by `check_value_homes.py`.
- **B-GAP (OptimizerConfig.strategies dead field) CLOSED:** `strategies` parameter
  is now wired through `PromptOptimizer.__init__`, `from_config()`, and
  `build_optimizer()` (gap-closure plan sub-task B1).
- **B-GAP (MonitoringConfig fields not applied) CLOSED:** `log_level`, `metrics_enabled`,
  `health_check_interval` are now applied via the facade (gap-closure plan sub-task B2).
- **B-GAP (CacheConfig.version_support_enabled not wired) CLOSED:** `build_cache()`
  now passes `version_support_enabled` and `max_versions` to `ExactCache` and
  `MultiLevelCache` (gap-closure plan sub-task B1).
- Facade (`TokenOptimizer`) is a thin delegator — no business logic; confirmed
  god-object free.

### Remaining Gaps

**B-GAP-1 (Medium):** The facade exposes `self.cache` (a `MultiLevelCache`) but the
`optimize()` path uses `self.optimizer.cache` — a **disjoint** `ExactCache` object.
The `CacheConfig.l2_*` fields (L2 threshold, L2 size) have **no effect on prompt
optimization**; they only affect KB/query use-cases. This is the correct design
(documented in `ARCHITECTURE.md §5` — L2 must not return semantically-similar-but-
different prompt text), but the **facade docstring still says "composes cache from
ConfigSchema"** without disclosing the disjoint-object consequence. A reader who
sets `config.cache.l2_similarity_threshold = 0.9` will reasonably expect it to
affect `optimize()` — it does not.

**B-GAP-2 (Low):** `Truncator` has no corresponding `TruncationConfig` section in
`ConfigSchema` — it is hard-wired with defaults in `build_truncator()`. The factory
comment acknowledges this ("truncation has no config section yet") but no ADR
captures the deliberate decision and its safety rationale.

### Sub-Task B1 — Document the disjoint-cache design explicitly in the facade and architecture doc

**Intent:** The L2-scoping decision (L2 never used in `optimize()`) is correct and
already documented in `ARCHITECTURE.md §5`. The gap is that the facade attribute
docstring and the config table in `ARCHITECTURE.md §4` do not make the
disjoint-object consequence visible at a glance. Close the gap with targeted
documentation — no code changes required.

**Expected Outcomes:**
- `src/facade.py` docstring for the `cache` attribute (or property) explicitly
  states: "This `MultiLevelCache` is available for KB/query use-cases. `optimize()`
  uses a separate `ExactCache` instance (`self.optimizer.cache`) and is unaffected
  by `CacheConfig.l2_*` settings — see ARCHITECTURE.md §5 (L2-scoping)."
- `docs/architecture/ARCHITECTURE.md §4` config table adds a "Scope" footnote to
  the `l2_similarity_threshold` and `l2_max_size` rows: "KB/query path only; does
  not affect `optimize()`."
- `generate_api_docs.py --check` continues to pass (docstring change is in-scope
  for the API doc freshness gate).
- All other gates pass unchanged.

**Todo List:**
1. Read `src/facade.py` — find the `cache` attribute / property and its current
   docstring.
2. Add the one-sentence disclosure to the `cache` docstring.
3. Read `docs/architecture/ARCHITECTURE.md:126-137` — the §4 config table.
4. Add a "KB/query only" footnote to the `l2_*` rows.
5. Run: `python3 scripts/generate_api_docs.py --check && uv run pytest tests/ -q`.

**Relevant Context:**
- `src/facade.py` — `TokenOptimizer.cache` attribute
- `docs/architecture/ARCHITECTURE.md:126-154` — §4 config table + §5 component notes
- `docs/adr/002-caching-strategy.md` — L2 exclusion rationale (cross-reference only)

**Status:** [x] done

---

**Sub-Task B2 — Record the TruncationConfig-absent decision as ADR-016**

**Intent:** `build_truncator()` in `src/factory.py` deliberately hardwires
truncation defaults without a corresponding `TruncationConfig` section. Truncation
is lossy; configuration increases risk of mis-tuning without safety gates (unlike
the optimizer's `min_quality_score` gate). This is a sound architectural decision
that should be captured so future maintainers do not add a config section without
understanding the tradeoff.

**Expected Outcomes:**
- `docs/adr/016-truncation-no-config.md` exists, following the established ADR
  template (Context / Decision / Consequences / Status: Accepted).
- `docs/adr/README.md` updated with the ADR-016 entry.
- `generate_api_docs.py --check` and `check_community_health.py` pass (new doc
  in the curated tree).

**Todo List:**
1. Read `src/factory.py:60-80` — confirm the hardwired truncation defaults.
2. Read `docs/adr/013-facade-factory-pattern.md` — use as template for the new ADR.
3. Write `docs/adr/016-truncation-no-config.md` (Context: lossy truncation risk from
   mis-tuning; Decision: no TruncationConfig, defaults in factory; Consequences:
   simpler, prevents accidental misconfiguration, but requires a code change to tune;
   Status: Accepted).
4. Append ADR-016 entry to `docs/adr/README.md`.
5. Run gate scripts.

**Relevant Context:**
- `src/factory.py` — `build_truncator()` implementation
- `docs/adr/013-facade-factory-pattern.md` — ADR template pattern
- `docs/adr/README.md` — ADR index

**Status:** [x] done

---

## Dimension C — Code Correctness & Reliability

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
All Phase-8 correctness gaps are confirmed fixed in the current codebase:

- **C-GAP-1 (versioned-key collision) CLOSED:** `src/cache/base.py:13-25` defines
  `escape_version()` which percent-encodes `:` → `%3A` and `%` → `%25`. Both
  `ExactCache._make_versioned_key()` (line 146) and `SemanticCache` call it,
  making `(version, key)` encoding injective. The Phase-8 bug
  (`f"{version}:{key}"` without escaping) is gone.
- **C-GAP-2 (`load_from_env` skips validation) CLOSED:** `manager.py:168-179`
  now builds a candidate config via `_compute_merge()`, validates it with
  `_validator.validate(candidate)`, and only then commits — same contract as
  `load_from_file()` and `update()`.
- **C-GAP-3/4 (lockless singletons / ExactCache.get race) CLOSED:**
  `metrics.py:420-438` uses double-checked locking (`_collector_init_lock`).
  `ExactCache.get()` is decorated with `@_synchronized` (line 159), which acquires
  `self._lock` (an `RLock`) before every dict-touching method.
- **C1–C7 + RLock deadlock** — all fixed; each guarded by a behavioral regression
  test (C1 and C5 adversarially revert-tested).

### Remaining Gaps

**None confirmed open.** Dimension C is effectively at A/A+ on correctness.

> If new bugs are found during this remediation cycle, add sub-tasks here following
> the pattern: Intent → Expected Outcomes → Todo List → Relevant Context → Status.

---

## Dimension D — Testing & Verification

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **D-GAP (circular target-savings test) CLOSED:** The old `test_prompt_optimizer.py`
  circular test is retired; replaced with behavioral regression tests.
- **D-GAP (split-brain pytest.ini vs pyproject) CLOSED:** Single `pyproject.toml`
  config, no separate `pytest.ini`.
- **D-GAP (no `--cov-fail-under`) CLOSED:** `fail_under = 80` in
  `[tool.coverage.report]`; per-package floors in `check_coverage_by_package.py`.
- **D-GAP (src/tools/ excluded from gated denominator) CLOSED:** `src/tools/` is
  now in the gated denominator with an 85% per-package floor.

### Remaining Gap

**D-GAP-1 (Medium):** Wall-clock timing assertions without time abstraction remain
in three test files. `tests/README.md:90` acknowledges these as a known flakiness
source. On a slow CI runner or under load, these assertions produce false failures
unrelated to code correctness:
- `tests/cache/test_multi_level_cache.py:388` — `l1_time < l2_time`
- `tests/cache/test_exact_cache.py:279` — `< 1.0 ms`
- `tests/delegation/test_coordinator.py:308` — `< 0.05 s`

### Sub-Task D1 — Replace wall-clock timing assertions with functional assertions

**Intent:** Unit tests should assert behavior, not timing. Latency validation
belongs in the benchmark suite (which already has a 25% regression threshold and
saved baseline). Removing timing assertions eliminates the primary flakiness source
reported in `tests/README.md:90`.

**Expected Outcomes:**
- The three test locations no longer contain `< X ms` / `< X s` wall-clock assertions.
- The behaviors they were testing (L1 faster than L2, cache lookup succeeds, parallel
  dispatch completes) are preserved via functional assertions (e.g., "L1 returns the
  stored value," "L2 miss returns None," "all tasks complete without error").
- The benchmark suite (`tests/performance/`) retains the latency targets.
- `tests/README.md:90` flakiness note is removed or updated to reflect the fix.
- All gates pass.

**Todo List:**
1. Read `tests/cache/test_multi_level_cache.py:380-395` in full — identify the
   timing assertion and what behavior it was testing beyond timing.
2. Read `tests/cache/test_exact_cache.py:270-285` in full — same.
3. Read `tests/delegation/test_coordinator.py:300-315` in full — same.
4. For each: replace the `assert elapsed < X` with a functional assertion that
   captures the same correctness property (e.g., that L1 hits, that the cache
   returns the right value, that parallel tasks all complete).
5. Update `tests/README.md:90` to reflect the fix.
6. Run: `uv run pytest tests/cache/ tests/delegation/ -q --tb=short`.

**Relevant Context:**
- `tests/cache/test_multi_level_cache.py:388` — L1 vs L2 timing assertion
- `tests/cache/test_exact_cache.py:279` — sub-millisecond assertion
- `tests/delegation/test_coordinator.py:308` — coordinator timing assertion
- `tests/README.md:90` — acknowledged flakiness note
- `tests/performance/` — where latency targets belong

**Status:** [x] done

---

## Dimension E — Build, Release & Supply-Chain

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **E-GAP-1 (CI installs on `>=` floors) CLOSED:** All package-consuming CI jobs
  (`test`, `typecheck`, `e2e`, `validation`, `benchmarks`) use
  `uv sync --frozen --extra dev --extra monitoring`. The `sbom` job intentionally
  uses `pip install` for `cyclonedx-bom`/`pip-audit`/`uv` which are not in the
  project's `uv.lock` — that is correct.
- **E-GAP-2 (`pip-audit` non-blocking) CLOSED:** `ci.yml:237-242` runs
  `pip-audit --requirement requirements.lock.txt --strict` with no
  `continue-on-error`. The comment at line 237 confirms "Was `continue-on-error`
  in Phase 3; … now a blocking gate."
- `uv.lock` in-sync verification (`uv lock --check`) in the `sbom` job.
- CycloneDX SBOM artifact per build.
- Dependabot configured.

### Remaining Gap

**E-GAP-3 (Low):** `evaluation/requirements.txt` is a second, unpinned dependency
manifest outside the `uv.lock` / `pyproject.toml` single-home discipline. It
carries a clear comment explaining it is analysis-only tooling, not installed by CI
or the test suite — which is the right framing. The gap is that it is unpinned
(uses `>=` floors) and un-audited by `pip-audit`.

**My recommendation (addressing your question 2):**

The `evaluation/requirements.txt` is genuinely analysis-only — used only for
running the adversarial review scripts under `evaluation/`, never by the package,
CI, or tests. Two options:

**Option A — Leave as-is, add a pinned lockfile alongside it (minimal).**  
Add `evaluation/requirements.lock.txt` generated from it (`pip-compile` or
`uv pip compile`) and optionally add a separate `pip-audit` step in the `sbom` job
scoped to this file. Pros: zero risk to the package install chain; evaluation/
stays self-contained. Cons: a second lockfile to maintain. **This is the right
choice.** Moving analysis deps into `pyproject.toml` is a false economy — it
pollutes the package's published optional-dependency surface for something that
only affects ad-hoc analysis runs.

**Option B — Move to `pyproject.toml [project.optional-dependencies].evaluation`.**  
Cleaner in theory, but it exposes `pandas`/`scipy`/`matplotlib`/`seaborn` as
published optional extras, which any `pip install bob-llmwiki-knowledge-manager[evaluation]`
user would receive. These packages are 40–80 MB each. For a token-optimization
library, that is inappropriate bloat on the published surface.

**Recommendation: Option A.** Pin `evaluation/requirements.txt` to exact versions
via a companion `evaluation/requirements.lock.txt`, audit it in the `sbom` job, and
leave `pyproject.toml` untouched.

### Sub-Task E1 — Pin evaluation dependencies and audit them in CI

**Intent:** Close the second-manifest gap by adding a pinned lockfile for the
evaluation tooling and auditing it in CI — without polluting the package's
published dependency surface.

**Expected Outcomes:**
- `evaluation/requirements.lock.txt` exists with exact-version pins for
  `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn` (generated via
  `uv pip compile evaluation/requirements.txt -o evaluation/requirements.lock.txt`).
- `evaluation/requirements.txt` header comment updated to reference the lockfile.
- The `sbom` CI job gains an optional `pip-audit --requirement evaluation/requirements.lock.txt`
  step (can be `continue-on-error: true` initially since these are analysis-only deps,
  but it at least produces a visible audit result).
- `pyproject.toml` is unchanged.
- All gates pass.

**Todo List:**
1. Run: `uv pip compile evaluation/requirements.txt --universal -o evaluation/requirements.lock.txt`
   to generate the pinned lockfile.
2. Update the comment block in `evaluation/requirements.txt` to reference the lockfile
   and its purpose.
3. Add a `pip-audit --requirement evaluation/requirements.lock.txt` step to the `sbom`
   job in `.github/workflows/ci.yml` (after the existing project-deps audit step).
4. Run: `python3 scripts/check_savings_claims.py && uv run pytest tests/ -q`.

**Relevant Context:**
- `evaluation/requirements.txt` — current unpinned manifest
- `.github/workflows/ci.yml:209-242` — `sbom` job
- `pyproject.toml:[project.optional-dependencies]` — do NOT add evaluation deps here

**Status:** [x] done

---

## Dimension F — Documentation & Knowledge Architecture

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **F-GAP (no authoritative architecture doc) CLOSED:** `docs/architecture/ARCHITECTURE.md`
  is the single authoritative architecture doc; both deprecated predecessors carry
  on-file banners.
- **F-GAP (no Diátaxis index) CLOSED:** `docs/INDEX.md` is organized by Diátaxis
  categories (Tutorials, How-To, Reference, Explanation).
- **F-GAP (API docs not drift-checked) CLOSED:** `generate_api_docs.py --check` runs
  in CI; 41 files in sync.
- **F-GAP (status consistency not enforced) CLOSED:** `check_status_consistency.py`
  enforces STATUS / README / AGENTS agreement.

### Remaining Gaps

**F-GAP-1 (Medium):** `AGENTS.md` contains two contradictory delegation coverage
floor values. Line 46 reads "Held at a 52% per-package coverage floor (measured
~53%…)" — that is correct. The Phase-8 audit flagged `AGENTS.md:44` citing "~54%
floor" — re-reading the current file at line 46, the text says 52% correctly.
**The specific `:44` contradiction may already be fixed.** Needs a fresh read of
lines 40–55 against `check_coverage_by_package.py` to confirm.

**F-GAP-2 (Low):** `STATUS.md` cites "683 passed" which is stale vs. the actual
897 (current test suite). The file's own disclaimer says it is a point-in-time
snapshot, but the gap is visible and erodes trust.

**F-GAP-3 (Low):** `INSTALLATION.md:18` may contain a broken
`git clone github.com/yourusername/...` placeholder. `pyproject.toml:urls.repository`
was corrected to the real URL but this file may not have been updated.

### Sub-Task F1 — Verify AGENTS.md floor value and fix if still wrong; add consistency guard

**Intent:** Confirm whether the `AGENTS.md` contradiction is already closed or still
present. If still wrong, correct it and add a CI guard so the value cannot drift
again without CI catching it.

**Expected Outcomes:**
- `AGENTS.md` cites the delegation floor exactly once and consistently
  as "52% per-package floor (measured ~53%)" — matching
  `check_coverage_by_package.py`.
- If any contradiction is found, `check_status_consistency.py` (or a new
  `check_agents_consistency.py`) extracts the floor value from `AGENTS.md` and
  compares it to the floor registered in `check_coverage_by_package.py`, failing
  on mismatch.
- All gates pass.

**Todo List:**
1. Read `AGENTS.md:40-55` in full — verify the exact current floor value.
2. If any contradiction exists, correct the wrong value to "52% per-package floor
   (measured ~53%)".
3. Grep `AGENTS.md` for all floor/percentage references to the delegation package
   to ensure there are no remaining inconsistencies.
4. Add a regex-based consistency check in `scripts/check_status_consistency.py`
   that extracts the delegation floor from `AGENTS.md` and compares it to the
   `DELEGATION` entry in `check_coverage_by_package.py`.
5. Run gate scripts.

**Relevant Context:**
- `AGENTS.md:40-55` — delegation description block
- `scripts/check_coverage_by_package.py` — authoritative floor source
- `scripts/check_status_consistency.py` — existing consistency checker pattern

**Status:** [x] done

---

**Sub-Task F2 — Update stale test count in STATUS.md and fix INSTALLATION.md clone URL**

**Intent:** Two low-risk factual accuracy fixes that are visible to anyone reading
the canonical status and installation docs.

**Expected Outcomes:**
- `STATUS.md` reflects the current test count (897 passed, 23 skipped), matching
  `tests/README.md`'s headline.
- `INSTALLATION.md:18` contains the actual repository URL
  (`https://github.com/davidleconte/bob-llmwiki-knowledge-manager`) from
  `pyproject.toml:urls.Repository`.
- `check_status_consistency.py` updated to add a test-count cross-check between
  `STATUS.md` and `tests/README.md` so this cannot silently drift again.
- All gates pass.

**Todo List:**
1. Read `STATUS.md:21-25` to locate the stale count.
2. Read `tests/README.md:1-10` to confirm the authoritative count.
3. Update `STATUS.md` to match.
4. Read `INSTALLATION.md:15-25` — find the placeholder clone URL.
5. Replace with the real URL from `pyproject.toml:urls.Repository`.
6. Add a cross-check to `scripts/check_status_consistency.py` (extract test count
   from `STATUS.md` and `tests/README.md`; fail if they differ).
7. Run gate scripts.

**Relevant Context:**
- `STATUS.md:21-25` — stale test count
- `tests/README.md:1-10` — authoritative test count
- `INSTALLATION.md:18` — potentially broken clone URL
- `pyproject.toml:54-57` — correct repository URLs

**Status:** [x] done

---

## Dimension G — Project Governance & Compliance

### Current Grade: A → Target: A+

### Verified Closed (do not re-open)
- **G-GAP-1 (delegation path traversal) CLOSED:** `documentation_agent.py:46-64`
  already routes `task.target` through `resolve_within(Path.cwd(), target)` with a
  `try/except ValueError` that returns a `FAILED` result for escape attempts.
  The THREAT_MODEL claim about delegation containment is now accurate.
- **`resolve_within` correctness CONFIRMED:** The Phase-8 probe tested absolute
  paths, `../`, dir-symlink, file-symlink, sibling-prefix, and mid-path `..` —
  all rejected; legitimate paths allowed. Uses correct resolve-then-check order.
- 12-artifact community-health set present and non-stub (gate-slip verified each
  file's deletion fails CI).
- ADR-012 fabricated security stack retracted with banner + superseded by
  `docs/security/THREAT_MODEL.md`.
- STRIDE analysis covers all 6 categories with defensible N/A calls for local CLI.

### Remaining Gap

**G-GAP-2 (Low):** The TOCTOU (time-of-check-time-of-use) window in
`resolve_within` — the gap between `.resolve()` (which canonicalizes symlinks) and
the subsequent `open()` call — is unnamed in `THREAT_MODEL.md`'s residual register.
For a single-user local CLI this is an accepted negligible risk. The model currently
claims exhaustiveness; adding this as a named accepted residual completes that claim.

### Sub-Task G1 — Add the TOCTOU residual to the threat model's residual register

**Intent:** `resolve_within` resolves then checks (correct order: symlinks are
canonicalized before the boundary check). However, between resolution and `open()`,
a symlink swap could theoretically redirect the path. For a local single-user CLI
this is negligible — an attacker would need to be on the same machine with
filesystem write access. The threat model claims to be exhaustive; naming this
accepted residual completes that claim without code changes.

**Expected Outcomes:**
- `docs/security/THREAT_MODEL.md` residual register contains a "TOCTOU:
  resolve-then-open" entry with:
  - Severity: Negligible
  - Condition: Attacker has filesystem write access on the same machine
  - Disposition: Accepted — local CLI, operator-privilege, single-user; a symlink
    swap attack requires equivalent access level to the operator
  - Mitigation note: The `resolve_within` check canonicalizes symlinks correctly;
    the window is the file open only
- No code changes needed.
- All gates pass.

**Todo List:**
1. Read `docs/security/THREAT_MODEL.md` to locate the residual register section.
2. Add the TOCTOU entry following the existing residual format.
3. Run: `python3 scripts/check_community_health.py && uv run pytest tests/ -q`.

**Relevant Context:**
- `docs/security/THREAT_MODEL.md` — STRIDE analysis and residual register
- `src/tools/safe_paths.py` — `resolve_within()` implementation

**Status:** [x] done

---

## Execution Order (Recommended)

Ordered to minimize inter-task dependencies and keep CI green throughout:

| # | Sub-Task | Dimension | Risk | Touches code? |
|---|----------|-----------|------|---------------|
| 1 | D1 — Remove wall-clock timing assertions | D | Low | Yes (tests only) |
| 2 | A1 — Fix README "Full transcript" overclaim | A | Minimal | No (docs only) |
| 3 | B1 — Document disjoint-cache design | B | Minimal | Docstring + arch doc |
| 4 | B2 — ADR-016 for truncation-no-config | B | Zero | New doc only |
| 5 | E1 — Pin evaluation deps + CI audit | E | Low | CI + lockfile |
| 6 | F1 — Verify/fix AGENTS.md floor + CI guard | F | Low | Doc + script |
| 7 | F2 — Update stale counts + clone URL | F | Minimal | Docs only |
| 8 | G1 — Add TOCTOU residual to threat model | G | Zero | Doc only |

---

## Sign-Off Criteria

The review is complete and all dimensions reach A/A+ when:

- [ ] All 8 sub-tasks are marked `[x] done`
- [ ] Full CI gate suite passes clean (0 failures, 0 new warnings)
- [ ] `pytest --cov=src` reports ≥ 80% global coverage (≥87% expected)
- [ ] `check_savings_claims.py` tree-wide scan passes
- [ ] `check_status_consistency.py` passes (including new test-count guard added in F2)
- [ ] `THREAT_MODEL.md` residual register is complete (TOCTOU entry added in G1)
- [ ] `AGENTS.md` floor value consistent with `check_coverage_by_package.py` (F1)
- [ ] `docs/architecture/ARCHITECTURE.md §4` config table clarifies L2 scope (B1)
- [ ] `docs/adr/016-truncation-no-config.md` exists and is indexed in `docs/adr/README.md` (B2)
- [ ] Adversarial spot-check: revert C1/C5 fixes → regression tests go red ✓ (already confirmed, preserve)
- [ ] Adversarial spot-check: probe `resolve_within` with path-traversal → all rejected ✓ (already confirmed, preserve)

At that point the weighted grade is expected to reach **A/A+ on all seven
dimensions**, meeting the institutional Tier-1 sign-off bar.

---

## What Is Already at A/A+ Standard (Do Not Change)

The following are verified and must be **preserved** through the remediation:

- Real validation harness with 11-field manifest; null test passes; three savings
  mechanisms measured and reported separately
- All 8 behavioral regression tests for C1–C7 + RLock (revert-tested for C1/C5)
- `resolve_within` path-traversal containment (tested against 5 escape vectors)
- Double-checked locking on all singletons; `@_synchronized` on all dict operations
- `uv sync --frozen` in all CI package jobs; `pip-audit --strict` blocking gate;
  0 CVEs in locked closure
- Tree-wide `check_savings_claims.py` with banner exception; `--selftest` mode
- `escape_version()` injective encoding preventing versioned-key collisions
- `load_from_env()` validates before committing (same contract as `load_from_file()`)
- 7 CI jobs, 8 lint gates, all real enforcement (gate-slip verified)
- 12-artifact community health set; CODEOWNERS; STRIDE threat model
