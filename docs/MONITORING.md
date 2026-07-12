# Monitoring and Observability

This document describes the monitoring and observability features of the Token Optimization System.

## Overview

The monitoring module provides three key components:

1. **Structured Logging** - JSON-formatted logs for easy parsing and analysis
2. **Metrics Collection** - Performance metrics and statistics tracking
3. **Health Checking** - System health monitoring and status checks

## Structured Logging

### Features

- JSON-formatted output for easy parsing
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic timestamp and context enrichment
- Optional file output with rotation
- Component-specific loggers

### Usage

```python
from src.monitoring import get_logger, configure_logging

# Configure global logging
configure_logging(log_level="INFO", log_dir=Path("logs"))

# Get component-specific logger
logger = get_logger("cache")

# Log events
logger.info("cache_hit", key="abc123", latency_ms=0.5)
logger.error("cache_error", error_type="ValueError", message="Invalid key")

# Specialized logging methods
logger.log_cache_hit("L1", "key123", 0.5)
logger.log_optimization(1000, 800, 20.0, 5.5)
logger.log_truncation("priority", 1000, 600, 10.0)
```

### Log Format

```json
{
  "timestamp": "2026-07-12T13:30:00.000Z",
  "level": "INFO",
  "component": "cache",
  "event": "cache_hit",
  "cache_level": "L1",
  "key_hash": 1234,
  "latency_ms": 0.5
}
```

## Metrics Collection

### Features

- Cache metrics (L1, L2, combined)
- Optimization metrics (token savings, latency)
- Truncation metrics (strategy usage, reduction)
- Latency statistics (p50, p95, p99)
- Thread-safe operations

### Usage

```python
from src.monitoring import get_metrics_collector

# Get global metrics collector
collector = get_metrics_collector()

# Record cache operations
collector.record_cache_hit("L1", 0.5)
collector.record_cache_miss("L2")
collector.update_cache_size("L1", 100)

# Record optimization
collector.record_optimization(1000, 800, 10.0)

# Record truncation
collector.record_truncation("priority", 1000, 600, 5.0)

# Get metrics
metrics = collector.get_metrics()
summary = collector.get_summary()
```

### Metrics Output

```json
{
  "timestamp": "2026-07-12T13:30:00.000Z",
  "uptime_seconds": 3600.0,
  "cache": {
    "L1": {
      "hits": 750,
      "misses": 250,
      "hit_rate_percent": 75.0,
      "latency": {
        "avg_ms": 0.5,
        "p95_ms": 1.2,
        "p99_ms": 2.5
      }
    },
    "L2": {
      "hits": 200,
      "misses": 50,
      "hit_rate_percent": 80.0
    },
    "combined_hit_rate_percent": 76.0
  },
  "optimization": {
    "count": 500,
    "avg_savings_percent": 22.5,
    "latency": {
      "avg_ms": 10.5
    }
  },
  "truncation": {
    "count": 300,
    "strategy_usage": {
      "priority": 200,
      "simple": 100
    },
    "avg_reduction_percent": 35.0
  }
}
```

## Health Checking

### Features

- Component health checks (cache, optimizer, truncator)
- System resource monitoring (CPU, memory)
- Overall system health status
- Automatic health degradation detection

### Usage

```python
from src.monitoring import configure_health_checker, check_health

# Configure health checker with components
configure_health_checker(
    cache_l1=l1_cache,
    cache_l2=l2_cache,
    optimizer=optimizer,
    truncator=truncator
)

# Check system health
health = check_health()

# Check if system is healthy
from src.monitoring import get_health_checker
checker = get_health_checker()
is_healthy = checker.is_healthy()
```

### Health Status

- **healthy** - All components operating normally
- **degraded** - Some components experiencing issues (high latency, low hit rate)
- **unhealthy** - Critical issues detected (component failures, resource exhaustion)

### Health Output

```json
{
  "timestamp": "2026-07-12T13:30:00.000Z",
  "status": "healthy",
  "message": "All components healthy",
  "uptime_seconds": 3600.0,
  "components": [
    {
      "name": "cache_l1",
      "status": "healthy",
      "message": "Operating normally",
      "latency_ms": 0.5,
      "details": {
        "hit_rate": 75.0,
        "size": 100
      }
    },
    {
      "name": "system_resources",
      "status": "healthy",
      "message": "Normal resource usage",
      "details": {
        "cpu_percent": 45.0,
        "memory_percent": 60.0
      }
    }
  ]
}
```

## Integration Example

```python
from pathlib import Path
from src.monitoring import (
    configure_logging,
    get_logger,
    get_metrics_collector,
    configure_health_checker
)

# Configure monitoring
configure_logging(log_level="INFO", log_dir=Path("logs"))
logger = get_logger("main")
collector = get_metrics_collector()

# Initialize components
cache_l1 = ExactMatchCache(max_size=1000)
cache_l2 = SemanticCache(max_size=500)
optimizer = PromptOptimizer()

# Configure health checker
configure_health_checker(
    cache_l1=cache_l1,
    cache_l2=cache_l2,
    optimizer=optimizer
)

# Use in application
def process_request(prompt: str) -> str:
    import time
    start = time.time()
    
    try:
        # Check cache
        result = cache_l1.get(prompt)
        if result:
            latency = (time.time() - start) * 1000
            collector.record_cache_hit("L1", latency)
            logger.log_cache_hit("L1", prompt, latency)
            return result
        
        # Optimize prompt
        optimized = optimizer.optimize(prompt)
        latency = (time.time() - start) * 1000
        collector.record_optimization(
            len(prompt),
            len(optimized),
            latency
        )
        
        return optimized
        
    except Exception as e:
        logger.log_error(type(e).__name__, str(e))
        collector.record_error(type(e).__name__)
        raise
    finally:
        total_latency = (time.time() - start) * 1000
        collector.record_request(total_latency)
```

## Best Practices

1. **Use structured logging** - Always use the structured logger instead of print statements
2. **Log at appropriate levels** - Use DEBUG for detailed info, INFO for normal operations, ERROR for failures
3. **Include context** - Add relevant context to log messages (IDs, counts, latencies)
4. **Monitor metrics regularly** - Check metrics periodically to detect issues early
5. **Set up health checks** - Configure health checker with all critical components
6. **Handle missing dependencies** - The health checker gracefully handles missing psutil

## Dependencies

- **Required**: None (core logging and metrics work without external dependencies)
- **Optional**: `psutil>=5.9.0` (for system resource monitoring in health checks)

Install optional dependencies:
```bash
pip install psutil
```

## Performance Impact

The monitoring system is designed for minimal performance impact:

- **Logging**: ~0.1ms per log entry
- **Metrics**: ~0.01ms per metric recording (thread-safe)
- **Health checks**: ~1-5ms per check (depending on components)

## Testing

Run monitoring tests:
```bash
pytest tests/monitoring/ -v
```

Test coverage:
- Logger: 24 tests
- Metrics: 45 tests  
- Health: 35 tests (requires psutil for full coverage)

Total: 104 tests
