# health

Health check system for monitoring operational status.

Provides health checks for cache systems, monitoring components, and system resources.
Supports readiness and liveness probes for production deployments.

## Constants

- `HEALTHY`
- `DEGRADED`
- `UNHEALTHY`
- `UNKNOWN`

## Functions

### `get_health_checker() -> HealthChecker`

Get global health checker instance.

Returns:
    Global HealthChecker instance


### `reset_health_checker() -> None`

Reset the global health checker.

Stops any running background monitoring thread and drops the shared
instance, so checks registered on it (e.g. by
``register_monitoring_health_check``) do not leak across callers. Mirrors
``reset_metrics()`` in ``metrics.py``; primarily used to isolate tests.


### `register_cache_health_check(cache_name: str, cache_instance: Any) -> None`

Register health check for a cache instance.

Args:
    cache_name: Name of the cache (e.g., "L1", "L2")
    cache_instance: Cache instance with stats() method


### `register_system_health_check() -> None`

Register system resource health check.


### `register_monitoring_health_check() -> None`

Register monitoring system health check.


### `check_cache_health() -> HealthCheckResult`

Check cache health.


### `check_system_health() -> HealthCheckResult`

Check system resources.


### `check_monitoring_health() -> HealthCheckResult`

Check monitoring system.


## Classes

### `HealthStatus(Enum)`

Health check status.


### `HealthCheckResult`

Result of a health check.

Attributes:
    name: Name of the health check
    status: Health status
    message: Optional message describing the status
    details: Optional additional details
    timestamp: When the check was performed
    duration_ms: How long the check took

#### Methods

##### `is_healthy() -> bool`

Check if status is healthy.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `SystemHealth`

Overall system health status.

Attributes:
    status: Overall health status
    checks: Individual health check results
    timestamp: When the health check was performed
    version: System version

#### Methods

##### `is_healthy() -> bool`

Check if system is healthy.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `HealthChecker`

Health check coordinator.

Manages and executes health checks for various system components.
Supports both synchronous and background health monitoring.

Attributes:
    checks: Registered health check functions
    check_interval: Interval for background checks (seconds)
    background_enabled: Whether background checking is enabled

#### Methods

##### `__init__(check_interval: float)`

Initialize health checker.

Args:
    check_interval: Interval for background checks in seconds


##### `register_check(name: str, check_func: Callable[[], HealthCheckResult]) -> None`

Register a health check function.

Args:
    name: Name of the health check
    check_func: Function that performs the check


##### `unregister_check(name: str) -> None`

Unregister a health check.

Args:
    name: Name of the health check to remove


##### `check(name: Optional[str]) -> SystemHealth`

Perform health checks.

Args:
    name: Optional specific check to run. If None, runs all checks.

Returns:
    SystemHealth with results


##### `get_last_results() -> Dict[str, HealthCheckResult]`

Get cached results from last check.

Returns:
    Dictionary of check name to result


##### `start_background_checks() -> None`

Start background health checking.


##### `stop_background_checks() -> None`

Stop background health checking.


