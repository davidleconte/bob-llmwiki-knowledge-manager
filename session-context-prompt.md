# Context prompt for next session
# Copy the block below and paste it as the first message in a new Bob Shell session.
# ---

---

## Project: bob-llmwiki-knowledge-manager

**Repository:** `~/Projects/bob-llmwiki-knowledge-manager`  
**Branch:** `fix-multilevel-cache-race`  
**Last worked:** 2026-07-14  
**Mode:** Plan → Agent (read architecture docs, investigate before acting, never speculate)

---

## What this repo is

Two independent systems in one repository:

| System | Technology | Status |
|--------|-----------|--------|
| **Bob Shell Knowledge Manager** | Bash scripts, YAML, Markdown | Stable v1.0 |
| **Python Token Optimization System** (`src/`) | Python 3.11+, tiktoken, scikit-learn | Beta — Not Production Ready |

They are **not integrated**. The Python system is composed behind a `TokenOptimizer` facade (`src/facade.py:37`) and `bob-optimize` CLI. Architecture: `docs/ARCHITECTURE.md` (KB Manager, arc42 v2.0) and `docs/architecture/ARCHITECTURE.md` (Python system, arc42 v3.0).

---

## Current grade: A (3.89 / 4.30) — authoritative in `STATUS.md`

Trajectory: D− (0.9) → B+/A− (3.46) → A− (3.70) → **A (3.89)**

| Dimension | Grade |
|-----------|:-----:|
| Product Integrity & Claims | **A** |
| Architecture & Design | A− |
| Code Correctness | **A** |
| Testing & Verification | A− |
| Build, Release & Supply-Chain | **A** |
| Documentation | **A** |
| Governance & Compliance | A− |

**Remaining gaps (from `STATUS.md:12`):**
- **B** — dead `OptimizerConfig.strategies` field: declared in `src/config/schema.py:51`, not read by `src/factory.py` → `PromptOptimizer`
- **D** — delegation agent coverage frozen at 52% floor (intentional; `scripts/check_coverage_by_package.py`)
- **G** — TOCTOU window in path-traversal is unnamed in `docs/security/THREAT_MODEL.md` residual register

---

## What was completed this session (do not redo)

All of the following are **done and gate-green**. Read the files, do not re-implement.

### Architecture documentation (all 6 priorities from `arch-doc-remediation-plan.md`)
- P1: `docs/architecture/README.md` rewritten — nav hub now points to `ARCHITECTURE.md` (v3.0), 7 stale claims fixed
- P2: 4 deprecated docs moved to `docs/architecture/deprecated/` via `git mv`
- P3: `docs/adr/013-facade-factory-pattern.md` written — full ADR for Phase-4 facade/factory
- P4+P5: `docs/architecture/ARCHITECTURE.md` extended with §9 Deployment + §10 Glossary
- P6: Implementation-status notes appended to ADR-002, 003, 004, 005
- Bonus: `ARCHITECTURE.md:74` wrong `src/tools/` coverage exclusion claim corrected

### Knowledge Manager architecture document (new, arc42 v2.0)
- `docs/ARCHITECTURE.md` rewritten to 612-line Tier-1 document: 13 sections, 8+ Mermaid diagrams, 5 inline ADRs, quality scenarios, risk register, glossary. All grounded in actual script code.

### All `docs/` documents elevated to Tier-1 arc42 standard
- `docs/MONITORING.md` — B→A: 3 Mermaid diagrams, 4 inline ADRs, quality scenarios
- `docs/INSTALLATION.md` — C→A: state diagram, 2 sequence diagrams (install.sh, init-project.sh), failure-modes table
- `docs/QUICK_START.md` — C→A: onboarding flowchart, stale PHASE3 link removed
- `docs/USAGE.md` — C→A: §0 "Starting a Session" added, 4 Mermaid diagrams
- `docs/CUSTOMIZATION.md` — C→A: config resolution chain, annotated YAML, KB contract flowchart
- `docs/WORKFLOWS.md` — D→A: 5 Mermaid workflow flowcharts, anti-patterns, quality scenarios

### README replacement
- `README4.md` reviewed, 4 fixes applied, copied to `README.md`
- `README.md` is now the live README — `README4.md` is the preserved source copy

### Session activation design (3 deliverables)
- `scripts/start-kb.sh` — new 51-line session launcher (daily driver)
- `scripts/init-project.sh` — enhanced: generates `CONTEXT.md`, fixes `$(date)` heredoc bug, updates `yourusername` link
- `docs/USAGE.md §0` — "Starting a Session" with Mermaid flowchart, 4 activation paths, standard resume prompt
- `docs/knowledge-base/guides/activating-knowledge-manager-in-new-session.md` — rewritten with diagrams and all 4 paths
- `docs/ARCHITECTURE.md` — updated: `start-kb.sh` in component table + directory structure, `CONTEXT.md` in runtime layout, 3 new glossary terms

---

## Gate state (all green, last verified 2026-07-14)

```
pytest: 899 passed / 23 skipped / 0 failed   (via: uv run pytest tests/ -q --tb=no)
check_status_consistency.py: OK
check_savings_claims.py: 211 surfaces clean
check_value_homes.py: OK
check_community_health.py: 12/12 artifacts
check_layering.py: OK
generate_api_docs.py --check: 41 files in sync
ruff check src/ scripts/ tests/: All checks passed
```

Run all at once:
```bash
python3 scripts/check_status_consistency.py && \
python3 scripts/check_savings_claims.py && \
python3 scripts/check_value_homes.py && \
python3 scripts/check_community_health.py && \
python3 scripts/check_layering.py && \
python3 scripts/generate_api_docs.py --check && \
ruff check src/ scripts/ tests/ && \
echo "ALL GATES GREEN"
```

Tests (requires uv):
```bash
uv run pytest tests/ -q --tb=no
```

---

## Key authoritative files (read these before touching anything)

| File | What it is |
|------|-----------|
| `STATUS.md` | Single source of truth for grade + remaining gaps |
| `docs/architecture/ARCHITECTURE.md` | Authoritative Python system architecture (arc42 v3.0, §1–10) |
| `docs/ARCHITECTURE.md` | Authoritative KB Manager architecture (arc42 v2.0, 13 sections) |
| `docs/adr/013-facade-factory-pattern.md` | Newest ADR — Phase-4 facade/factory composition |
| `src/facade.py` | Primary composition point; holds no business logic |
| `src/factory.py` | Single home for config → constructor mapping |
| `src/config/schema.py` | Single home for config defaults (CacheConfig, OptimizerConfig, MonitoringConfig) |
| `src/pricing.py` | Single home for model rates and Bobcoin conversion |
| `docs/security/THREAT_MODEL.md` | STRIDE threat model (exemplary; supersedes retracted ADR-012) |
| `evaluation/results/validation-2026-07-14/manifest.json` | Provenance for all ~20% savings claims |
| `pyproject.toml` | Single home for version, Python floor, coverage gate (≥80%) |
| `scripts/check_coverage_by_package.py` | Per-package coverage floors (monitoring 70%, delegation 52%, validation 85%, tools 85%) |

---

## Key design invariants (enforce always)

1. **One home per value** — version, Python floor, pricing, coverage gate, maturity status each have one canonical source. `scripts/check_value_homes.py` enforces this.
2. **Manifest-backed numbers** — every published savings/cost percentage must cite `evaluation/results/validation-2026-07-14/manifest.json` on the same line. `scripts/check_savings_claims.py` enforces this.
3. **Layering** — `src/` never imports from `scripts/`. `scripts/check_layering.py` enforces this.
4. **STATUS.md is authoritative** — any maturity claim in any other file must match it.
5. **No speculation** — read the file before claiming anything about code. Never invent a class name, line number, or behaviour.

---

## Open items / possible next work

These are genuinely open — nothing is planned or in progress:

| Priority | Item | Where |
|----------|------|-------|
| Low | Close dimension B gap: remove or wire `OptimizerConfig.strategies` dead field | `src/config/schema.py:51`, `src/factory.py` |
| Low | Name the TOCTOU window explicitly in the threat model residual register | `docs/security/THREAT_MODEL.md` |
| Low | Post-remediation note on arch audit doc estimated score B−→A− needs updating to reflect `src/tools/` fix | `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` |
| — | Commit all changes on `fix-multilevel-cache-race` branch and open PR | — |

---

## Starting this session

You are in **Plan mode**. Load the `create-plan` skill first. Read files before making any claims.
The canonical first prompt after reading this context:

> "What is the current state of the project and what should we work on next?"

Bob will read `STATUS.md`, scan the open items above, and propose a focused next task.
