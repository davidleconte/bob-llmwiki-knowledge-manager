# Project Governance

This document describes how decisions are made in
`bob-llmwiki-knowledge-manager`.

## Model

The project uses a **single-maintainer, ADR-driven** model. The maintainer
(**@davidleconte**) is responsible for the roadmap, for reviewing and merging
contributions, and for the final decision on any change. As the community
grows, this document will evolve toward a multi-maintainer model.

## How decisions are recorded

Significant technical and process decisions are captured as **Architecture
Decision Records (ADRs)** under [`docs/adr/`](docs/adr/). The ADR culture is the
backbone of this project's governance — it is how "why" is preserved.

An ADR:

- States the **context** (the forces at play), the **decision**, the
  **options considered**, and the **consequences**.
- Has a **status**: `Proposed`, `Accepted`, `Deprecated`, or `Superseded`.
- Is **append-only history** once accepted. A decision that changes is recorded
  by adding a new ADR (or a superseding banner on the old one), never by
  silently rewriting the original. See `docs/adr/012-security-model.md` for a
  worked example of a superseded ADR.

## Proposing a change

1. **Small changes** (bug fixes, docs, tests): open a pull request directly,
   following [`CONTRIBUTING.md`](CONTRIBUTING.md).
2. **Significant changes** (new subsystems, contract changes, anything with
   architectural consequence): open an issue or draft ADR first to align on the
   approach before implementation.
3. All changes pass the CI gate suite. The gates are non-negotiable invariants,
   not style preferences — they encode the correctness and honesty rules the
   project was remediated to hold (see `CHANGELOG.md`).

## Roadmap

The project follows a dependency-ordered remediation roadmap (Phases 0–8),
tracked in `AGENTS.md` and the audit under
`docs/knowledge-base/research/`. The current phase status is a single home in
`AGENTS.md`, validated by `scripts/check_status_consistency.py`.

## Changing this document

Governance changes are themselves significant decisions: propose them via an
ADR or a clearly-scoped pull request, and expect discussion before they land.
