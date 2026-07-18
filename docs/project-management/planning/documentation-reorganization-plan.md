---
title: "Documentation Reorganization Plan (Historical)"
date: 2026-07-12
status: historical
category: planning
note: "Reorganization plan from 2026-07-12. Executed across Phases 1–8."
---

# Documentation Reorganization Plan

**Date:** 2026-07-12  
**Status:** Proposed  
**Purpose:** Improve organization and discoverability of 39 root-level markdown files

---

## Current State Analysis

### File Inventory (39 .md files at root)

**Architecture Documentation (9 files):**
- ARCHITECTURE_MASTER.md
- ARCHITECTURE_QUALITY_ATTRIBUTES.md
- ARCHITECTURE_DOCUMENTATION_PLAN.md
- ARCHITECTURE_CACHE.md
- ARCHITECTURE_OPTIMIZER.md
- ARCHITECTURE_FORMATTER.md
- ARCHITECTURE_TRUNCATION.md
- ARCHITECTURE_BATCH.md
- ARCHITECTURE_INTEGRATION.md
- ARCHITECTURE_MONITORING.md

**Architecture Decision Records (12 files):**
- ADR-001-python-choice.md
- ADR-002-caching-strategy.md
- ADR-003-tfidf-scoring.md
- ADR-004-semantic-similarity.md
- ADR-005-batch-processing.md
- ADR-006-cache-strategy.md
- ADR-007-sync-vs-async.md
- ADR-008-token-counting.md
- ADR-009-error-handling.md
- ADR-010-testing-strategy.md
- ADR-011-monitoring-observability.md
- ADR-012-security-model.md

**Project Management (10 files):**
- PHASE_1_IMPLEMENTATION_SUMMARY.md
- PHASE_2_IMPLEMENTATION_PLAN.md
- PHASE_3_EXECUTIVE_SUMMARY.md
- PHASE_3_IMPLEMENTATION_PLAN.md
- PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md
- PROJECT_STATUS.md
- BEST_PRACTICES_IMPLEMENTATION_PLAN.md
- MOCK_DATA_AUTOMATION.md
- MOCK_DATA_QUALITY_ANALYSIS.md
- LLM_OPTIMIZATION_COMPLETE_SUMMARY.md

**Review & Validation (5 files):**
- WEEK18_FINAL_VALIDATION_REPORT.md
- WEEK2_DAILY_CHECKLIST.md
- HANDOFF_PROMPT.md
- ADVERSARIAL_REVIEW_NEXT_STEPS.md

**Root Documentation (3 files):**
- README.md
- CHANGELOG.md
- INDEX.md

### Problems with Current Structure

1. **Discoverability:** 39 files at root level is overwhelming
2. **Navigation:** Hard to find specific document types
3. **Maintenance:** Difficult to manage related documents
4. **Scalability:** Adding more docs will worsen the problem
5. **Context:** Related documents are not grouped together

---

## Proposed Directory Structure

```
bob-llmwiki-knowledge-manager/
├── README.md                          # Keep at root
├── CHANGELOG.md                       # Keep at root
├── INDEX.md                           # Keep at root (master index)
│
├── docs/
│   ├── architecture/                  # Architecture documentation
│   │   ├── README.md                  # Architecture overview
│   │   ├── MASTER.md                  # Renamed from ARCHITECTURE_MASTER.md
│   │   ├── QUALITY_ATTRIBUTES.md      # Renamed from ARCHITECTURE_QUALITY_ATTRIBUTES.md
│   │   ├── DOCUMENTATION_PLAN.md      # Renamed from ARCHITECTURE_DOCUMENTATION_PLAN.md
│   │   │
│   │   └── components/                # Component specifications
│   │       ├── README.md              # Components overview
│   │       ├── CACHE.md               # Renamed from ARCHITECTURE_CACHE.md
│   │       ├── OPTIMIZER.md           # Renamed from ARCHITECTURE_OPTIMIZER.md
│   │       ├── FORMATTER.md           # Renamed from ARCHITECTURE_FORMATTER.md
│   │       ├── TRUNCATION.md          # Renamed from ARCHITECTURE_TRUNCATION.md
│   │       ├── BATCH.md               # Renamed from ARCHITECTURE_BATCH.md
│   │       ├── INTEGRATION.md         # Renamed from ARCHITECTURE_INTEGRATION.md
│   │       └── MONITORING.md          # Renamed from ARCHITECTURE_MONITORING.md
│   │
│   ├── adr/                           # Architecture Decision Records
│   │   ├── README.md                  # ADR index and guidelines
│   │   ├── 001-python-choice.md       # Renamed (remove ADR- prefix)
│   │   ├── 002-caching-strategy.md
│   │   ├── 003-tfidf-scoring.md
│   │   ├── 004-semantic-similarity.md
│   │   ├── 005-batch-processing.md
│   │   ├── 006-cache-strategy.md
│   │   ├── 007-sync-vs-async.md
│   │   ├── 008-token-counting.md
│   │   ├── 009-error-handling.md
│   │   ├── 010-testing-strategy.md
│   │   ├── 011-monitoring-observability.md
│   │   └── 012-security-model.md
│   │
│   ├── project-management/            # Project planning and tracking
│   │   ├── README.md                  # Project management overview
│   │   ├── PROJECT_STATUS.md          # Current status
│   │   │
│   │   ├── phases/                    # Implementation phases
│   │   │   ├── PHASE_1_IMPLEMENTATION_SUMMARY.md
│   │   │   ├── PHASE_2_IMPLEMENTATION_PLAN.md
│   │   │   ├── PHASE_3_EXECUTIVE_SUMMARY.md
│   │   │   ├── PHASE_3_IMPLEMENTATION_PLAN.md
│   │   │   └── PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md
│   │   │
│   │   ├── planning/                  # Planning documents
│   │   │   ├── BEST_PRACTICES_IMPLEMENTATION_PLAN.md
│   │   │   ├── LLM_OPTIMIZATION_COMPLETE_SUMMARY.md
│   │   │   ├── MOCK_DATA_AUTOMATION.md
│   │   │   └── MOCK_DATA_QUALITY_ANALYSIS.md
│   │   │
│   │   └── reviews/                   # Review and validation
│   │       ├── WEEK2_DAILY_CHECKLIST.md
│   │       ├── WEEK18_FINAL_VALIDATION_REPORT.md
│   │       ├── ADVERSARIAL_REVIEW_NEXT_STEPS.md
│   │       └── HANDOFF_PROMPT.md
│   │
│   └── knowledge-base/                # Existing knowledge base (keep as-is)
│       └── ...
│
├── config/                            # Existing config (keep as-is)
├── evaluation/                        # Existing evaluation (keep as-is)
├── examples/                          # Existing examples (keep as-is)
├── scripts/                           # Existing scripts (keep as-is)
└── tests/                             # Existing tests (keep as-is)
```

---

## Benefits of Proposed Structure

### 1. Improved Discoverability
- **Before:** 39 files at root, hard to find anything
- **After:** 4 clear categories with logical grouping

### 2. Better Navigation
- **Before:** Scroll through long list of files
- **After:** Navigate by category, then drill down

### 3. Easier Maintenance
- **Before:** Related docs scattered at root
- **After:** Related docs grouped together

### 4. Scalability
- **Before:** Adding docs makes root more cluttered
- **After:** New docs go into appropriate category

### 5. Clear Context
- **Before:** No indication of document relationships
- **After:** Directory structure shows relationships

### 6. Professional Organization
- **Before:** Looks like a dumping ground
- **After:** Looks like a well-organized project

---

## Migration Strategy

### Phase 1: Create Directory Structure (5 minutes)

```bash
# Create new directories
mkdir -p docs/architecture/components
mkdir -p docs/adr
mkdir -p docs/project-management/phases
mkdir -p docs/project-management/planning
mkdir -p docs/project-management/reviews
```

### Phase 2: Move Architecture Files (10 minutes)

```bash
# Move master architecture docs
mv ARCHITECTURE_MASTER.md docs/architecture/deprecated/MASTER.md
mv ARCHITECTURE_QUALITY_ATTRIBUTES.md docs/architecture/QUALITY_ATTRIBUTES.md
mv ARCHITECTURE_DOCUMENTATION_PLAN.md docs/architecture/DOCUMENTATION_PLAN.md

# Move component specs
docs/architecture/deprecated/
mv ARCHITECTURE_OPTIMIZER.md docs/architecture/components/OPTIMIZER.md
mv ARCHITECTURE_FORMATTER.md docs/architecture/components/FORMATTER.md
mv ARCHITECTURE_TRUNCATION.md docs/architecture/components/TRUNCATION.md
mv ARCHITECTURE_BATCH.md docs/architecture/components/BATCH.md
mv ARCHITECTURE_INTEGRATION.md docs/architecture/components/INTEGRATION.md
mv ARCHITECTURE_MONITORING.md docs/architecture/components/MONITORING.md
```

### Phase 3: Move ADR Files (10 minutes)

```bash
# Move ADRs (rename to remove ADR- prefix)
mv ADR-001-python-choice.md docs/adr/001-python-choice.md
mv ADR-002-caching-strategy.md docs/adr/002-caching-strategy.md
mv ADR-003-tfidf-scoring.md docs/adr/003-tfidf-scoring.md
mv ADR-004-semantic-similarity.md docs/adr/004-semantic-similarity.md
mv ADR-005-batch-processing.md docs/adr/005-batch-processing.md
mv ADR-006-cache-strategy.md docs/adr/006-cache-strategy.md
mv ADR-007-sync-vs-async.md docs/adr/007-sync-vs-async.md
mv ADR-008-token-counting.md docs/adr/008-token-counting.md
mv ADR-009-error-handling.md docs/adr/009-error-handling.md
mv ADR-010-testing-strategy.md docs/adr/010-testing-strategy.md
mv ADR-011-monitoring-observability.md docs/adr/011-monitoring-observability.md
mv ADR-012-security-model.md docs/adr/012-security-model.md
```

### Phase 4: Move Project Management Files (10 minutes)

```bash
# Move phase documents
mv PHASE_1_IMPLEMENTATION_SUMMARY.md docs/project-management/phases/
mv PHASE_2_IMPLEMENTATION_PLAN.md docs/project-management/phases/
mv PHASE_3_EXECUTIVE_SUMMARY.md docs/project-management/phases/
mv PHASE_3_IMPLEMENTATION_PLAN.md docs/project-management/phases/
mv PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md docs/project-management/phases/

# Move planning documents
mv BEST_PRACTICES_IMPLEMENTATION_PLAN.md docs/project-management/planning/
mv LLM_OPTIMIZATION_COMPLETE_SUMMARY.md docs/project-management/planning/
mv MOCK_DATA_AUTOMATION.md docs/project-management/planning/
mv MOCK_DATA_QUALITY_ANALYSIS.md docs/project-management/planning/

# Move review documents
mv WEEK2_DAILY_CHECKLIST.md docs/project-management/reviews/
mv WEEK18_FINAL_VALIDATION_REPORT.md docs/project-management/reviews/
mv ADVERSARIAL_REVIEW_NEXT_STEPS.md docs/project-management/reviews/
mv HANDOFF_PROMPT.md docs/project-management/reviews/

# Move status
mv PROJECT_STATUS.md docs/project-management/
```

### Phase 5: Create README Files (15 minutes)

Create overview README.md files for each directory:
- docs/architecture/README.md
- docs/architecture/components/README.md
- docs/adr/README.md
- docs/project-management/README.md

### Phase 6: Update INDEX.md (10 minutes)

Update the root INDEX.md to reflect new structure with links to all documents.

### Phase 7: Update Cross-References (20 minutes)

Update internal links in documents to reflect new paths.

### Phase 8: Git Commit (5 minutes)

```bash
git add -A
git commit -m "Reorganize documentation into logical directory structure

- Move architecture docs to docs/architecture/
- Move ADRs to docs/adr/
- Move project management to docs/project-management/
- Create README files for each category
- Update INDEX.md with new structure
- Update cross-references

Benefits:
- Improved discoverability
- Better navigation
- Easier maintenance
- Scalability for future docs
- Professional organization"
```

**Total Time:** ~75 minutes

---

## README Templates

### docs/architecture/README.md

```markdown
# Architecture Documentation

This directory contains comprehensive architecture documentation for the HCD LLM Optimization System.

## Master Documents

- [MASTER.md](MASTER.md) - Complete system architecture (IEEE 1471, 4+1 views)
- [QUALITY_ATTRIBUTES.md](QUALITY_ATTRIBUTES.md) - Quality attributes and NFRs
- [DOCUMENTATION_PLAN.md](DOCUMENTATION_PLAN.md) - Documentation roadmap

## Component Specifications

Detailed specifications for each system component:

- [CACHE.md](components/CACHE.md) - Multi-level caching system
- [OPTIMIZER.md](components/OPTIMIZER.md) - Prompt optimization engine
- [FORMATTER.md](components/FORMATTER.md) - Output format control
- [TRUNCATION.md](components/TRUNCATION.md) - Smart truncation system
- [BATCH.md](components/BATCH.md) - Batch processing engine
- [INTEGRATION.md](components/INTEGRATION.md) - Integration layer
- [MONITORING.md](components/MONITORING.md) - Monitoring and observability

## Related Documentation

- [Architecture Decision Records](../adr/) - Design decisions and rationale
- [Project Management](../project-management/) - Implementation planning
```

### docs/adr/README.md

```markdown
# Architecture Decision Records (ADRs)

This directory contains all Architecture Decision Records for the HCD LLM Optimization System.

## What are ADRs?

Architecture Decision Records document important architectural decisions made during the project, including:
- Context and problem statement
- Decision made
- Rationale and alternatives considered
- Consequences and trade-offs

## ADR Index

### Technology Choices
- [001-python-choice.md](001-python-choice.md) - Choice of Python 3.11+ as implementation language

### Architecture Patterns
- [002-caching-strategy.md](002-caching-strategy.md) - Multi-level caching strategy
- [006-cache-strategy.md](006-cache-strategy.md) - In-memory vs distributed cache
- [007-sync-vs-async.md](007-sync-vs-async.md) - Synchronous vs asynchronous processing

### Algorithms & Techniques
- [003-tfidf-scoring.md](003-tfidf-scoring.md) - TF-IDF for relevance scoring
- [004-semantic-similarity.md](004-semantic-similarity.md) - Cosine similarity for semantic matching
- [005-batch-processing.md](005-batch-processing.md) - Batch processing with similarity grouping
- [008-token-counting.md](008-token-counting.md) - Token counting methodology

### Quality Attributes
- [009-error-handling.md](009-error-handling.md) - Error handling strategy
- [010-testing-strategy.md](010-testing-strategy.md) - Mock-based testing approach
- [011-monitoring-observability.md](011-monitoring-observability.md) - Monitoring and observability
- [012-security-model.md](012-security-model.md) - Security model and practices

## ADR Guidelines

When creating a new ADR:
1. Use the next sequential number (013, 014, etc.)
2. Use descriptive kebab-case filename
3. Follow the standard ADR template
4. Update this README with the new ADR
5. Reference related ADRs and architecture docs
```

### docs/project-management/README.md

```markdown
# Project Management Documentation

This directory contains project planning, tracking, and review documentation.

## Current Status

- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current project status and metrics

## Implementation Phases

Phased implementation plans and summaries:

- [PHASE_1_IMPLEMENTATION_SUMMARY.md](phases/PHASE_1_IMPLEMENTATION_SUMMARY.md)
- [PHASE_2_IMPLEMENTATION_PLAN.md](phases/PHASE_2_IMPLEMENTATION_PLAN.md)
- [PHASE_3_EXECUTIVE_SUMMARY.md](phases/PHASE_3_EXECUTIVE_SUMMARY.md)
- [PHASE_3_IMPLEMENTATION_PLAN.md](phases/PHASE_3_IMPLEMENTATION_PLAN.md)
- [PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md](phases/PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md)

## Planning Documents

Strategic planning and analysis:

- [BEST_PRACTICES_IMPLEMENTATION_PLAN.md](planning/BEST_PRACTICES_IMPLEMENTATION_PLAN.md)
- [LLM_OPTIMIZATION_COMPLETE_SUMMARY.md](planning/LLM_OPTIMIZATION_COMPLETE_SUMMARY.md)
- [MOCK_DATA_AUTOMATION.md](planning/MOCK_DATA_AUTOMATION.md)
- [MOCK_DATA_QUALITY_ANALYSIS.md](planning/MOCK_DATA_QUALITY_ANALYSIS.md)

## Reviews & Validation

Review reports and validation documentation:

- [WEEK2_DAILY_CHECKLIST.md](reviews/WEEK2_DAILY_CHECKLIST.md)
- [WEEK18_FINAL_VALIDATION_REPORT.md](reviews/WEEK18_FINAL_VALIDATION_REPORT.md)
- [ADVERSARIAL_REVIEW_NEXT_STEPS.md](reviews/ADVERSARIAL_REVIEW_NEXT_STEPS.md)
- [HANDOFF_PROMPT.md](reviews/HANDOFF_PROMPT.md)
```

---

## Updated INDEX.md Structure

```markdown
# HCD LLM Optimization System - Documentation Index

## Quick Links

- [README](README.md) - Project overview
- [CHANGELOG](CHANGELOG.md) - Version history
- [Architecture Master](docs/architecture/MASTER.md) - Complete system architecture
- [Project Status](docs/project-management/PROJECT_STATUS.md) - Current status

## Documentation Categories

### 1. Architecture Documentation

**Location:** `docs/architecture/`

**Master Documents:**
- [System Architecture](docs/architecture/MASTER.md) - IEEE 1471, 4+1 views
- [Quality Attributes](docs/architecture/QUALITY_ATTRIBUTES.md) - NFRs and quality goals
- [Documentation Plan](docs/architecture/DOCUMENTATION_PLAN.md) - Documentation roadmap

**Component Specifications:**
- [Cache System](docs/architecture/components/CACHE.md)
- [Optimizer](docs/architecture/components/OPTIMIZER.md)
- [Formatter](docs/architecture/components/FORMATTER.md)
- [Truncation](docs/architecture/components/TRUNCATION.md)
- [Batch Processor](docs/architecture/components/BATCH.md)
- [Integration Layer](docs/architecture/components/INTEGRATION.md)
- [Monitoring System](docs/architecture/components/MONITORING.md)

### 2. Architecture Decision Records (ADRs)

**Location:** `docs/adr/`

**Technology Choices:**
- [001: Python Choice](docs/adr/001-python-choice.md)

**Architecture Patterns:**
- [002: Caching Strategy](docs/adr/002-caching-strategy.md)
- [006: Cache Strategy](docs/adr/006-cache-strategy.md)
- [007: Sync vs Async](docs/adr/007-sync-vs-async.md)

**Algorithms:**
- [003: TF-IDF Scoring](docs/adr/003-tfidf-scoring.md)
- [004: Semantic Similarity](docs/adr/004-semantic-similarity.md)
- [005: Batch Processing](docs/adr/005-batch-processing.md)
- [008: Token Counting](docs/adr/008-token-counting.md)

**Quality Attributes:**
- [009: Error Handling](docs/adr/009-error-handling.md)
- [010: Testing Strategy](docs/adr/010-testing-strategy.md)
- [011: Monitoring & Observability](docs/adr/011-monitoring-observability.md)
- [012: Security Model](docs/adr/012-security-model.md)

### 3. Project Management

**Location:** `docs/project-management/`

**Status:**
- [Project Status](docs/project-management/PROJECT_STATUS.md)

**Implementation Phases:**
- [Phase 1 Summary](docs/project-management/phases/PHASE_1_IMPLEMENTATION_SUMMARY.md)
- [Phase 2 Plan](docs/project-management/phases/PHASE_2_IMPLEMENTATION_PLAN.md)
- [Phase 3 Summary](docs/project-management/phases/PHASE_3_EXECUTIVE_SUMMARY.md)
- [Phase 3 Plan](docs/project-management/phases/PHASE_3_IMPLEMENTATION_PLAN.md)
- [Phased Implementation](docs/project-management/phases/PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md)

**Planning:**
- [Best Practices Plan](docs/project-management/planning/BEST_PRACTICES_IMPLEMENTATION_PLAN.md)
- [LLM Optimization Summary](docs/project-management/planning/LLM_OPTIMIZATION_COMPLETE_SUMMARY.md)
- [Mock Data Automation](docs/project-management/planning/MOCK_DATA_AUTOMATION.md)
- [Mock Data Quality](docs/project-management/planning/MOCK_DATA_QUALITY_ANALYSIS.md)

**Reviews:**
- [Week 2 Checklist](docs/project-management/reviews/WEEK2_DAILY_CHECKLIST.md)
- [Week 18 Validation](docs/project-management/reviews/WEEK18_FINAL_VALIDATION_REPORT.md)
- [Adversarial Review](docs/project-management/reviews/ADVERSARIAL_REVIEW_NEXT_STEPS.md)
- [Handoff Prompt](docs/project-management/reviews/HANDOFF_PROMPT.md)

### 4. Knowledge Base

**Location:** `docs/knowledge-base/`

See [Knowledge Base Index](docs/knowledge-base/index.md)

### 5. Configuration

**Location:** `config/`

- Custom modes
- Settings
- Templates

### 6. Evaluation

**Location:** `evaluation/`

- Test data
- Results
- Reports
- Scripts

### 7. Examples

**Location:** `examples/`

- Personal wiki
- Research project
- Software project

### 8. Scripts

**Location:** `scripts/`

- Export scripts
- Initialization scripts
- Validation scripts

### 9. Tests

**Location:** `tests/`

- Unit tests
- Integration tests
- Test utilities
```

---

## Implementation Checklist

### Pre-Migration
- [ ] Review proposed structure with team
- [ ] Get approval for reorganization
- [ ] Create backup of current state
- [ ] Schedule maintenance window (if needed)

### Migration
- [ ] Create directory structure
- [ ] Move architecture files
- [ ] Move ADR files
- [ ] Move project management files
- [ ] Create README files
- [ ] Update INDEX.md
- [ ] Update cross-references
- [ ] Test all links

### Post-Migration
- [ ] Verify all files moved correctly
- [ ] Test navigation
- [ ] Update any external references
- [ ] Commit changes to Git
- [ ] Notify team of new structure
- [ ] Update documentation guidelines

---

## Rollback Plan

If issues arise during migration:

1. **Stop immediately** - Don't continue with migration
2. **Assess impact** - Determine what's broken
3. **Restore from backup** - Use Git to revert changes
4. **Document issues** - Record what went wrong
5. **Revise plan** - Adjust approach based on lessons learned

```bash
# Rollback command
git reset --hard HEAD~1  # Undo last commit
git clean -fd            # Remove untracked files/directories
```

---

## Future Enhancements

After successful reorganization, consider:

1. **Automated Link Checking** - Script to validate all internal links
2. **Documentation Generator** - Auto-generate index pages
3. **Search Functionality** - Add search capability
4. **Version Control** - Document versioning strategy
5. **Access Control** - If needed for sensitive docs

---

## Questions & Feedback

**Questions?** Contact the architecture team

**Feedback?** Open an issue or submit a PR

**Suggestions?** We welcome improvements to this structure

---

## Approval

**Proposed By:** Architecture Team  
**Date:** 2026-07-12  
**Status:** Awaiting Approval

**Approvers:**
- [ ] Technical Lead
- [ ] Architecture Team
- [ ] Documentation Team
- [ ] Project Manager

---

**End of Reorganization Plan**
