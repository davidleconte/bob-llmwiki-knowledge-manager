# Documentation

The entry point to this repository's documentation, organized by the
[Diátaxis](https://diataxis.fr/) framework — four kinds of doc for four different
needs. Start here and follow the quadrant that matches what you're trying to do.

> **Two systems live here.** The Python **token-optimization system** (`src/`) and
> the Bash **Bob Shell Knowledge Manager** (~500 lines) share a repo but are
> separate products. Canonical maturity/status: [`STATUS.md`](../STATUS.md).
> This page links live, evergreen docs; dated audit snapshots (under
> `knowledge-base/research/`, `PHASE*_IMPLEMENTATION_COMPLETE.md`,
> `project-management/reviews/`) are a point-in-time record, not listed here.

| Quadrant | When you want to… |
|---|---|
| [Tutorials](#tutorials) | learn by doing, start to finish |
| [How-to guides](#how-to-guides) | accomplish a specific task |
| [Reference](#reference) | look up precise facts (APIs, CLI, config) |
| [Explanation](#explanation) | understand how and why it works |

## Tutorials

*Learning-oriented — safe, guided, guaranteed to work.*

- **[Optimize your first prompt](tutorials/optimize-a-prompt.md)** — the Python
  optimizer/facade/CLI end to end (install → count → optimize → from Python).
- [Quick Start](QUICK_START.md) — the Bash KB manager in 5 minutes.

## How-to guides

*Task-oriented recipes for someone who already knows the basics.*

Token-optimization system:

- [Set up token optimization](knowledge-base/guides/setup-token-optimization.md)
- [Track costs](knowledge-base/guides/cost-tracking-guide.md)
- [Real-time monitoring](knowledge-base/guides/real-time-monitoring-guide.md) · [Monitoring guide](MONITORING.md)
- [Set up end-to-end testing](knowledge-base/guides/e2e-testing-setup-guide.md)

Bob Shell KB manager:

- [Installation](INSTALLATION.md) · [Usage](USAGE.md) · [Workflows](WORKFLOWS.md) · [Customization](CUSTOMIZATION.md)
- [Repository analysis workflow](REPOSITORY_ANALYSIS_WORKFLOW.md) · [Complete repository analysis](knowledge-base/guides/complete-repository-analysis.md)
- [Bob Shell UI integration](knowledge-base/guides/bob-shell-ui-integration.md)

## Reference

*Information-oriented — precise, dry, structured.*

- **[API reference](api/README.md)** — generated from source docstrings, CI-checked for freshness.
- **[Architecture Decision Records](adr/README.md)** — ADR 001–012.
- **[Architecture](architecture/ARCHITECTURE.md)** — the authoritative system architecture (also explanation).
- **CLI** — [`src/cli.py`](../src/cli.py): `optimize`, `truncate`, `count`, `cache-stats`, `cost-report`, `metrics`, `health`, `config`.
- **Configuration** — [`src/config/schema.py`](../src/config/schema.py) (typed defaults).
- **Validation harness** — [`src/validation/README.md`](../src/validation/README.md) (`python -m src.validation`).
- **Cache API** — [cache-api.md](knowledge-base/references/cache-api.md).
- **Security policy** — [`SECURITY.md`](../SECURITY.md) (vulnerability disclosure).
- **Contributing & governance** — [`CONTRIBUTING.md`](../CONTRIBUTING.md) · [`GOVERNANCE.md`](../GOVERNANCE.md) · [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) · [`SUPPORT.md`](../SUPPORT.md).
- **[CHANGELOG](../CHANGELOG.md)** · **[STATUS](../STATUS.md)** (canonical maturity/coverage).

## Explanation

*Understanding-oriented — the concepts, design, and trade-offs.*

- **Concepts** — [token optimization](knowledge-base/concepts/token-optimization.md) · [multi-level caching](knowledge-base/concepts/multi-level-caching.md) · [dependency analysis](knowledge-base/concepts/dependency-analysis.md)
- **[Architecture](architecture/ARCHITECTURE.md)** — components, dataflow, config→runtime.
- **[Security (STRIDE threat model)](security/THREAT_MODEL.md)** — trust boundaries, residual risks; supersedes the retracted ADR-012.
- **Design** — [Design document](DESIGN_DOCUMENT.md) · [MECE framework](MECE_FRAMEWORK.md) · [Comparison with alternatives](COMPARISON.md)
- **Savings methodology** — [KB savings estimation methodology](knowledge-base/references/kb-savings-estimation-methodology.md).
- **The Complete Guide (book)** — [table of contents](BOOK_TABLE_OF_CONTENTS.md) (long-form narrative).

---

*Looking for the older exhaustive index? See [INDEX.md](INDEX.md). Knowledge-base
docs also have their own [index](knowledge-base/INDEX.md).*
