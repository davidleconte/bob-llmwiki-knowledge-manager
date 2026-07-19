# Changelog

All notable changes to this repository — the Bash **Bob Shell Knowledge Manager**
and the Python **token-optimization system** — are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- oldest-release marker; see [1.1.0] above for the current release -->
## [Unreleased] — 2026-07-19 Adversarial Audit & Remediation

### Research / Audits Added
- **Independent Counter-Audit 2026-07-19** (`docs/knowledge-base/research/counter-audit-2026-07-19-independent.md`):
  MECE 5-dimension audit, methodology McKinsey issue-tree, empirical test execution.
  Scored **2.9/5** overall. Key findings: retrieval stack unwired from every production path
  (CODE-01/02), optimizer can return empty string for inputs >4096 tokens (CODE-03),
  `validate-kb.sh` subshell counter-bug always reports "no broken links" (MEM-04),
  3 CI gates currently failing (CLM-01). ~20% compression claim (manifest-backed) and ≥80% coverage claim
  both survive adversarial reading.

- **Adversarial Audit 2026-07-19** (`docs/knowledge-base/research/adversarial-audit-2026-07-19.md`):
  Red-team audit with 19 CONFIRMED live exploits (15 executed in isolated sandbox,
  4 plausible). Headline findings: arbitrary file read via KB retrieval path (ATK-FS-01),
  persistent cache poisoning via hashing collision (ATK-FS-02/CODE-08), indirect prompt
  injection through KB auto-load (ATK-MEM-01), end-to-end defeat of honesty gates
  (ATK-GATE-01–03). Measurement core (manifest, null-test, supply-chain) held under
  direct attack.

- **Innovation Portfolio 2026-07-19** (`docs/knowledge-base/research/innovation-portfolio-2026-07-19.md`):
  24-candidate innovation portfolio in three horizons (H1 ship on existing assets,
  H2 lifecycle intelligence, H3 frontier). Top 5: Mnemox MCP Server, Compact Cold-Start
  Index, Docling Ingestion Bridge, Memory-Lifecycle Intelligence ("the Gardener"),
  Trust-Tiered Memory.

### Added — Adversarial Regression Test Suites (untracked, pending merge)

- **`tests/security/`** — 4 test modules covering ATK-FS-01 (path containment on all
  KB read paths), ATK-FS-02/CODE-08 (cache integrity: exact-key promotion, TTL,
  metadata isolation), ATK-MEM-01 (prompt injection boundary), and trust-tier enforcement.

- **`tests/gates/`** — 5 test modules covering CI gate baseline (Sub-Task 0), gate
  configuration, savings gate binding, status gate hardening, and `validate-kb.sh`
  exit-code regression.

- **`tests/retrieval/`** — 2 test modules covering ranking normalization (CODE-05/06
  scale-mismatch) and retrieval wiring (CODE-01/02 index+graph injection into
  production paths).

- **`tests/performance/test_dos_hardening.py`** — 3 tests: PageRank 2,000 dangling
  nodes <1s (ATK-DOS-01 already-fixed verification), semantic edge cap (ATK-DOS-02),
  L2 BLAS scan p95 <200ms (ATK-DOS-03).

- **`tests/optimizer/test_optimizer_integrity.py`** — 2 tests: `optimize()` never
  returns empty string for any non-empty input (CODE-03 regression).

### Planning Artefacts
- **`adversarial-remediation-plan.md`** — Detailed technical specification (v2) for
  closing all Critical and High audit findings. 14 sub-tasks (0, R, 1–12) covering:
  baseline freeze, integrity repair sprint, path containment, cache integrity, retrieval
  wiring, optimizer structure-preservation, ranking normalization, sanitization,
  provenance/trust-tier, honesty-gate hardening, status/grade gate, gate independence,
  DoS hardening, supply-chain hygiene, and an adversarial regression suite.
  Adversarially audited before implementation (10 v1 errors corrected in v2).

## [1.1.0] - 2026-07-18

> **Branch:** `fix-multilevel-cache-race` — all items below are shipped on this branch.

### Added
- **sentence-transformers added to `dev` extras** (`pyproject.toml`): cross-platform
  MiniLM backend is now always available in the dev venv. The previously-skipped
  `TestMiniLMBackend` tests (`test_minilm_st_fallback_activates`,
  `test_minilm_st_vector_shape_and_norm`, `test_minilm_generator_backend_property`)
  now run unconditionally and pass. `uv.lock` updated (sentence-transformers 5.6.0).

- **Load/soak test suite + formal SLA** (`tests/load/test_load_soak.py`, `docs/sla.md`):
  - `docs/sla.md` — SLA v1.0: latency p99 targets per component (L1 hit ≤ 750 µs,
    cold pipeline ≤ 3.5 ms, token count 1K ≤ 1.8 ms), throughput targets (≥ 50 req/s
    single-thread, ≥ 100 req/s combined 4-thread), concurrency and quality SLAs.
  - `tests/load/test_load_soak.py` — 8 tests: sustained throughput, 4-thread
    concurrent throughput + corruption check, L1 bulk-fill, deadlock-free concurrent
    writes, post-write hit-rate, 60-s soak (marked `slow`). All 7 non-soak tests pass
    locally asserting (`LOAD_TEST_ASSERT=1`), beating SLA targets by orders of magnitude
    on cache-hit path (~58 000 req/s vs 50 req/s SLA target).
  - **`load` CI job** added to `.github/workflows/ci.yml` — informational (non-blocking)
    on CI; asserting on developer hardware with `LOAD_TEST_ASSERT=1`.


- **G-2 gap closed: mypy full-scope type coverage** — removed `exclude = "^src/(delegation|tools)/"` from `[tool.mypy]`; fixed all resulting type errors across `src/cache/embeddings.py`, `src/graph/graph.py`, `src/cli.py`, `src/tools/component_analyzer.py`, `src/tools/kb_query.py`, `src/delegation/agents/security_agent.py`, and `src/delegation/agents/research_agent.py`. `src/` now type-checks clean (0 errors; `[annotation-unchecked]` notes only) under `--ignore-missing-imports`.
- **G-4 gap closed: CODEOWNERS covers `src/delegation/`** — added `/src/delegation/ @davidleconte` entry to `.github/CODEOWNERS`.

- **Gap-fix: Delegation Analysis Pipeline** (ADR-019, `src/delegation/pipeline.py`):
  - `src/delegation/pipeline.py` — thin connector (~175 lines) running 6 parallel
    agents, compressing each report through `TokenOptimizer`, and writing KB
    research documents to `output_dir`.
  - **`bob-optimize analyze <target>`** CLI subcommand: `--kb-path`, `--output-dir`,
    `--workers`, `--depth`, `--no-compress`. Path-traversal containment enforced.
  - **`bob-optimize kb-status`** CLI subcommand: reports embedding backend,
    index freshness, compression availability, and doc counts in JSON or
    human-readable form.
  - Per-agent coverage floor raised 52% → 70% in
    `scripts/check_coverage_by_package.py`; measured at 84% after adding
    `tests/delegation/test_pipeline.py` (9 tests) and
    `tests/delegation/test_agents_containment.py` (10 smoke + containment tests).
  - `scripts/setup.sh` — one-step full-stack setup: Python extras, embedding
    index build, stack validation.

- **Gap-fix: KB Manager architecture doc consolidation** (Sub-Task 7):
  - `docs/ARCHITECTURE.md` (KB Manager arc42 document) renamed to
    `docs/kb-manager/ARCHITECTURE.md` to eliminate the dual-architecture-doc
    navigation confusion identified in the gap audit.
  - Cross-references in `README.md`, `docs/architecture/ARCHITECTURE.md`,
    `docs/README.md`, and `AGENTS.md` updated.
  - `tests/test_workflows.py::test_documentation_files_exist` updated to
    assert the new path.

- **P4 — Query quality improvements** (ADR-018):
  - `KnowledgeBaseQuery(recency_weight=0.0)`: optional recency tiebreaker. Blends
    relative file mtime into scores (`score = (1-rw)*base + rw*(norm_mtime×15.0)`).
    Resolves golden-set Miss #3 (`security-scan` recency tie). Default `0.0` is
    backward-compatible.
  - `KnowledgeBaseQuery.query(date_filter=None)`: optional ISO date prefix filter
    (e.g. `"2026-07"`). Includes undated documents (fail-open). Resolves Miss #2
    (date-based queries). Default `None` is backward-compatible.
  - **`bob-optimize kb-search`** CLI subcommand: `--recency-weight`, `--date-filter`,
    `--max-results`, `--categories` (`src/cli.py`).
- **P4 — Graph NodeProps enrichment** (`src/graph/graph.py`, `src/graph/builder.py`):
  four new optional fields with backward-compatible defaults:
  `mtime_epoch` (file mtime), `content_length` (char count),
  `description` (first paragraph ≤ 200 chars), `related_refs` (raw frontmatter list).
  `KnowledgeGraphBuilder._add_nodes()` populates all four. Old `.bob/kb-graph.json`
  files load cleanly via `from_dict()` `.get(key, default)`.
- **P3 — Knowledge Graph Layer** (`src/graph/`): pure-Python property graph over
  KB documents. `KnowledgeGraph` (adjacency dict, BFS, PageRank), `KnowledgeGraphBuilder`
  (explicit edges from frontmatter `related:` + inline links; semantic edges via
  `PersistentEmbeddingIndex` cosine similarity at threshold 0.30), `GraphRanker`
  (lazy PageRank cache, `rerank()` blend formula), `GraphStore` (atomic JSON
  persistence to `.bob/kb-graph.json`). All are opt-in; injected into
  `KnowledgeBaseQuery` via `graph=` / `graph_weight=` parameters (ADR-017).
- **Graph CLI commands**: `bob-optimize graph-build`, `bob-optimize graph-query`,
  `bob-optimize graph-health` (KB structural health report: orphans, hubs,
  broken links, PageRank top-10).
- **Live validation** (`docs/knowledge-base/research/graph-validation-2026-07-17.md`):
  80-doc corpus, 2 836 edges (163 explicit + 2 654 semantic), 39→13 orphans rescued
  by semantic edges, p@3=0.88 with MiniLM (no regression, no uplift from graph
  re-ranking at any tested weight). Validated defaults: `semantic_threshold=0.30`,
  `graph_weight=0.0`. See ADR-017.

### Fixed (Round 4 — S-1, S-2, S-3, S-4)
- **S-1 — `MultiLevelCache.stats()` read `self.l2_cache.similarity_threshold` without
  `SemanticCache._lock`.** Added `SemanticCache.get_threshold()` — a lock-guarded
  read that mirrors `average_similarity_score()` — and updated `stats()` to call
  it (`src/cache/semantic_cache.py`, `src/cache/multi_level_cache.py`).

- **S-2 — `stats()` called `self.size()` after releasing `_stats_lock`**, producing a
  `unique_entries` value at a different moment-in-time than `l1_size` / `l2_size`.
  Inlined the key-union computation alongside the already-snapshotted
  `snapshot_keys()` calls so all four size-related fields are taken at the same
  point in time (`src/cache/multi_level_cache.py`).

- **S-3/S-4 — Deleted stale root-level plan files and `README2.md`:**
  `cache-race-fixes-plan.md`, `cache-race-fixes-round2-plan.md`, `README2.md`.
  `README.md` is the sole authoritative README; the plan documents are superseded
  by CHANGELOG.md entries and KB research notes.

- **Regression tests:** `TestStatsThresholdAndUniqueEntries` (3 tests — threshold
  round-trip, unique_entries bound, concurrent threshold-flip race detector).
  Tests: 1106 → 1109 passed.

### Fixed (Round 3 — O-1, O-2)
- **O-1 — `promote_l2_hits` read in `get()` outside `_stats_lock`.**
  After the L2 hit counter was incremented under `_stats_lock`, the `promote_l2_hits`
  flag was read outside the lock on the next line — a concurrent `disable_promotion()`
  / `enable_promotion()` could therefore race between the counter increment and the
  promotion decision. Fixed by snapshotting `do_promote = self.promote_l2_hits`
  inside the same `with self._stats_lock` block that increments `l2_hits`.
  The log message `promoted=` also uses the local snapshot (`do_promote`) rather
  than re-reading the live field (`src/cache/multi_level_cache.py`).

- **O-2 — `get_with_level()` bypassed all stats accounting and L2→L1 promotion.**
  The method re-implemented the two-level lookup without calling `get()`, so
  `l1_hits` / `l2_hits` / `misses` and `_lookup_times` were never updated for
  calls made via this path — `hit_rate()`, `average_lookup_time_ms()`, and
  `stats()` all silently under-reported. L2→L1 promotion was also skipped.
  Fixed by delegating to `self.get()` and inferring the hit level from the
  counter delta under `_stats_lock` (`src/cache/multi_level_cache.py`).

- **Regression tests:** `TestMultiLevelCachePromoteFlagRace` (1 test — concurrent
  flag-flip + getter, verifies no exceptions, checks counter consistency) and
  `TestGetWithLevelStatsAccounting` (3 tests — l1_hits, misses, hit_rate parity
  with `get()`). Tests: 1102 → 1106 passed.

### Changed
- **`EmbeddingGenerator(backend="minilm")` fallback chain**: now resolves via
  `mlx-embeddings` first (Apple Silicon, ~2–4 ms), then `sentence-transformers`
  as a cross-platform fallback (~5–20 ms), then `"hashing"` if neither is
  installed. Previously only `mlx-embeddings` activated MiniLM; `sentence-transformers`
  was installed but silently ignored (`src/cache/embeddings.py`). ADR-017 follow-up.

### Fixed
- **AF-3: `_extract_tables` used `findall` with capturing group** (truncated to last
  row). Replaced `findall` guard with `finditer` exclusively (`src/embeddings/chunker.py`).
- **AF-1: `FileBackedVectorStore` flush/reload shape mismatch.** `manifest.json`
  now holds chunk-level entries only; file-level mtime/hash sentinels are written
  to a separate `staleness.json`. Fixes `load()` returning `None` when chunk and
  file keys were mixed in one manifest (`src/embeddings/store.py`,
  `src/embeddings/index.py`).
- **AF-2: `is_stale()` always returning `True` with non-default KB paths.**
  Added explicit `kb_path: Optional[Path]` parameter; removed hardcoded
  `docs/knowledge-base` reconstruction from index path (`src/embeddings/index.py`).
- **AF-4: Private `_embedder` access in `KBIndexer`.** Replaced with public
  `embedder` property on `PersistentEmbeddingIndex` (`src/embeddings/index.py`,
  `src/embeddings/indexer.py`).

- P1-1: KB query hybrid embedding scorer (ADR-014, `EmbeddingGenerator` injection)
- P1-3: Opt-in context compression in `knowledge-manager` mode

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

## [1.0.0-tos] - 2026-07-16

The token-optimization library (`src/`) reaches its first stable release.
Maturity: **Beta** — all correctness bugs resolved, all fabricated figures
retracted and replaced with manifest-backed measurements. See [`STATUS.md`](STATUS.md).

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
- **C-1 — `MultiLevelCache` stats counters unsynchronised** (`src/cache/multi_level_cache.py`):
  added `_stats_lock = threading.RLock()` and serialised all four counter mutations
  (`l1_hits`, `l2_hits`, `misses`, `l3_hits`) in `get()`, `query_l3()`, `clear()`,
  and `reset_stats()`, and all counter reads in `hit_rate()`, `l1_hit_rate()`,
  `l2_hit_rate()`, and `stats()`. Regression test
  `test_stats_counters_never_race_with_concurrent_gets` in `TestMultiLevelCacheConcurrency`.
- **M-3 / ST-2 — `_lookup_times` deque non-atomic iteration** (`src/cache/multi_level_cache.py`):
  `stats()` and `average_lookup_time_ms()` now snapshot the deque into a local list
  under `_stats_lock` before calling `sum()`/`len()`, eliminating the
  check-then-act race that could raise `ZeroDivisionError` under concurrent
  `reset_stats()`. Deque appends in `get()` also moved inside `_stats_lock`.
- **C-2 — `SemanticCache.migrate()` TOCTOU** (`src/cache/semantic_cache.py`):
  the `with self._lock:` block now covers both the collection phase and the `set()`
  loop, making migration atomic with respect to concurrent writers. Safe because
  `self._lock` is a reentrant `RLock`. Regression test
  `test_migrate_is_atomic_no_interleaved_writes` in `TestSemanticCacheMigrateLock`.
- **M-4 — `SemanticCache.get_entry()` missing lock** (`src/cache/semantic_cache.py`):
  added `with self._lock:` around the `self.entries.get()` call. Called from
  `MultiLevelCache.get()` on the L2→L1 promotion path while concurrent eviction
  could mutate `entries`. Regression test
  `test_get_entry_never_raises_under_concurrent_eviction` in `TestSemanticCacheGetEntryLock`.
- **M-2 — `ExactCache.migrate()` silent no-op made visible** (`src/cache/exact_cache.py`):
  the dead iteration loop (which could never migrate anything because SHA-256 keys
  are irreversible) was replaced with an explicit early return. The log event is now
  `cache_migration_skipped` with `reason="irreversible_hash"` so callers can
  distinguish "nothing matched" from "migration not supported".
  `MultiLevelCache.migrate()` docstring updated to document that L1 always
  contributes 0. Regression tests in `TestExactCacheMigrate`.
- **L-1 — `MultiLevelCache.reset_stats()` missing `l3_hits` reset**
  (`src/cache/multi_level_cache.py`): `reset_stats()` now zeroes all four counters
  (`l1_hits`, `l2_hits`, `l3_hits`, `misses`) inside `_stats_lock`, consistent
  with `clear()`. Regression test `test_reset_stats_clears_l3_hits` in `TestMultiLevelCacheL3`.
- **M-1 — `MultiLevelCache.get_with_level()` ignoring `l1_enabled`/`l2_enabled`**
  (`src/cache/multi_level_cache.py`): the method now guards each sub-cache call
  behind the same `if self.l1_enabled` / `if self.l2_enabled` flags used by
  `get()`. Regression test `test_get_with_level_respects_disabled_flags` in
  `TestMultiLevelCache`.
- **N-1 — `SemanticCache.average_similarity_score()` / `reset_stats()` race**
  (`src/cache/semantic_cache.py`): `average_similarity_score()` now snapshots
  `_similarity_scores` under `self._lock` so a concurrent `reset_stats()` cannot
  clear the list between the emptiness guard and `sum()`. `reset_stats()` now
  performs both `_stats.reset()` and `_similarity_scores.clear()` atomically
  inside `with self._lock:`. Regression test
  `TestSemanticCacheAverageSimilarityLock::test_average_similarity_score_never_races_with_reset`.
- **N-2 — `SemanticCache.update_threshold()` unsynchronised write**
  (`src/cache/semantic_cache.py`): `update_threshold()` now acquires `self._lock`
  before assigning `self.similarity_threshold`, making the write consistent with
  the guarded reads in `get()` and `stats()`. Regression test
  `TestSemanticCacheUpdateThresholdLock::test_update_threshold_never_races_with_get`.
- **N-3 — `MultiLevelCache.enable_promotion()` / `disable_promotion()` unsynchronised writes**
  (`src/cache/multi_level_cache.py`): both methods now acquire `self._stats_lock`
  before writing `promote_l2_hits`. `stats()` snapshots the flag inside the same
  `with self._stats_lock:` block as the hit/miss counters so the returned
  `"promote_l2_hits"` value is consistent with the counters in the same snapshot.
  Regression test
  `TestMultiLevelCache::test_promotion_flag_consistent_in_stats_snapshot`.
- **N-4 — `stats()` double `size()` calls producing inconsistent snapshots**
  (`src/cache/exact_cache.py`, `src/cache/multi_level_cache.py`):
  `ExactCache.stats()` now snapshots `n = self.size()` once and reuses it for
  both `"size"` and `"utilization"`, eliminating the window where a concurrent
  eviction could make the two fields disagree. `MultiLevelCache.stats()` applies
  the same pattern via `l1_size` and `l2_size` locals. Regression tests
  `TestExactCacheStatsConsistency` and
  `TestMultiLevelCache::test_stats_l1_size_and_utilization_are_consistent`.
- **N-5 — advisory lock-order comment in `SemanticCache.stats()`**
  (`src/cache/semantic_cache.py`): added a 3-line comment above the
  `embedding_generator.cache_size()` call documenting that `self._lock` is held
  at that point and that `embedding_generator` must not re-acquire it.

### Security
- **STRIDE threat model** (Phase 7): [`docs/security/threat-model.md`](docs/security/threat-model.md)
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
  `docs/security/threat-model.md` is now canonical.

---

For more information, see the [README](README.md) and [documentation](docs/).
