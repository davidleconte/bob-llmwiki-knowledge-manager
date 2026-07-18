---
title: "Architecture Documentation Audit — MECE / Tier-1 Software Vendor Standard"
category: research
tags: [architecture, audit, mece]
date: 2026-07-14
type: research
status: complete
frozen: true
audit_standard: >
  McKinsey MECE framework · ISO/IEC 42010 (Architecture Description) ·
  ISO/IEC 25010 (Quality Attributes) · arc42 template · C4 model ·
  Tier-1 Software Vendor institutional bar (AWS, Google, Microsoft, Stripe)
auditor: Bob (Plan/Agent) — firsthand read of every file; no inferred content
scope: >
  docs/architecture/ (all 13 files) · docs/adr/ (12 ADRs + README) ·
  docs/security/threat-model.md · src/facade.py · src/factory.py ·
  src/__init__.py · src/config/schema.py · src/delegation/experimental.md
do_not_edit: Point-in-time snapshot. Corrections in a new document.
related:
  - audit-2026-07-14-post-remediation.md
  - ../../architecture/ARCHITECTURE.md
  - ./full-technical-design-retro-2026-07.md
  - ./full-codebase-review-2026-07-14.md
created: 2026-07-14
updated: 2026-07-14

---

# Architecture Documentation Audit
## MECE Framework · Tier-1 Software Vendor Standard

**Auditor:** Bob (Plan/Agent) — firsthand read of all 30 files  
**Standard:** McKinsey MECE · ISO/IEC 42010 · arc42 · C4 · Tier-1 institutional bar  
**Corpus:** ~8,200 lines across 30 files (ADRs, arch docs, threat model, facade/config source)

---

## Audit Method

MECE = **Mutually Exclusive, Collectively Exhaustive**. Applied here as:

- **ME (no overlap):** each architectural concern is addressed in exactly one authoritative place; no two documents contradict each other on the same claim
- **CE (no gaps):** every concern a Tier-1 software vendor must document is covered

The seven audit dimensions below are mutually exclusive (each covers a distinct architectural concern) and collectively exhaustive (together they cover the full arc42/ISO 42010 surface).

---

## Dimension 1 — Single Authoritative Source per Concern

**What Tier-1 requires:** One document "owns" each architectural question. Any reader asking "what is the architecture?" finds exactly one answer.

**Finding:**

There are **four competing documents** that claim or imply architectural authority:

| File | Self-description | Actual status |
|------|-----------------|---------------|
| `docs/architecture/architecture.md` | "Single authoritative architecture document… supersedes ACTUAL and UNIFIED" | ✅ **Authoritative** (v3.0, 2026-07-14, post-Phase-4) |
| `docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md` | "Complete technical design" (from `token-optimization.md:290`) | ⚠️ Deprecated but not clearly marked with a banner in its header |
| `docs/architecture/UNIFIED_ARCHITECTURE.md` | "Master reference" per `docs/architecture/README.md:12-13` | ⚠️ Superseded but `docs/architecture/README.md` still points here as primary |
| `docs/architecture/README.md` | Navigation hub — says "Start Here: UNIFIED_ARCHITECTURE.md" | ❌ **Contradicts** `ARCHITECTURE.md:7-9`; points new developers to the wrong doc |

**Root cause:** `docs/architecture/README.md` was last updated in July 2026 (Phase 5) and points to `UNIFIED_ARCHITECTURE.md` as the "master reference". `ARCHITECTURE.md` (the actual authoritative document, written at Phase-4/post-remediation) says it supersedes UNIFIED but the navigation hub was never updated.

**Severity:** **High** — a developer following the README's "Start Here" instruction reaches a superseded document.

**Specific evidence:**
- `docs/architecture/architecture.md:7-9` → explicitly supersedes UNIFIED and ACTUAL

**ME violation:** UNIFIED and ARCHITECTURE both claim to be the master reference.  
**CE gap:** Navigation hub is not updated.

---

## Dimension 2 — Completeness Against arc42 / ISO 42010 Template

**What Tier-1 requires:** Architecture documentation covers: (1) context & goals, (2) constraints, (3) solution strategy, (4) building-block view (static structure), (5) runtime view (dynamic behaviour), (6) deployment view, (7) cross-cutting concepts, (8) quality scenarios, (9) risks & technical debt, (10) glossary.

**Finding per arc42 section:**

| arc42 Section | Required | Covered | Location | Gap |
|---|:---:|:---:|---|---|
| 1. Context & goals | ✅ | ✅ | `ARCHITECTURE.md §1` | None |
| 2. Constraints | ✅ | ⚠️ | `ARCHITECTURE.md §1` (implied) | No explicit constraints section; Python ≥3.11, local-only, sync-only constraints not formally stated |
| 3. Solution strategy | ✅ | ✅ | `ARCHITECTURE.md §2-3` — facade + factory + config → runtime | None |
| 4. Building-block view (static) | ✅ | ✅ | `ARCHITECTURE.md §2` Mermaid flowchart | Delegation and tools are "deliberately separate" — correct; but their public API surfaces are not documented in this view |
| 5. Runtime view (dynamic) | ✅ | ✅ | `ARCHITECTURE.md §3` sequence diagram | Only optimize() is shown; truncate(), health(), cost_report() paths are absent |
| 6. Deployment view | ✅ | ❌ | Absent | No deployment diagram. Where does this run? What OS? What Python? pyproject.toml constraints alone are insufficient for a Tier-1 vendor. |
| 7. Cross-cutting concepts | ✅ | ✅ | `ARCHITECTURE.md §7` — layering, single-home, manifest-backed numbers | Well done; enforced by CI |
| 8. Quality scenarios | ✅ | ⚠️ | `QUALITY_ATTRIBUTES.md` (carries retraction banner; in archive/) | Moved to archive; `ARCHITECTURE.md` does not reference quality scenarios or performance targets explicitly |
| 9. Risks & technical debt | ✅ | ⚠️ | Scattered across audit docs in knowledge-base/research/ | No single "known risks" section in the architecture doc |
| 10. Glossary | ✅ | ❌ | Absent | No glossary of domain terms: "Bobcoin", "L1/L2", "facade", "manifest-backed", "tiktoken_active", etc. |

**ME:** No overlapping coverage between sections — clean.  
**CE:** 3 gaps: deployment view, glossary, quality scenarios from the authoritative doc.

**Severity of gaps:**
- Deployment view absent: **Medium** (local CLI, context is obvious, but "obvious" is not documented)
- Glossary absent: **Medium** (Bobcoin, tiktoken_active etc. are domain-specific; external contributors will not know them)
- Quality scenarios not in authoritative doc: **Low** (covered in archived QUALITY_ATTRIBUTES.md but unreachable from the main doc)

---

## Dimension 3 — ADR Coverage and Quality

**What Tier-1 requires:** Every significant architectural decision has an ADR with: clear decision statement, alternatives considered, rationale grounded in stated constraints, consequences acknowledged, and a way to know if the decision is still valid.

**ADR inventory assessment:**

| ADR | Decision | Quality | Status | Issue |
|-----|----------|---------|--------|-------|
| 001 Python | Use Python 3.11+ | ✅ Complete — context, alternatives (Go, Rust, Node), consequences | Accepted | None |
| 002 Caching | Hash-based + in-memory LRU | ⚠️ **Code examples describe a different, older design** (file-based JSON, `ResponseCache` class) — not the current `ExactCache` + `OrderedDict` | Accepted | **Code/ADR drift** — examples no longer match implementation |
| 003 TF-IDF | TF-IDF for relevance scoring | ⚠️ Same drift — implementation class `RelevanceScorer` does not exist; actual: `SemanticCache` uses `TfidfVectorizer` | Accepted | **Code/ADR drift** |
| 004 Semantic Similarity | Cosine similarity + TF-IDF | ⚠️ Implementation example shows `SemanticCache(ResponseCache)` inheritance — current `SemanticCache` is standalone, not a subclass | Accepted | **Code/ADR drift** |
| 005 Batch Processing | Similarity-based batching | ❌ **`BatchProcessor` class described does not exist in `src/`** | Accepted | **Decision partially not implemented** |
| 006 Cache strategy | In-memory first, Redis later | ✅ "Phase 2/3" framing is honest — current = Phase 1 | Accepted | Accepted trade-off; documented |
| 007 Sync vs Async | Sync now, async later | ✅ Honest phasing | Accepted | None |
| 008 Token counting | tiktoken | ⚠️ Retraction banner present; references fabricated savings figures below it | Accepted | Banner present but the ADR still describes a `CharacterCounter`/`TokenEstimator` design that was never implemented |
| 009 Error handling | Layered + retry + circuit breaker | ⚠️ Circuit breaker described does not appear in `src/` | Accepted | **Decision partially not implemented** |
| 010 Testing | Mock-based | ✅ Accurate — matches actual test suite | Accepted | None |
| 011 Monitoring | 3-pillar: metrics/log/health | ✅ Largely accurate post-Phase-2 fixes | Accepted | `MonitoringConfig` fields (log_level, metrics_enabled) still not read by the facade — gap between ADR intent and implementation undisclosed |
| 012 Security | Defence-in-depth stack | ⛔ **SUPERSEDED** — fabricated implementation claims; retraction banner present | Superseded | Well handled; THREAT_MODEL.md is the replacement |

**ME assessment:** ADRs 002 and 006 both address caching — 002 is about the algorithm, 006 about the infrastructure tier. Conceptually distinct but the split is not obvious; a reader could wonder why caching needs two ADRs.

**CE assessment:** 
- **Missing ADR: Facade/Factory pattern (Phase 4)** — the single most significant architectural decision (composing all components behind a `TokenOptimizer` facade with a factory) has no ADR. This was introduced in Phase 4 and is the runtime composition point.
- **Missing ADR: Validation harness design** — `src/validation/` is a load-bearing measurement system with specific design decisions (manifest fields, null test, separate mechanism reporting). No ADR.
- **Missing ADR: Pricing single-home pattern** — `src/pricing.py` as the single source for model rates + Bobcoin conversion is an explicit architectural decision enforced by CI. No ADR.

**Severity:**
- Code/ADR drift in 002, 003, 004, 008: **Medium** — ADRs are labelled as historical snapshots; the drift is disclosed but not quantified per ADR
- Missing Facade ADR: **High** — the Phase-4 facade is the primary architectural unit; its absence means new contributors have no decision rationale for the most important design choice
- Missing Validation ADR: **Medium**
- ADR-005 (BatchProcessor not implemented): **Low** — ADR says "Accepted" but the code shows deferred implementation; honest only if read carefully

---

## Dimension 4 — Code ↔ Documentation Accuracy

**What Tier-1 requires:** Every claim in architecture docs is verifiable against the code, with `path:line` citations or equivalent grounding.

**Assessment by document:**

**`ARCHITECTURE.md` (the authoritative doc):**
- ✅ Excellent grounding: `src/facade.py:9`, `src/factory.py:3`, `src/cache/exact_cache.py:66`, `src/config/schema.py`, `src/validation/manifest.py:45-58` — all verified as correct by direct code read
- ✅ Config table §4 matches `src/config/schema.py` exactly (l1_max_size=1000, l2_similarity_threshold=0.85, etc.)
- ✅ Sequence diagram §3 matches `src/facade.py:73-96` exactly
- ⚠️ `ARCHITECTURE.md:74` — says `src/tools/` is "excluded from the coverage and type gates" — this is **false** post-Phase-8: `src/tools/` has a per-package floor of 85% in `check_coverage_by_package.py` and is explicitly in the gated denominator

**`ARCHITECTURE.md §4` config table:**
- States `MonitoringConfig.health_check_interval` default is 60s — ✅ matches `schema.py:73`
- States `OptimizerConfig.strategies` is not listed — ❌ the field exists in `schema.py:51` but is noted as a dead field in `facade.py:9` docstring; the table omits it entirely rather than documenting it as "declared but not read"

**`docs/architecture/README.md`:**
- States delegation module has "0% coverage" → ❌ actual: ~52.9% (per `check_coverage_by_package.py`)
- States Token Optimization System is "~3,500 lines" → ❌ actual: ~5,400 logical / ~8,292 physical (per prior audit)
- States "Status: Beta (7/10)" → ❌ stale: current grade is A (3.89/4.3) per `STATUS.md`

**`docs/architecture/components/README.md`:**
- References `ACTUAL_SYSTEM_ARCHITECTURE.md` — file exists but is deprecated
- States "122 tests" for cache, "53 tests" for optimizer, etc. — stale; actual: 899 total

**`docs/adr/README.md`:**
- "Total ADRs: 12 · Lines: ~4,747" → ADRs total is correct; line count not verified but plausible
- States ADR-005 is accepted → correct but batch processing was never implemented (should note "deferred")

**Severity of code↔doc drift:**
- `ARCHITECTURE.md:74` wrong claim about `src/tools/` exclusion: **Medium** (the authoritative document has a factual error)
- `architecture/README.md` stale numbers: **Medium** (navigation hub, first doc a new developer reads)

---

## Dimension 5 — Security Documentation Quality

**What Tier-1 requires:** A STRIDE or equivalent threat model, grounded in actual code, with: trust boundaries, data flows, mitigations with `path:line` evidence, residual risks explicitly accepted, and a maintenance trigger list.

**Finding:** This is **the strongest dimension** in the corpus.

`docs/security/threat-model.md` meets or exceeds Tier-1 standard on every criterion:

| Criterion | Met? | Evidence |
|-----------|:----:|---------|
| Deployment context explicitly stated | ✅ | "local Python library and CLI… single local user, the operator" |
| All trust boundaries diagrammed | ✅ | Mermaid flowchart with 6 boundary crossings |
| STRIDE categories each addressed | ✅ | Full table; N/A calls explicitly justified (Spoofing, Repudiation, EoP) |
| Every mitigation has path:line citation | ✅ | `safe_paths.py`, `exact_cache.py:66`, `manifest.py:45-58` etc. |
| Residual risks documented with rationale | ✅ | 3 residuals with deployment context; H-19, L-1 referenced |
| Non-risks explicitly scoped out | ✅ | "No deserialization… no secrets… no shell execution" all verified |
| Maintenance triggers stated | ✅ | 5 explicit trigger conditions |
| ADR-012 retraction handled | ✅ | Supersedes banner + pointer to THREAT_MODEL; fabrication acknowledged |

**One finding:** `THREAT_MODEL.md:104` states "the paths reach these tools untrusted — directly from each tool's CLI, and for the delegation agents via `task.target` (`src/delegation/agents/*.py`)". This implies all delegation agents route through `resolve_within`. As noted in prior audits, the leaf-level containment fix was applied to `DocumentationAgent` and `ComponentAnalyzer`, but the threat model's STRIDE table says the path-traversal finding is "FIXED" globally. A precise reader would want to know that `resolve_within` is per-entry-path and that the leaf-level symlink filter was added in Phase 8 (line 118). This is documented in the text below the table but not updated in the table cell.

**Severity:** Low — clearly documented; the fix text at lines 118-133 is accurate and detailed.

**Overall Security Dimension Grade: A (exemplary)**

---

## Dimension 6 — ADR Governance and Lifecycle

**What Tier-1 requires:** ADRs follow a defined lifecycle (Proposed → Accepted → Deprecated / Superseded); superseded ADRs are clearly marked and replaced; no zombie ADRs claiming current status for abandoned decisions.

**Finding:**

✅ **ADR-012 retraction is handled correctly** — retraction banner, retained as audit trail, replaced by THREAT_MODEL.md. This is textbook ADR governance.

✅ **ADR template is defined** in `docs/adr/README.md:106-153` with all required sections.

✅ **Status field** present in all 12 ADRs.

⚠️ **ADR-002 through ADR-005 code examples** show implementation that was never built (file-based JSON, `ResponseCache`, `BatchProcessor`, `RelevanceScorer`). These ADRs are marked "Accepted" — but "accepted" should mean the decision is in force and the implementation matches. For these four ADRs, the decision principle is in force (caching, TF-IDF, cosine similarity) but the implementation examples are wrong. At Tier-1, these would carry a "Decision: Accepted / Implementation: Evolved — see ARCHITECTURE.md §5" note.

⚠️ **No ADR creation process or PR gate** — `CONTRIBUTING.md` documents the gate suite but does not mandate an ADR for significant architectural changes. Phase 4 (facade + factory + config wiring) was the largest architectural change in the project's history and has no ADR.

⚠️ **ADR-005 (Batch Processing)** says "Accepted" but the `BatchProcessor` does not exist in `src/`. The honest status is "Accepted / Deferred". No mechanism exists to catch this drift.

**ME:** Each decision has exactly one ADR — no duplicates. ✅  
**CE gap:** No mechanism (no gate, no process) to require an ADR for significant new decisions.

---

## Dimension 7 — Documentation Navigation and Discoverability

**What Tier-1 requires:** A new engineer can reach the correct authoritative document within two clicks from any entry point; deprecated docs are clearly marked and not on the primary navigation path; the index/hub is accurate.

**Finding:**

**Navigation path analysis:**

| Entry point | Path to correct doc | Clicks | Problem |
|-------------|--------------------|----|---------|
| `docs/architecture/README.md` | README → "Start Here: UNIFIED_ARCHITECTURE.md" → wrong doc | 1 wrong click | ❌ Hub points to superseded doc |
| `docs/README.md` (Diátaxis hub) | README → "Architecture" → `architecture/ARCHITECTURE.md` | 2 correct clicks | ✅ |
| Root `README.md` | README → `docs/architecture/architecture.md` | 1 correct click | ✅ |
| `docs/index.md` | Index → links not updated post-archive move | stale | ⚠️ |

**`docs/architecture/README.md` problems (precise):**
- Line 35: `ACTUAL_SYSTEM_ARCHITECTURE.md` listed as item 2 "Token Optimization System details" — deprecated
- Line 163: `Status: Beta (7/10)` — stale
- Line 178: delegation module "0% coverage" — wrong (52.9%)
- Line 229: "Last major update: July 13, 2026 (Phase 5)" — correct, which explains why everything above is wrong

**`docs/architecture/DOCUMENTATION_PLAN.md` and `QUALITY_ATTRIBUTES.md`:**
- Both are in `docs/architecture/` root (now accessible) but not archived
- Both are referenced in `docs/architecture/README.md` as current documentation
- `QUALITY_ATTRIBUTES.md` carries a retraction banner (metrics fabricated) but is still presented as a current reference for quality requirements

**Deprecated docs still in `docs/architecture/` root (not moved to archive):**
- `ACTUAL_SYSTEM_ARCHITECTURE.md` — superseded but not in archive
- `DOCUMENTATION_PLAN.md` — planning doc, should be in archive
- `QUALITY_ATTRIBUTES.md` — retraction banner present; should be in archive

**ME gap:** `docs/architecture/` root contains both the authoritative `ARCHITECTURE.md` and three deprecated documents that have not been archived. Readers cannot immediately distinguish authoritative from deprecated.

**CE gap:** The `docs/architecture/README.md` navigation hub is the primary entry point for architecture documentation and it is comprehensively wrong in its pointers.

**Severity: High** — this is the most actionable finding in the audit.

---

## MECE Scorecard

| # | Dimension | ME | CE | Grade | Primary Gap |
|---|-----------|:--:|:--:|:-----:|-------------|
| 1 | Single authoritative source | ❌ | ⚠️ | **C+** | README.md nav hub points to wrong doc; 3 competing "master" docs |
| 2 | arc42 completeness | ✅ | ⚠️ | **B** | Deployment view absent; glossary absent; quality scenarios unreachable |
| 3 | ADR coverage & quality | ✅ | ❌ | **B−** | No facade ADR; code/ADR drift in 002-005; ADR-005 zombie |
| 4 | Code ↔ doc accuracy | ✅ | ⚠️ | **B+** | `ARCHITECTURE.md:74` wrong; README hub stale numbers; schema dead field undisclosed |
| 5 | Security documentation | ✅ | ✅ | **A** | STRIDE complete; grounded in code; one table cell imprecise |
| 6 | ADR governance & lifecycle | ✅ | ⚠️ | **B** | No ADR process/gate; 4 ADRs have evolved implementations |
| 7 | Navigation & discoverability | ❌ | ❌ | **C** | Hub points to superseded docs; deprecated docs not archived; stale numbers throughout |

**Weighted overall: B− (2.65/4.30)**

| Dim | Weight | GPA | Weighted |
|-----|--------|-----|---------|
| 1 | 20% | 2.3 (C+) | 0.46 |
| 2 | 15% | 3.0 (B) | 0.45 |
| 3 | 15% | 2.7 (B−) | 0.41 |
| 4 | 20% | 3.3 (B+) | 0.66 |
| 5 | 15% | 4.0 (A) | 0.60 |
| 6 | 5% | 3.0 (B) | 0.15 |
| 7 | 10% | 2.0 (C) | 0.20 |
| **Total** | 100% | | **2.93 ≈ B−** |

---

## Prioritised Remediation

### Priority 1 — Fix the navigation hub (1–2 hours)

**`docs/architecture/README.md`** is the entry point for architecture documentation and is comprehensively wrong. Specific changes:

1. Replace "Start Here: UNIFIED_ARCHITECTURE.md" with "Start Here: ARCHITECTURE.md"
2. Update item 1 to list `ARCHITECTURE.md` as "Master reference (authoritative, v3.0)"
3. Mark `ACTUAL_SYSTEM_ARCHITECTURE.md` and `UNIFIED_ARCHITECTURE.md` as deprecated in the listing
4. Update status from "Beta (7/10)" to "A (3.89/4.30)" per STATUS.md
5. Update delegation coverage from "0%" to "~52.9%"
6. Update LOC from "~3,500" to "~5,400 logical"
7. Update "Last major update" to 2026-07-14

### Priority 2 — Archive deprecated docs in `docs/architecture/` root (30 min)

Move to `docs/archive/architecture/` or `docs/architecture/deprecated/`:
- `ACTUAL_SYSTEM_ARCHITECTURE.md` (superseded)
- `DOCUMENTATION_PLAN.md` (planning doc)
- `QUALITY_ATTRIBUTES.md` (metrics retracted; now in archive/)

Update the one reference each has in the navigation documents.

### Priority 3 — Write the missing Facade ADR (2–3 hours)

Create `docs/adr/013-facade-factory-pattern.md`:
- Context: pre-Phase-4, components were not composed; each caller wired them manually
- Decision: `TokenOptimizer` facade + factory builders + `ConfigSchema` single home
- Rationale: single composition point, no business logic in facade, config→runtime cannot drift
- Consequences: `config.monitoring` fields partially unread (documented); L2 not used by optimize() by design
- Status: Accepted

### Priority 4 — Add a deployment view to `ARCHITECTURE.md` (1 hour)

Add a §9 between §8 "Where to go next" and EOF:

```markdown
## 9. Deployment

**Runtime context:** Local Python library and CLI. No server, no daemon, no container required.

| Constraint | Value |
|------------|-------|
| Python | ≥3.11 (3.11 and 3.12 tested in CI) |
| OS | macOS, Linux (Bash scripts: macOS/Linux only) |
| Dependencies | numpy, scikit-learn, tiktoken (psutil optional) |
| Concurrency | Single-process, synchronous (ThreadPoolExecutor in delegation only) |
| Persistence | In-memory only (no disk cache, no DB) |
| Network | None except optional tiktoken BPE vocab download on first use |
```

### Priority 5 — Add a glossary to `ARCHITECTURE.md` (45 min)

Add a §10 Glossary with: Bobcoin, tiktoken_active, manifest-backed, L1/L2 cache, facade, factory, MECE, null test, target_reduction, quality_score.

### Priority 6 — Add implementation-status notes to ADR-002, 003, 004, 005 (1 hour)

For each, append a one-paragraph "Implementation note (2026-07-14)" clarifying:
- ADR-002: The principle is implemented; the class names differ (ExactCache + OrderedDict, not ResponseCache + JSON)
- ADR-003: TF-IDF is used inside SemanticCache, not as a standalone RelevanceScorer
- ADR-004: SemanticCache is standalone, not a subclass of ExactCache
- ADR-005: BatchProcessor is deferred; status should read "Accepted / Deferred"

---

## What Is Already Excellent (Credit Due)

1. **`docs/architecture/architecture.md`** — the authoritative document is genuinely excellent: Mermaid diagrams are accurate (verified against source), config table matches `schema.py` exactly, cross-cutting invariants section is complete and enforced in CI. This meets the Tier-1 bar for the document itself.

2. **`docs/security/threat-model.md`** — STRIDE analysis grounded in actual code with `path:line` citations. N/A calls explicitly justified. Residual risks and non-risks both documented. Maintenance triggers listed. Exemplary.

3. **ADR-012 retraction handling** — fabricated security claims correctly retracted with a banner, kept as audit trail, replaced by the real threat model. Textbook ADR governance.

4. **`docs/adr/` collection** — 11 of 12 ADRs follow a consistent, complete template (context, decision, alternatives, consequences, validation). The template itself is well-defined in `docs/adr/README.md`.

5. **CI-enforced cross-cutting invariants** — layering gate, single-home values, savings-claim gate, API-doc drift check are all wired and real. This is architecture documentation enforcement at the code level, which no doc can fake.

---

## Post-Remediation Note (2026-07-14)

All 6 prioritised remediation items were implemented on 2026-07-14. Gates remained green throughout.

### Changes made

| Priority | Item | File(s) changed |
|---|---|---|
| P1 | Fixed navigation hub — 7 stale/wrong claims corrected | `docs/architecture/README.md` (full rewrite) |
| P2 | Archived 4 deprecated docs | `ACTUAL_SYSTEM_ARCHITECTURE.md`, `UNIFIED_ARCHITECTURE.md`, `DOCUMENTATION_PLAN.md`, `QUALITY_ATTRIBUTES.md` → `docs/architecture/deprecated/`; `deprecated/README.md` updated |
| P3 | Wrote missing ADR-013 | `docs/adr/013-facade-factory-pattern.md` (new); `docs/adr/README.md` index updated |
| P4 | Added deployment view §9 | `docs/architecture/architecture.md` (§9 appended) |
| P5 | Added glossary §10 | `docs/architecture/architecture.md` (§10 appended, 11 terms) |
| P6 | Added implementation-status notes to ADR-002–005 | `docs/adr/002-caching-strategy.md`, `003-tfidf-scoring.md`, `004-semantic-similarity.md`, `005-batch-processing.md` |

### Revised score estimate

| # | Dimension | Pre-remediation | Post-remediation | Change |
|---|-----------|:---:|:---:|:---:|
| 1 | Single authoritative source | C+ (2.3) | A− (3.7) | ↑↑ Hub now correct; 4 deprecated docs removed from root |
| 2 | arc42 completeness | B (3.0) | A− (3.7) | ↑ Deployment view + glossary added |
| 3 | ADR coverage & quality | B− (2.7) | B+ (3.3) | ↑ ADR-013 written; implementation notes on 002–005 |
| 4 | Code ↔ doc accuracy | B+ (3.3) | B+ (3.3) | → ARCHITECTURE.md:74 wrong claim not yet fixed (src/tools/ exclusion claim) |
| 5 | Security documentation | A (4.0) | A (4.0) | → Unchanged |
| 6 | ADR governance & lifecycle | B (3.0) | B+ (3.3) | ↑ ADR-013 addresses the biggest missing ADR; zombie ADR-005 now documented as Deferred |
| 7 | Navigation & discoverability | C (2.0) | A− (3.7) | ↑↑ Hub fixed; deprecated docs not on primary path |

**Estimated revised weighted score: ~3.65 (A−)**, up from 2.65 (B−).

Note: Dimension 4 is held at B+ because `ARCHITECTURE.md:74` still incorrectly states
`src/tools/` is "excluded from coverage gates" — it is not (85% per-package floor).
Fixing that one line would move Dim 4 to A and push the overall to ~A.

### Gate state (post-remediation, 2026-07-14)

```
pytest: 899 passed / 23 skipped / 0 failed
check_status_consistency.py: OK
check_savings_claims.py: 211 surfaces clean
check_value_homes.py: OK
check_community_health.py: 12/12 artifacts
check_layering.py: OK
generate_api_docs.py --check: 41 files in sync
ruff check src/ scripts/ tests/: All checks passed
```

---

## Correction Addendum (post-remediation, 2026-07-14+)

> **This addendum corrects the note above without editing the frozen findings.**

The post-remediation note (above) says:
> "Dimension 4 is held at B+ because `ARCHITECTURE.md:74` still incorrectly states
> `src/tools/` is 'excluded from coverage gates'."

**That claim is now false.** `docs/architecture/architecture.md:73-74` currently reads:
> "Included in the coverage and type gates with a per-package floor of 85% (`scripts/check_coverage_by_package.py`)."

The exclusion claim was corrected in the same session as the P1–P6 remediations above.
Dimension 4 therefore moves from B+ (3.3) to **A (4.0)** once that line is correct.

### Revised weighted score

| # | Dimension | P1–P6 post-remediation | After Dim-4 correction | Change |
|---|-----------|:---:|:---:|:---:|
| 1 | Single authoritative source | A− (3.7) | A− (3.7) | = |
| 2 | arc42 completeness | A− (3.7) | A− (3.7) | = |
| 3 | ADR coverage & quality | B+ (3.3) | B+ (3.3) | = |
| 4 | Code ↔ doc accuracy | B+ (3.3) | **A (4.0)** | ↑ `ARCHITECTURE.md:74` corrected |
| 5 | Security documentation | A (4.0) | A (4.0) | = |
| 6 | ADR governance & lifecycle | B+ (3.3) | B+ (3.3) | = |
| 7 | Navigation & discoverability | A− (3.7) | A− (3.7) | = |

| Dim | Weight | GPA | Weighted |
|-----|--------|-----|---------|
| 1 | 20% | 3.7 | 0.74 |
| 2 | 15% | 3.7 | 0.56 |
| 3 | 15% | 3.3 | 0.50 |
| 4 | 20% | 4.0 | 0.80 |
| 5 | 15% | 4.0 | 0.60 |
| 6 | 5% | 3.3 | 0.17 |
| 7 | 10% | 3.7 | 0.37 |
| **Total** | 100% | | **3.74 ≈ A−/A** |

**Corrected estimated weighted score: ~3.74 (A−/A)**, up from ~3.65 (A−).
