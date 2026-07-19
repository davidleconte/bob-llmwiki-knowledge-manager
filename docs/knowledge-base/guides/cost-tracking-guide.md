---
title: "Cost Tracking Guide"
category: guides
tags: [guides]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Cost Tracking Guide

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


**Created:** 2026-07-13  
**Category:** Monitoring  
**Status:** Active

## Overview

The Cost Tracking System provides comprehensive Bobcoin monitoring and budget management for the Token Optimization System. It tracks token usage, calculates costs, monitors budgets, and generates detailed reports.

**Key Features:**
- Real-time cost tracking per operation
- Token-to-Bobcoin conversion (1 Bobcoin = 1,000 tokens)
- Budget monitoring with configurable alerts
- ROI calculation and savings tracking
- Cost breakdown by operation type
- Dashboard and reporting utilities

## Installation

The cost tracking system is included in the monitoring module. No additional dependencies required.

```python
from src.monitoring.cost_tracker import get_cost_tracker, CostTracker
from src.monitoring.cost_reporting import generate_cost_dashboard
```

## Quick Start

### Basic Usage

```python
from src.monitoring.cost_tracker import get_cost_tracker

# Initialize tracker with budget
tracker = get_cost_tracker(budget_bobcoins=100.0)

# Record token counting operation
tracker.record_token_counting(1500)  # 1.5 Bobcoins

# Record optimization with savings
tracker.record_optimization(
    original_tokens=2000,
    optimized_tokens=1200
)  # Spent 1.2 BC, saved 0.8 BC

# Record cache hit (pure savings)
tracker.record_cache_hit(1000)  # Saved 1.0 Bobcoins

# Get budget status
status = tracker.get_budget_status()
print(f"Spent: {status['spent_bobcoins']} BC")
print(f"Saved: {status['saved_bobcoins']} BC")
print(f"Remaining: {status['remaining_bobcoins']} BC")
```

### Automatic Integration

Enable cost tracking in components:

```python
from src.optimizer import TokenCounter, PromptOptimizer
from src.cache import ExactCache, SemanticCache

# Enable cost tracking
counter = TokenCounter(model="gpt-4", track_costs=True)
optimizer = PromptOptimizer(model="gpt-4", track_costs=True)
cache = ExactCache(max_size=100, track_costs=True)

# Operations automatically tracked
tokens = counter.count_tokens("Your prompt here")
result = optimizer.optimize("Your prompt here")
cached = cache.get("Your prompt here")
```

## Cost Tracking Pricing Model

**Bobcoin Conversion:**
- 1 Bobcoin = 1,000 tokens
- Based on typical LLM pricing (~$0.01 per 1K tokens)

**Example Costs:**
- Token counting (1,500 tokens): 1.5 Bobcoins
- Optimization (2,000 → 1,200 tokens): 1.2 BC spent, 0.8 BC saved
- Cache hit (1,000 tokens): 0 BC spent, 1.0 BC saved

## Budget Management

### Setting Budget

```python
tracker = get_cost_tracker(budget_bobcoins=100.0)

# Update budget later
tracker.set_budget(150.0)
```

### Budget Alerts

Configure alerts at specific thresholds:

```python
tracker = CostTracker(
    budget_bobcoins=100.0,
    alert_thresholds=[50.0, 75.0, 90.0]  # Alert at 50%, 75%, 90%
)

# Check active alerts
alerts = tracker.get_active_alerts()
for alert in alerts:
    print(f"Alert: {alert['threshold_percent']}% threshold exceeded")
```

### Budget Health Check

```python
from src.monitoring.cost_reporting import check_budget_health

health = check_budget_health()
print(f"Status: {health['status']}")  # healthy, caution, warning, critical
print(f"Message: {health['message']}")
print(f"Remaining: {health['remaining_bobcoins']} BC")
```

## Cost Reporting

### Generate Dashboard

```python
from src.monitoring.cost_reporting import generate_cost_dashboard, print_cost_dashboard

# Generate ASCII dashboard
dashboard = generate_cost_dashboard()
print(dashboard)

# Or use convenience function
print_cost_dashboard()
```

**Example Output:**
```
======================================================================
              BOBCOIN COST TRACKING DASHBOARD
======================================================================

                           BUDGET STATUS
----------------------------------------------------------------------
  Budget:                100.0000 Bobcoins
  Spent:                  45.2500 Bobcoins
  Saved:                  28.7500 Bobcoins
  Net Spent:              16.5000 Bobcoins
  Remaining:              83.5000 Bobcoins
  Used:                    16.50%
  [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

                           COST METRICS
----------------------------------------------------------------------
  Total Operations:              150
  Avg Cost/Operation:         0.3017 Bobcoins
  ROI:                        63.54%
  Total Tokens Used:          45,250
  Total Tokens Saved:         28,750
```

### Cost Summary

```python
from src.monitoring.cost_reporting import generate_cost_summary

summary = generate_cost_summary()
print(f"Total Spent: {summary['budget']['spent_bobcoins']} BC")
print(f"ROI: {summary['costs']['roi_percent']}%")
```

### Top Cost Operations

```python
from src.monitoring.cost_reporting import get_top_cost_operations

top_ops = get_top_cost_operations(limit=5)
for op in top_ops:
    print(f"{op['operation']}: {op['cost_bobcoins']} BC ({op['tokens']} tokens)")
```

## Cost Breakdown

### By Operation Type

```python
metrics = tracker.get_cost_metrics()

# Cost by operation
for operation, cost in metrics['cost_by_operation'].items():
    tokens = metrics['tokens_by_operation'][operation]
    print(f"{operation}: {cost} BC ({tokens} tokens)")

# Savings by source
for source, savings in metrics['savings_by_source'].items():
    print(f"{source}: {savings} BC saved")
```

### Cost Rate

```python
rate = tracker.get_cost_rate()
print(f"Per second: {rate['bobcoins_per_second']} BC")
print(f"Per minute: {rate['bobcoins_per_minute']} BC")
print(f"Per hour: {rate['bobcoins_per_hour']} BC")
```

## ROI Calculation

```python
metrics = tracker.get_cost_metrics()

roi = metrics['roi_percent']
print(f"ROI: {roi}%")

# ROI = (Total Saved / Total Spent) × 100
# Example: Spent 45 BC, Saved 28 BC → ROI = 62.2%
```

## Cost Projections

```python
from src.monitoring.cost_reporting import calculate_projected_costs

# Project costs for next 24 hours
projection = calculate_projected_costs(
    operations_per_hour=100,
    hours=24
)

print(f"Projected cost: {projection['projected_cost_bobcoins']} BC")
print(f"Will exceed budget: {projection['will_exceed_budget']}")
```

## Integration Examples

### Full Workflow with Cost Tracking

```python
from src.optimizer import TokenCounter, PromptOptimizer
from src.cache import MultiLevelCache
from src.monitoring.cost_tracker import get_cost_tracker
from src.monitoring.cost_reporting import print_cost_dashboard

# Initialize with cost tracking
tracker = get_cost_tracker(budget_bobcoins=100.0)
counter = TokenCounter(model="gpt-4", track_costs=True)
optimizer = PromptOptimizer(model="gpt-4", track_costs=True)
cache = MultiLevelCache()

# Enable cache cost tracking
cache.l1_cache.track_costs = True
cache.l1_cache._cost_tracker = tracker
cache.l2_cache.track_costs = True
cache.l2_cache._cost_tracker = tracker

# Process prompts
prompts = [
    "Explain machine learning",
    "What is deep learning?",
    "How do neural networks work?"
]

for prompt in prompts:
    # Check cache first
    cached = cache.get(prompt)
    
    if cached:
        print(f"Cache hit: {prompt[:30]}...")
    else:
        # Optimize and cache
        result = optimizer.optimize(prompt)
        cache.set(prompt, result['optimized'], 
                 metadata={'tokens': result['optimized_tokens']})
        print(f"Optimized: {prompt[:30]}...")

# Display cost dashboard
print_cost_dashboard()
```

### E2E Testing with Cost Tracking

```python
import pytest
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker

class TestWithCostTracking:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset cost tracker before each test."""
        reset_cost_tracker()
        yield
        reset_cost_tracker()
    
    def test_operation_costs(self):
        tracker = get_cost_tracker(budget_bobcoins=50.0)
        counter = TokenCounter(model="gpt-4", track_costs=True)
        
        # Perform operations
        tokens = counter.count_tokens("Test prompt")
        
        # Verify costs
        metrics = tracker.get_cost_metrics()
        assert metrics['total_tokens_used'] == tokens
        assert metrics['total_bobcoins_spent'] > 0
```

## Best Practices

### 1. Set Realistic Budgets

```python
# Calculate based on expected usage
operations_per_day = 1000
avg_tokens_per_operation = 500
daily_tokens = operations_per_day * avg_tokens_per_operation
daily_bobcoins = daily_tokens / 1000

tracker = get_cost_tracker(budget_bobcoins=daily_bobcoins * 30)  # Monthly budget
```

### 2. Monitor Regularly

```python
# Check budget health periodically
from src.monitoring.cost_reporting import check_budget_health

health = check_budget_health()
if health['status'] in ['warning', 'critical']:
    print(f"⚠️  {health['message']}")
    # Take action: reduce operations, increase budget, etc.
```

### 3. Track Savings Sources

```python
# Identify which optimizations provide best ROI
metrics = tracker.get_cost_metrics()
for source, savings in sorted(
    metrics['savings_by_source'].items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{source}: {savings} BC saved")
```

### 4. Export Cost Data

```python
from src.monitoring.cost_reporting import export_cost_data

# Export for analysis
export_cost_data('costs.json', format='json')
```

### 5. Reset Between Sessions

```python
from src.monitoring.cost_tracker import reset_cost_tracker

# Reset for new session/test
reset_cost_tracker()
```

## API Reference

### CostTracker Class

**Methods:**
- `record_token_counting(tokens: int) -> float`
- `record_optimization(original_tokens: int, optimized_tokens: int) -> Tuple[float, float]`
- `record_cache_hit(tokens_saved: int) -> float`
- `record_cache_miss(tokens_used: int) -> float`
- `record_truncation(original_tokens: int, truncated_tokens: int) -> Tuple[float, float]`
- `get_budget_status() -> Dict[str, Any]`
- `get_cost_metrics() -> Dict[str, Any]`
- `get_cost_rate() -> Dict[str, float]`
- `set_budget(budget_bobcoins: float) -> None`
- `reset() -> None`

### Cost Reporting Functions

**Functions:**
- `generate_cost_summary() -> Dict[str, Any]`
- `generate_cost_dashboard() -> str`
- `generate_cost_report(include_breakdown: bool, include_trends: bool) -> Dict[str, Any]`
- `check_budget_health() -> Dict[str, Any]`
- `get_top_cost_operations(limit: int) -> List[Dict[str, Any]]`
- `calculate_projected_costs(operations_per_hour: int, hours: int) -> Dict[str, Any]`
- `export_cost_data(filepath: str, format: str) -> None`

### Utility Functions

**Functions:**
- `get_cost_tracker(budget_bobcoins: float) -> CostTracker`
- `reset_cost_tracker() -> None`
- `tokens_to_bobcoins(tokens: int) -> float`
- `bobcoins_to_tokens(bobcoins: float) -> int`

## Troubleshooting

### Cost Tracking Not Working

**Problem:** Operations not being tracked

**Solution:**
```python
# Ensure track_costs=True
counter = TokenCounter(model="gpt-4", track_costs=True)

# Verify tracker is initialized
from src.monitoring.cost_tracker import get_cost_tracker
tracker = get_cost_tracker()
print(tracker.get_cost_metrics())
```

### Budget Alerts Not Triggering

**Problem:** Alerts not appearing

**Solution:**
```python
# Check alert configuration
tracker = CostTracker(
    budget_bobcoins=100.0,
    alert_thresholds=[50.0, 75.0, 90.0]
)

# Manually check alerts
alerts = tracker.get_active_alerts()
print(f"Active alerts: {len(alerts)}")
```

### Inaccurate Cost Calculations

**Problem:** Costs don't match expectations

**Solution:**
```python
# Verify token counting
counter = TokenCounter(model="gpt-4")
tokens = counter.count_tokens("Your text")
expected_cost = tokens / 1000  # Bobcoins

# Check if tiktoken is available
print(f"Using tiktoken: {counter.use_tiktoken}")
```

## Performance Considerations

- **Overhead:** Cost tracking adds <1ms overhead per operation
- **Memory:** Minimal (~100 bytes per tracked operation)
- **Thread Safety:** All operations are thread-safe with locks
- **Scalability:** Tested with 10,000+ operations

## Related Documentation

- [Monitoring Guide](../../MONITORING.md) - Overall monitoring system
- [E2E Testing Setup Guide](./e2e-testing-setup-guide.md) - Testing with cost tracking
- [Token Optimization Concept](../concepts/token-optimization.md) - Core optimization concepts

## Examples

See `tests/e2e/test_cost_tracking.py` for comprehensive examples.

---

*Last Updated: 2026-07-13*  
*Category: Guide*  
*Status: Active*
