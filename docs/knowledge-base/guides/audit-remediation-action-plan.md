---
title: External Audit Remediation Action Plan
category: guide
tags: [action-plan, audit-response, remediation, production-readiness]
created: 2026-07-13
updated: 2026-07-13
status: in-progress
priority: P0-critical
---

# External Audit Remediation Action Plan

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Overview

This action plan addresses the 85 findings from the external audit (2026-07-12), prioritized by severity and value-to-risk ratio.

**Audit Summary:**
- 5 Critical findings
- 35 High findings
- 29 Medium findings
- 16 Low findings
- 37 Confirmed, 3 Partially confirmed, 0 Refuted

---

## Phase 1: Documentation Integrity (P0 - Week 1)

**Goal:** Establish single source of truth and retract fabricated claims

**Estimated Time:** 3-5 days  
**Risk:** Low  
**Value:** Highest - Restores credibility

### Task 1.1: Reconcile Production Readiness Status

**Current State:** Three contradictory claims
- AGENTS.md: "Production ready ✅"
- HONEST_ASSESSMENT.md: "Don't use yet"
- README.md: "7/10, not for enterprise"

**Action:**
```markdown
Adopt unified status: "Beta (7/10) - Not Production Ready"
- Update README.md badge
- Update AGENTS.md
- Update PROJECT_STATUS.md
- Remove all "🎉 production-ready" claims
```

**Files to Update:**
- [ ] README.md
- [ ] AGENTS.md
- [ ] docs/project-management/PROJECT_STATUS.md
- [ ] docs/BOOK_SUMMARY.md

### Task 1.2: Retract Fabricated Metrics

**Current State:** Headline metrics are fabricated
- "68.96% token savings" - circular simulation
- "95% CI [66.42, 71.51]" - fabricated precision
- "52/73/81% scaling" - artifact of capped baseline
- "98.4% coverage" - actually pass rate

**Action:**
```markdown
1. Add disclaimer to README.md:
   "⚠️ Token savings metrics (68.96%, 52/73/81%) are from synthetic 
   simulation, not real-world validation. Real validation pending."

2. Relabel "coverage 98.4%" → "pass rate 98.4%"

3. Update evaluation/README.md:
   - Mark validation_report.json as "synthetic simulation"
   - Add "NOT VALIDATED" warnings
   - Document that optimizer was never called

4. Create new section: "Pending Real-World Validation"
```

**Files to Update:**
- [ ] README.md (add disclaimer)
- [ ] evaluation/README.md (mark as synthetic)
- [ ] evaluation/scripts/run_token_validation.py (add warnings)
- [ ] docs/token-savings-test-plan.md (mark as unexecuted)

### Task 1.3: Fix Architecture Documentation

**Current State:** Two architecture docs contradict each other and code
- docs/ARCHITECTURE.md - describes Bash/Markdown Project A
- docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md - wrong diagrams, outdated

**Action:**
```markdown
1. Create NEW: docs/architecture/UNIFIED_ARCHITECTURE.md
   - Clearly separate Project A (KB Manager) and Project B (Token Optimization)
   - Document real dependency graph
   - Show actual constructor signatures
   - Include monitoring (already built)
   - Include delegation (orphaned but exists)

2. Deprecate old docs:
   - Move docs/ARCHITECTURE.md → docs/architecture/deprecated/KB_MANAGER_ARCH.md
   - Update docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md or deprecate

3. Update README.md to link to unified architecture
```

**Files to Create:**

**Files to Update:**
- [ ] README.md (update architecture link)
- [ ] docs/index.md (update references)

### Task 1.4: Consolidate Test Count Claims

**Current State:** Four different test counts
- 45 (original KB manager)
- 213 (token optimization unit tests)
- 310+ (fabricated claim)
- 317 (actual count)

**Action:**
```markdown
Adopt single truth: "317 test functions (98.4% pass rate, 0% measured coverage)"

Update all references:
- README.md
- PROJECT_STATUS.md
- HONEST_ASSESSMENT.md
- Test documentation
```

**Files to Update:**
- [ ] README.md
- [ ] docs/project-management/PROJECT_STATUS.md
- [ ] evaluation/HONEST_ASSESSMENT.md
- [ ] tests/README.md

---

## Phase 2: Test & Build Hygiene (P0 - Week 2)

**Goal:** Make tests runnable and measure real coverage

**Estimated Time:** 3-5 days  
**Risk:** Low  
**Value:** High - Enables validation

### Task 2.1: Fix Test Collection

**Current State:** Clean pytest fails
- `ModuleNotFoundError: No module named 'src'`
- Only works with `python3 -m pytest` from repo root
- Collects ~240 instead of 317

**Action:**
```markdown
1. Create pyproject.toml with proper package configuration
2. Add conftest.py to set up PYTHONPATH
3. Verify: `pytest` collects all 317 tests from clean checkout
4. Document in tests/README.md
```

**Files to Create:**
- [ ] pyproject.toml
- [ ] tests/conftest.py

**Files to Update:**
- [ ] tests/README.md (update instructions)

### Task 2.2: Measure Real Coverage

**Current State:** No coverage ever measured
- No `--cov` in pytest.ini
- No .coveragerc
- No .coverage artifact
- "98.4% coverage" is actually pass rate

**Action:**
```markdown
1. Add pytest-cov to requirements.txt
2. Configure pytest.ini with --cov=src
3. Run coverage: pytest --cov=src --cov-report=html
4. Document real coverage number (likely 60-80%)
5. Update README.md badge with real number
```

**Files to Update:**
- [ ] requirements.txt (add pytest-cov)
- [ ] pytest.ini (add --cov config)
- [ ] README.md (update badge with real coverage)
- [ ] .gitignore (add htmlcov/, .coverage)

### Task 2.3: Fix test_metrics.py Hang

**Current State:** Hangs >3 min under Python 3.14

**Action:**
```markdown
1. Investigate test_metrics.py hang
2. Add timeout decorators
3. Fix or skip problematic tests
4. Document Python version compatibility
```

**Files to Update:**
- [ ] tests/monitoring/test_metrics.py

### Task 2.4: Clean Up Empty Directories

**Current State:** Empty directories with phantom test claims
- src/batch/ (empty, 15 tests claimed)
- src/formatter/ (empty, 12 tests claimed)
- src/integration/ (empty, 18 tests claimed)
- tests/batch/, tests/formatter/, tests/integration/ (empty)

**Action:**
```markdown
Option A: Delete empty directories
Option B: Add TODO.md explaining future plans

Recommended: Delete for now, add back when implemented
```

**Directories to Delete:**
- [ ] src/batch/
- [ ] src/formatter/
- [ ] src/integration/
- [ ] tests/batch/
- [ ] tests/formatter/
- [ ] tests/integration/

---

## Phase 3: Code Correctness (P1 - Week 3)

**Goal:** Fix critical bugs that make features silently fail

**Estimated Time:** 5-7 days  
**Risk:** Medium  
**Value:** High - Makes monitoring actually work

### Task 3.1: Fix Health Check Bugs (Critical)

**Bug #1:** Calls `cache.get_stats()` - method doesn't exist
- **Location:** monitoring/health.py:115
- **Effect:** Cache health always UNHEALTHY; error swallowed
- **Fix:** Change to `cache.stats()`

**Bug #2:** Wrong kwarg `truncate(max_length=…)`
- **Location:** monitoring/health.py:216
- **Effect:** Truncator health always UNHEALTHY
- **Fix:** Change to `max_tokens=…`; handle dict return

**Action:**
```python
# monitoring/health.py:115
# BEFORE: stats = cache.get_stats()
# AFTER:  stats = cache.stats()

# monitoring/health.py:216
# BEFORE: result = truncator.truncate(text, max_length=100)
# AFTER:  result = truncator.truncate(text, max_tokens=100)
#         text = result["truncated"] if isinstance(result, dict) else result
```

**Files to Update:**
- [ ] src/monitoring/health.py (fix both bugs)
- [ ] tests/monitoring/test_health.py (add regression tests)

### Task 3.2: Fix Cache Bugs

**Bug #3:** `size()` double-counts keys
- **Location:** multi_level_cache.py:131-133
- **Effect:** unique_entries count is wrong
- **Fix:** Hash L2 keys before union

**Bug #4:** `contains()` tests raw key against hashed L1
- **Location:** multi_level_cache.py:271
- **Effect:** L1 branch never matches
- **Fix:** Hash the key before L1 check

**Action:**
```python
# multi_level_cache.py:131-133
# BEFORE: l1_keys = set(self.l1._cache.keys())
#         l2_keys = set(self.l2._cache.keys())
# AFTER:  l1_keys = set(self.l1._cache.keys())  # already hashed
#         l2_keys = set(hashlib.sha256(k.encode()).hexdigest() 
#                      for k in self.l2._cache.keys())

# multi_level_cache.py:271
# BEFORE: if key in self.l1._cache:
# AFTER:  hashed_key = hashlib.sha256(key.encode()).hexdigest()
#         if hashed_key in self.l1._cache:
```

**Files to Update:**
- [ ] src/cache/multi_level_cache.py (fix both bugs)
- [ ] tests/cache/test_multi_level_cache.py (add regression tests)

### Task 3.3: Fix Delegation Bugs

**Bug #5:** Retry adds task to both failed and completed
- **Location:** delegation/coordinator.py:127-135
- **Effect:** Recovered task lives in both sets
- **Fix:** Remove from failed_tasks when adding to completed

**Action:**
```python
# delegation/coordinator.py:127-135
# Add after line 135:
self._failed_tasks.discard(task_id)
```

**Files to Update:**
- [ ] src/delegation/coordinator.py (fix bug)
- [ ] tests/delegation/test_coordinator.py (add regression test)

### Task 3.4: Fix Optimizer Cache Bug

**Bug #6:** Optimizer caches through SemanticCache
- **Location:** prompt_optimizer.py:71-74
- **Effect:** `optimize(A)` can return different prompt's text
- **Fix:** Use ExactCache only, or disable caching

**Action:**
```python
# prompt_optimizer.py:71-74
# Option A: Use ExactCache only
self._cache = ExactCache(max_size=1000)

# Option B: Disable semantic caching for optimizer
# (semantic matching inappropriate for optimization)
```

**Files to Update:**
- [ ] src/optimizer/prompt_optimizer.py (fix bug)
- [ ] tests/optimizer/test_prompt_optimizer.py (add test)

### Task 3.5: Fix Embedding Memory Leak

**Bug #7:** Embedding corpus grows unbounded
- **Location:** embeddings.py:109-150
- **Effect:** Memory + latency blow-up
- **Fix:** Add LRU eviction or max corpus size

**Action:**
```python
# embeddings.py
# Add max_corpus_size parameter
# Implement LRU eviction when corpus exceeds limit
```

**Files to Update:**
- [ ] src/cache/embeddings.py (add eviction)
- [ ] tests/cache/test_embeddings.py (test eviction)

---

## Phase 4: Delegation Integration (P2 - Week 4)

**Goal:** Decide delegation's fate and integrate or remove

**Estimated Time:** 3-5 days  
**Risk:** Low  
**Value:** Medium - Clarifies system scope

### Task 4.1: Assess Delegation Subsystem

**Current State:**
- 1,585 LOC in src/delegation/
- Zero importers (except examples)
- Zero tests
- No documentation
- Works but orphaned

**Options:**

**Option A: Integrate**
- Add tests (target: 50+ tests)
- Add to main API
- Document in architecture
- Create usage guide

**Option B: Move to Examples**
- Move src/delegation/ → examples/delegation/
- Keep as reference implementation
- Document as "experimental"

**Option C: Delete**
- Remove entirely
- Focus on core cache/optimizer/truncation

**Recommendation:** Option B (move to examples)
- Preserves work
- Clarifies it's not production
- Reduces maintenance burden

**Files to Move/Update:**
- [ ] src/delegation/ → examples/delegation/
- [ ] Update README.md (remove delegation claims)
- [ ] Update architecture docs

---

## Phase 5: Monitoring Integration (P2 - Week 5)

**Goal:** Wire monitoring into real components

**Estimated Time:** 3-5 days  
**Risk:** Low  
**Value:** Medium - Makes monitoring useful

### Task 5.1: Integrate Monitoring

**Current State:**
- 1,182 LOC fully built
- 104 tests passing
- Not wired into any components
- Cost tracking added but not integrated

**Action:**
```markdown
1. Add monitoring to cache operations
2. Add monitoring to optimizer
3. Add monitoring to truncator
4. Update examples to show monitoring
5. Create monitoring guide
```

**Files to Update:**
- [ ] src/cache/exact_cache.py (add logging)
- [ ] src/cache/semantic_cache.py (add logging)
- [ ] src/optimizer/prompt_optimizer.py (add logging)
- [ ] src/truncation/truncator.py (add logging)
- [ ] examples/ (add monitoring examples)
- [ ] docs/knowledge-base/guides/monitoring-integration-guide.md (new)

---

## Phase 6: Real-World Validation (P0 - Week 6-7)

**Goal:** Replace fabricated metrics with real measurements

**Estimated Time:** 10-14 days  
**Risk:** High (may disprove claims)  
**Value:** Highest - Validates entire system

### Task 6.1: Select Test Repositories

**Criteria:**
- 10+ diverse repositories
- Multiple languages (Python, JavaScript, Go, Rust, Java)
- Different sizes (small 20 files, medium 50, large 100+)
- Different domains (web apps, CLI tools, libraries)

**Action:**
```markdown
1. Identify 10-15 candidate repositories
2. Get permission if needed
3. Document selection criteria
4. Create test matrix
```

### Task 6.2: Run Real Validation

**Action:**
```markdown
1. Fix run_token_validation.py to call real optimizer
2. Run on all test repositories
3. Measure actual token savings
4. Measure actual cache hit rates
5. Measure actual quality preservation
6. Document results honestly
```

**Expected Outcomes:**
- Real token savings: 20-40% (not 68.96%)
- Real cache hit rate: 10-20% (not 23.33%)
- Real quality: 85-95% (not 91.80%)

### Task 6.3: Update Documentation

**Action:**
```markdown
1. Replace fabricated metrics with real measurements
2. Update README.md with real numbers
3. Update PROJECT_STATUS.md
4. Create validation report
5. Update production readiness assessment
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Single source of truth for production readiness
- [ ] All fabricated metrics retracted or marked as synthetic
- [ ] Architecture docs unified and accurate
- [ ] Test count claims consistent

### Phase 2 Complete When:
- [ ] `pytest` collects all 317 tests from clean checkout
- [ ] Real coverage measured and documented
- [ ] test_metrics.py hang fixed
- [ ] Empty directories cleaned up

### Phase 3 Complete When:
- [ ] All 7 correctness bugs fixed
- [ ] Regression tests added
- [ ] Health checks actually work
- [ ] Cache operations correct

### Phase 4 Complete When:
- [ ] Delegation fate decided
- [ ] Either integrated with tests or moved to examples
- [ ] Documentation updated

### Phase 5 Complete When:
- [ ] Monitoring wired into all components
- [ ] Examples demonstrate monitoring
- [ ] Integration guide created

### Phase 6 Complete When:
- [ ] 10+ real repositories tested
- [ ] Real metrics measured and documented
- [ ] Documentation updated with real numbers
- [ ] Production readiness honestly assessed

---

## Timeline

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| Phase 1: Documentation | 3-5 days | Week 1 | Week 1 | ⏳ Pending |
| Phase 2: Test Hygiene | 3-5 days | Week 2 | Week 2 | ⏳ Pending |
| Phase 3: Code Correctness | 5-7 days | Week 3 | Week 3 | ⏳ Pending |
| Phase 4: Delegation | 3-5 days | Week 4 | Week 4 | ⏳ Pending |
| Phase 5: Monitoring | 3-5 days | Week 5 | Week 5 | ⏳ Pending |
| Phase 6: Validation | 10-14 days | Week 6 | Week 7 | ⏳ Pending |

**Total Estimated Time:** 6-7 weeks

---

## Risk Assessment

### High Risk Items
- **Real-world validation may disprove claims** - Mitigation: Be honest about results
- **Fixing bugs may break existing code** - Mitigation: Add regression tests first
- **Documentation changes may confuse users** - Mitigation: Clear migration guide

### Medium Risk Items
- **Test hygiene may reveal more issues** - Mitigation: Fix incrementally
- **Monitoring integration may impact performance** - Mitigation: Measure overhead

### Low Risk Items
- **Documentation updates** - Low risk, high value
- **Cleaning empty directories** - Trivial change

---

## Progress Tracking

Track progress in: `docs/project-management/audit-remediation-progress.md`

Update weekly with:
- Tasks completed
- Blockers encountered
- Metrics measured
- Next week's plan

---

## References

- [External Audit 2026-07-12](../research/external-audit-2026-07-12.md)
- [Repository Improvement Plan](../research/repository-improvement-plan.md)
- [Project Status](../../project-management/project-status.md)
- [Honest Assessment](../../../evaluation/validation-disclaimer.md)

---

*Action plan created: 2026-07-13*  
*Based on: External audit findings (2026-07-12)*  
*Status: Ready to execute*  
*Owner: Development team*
