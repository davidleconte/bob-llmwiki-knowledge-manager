# schema

Configuration schema definitions.

Defines typed configuration structures for all system components.

## Classes

### `CacheConfig`

Cache configuration settings.

Attributes:
    l1_max_size: Maximum number of entries in L1 cache
    l1_ttl_seconds: Time-to-live for L1 cache entries (seconds)
    l1_enabled: Whether L1 cache is enabled
    l2_max_size: Maximum number of entries in L2 cache
    l2_ttl_seconds: Time-to-live for L2 cache entries (seconds)
    l2_similarity_threshold: Minimum similarity score for L2 cache hits
    l2_enabled: Whether L2 cache is enabled
    version_support_enabled: Whether version support is enabled
    max_versions: Maximum number of versions to keep per key


### `OptimizerConfig`

Optimizer configuration settings.

Attributes:
    max_tokens: Maximum tokens allowed in optimized output
    target_reduction: Target token reduction ratio (0.0-1.0)
    min_quality_score: Minimum quality score to accept optimization
    strategies: List of optimization strategies to apply

#### Methods


### `MonitoringConfig`

Monitoring configuration settings.

Attributes:
    enabled: Whether monitoring is enabled
    log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    metrics_enabled: Whether metrics collection is enabled
    health_check_interval: Health check interval in seconds


### `ConfigSchema`

Complete configuration schema.

Attributes:
    cache: Cache configuration
    optimizer: Optimizer configuration
    monitoring: Monitoring configuration

