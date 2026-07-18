# Component Documentation

**Status:** Redirects to current documentation
**Date:** July 13, 2026 (last updated: July 18, 2026)
**Reason:** Original component specifications described a planned system that was not implemented

---

## ⚠️ IMPORTANT: Documentation Has Moved

All component specifications have been **moved to the deprecated folder** because they describe a planned system that was **NOT implemented**.

### Where to Find Current Documentation

**For the authoritative architecture:** See [ARCHITECTURE.md](../ARCHITECTURE.md)

This document covers:
- **§2:** Component overview (cache, optimizer, truncator, monitoring, KB subsystems)
- **§3:** Runtime dataflow (facade → factory → components)
- **§3b:** KB query dataflow (embeddings P2, graph P3, query quality P4)
- **§4:** Configuration → runtime wiring (`ConfigSchema` → factory → constructors)
- **§5:** Per-component details (Cache, KB Embedding Index, Knowledge Graph, Optimizer, Truncation, Monitoring, Pricing)
- **§6:** Validation harness (`python -m src.validation`)
- **§7:** Cross-cutting invariants (CI-enforced)
- **§8:** Quality scenarios

---

## Deprecated Documentation

Original component specifications (5,534 lines total) have been moved to:

**Location:** [deprecated/](../deprecated/)

**Contents:**
- BATCH.md (828 lines) — Batch processing (not implemented)
- CACHE.md (670 lines) — Original cache design (implemented differently)
- FORMATTER.md (750 lines) — Format control (not implemented)
- INTEGRATION.md (858 lines) — Integration layer (not implemented)
- MONITORING.md (873 lines) — Original monitoring (implemented differently)
- OPTIMIZER.md (698 lines) — Original optimizer (implemented differently)
- TRUNCATION.md (751 lines) — Original truncation (implemented differently)

**Why Deprecated:** See [deprecated/README.md](../deprecated/README.md)

---

## Quick Navigation

### Current Architecture

1. **System Overview:** [ARCHITECTURE.md](../ARCHITECTURE.md) — authoritative, v3.0
2. **Cache Layer:** [ARCHITECTURE.md §5](../ARCHITECTURE.md#5-components) — `src/cache/`
3. **KB Embedding Index:** [ARCHITECTURE.md §5](../ARCHITECTURE.md#5-components) — `src/embeddings/`
4. **Knowledge Graph:** [ARCHITECTURE.md §5](../ARCHITECTURE.md#5-components) — `src/graph/`
5. **Optimizer Layer:** [ARCHITECTURE.md §5](../ARCHITECTURE.md#5-components) — `src/optimizer/`
6. **Truncation Layer:** [ARCHITECTURE.md §5](../ARCHITECTURE.md#5-components) — `src/truncation/`
7. **Monitoring:** [docs/MONITORING.md](../../MONITORING.md)
8. **Delegation Pipeline:** [ARCHITECTURE.md §2](../ARCHITECTURE.md#2-component-overview) — `src/delegation/`

### Source Code (current test counts — see `pytest tests/ -v` for live counts)

- **Cache:** `src/cache/` (5 modules)
- **Embeddings:** `src/embeddings/` (4 modules — P2 KB index)
- **Graph:** `src/graph/` (4 modules — P3 knowledge graph)
- **Optimizer:** `src/optimizer/` (2 modules)
- **Truncation:** `src/truncation/` (2 modules)
- **Monitoring:** `src/monitoring/` (5 modules)
- **Delegation:** `src/delegation/` (pipeline + 6 agents — ADR-019)

### Architecture Decisions

- **ADRs:** [docs/adr/](../../adr/) (ADR-001 through ADR-019; ADR-012 superseded)
- **Design Rationale:** See individual ADRs for component decisions

---

## What Changed?

### Original Plan (Week 18)
- 8 components across 6 layers
- Complex orchestration
- Format validation
- Batch processing

### Actual Implementation
- 14 packages (`cache`, `config`, `delegation`, `embeddings`, `graph`, `monitoring`, `optimizer`, `tools`, `truncation`, `validation` + facade/factory/cli/pricing at root)
- Facade + factory composition pattern (ADR-013)
- Layered architecture with clean `src/ → scripts/` boundary
- KB subsystems: persistent embedding index (P2), knowledge graph (P3), query quality (P4)
- Delegation analysis pipeline (ADR-019): 6 parallel agents → TokenOptimizer → KB ingestion

**Result:** Simpler, faster, more maintainable system than the original plan

---

## Related Documentation

- **Current Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md) — authoritative, v3.0
- **Deprecated Specs:** [deprecated/](../deprecated/)
- **Gap Analysis:** [docs/knowledge-base/research/external-audit-2026-07-12.md](../../knowledge-base/research/external-audit-2026-07-12.md)

---

**Last Updated:** July 18, 2026
**Maintained By:** Architecture Team
**Purpose:** Redirect to current documentation