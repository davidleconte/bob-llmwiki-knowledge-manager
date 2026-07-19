---
title: "Thread-Safe Cost Tracking"
category: concept
tags: [cost-tracking, thread-safety, bobcoins, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
related:
  - ../research/cache-race-fix-lessons-2026-07.md
  - ../concepts/cache-thread-safety-patterns.md
---

# Thread-Safe Cost Tracking

## Overview
Cost tracking in `src/monitoring/cost_tracker.py` is opt-in (`track_costs=True`), lock-protected, and imposes <1 ms overhead per operation. The core design principles are: opt-in to avoid breaking existing code, thread-safe from day one, and separate tracking from reporting.

## Key Points
- Always opt-in: `TokenCounter(model="gpt-4", track_costs=True)`
- Thread-safe via a single `Lock` in `CostTracker.__init__`; all counter writes inside `with self._lock:`
- Tracking (data collection) and reporting (presentation) are separate classes
- Never provide point estimates for KB savings — always three confidence tiers (conservative / realistic / optimistic; the tier probabilities live in `kb-savings-estimation-methodology.md`)
- `1 Bobcoin = 1,000 tokens` is the single pricing constant; define it once at module level

## Details

### Architecture
```
CostTracker        (data collection — thread-safe)
    ↓
CostMetrics        (data model — frozen snapshots)
    ↓
CostReporting      (presentation — formatting, ROI, dashboard)
```

Each layer has a single responsibility. `CostTracker` never formats output. `CostReporting` never mutates counters.

### Opt-In Design
```python
# Default — no cost tracking, no overhead
counter = TokenCounter(model="gpt-4")

# Opt-in — tracking enabled
counter = TokenCounter(model="gpt-4", track_costs=True)
optimizer = PromptOptimizer(use_cache=True, track_costs=False)  # explicit opt-out
```
Existing code continues working without changes. No performance impact when disabled.

### Thread Safety
```python
from threading import Lock

class CostTracker:
    def __init__(self):
        self._lock = Lock()
        self._total_tokens = 0
        self._total_bobcoins = 0.0

    def record_cost(self, tokens: int, operation: str) -> None:
        with self._lock:
            self._total_tokens += tokens
            self._total_bobcoins += tokens / TOKENS_PER_BOBCOIN
```
<1 ms overhead per operation even with locking. Verified against 1000+ concurrent operations.

### KB Savings Estimation
Never report point estimates. Always provide three confidence levels:

```python
conservative, realistic, optimistic = estimate_research_tokens(kb_doc_path, source_path)

print(f"Savings estimate: {realistic} tokens (realistic tier)")
print(f"Range: {conservative}–{optimistic} tokens")
```

| Level | Confidence | Use for |
|---|---|---|
| Conservative | 95% | Budget planning |
| Realistic | 70% | Standard reporting |
| Optimistic | 30% | Potential analysis |

### Pricing Constant
```python
# Define once at module level — use everywhere
TOKENS_PER_BOBCOIN = 1_000
DEFAULT_BUDGET_BOBCOINS = 100.0

bobcoins = tokens / TOKENS_PER_BOBCOIN
```

### Alert Thresholds
Configure thresholds at construction time:
```python
tracker = CostTracker(
    budget_bobcoins=100.0,
    alert_thresholds=[0.5, 0.75, 0.9]  # fires at 50%, 75%, 90% of budget
)
```

### ROI Calculation
```python
roi_percent = (total_saved / total_spent) * 100
# Cache hits: ~50% ROI
# With optimizer: ~80% ROI
# With KB (well-formed pairs): ~2162% ROI (80× return at 40 queries, breakeven at 1)
```

## Examples

### Basic usage
```python
from src.monitoring.cost_tracker import CostTracker

tracker = CostTracker(budget_bobcoins=100.0)
tracker.record_cost(tokens=1500, operation="optimize")

stats = tracker.get_stats()
print(f"Spent: {stats.total_bobcoins:.2f} BC / {stats.budget_bobcoins:.0f} BC budget")
```

### Integration with TokenCounter
```python
from src.optimizer.token_counter import TokenCounter

counter = TokenCounter(model="gpt-4", track_costs=True)
count = counter.count_tokens("your prompt text here")
# cost recorded automatically
```

## Related Documents
- [Token Optimization](./token-optimization.md)
- [Multi-Level Caching](./multi-level-caching.md)
- [Cache Thread-Safety Patterns](./cache-thread-safety-patterns.md)
- [KB Document Types](./kb-document-types.md)
- [Cost Tracking Lessons Learned](../research/cost-tracking-lessons-learned.md)

## References
- `src/monitoring/cost_tracker.py` — implementation
- `docs/knowledge-base/guides/cost-tracking-guide.md` — usage guide
- `docs/knowledge-base/references/kb-savings-estimation-methodology.md` — estimation methodology
- `tests/monitoring/` — test suite

---
*Last Updated: 2026-07-18*
*Category: Concept*
