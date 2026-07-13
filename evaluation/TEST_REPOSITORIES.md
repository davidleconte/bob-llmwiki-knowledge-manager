---
title: Phase 6 Test Repository Selection
category: validation
tags: [phase6, testing, repositories]
created: 2026-07-13
updated: 2026-07-13
status: active
---

# Phase 6 Test Repository Selection

## Overview

Selected repositories for Phase 6 real-world validation using Bob Shell as LLM API.

**Selection Criteria:**
- Diverse languages and frameworks
- Varying sizes (small, medium, large)
- Different code complexity levels
- Real-world production codebases
- Publicly accessible (for reproducibility)

**Budget Allocation:**
- Small repos (10-30 files): 5 BC each
- Medium repos (30-100 files): 10 BC each
- Large repos (100+ files): 15 BC each
- **Total Budget:** 100 BC

---

## Test Repository Matrix

### Category 1: Small Repositories (10-30 files)

#### 1. Flask Minimal API
- **Path:** TBD (user to provide or use public repo)
- **Language:** Python
- **Size:** ~15 files
- **Budget:** 5 BC
- **Focus:** REST API, simple architecture
- **Expected Savings:** 30-40%

#### 2. Express.js Starter
- **Path:** TBD
- **Language:** JavaScript/Node.js
- **Size:** ~20 files
- **Budget:** 5 BC
- **Focus:** Web server, middleware patterns
- **Expected Savings:** 25-35%

#### 3. Go CLI Tool
- **Path:** TBD
- **Language:** Go
- **Size:** ~12 files
- **Budget:** 5 BC
- **Focus:** Command-line interface, concurrency
- **Expected Savings:** 35-45%

**Subtotal:** 15 BC for 3 small repositories

---

### Category 2: Medium Repositories (30-100 files)

#### 4. Django Blog Application
- **Path:** TBD
- **Language:** Python/Django
- **Size:** ~50 files
- **Budget:** 10 BC
- **Focus:** MVC architecture, ORM, templates
- **Expected Savings:** 35-45%

#### 5. React Component Library
- **Path:** TBD
- **Language:** TypeScript/React
- **Size:** ~60 files
- **Budget:** 10 BC
- **Focus:** Component patterns, hooks, testing
- **Expected Savings:** 30-40%

#### 6. Spring Boot Microservice
- **Path:** TBD
- **Language:** Java/Spring
- **Size:** ~45 files
- **Budget:** 10 BC
- **Focus:** Enterprise patterns, dependency injection
- **Expected Savings:** 25-35%

#### 7. Ruby on Rails API
- **Path:** TBD
- **Language:** Ruby/Rails
- **Size:** ~55 files
- **Budget:** 10 BC
- **Focus:** RESTful API, ActiveRecord
- **Expected Savings:** 30-40%

**Subtotal:** 40 BC for 4 medium repositories

---

### Category 3: Large Repositories (100+ files)

#### 8. E-commerce Platform (Backend)
- **Path:** TBD
- **Language:** Python/FastAPI
- **Size:** ~120 files
- **Budget:** 15 BC
- **Focus:** Complex business logic, async operations
- **Expected Savings:** 40-50%

#### 9. Full-Stack Web Application
- **Path:** TBD
- **Language:** TypeScript (Next.js)
- **Size:** ~150 files
- **Budget:** 15 BC
- **Focus:** SSR, API routes, database integration
- **Expected Savings:** 35-45%

#### 10. Data Processing Pipeline
- **Path:** TBD
- **Language:** Python/Pandas
- **Size:** ~100 files
- **Budget:** 15 BC
- **Focus:** ETL, data transformation, analytics
- **Expected Savings:** 40-50%

**Subtotal:** 45 BC for 3 large repositories

---

## Budget Summary

| Category | Repositories | Budget per Repo | Total Budget |
|----------|--------------|-----------------|--------------|
| Small (10-30 files) | 3 | 5 BC | 15 BC |
| Medium (30-100 files) | 4 | 10 BC | 40 BC |
| Large (100+ files) | 3 | 15 BC | 45 BC |
| **Total** | **10** | - | **100 BC** |

**Buffer:** 0 BC (tight budget, may need adjustment)

---

## Alternative: Use This Project as First Test

### Self-Validation on bob-llmwiki-knowledge-manager

**Already completed initial test:**
- ✅ 5 files analyzed
- ✅ 5.22 BC spent
- ✅ 37.8% estimated savings
- ✅ 70% confidence

**Full project analysis:**
- **Total Python files:** 227 (limited to 50 for budget)
- **Estimated budget:** 20-25 BC
- **Expected savings:** 35-45%
- **Advantage:** Immediate availability, no setup needed

**Recommendation:** Start with full analysis of this project, then expand to external repositories.

---

## Execution Plan

### Phase 1: Self-Validation (Days 1-3)

```bash
# Full analysis of current project
python3 evaluation/scripts/run_bob_shell_validation.py \
    --repo /Users/david.leconte/Projects/bob-llmwiki-knowledge-manager \
    --name "bob-llmwiki-knowledge-manager" \
    --budget 25.0 \
    --max-files 50 \
    --output evaluation/results/self-validation-full.json
```

**Expected Results:**
- Files analyzed: 50
- Cost: 20-25 BC
- Savings: 35-45%
- Confidence: 65-75%

### Phase 2: External Repositories (Days 4-10)

**Option A: User-Provided Repositories**
- User provides paths to 9 additional repositories
- Run validation on each with appropriate budget
- Aggregate results

**Option B: Public Repository Analysis**
- Clone popular open-source projects
- Run validation on each
- Document results

### Phase 3: Analysis & Documentation (Days 11-14)

```bash
# Aggregate all results
python3 evaluation/scripts/aggregate_results.py \
    --input evaluation/results/*.json \
    --output evaluation/reports/phase6-final-report.json

# Generate summary report
python3 evaluation/scripts/generate_summary.py \
    --input evaluation/reports/phase6-final-report.json \
    --output evaluation/reports/phase6-summary.md
```

---

## Success Criteria

### Validation Complete When:

- [x] 10+ repositories selected
- [ ] All repositories analyzed
- [ ] Budget stayed within 100 BC
- [ ] Results documented
- [ ] Aggregate statistics calculated
- [ ] Final report generated

### Expected Aggregate Results:

**Token Savings:**
- Target: 30-40% average
- Minimum acceptable: 20%
- Stretch goal: 45%+

**Cache Hit Rate:**
- Target: 15-25% average
- Minimum acceptable: 10%
- Stretch goal: 30%+

**Quality Preservation:**
- Target: 85-95% average
- Minimum acceptable: 80%
- Stretch goal: 95%+

**Confidence:**
- Target: 65-75% average
- Minimum acceptable: 60%
- Stretch goal: 80%+

---

## Risk Mitigation

### Risk 1: Repository Access
- **Issue:** External repositories may not be accessible
- **Mitigation:** Start with self-validation, expand gradually
- **Contingency:** Use public GitHub repositories

### Risk 2: Budget Overrun
- **Issue:** Repositories larger than expected
- **Mitigation:** Strict per-repo limits, max-files parameter
- **Contingency:** Stop validation if budget exceeded

### Risk 3: Low Savings
- **Issue:** Actual savings lower than expected
- **Mitigation:** Document honestly, analyze causes
- **Contingency:** Adjust optimization parameters, retest

### Risk 4: Time Overrun
- **Issue:** Analysis takes longer than 10-14 days
- **Mitigation:** Parallel execution where possible
- **Contingency:** Reduce repository count, focus on quality

---

## Next Steps

### Immediate Actions (User)

1. **Review repository selection** - Confirm or modify list
2. **Provide repository paths** - For external repositories
3. **Approve budget** - Confirm 100 BC allocation
4. **Start Phase 1** - Run full self-validation

### Recommended Approach

**Start with self-validation:**
```bash
# Run full validation on current project
python3 evaluation/scripts/run_bob_shell_validation.py \
    --repo . \
    --name "bob-llmwiki-knowledge-manager" \
    --budget 25.0 \
    --max-files 50 \
    --output evaluation/results/self-validation-full.json
```

**Then expand to external repositories as available.**

---

## Related Documentation

- [Phase 6 Bob Shell Validation Approach](../docs/knowledge-base/guides/phase6-bob-shell-validation-approach.md)
- [Phase 6 Real-World Validation Plan](../docs/knowledge-base/guides/phase6-real-world-validation-plan.md)
- [Validation Script](./scripts/run_bob_shell_validation.py)

---

**Document Status:** Active  
**Last Updated:** July 13, 2026  
**Phase:** 6.1 - Repository Selection  
**Budget:** 100 BC total
