# Architecture Documentation

**Last Updated:** 2026-07-25
**Status:** Beta — Not Production Ready — see [STATUS.md](../../STATUS.md). This page states no grade of its own; the previously stated "A+" was self-assessed and has been withdrawn.

---

## 🎯 Start Here

### For Complete System Understanding

**Primary Document:** [ARCHITECTURE.md](ARCHITECTURE.md)

This is the **master architecture reference** (v3.0, 2026-07-14) that explains:
- The dual system nature (Bob Shell KB Manager + Token Optimization System)
- Complete facade/factory/config architecture
- Component breakdown with source citations
- Cross-cutting invariants enforced by CI
- Quality attributes and performance targets

**Read this first** to understand the complete picture.

> ⚠️ `UNIFIED_ARCHITECTURE.md` and `ACTUAL_SYSTEM_ARCHITECTURE.md` are **deprecated**.
> They were removed from the tree on 2026-07-25 and remain recoverable from git history (see below).

---

## 📚 Quick Navigation

### Current Architecture Documentation

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** ⭐ — Master reference (authoritative, v3.0, 2026-07-14)
   - Dual system overview
   - Facade + factory + config architecture
   - Component breakdown with source citations
   - Cross-cutting invariants (single-home, layering, manifest-backed)
   - Deployment view and glossary

2. **[docs/adr/](../adr/)** — Architecture Decision Records (ADR-001 through ADR-019)
   - Key decisions: Python choice, caching strategy, TF-IDF, semantic similarity, monitoring, security
   - ADR-013: Facade/factory pattern (Phase-4 composition decision)
   - ADR-019: Delegation pipeline activation (analysis pipeline → KB ingestion)

> **mypy note (post G-2 gap closure, 2026-07-17):** `src/delegation/` and `src/tools/` are now fully included in the mypy scope — the previous `exclude` directive has been removed. `src/` type-checks clean (0 errors; only `[annotation-unchecked]` advisory notes for untyped function bodies remain, which are acceptable and not counted as errors).

3. **[docs/security/threat-model.md](../security/threat-model.md)** — STRIDE threat model
   - Trust boundaries and data flows
   - Mitigations with path:line citations
   - Residual risks and non-risks

### Deprecated Documentation

The original component specifications (13 documents, ~256 KB) described a planned
system that was largely **not implemented** — batch processing, a formatter layer
and an integration layer never existed, and cache/optimizer/truncation/monitoring
were built differently. They were removed from the working tree on 2026-07-25
rather than carried indefinitely as a parallel architecture no one maintained.

They remain in git history and are recoverable:

```bash
git log --diff-filter=D --name-only -- 'docs/architecture/deprecated/*'
git show c84b33d:docs/architecture/deprecated/BATCH.md
```

What replaced them is [`ARCHITECTURE.md`](ARCHITECTURE.md) — see its §2 component
overview and §5 per-component detail.

---

## 🗂️ Directory Structure

```
docs/architecture/
├── README.md          (this file)
├── ARCHITECTURE.md    ⭐ authoritative — components, dataflow, config→runtime
└── components/
    └── README.md      historical note on the superseded per-component specs
```

---

## ⚠️ Important Notes

### Superseded component specifications

The original plan described 8 components across 6 layers. What was built is a
facade + factory over 10 packages — simpler, and different enough that the old
specs were misleading rather than merely stale. They were removed on 2026-07-25
and remain in git history; see the *Deprecated Documentation* section above for
the recovery commands.

---

## 🚀 Getting Started

### For New Developers

**Step 1:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
- Understand the dual system nature
- Review the facade/factory composition model
- Check the cross-cutting invariants section

**Step 2:** Read system-specific documentation
- **Bob Shell KB Manager:** See [ARCHITECTURE.md §1](ARCHITECTURE.md#1-system-context)
- **Token Optimization System:** See [ARCHITECTURE.md §2](ARCHITECTURE.md#2-component-architecture)

**Step 3:** Review Architecture Decision Records
- See [docs/adr/](../adr/) for design decisions
- 19 ADRs covering key architectural choices

### For Maintainers

**Architecture Updates:**
1. Update [ARCHITECTURE.md](ARCHITECTURE.md) for any system changes
2. Create ADR in [docs/adr/](../adr/) for significant decisions
3. Update this README if directory structure changes
4. Run `scripts/generate_api_docs.py --check` to verify API doc sync

**Documentation Sync:**
- Keep code and docs in sync
- Update examples from actual source code
- Verify all links work
- Run validation scripts

---

## 📊 System Overview

### Bob Shell Knowledge Manager

**Purpose:** Lightweight documentation framework for Bob Shell  
**Technology:** Bash scripts, YAML configuration, Markdown templates  
**Complexity:** ~5,320 lines of Bash across 23 scripts  
**Status:** Stable (v1.0)

**Key Components:**
- Custom Bob Shell mode (`knowledge-manager`)
- 4 document templates
- 4 bash automation scripts
- Example knowledge bases

**Documentation:** See [ARCHITECTURE.md §1](ARCHITECTURE.md#1-system-context)

### Token Optimization System

**Purpose:** Reduce LLM token costs through caching and optimization  
**Technology:** Python 3.11+, tiktoken, scikit-learn, numpy  
**Complexity:** ~12,850 non-blank/non-comment lines across 67 modules (16,840 physical)  
**Status:** Beta — Not Production Ready — see [STATUS.md](../../STATUS.md); no grade is claimed here

**Key Components:**
- Multi-level caching (L1: exact, L2: semantic)
- Prompt optimization and token counting
- Text truncation strategies
- Monitoring and observability
- Unified `TokenOptimizer` facade + `bob-optimize` CLI

**Documentation:** See [ARCHITECTURE.md](ARCHITECTURE.md)

### Delegation Module (Analysis Pipeline)

**Purpose:** Parallel code repository analysis → KB ingestion
**Technology:** Python 3.11+, ThreadPoolExecutor
**Complexity:** ~1,588 lines
**Status:** Integrated — analysis pipeline (84% coverage, 70% floor; ADR-019)

**CLI:** `bob-optimize analyze <target> [--kb-path] [--output-dir] [--workers] [--depth] [--no-compress]`
**Documentation:** [src/delegation/experimental.md](../../src/delegation/EXPERIMENTAL.md) · [ADR-019](../adr/019-delegation-pipeline-activation.md)

---

## 🔗 Related Documentation

### Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Master reference (authoritative)
- **[docs/adr/](../adr/)** — Architecture Decision Records (ADR-001–019)
- **[docs/security/threat-model.md](../security/threat-model.md)** — STRIDE threat model

### Implementation

- **[docs/knowledge-base/guides/](../knowledge-base/guides/)** — Implementation guides
- **[docs/knowledge-base/research/](../knowledge-base/research/)** — Research notes
- **[docs/api/README.md](../api/README.md)** — Auto-generated API reference

### Project Management

- **[STATUS.md](../../STATUS.md)** — Canonical maturity status (single source of truth)
- **[docs/knowledge-base/guides/audit-remediation-status.md](../knowledge-base/guides/audit-remediation-status.md)** — Audit remediation

### User Documentation

- **[README.md](../../README.md)** — Project overview
- **[docs/quick-start.md](../quick-start.md)** — 5-minute guide
- **[docs/USAGE.md](../USAGE.md)** — Usage guide
- **[docs/MONITORING.md](../MONITORING.md)** — Monitoring guide

---

## 📈 Documentation Quality

### Current Status

**Accuracy (as of 2026-07-14):**
- `ARCHITECTURE.md`: authoritative (v3.0, verified against source)
- `docs/adr/`: 19 ADRs, principles in force; ADR-012 superseded; implementation-status notes on ADR-002–005 where class names evolved
- `THREAT_MODEL.md`: exemplary — STRIDE, grounded in code, path:line citations
- Deprecated docs: historical reference only

**Coverage:**
- Bob Shell KB Manager: complete
- Token Optimization System: complete
- Delegation Module: documented as experimental

**Maintenance:**
- Last major update: 2026-07-14 (architecture remediation — MECE audit)
- Next review: when significant architectural change is made (ADR required)

### Quality Standards

**All architecture documentation must:**
1. Accurately reflect the implemented system
2. Include code examples from actual source with path:line citations
3. Provide performance metrics (measured, not estimated)
4. Link to related documentation
5. Include version history

**Deprecated documentation must:**
1. Be clearly marked as deprecated
2. Explain why it was deprecated
3. Point to current documentation
4. Be moved to `deprecated/` folder

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0 | 2026-07-14 | Architecture remediation: nav hub fixed; deprecated docs moved; ARCHITECTURE.md v3.0 is now authoritative |
| 3.0 | 2026-07-13 | Phase 5: Created UNIFIED_ARCHITECTURE.md, moved deprecated component specs |
| 2.0 | 2026-07-12 | Created ACTUAL_SYSTEM_ARCHITECTURE.md, identified gaps |
| 1.0 | 2026-07-12 | Initial version with deprecation warnings |
| 0.x | 2026-06-XX | Original planned architecture (now deprecated) |

---

## 📞 Support

### Questions?

1. **Architecture Questions:** See [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Implementation Questions:** Check source code in `src/` or tests in `tests/`
3. **Design Decisions:** See [docs/adr/](../adr/)
4. **Security:** See [docs/security/threat-model.md](../security/threat-model.md)
5. **Status / Grade:** See [STATUS.md](../../STATUS.md)

### Contributing

When updating architecture documentation:
1. Update `ARCHITECTURE.md` first
2. Keep documentation in sync with code
3. Add examples from actual source code
4. Update this README if structure changes
5. Create ADR for significant decisions

---

**Authoritative architecture document:** [ARCHITECTURE.md](ARCHITECTURE.md) (v3.0)  
**Canonical status:** [STATUS.md](../../STATUS.md)  
**Maintainer:** Architecture Team
