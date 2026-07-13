# Architecture Documentation

**Last Updated:** July 13, 2026  
**Status:** Phase 5 Complete - Documentation Reconciled

---

## 🎯 Start Here

### For Complete System Understanding

**Primary Document:** [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md)

This is the **master architecture reference** that explains:
- The dual system nature (Bob Shell KB Manager + Token Optimization System)
- Complete architecture for both systems
- Repository structure and organization
- Development guidelines
- Documentation map

**Read this first** to understand the complete picture.

---

## 📚 Quick Navigation

### Current Architecture Documentation

1. **[UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md)** - Master reference for entire repository
   - Explains dual system architecture
   - Bob Shell Knowledge Manager overview
   - Token Optimization System complete architecture
   - Repository structure and guidelines

2. **[ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md)** - Token Optimization System details
   - 3-layer architecture (Cache, Optimizer, Truncation)
   - Component specifications with code examples
   - Performance characteristics
   - Testing strategy
   - Deployment guide

3. **[QUALITY_ATTRIBUTES.md](QUALITY_ATTRIBUTES.md)** - Quality requirements
   - Performance targets
   - Reliability requirements
   - Security considerations
   - Maintainability goals

4. **[DOCUMENTATION_PLAN.md](DOCUMENTATION_PLAN.md)** - Documentation strategy
   - Documentation structure
   - Update procedures
   - Quality standards

---

## 🗂️ Directory Structure

```
docs/architecture/
├── README.md (this file)
├── UNIFIED_ARCHITECTURE.md          ⭐ START HERE
├── ACTUAL_SYSTEM_ARCHITECTURE.md    📖 Token Optimization System
├── QUALITY_ATTRIBUTES.md
├── DOCUMENTATION_PLAN.md
├── components/
│   └── README.md                    ↪️  Redirects to deprecated/
└── deprecated/
    ├── README.md                    ⚠️  Historical reference
    ├── MASTER.md                    ❌ Original 6-layer plan
    ├── BATCH.md                     ❌ Not implemented
    ├── CACHE.md                     ❌ Implemented differently
    ├── FORMATTER.md                 ❌ Not implemented
    ├── INTEGRATION.md               ❌ Not implemented
    ├── MONITORING.md                ❌ Implemented differently
    ├── OPTIMIZER.md                 ❌ Implemented differently
    └── TRUNCATION.md                ❌ Implemented differently
```

---

## ⚠️ Important Notes

### Deprecated Documentation

**Location:** [deprecated/](deprecated/)

Contains **5,534 lines** of original architecture specifications that describe a planned system that was **NOT implemented**.

**Why Deprecated:**
- Original plan: 8 components, 6 layers
- Actual implementation: 11 components, 3 layers
- Documentation accuracy: ~15% (critical mismatch)

**Do NOT use these documents** for understanding the current system. They are kept for historical reference only.

See [deprecated/README.md](deprecated/README.md) for details.

### Component Documentation

**Location:** [components/](components/)

This directory now contains only a README that redirects to either:
- Current documentation (ACTUAL_SYSTEM_ARCHITECTURE.md)
- Deprecated documentation (deprecated/)

All original component specifications have been moved to deprecated/.

---

## 🚀 Getting Started

### For New Developers

**Step 1:** Read [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md)
- Understand the dual system nature
- Choose which system you're working on

**Step 2:** Read system-specific documentation
- **Bob Shell KB Manager:** See [UNIFIED_ARCHITECTURE.md Section 2](UNIFIED_ARCHITECTURE.md#2-bob-shell-knowledge-manager)
- **Token Optimization System:** See [ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md)

**Step 3:** Review Architecture Decision Records
- See [docs/adr/](../adr/) for design decisions
- 12 ADRs covering key architectural choices

### For Maintainers

**Architecture Updates:**
1. Update [ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md) for Token Optimization System changes
2. Update [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) for cross-system changes
3. Create ADR in [docs/adr/](../adr/) for significant decisions
4. Update this README if structure changes

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
**Complexity:** ~500 lines  
**Status:** Stable (v1.0)

**Key Components:**
- Custom Bob Shell mode (`knowledge-manager`)
- 4 document templates
- 4 bash automation scripts
- Example knowledge bases

**Documentation:** See [UNIFIED_ARCHITECTURE.md Section 2](UNIFIED_ARCHITECTURE.md#2-bob-shell-knowledge-manager)

### Token Optimization System

**Purpose:** Reduce LLM token costs through caching and optimization  
**Technology:** Python 3.11+, tiktoken, scikit-learn, numpy  
**Complexity:** ~3,500 lines  
**Status:** Beta (7/10) - Not Production Ready

**Key Components:**
- Multi-level caching (L1: exact, L2: semantic)
- Prompt optimization and token counting
- Text truncation strategies
- Monitoring and observability

**Documentation:** See [ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md)

### Delegation Module (Experimental)

**Purpose:** Parallel code repository analysis  
**Technology:** Python 3.11+, ThreadPoolExecutor  
**Complexity:** ~1,588 lines  
**Status:** Experimental (0% coverage, not integrated)

**Documentation:** See [src/delegation/EXPERIMENTAL.md](../../src/delegation/EXPERIMENTAL.md)

---

## 🔗 Related Documentation

### Architecture

- **[UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md)** - Master reference
- **[ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md)** - Token Optimization System
- **[docs/adr/](../adr/)** - Architecture Decision Records (12 ADRs)

### Implementation

- **[docs/knowledge-base/guides/](../knowledge-base/guides/)** - Implementation guides
- **[docs/knowledge-base/research/](../knowledge-base/research/)** - Research notes
- **[docs/api/README.md](../api/README.md)** - Auto-generated API reference

### Project Management

- **[docs/project-management/PROJECT_STATUS.md](../project-management/PROJECT_STATUS.md)** - Current status
- **[docs/project-management/phases/](../project-management/phases/)** - Phase documentation
- **[docs/knowledge-base/guides/audit-remediation-status.md](../knowledge-base/guides/audit-remediation-status.md)** - Audit remediation

### User Documentation

- **[README.md](../../README.md)** - Project overview
- **[docs/QUICK_START.md](../QUICK_START.md)** - 5-minute guide
- **[docs/USAGE.md](../USAGE.md)** - Usage guide
- **[docs/MONITORING.md](../MONITORING.md)** - Monitoring guide

---

## 📈 Documentation Quality

### Current Status

**Accuracy:**
- UNIFIED_ARCHITECTURE.md: 100% (newly created)
- ACTUAL_SYSTEM_ARCHITECTURE.md: 95% (verified Week 19)
- Deprecated docs: ~15% (historical reference only)

**Coverage:**
- Bob Shell KB Manager: Complete
- Token Optimization System: Complete
- Delegation Module: Documented as experimental

**Maintenance:**
- Last major update: July 13, 2026 (Phase 5)
- Next review: Phase 6 (real-world validation)

### Quality Standards

**All architecture documentation must:**
1. Accurately reflect implemented system
2. Include code examples from actual source
3. Provide performance metrics (measured, not estimated)
4. Link to related documentation
5. Include version history

**Deprecated documentation must:**
1. Be clearly marked as deprecated
2. Explain why it was deprecated
3. Point to current documentation
4. Be moved to deprecated/ folder

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2026-07-13 | Phase 5: Created UNIFIED_ARCHITECTURE.md, moved deprecated docs |
| 2.0 | 2026-07-12 | Created ACTUAL_SYSTEM_ARCHITECTURE.md, identified gaps |
| 1.0 | 2026-07-12 | Initial version with deprecation warnings |
| 0.x | 2026-06-XX | Original planned architecture (now deprecated) |

---

## 📞 Support

### Questions?

1. **Architecture Questions:** See [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) or [ACTUAL_SYSTEM_ARCHITECTURE.md](ACTUAL_SYSTEM_ARCHITECTURE.md)
2. **Implementation Questions:** Check source code in `src/` or tests in `tests/`
3. **Design Decisions:** See [docs/adr/](../adr/)
4. **Gap Analysis:** See [docs/knowledge-base/research/external-audit-2026-07-12.md](../knowledge-base/research/external-audit-2026-07-12.md)

### Contributing

When updating architecture documentation:
1. Update ACTUAL_SYSTEM_ARCHITECTURE.md or UNIFIED_ARCHITECTURE.md first
2. Keep documentation in sync with code
3. Add examples from actual source code
4. Update this README if structure changes
5. Create ADR for significant decisions

---

**Current Status:** Phase 5 Complete - Documentation Reconciled  
**Next Update:** Phase 6 - Add real-world validation results  
**Maintainer:** Architecture Team
