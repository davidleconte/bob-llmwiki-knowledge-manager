---
title: "Token Savings Test Plan — Synthetic Data Validation (Historical)"
date: 2026-07-12
status: superseded
category: research
superseded_by: evaluation/results/validation-2026-07-14/manifest.json
note: "Design target (55%) on synthetic data — never a measured result. Phase 5 replaced this with a real manifest-backed harness."
---

# Token Savings Test Plan - Synthetic Data Validation

**Purpose:** Mathematically prove token savings across all 4 phases using synthetic data and statistical analysis

**Date:** 2026-07-12  
**Status:** Design Phase — **SUPERSEDED design target**

> **Superseded.** The 55% figure below was a *design target* on synthetic data, never a measured result. Phase 5 shipped a real, manifest-backed harness (`python -m src.validation`); the measured optimizer-compression figure and its provenance live in `evaluation/results/validation-2026-07-14/` and [STATUS.md](../STATUS.md). Treat this document as historical methodology notes.

---

## Executive Summary

This test plan establishes a rigorous, statistically sound methodology to validate the claimed token savings (55% average) across all four implementation phases using synthetic data and controlled experiments.

### Key Objectives

1. **Quantify token savings** with statistical confidence (95% CI)
2. **Validate performance claims** (4x speedup, 71% time savings)
3. **Reuse existing test infrastructure** where applicable
4. **Create new tests** for Phases 3 & 4
5. **Provide mathematical proof** of efficiency gains

---

## Existing Test Infrastructure Assessment

### Current Test Coverage (213 tests)

```
tests/
├── cache/              # 45 tests - L1/L2 caching, hit rates
├── optimizer/          # 38 tests - Token counting, optimization
├── truncation/         # 32 tests - Text truncation strategies
├── monitoring/         # 28 tests - Logging, metrics, health
├── batch/              # 15 tests - Batch processing
├── formatter/          # 12 tests - Output formatting
├── integration/        # 18 tests - End-to-end workflows
├── performance/        # 15 tests - Performance benchmarks
└── e2e/               # 10 tests - Full system tests
```

### Reusability Analysis

#### ✅ **Highly Reusable (No Changes Needed)**

1. **Cache Tests** (`tests/cache/`)
   - Already test L1/L2 hit rates
   - Measure token savings through caching
   - Performance benchmarks (<1ms L1, <100ms L2)
   - **Reuse:** 100% - No changes needed

2. **Optimizer Tests** (`tests/optimizer/`)
   - Token counting accuracy
   - Optimization effectiveness
   - **Reuse:** 100% - No changes needed

3. **Monitoring Tests** (`tests/monitoring/`)
   - Metrics collection
   - Statistics tracking
   - **Reuse:** 100% - No changes needed

#### ⚠️ **Partially Reusable (Minor Updates)**

4. **Integration Tests** (`tests/integration/`)
   - Test end-to-end workflows
   - **Update needed:** Add Phase 3 & 4 scenarios
   - **Reuse:** 70% - Add new test cases

5. **Performance Tests** (`tests/performance/`)
   - Benchmark execution times
   - **Update needed:** Add parallel execution benchmarks
   - **Reuse:** 60% - Extend with new metrics

#### ❌ **Not Applicable (New Tests Needed)**

6. **Phase 3 Utilities** - No existing tests
   - Batch file reader
   - Component analyzer
   - KB query
   - Visualizer

7. **Phase 4 Delegation** - No existing tests
   - Sub-agent framework
   - Parallel execution
   - Coordinator
   - Specialized agents

---

## Test Plan Architecture

### Three-Tier Testing Strategy

```
Tier 1: Unit Tests (Micro-benchmarks)
├── Individual component token counting
├── Cache hit rate validation
└── Single operation timing

Tier 2: Integration Tests (Macro-benchmarks)
├── Multi-component workflows
├── Phase-specific scenarios
└── Cross-phase integration

Tier 3: System Tests (End-to-End)
├── Complete workflow simulation
├── Real-world scenario modeling
└── Statistical validation
```

---

## Synthetic Data Design

### Data Generation Strategy

#### 1. Repository Simulation

**Synthetic Repository Structure:**
```
synthetic-repo/
├── src/
│   ├── auth/          # 10 files, 500 lines each
│   ├── api/           # 15 files, 400 lines each
│   ├── database/      # 8 files, 600 lines each
│   └── utils/         # 20 files, 200 lines each
├── tests/             # 30 files, 300 lines each
└── docs/              # 10 markdown files
```

**Total:** 93 files, ~35,000 lines of code

#### 2. Code Patterns

**Security Patterns (for SecurityAgent):**
- 5 hardcoded passwords
- 3 API keys
- 2 SQL injection vulnerabilities
- 4 XSS risks
- 3 weak crypto usages

**Performance Patterns (for PerformanceAgent):**
- 8 nested loops (O(n²))
- 5 N+1 query patterns
- 3 blocking operations
- 6 inefficient algorithms

**Quality Patterns (for QualityAgent):**
- 12 long functions (>50 lines)
- 8 complex functions (cyclomatic complexity >10)
- 15 code smells

#### 3. Knowledge Base Content

**Synthetic KB:**
- 50 concept documents
- 30 guide documents
- 20 reference documents
- 40 research documents

**Total:** 140 documents, ~100,000 words

---

## Mathematical Framework

### Token Counting Methodology

#### Baseline (Without Optimization)

```python
def calculate_baseline_tokens(scenario):
    """Calculate tokens for unoptimized workflow"""
    tokens = 0
    
    # Phase 1: Manual analysis
    tokens += count_tokens(read_all_files())  # No caching
    tokens += count_tokens(analyze_dependencies())
    tokens += count_tokens(security_scan())
    tokens += count_tokens(quality_check())
    
    # Phase 2: Sequential execution
    for component in components:
        tokens += count_tokens(analyze_component(component))
    
    return tokens
```

#### Optimized (With All Phases)

```python
def calculate_optimized_tokens(scenario):
    """Calculate tokens for optimized workflow"""
    tokens = 0
    
    # Phase 1: Automated scripts (cached results)
    tokens += count_tokens(run_scripts())  # Minimal tokens
    
    # Phase 2: Guided workflow (reuses Phase 1)
    tokens += count_tokens(guided_analysis())  # References cache
    
    # Phase 3: Enhanced utilities (batch + cache)
    tokens += count_tokens(batch_operations())  # Batch efficiency
    
    # Phase 4: Parallel execution (shared cache)
    tokens += count_tokens(parallel_analysis())  # Parallel + cache
    
    return tokens
```

#### Savings Calculation

```python
def calculate_savings(baseline, optimized):
    """Calculate token savings with confidence interval"""
    savings_pct = ((baseline - optimized) / baseline) * 100
    
    # Statistical validation
    mean_savings = np.mean(savings_pct)
    std_savings = np.std(savings_pct)
    ci_95 = 1.96 * (std_savings / np.sqrt(len(savings_pct)))
    
    return {
        "mean": mean_savings,
        "std": std_savings,
        "ci_95": (mean_savings - ci_95, mean_savings + ci_95),
        "samples": len(savings_pct)
    }
```

---

## Test Scenarios

### Scenario 1: Small Repository (Baseline)

**Repository:**
- 20 files
- 5,000 lines of code
- 3 components

**Expected Results:**
- Baseline: ~2,000 tokens
- Optimized: ~900 tokens
- Savings: 55%

### Scenario 2: Medium Repository

**Repository:**
- 50 files
- 15,000 lines of code
- 8 components

**Expected Results:**
- Baseline: ~5,000 tokens
- Optimized: ~2,250 tokens
- Savings: 55%

### Scenario 3: Large Repository

**Repository:**
- 100 files
- 35,000 lines of code
- 15 components

**Expected Results:**
- Baseline: ~10,000 tokens
- Optimized: ~4,500 tokens
- Savings: 55%

### Scenario 4: Complex Analysis (Deep Dive)

**Repository:**
- 50 files
- 15,000 lines of code
- Deep security + performance + quality analysis

**Expected Results:**
- Baseline: ~8,000 tokens
- Optimized: ~3,200 tokens
- Savings: 60%

### Scenario 5: Parallel Execution (Phase 4)

**Repository:**
- 50 files
- 6 parallel tasks

**Expected Results:**
- Sequential: 120ms, 3,000 tokens
- Parallel: 30ms, 1,800 tokens
- Speedup: 4x
- Token savings: 40% (through shared cache)

---

## Statistical Validation

### Hypothesis Testing

**Null Hypothesis (H₀):** Token savings ≤ 50%  
**Alternative Hypothesis (H₁):** Token savings > 50%  
**Significance Level:** α = 0.05

### Sample Size Calculation

```python
def calculate_sample_size(effect_size=0.55, power=0.80, alpha=0.05):
    """Calculate required sample size for statistical power"""
    from scipy.stats import norm
    
    z_alpha = norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    
    n = ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
    return int(np.ceil(n))

# Result: n ≈ 30 test runs per scenario
```

### Validation Metrics

1. **Mean Token Savings:** μ = 55%
2. **Standard Deviation:** σ ≤ 5%
3. **95% Confidence Interval:** [52%, 58%]
4. **P-value:** p < 0.05
5. **Effect Size:** Cohen's d > 0.8 (large effect)

---

## Implementation Plan

### Phase 1: Existing Test Updates (Week 1)

**Tasks:**
1. Review and validate existing 213 tests
2. Update integration tests for Phases 3 & 4
3. Add token counting to all tests
4. Create baseline measurements

**Deliverables:**
- Updated test suite (213 → 250 tests)
- Baseline token measurements
- Performance benchmarks

### Phase 2: Synthetic Data Generation (Week 1)

**Tasks:**
1. Create synthetic repository generator
2. Generate test scenarios (5 scenarios × 30 runs)
3. Create synthetic knowledge base
4. Implement data validation

**Deliverables:**
- Synthetic data generator script
- 150 test data sets
- Validation report

### Phase 3: New Test Development (Week 2)

**Tasks:**
1. Create Phase 3 utility tests (50 tests)
2. Create Phase 4 delegation tests (40 tests)
3. Create integration tests (30 tests)
4. Create system tests (20 tests)

**Deliverables:**
- 140 new tests
- Total: 390 tests
- 100% coverage for Phases 3 & 4

### Phase 4: Statistical Analysis (Week 2)

**Tasks:**
1. Run all test scenarios (150 runs)
2. Collect token measurements
3. Perform statistical analysis
4. Generate validation report

**Deliverables:**
- Statistical analysis report
- Token savings proof (with 95% CI)
- Performance validation
- Publication-ready results

---

## Test Execution Framework

### Automated Test Runner

```python
class TokenSavingsValidator:
    """Automated test runner for token savings validation"""
    
    def __init__(self):
        self.scenarios = []
        self.results = []
    
    def add_scenario(self, scenario):
        """Add test scenario"""
        self.scenarios.append(scenario)
    
    def run_all(self, iterations=30):
        """Run all scenarios with statistical sampling"""
        for scenario in self.scenarios:
            for i in range(iterations):
                result = self.run_scenario(scenario)
                self.results.append(result)
    
    def run_scenario(self, scenario):
        """Run single scenario"""
        # Baseline
        baseline_tokens = self.measure_baseline(scenario)
        baseline_time = self.measure_time(scenario, optimized=False)
        
        # Optimized
        optimized_tokens = self.measure_optimized(scenario)
        optimized_time = self.measure_time(scenario, optimized=True)
        
        return {
            "scenario": scenario.name,
            "baseline_tokens": baseline_tokens,
            "optimized_tokens": optimized_tokens,
            "savings_pct": ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100,
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "speedup": baseline_time / optimized_time
        }
    
    def generate_report(self):
        """Generate statistical validation report"""
        df = pd.DataFrame(self.results)
        
        report = {
            "mean_savings": df["savings_pct"].mean(),
            "std_savings": df["savings_pct"].std(),
            "ci_95": self.calculate_ci(df["savings_pct"]),
            "p_value": self.hypothesis_test(df["savings_pct"]),
            "effect_size": self.calculate_effect_size(df),
            "mean_speedup": df["speedup"].mean()
        }
        
        return report
```

---

## Expected Outcomes

### Token Savings Validation

**Hypothesis:** All phases combined achieve 55% ± 3% token savings

**Evidence Required:**
- ✅ Mean savings: 55%
- ✅ 95% CI: [52%, 58%]
- ✅ P-value: < 0.05
- ✅ Effect size: > 0.8
- ✅ Sample size: ≥ 30 per scenario

### Performance Validation

**Hypothesis:** Phase 4 achieves 4x ± 0.5x parallelization speedup

**Evidence Required:**
- ✅ Mean speedup: 4.0x
- ✅ 95% CI: [3.5x, 4.5x]
- ✅ P-value: < 0.05
- ✅ Consistent across scenarios

### Quality Validation

**Hypothesis:** 100% success rate with error handling

**Evidence Required:**
- ✅ Success rate: 100%
- ✅ Error recovery: 100%
- ✅ Cache hit rate: > 80%
- ✅ No data loss

---

## Reporting Format

### Final Validation Report Structure

```markdown
# Token Savings Validation Report

## Executive Summary
- Overall token savings: X% (95% CI: [Y%, Z%])
- Statistical significance: p < 0.05
- Effect size: Cohen's d = X.XX
- Conclusion: [VALIDATED / NOT VALIDATED]

## Methodology
- Sample size: N runs
- Test scenarios: 5
- Statistical tests: t-test, ANOVA, effect size

## Results by Phase
### Phase 1: Automated Scripts
- Token savings: X%
- Time savings: Y%

### Phase 2: repo-analyzer Mode
- Token savings: X%
- Effort reduction: Y%

### Phase 3: Enhanced Utilities
- Token savings: X%
- Efficiency gain: Y%

### Phase 4: Sub-Agent Delegation
- Token savings: X%
- Parallelization: Yx speedup

## Statistical Analysis
- Descriptive statistics
- Hypothesis testing
- Confidence intervals
- Effect sizes

## Visualizations
- Token savings distribution
- Performance comparison charts
- Confidence interval plots
- Speedup analysis

## Conclusion
- Claims validated: [YES/NO]
- Recommendations
- Future work
```

---

## Success Criteria

### Must Have (Required for Validation)

- [ ] 390 total tests (213 existing + 177 new)
- [ ] 150 test runs (5 scenarios × 30 iterations)
- [ ] Statistical significance (p < 0.05)
- [ ] 95% confidence intervals
- [ ] Token savings: 55% ± 3%
- [ ] Parallelization: 4x ± 0.5x

### Should Have (Recommended)

- [ ] Automated test runner
- [ ] Real-time monitoring
- [ ] Interactive visualizations
- [ ] Publication-ready report

### Nice to Have (Optional)

- [ ] Comparison with competitors
- [ ] Cost analysis ($ savings)
- [ ] ROI calculation
- [ ] Case studies

---

## Timeline

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| 1 | Setup | Update existing tests, generate synthetic data | 250 tests, 150 datasets |
| 2 | Development | Create new tests, implement runner | 390 tests, test framework |
| 3 | Execution | Run all scenarios, collect data | Raw results |
| 4 | Analysis | Statistical analysis, report generation | Final validation report |

**Total Duration:** 4 weeks

---

## Conclusion

This test plan provides a rigorous, statistically sound methodology to validate token savings claims using synthetic data. The existing test infrastructure (213 tests) is highly reusable, requiring only minor updates and 177 new tests for complete coverage.

**Key Strengths:**
- Reuses 100% of cache/optimizer tests
- Mathematical proof framework
- Statistical validation (95% CI)
- Comprehensive coverage (390 tests)
- Automated execution

**Next Steps:**
1. Review and approve test plan
2. Begin Phase 1 (existing test updates)
3. Generate synthetic data
4. Execute validation
5. Publish results

**Expected Outcome:** Mathematical proof of 55% token savings with 95% statistical confidence.
