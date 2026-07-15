---
title: "Code Coverage Measurement Results"
date: 2026-07-13
type: research
status: complete
tags: [testing, coverage, metrics, audit-remediation]
related:
  - external-audit-2026-07-12.md
  - audit-2026-07-13-institutional.md
  - codebase-analysis-2026-07-14.md
  - ../guides/audit-remediation-action-plan.md
---

# Code Coverage Measurement Results

## Executive Summary

**Critical Finding:** The claimed "98.4% coverage" was actually **test pass rate**, not code coverage.

**Real Code Coverage:** **49%** (1,090 of 2,153 statements not covered)

## Measurement Details

**Date:** 2026-07-13  
**Tool:** pytest with pytest-cov  
**Command:** `pytest tests/ --cov=src --cov-report=term-missing --cov-report=html`

### Test Execution Results

- **Total Tests:** 294 (265 passed, 29 skipped)
- **Test Pass Rate:** 90.1% (265/294) - Note: E2E tests skipped
- **Execution Time:** 2.54 seconds
- **Warnings:** 20 warnings

### Code Coverage Results

```
Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
src/__init__.py                                    4      0   100%
src/cache/__init__.py                              5      0   100%
src/cache/base.py                                 48      2    96%
src/cache/embeddings.py                           87     38    56%
src/cache/exact_cache.py                          81      8    90%
src/cache/multi_level_cache.py                    95      5    95%
src/cache/semantic_cache.py                      138     10    93%
src/delegation/__init__.py                         5      5     0%   ← ORPHANED
src/delegation/agents/__init__.py                  7      7     0%   ← ORPHANED
src/delegation/agents/architecture_agent.py       40     40     0%   ← ORPHANED
src/delegation/agents/documentation_agent.py      60     60     0%   ← ORPHANED
src/delegation/agents/performance_agent.py        41     41     0%   ← ORPHANED
src/delegation/agents/quality_agent.py            55     55     0%   ← ORPHANED
src/delegation/agents/research_agent.py           43     43     0%   ← ORPHANED
src/delegation/agents/security_agent.py           72     72     0%   ← ORPHANED
src/delegation/base.py                           109    109     0%   ← ORPHANED
src/delegation/coordinator.py                    130    130     0%   ← ORPHANED
src/delegation/registry.py                        46     46     0%   ← ORPHANED
src/monitoring/__init__.py                         4      0   100%
src/monitoring/cost_reporting.py                 135    120    11%
src/monitoring/cost_tracker.py                   163    112    31%
src/monitoring/health.py                         144     21    85%
src/monitoring/logger.py                          79      0   100%
src/monitoring/metrics.py                        175    102    42%
src/optimizer/__init__.py                          3      0   100%
src/optimizer/prompt_optimizer.py                135      9    93%
src/optimizer/token_counter.py                    71     11    85%
src/truncation/__init__.py                         3      0   100%
src/truncation/strategies.py                     115     44    62%
src/truncation/truncator.py                       60      0   100%
----------------------------------------------------------------------------
TOTAL                                           2153   1090    49%
```

## Analysis

### Coverage by Module

| Module | Coverage | Status | Notes |
|--------|----------|--------|-------|
| **cache/** | 88% | ✅ Good | Core functionality well-tested |
| **delegation/** | 0% | ❌ Orphaned | 608 lines, 0% coverage - not integrated |
| **monitoring/** | 48% | ⚠️ Partial | Cost tracking/reporting under-tested |
| **optimizer/** | 91% | ✅ Good | Core optimization well-tested |
| **truncation/** | 74% | ✅ Good | Strategies partially tested |

### Orphaned Code Analysis

**Total Orphaned:** 608 statements (28% of codebase)

**Delegation Module (100% orphaned):**
- `delegation/__init__.py` - 5 statements
- `delegation/agents/` - 318 statements (6 agent files)
- `delegation/base.py` - 109 statements
- `delegation/coordinator.py` - 130 statements
- `delegation/registry.py` - 46 statements

**Impact:** These files exist but are never imported or used by any tests or main code paths.

### Under-Tested Areas

**Monitoring Module (48% coverage):**
- `cost_reporting.py` - 11% coverage (120/135 statements missed)
- `cost_tracker.py` - 31% coverage (112/163 statements missed)
- `metrics.py` - 42% coverage (102/175 statements missed)

**Reason:** These modules exist but are not integrated into main workflows.

### Well-Tested Areas

**Cache Module (88% average):**
- `exact_cache.py` - 90% coverage
- `multi_level_cache.py` - 95% coverage
- `semantic_cache.py` - 93% coverage
- `base.py` - 96% coverage

**Optimizer Module (91% average):**
- `prompt_optimizer.py` - 93% coverage
- `token_counter.py` - 85% coverage

**Truncation Module (74% average):**
- `truncator.py` - 100% coverage
- `strategies.py` - 62% coverage

## Comparison with Claims

### Original Claim (Incorrect)

> "Test Coverage: 98.4% (312/317 tests passing)"

**Problem:** This was test **pass rate**, not code coverage.

### Actual Reality

- **Test Pass Rate:** 90.1% (265/294 tests, with 29 skipped)
- **Code Coverage:** 49% (1,090/2,153 statements uncovered)
- **Orphaned Code:** 28% of codebase (608 statements at 0% coverage)

## Known Issues

### Test Collection Issue

**Problem:** `test_metrics.py` causes pytest to hang under Python 3.14

**Workaround:** Tests run with `--ignore=tests/monitoring/test_metrics.py`

**Impact:** Monitoring metrics tests not included in coverage measurement

### E2E Tests Skipped

**Reason:** E2E tests require `RUN_E2E_TESTS=1` environment variable

**Impact:** 29 tests skipped, including:
- Cost tracking integration tests (10 tests)
- Real LLM token counting tests (15 tests)
- Cache performance tests (4 tests)

## Recommendations

### Immediate Actions (Phase 2)

1. ✅ **Document real coverage** - This document
2. ⏳ **Fix test_metrics.py hang** - Debug Python 3.14 compatibility
3. ⏳ **Delete orphaned code** - Remove delegation module or integrate it
4. ⏳ **Improve monitoring coverage** - Add tests for cost tracking/reporting

### Medium-Term Actions (Phase 3-4)

1. **Integrate or remove delegation** - Currently 608 lines of dead code
2. **Test monitoring features** - Bring coverage from 48% to 80%+
3. **Enable E2E tests** - Run with real token counting
4. **Set coverage targets** - Aim for 80% overall (excluding orphaned code)

### Long-Term Actions (Phase 6)

1. **Real-world validation** - Test coverage in production scenarios
2. **Performance testing** - Measure actual latency under load
3. **Integration testing** - Test full workflows end-to-end

## Conclusion

The external audit was correct: the "98.4% coverage" claim was misleading. The actual code coverage is **49%**, with **28% of the codebase completely orphaned** (delegation module).

**Key Takeaways:**
- ✅ Core functionality (cache, optimizer, truncation) is well-tested (74-91%)
- ❌ Monitoring features are under-tested (48%)
- ❌ Delegation module is completely orphaned (0%)
- ⚠️ Test pass rate ≠ code coverage

**Next Steps:** Follow Phase 2 of remediation plan to improve test hygiene and remove/integrate orphaned code.

---

**References:**
- [External Audit Findings](external-audit-2026-07-12.md)
- [Remediation Action Plan](../guides/audit-remediation-action-plan.md)
- [HTML Coverage Report](../../../htmlcov/index.html)
