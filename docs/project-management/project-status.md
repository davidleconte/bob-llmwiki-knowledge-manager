# Project Status — DEPRECATED

> **This document is deprecated. It is not the source of truth for project status.**
>
> The single source of truth for maturity, coverage, and test status is
> [`STATUS.md`](../../STATUS.md) at the repository root.
>
> This file previously asserted "All Phases Complete", a 98.5% coverage figure,
> and a "68.96% token savings (VALIDATED)" headline. Those claims were **stale or
> fabricated** — the savings number came from a simulation that never invoked the
> optimizer (see [`evaluation/VALIDATION_DISCLAIMER.md`](../../evaluation/validation-disclaimer.md)),
> and real validation is scheduled in Phase 5. They have been retracted here to
> stop them from re-circulating. The prior content remains in git history.

## Where to look instead

| For… | See |
|---|---|
| Current maturity, coverage gate, test status | [`STATUS.md`](../../STATUS.md) |
| The authoritative audit and Phases 0–8 roadmap | [`docs/knowledge-base/research/audit-2026-07-13-institutional.md`](../knowledge-base/research/audit-2026-07-13-institutional.md) |
| Why the headline savings numbers were retracted | [`evaluation/VALIDATION_DISCLAIMER.md`](../../evaluation/validation-disclaimer.md) |

A CI validator (`scripts/check_status_consistency.py`) enforces that live status
docs do not diverge from `STATUS.md`.
