---
title: Phase 8 — Independent Adversarial Re-Audit & Sign-Off (2026-07-14)
category: research
status: active
tags: [audit, sign-off, phase-8, adversarial, mece, scorecard, production-readiness, go-no-go]
created: 2026-07-14
updated: 2026-07-14
audit_date: 2026-07-14
audit_method: Independent adversarial re-audit — orchestrator firsthand verification (full suite, all gates, revert-a-fix, path-traversal probe, clean CVE closure) + 10 refute-by-default subagents (7 MECE dimensions + gate-slip in an isolated worktree + fresh-eyes bug hunt + internal-consistency)
audit_standard: ISO/IEC 25010 · OpenSSF Scorecard / SLSA · arc42+ADR+Diátaxis · Keep-a-Changelog/SemVer · CHAOSS
audit_scope: analysis only — repository unchanged by this audit; all mutation experiments reverted (git-verified clean)
supersedes_context: verifies (does not replace) audit-2026-07-13-institutional.md and comprehensive-issue-list-2026-07-13.md
target_grade: "A+ on every dimension (audit-2026-07-13-institutional.md:190)"
signoff_decision: "NO-GO (A+ sign-off bar) — remediation is real and large (D- → B+/A-), but two dimensions remain below A and no dimension reached A+"
frozen: true
---

# Phase 8 — Independent Adversarial Re-Audit & Sign-Off

> **This is a frozen point-in-time snapshot (2026-07-14). Do not edit.** It is the audit's own final step (`audit-2026-07-13-institutional.md:190`: "independent adversarial re-audit; each dimension A/A+"). Every "fixed / done / measured / retracted" claim below was treated as a hypothesis to falsify with `path:line` or a command repro — nothing was accepted because a doc, changelog, or prior session said so.

## SIGN-OFF DECISION: **NO-GO** (against "A/A+ on every dimension")

The remediation is **real, substantial, and largely honest** — the weighted grade moved from **≈ D‑ (0.9)** to **≈ B+/A‑ (3.46 / 4.3)**, a ~+2.6 GPA jump earned with genuine engineering, not repainting. Nine of the original ten "Critical/High" defect families are closed with behavioral regression tests I confirmed go **red** when the fix is reverted.

It is **not** an A+ sign-off, for one decisive reason and several supporting ones:

- **The exact fabrication this whole phase existed to eliminate still ships, unretracted, on ~12+ genuinely-live documentation surfaces.** `docs/BOOK_CHAPTER_07.md:180` presents "**Results: 68.96% Savings**" complete with a *fabricated* "Mean 68.96% / Median 67.5% / Std 8.2%" **and the explicitly-banned mechanism re-blend** (cache 40% + optimization 9% + truncation 12% + "~8% compound"); `docs/adr/011-monitoring-observability.md:713` asserts "✅ Tracked 89.3% token savings"; the current how-to guide `docs/knowledge-base/guides/setup-token-optimization.md:4` still promises "reduce token costs by up to **89.3%**." None carry a retraction banner. This is a **Critical claims-integrity residual** in the 20%-weighted dimension whose entire purpose is claims substantiation.
- **The 84.4% coverage headline is load-bearing on excluding a barely-tested third of the package.** Re-measured with `src/tools/` in the denominator, real coverage is **74.9%** — *below the project's own 80% gate* — and the excluded code includes the untrusted-path handlers (`kb_query.py` 18.9%, `batch_file_reader.py` 20.4%).

A NO-GO with a tight, honest gap list is the correct Phase-8 outcome here. The blockers are concentrated and addressable (see [Path to GO](#path-to-go-what-would-flip-this-to-a-sign-off)); none require re-architecture.

---

## Re-Graded MECE Scorecard

| # | Dimension | Weight | Original (07-13) | **Re-grade (07-14)** | Δ |
|---|-----------|:---:|:---:|:---:|:---:|
| A | Product Integrity & Claims Substantiation | 20% | F | **B** | ▲▲▲ |
| B | Architecture & Design | 15% | D | **A‑** | ▲▲▲ |
| C | Code Correctness & Reliability | 20% | D | **A‑** | ▲▲▲ |
| D | Testing & Verification | 15% | C‑ | **B** | ▲▲ |
| E | Build, Release & Supply-Chain | 12% | F | **A‑** | ▲▲▲▲ |
| F | Documentation & Knowledge Architecture | 10% | C | **A‑** | ▲▲ |
| G | Project Governance & Compliance | 8% | D | **A‑** | ▲▲▲ |

**Weighted grade ≈ B+/A‑ (3.46 / 4.3).** Original ≈ D‑ (0.9). **A/A+ on every dimension: NOT met** — two dimensions (A, D) sit at B; five at A‑; none reached A/A+.

> GPA map (4.3 scale): A+ 4.3 · A 4.0 · A‑ 3.7 · B+ 3.3 · B 3.0 · C‑ 1.7 · D 1.0 · F 0.
> Weighted: A 0.60 + B 0.555 + C 0.74 + D 0.45 + E 0.444 + F 0.37 + G 0.296 = **3.455**.

---

## Reproducibility statement

- **Target state audited:** branch `main` @ `bafc234` — the merge of PR #12 (`phase-7-governance`). **The task prompt's premise that PR #12 is "OPEN, not on main" is stale**: the merge is already on `main` (`bafc234 Merge pull request #12`), so `main` *is* the fully-remediated Phases 0–7 state. No merge was needed.
- **Environment:** Python 3.12.10; editable install `bob-llmwiki-knowledge-manager==1.0.0`.
- **What I ran firsthand:** `pytest --cov=src` (695 passed / 23 skipped / 0 failed, 84.4% cov); `pytest` with `src/tools/` re-included (74.9%); `ruff check` + `ruff format --check` (clean); `mypy` (0 issues, 34 files); `bandit -r src/ -ll` (0 High / 0 Med / 14 Low); all 8 `scripts/check_*.py` gates (pass); `generate_api_docs.py --check` (41 in sync); `python -m src.validation` (regenerated report **reverted** with `git checkout --`, per the frozen-file constraint); `pip-audit` against the real locked closure; `uv lock --check`.
- **Reproduced:** the ~20% headline (fresh run **N=216, mean 18.96%, 95% CI [17.89, 19.98], null 0.57% PASS**) independently corroborates the committed frozen figure (**N=183, 20.01%, CI [18.9, 21.2], null 0.65% PASS**); C1 and C5 fixes go **red** on revert; `resolve_within` rejects all 5 escape vectors; the project's locked closure has **0 CVEs**.
- **Could NOT reproduce exactly (honestly disclosed by the harness):** the frozen "N=183 / 20.01%" is **not regenerable from HEAD** — `src/validation/corpus.py` auto-globs in-repo docs, so N drifts as the repo grows (183 → 216 today) and the committed run was `git_dirty=true`. The claim is verifiable only via the manifest `data_hash`, not re-derivable. This is disclosed, not concealed.
- **Mutation hygiene:** every revert-a-fix and gate-slip experiment was restored; `git status` shows **no changes** under `src/`, `scripts/`, `tests/`, `pyproject.toml`, or `evaluation/`.
- **A correction I owe on my own process:** my first `pip-audit` reported 293 CVEs — but that audited a *pre-existing polluted `.venv`* (493 packages incl. `transformers`/`torch`/`unstructured`, none of them project deps). The project's **real** locked closure (`uv.lock`, 45 packages) has **zero** known vulnerabilities (patched `urllib3 2.7.0`). The honest number is 0, not 293. Likewise, my early "fabrication sweep is clean" was **wrong** — my grep was scoped too narrowly and a malformed pipe hid the matches; the adversarial fan-out caught the surviving fabrication I missed. Both corrections are folded in below.

---

## Method

One orchestrator + ten refute-by-default subagents. The orchestrator established a shared empirical ground-truth firsthand (full suite, all gates, validation harness, clean-closure CVE audit), then did the **decisive mutation experiments personally, serially, on the main tree** (revert-a-fix for C1/C5/C7; a symlink/TOCTOU path-traversal probe; a coverage re-measurement; firsthand repros of the three highest-value new bugs). Ten subagents ran read-only in parallel: seven MECE-dimension refuters (each told to **break** its dimension's A-grade), a gate-slip agent in an **isolated git worktree** (plant a violation past each CI gate), a fresh-eyes bug hunter, and an internal-consistency auditor. Findings that survived were cross-checked against the orchestrator's firsthand evidence. Total: 10 agents, ~865k agent-tokens, ~19 min wall-clock.

---

## Dimension A — Product Integrity & Claims Substantiation · **B** (was F)

**The measurement engine is now genuinely honest — and I proved it by invoking it.** `src/validation/measure.py:94-107` constructs a *real* `PromptOptimizer(use_cache=False, max_tokens=None)` and calls `.optimize()` per document (no hand-written literal, unlike the fraudulent `run_token_validation.py`); `src/validation/report.py:5` *"refuses to print VALIDATED"* and prints measured numbers with provenance. Independent re-run: N=216, mean 18.96%, power-matched null **0.57% ≪ 19%** PASS, three mechanisms (compression / cache recompute-avoidance / lossy truncation) **rigorously separated**, complete 11-field manifest (`manifest.py:27-39`, seed=0). **A2** (catastrophic ‑13093.9% latency) is fixed — honest latency (mean 3.14 ms / p95 6.82 ms) is measured; **A3** (manifest) fixed; **A5** (budget) fixed via disclosure (`cost_tracker.py:295-319` surfaces `is_over_budget` rather than silently clamping). This is a real, large jump from F.

**Why it is not A (the sign-off blocker lives here):**

- **A1 — the fabrication still ships (Critical residual).** `68.96%` / `89.3%` / `91.80%` survive as *current, validated* results — not as retraction records — on **12+ verified-live surfaces** with no on-file banner: `docs/BOOK_CHAPTER_07.md:180-200` (fabricated Mean/Median/Std **+ the banned cache+opt+trunc re-blend**), `docs/BOOK_SUMMARY.md:119` ("**Validated:** 68.96%"), `docs/BOOK_CHAPTER_02/03/09.md`, `docs/BOOK_TABLE_OF_CONTENTS.md`, `docs/DESIGN_DOCUMENT.md:216`, `docs/adr/008-token-counting.md`, `docs/adr/011-monitoring-observability.md:713` ("✅ Tracked 89.3%"), `docs/architecture/QUALITY_ATTRIBUTES.md`, `docs/knowledge-base/guides/setup-token-optimization.md:4` ("reduce token costs by up to 89.3%"), `docs/knowledge-base/guides/p0-critical-fixes-implementation.md`. Repro: `grep -rlnE '68\.96|89\.3%' --include=*.md docs/ | grep -v knowledge-base/research | while read f; do grep -qiE 'retract|fabricat|withdrawn' "$f" || echo "LIVE-UNRETRACTED: $f"; done`.
- **The savings-claim gate gives false coverage (Medium).** `scripts/check_savings_claims.py:42-49` checks a **hardcoded 5-file allowlist** (STATUS/README/AGENTS/docs/INDEX/REPOSITORY_ANALYSIS_WORKFLOW + 2 code files). It *works correctly within that scope* (gate-slip confirmed it fails on an unbacked number added to README) — but it **structurally cannot see** the BOOK/DESIGN/ADR/guide files where the fabrication survives. Green CI is therefore **not** evidence of a clean tree.
- **A4 — half-fixed.** The source anecdote is now properly retracted (`evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md:8`), but `README.md:109-124` still frames it as a "**Proof point**" and cites a "**Full transcript**" the source file explicitly says does not exist.

---

## Dimension B — Architecture & Design · **A‑** (was D)

Genuinely improved, not repainted. **Layering is clean and gated** — zero `src/→scripts/` imports (`check_layering.py` verified; the B3 fix relocated shared utilities to `src/tools/`). **Pricing is single-homed** — `src/pricing.py` holds the model string + USD table once, imported everywhere, enforced by `check_value_homes.py` (2 price values + version + python floor + security line). The **facade** (`src/facade.py`, `class TokenOptimizer`) + CLI (`bob-optimize = src.cli:main`) + `src/__main__.py` exist and the facade is a thin, god-object-free delegator. Monitoring health checks are wired; the delegation product is honestly labeled orphaned/experimental (`AGENTS.md`, `src/delegation/experimental.md`).

**Residuals keeping it off A (config→runtime is only partly wired):**
- **The facade builds a config-driven `MultiLevelCache` that the optimize() path never uses (Medium, verified).** `facade.cache` is a `MultiLevelCache`; `facade.optimizer.cache` is a *separate* `ExactCache` (confirmed disjoint object identities). So `config.cache.*` (L2 threshold, sizes) has **no effect** on optimization caching — undisclosed in the facade docstrings, unlike the well-documented ExactCache-bypass (B5).
- `OptimizerConfig.strategies` is a **dead config field** — declared, defaulted, validated, tested at the dataclass level, but never read by the optimizer runtime (residual of B6).
- `MonitoringConfig` fields (`log_level`, `metrics_enabled`, `health_check_interval`) are never read via the facade; the facade docstring's "composes monitoring from ConfigSchema" **overclaims**.

---

## Dimension C — Code Correctness & Reliability · **A‑** (was D)

**The correctness remediation is real, not theatrical — and I proved two of the load-bearing fixes go red on revert.** Every Critical/High bug C1–C7 + the RLock re-entrancy deadlock is fixed in current code, each guarded by a **behavioral** regression test (asserts the fixed *behavior*, not a config default — the old circular `target_savings==0.893` test is retired, `test_prompt_optimizer.py:23`):

- **C1 (Critical) — VERIFIED by revert.** `prompt_optimizer.py:476` now passes `metadata=metadata` as a keyword (with an explanatory comment). Revert to positional → `test_cache_integration` + `test_cache_actually_hits_on_repeat` **FAIL**; restored. The optimizer cache actually hits.
- **C5 (High) — VERIFIED by revert.** `semantic_cache.py:180-183` adds an exact-key fast-path. Disable it → `test_exact_key_returns_its_own_value_under_collisions` **FAILS** (`assert not [40, 55, 68, …]` — dozens of keys returning a colliding neighbour's value); restored.
- **C7** (health always 0) fixed at `health.py:427-449` (reads nested `cache.L1/L2` hits/misses); **C4** deadlock test passes under the new 60 s pytest-timeout; **C3** config-atomicity guarded (`test_manager.py:179`); **C6** order-preservation guarded (`test_strategies.py:114`).

**Residuals + newly-found bugs keeping it off A:**
- **NEW (Medium, verified) — versioned-key collision.** `ExactCache` builds keys as unescaped `f"{version}:{key}"`. `set('b', version='v1:a')` and `set('a:b', version='v1')` both hash to `v1:a:b`; `get('b', version='v1:a')` returns `'VALUE_B'`. Same wrong-content class as C1/C5, in the version dimension. (Practical exploitability is low — versions are normally colon-free literals — but it is a real latent defect the prior audits missed.)
- **NEW (Medium, verified) — `ConfigManager.load_from_env()` skips validation.** `CONFIG_CACHE__L1__MAX_SIZE=0` and `CONFIG_OPTIMIZER__MAX_TOKENS=-5` are accepted silently; `update()`/`load_from_file()` validate, the env path does not.
- **C8 residual (Low).** `get_metrics_collector` (`metrics.py:428`) and `get_cost_tracker` (`cost_tracker.py:441`) remain unlocked check-then-create singletons; `ExactCache.get()` is a lockless check-then-act on a shared `OrderedDict` while `SemanticCache` holds a lock.
- **Doc contradiction (Medium).** `STATUS.md:18` — the self-declared canonical maturity doc — still asserts "**Known Critical/High correctness bugs remain open**," which is **false** against the verified code + CHANGELOG, and no gate catches it.

---

## Dimension D — Testing & Verification · **B** (was C‑)

Genuinely above C‑: **D2** (circular target-savings test) removed, **D5** (split-brain `pytest.ini` vs `pyproject`) resolved, **D6** (no `--cov-fail-under`) fixed with an enforced 80% gate + per-package floors, **D3** substantially fixed (the claim-validating harness runs by default: `measure.py` 99%, `report.py` 100%, real null test, seed=0). 39 test files assert real behavior with real components — not mock-theater.

**Why it is a B, not A (the second sign-off blocker):**
- **The 84.4% headline is load-bearing on excluding `src/tools/` (High, verified).** Re-measured with tools in the denominator: **74.9%** (3867 stmts, 972 missed) — *below the project's own 80% gate*. The exclusion is documented (CLI utils relocated from `scripts/`), but the excluded third includes the **untrusted-path handlers**: `kb_query.py` 18.9%, `batch_file_reader.py` 20.4%, `component_analyzer.py` 44.9% (only `safe_paths.py` is 100%). The headline number is scoped around the least-tested, most-security-relevant code.
- **D1 not fully closed.** The thesis-proving delegation `agents/*.py` (293 stmts) sit at 15–24% each; the 52% per-package floor is explicitly designed *not to ratchet*, freezing the shallow level.
- **Residual flakiness.** Wall-clock assertions with no time abstraction remain (`test_multi_level_cache.py:388` `l1_time<l2_time`; `test_exact_cache.py:279` `<1.0ms`; `test_coordinator.py:308` `<0.05s`) — the suite itself concedes this (`tests/README.md:90`).

---

## Dimension E — Build, Release & Supply-Chain · **A‑** (was F)

The biggest single-dimension jump (F → A‑). Verified firsthand: **one comprehensive `ci.yml`** with a 3.11/3.12 test matrix and *all* gates actually wired (not present-but-dead) — coverage+fail_under, per-package floors, status consistency, ruff lint/format, mypy, layering, savings-claims, value-homes, API-doc freshness, community-health, **bandit SAST blocking at medium+**, e2e, the manifest-backed validation job (null+manifest+tiktoken gates, deliberately **not** gating savings *magnitude* — a sound anti-fabrication design, `ci.yml:158-161`), benchmark-regression, a CycloneDX SBOM, and Dependabot. **`uv.lock` is present and in sync** (`uv lock --check` clean), `requirements.txt` is gone, the Python floor is coherent and validator-enforced (`>=3.11`, classifiers 3.11/3.12, CI matrix 3.11/3.12), and the **real locked closure has 0 known CVEs** (patched `urllib3 2.7.0`).

**Residuals keeping it off A:**
- **CI never installs *from* `uv.lock` (Medium).** Every job runs `pip install -e ".[dev,monitoring]"`, floating on `>=` floors — so builds are reproducible-in-principle (lock exists) but **not lock-pinned in practice**.
- `pip-audit` is `continue-on-error` (`ci.yml:229`) — no CVE can fail the build. Low impact today (closure is clean) but an A+ supply chain gates on it.
- `evaluation/requirements.txt` is a second, unpinned, un-validated dependency manifest outside the single-home discipline (residual E3).
- Import package is literally top-level `src` (E6); no pre-commit (server-side enforcement only).

---

## Dimension F — Documentation & Knowledge Architecture · **A‑** (was C)

Solidly fixed and adversarially survived: **F1** (maturity status single-homed — no "Production Ready" contradiction in the primary live surfaces; `check_status_consistency.py` enforces STATUS/README/AGENTS agreement), **F2** (one authoritative `docs/ARCHITECTURE.md`; the competitors `UNIFIED_ARCHITECTURE.md` / `ACTUAL_SYSTEM_ARCHITECTURE.md` carry real on-file deprecation banners), **F5** (complete API docs across every `src` package with an AST `--check` drift gate — 41 files in sync).

**Residuals keeping it off A:**
- **AGENTS.md contradicts itself on the delegation coverage floor (Medium) — a "one home per value" violation the gates miss.** `AGENTS.md:44` says "~54% floor"; `AGENTS.md:362` says "~53% / floor 52%". The actual is 52.9% / floor 52% (`check_coverage_by_package.py`), so the loud `:44` value is *factually wrong*, and no CI validator covers it.
- `STATUS.md:23` cites "683 passed" — stale vs the actual 695, and by-design outside the consistency gate.
- Several un-bannered dated docs (`PHASE3/PHASE4_IMPLEMENTATION_COMPLETE.md`, `BOOK_SUMMARY.md`) still assert "Production Ready," protected only by STATUS.md's blanket disclaimer rather than on-file banners.
- `docs/` root is a ~35-file un-curated dump (the full BOOK set, DESIGN_DOCUMENT + addendum, planning docs) outside the Diátaxis spine — and it is **where the A1 fabrication hides**. F and A share this root cause.

---

## Dimension G — Project Governance & Compliance · **A‑** (was D)

Genuine, honest, well-executed — not vibes. **`resolve_within` is empirically sound** (`src/tools/safe_paths.py`): my probe threw absolute paths, `../`, dir- and file-symlink escapes, the sibling-prefix trick, and mid-path `..` at it — **all rejected**, legit paths allowed. It uses the correct resolve-*then*-check order (`.resolve()` canonicalizes symlinks before the component-wise `is_relative_to`). All three tools route their untrusted caller path through it (`batch_file_reader.py:45`, `component_analyzer.py:42`, `kb_query.py:251`). The STRIDE N/A calls are defensible for a single-user local CLI; **ADR-012's fabricated security stack is cleanly retracted** (banner + superseded by `docs/security/threat-model.md`); the 12-artifact community-health set is real and non-stub (gate-slip confirmed deleting/stubbing any of them fails CI).

**Residuals keeping it off A:**
- **The threat model over-claims completeness (Medium).** `docs/security/threat-model.md:104-115` states delegation uniformly routes untrusted `task.target` through `resolve_within`, but `src/delegation/agents/documentation_agent.py:50-55` does a **raw `Path(target).rglob()` outside** it. The delegation subsystem is orphaned/demo-only (so exposure is limited), but the model's exhaustiveness claim is false, and delegation is the lowest-covered package (52.9%) with **zero** boundary security tests.
- `INSTALLATION.md:18` still ships a broken `git clone github.com/yourusername/...` command (repo-metadata placeholder only partly fixed — `pyproject.toml` was corrected).
- The TOCTOU resolve-then-open window is unnamed in the threat model's residual register (negligible for a local CLI, but the model claims to be exhaustive).

---

## Tension reconciliation (the four the prompt flagged, + two more)

| # | Tension | Resolution | Evidence |
|---|---------|-----------|----------|
| 1 | Three grades: STATUS "≈D‑" vs AGENTS "7/10" vs vendor-eval "C+" | **STATUS's "≈D‑" is the declared live SSoT — but it is now itself stale.** The true re-audited grade is **B+/A‑**. STATUS carries the pre-remediation institutional figure. | `STATUS.md:3,11`; this audit's scorecard |
| 2 | STATUS "correctness bugs remain OPEN" vs CHANGELOG "C1–C7 fixed" | **CHANGELOG holds.** C1–C7 + RLock verified fixed in code (C1/C5 revert-tested). `STATUS.md:18` is **false** and ungated. | `CHANGELOG.md:109-110`; revert experiments above |
| 3 | Fabricated metrics = "false positive" (issue-list) vs "Critical defect" (institutional) | **Institutional A1 holds, decisively.** The fabrication is not "clearly marked as a target" — it still ships as "**Results**" and "✅ Tracked" on live BOOK/ADR/guide surfaces. `comprehensive-issue-list:721` is **wrong**. | `docs/BOOK_CHAPTER_07.md:180`; `adr/011:713`; 12-file live grep |
| 4 | AGENTS delegation "~54%/floor 54%" vs "~53%/floor 52%" | **`AGENTS.md:362` ("~53% / floor 52%") holds; `:44` ("54%") is wrong** vs actual 52.9%/floor 52%. Real internal contradiction, ungated. | `AGENTS.md:44,362`; `check_coverage_by_package.py` |
| 5 | Test count STATUS "683" vs actual 695 | Honest-but-stale drift; `STATUS.md:23` labels it a point-in-time CI snapshot; ungated. | `STATUS.md:23`; `pytest` run |
| 6 | N=183 (docs/committed) vs N=216 (fresh re-run) | **Citing N=183 is honest** — anchored to the committed manifest `data_hash`; the corpus-glob drift is disclosed via `git_dirty`. Not regenerable from HEAD, but not fabricated. | `manifest.json`; `corpus.py:38-41` |

**Net:** four *real* internal inconsistencies (#2, #3, #4, and STATUS's own stale grade), all **unenforced by any CI validator**, plus two honest drifts.

---

## Severity-ranked residual findings (the gap to A+)

**Critical (blocks A on the flagship dimension)**
1. **A1 — the 68.96% / 89.3% fabrication still ships unretracted** on ~12+ live doc surfaces (BOOK series, DESIGN_DOCUMENT, adr/008, adr/011, QUALITY_ATTRIBUTES, setup + p0 guides), complete with fabricated statistics and the banned mechanism re-blend.

**High**
2. **Coverage headline is load-bearing on the `src/tools/` exclusion** — real total 74.9% < the 80% gate; excluded code includes the untrusted-path handlers (D).
3. **`check_savings_claims.py` is scoped to a 5-file allowlist** — false coverage that lets #1 pass CI green (A / governance).

**Medium**
4. Facade's config-driven `MultiLevelCache` is disjoint from the optimize() `ExactCache` — config.cache is inert for the primary path (B, verified).
5. NEW: versioned-key collision in `ExactCache` (`f"{version}:{key}"` unescaped) (C, verified).
6. NEW: `ConfigManager.load_from_env()` accepts invalid values without validation (C, verified).
7. `STATUS.md:18` falsely asserts correctness bugs "remain open"; `AGENTS.md:44` states the wrong delegation floor — both ungated "one home" violations (C/F).
8. `THREAT_MODEL.md` over-claims delegation containment; `documentation_agent.py:50-55` does raw `rglob()` outside `resolve_within` (G).
9. CI installs on `>=` floors, never from the in-sync `uv.lock` — not lock-reproducible (E).

**Low**
10. C8 unlocked singletons + lockless `ExactCache.get()` race; TTL-ignoring accessors; in-place metadata mutation across L1/L2; direct-call truncation budget overshoot (C, all verified by the bug-hunt).
11. `pip-audit` non-blocking; `evaluation/requirements.txt` second unpinned manifest; `INSTALLATION.md` broken clone URL; `README §5` "Proof point / Full transcript" overstatement; BOOK_CHAPTER_07 stale "310+ tests / 98.4% coverage."

---

## What is genuinely good (credited, and it is a lot)

- **Honest, reproducible measurement.** The validator invokes the real optimizer, refuses "VALIDATED," separates the three savings mechanisms, ships a full manifest, and passes a power-matched null — independently reproduced. This is a model of the discipline the flagship metric once violated.
- **Real regression tests.** C1–C7 + RLock each fail when the fix is reverted (spot-verified). This is the standard the plan demanded and it was met in code.
- **All 7 CI gates are real enforcement** — gate-slip planted a violation past each and every one failed (exit 1) then recovered on revert; zero paper gates.
- **Sound, empirically-tested path-traversal containment**; **0-CVE locked closure**; **clean ruff/mypy/bandit**; single-homed pricing/version/python-floor with a validator.

---

## Path to GO (what would flip this to a sign-off)

Concentrated and addressable — no re-architecture:

1. **Purge or banner the surviving fabrications** (the ~12 live files) **and broaden `check_savings_claims.py`** from its 5-file allowlist to a tree-wide scan (or add a dedicated "no un-retracted 68.96/89.3/91.80" gate). This closes A1 *and* the false-coverage gate together → unblocks **A** toward A.
2. **Either test `src/tools/` to the 80% bar or fold it into the gated denominator** (especially the untrusted-path handlers `kb_query`/`batch_file_reader`) → unblocks **D** toward A.
3. **Route `documentation_agent`'s `rglob` through `resolve_within`** (or explicitly scope-exclude delegation and correct the THREAT_MODEL completeness claim) → tightens **G**.
4. **Fix the ungated "one home" lies:** `STATUS.md:18` ("remain open"), `AGENTS.md:44` (delegation floor), and add validators so they cannot silently drift again.
5. **Close the verified new bugs** (versioned-key collision, env-config validation, disjoint cache) and **install-from-lock in CI**.

Complete 1–2 and the weighted grade clears A‑ with A on the two blocking dimensions; complete 1–5 and "A/A+ on every dimension" is within reach.

---

## Reproducibility of this audit

- **Target:** `main` @ `bafc234` (PR #12 merged; Phases 0–7 on main).
- **Method:** orchestrator firsthand verification + 10 refute-by-default subagents (7 MECE dimensions + gate-slip in an isolated worktree + fresh-eyes bug hunt + consistency); ~865k agent-tokens.
- **Commands:** `pytest --cov=src` (+ a tools-included re-measure); `ruff`/`mypy`/`bandit`; all 8 `scripts/check_*.py`; `generate_api_docs.py --check`; `python -m src.validation` (report **reverted** after); `pip-audit` on the exported locked closure; `uv lock --check`; targeted revert-a-fix on `prompt_optimizer.py` & `semantic_cache.py`; a symlink/TOCTOU probe of `resolve_within`.
- **Repository state:** unchanged by this audit — all mutation experiments reverted; `git status` clean under `src/`, `scripts/`, `tests/`, `pyproject.toml`, `evaluation/`.

*Audit performed: 2026-07-14 · Standard: institutional-vendor (ISO/IEC 25010, OpenSSF/SLSA, arc42/ADR/Diátaxis, CHAOSS) · Verdict: **NO-GO** against A+ sign-off; **B+/A‑** weighted, up from D‑ · This file is frozen.*
