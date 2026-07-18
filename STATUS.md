# Project Status — Single Source of Truth

> **This file is the canonical maturity status for the repository.** Any other document that states a maturity level must defer to this file. Divergence is a bug (a "one home per value" CI validator, `scripts/check_status_consistency.py`, enforces this automatically). Historical/dated snapshots under `docs/**` and `evaluation/**` reflect what was believed at their date and are **not** authoritative.

| Field | Value |
|---|---|
| **Overall status** | **Beta — Not Production Ready** |
| **Maturity** | Remediation in progress toward production-readiness |
| **As of** | 2026-07-18 |
| **Basis** | [Phase-8 Adversarial Re-Audit 2026-07-14](docs/knowledge-base/research/audit-2026-07-14-signoff.md) · [Institutional Audit 2026-07-13](docs/knowledge-base/research/audit-2026-07-13-institutional.md) · [External Audit 2026-07-12](docs/knowledge-base/research/external-audit-2026-07-12.md) |
| **Weighted grade vs institutional bar** | **A+ (4.30/4.30)** — all 4 structural gaps closed 2026-07-17; SLA v1.0 + load-test suite + `sentence-transformers` in dev extras added 2026-07-18 |
| **Roadmap** | Phases 0–8 complete + A+ gap closure + 2 production-readiness items (2026-07-18). G-1–G-4 closed. **SLA (2026-07-18):** `docs/sla.md` v1.0; `tests/load/` 8 load+soak tests; `load` CI job (informational). **ST (2026-07-18):** `sentence-transformers>=3.0` in dev extras; all 3 MiniLM tests unconditionally active. **P2 integration (KB Manager ↔ TOS):** `src/embeddings/` package (persistent index), `KnowledgeBaseQuery` 3-tier fallback, `MultiLevelCache` L3 type-contract fix (L3 moved to `query_l3()`). **P3 (Knowledge Graph Layer):** `src/graph/` — pure-Python property graph, PageRank re-ranking, KB health analysis (`orphans()`, `hubs()`), CLI `graph-build/query/health` — shipped and validated 2026-07-17 (ADR-017; p@3=0.88 with MiniLM, `graph_weight=0.0` default confirmed). **P4 (Query Quality):** `KnowledgeBaseQuery(recency_weight=)`, `query(date_filter=)`, `bob-optimize kb-search` CLI, `NodeProps` enrichment (mtime_epoch/content_length/description/related_refs), AF-3 chunker fix, MiniLM sentence-transformers wiring — shipped 2026-07-17 (ADR-018; Miss #3 resolved, p@3=0.88 baseline maintained). **Gap-fix (post-P4):** 3 structural gaps closed: (1) `bob-optimize kb-status` integration health CLI; (2) `bob-optimize analyze` delegation pipeline wired to CLI and KB (ADR-019; floor raised 52% → 70%, measured 84%); (3) `docs/ARCHITECTURE.md` renamed to `docs/kb-manager/ARCHITECTURE.md` eliminating dual-doc confusion. |

## What "Beta — Not Production Ready" means here

- **Headline savings are now measured, manifest-backed (Phase 5).** The earlier "68.96% / 95% CI / VALIDATED" figures were fabricated by a simulation that never invoked the optimizer (see [VALIDATION_DISCLAIMER.md](evaluation/VALIDATION_DISCLAIMER.md)) and remain withdrawn. Phase 5 replaced that with a real harness (`python -m src.validation`): optimizer compression measures **~20% mean savings** (95% CI ≈ [19%, 21%]) over N=183 real in-repo documents with a passing null test; cache recompute-avoidance and lossy truncation are reported **separately**. Provenance: `evaluation/results/validation-2026-07-14/` (`report.json` + `manifest.json`).
- **The Python token optimizer now has a unified facade/CLI (Phase 4, done).** Its cache/optimizer/truncation/monitoring are composed behind a single `TokenOptimizer` facade and a `bob-optimize` CLI (`python -m src`), with configuration wired to the runtime. The Bash "Bob Shell KB manager" remains a separate product; merging the two is not in scope.
- **The Critical/High correctness bugs the institutional audit found (Dimension C: C1–C7 + the RLock deadlock) are fixed**, each guarded by a behavioral regression test that fails if the fix is reverted (see `CHANGELOG.md` → Fixed). Lower-severity residuals are tracked in the Phase-8 sign-off audit.
- **CI enforces the quality gates.** Coverage gate + per-package floors, ruff lint/format, mypy, a 3.11/3.12 matrix, the flag-gated e2e suite, the manifest-backed validation harness (null + manifest + tiktoken gates) and its savings-claim guard, benchmark-regression trending, an SBOM, and a `src→scripts` layering gate all run in CI. Dependency locking, the lint/type gates, and the reconciled Python matrix landed in Phase 3; the facade/CLI + config→runtime wiring in Phase 4; the real, manifest-backed validation in Phase 5.

## Terminology guardrail

- **"Coverage"** = code coverage measured by `pytest --cov`, enforced by the `fail_under` gate in `pyproject.toml` (the single home for the number: **≥80%**). It is **not** the same as **test pass rate**. Do not conflate them. Point-in-time snapshot (2026-07-18, post-gap-fix): 84% delegation / 89.82% global — `src/tools/` and `src/delegation/` both fold into the gated denominator with per-package floors (`scripts/check_coverage_by_package.py`); 1112 passed / 23 skipped (performance tests excluded from coverage run due to benchmark harness contention; 23/23 pass when run in isolation). Undated maturity claims elsewhere must defer to this file; a CI validator (`scripts/check_status_consistency.py`) enforces that the cited gate matches `pyproject.toml`.
- **Every published savings/cost number must cite a reproducible run with a manifest** (data hash, code SHA, config, seed, library versions, `git_dirty`). Numbers without provenance are not to be published.

## Not claimed

Enterprise SLAs, production support, guaranteed savings percentages, automated multi-agent research, or Windows compatibility.
