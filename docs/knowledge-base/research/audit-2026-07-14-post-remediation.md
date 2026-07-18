---
title: "Post-Remediation Full Audit"
category: research
date: 2026-07-14
type: research
status: complete
frozen: true
tags: [audit, post-remediation, adversarial, full-review, codebase, documentation]
reviewer: Bob (Plan + Agent modes) + adversarial explore subagent
review_method: >
  Adversarial explore subagent (refute-by-default) + firsthand file reads for
  every finding. Every "fixed" claim verified against actual source. New bugs
  probed for. Synthesises all prior audits; does not repeat their evidence.
supersedes_context: >
  Verifies and updates audit-2026-07-14-signoff.md against the post-remediation
  branch state. That document remains the canonical Phase-8 sign-off record.
do_not_edit: >
  Point-in-time snapshot (2026-07-14, post-remediation). Corrections in new doc.
related:
  - audit-2026-07-14-signoff.md
  - full-codebase-review-2026-07-14.md
  - remediation-plan.md
created: 2026-07-14
updated: 2026-07-14

---

# Post-Remediation Full Audit
**Date:** 2026-07-14  
**Scope:** Adversarial verification of all Phase-8 sign-off findings + all remediation changes applied in the current session  
**Method:** Refute-by-default subagent + firsthand file reads for contested items  
**Prior grade (Phase-8 sign-off):** B+/A− (3.46/4.3) — NO-GO against A+ bar

---

## 1. Remediation Applied This Session — Verification

Every change made in the remediation session was independently verified.

| Change | Evidence | Result |
|--------|----------|--------|
| `yourusername` → `davidleconte` in 5 doc files | `grep -r yourusername --include=*.md . --exclude-dir=.claude` exits 1 (no matches outside frozen research) | ✅ Confirmed |
| `docs/knowledge-base/index.md` — README3.md link removed | Link absent from current file | ✅ Confirmed |
| `STATUS.md` grade table: D− → B+/A− | `STATUS.md:11` reads `≈ B+/A‑ (3.46/4.3)` | ✅ Confirmed |
| `STATUS.md` roadmap: Phase 8 = NO-GO filed | `STATUS.md:12` references `audit-2026-07-14-signoff.md` and `remediation-plan.md` | ✅ Confirmed |
| `dual-system-use-case-example.md` — WITHDRAWN banner | Line 13: `WITHDRAWN AS VALIDATED RESULTS` — triggers `has_banner()` gate | ✅ Confirmed |
| `using-both-systems-together.md` — WITHDRAWN banner | Line 14: `WITHDRAWN AS VALIDATED RESULTS` — triggers `has_banner()` gate | ✅ Confirmed |
| `token-optimizer-quick-install.md` — manifest provenance | Line 88: cites `evaluation/results/validation-2026-07-14/manifest.json` | ✅ Confirmed |
| `check_savings_claims.py` gate: all 209 surfaces pass | Script exits 0 | ✅ Confirmed |
| `README2.md`, `README3.md` deletion | **NOT DONE** — files still exist at root | ⚠️ Pending |

---

## 2. Prior Phase-8 Sign-Off Blockers — Current Status

### Blocker A — Product Integrity (was grade B, blocked A)

**A1 — Fabricated metrics on ~12 live surfaces**

All 12 files identified in `audit-2026-07-14-signoff.md:77` were individually verified:

| File | Banner present? | Banner token |
|------|-----------------|--------------|
| `docs/BOOK_CHAPTER_07.md` | ✅ Lines 1-3 | RETRACT |
| `docs/BOOK_SUMMARY.md` | ✅ Lines 1-3 | RETRACT |
| `docs/BOOK_CHAPTER_02/03/09.md` | ✅ Lines 1-3 | RETRACT |
| `docs/BOOK_TABLE_OF_CONTENTS.md` | ✅ Lines 1-3 | RETRACT |
| `docs/DESIGN_DOCUMENT.md` | ✅ Lines 3-23 (expanded) | FABRICAT + RETRACT |
| `docs/adr/008-token-counting.md` | ✅ Lines 1-3 | RETRACT |
| `docs/adr/011-monitoring-observability.md` | ✅ Lines 1-3 | RETRACT |
| `docs/architecture/QUALITY_ATTRIBUTES.md` | ✅ Line 3 | RETRACT |
| `docs/knowledge-base/guides/setup-token-optimization.md` | ✅ Line 3 | RETRACT |
| `docs/knowledge-base/guides/p0-critical-fixes-implementation.md` | ✅ Line 3 | RETRACT |

**A0 — `check_savings_claims.py` 5-file allowlist**

Gate now scans tree-wide (209 surfaces). Gate-slip was verified by the Phase-8 audit; CI wires it at `.github/workflows/ci.yml:82`.

**Blocker A verdict:** ✅ **Resolved.** All fabricated-metric surfaces carry retraction banners. Gate is tree-wide and passing.

---

### Blocker D — Testing (was grade B, blocked A)

**D1 — Real coverage 74.9% when `src/tools/` included**

`pyproject.toml:92-105`: `src/tools/` is NOT in the omit list. `scripts/check_coverage_by_package.py` FLOORS dict has `"src/tools": 85.0`. The most recent CI run (`STATUS.md:23`) reports **87.1%** with `771 passed / 23 skipped`.

The Phase-8 finding was that `src/tools/` was being excluded from the measured denominator. The current configuration explicitly includes it — this was the Phase-8 fix that brought the headline from 84.4% (excluding tools) to 87.1% (including tools, with tools tested to 85%+ floor).

**Blocker D verdict:** ✅ **Resolved.** Coverage is measured inclusively with `src/tools/` in scope and gated at 80% global + 85% per-package floor for tools.

---

## 3. Code Correctness — C1–C7 + RLock Verified

All 7 critical bugs and the RLock deadlock were verified against current source:

| Bug | Fix location | Verification |
|-----|-------------|--------------|
| **C1** — optimizer cache always missed (metadata positional arg) | `src/optimizer/prompt_optimizer.py:491` | `self.cache.set(prompt, result["optimized"], metadata=metadata)` — keyword arg confirmed |
| **C5** — semantic cache key collision | `src/cache/semantic_cache.py:177-187` | Exact-key dict fast-path before embedding/similarity lookup confirmed |
| **C7** — health check always reports 0 ops | `src/monitoring/health.py:430-434` | Reads nested `cache.L1/L2.hits/misses` confirmed |
| **RLock deadlock** | `src/cache/exact_cache.py:24-41, 86` | `@_synchronized` decorator on 15 methods, `threading.RLock()` confirmed |
| **Versioned-key collision** | `src/cache/exact_cache.py:129` | `escape_version(version)` called in `_make_versioned_key` confirmed |
| **Env-config validation bypass** | `src/config/manager.py:169-176` | Compute-validate-commit with lock confirmed |
| **Facade disjoint cache** | `src/facade.py:80-86` | `self.cache.get_l1_cache()` passed to optimizer — same L1 instance confirmed |

All regression tests for C1–C7 were verified present in prior audits (revert-tested by Phase-8 orchestrator).

---

## 4. Remaining Open Findings

### 4.1 Medium — `README2.md` and `README3.md` still exist at root

**Status:** ⚠️ Pending  
**Location:** `/README2.md`, `/README3.md`  
**Evidence:** Files exist; `README2.md` is a "dual-system" framing variant; `README3.md` is a near-copy of `README.md`. Neither is referenced from any live index (the `docs/knowledge-base/index.md` link was removed). `README.md` is the declared authoritative file.  
**Fix:** `rm README2.md README3.md` — no code change needed; no tests affected.

### 4.2 Low — C8 singleton races confirmed still present

**Status:** Documented residual (not a regression)  
**Location:** `src/monitoring/metrics.py:428-431`, `src/monitoring/cost_tracker.py:441-444`  
**Evidence:** Both `get_metrics_collector()` and `get_cost_tracker()` use unlocked check-then-create:
```python
# metrics.py:428-431
global _global_collector
if _global_collector is None:
    _global_collector = MetricsCollector()
return _global_collector
```
**Context:** Documented in `audit-2026-07-14-signoff.md:105` as a C8 residual. Practical exposure is very low — singletons are initialized at startup, not under sustained concurrent load. `tests/conftest.py` resets them between tests (`_reset_monitoring_singletons` autouse fixture).  
**Fix (if desired):** Wrap check-then-create in a `threading.Lock()` using double-checked locking or `threading.Lock()` with a module-level lock object.

### 4.3 Info — `STATUS.md` test count is a point-in-time snapshot

**Status:** Info only, expected  
**Location:** `STATUS.md:23`  
**Evidence:** Reads `771 passed / 23 skipped / 0 xfailed` — the most recent CI run count. The session just ran `pytest` which reported **897 passed, 23 skipped**. The delta (771 → 897) reflects the benchmark tests being included in the full suite run. The file correctly labels this a "point-in-time CI snapshot."  
**Fix:** Update to `897 passed / 23 skipped` to keep the snapshot current, or leave as-is (the language acknowledges the drift).

---

## 5. Full Scorecard — Post-Remediation

| # | Dimension | Phase-8 grade | Post-remediation grade | Change |
|---|-----------|:---:|:---:|:---:|
| A | Product Integrity & Claims Substantiation | B | **A−** | ▲ |
| B | Architecture & Design | A− | **A−** | = |
| C | Code Correctness & Reliability | A− | **A−** | = |
| D | Testing & Verification | B | **A−** | ▲ |
| E | Build, Release & Supply-Chain | A− | **A−** | = |
| F | Documentation & Knowledge Architecture | A− | **A−** | = |
| G | Project Governance & Compliance | A− | **A−** | = |

**Weighted grade: A− (≈ 3.7/4.3)** — up from B+/A− (3.46).

The two blocking dimensions (A and D) both resolved:
- **A** moved from B to A− by applying retraction banners to all remaining live fabrication surfaces and confirming the tree-wide gate passes.
- **D** confirmed at A− — `src/tools/` is in scope, per-package floor at 85%, global gate at 80%.

No dimension has reached A or A+. The gap to A+ on each dimension:

| Dim | Gap to A+ |
|-----|-----------|
| A | C8 singletons (Low); README2/3 at root (Medium) |
| B | `OptimizerConfig.strategies` dead config field; `MonitoringConfig` fields unread via facade |
| C | C8 singleton races (Low); TTL fields validated but never enforced |
| D | Delegation agents at 52% floor (intentional); residual wall-clock flaky tests |
| E | CI installs from `>=` floors, not from `uv.lock` (medium residual); `pip-audit` was already blocking |
| F | `docs/` root is a ~35-file dump outside Diátaxis spine |
| G | TOCTOU window unnamed in THREAT_MODEL residual register |

---

## 6. What Is Genuinely Excellent (Unchanged from Phase-8)

- **Real, manifest-backed validation harness** — `python -m src.validation`, honest ~20% mean, null test passing, 11-field manifest
- **Behavioral regression tests for C1–C7** — each fails on revert (spot-verified by Phase-8 orchestrator)
- **All 7 CI gates are real enforcement** — gate-slip confirmed every one blocks on violation
- **Sound path-traversal containment** — `resolve_within()` verified end-to-end
- **0-CVE locked closure** — `uv.lock` (45 packages), `pip-audit` blocking
- **Clean ruff/mypy/bandit** — zero lint, type, SAST issues across `src/`, `scripts/`, `tests/`

---

## 7. Recommended Next Actions

In priority order:

1. **Delete `README2.md` and `README3.md`** (1 min) — `rm README2.md README3.md`
2. **Update `STATUS.md:23` test count** from `771` to `897` (5 min) — keep snapshot current
3. **Fix C8 singletons** (30 min) — add module-level `threading.Lock` to `get_metrics_collector()` and `get_cost_tracker()` initialization
4. **Enforce TTL in caches** (2–4 h) — `ExactCache.get()` should check `CacheEntry.age_seconds()` against configured TTL before returning
5. **Wire CI to install from `uv.lock`** (30 min) — replace `pip install -e ".[dev,monitoring]"` with `uv pip install --system --locked -e ".[dev,monitoring]"` in test matrix jobs
