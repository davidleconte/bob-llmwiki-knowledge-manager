# Project Status — Single Source of Truth

> **This file is the canonical maturity status for the repository.** Any other document that states a maturity level must defer to this file. Divergence is a bug (a "one home per value" CI validator, `scripts/check_status_consistency.py`, enforces this automatically). Historical/dated snapshots under `docs/**` and `evaluation/**` reflect what was believed at their date and are **not** authoritative.

| Field | Value |
|---|---|
| **Overall status** | **Beta — Not Production Ready** |
| **Maturity** | Remediation in progress toward production-readiness |
| **As of** | 2026-07-14 |
| **Basis** | [Institutional Audit 2026-07-13](docs/knowledge-base/research/audit-2026-07-13-institutional.md) · [External Audit 2026-07-12](docs/knowledge-base/research/external-audit-2026-07-12.md) |
| **Weighted grade vs institutional bar** | ≈ D‑ (target: A+) |
| **Roadmap** | Phases 0–8 (see the approved remediation plan) |

## What "Beta — Not Production Ready" means here

- **Headline savings are now measured, manifest-backed (Phase 5).** The earlier "68.96% / 95% CI / VALIDATED" figures were fabricated by a simulation that never invoked the optimizer (see [VALIDATION_DISCLAIMER.md](evaluation/VALIDATION_DISCLAIMER.md)) and remain withdrawn. Phase 5 replaced that with a real harness (`python -m src.validation`): optimizer compression measures **~20% mean savings** (95% CI ≈ [19%, 21%]) over N=183 real in-repo documents with a passing null test; cache recompute-avoidance and lossy truncation are reported **separately**. Provenance: `evaluation/results/validation-2026-07-14/` (`report.json` + `manifest.json`).
- **The Python token optimizer now has a unified facade/CLI (Phase 4, done).** Its cache/optimizer/truncation/monitoring are composed behind a single `TokenOptimizer` facade and a `bob-optimize` CLI (`python -m src`), with configuration wired to the runtime. The Bash "Bob Shell KB manager" remains a separate product; merging the two is not in scope.
- **The Critical/High correctness bugs the institutional audit found (Dimension C: C1–C7 + the RLock deadlock) are fixed**, each guarded by a behavioral regression test that fails if the fix is reverted (see `CHANGELOG.md` → Fixed). Lower-severity residuals are tracked in the Phase-8 sign-off audit.
- **CI enforces the quality gates.** Coverage gate + per-package floors, ruff lint/format, mypy, a 3.11/3.12 matrix, the flag-gated e2e suite, the manifest-backed validation harness (null + manifest + tiktoken gates) and its savings-claim guard, benchmark-regression trending, an SBOM, and a `src→scripts` layering gate all run in CI. Dependency locking, the lint/type gates, and the reconciled Python matrix landed in Phase 3; the facade/CLI + config→runtime wiring in Phase 4; the real, manifest-backed validation in Phase 5.

## Terminology guardrail

- **"Coverage"** = code coverage measured by `pytest --cov`, enforced by the `fail_under` gate in `pyproject.toml` (the single home for the number: **≥80%**). It is **not** the same as **test pass rate**. Do not conflate them. Point-in-time snapshot (2026-07-14, Phase 8): 87.1% coverage — `src/tools/` (the untrusted-path handlers) is now folded into the gated denominator with a per-package floor (`scripts/check_coverage_by_package.py`); 771 passed / 23 skipped / 0 xfailed. Undated maturity claims elsewhere must defer to this file; a CI validator (`scripts/check_status_consistency.py`) enforces that the cited gate matches `pyproject.toml`.
- **Every published savings/cost number must cite a reproducible run with a manifest** (data hash, code SHA, config, seed, library versions, `git_dirty`). Numbers without provenance are not to be published.

## Not claimed

Enterprise SLAs, production support, guaranteed savings percentages, automated multi-agent research, or Windows compatibility.
