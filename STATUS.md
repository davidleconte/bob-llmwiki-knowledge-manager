# Project Status — Single Source of Truth

> **This file is the canonical maturity status for the repository.** Any other document that states a maturity level must defer to this file. Divergence is a bug (a "one home per value" CI validator, `scripts/check_status_consistency.py`, enforces this automatically). Historical/dated snapshots under `docs/**` and `evaluation/**` reflect what was believed at their date and are **not** authoritative.

| Field | Value |
|---|---|
| **Overall status** | **Beta — Not Production Ready** |
| **Maturity** | Remediation in progress toward production-readiness |
| **As of** | 2026-07-13 |
| **Basis** | [Institutional Audit 2026-07-13](docs/knowledge-base/research/audit-2026-07-13-institutional.md) · [External Audit 2026-07-12](docs/knowledge-base/research/external-audit-2026-07-12.md) |
| **Weighted grade vs institutional bar** | ≈ D‑ (target: A+) |
| **Roadmap** | Phases 0–8 (see the approved remediation plan) |

## What "Beta — Not Production Ready" means here

- **Headline savings metrics are retracted.** The "68.96% / 95% CI / VALIDATED" figures were fabricated by a simulation that never invoked the optimizer (see [VALIDATION_DISCLAIMER.md](evaluation/VALIDATION_DISCLAIMER.md)). Real, reproducible, manifest-backed validation is scheduled in Phase 5.
- **Two systems are being integrated into one.** The Bash "Bob Shell KB manager" and the Python "token optimizer" were never merged; a unified facade/CLI is scheduled in Phase 4.
- **Known Critical/High correctness bugs remain open** (see the institutional audit, Dimension C).
- **CI runs; supply-chain hardening is in progress.** A minimal CI enforces the coverage gate, the flag-gated e2e suite, and benchmark-regression trending. Dependency locking, lint/type gates, a reconciled Python matrix, and an SBOM are Phase 3 (in progress).

## Terminology guardrail

- **"Coverage"** = code coverage measured by `pytest --cov`, enforced by the `fail_under` gate in `pyproject.toml` (the single home for the number: **≥80%**). It is **not** the same as **test pass rate**. Do not conflate them. Point-in-time snapshot (from CI, 2026-07-14): 82.4% coverage; 653 passed / 23 skipped / 0 xfailed (the config→runtime xfails were wired in Phase 4). Undated maturity claims elsewhere must defer to this file; a CI validator (`scripts/check_status_consistency.py`) enforces that the cited gate matches `pyproject.toml`.
- **Every published savings/cost number must cite a reproducible run with a manifest** (data hash, code SHA, config, seed, library versions, `git_dirty`). Numbers without provenance are not to be published.

## Not claimed

Enterprise SLAs, production support, guaranteed savings percentages, automated multi-agent research, or Windows compatibility.
