# metrics

Metrics collection module for the Token Optimization System.

Provides comprehensive performance metrics tracking including cache hit rates,
latency percentiles, token savings, and system health indicators.

## Functions

### `get_metrics_collector() -> MetricsCollector`

Get global metrics collector instance.

Returns:
    MetricsCollector instance


### `reset_metrics() -> None`

Reset global metrics collector.


## Classes

### `LatencyStats`

Statistics for latency measurements.

#### Methods

##### `record(latency: float) -> None`

Record a latency measurement.


##### `get_average() -> float`

Get average latency.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `CacheMetrics`

Metrics for cache operations.

#### Methods

##### `record_hit(latency_ms: float) -> None`

Record cache hit.


##### `record_miss() -> None`

Record cache miss.


##### `record_promotion() -> None`

Record cache promotion.


##### `record_eviction() -> None`

Record cache eviction.


##### `get_hit_rate() -> float`

Calculate hit rate.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `OptimizationMetrics`

Metrics for optimization operations.

#### Methods

##### `record_optimization(original_tokens: int, optimized_tokens: int, latency_ms: float) -> None`

Record optimization operation.


##### `get_average_savings_percent() -> float`

Calculate average savings percentage.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `TruncationMetrics`

Metrics for truncation operations.

#### Methods

##### `record_truncation(strategy: str, original_length: int, truncated_length: int, latency_ms: float) -> None`

Record truncation operation.


##### `get_average_reduction_percent() -> float`

Calculate average reduction percentage.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `MetricsCollector`

Central metrics collector for the Token Optimization System.

Thread-safe metrics collection with support for:
- Cache metrics (L1, L2, combined)
- Optimization metrics
- Truncation metrics
- System-wide statistics

Example:
    >>> collector = MetricsCollector()
    >>> collector.record_cache_hit("L1", 0.5)
    >>> metrics = collector.get_metrics()
    >>> print(metrics["cache"]["L1"]["hit_rate_percent"])
    75.0

#### Methods

##### `__init__()`

Initialize metrics collector.


##### `record_cache_hit(cache_level: str, latency_ms: float) -> None`

Record cache hit.

Args:
    cache_level: Cache level (L1 or L2)
    latency_ms: Lookup latency in milliseconds


##### `record_cache_miss(cache_level: str) -> None`

Record cache miss.

Args:
    cache_level: Cache level (L1 or L2)


##### `record_cache_promotion() -> None`

Record L2 to L1 cache promotion.


##### `record_cache_eviction(cache_level: str) -> None`

Record cache eviction.

Args:
    cache_level: Cache level (L1 or L2)


##### `update_cache_size(cache_level: str, size: int) -> None`

Update cache size.

Args:
    cache_level: Cache level (L1 or L2)
    size: Current cache size


##### `record_optimization(original_tokens: int, optimized_tokens: int, latency_ms: float) -> None`

Record optimization operation.

Args:
    original_tokens: Original token count
    optimized_tokens: Optimized token count
    latency_ms: Optimization latency in milliseconds


##### `record_truncation(strategy: str, original_length: int, truncated_length: int, latency_ms: float) -> None`

Record truncation operation.

Args:
    strategy: Truncation strategy used
    original_length: Original text length
    truncated_length: Truncated text length
    latency_ms: Truncation latency in milliseconds


##### `record_request(latency_ms: float) -> None`

Record request completion.

Args:
    latency_ms: Total request latency in milliseconds


##### `record_error(error_type: str) -> None`

Record error occurrence.

Args:
    error_type: Type of error


##### `get_combined_cache_hit_rate() -> float`

Calculate combined cache hit rate.

Returns:
    Combined hit rate percentage


##### `get_uptime_seconds() -> float`

Get system uptime in seconds.


##### `get_metrics() -> Dict[str, Any]`

Get all metrics.

Returns:
    Dictionary containing all metrics


##### `get_summary() -> Dict[str, Any]`

Get summary metrics.

Returns:
    Dictionary containing summary metrics


##### `reset() -> None`

Reset all metrics.


