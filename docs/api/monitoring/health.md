# health

Health check module for the Token Optimization System.

Provides system health monitoring and status checks for all components.

## Constants

- `PSUTIL_AVAILABLE`
- `HEALTHY`
- `DEGRADED`
- `UNHEALTHY`
- `PSUTIL_AVAILABLE`

## Functions

### `configure_health_checker(cache_l1, cache_l2, optimizer, truncator) -> None`

Configure global health checker.

Args:
    cache_l1: L1 cache instance
    cache_l2: L2 cache instance
    optimizer: Optimizer instance
    truncator: Truncator instance


### `get_health_checker() -> HealthChecker`

Get global health checker instance.

Returns:
    HealthChecker instance


### `check_health() -> Dict[str, Any]`

Check system health using global checker.

Returns:
    Health status dictionary


## Classes

### `HealthStatus(Enum)`

Health status enumeration.


### `ComponentHealth`

Health status for a component.

#### Methods

##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `HealthChecker`

System health checker.

Monitors health of all system components and provides
overall system health status.

Example:
    >>> checker = HealthChecker()
    >>> health = checker.check_health()
    >>> print(health["status"])
    "healthy"

#### Methods

##### `__init__(cache_l1, cache_l2, optimizer, truncator)`

Initialize health checker.

Args:
    cache_l1: L1 cache instance
    cache_l2: L2 cache instance
    optimizer: Optimizer instance
    truncator: Truncator instance


##### `check_cache_health(cache, name: str) -> ComponentHealth`

Check cache health.

Args:
    cache: Cache instance
    name: Cache name
    
Returns:
    ComponentHealth instance


##### `check_optimizer_health() -> ComponentHealth`

Check optimizer health.

Returns:
    ComponentHealth instance


##### `check_truncator_health() -> ComponentHealth`

Check truncator health.

Returns:
    ComponentHealth instance


##### `check_system_resources() -> ComponentHealth`

Check system resource usage.

Returns:
    ComponentHealth instance


##### `check_health() -> Dict[str, Any]`

Check overall system health.

Returns:
    Dictionary containing health status for all components


##### `is_healthy() -> bool`

Check if system is healthy.

Returns:
    True if system is healthy, False otherwise


