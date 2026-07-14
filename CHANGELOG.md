# Changelog

All notable changes to this repository — the Bash **Bob Shell Knowledge Manager**
and the Python **token-optimization system** — are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-12

### Added
- Initial release of Bob Shell Knowledge Manager
- Custom knowledge-manager mode for Bob Shell
- Four document templates (concept, guide, reference, research)
- Knowledge base structure (concepts, guides, references, research)
- Automation scripts:
  - `install.sh` - Install mode to Bob Shell
  - `init-project.sh` - Initialize KB structure in projects
  - `validate-kb.sh` - Validate KB structure and integrity
  - `export-kb.sh` - Export KB to multiple formats (markdown, Obsidian, HTML, PDF)
- Comprehensive documentation:
  - Quick Start Guide (5-minute setup)
  - Installation Guide
  - Usage Guide
  - Customization Guide
  - Workflows Guide
  - Architecture Documentation
  - Comparison with LLM-Wiki
- Three complete example knowledge bases:
  - Software project (e-commerce platform, 7 documents)
  - Research project (consensus algorithms, 6 documents)
  - Personal wiki (knowledge management, 6 documents)
- Comprehensive test suite:
  - 45 automated tests (100% passing)
  - Mode configuration validation (10 tests)
  - Template structure verification (16 tests)
  - Script functionality and syntax (19 tests)
  - pytest configuration with unit/integration markers

### Features
- Structured knowledge organization with four document types
- Full-text search across all documents using Bob Shell's native tools
- Persistent memory integration with save_memory tool
- Automatic cross-referencing between documents
- Template-driven document creation
- Zero external dependencies (uses only Bob Shell native features)
- Export to multiple formats (markdown, Obsidian, HTML, PDF)
- File restrictions to protect knowledge base integrity
- Naming conventions enforcement
- INDEX.md automatic maintenance

### Documentation
- README with badges, quick start, and comprehensive overview
- Quick Start Guide for 5-minute setup
- Detailed installation instructions
- Usage patterns and workflows
- Customization options
- Architecture documentation
- Feature comparison with LLM-Wiki
- Three working examples with best practices

### Testing
- pytest configuration with markers
- 10 mode configuration tests
- 16 template structure tests
- 19 workflow and integration tests
- Bash syntax validation for all scripts
- Example knowledge base integrity checks

## [Unreleased]

The repository grew a second system alongside the Bash KB manager: a Python
**token-optimization library** (~3,500 lines) plus the phased audit remediation
(Phases 0–7) that hardened it. None of this is cut as a release yet — it is
**Beta, Not Production Ready** (see [`STATUS.md`](STATUS.md)).

### Added
- **Token-optimization system** (`src/`): multi-level cache (L1 exact + L2
  semantic), prompt optimizer, intelligent truncator, and monitoring.
- **Unified facade + CLI** (Phase 4): a single `TokenOptimizer` facade composes
  cache/optimizer/truncation/monitoring; the `bob-optimize` CLI (`python -m src`)
  drives it; typed configuration is wired to the runtime.
- **Manifest-backed validation harness** (Phase 5): `python -m src.validation`
  measures the real product and writes a reproducibility manifest per run (data
  hash, code SHA, config, seed, library versions, `git_dirty`, `tiktoken_active`)
  with a null test and honest variance/latency.
- **CI quality gates**: a 3.11/3.12 matrix, coverage gate + per-package floors,
  ruff lint/format, mypy, a flag-gated e2e suite, benchmark-regression trending,
  a CycloneDX SBOM, a `src -> scripts` layering gate, the validation job (null +
  manifest + tiktoken), and three "one home per value" guards — status, savings,
  and the generic value-homes validator.
- **Documentation** (Phase 6): a single authoritative architecture doc, a
  Diátaxis navigation spine with a getting-started tutorial, complete
  auto-generated API reference with a CI freshness check, and this changelog.
- **Governance & community-health** (Phase 7): `SECURITY.md` (disclosure policy),
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `SUPPORT.md`,
  `.github/CODEOWNERS`, and issue/PR templates, kept present by a
  `check_community_health.py` CI gate.

### Changed
- **Savings are measured, not asserted.** Optimizer compression measures a
  manifest-backed ~20% mean savings on real in-repo prose (95% CI ≈ [19%, 21%],
  N=183; manifest: `evaluation/results/validation-2026-07-14/`); cache
  recompute-avoidance and lossy truncation are reported **separately**, never
  blended into one headline.
- **One home per value.** Model pricing, the coverage gate, the package version,
  the supported-Python floor, and the maturity status each have one canonical
  source, enforced in CI.

### Fixed
- Correctness bugs C1–C7 (Phase 1), including the L2 semantic-cache colliding-key
  wrong-content bug (C-5) and an RLock re-entrancy deadlock; single pricing home.

### Security
- **STRIDE threat model** (Phase 7): [`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md)
  — a real, code-grounded analysis (trust boundaries, honest N/A calls, a
  residual-risk register) that supersedes the fabricated ADR-012 security stack.
- **Path-traversal containment** (Phase 7): the `src/tools` read helpers
  (`ComponentAnalyzer`, `KnowledgeBaseQuery`, `BatchFileReader`) now reject `../`
  and absolute-path escapes via `src/tools/safe_paths.resolve_within`, with a
  regression test in `tests/tools/`. Fixes the one concrete Information-Disclosure
  finding in the threat model.
- **Security CI**: bandit SAST (medium+, blocking) and Dependabot (weekly
  `pip` + `github-actions`), alongside the existing CycloneDX SBOM + `pip-audit`.

### Removed
- **The fabricated "68.96% / VALIDATED" savings figure is retracted.** The
  simulation that produced it never invoked the optimizer; Phase 5 replaced it
  with the real harness and reduced the old validator to a thin shim. See
  [`evaluation/VALIDATION_DISCLAIMER.md`](evaluation/VALIDATION_DISCLAIMER.md).
- **The fabricated security architecture in ADR-012 is retracted** (Phase 7). It
  documented an auth / AES-256 / RBAC / rate-limit / audit-log stack and asserted
  it had passed a security audit with zero incidents — none of which was ever
  implemented. The ADR is kept as audit trail with a retraction banner;
  `docs/security/THREAT_MODEL.md` is now canonical.

### Planned
- Phase 8 — Sign-off: an independent adversarial re-audit.

---

For more information, see the [README](README.md) and [documentation](docs/).
