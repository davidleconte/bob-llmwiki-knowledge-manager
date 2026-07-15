# Appendix A: API Reference

## A.1 Cache API

### MultiLevelCache

**Purpose:** Orchestrates L1 and L2 caches for optimal performance

**Import:**
```python
from src.cache import MultiLevelCache
```

**Constructor:**
```python
cache = MultiLevelCache(
    l1_max_size=10000,      # Maximum L1 entries
    l1_ttl=3600,            # L1 TTL in seconds
    l2_max_size=5000,       # Maximum L2 entries
    l2_ttl=86400,           # L2 TTL in seconds
    similarity_threshold=0.85  # L2 similarity threshold
)
```

**Methods:**

**get(key: str) → Optional[Any]**
```python
result = cache.get("query_text")
# Returns cached value or None
```

**set(key: str, value: Any) → None**
```python
cache.set("query_text", result)
# Stores value in L2 cache
```

**clear() → None**
```python
cache.clear()
# Clears both L1 and L2 caches
```

**get_stats() → Dict[str, Any]**
```python
stats = cache.get_stats()
# Returns: {
#   "l1_size": 150,
#   "l2_size": 300,
#   "l1_hits": 1000,
#   "l2_hits": 500,
#   "misses": 200,
#   "hit_rate": 0.88
# }
```

### L1Cache

**Purpose:** Fast exact-match caching using hash table

**Import:**
```python
from src.cache import L1Cache
```

**Constructor:**
```python
cache = L1Cache(max_size=10000, ttl=3600)
```

**Methods:**

**get(key: str) → Optional[Any]**
**set(key: str, value: Any) → None**
**clear() → None**
**get_stats() → Dict[str, Any]**

### L2Cache

**Purpose:** Semantic similarity matching using TF-IDF

**Import:**
```python
from src.cache import L2Cache
```

**Constructor:**
```python
cache = L2Cache(
    max_size=5000,
    ttl=86400,
    similarity_threshold=0.85
)
```

**Methods:**

**get(key: str) → Optional[Any]**
**set(key: str, value: Any) → None**
**clear() → None**
**get_stats() → Dict[str, Any]**

## A.2 Optimizer API

### PromptOptimizer

**Purpose:** Optimize prompts and count tokens

**Import:**
```python
from src.optimizer import PromptOptimizer
```

**Constructor:**
```python
optimizer = PromptOptimizer(
    model="gpt-4",
    min_optimization_threshold=0.10
)
```

**Methods:**

**optimize(prompt: str) → str**
```python
optimized = optimizer.optimize(
    "Could you please explain how this works?"
)
# Returns: "Explain how this works"
```

**count_tokens(text: str) → int**
```python
count = optimizer.count_tokens("Hello world")
# Returns: 2
```

**get_optimization_stats(original: str, optimized: str) → Dict[str, Any]**
```python
stats = optimizer.get_optimization_stats(original, optimized)
# Returns: {
#   "original_tokens": 15,
#   "optimized_tokens": 5,
#   "savings_percent": 66.7,
#   "quality_preserved": True
# }
```

## A.3 Truncation API

### Truncator

**Purpose:** Truncate text using various strategies

**Import:**
```python
from src.truncation import Truncator
```

**Constructor:**
```python
truncator = Truncator(
    max_length=2000,
    strategy="auto"  # or "simple", "priority", "semantic", "sliding"
)
```

**Methods:**

**truncate(text: str, max_tokens: int) → str**
```python
truncated = truncator.truncate(long_text, max_tokens=500)
```

**auto_select_strategy(text: str) → str**
```python
strategy = truncator.auto_select_strategy(text)
# Returns: "priority" or "semantic" or "sliding"
```

**get_truncation_stats(original: str, truncated: str) → Dict[str, Any]**
```python
stats = truncator.get_truncation_stats(original, truncated)
# Returns: {
#   "original_tokens": 2000,
#   "truncated_tokens": 500,
#   "savings_percent": 75.0,
#   "strategy_used": "priority"
# }
```

## A.4 Monitoring API

### Logger

**Purpose:** Structured logging with JSON format

**Import:**
```python
from src.monitoring import get_logger
```

**Usage:**
```python
logger = get_logger("component_name")

logger.info("event_name", key="value", count=42)
logger.warning("warning_event", reason="something")
logger.error("error_event", error=str(e))
```

### MetricsCollector

**Purpose:** Collect and aggregate metrics

**Import:**
```python
from src.monitoring import get_metrics_collector
```

**Usage:**
```python
metrics = get_metrics_collector()

metrics.record_cache_hit("L1", latency_ms=0.5)
metrics.record_cache_miss("L2", latency_ms=50.0)
metrics.record_optimization(
    original_tokens=1000,
    optimized_tokens=600,
    latency_ms=10.0
)

stats = metrics.get_metrics()
```

### HealthChecker

**Purpose:** Monitor system health

**Import:**
```python
from src.monitoring import HealthChecker
```

**Usage:**
```python
health = HealthChecker()

status = health.check_all()
# Returns: {
#   "status": "healthy",
#   "components": {
#     "cache": "healthy",
#     "optimizer": "healthy",
#     "truncation": "healthy"
#   }
# }
```

---

**See also:**
- Appendix B: Configuration Reference
- Appendix C: Template Reference
