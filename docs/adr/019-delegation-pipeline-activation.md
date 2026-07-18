# ADR-019: Activate Delegation Module as Analysis Pipeline

**Status:** Accepted
**Date:** 2026-07-17
**Deciders:** @davidleconte
**Context:** Token Optimization System + Delegation subsystem

---

## Context

The delegation module (`src/delegation/`) was built in Phase 2 as a parallel
sub-agent framework for repository analysis (6 agents: Security, Quality,
Performance, Architecture, Documentation, Research). Since Phase 4 it has been
marked `EXPERIMENTAL` and held at a 52% coverage floor. Its status was
"maintained but not actively developed."

The Phase-8 institutional audit characterised the module as "dead weight" —
functionally correct, well-structured, but delivering no user value because it
was not wired into any production path.

Three integration scenarios were evaluated in
[`docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md`](../../docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md):

| Scenario | Effort | Verdict |
|---|---|---|
| Parallel prompt optimisation (batch) | 2–3 weeks | Marginal (optimizer already fast) |
| Repository analysis → KB ingestion | 1–2 weeks | **High value** |
| Full facade merger | 4–6 weeks | No value; adds complexity |

An adversarial re-audit (2026-07-17) further identified that `ResearchAgent`
already imports `KnowledgeBaseQuery` — a live integration point already present
in the codebase — and that a thin pipeline connector (~60 lines) could activate
the "repository analysis → KB ingestion" scenario without changing any existing
component.

---

## Decision

Activate the delegation module as the parallel analysis engine for repository
analysis via a thin connector module, `src/delegation/pipeline.py`.

**What `pipeline.py` does (~175 lines including docstrings):**

1. `DelegationCoordinator` fans out 6 agents in parallel across a target directory.
2. `ResearchAgent` runs first (no dependencies) to load prior KB findings via
   `KnowledgeBaseQuery`; all other agents depend on the research task completing.
3. Each successful agent result is optionally compressed via `TokenOptimizer`
   before being written as a KB research document to `output_dir`.
4. Returns `AnalysisPipelineResult` (dataclass) with per-agent status, compression
   ratios, total tokens saved, and coordinator statistics.

**What is NOT changed:**

- The `TokenOptimizer` facade — `pipeline.py` calls it as a client, not a component.
- The `DelegationCoordinator` or any agent — they are used as-is.
- The "delegation is not facade-wired" principle — `TokenOptimizer` does not depend
  on `src/delegation`; the dependency flows one way: `pipeline.py` → both.

---

## Rationale

### Why now

The gap analysis (2026-07-17) showed the integration was ~50 lines of glue away.
Keeping the module in `src/` as "maintained but not developed" incurred ongoing
CI cost (coverage floor enforcement, layering checks) while delivering zero value.
The three options were: activate, delete, or keep the status quo. Status quo is
the worst outcome.

### Why not delete

The `DelegationCoordinator` infrastructure (non-blocking per-task timeouts with
`executor.shutdown(wait=False)`, dependency-wave scheduling, load-balanced registry)
is non-trivial and correct. It would need to be rebuilt if the analysis use case
were activated later. Deletion is appropriate only if the analysis use case has no
roadmap; the `bob-optimize analyze` CLI subcommand provides that roadmap.

### Why the thin connector pattern

Merging delegation into the TOS facade would couple two systems with fundamentally
different latency characteristics (milliseconds vs seconds-to-minutes) and different
execution models (synchronous vs `ThreadPoolExecutor`). The connector pattern keeps
each subsystem independently testable and independently deployable.

---

## Consequences

### Positive

- The delegation module has a production use case and a user-facing CLI entry point.
- The "no re-derivation" principle (KB Manager's core value) is extended to repo
  analysis: `ResearchAgent` loads prior findings before other agents run, preventing
  duplicate KB entries for known issues.
- Token compression is applied to stored analysis reports, reducing KB document
  size and subsequent retrieval cost (compression is measured per-run at evaluation
  time; see `evaluation/results/validation-2026-07-14/manifest.json` for the
  current validated figure).
- Per-agent coverage floor raised from 52% to 70%; the module is no longer
  "dead weight" in the coverage accounting.

### Negative

- `src/delegation/__init__.py` now imports `pipeline.py` at package load time,
  which in turn imports `src.facade` (the `TokenOptimizer`). This is a new
  import-time dependency. The import is handled correctly because `pipeline.py`
  imports `TokenOptimizer` inside the function body (lazy), not at module level.
- The `analyze` CLI subcommand increases the CLI surface area.

### Neutral

- The `src/delegation/EXPERIMENTAL.md` status is updated from "Experimental / Not
  Integrated" to "Integrated — Analysis Pipeline".
- ADR count moves from 18 to 19.

---

## Implementation

See:

- `src/delegation/pipeline.py` — the connector module
- `src/cli.py` — `analyze` and `kb-status` subcommand handlers
- `tests/delegation/test_pipeline.py` — 8 unit tests (all pipeline paths)

---

## Validation

```bash
# Run pipeline tests
pytest tests/delegation/test_pipeline.py -v

# Run full delegation suite + coverage check
pytest tests/delegation/ --cov=src/delegation --cov-report=term-missing

# Confirm CLI parses correctly
bob-optimize analyze --help

# End-to-end smoke test (writes to /tmp, not docs/)
bob-optimize analyze src/cache --output-dir /tmp/delegation-test --kb-path docs/knowledge-base
```

---

## References

- [`docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md`](../../docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md)
- [`src/delegation/EXPERIMENTAL.md`](../../src/delegation/EXPERIMENTAL.md) (updated)
- [ADR-013: Facade and Factory Pattern](013-facade-factory-pattern.md)
- [ADR-014: KB Query Embedding Scorer](014-kb-query-embedding-scorer.md)
