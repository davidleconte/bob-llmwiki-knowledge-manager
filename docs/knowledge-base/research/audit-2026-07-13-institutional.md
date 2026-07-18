---
title: Institutional Codebase & Documentation Audit (2026-07-13)
category: research
status: active
tags: [audit, institutional, mece, scorecard, production-readiness, supply-chain, claims-integrity]
created: 2026-07-13
updated: 2026-07-13
audit_date: 2026-07-13
audit_method: MECE 7-dimension audit, 3 parallel read-only agents + orchestrator verification
audit_standard: ISO/IEC 25010 · OpenSSF Scorecard / SLSA · arc42+ADR+Diátaxis · Keep-a-Changelog/SemVer · CHAOSS
audit_scope: analysis only — repository unchanged at audit time
supersedes_context: builds on external-audit-2026-07-12.md (does not replace it)
target_grade: "A+ (independently re-audited, reproducible, production-ready)"
---

# Institutional Codebase & Documentation Audit

> **How this differs from the 2026-07-12 audit.** The prior pass was an excellent *findings list* (85 issues across 10 dimensions, refute-by-default). This pass is a **MECE scorecard benchmarked to named institutional standards**, it **re-verifies current state** (several things changed since 2026-07-12), and it **surfaces new Critical/High defects the prior pass missed**. It is additive, not a re-run.

## Executive Summary

**Date:** 2026-07-13 · **Method:** 7-dimension MECE audit, three parallel read-only agents (architecture/code, docs/governance, testing/CI/ops) + orchestrator firsthand verification · **Scope:** analysis only.

### Headline verdict

> The repository is a small (~8,300 physical lines, ~5,400 logical LOC, 34 modules), mostly-real Python library wrapped in documentation that describes a larger, validated, "production-ready" product that does not yet exist. The flagship savings metrics are fabricated by a simulation that never invokes the optimizer — and the repo's own `evaluation/VALIDATION_DISCLAIMER.md` says so, yet other live documents still label those numbers "VALIDATED." Against the highest institutional-vendor bar, the repository currently scores **≈ D‑**. It is a **good foundation with a candid culture**, not a production system.

### MECE Scorecard

Seven mutually-exclusive, collectively-exhaustive dimensions. Security is decomposed **by concern** — code-level (C), supply-chain (E), policy/threat-model (G) — to preserve MECE rather than lumping it.

| # | Dimension | Weight | Current | Target |
|---|-----------|:---:|:---:|:---:|
| A | Product Integrity & Claims Substantiation | 20% | **F** | A+ |
| B | Architecture & Design | 15% | **D** | A+ |
| C | Code Correctness & Reliability | 20% | **D** | A+ |
| D | Testing & Verification | 15% | **C‑** | A+ |
| E | Build, Release & Supply-Chain (DevSecOps) | 12% | **F** | A+ |
| F | Documentation & Knowledge Architecture | 10% | **C** | A+ |
| G | Project Governance & Compliance | 8% | **D** | A+ |

**Weighted current grade ≈ D‑ (≈0.9 / 4.3 GPA).** The self-claimed "Beta 7/10" is generous against an institutional bar.

### Severity roll-up (this pass)

- **Critical:** 3 (optimizer cache write-only; fabricated metrics still labeled VALIDATED; no CI/CD + non-reproducible builds)
- **High:** ~18 (correctness, architecture, supply-chain, doc-drift)
- **Medium/Low:** ~25

---

## Methodology

Three read-only agents swept disjoint MECE areas in parallel, each returning `path:line`-cited findings; the orchestrator independently verified load-bearing claims (grep/diff/git). Cross-checked against the prior `external-audit-2026-07-12.md` to (a) avoid re-reporting known issues, (b) confirm what was remediated, and (c) extend to institutional dimensions the prior pass did not grade (supply-chain, release engineering, governance maturity).

**Resources:** 3 agents · ~310k agent tokens · read-only · repository unchanged.

### What changed since 2026-07-12 (delta)

| Prior claim (2026-07-12) | Current state (2026-07-13) | Note |
|---|---|---|
| "Real code coverage 0% — never measured" | **49.4% measured** (`htmlcov/status.json`: 2,153 stmts, 1,090 missed) | Coverage tooling was run since; delegation still 0% |
| Health bugs #1/#2 (`get_stats`, `max_length` at `health.py:115/216`) | **No longer present** — `health.py` was rewritten in the "Phase 3 monitoring" track | Likely fixed, but a **new** health bug was introduced (see C) |
| "68.96% / VALIDATED" in README | Still in README as a **disclosed fabrication** (`README.md:206-210`); **still labeled VALIDATED** in other files | Partially addressed; not retracted |
| `README copy.md` | Still present — byte-identical untracked duplicate | Not addressed |

The remediation energy since the prior audit went into a *new* monitoring/validation track (git log: "Phase 3 …"), **not** into the prior audit's R1 (doc integrity) / R2 (build hygiene) / R3 (correctness) recommendations — which remain largely open.

---

## Dimension A — Product Integrity & Claims Substantiation · **F**

The product's core promise is Bobcoin/token savings. Its headline evidence is fabricated, and the repo contains its own refutation that was never propagated.

- **A1 (Critical) — fabricated headline metric still presented as validated.** `evaluation/VALIDATION_DISCLAIMER.md:20-42` documents that `scripts/run_token_validation.py:38-141` instantiates `PromptOptimizer()` but **never invokes it**; the "68.96%" is arithmetic between two hand-written literal functions; `"std": 0.0` on 90 deterministic duplicates makes the "95% CI [66.42, 71.51] / p<0.05" meaningless; the baseline is a strawman (optimized path capped at first 10 files, `:98`). Yet `evaluation/HONEST_ASSESSMENT.md:93-96`, `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md:246`, and `evaluation/results/validation_report.json` still label it **VALIDATED**.
- **A2 (Critical) — undisclosed catastrophic result.** `validation_report.json` records `time_savings_pct = -13093.9` — the "optimized" path was **~130× slower** — surfaced nowhere in prose except the disclaimer.
- **A3 (High) — not reproducible even in principle.** No seed, data hash, code SHA, or library versions in any `evaluation/results/*.json` (grep for seed/hash/manifest returns nothing). Fails the team's own reproducibility-manifest invariant.
- **A4 (High) — the "0.36 Bobcoin / 94-module" headline is an unverifiable anecdote.** `LIVE_EXAMPLE_HCD_ANALYSIS.md:137-143` splits 0.36 into "~0.30 read / ~0.06 analysis" with no token counts, tokenizer, model, or transcript; the same file asserts "ROI 20,000–30,000%" (`:206`).
- **A5 (High) — budget accounting is unguarded.** `evaluation/results/self-validation-full.json` shows `budget_spent 27.99975 > budget 25.0` → `budget_remaining: -2.999`; the cost tracker permitted a negative balance.

**Only genuinely substantiated figures:** the E2E controlled-environment ranges "prompt optimization 10–20%, cache hit 100% when matched, combined 40–60%" (`README.md:201-204`) — and even these are mock/tiktoken, not real-LLM (`HONEST_ASSESSMENT.md:258`).

---

## Dimension B — Architecture & Design · **D**

- **B1 (High) — two unmerged products in one tree.** A Bash "Bob Shell KB manager" (v1.0) and a Python token-optimizer (beta) share a repo with no reconciling facade; `AGENTS.md:7` even declares a *third* system (delegation) the README omits.
- **B2 (High) — no single source of truth for cost/pricing.** `token_counter.py:142-149` hard-codes a USD table ($0.03/1K gpt-4); `cost_tracker.py:16-19` uses a *different, contradictory* flat model (`TOKENS_PER_BOBCOIN=1000`, implied $0.01/1K). The default model string `"gpt-4"` is re-hard-coded in three constructors; the chars-per-token ratio appears as `3.5`, `3.0`, and `4` in different files. Any cost figure depends on which subsystem computed it.
- **B3 (High) — layering violation: `src/` depends on `scripts/`.** All six delegation agents do `sys.path.insert(0, <repo root>)` at import time and import `from scripts.utils.*` (`security_agent.py:11,14` +5). Reversed dependency + global import side effect.
- **B4 (High) — ~27% of `src/` is orphaned.** `delegation/` and `monitoring/` are fully built but wired into nothing (reachable only from example scripts); `VocabularyDriftMonitor` — built to detect the semantic cache's non-stationarity — is never invoked.
- **B5 (High) — the optimizer bypasses its own cache abstraction.** `prompt_optimizer.py:51-54` instantiates `ExactCache` directly with a comment admitting `MultiLevelCache`/`SemanticCache` "return wrong prompt's optimization." An abstraction the codebase cannot safely use for its primary purpose.
- **B6 (Medium-High) — the config layer is largely disconnected from runtime.** `OptimizerConfig.strategies` is never read by `PromptOptimizer` (strategies are hard-coded methods); config field names don't match optimizer params; default sizes diverge (config `l2=10000` vs code `500`); TTL fields are validated but unused.
- **Missing:** no orchestrator, facade, CLI, or `__main__` anywhere; empty `src/integration`, `src/batch`, `src/formatter` directories.

---

## Dimension C — Code Correctness & Reliability · **D**

- **C1 (Critical) — the optimizer's exact-cache is write-only.** `prompt_optimizer.py:388` calls `self.cache.set(prompt, optimized, metadata)` — 3 positional args — but `CacheInterface.set(key, value, version=None, metadata=None)` (`cache/base.py:141`) binds `metadata` to `version`. The set-key becomes `f"{metadata_dict}:{prompt}"` (`exact_cache.py:168`) while `get(prompt)` uses `version=None → "v1"`. **Keys never match → the optimizer cache never hits**; every call re-optimizes and cache-hit cost tracking is always 0. (New this pass; prior audit found the *semantic* cross-contamination, not this exact-cache miss.)
- **C2 (High) — non-deterministic semantic cache.** `embeddings.py:111-155` mutates the corpus and **refits the whole `TfidfVectorizer` on every new text**; similarity between the same two prompts drifts over time; a *read* triggers `_regenerate_all_embeddings()` — an O(n·corpus) side effect on lookups. Root cause of B5. **Blocks Phase 4 integration.**
- **C3 (High) — non-atomic config update.** `manager.py:220-228`: the rollback snapshot `temp_config` is created but never used; `_merge_config` mutates `self._config` **outside the lock, before validation**; a failed validation leaves invalid state applied and unreverted, then merges a second time inside the lock.
- **C4 (High) — coordinator timeout cannot cancel threads.** `coordinator.py:122` `future.result(timeout=…)` on a `ThreadPoolExecutor`; on timeout the worker keeps running and the `with` block hangs at shutdown → pool exhaustion. The constructor's global `timeout_seconds` is never enforced; `import asyncio` is dead.
- **C5 (High) — TTL configured everywhere, enforced nowhere.** `CacheEntry.age_seconds()/idle_seconds()` exist (`base.py:40,48`) and `schema.py:26,29`/`validator.py:53-79` expose/validate `l1/l2_ttl_seconds`, but no cache ever calls them. Entries only leave via LRU.
- **C6 (High) — priority truncation reorders content.** `strategies.py:159-177` sorts sections by priority and emits them in priority order, scrambling document order while claiming to "preserve" meaning. Token budgets also overshoot (non-additive per-piece sums; `SlidingWindow` prepends its "[…truncated…]" marker *after* the budget is filled).
- **C7 (Medium-High) — monitoring health check always reports 0.** `health.py:409-412` reads `metrics_data['cache_hits'/'cache_misses']`, but `MetricsCollector.get_metrics()` returns a **nested** schema (`cache.L1.hits`, `metrics.py:388`) with no such top-level keys → `total_operations` is always 0; health silently reports "ready (no operations yet)" forever. (New third health bug, distinct from the two prior ones that were fixed.)
- **C8 (Medium) — racy unlocked singletons.** `get_cost_tracker` (`cost_tracker.py:449`), `get_metrics_collector` (`metrics.py:436`), `get_drift_monitor` (`vocabulary_drift.py:328`) are check-then-set without a lock; only `health.get_health_checker` double-checks under a lock.
- **Resource / hygiene:** unbounded `_lookup_times` / `_similarity_scores` lists; `_remove_redundancy` (`prompt_optimizer.py:199-229`) can delete non-redundant words; one swallowed exception (`vocabulary_drift.py:140`); `datetime.utcnow()` ×10 (deprecated ≥3.12).
- **Positives:** every module docstringed; ~90% type-hint coverage; no `FIXME/HACK/XXX`; only one swallowed exception; clean `cache/base.py` interface; no dangerous primitives.

---

## Dimension D — Testing & Verification · **C‑**

- **D1 (High) — the subsystems that would prove the thesis are the least tested.** Coverage 49.4% overall, but `src/delegation/` = **0%** (all ~600 stmts incl. 6 agents), `monitoring/cost_reporting.py` 11%, `cost_tracker.py` 31%, `metrics.py` 42%. Cache/optimizer core is 85–100%.
- **D2 (High) — tests assert configuration, not the claim.** `tests/optimizer/test_prompt_optimizer.py:24` asserts `target_savings == 0.893` (a stored default). "Quality" is a purely lexical heuristic (`prompt_optimizer.py:325`) compared against its own seed default (`min_quality=0.918`) — circular. No test proves real token/cost savings or quality preservation.
- **D3 (Medium-High) — the claim-validating tests never run by default.** The entire `tests/e2e/` suite is `skipif(not RUN_E2E_TESTS)` (`test_real_llm.py:23`, `test_cost_tracking.py:25`) and uses tiktoken, not a real API.
- **D4 (Medium) — flaky, time-dependent tests.** Wall-clock assertions (`assert l1_time < l2_time`, `execution_time < 0.05`, `avg_time < 100`) and heavy `time.sleep` reliance; no randomness seeding despite sklearn nondeterminism. Four hard skips in `tests/monitoring/test_metrics.py:364,383,415,434` ("hangs on Python 3.14").
- **D5 (Medium) — split-brain pytest config.** Both `pytest.ini` and `pyproject.toml [tool.pytest.ini_options]` exist; `pytest.ini` wins → the config actually used **omits `--cov`** and defines a *different* marker set (`--strict-markers` latent breakage).
- **D6 (Medium) — no reproducibility discipline in tests/benchmarks.** No property-based tests; `pytest-benchmark` is wired but `.benchmarks/` is empty (never trended); no `--cov-fail-under` gate.

---

## Dimension E — Build, Release & Supply-Chain (DevSecOps) · **F**

- **E1 (Critical) — no CI/CD and no pre-commit.** No `.github/workflows/`, no `.gitlab-ci.yml`, no `.pre-commit-config.yaml`. Zero automated enforcement on push/PR.
- **E2 (High) — non-reproducible builds.** Every dependency is a floor (`>=`) with no lock file and no hashes (`pyproject.toml:26-29`, `requirements.txt`). A fresh install pulls arbitrary newer majors.
- **E3 (High) — two conflicting dependency manifests.** `requirements.txt` lists `black/flake8/mypy/isort/pytest-asyncio/pytest-benchmark/prometheus-client/structlog/redis/psutil` absent from `pyproject.toml`; `pyproject.toml` lists `pytest-mock` absent from `requirements.txt`. Neither is complete.
- **E4 (High) — Python-version incoherence.** `pyproject.toml:20` declares `>=3.8` (EOL), classifiers stop at 3.12, the environment is 3.14 (breaks metrics tests). Real minimum is **3.9+** — code uses PEP 585 builtin generics in evaluated annotation positions with no `from __future__ import annotations` (`token_counter.py:104`, `exact_cache.py:310`), which raises `TypeError` at import on 3.8.
- **E5 (High) — quality gates configured-but-absent.** `black/flake8/mypy/isort` are declared but have **no config files** and no enforcement; mypy ran (cache present) but ungated and unstrict. No ruff. No SBOM, no dependency vulnerability scan.
- **E6 (Medium) — fragile packaging.** The import package is literally `src`; imports rely on `tests/conftest.py` injecting `sys.path` rather than a real namespaced package.
- **Positive:** the git tree is clean — caches, coverage, `.db` (mypy cache, not app DBs), and `.DS_Store` are **not tracked**; `.gitignore` covers the big artifacts; scripts are non-destructive with backup-before-overwrite.

---

## Dimension F — Documentation & Knowledge Architecture · **C**

- **Strengths (real, keep + extend):** 13 ADRs (`docs/adr/001-012`); AST-generated, drift-resistant API docs (`scripts/generate_api_docs.py`).
- **F1 (High) — contradictory maturity status.** "Not Production Ready" (`README.md:223`) vs "Production Ready" (`evaluation/README.md:247`, `docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md:6`, `docs/index.md:5`). Direct violation of "one home per value."
- **F3 (Medium-High) — doc-vs-code numeric drift.** `src/` is 8,292 physical lines vs "~3,500" claimed (`README.md:28`); three Python-version stories (3.8/3.11/3.14); `pyproject` vs `requirements.txt` divergence; test counts 45/213/310+/317 across docs; cache-hit rate 10-20% / 23% / 80%+ across docs.
- **F4 (Medium) — stale, mis-scoped CHANGELOG.** Documents only the 45-test Bash framework at 1.0.0; omits the entire 317-test Python system and all phase work — violates the Keep-a-Changelog/SemVer contract it claims.
- **F5 (Medium) — incomplete API docs.** `docs/api/` omits `src/config/` and `src/delegation/` and 3 monitoring modules (~40% of `src/` undocumented); `docs/index.md` links only ~47% of markdown files.
- **F6 (Low) — bloat/duplication.** `README copy.md` byte-identical duplicate; two ~147K near-identical security scans (`security-scan-2026-07-12/13.md`, differ ~21 lines); `reports/` is all `test_*` demo fixtures mislabeled as reports; `.bob/settings.json` references a nonexistent `CONTEXT.md`.

---

## Dimension G — Project Governance & Compliance · **D**

| Artifact | Status |
|---|---|
| LICENSE (MIT) | ✅ Present |
| ADRs | ✅ Strong (13) |
| CONTRIBUTING | ❌ Missing |
| SECURITY policy (disclosure + SLA) | ❌ Missing (only a design ADR) |
| CODE_OF_CONDUCT | ❌ Missing |
| GOVERNANCE | ❌ Missing |
| CODEOWNERS | ❌ Missing |
| THREAT_MODEL | ❌ Missing |
| SUPPORT | ❌ Missing |
| Runbooks / on-call | ❌ Missing |
| Reproducibility manifests | ❌ Missing |
| Published repo metadata | ❌ Placeholder (`github.com/yourusername/...`, `pyproject.toml:45-48`) |

Governance is the standard-vendor community-health set — largely absent. The ADR culture is the seed to build the rest on.

---

## What is genuinely good (credited)

- Clean `cache/base.py` interface, cleanly implemented by `ExactCache`/`SemanticCache`/`MultiLevelCache`.
- AST-generated API docs that faithfully match signatures — a drift-resistant pattern worth extending.
- No dangerous primitives (no eval/exec/subprocess/pickle/shell/SQL), no hardcoded secrets, SHA-256 cache keying.
- ~90% type-hint coverage, every module docstringed, no `FIXME/HACK/XXX`.
- Clean git tree; adequate `.gitignore`; non-destructive scripts.
- 13 ADRs and an unusually candid self-audit posture (`VALIDATION_DISCLAIMER.md`, `HONEST_ASSESSMENT.md`) — the honesty is a genuine asset a mature remediation can stand on.

---

## Remediation → A+

Full roadmap: **[Repository Improvement Plan](./repository-improvement-plan.md)** (existing) + the dependency-ordered plan approved 2026-07-13 (Phases 0–8). Ordering is dependency-driven: *you cannot validate savings until the cache works and pricing has one home; you cannot integrate until the semantic cache is deterministic.*

1. **Phase 0 — Integrity freeze:** retract fabrications everywhere; one status; delete duplicates; fix broken refs.
2. **Phase 1 — Correctness foundation:** C1–C7 + single pricing source, each with a regression test.
3. **Phase 2 — Test hardening:** ≥80% coverage with a `--cov-fail-under` gate; claim-level + property tests; deterministic suite.
4. **Phase 3 — Build/supply-chain:** CI matrix, pinned+locked deps, SBOM, enforced gates, coherent Python support.
5. **Phase 4 — Integration:** unified facade/CLI; wire monitoring; connect config; kill the `src/→scripts/` layering violation. *(Delegation: the original "wire delegation" intent was superseded 2026-07-14 — it stays a **separate, layering-clean subsystem** per [delegation-integration-analysis](./delegation-integration-analysis-2026-07-13.md) (different problem domain; integration adds complexity without benefit). Phase 4 fixes only its B3 layering violation, relocating shared utilities to `src/tools/`.)*
6. **Phase 5 — Real validation:** rewrite the validator to invoke the real product; manifest per run; honest variance + latency.
7. **Phase 6 — Docs:** one architecture doc, Diátaxis structure, complete API docs, CHANGELOG discipline, a "one home per value" CI validator.
8. **Phase 7 — Governance:** the full community-health set + STRIDE threat model.
9. **Phase 8 — Sign-off:** independent adversarial re-audit; each dimension A/A+.

---

## Reproducibility of this audit

- **Method:** 3 read-only agents (architecture/code, docs/governance, testing/ops) + orchestrator verification.
- **Environment:** Python 3.14 (`.mypy_cache/3.14/`, `cpython-314` bytecode), macOS (Darwin 25.4.0).
- **Verification commands used:** `git ls-files`, `diff README.md "README copy.md"`, `grep -n` on cited files, `htmlcov/status.json` for coverage, `wc -l` for LOC.
- **Repository state:** unchanged at audit time; remediation performed subsequently on branch `audit/institutional-a-plus-2026-07-13`.

---

## References

- [External Audit 2026-07-12](./external-audit-2026-07-12.md) — the prior findings-list pass this builds on
- [Comprehensive Codebase Analysis 2026-07-14](./codebase-analysis-2026-07-14.md) — detailed analysis of current repository state
- [Repository Improvement Plan](./repository-improvement-plan.md)
- [Honest Assessment](../../../evaluation/HONEST_ASSESSMENT.md)
- [Validation Disclaimer](../../../evaluation/VALIDATION_DISCLAIMER.md)

*Audit performed: 2026-07-13 · Standard: institutional-vendor (ISO/IEC 25010, OpenSSF/SLSA, arc42/ADR/Diátaxis, CHAOSS) · Status: remediation in progress*
