# Deprecated Architecture Documentation

**Status:** Historical Reference Only
**Last Updated:** 2026-07-14
**Reason:** Documents describe planned system that was not implemented, or have been superseded by `ARCHITECTURE.md` (v3.0)

---

## ⚠️ WARNING: DO NOT USE THESE DOCUMENTS

These documents describe the **original planned architecture** from Week 18, which was **NOT implemented** in Week 19.

**Accuracy:** ~15% (critical mismatch with actual implementation)

---

## What's Here

### Superseded Architecture Documents (moved 2026-07-14)

**ACTUAL_SYSTEM_ARCHITECTURE.md** — Superseded by `ARCHITECTURE.md` v3.0 (2026-07-14)
- Was: detailed Token Optimization System architecture with code examples
- Now: `ARCHITECTURE.md` is the single authoritative document

**UNIFIED_ARCHITECTURE.md** — Superseded by `ARCHITECTURE.md` v3.0 (2026-07-14)
- Was: "master reference" for the dual system
- Now: `ARCHITECTURE.md` covers both systems with accurate Phase-4 + facade/factory model

**DOCUMENTATION_PLAN.md** — Planning document for phases now complete
- Was: documentation strategy for Phases 1–5
- Retraction: cites fabricated savings figures; see `STATUS.md` for current numbers

**QUALITY_ATTRIBUTES.md** — Retraction banner present; metrics fabricated
- Was: quality attribute specifications with "68.96%" / "89.3%" savings figures
- Retraction: those figures were produced by a simulation that never invoked the optimizer; actual measured figure is ~20% compression (see `STATUS.md`)

---

### Original Architecture Plan (Not Implemented)

**MASTER.md** - 6-layer architecture specification
- Planned: 8 components across 6 layers
- Actual: 11 components across 3 layers
- Mismatch: Completely different design

### Component Specifications (Not Implemented)

1. **BATCH.md** (828 lines) - Batch processing with similarity grouping
   - Status: Not implemented
   - Reason: Deferred to future phases

2. **CACHE.md** (670 lines) - Original cache design
   - Status: Partially implemented differently
   - Actual: See `ACTUAL_SYSTEM_ARCHITECTURE.md` Section 2

3. **FORMATTER.md** (750 lines) - Format control system
   - Status: Not implemented
   - Reason: Out of scope for Week 19

4. **INTEGRATION.md** (858 lines) - Integration layer
   - Status: Not implemented
   - Reason: Simplified to direct component usage

5. **MONITORING.md** (873 lines) - Original monitoring design
   - Status: Implemented differently in Week 20
   - Actual: See `src/monitoring/` and `docs/monitoring.md`

6. **OPTIMIZER.md** (698 lines) - Original optimizer design
   - Status: Partially implemented differently
   - Actual: See `ACTUAL_SYSTEM_ARCHITECTURE.md` Section 3

7. **TRUNCATION.md** (751 lines) - Original truncation design
   - Status: Partially implemented differently
   - Actual: See `ACTUAL_SYSTEM_ARCHITECTURE.md` Section 4

---

## Why Deprecated?

### Original Plan (Week 18)
- **Scope:** 8 components, 6 layers
- **Complexity:** High (orchestration layer, format validation, batch processing)
- **Timeline:** 4 weeks
- **Risk:** High (too ambitious)

### Actual Implementation (Week 19)
- **Scope:** 11 components, 3 layers
- **Complexity:** Medium (focused on core functionality)
- **Timeline:** 2 weeks
- **Risk:** Low (proven patterns)

### Key Differences

| Aspect | Planned | Actual |
|--------|---------|--------|
| Layers | 6 | 3 |
| Components | 8 | 11 |
| Lines of Code | ~5,000 (est.) | 2,533 |
| Test Coverage | Unknown | 87% |
| Architecture | Complex orchestration | Simple layered |
| Batch Processing | Yes | No (deferred) |
| Format Validation | Yes | No (deferred) |
| Integration Layer | Yes | No (direct usage) |

---

## What to Use Instead

### For Current Architecture

**Primary Document:** [ARCHITECTURE.md](../ARCHITECTURE.md) (v3.0, 2026-07-14)

This is the **single authoritative architecture document** covering:
- Facade + factory + config composition model
- Component breakdown with `path:line` citations
- Cross-cutting invariants enforced by CI
- Deployment view and glossary

### For Specific Components

**Cache System:** See `ARCHITECTURE.md §2` and `src/cache/`
- ExactCache (L1) — SHA-256 hash-based
- SemanticCache (L2) — TF-IDF similarity
- MultiLevelCache — L1+L2 orchestration

**Optimizer System:** See `ARCHITECTURE.md §2` and `src/optimizer/`
- TokenCounter — tiktoken + fallback
- PromptOptimizer — compression strategies

**Truncation System:** See `ARCHITECTURE.md §2` and `src/truncation/`
- 4 truncation strategies
- Truncator — auto-selection

**Monitoring System:** See `docs/monitoring.md` and `src/monitoring/`
- Structured logging (JSON)
- Metrics collection
- Health checks

---

## Historical Context

These documents were created during Week 18 planning phase as part of the initial system design. They represent the **aspirational architecture** before implementation constraints were understood.

**Lessons Learned:**
1. Start simple, add complexity later
2. Validate assumptions early
3. Keep documentation in sync with code
4. Prefer working code over perfect design

---

## Related Documentation

- **Current Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md) (authoritative, v3.0)
- **Architecture Decisions:** [docs/adr/](../../adr/)
- **Canonical Status:** [STATUS.md](../../../STATUS.md)
- **Gap Analysis:** [docs/knowledge-base/research/external-audit-2026-07-12.md](../../knowledge-base/research/external-audit-2026-07-12.md)

---

**Last Updated:** 2026-07-14
**Maintained By:** Architecture Team
**Purpose:** Historical reference and lessons learned
