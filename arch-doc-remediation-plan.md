# Architecture Documentation Remediation Plan

**Goal:** Bring `docs/architecture/` documentation from B− (2.65/4.30) to A by fixing the navigation hub, archiving deprecated docs, writing the missing facade ADR, and completing the arc42 template gaps in `ARCHITECTURE.md`.

**Scope:** 6 sub-tasks, all in `docs/architecture/` and `docs/adr/`. No source code changes. No test changes.

**Audit source:** `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md`

**Gates that must stay green after each sub-task:**
- `scripts/check_status_consistency.py`
- `scripts/check_savings_claims.py`
- `scripts/check_value_homes.py`
- `scripts/check_community_health.py`
- `scripts/check_layering.py`
- `scripts/generate_api_docs.py --check`
- `ruff check src/ scripts/ tests/`

---

## Sub-Task 1 — Fix the Navigation Hub

**Status:** [ ] pending

**Intent:** `docs/architecture/README.md` is the entry point for architecture documentation. It currently points to `UNIFIED_ARCHITECTURE.md` as "START HERE" — a superseded document. A new developer following this hub reaches the wrong doc. This is the highest-severity finding from the audit.

**Expected Outcomes:**
- "Start Here" section points to `ARCHITECTURE.md` (not `UNIFIED_ARCHITECTURE.md`)
- `UNIFIED_ARCHITECTURE.md` and `ACTUAL_SYSTEM_ARCHITECTURE.md` are listed as deprecated in the nav
- Status shows A (3.89/4.30) instead of "Beta (7/10)"
- Delegation coverage shows ~52.9% instead of "0%"
- LOC shows ~5,400 logical instead of ~3,500
- "UNIFIED_ARCHITECTURE.md: 100% accurate" claim removed
- "Last major update" updated to 2026-07-14

**Todo List:**
1. Read `docs/architecture/README.md` in full to identify all 7 stale/wrong claims
2. Replace "Start Here" block (lines 8–21): change primary document reference from `UNIFIED_ARCHITECTURE.md` to `ARCHITECTURE.md`
3. Update Quick Navigation (lines 25–51): list `ARCHITECTURE.md` as item 1 "Master reference (authoritative, v3.0)"; demote `UNIFIED_ARCHITECTURE.md` and `ACTUAL_SYSTEM_ARCHITECTURE.md` with "(deprecated)" labels
4. Update Directory Structure diagram (lines 55–76): add `ARCHITECTURE.md` as `⭐ START HERE`; mark `UNIFIED_ARCHITECTURE.md` and `ACTUAL_SYSTEM_ARCHITECTURE.md` as `⚠️ Deprecated`
5. Update "Getting Started" section: replace all `UNIFIED_ARCHITECTURE.md` references with `ARCHITECTURE.md`
6. Update "Maintainers" section: remove instruction to update `UNIFIED_ARCHITECTURE.md`
7. Update Token Optimization System status from "Beta (7/10)" to "A (3.89/4.30) — see STATUS.md"
8. Update delegation coverage from "0%" to "~52.9%"
9. Update LOC from "~3,500 lines" to "~5,400 logical lines"
10. Remove "UNIFIED_ARCHITECTURE.md: 100% (newly created)" accuracy claim; replace with "ARCHITECTURE.md: authoritative (v3.0, 2026-07-14)"
11. Update "Last major update" to 2026-07-14
12. Update ADR count from "12 ADRs" to "13 ADRs" (after sub-task 3 adds ADR-013) — note: do this step last, after sub-task 3

**Relevant Context:**
- File: `docs/architecture/README.md`
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 1 and Dimension 7
- Authoritative doc: `docs/architecture/ARCHITECTURE.md` (v3.0, 2026-07-14)
- Grade source: `STATUS.md` line 11

---

## Sub-Task 2 — Archive Deprecated Docs from `docs/architecture/` Root

**Status:** [ ] pending

**Intent:** Four files in `docs/architecture/` root are superseded or fabrication-retracted but remain on the primary navigation path alongside the authoritative `ARCHITECTURE.md`. Readers cannot immediately distinguish authoritative from deprecated. Moving them to `docs/architecture/deprecated/` eliminates the ambiguity.

**Expected Outcomes:**
- `docs/architecture/deprecated/` contains 4 new files
- `docs/architecture/` root contains only: `README.md`, `ARCHITECTURE.md`, `components/`, `deprecated/`
- Each moved file has a deprecation banner at the top pointing to the current authoritative document
- All references to these files in `docs/architecture/README.md` and `docs/architecture/components/README.md` are updated
- `docs/architecture/deprecated/README.md` updated to list the 4 new additions

**Todo List:**
1. Read `docs/architecture/deprecated/README.md` to understand existing deprecated file list
2. Read `docs/architecture/components/README.md` to find any references to the 4 files being moved
3. Move `ACTUAL_SYSTEM_ARCHITECTURE.md` to `docs/architecture/deprecated/ACTUAL_SYSTEM_ARCHITECTURE.md`; prepend a deprecation banner: "⚠️ DEPRECATED — Superseded by ARCHITECTURE.md (v3.0). This file is retained as historical reference only."
4. Move `UNIFIED_ARCHITECTURE.md` to `docs/architecture/deprecated/UNIFIED_ARCHITECTURE.md`; prepend same banner
5. Move `DOCUMENTATION_PLAN.md` to `docs/architecture/deprecated/DOCUMENTATION_PLAN.md`; prepend banner: "⚠️ DEPRECATED — Planning document for phases that are now complete. Retained for historical reference."
6. Move `QUALITY_ATTRIBUTES.md` to `docs/architecture/deprecated/QUALITY_ATTRIBUTES.md`; ensure existing retraction banner is preserved; add archive note
7. Update `docs/architecture/deprecated/README.md` to list the 4 new entries with brief descriptions
8. Update `docs/architecture/README.md` Directory Structure diagram to reflect the moves (will already be partially done in sub-task 1)

**Relevant Context:**
- Files to move: `docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md`, `UNIFIED_ARCHITECTURE.md`, `DOCUMENTATION_PLAN.md`, `QUALITY_ATTRIBUTES.md`
- Destination: `docs/architecture/deprecated/`
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 7 — "Deprecated docs still in root"
- Existing deprecated dir: `docs/architecture/deprecated/` (already has 7 component specs)

---

## Sub-Task 3 — Write Missing ADR-013 (Facade/Factory Pattern)

**Status:** [ ] pending

**Intent:** The Phase-4 `TokenOptimizer` facade + factory pattern is the single most significant architectural decision in the project's history (it is the runtime composition point for all subsystems), yet it has no ADR. Every other major decision (Python version, caching algorithm, TF-IDF, etc.) has one. This gap means new contributors have no documented rationale for the most central design choice.

**Expected Outcomes:**
- `docs/adr/013-facade-factory-pattern.md` exists and follows the ADR template from `docs/adr/README.md`
- Covers: context (pre-Phase-4 manual wiring), decision (TokenOptimizer facade + factory + ConfigSchema), alternatives considered, rationale, consequences (including the known partial gap: `MonitoringConfig` fields not yet read by facade), status: Accepted
- `docs/adr/README.md` ADR index updated to list ADR-013
- Code references cite actual source: `src/facade.py`, `src/factory.py`, `src/config/schema.py`

**Todo List:**
1. Read `docs/adr/README.md` to get the exact ADR template format
2. Read `docs/adr/012-security-considerations.md` as a quality example (the most recently written ADR)
3. Read `src/facade.py` to get accurate code references for the ADR
4. Read `src/factory.py` to get accurate code references
5. Read `src/config/schema.py` to get accurate config class references
6. Write `docs/adr/013-facade-factory-pattern.md` following the template exactly, with:
   - Context: pre-Phase-4, callers wired components manually; no single composition point; config not wired to runtime
   - Decision: `TokenOptimizer` facade delegates to subsystems; `factory.py` maps config → constructors; `ConfigSchema` is the single home for defaults
   - Alternatives considered: (a) no facade — callers compose directly; (b) dependency injection container; (c) service locator
   - Rationale: single composition point, no business logic leaks into facade, config→runtime cannot drift, testable without end-to-end harness
   - Consequences: `MonitoringConfig.log_level` and `metrics_enabled` not yet read by facade (documented gap); L2 cache not used in `optimize()` path by design (cost/latency trade-off)
   - Status: Accepted
7. Update `docs/adr/README.md` ADR index table to add ADR-013 entry

**Relevant Context:**
- Template: `docs/adr/README.md` lines 106–153
- Quality reference: any of ADR-001 through ADR-011
- Primary source files: `src/facade.py`, `src/factory.py`, `src/config/schema.py`
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 3 — "Missing ADR: Facade/Factory pattern"

---

## Sub-Task 4 — Add Deployment View §9 to `ARCHITECTURE.md`

**Status:** [ ] pending

**Intent:** arc42 requires a deployment view. `ARCHITECTURE.md` currently ends at §8. Adding §9 closes the most critical arc42 gap: the deployment context (local CLI, no server, no container, sync-only) is currently implicit and not formally stated anywhere in the authoritative architecture document.

**Expected Outcomes:**
- `ARCHITECTURE.md` has a §9 Deployment section between §8 and EOF
- Section covers: runtime context, Python version, OS support, dependencies, concurrency model, persistence, network requirements
- All facts are verifiable against `pyproject.toml` and source code (no invented constraints)

**Todo List:**
1. Read `docs/architecture/ARCHITECTURE.md` to find the current last section (§8) and exact EOF
2. Read `pyproject.toml` to verify Python floor, dependency names, and optional deps
3. Read `src/facade.py` to confirm sync-only, no async
4. Read `.github/workflows/ci.yml` to confirm which OS and Python versions are tested
5. Write §9 with a constraints table: Python ≥3.11 (3.11+3.12 in CI), OS (macOS + Linux), deps (numpy, scikit-learn, tiktoken; psutil optional), concurrency (single-process synchronous; ThreadPoolExecutor in delegation only), persistence (in-memory only), network (none except tiktoken BPE vocab download on first use)
6. Insert the section before EOF in `ARCHITECTURE.md`

**Relevant Context:**
- File: `docs/architecture/ARCHITECTURE.md`
- arc42 §6 requirement: deployment view
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 2 — "Deployment view absent"
- Data sources: `pyproject.toml`, `.github/workflows/ci.yml`, `src/facade.py`

---

## Sub-Task 5 — Add Glossary §10 to `ARCHITECTURE.md`

**Status:** [ ] pending

**Intent:** arc42 requires a glossary. Domain-specific terms used throughout the architecture documentation (Bobcoin, tiktoken_active, manifest-backed, L1/L2, facade, factory, null test, target_reduction, quality_score, MECE) are undefined. External contributors and auditors encounter them without explanation.

**Expected Outcomes:**
- `ARCHITECTURE.md` has a §10 Glossary section after §9
- Glossary defines at minimum: Bobcoin, tiktoken_active, manifest-backed, L1 cache, L2 cache, facade, factory, null test, target_reduction, quality_score
- All definitions are grounded in actual code (cite source file where the term originates)

**Todo List:**
1. Read `docs/architecture/ARCHITECTURE.md` to confirm §9 was added (sub-task 4) and find exact insertion point
2. Collect term definitions from source:
   - Bobcoin: `src/pricing.py` — what it is, the formula
   - tiktoken_active: `src/optimizer/token_counter.py` — what it means when false
   - manifest-backed: `src/validation/manifest.py` — what the manifest records
   - L1/L2: `src/cache/exact_cache.py`, `src/cache/semantic_cache.py`
   - facade: `src/facade.py`
   - factory: `src/factory.py`
   - null test: `src/validation/` — what it tests
   - target_reduction / quality_score: config schema or optimizer
3. Write §10 Glossary as a definition list or table, with one source citation per term
4. Append to `ARCHITECTURE.md` after §9

**Relevant Context:**
- File: `docs/architecture/ARCHITECTURE.md`
- arc42 §10 requirement: glossary
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 2 — "Glossary absent"
- Term sources: `src/pricing.py`, `src/optimizer/token_counter.py`, `src/validation/manifest.py`, `src/cache/`, `src/config/schema.py`

---

## Sub-Task 6 — Add Implementation-Status Notes to ADR-002, 003, 004, 005

**Status:** [ ] pending

**Intent:** ADRs 002–005 describe implementation details (class names, file structures, inheritance hierarchies) that reflect what was planned, not what was built. The principles are in force, but the code examples are wrong. At Tier-1, an ADR marked "Accepted" implies the implementation matches. Adding a one-paragraph "Implementation note (2026-07-14)" to each ADR makes the drift explicit, preserves the historical rationale, and prevents new contributors from being misled.

**Expected Outcomes:**
- `docs/adr/002-caching-strategy.md` has an appended Implementation note clarifying that the principle is implemented as `ExactCache` + `OrderedDict`, not `ResponseCache` + JSON file
- `docs/adr/003-tfidf-relevance.md` has an appended note clarifying TF-IDF is used inside `SemanticCache`, not as a standalone `RelevanceScorer`
- `docs/adr/004-semantic-similarity.md` has an appended note clarifying `SemanticCache` is standalone (not a subclass of `ExactCache`)
- `docs/adr/005-batch-processing.md` has an appended note clarifying `BatchProcessor` is deferred; status effectively "Accepted / Deferred"
- No existing ADR content is altered — notes are appended only

**Todo List:**
1. Read `docs/adr/002-caching-strategy.md` to find current content and last line
2. Read `docs/adr/003-tfidf-relevance.md`
3. Read `docs/adr/004-semantic-similarity.md`
4. Read `docs/adr/005-batch-processing.md`
5. Read `src/cache/exact_cache.py` class definition to get accurate class names for the ADR-002 note
6. Read `src/cache/semantic_cache.py` class definition for ADR-003 and ADR-004 notes
7. Verify `src/` has no `BatchProcessor` class (confirm it's deferred, not just renamed) for ADR-005 note
8. Append implementation note to ADR-002 citing `src/cache/exact_cache.py` and `src/cache/multi_level_cache.py`
9. Append implementation note to ADR-003 citing `src/cache/semantic_cache.py`
10. Append implementation note to ADR-004 citing `src/cache/semantic_cache.py`
11. Append implementation note to ADR-005 noting deferred status

**Relevant Context:**
- Files: `docs/adr/002-caching-strategy.md`, `003-tfidf-relevance.md`, `004-semantic-similarity.md`, `005-batch-processing.md`
- Audit findings: `architecture-audit-mece-2026-07-14.md` Dimension 3 and Dimension 6
- Source truth: `src/cache/exact_cache.py`, `src/cache/semantic_cache.py`, `src/cache/multi_level_cache.py`

---

## Post-Completion

After all 6 sub-tasks are done:
1. Run the full gate suite to confirm all green
2. Update `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` — add a "Post-remediation" section noting completion date and revised score estimate
3. Update STATUS.md Roadmap line to remove architecture docs from remaining gaps
4. Consider updating overall grade from A (3.89/4.30) toward A+ if the remediation closes the F dimension gap
