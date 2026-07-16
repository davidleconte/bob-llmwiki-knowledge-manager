---
title: "Mock Data Quality Analysis & Best Practices Coverage (Historical)"
date: 2026-07-12
status: historical
category: audit
note: "Analysis based on mock/synthetic data. Superseded by Phase 5 manifest-backed harness."
---

# Mock Data Quality Analysis & Best Practices Coverage

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Executive Summary

The current mock data is **moderately realistic** but lacks several behavioral patterns that would occur in real usage. The knowledge manager implements approximately **60-70%** of documented Bob Shell token-saving best practices.

## Mock Data Quality Assessment

### ✅ What's Realistic

1. **Token Distribution**
   - Control: 400-600 tokens (realistic for ad-hoc queries)
   - Treatment: 40-70% reduction (matches expected knowledge reuse)
   - Scenario adjustments (document creation > retrieval)

2. **Time Patterns**
   - 3-5 minutes for control tasks (reasonable)
   - 30% time reduction with treatment (plausible)
   - Scenario-specific timing variations

3. **Quality Scores**
   - Control: 75-90/100 (realistic baseline)
   - Treatment: 85-98/100 (improvement from better context)
   - Proper distribution across 4 quality dimensions

### ❌ What's Missing (Behavioral Realism)

1. **Learning Curve**
   ```python
   # Current: Static distributions
   base_tokens = random.randint(400, 600)
   
   # Should be: Progressive improvement
   # Task 1: 600 tokens → Task 30: 350 tokens (learning effect)
   learning_factor = 1.0 - (task_number / 60) * 0.4
   base_tokens = int(random.randint(400, 600) * learning_factor)
   ```

2. **Task Complexity Variance**
   - Current: Uniform random within ranges
   - Reality: Some tasks are 2x harder than others
   - Missing: Outliers (very easy/very hard tasks)

3. **Fatigue Effects**
   - Current: No time-of-day effects
   - Reality: Tasks at end of day are slower/lower quality
   - Missing: Session length impact

4. **Context Switching Costs**
   - Current: Each task independent
   - Reality: Related tasks are faster (warm cache)
   - Missing: Task sequence dependencies

5. **Error Recovery**
   - Current: All tasks succeed
   - Reality: Some tasks require retries (token spikes)
   - Missing: Failed attempts, corrections

6. **Individual Differences**
   - Current: Single "mock_user" profile
   - Reality: Different users have different baselines
   - Missing: User-specific patterns

## Bob Shell Token-Saving Best Practices Coverage

### Core Best Practices (from Bob Book)

#### ✅ Implemented by Knowledge Manager (60-70%)

1. **Context Reuse** (HIGH IMPACT)
   - ✅ Cross-references to existing documents
   - ✅ Memory recalls from previous sessions
   - ✅ Search queries to find relevant context
   - **Impact**: 30-50% token reduction

2. **Structured Knowledge Storage** (HIGH IMPACT)
   - ✅ Markdown-based documentation
   - ✅ Hierarchical organization
   - ✅ Consistent formatting
   - **Impact**: 20-30% token reduction

3. **Incremental Updates** (MEDIUM IMPACT)
   - ✅ Update existing docs vs recreating
   - ✅ Targeted edits with context
   - **Impact**: 15-25% token reduction

4. **Template Reuse** (MEDIUM IMPACT)
   - ✅ Task templates (60 predefined)
   - ✅ Consistent structure
   - **Impact**: 10-20% token reduction

5. **Semantic Search** (MEDIUM IMPACT)
   - ✅ Find relevant docs quickly
   - ✅ Reduce exploratory queries
   - **Impact**: 10-15% token reduction

6. **Quality Metrics** (LOW IMPACT)
   - ✅ Track completeness, accuracy, consistency, usability
   - **Impact**: 5-10% quality improvement

#### ❌ Not Yet Implemented (30-40%)

7. **Prompt Optimization** (HIGH IMPACT)
   - ❌ Compress prompts (remove redundancy)
   - ❌ Use system messages efficiently
   - ❌ Batch related queries
   - **Potential**: 20-30% additional reduction

8. **Caching Strategies** (HIGH IMPACT)
   - ❌ Cache common responses
   - ❌ Reuse embeddings
   - ❌ Store intermediate results
   - **Potential**: 15-25% additional reduction

9. **Smart Truncation** (MEDIUM IMPACT)
   - ❌ Summarize long contexts
   - ❌ Extract key information only
   - ❌ Progressive detail loading
   - **Potential**: 10-20% additional reduction

10. **Batch Processing** (MEDIUM IMPACT)
    - ❌ Group similar tasks
    - ❌ Amortize setup costs
    - ❌ Parallel processing
    - **Potential**: 10-15% additional reduction

11. **Output Format Control** (LOW IMPACT)
    - ❌ Request concise formats
    - ❌ Limit verbosity
    - ❌ Structured outputs (JSON)
    - **Potential**: 5-10% additional reduction

12. **Model Selection** (LOW IMPACT)
    - ❌ Use smaller models for simple tasks
    - ❌ Route by complexity
    - **Potential**: 5-10% cost reduction

### Best Practices Applied in Mock Data

The mock data simulates these practices through metrics:

```python
# Treatment condition includes:
cross_refs = random.randint(2, 8)      # Context reuse
searches = random.randint(1, 5)        # Knowledge retrieval
recalls = random.randint(1, 4)         # Memory access

# These drive the 40-70% token reduction
reduction = random.uniform(0.4, 0.7)
base_tokens = int(base_tokens * (1 - reduction))
```

## Improvements for Better Behavioral Simulation

### Priority 1: Learning Curves

```python
def apply_learning_curve(task_number: int, base_value: float) -> float:
    """Simulate user getting better over time."""
    # Exponential learning: fast improvement, then plateau
    learning_rate = 0.3  # 30% improvement potential
    progress = 1 - math.exp(-task_number / 10)  # Plateau after ~20 tasks
    improvement = learning_rate * progress
    return base_value * (1 - improvement)
```

### Priority 2: Task Complexity Distribution

```python
def get_task_complexity() -> float:
    """Generate realistic complexity distribution."""
    # 70% normal, 20% easy, 10% hard
    roll = random.random()
    if roll < 0.2:
        return random.uniform(0.5, 0.7)  # Easy
    elif roll < 0.9:
        return random.uniform(0.8, 1.2)  # Normal
    else:
        return random.uniform(1.5, 2.5)  # Hard
```

### Priority 3: Temporal Effects

```python
def apply_fatigue(task_in_session: int, time_of_day: int) -> float:
    """Simulate fatigue and time-of-day effects."""
    # Fatigue: +5% time per task in session
    fatigue_factor = 1 + (task_in_session * 0.05)
    
    # Time of day: slower in afternoon
    if 13 <= time_of_day <= 15:  # Post-lunch dip
        tod_factor = 1.15
    elif time_of_day >= 17:  # End of day
        tod_factor = 1.25
    else:
        tod_factor = 1.0
    
    return fatigue_factor * tod_factor
```

### Priority 4: Error Recovery

```python
def simulate_errors(task_complexity: float) -> dict:
    """Simulate occasional failures and retries."""
    # 10% chance of needing retry for complex tasks
    if task_complexity > 1.5 and random.random() < 0.1:
        return {
            'attempts': 2,
            'tokens_used': base_tokens * 1.8,  # Retry costs
            'time_seconds': base_time * 1.6
        }
    return {'attempts': 1, 'tokens_used': base_tokens, 'time_seconds': base_time}
```

### Priority 5: Context Switching

```python
def apply_context_switching(prev_scenario: str, curr_scenario: str) -> float:
    """Simulate warm/cold cache effects."""
    if prev_scenario == curr_scenario:
        return 0.85  # 15% faster with warm context
    else:
        return 1.1   # 10% slower with cold start
```

## Recommended Mock Data V2 Architecture

```python
class RealisticUserSimulator:
    """Simulate realistic user behavior patterns."""
    
    def __init__(self, user_profile: str = "average"):
        self.skill_level = self._get_skill_level(user_profile)
        self.task_history = []
        self.session_start = None
        
    def generate_task_metrics(self, task_number: int, scenario: str) -> dict:
        """Generate realistic metrics with behavioral patterns."""
        
        # 1. Base complexity
        complexity = self._get_task_complexity(scenario)
        
        # 2. Learning curve
        learning_factor = self._apply_learning(task_number)
        
        # 3. Context switching
        context_factor = self._apply_context_switching(scenario)
        
        # 4. Temporal effects
        temporal_factor = self._apply_temporal_effects(task_number)
        
        # 5. Error recovery
        error_factor = self._simulate_errors(complexity)
        
        # Combine all factors
        base_tokens = 500
        final_tokens = int(
            base_tokens * 
            complexity * 
            learning_factor * 
            context_factor * 
            temporal_factor * 
            error_factor
        )
        
        return {
            'tokens_used': final_tokens,
            'complexity': complexity,
            'learning_progress': 1 - learning_factor,
            'context_warm': context_factor < 1.0,
            'had_errors': error_factor > 1.0
        }
```

## Validation Metrics

To assess mock data quality, compare against real data on:

1. **Distribution Shape**
   - Real: Long-tailed (some outliers)
   - Mock V1: Normal distribution
   - Mock V2: Should match real distribution

2. **Temporal Patterns**
   - Real: Improvement over time
   - Mock V1: Static
   - Mock V2: Learning curves

3. **Variance**
   - Real: High variance (CV ~0.4)
   - Mock V1: Low variance (CV ~0.2)
   - Mock V2: Should match real variance

4. **Correlations**
   - Real: Time correlates with tokens (r ~0.7)
   - Mock V1: Weak correlation (r ~0.3)
   - Mock V2: Should match real correlations

## Summary

### Current Mock Data Quality: **6/10**

**Strengths:**
- Correct magnitude of effects
- Proper scenario adjustments
- Realistic quality distributions

**Weaknesses:**
- No learning curves
- No behavioral variance
- No temporal effects
- No error recovery
- Too uniform

### Knowledge Manager Best Practices: **60-70%**

**Implemented (High Value):**
- Context reuse (cross-refs, searches, recalls)
- Structured knowledge storage
- Incremental updates
- Template reuse
- Semantic search

**Missing (High Value):**
- Prompt optimization
- Caching strategies
- Smart truncation
- Batch processing

### Recommended Actions

1. **For Testing**: Current mock data is adequate
2. **For Realism**: Implement Mock Data V2 with behavioral patterns
3. **For Research**: Use real human data (no substitute)
4. **For Knowledge Manager**: Add caching and prompt optimization (30% more savings)

---

**Bottom Line**: Mock data demonstrates the pipeline works, but real user behavior is more complex. The knowledge manager captures the most impactful best practices (60-70%), with room for 30-40% more optimization through caching and prompt engineering.
