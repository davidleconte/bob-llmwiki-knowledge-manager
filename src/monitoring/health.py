"""Health check system for monitoring operational status.

Provides health checks for cache systems, monitoring components, and system resources.
Supports readiness and liveness probes for production deployments.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.monitoring.logger import get_logger


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check.
    
    Attributes:
        name: Name of the health check
        status: Health status
        message: Optional message describing the status
        details: Optional additional details
        timestamp: When the check was performed
        duration_ms: How long the check took
    """
    name: str
    status: HealthStatus
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0

    def is_healthy(self) -> bool:
        """Check if status is healthy."""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SystemHealth:
    """Overall system health status.
    
    Attributes:
        status: Overall health status
        checks: Individual health check results
        timestamp: When the health check was performed
        version: System version
    """
    status: HealthStatus
    checks: List[HealthCheckResult]
    timestamp: float = field(default_factory=time.time)
    version: str = "v1"

    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "checks": [check.to_dict() for check in self.checks],
            "timestamp": self.timestamp,
            "version": self.version,
        }


class HealthChecker:
    """Health check coordinator.
    
    Manages and executes health checks for various system components.
    Supports both synchronous and background health monitoring.
    
    Attributes:
        checks: Registered health check functions
        check_interval: Interval for background checks (seconds)
        background_enabled: Whether background checking is enabled
    """

    def __init__(self, check_interval: float = 60.0):
        """Initialize health checker.
        
        Args:
            check_interval: Interval for background checks in seconds
        """
        self.checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self.check_interval = check_interval
        self.background_enabled = False
        self._background_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_results: Dict[str, HealthCheckResult] = {}
        self._lock = threading.Lock()

        self._logger = get_logger("monitoring.health")

        self._logger.info("health_checker_initialized",
                         check_interval=check_interval)

    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]) -> None:
        """Register a health check function.
        
        Args:
            name: Name of the health check
            check_func: Function that performs the check
        """
        with self._lock:
            self.checks[name] = check_func
            self._logger.debug("health_check_registered", name=name)

    def unregister_check(self, name: str) -> None:
        """Unregister a health check.
        
        Args:
            name: Name of the health check to remove
        """
        with self._lock:
            if name in self.checks:
                del self.checks[name]
                if name in self._last_results:
                    del self._last_results[name]
                self._logger.debug("health_check_unregistered", name=name)

    def check(self, name: Optional[str] = None) -> SystemHealth:
        """Perform health checks.
        
        Args:
            name: Optional specific check to run. If None, runs all checks.
            
        Returns:
            SystemHealth with results
        """
        start_time = time.time()
        results: List[HealthCheckResult] = []

        with self._lock:
            checks_to_run = {name: self.checks[name]} if name and name in self.checks else self.checks.copy()

        # Run checks
        for check_name, check_func in checks_to_run.items():
            try:
                check_start = time.time()
                result = check_func()
                result.duration_ms = (time.time() - check_start) * 1000
                results.append(result)

                # Cache result
                with self._lock:
                    self._last_results[check_name] = result

            except Exception as e:
                self._logger.error("health_check_failed",
                                 check_name=check_name,
                                 error=str(e))
                results.append(HealthCheckResult(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    duration_ms=(time.time() - check_start) * 1000
                ))

        # Determine overall status
        if not results:
            overall_status = HealthStatus.UNKNOWN
        elif all(r.status == HealthStatus.HEALTHY for r in results):
            overall_status = HealthStatus.HEALTHY
        elif any(r.status == HealthStatus.UNHEALTHY for r in results):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        duration_ms = (time.time() - start_time) * 1000

        self._logger.debug("health_check_complete",
                         status=overall_status.value,
                         checks_run=len(results),
                         duration_ms=duration_ms)

        return SystemHealth(
            status=overall_status,
            checks=results,
            timestamp=time.time()
        )

    def get_last_results(self) -> Dict[str, HealthCheckResult]:
        """Get cached results from last check.
        
        Returns:
            Dictionary of check name to result
        """
        with self._lock:
            return self._last_results.copy()

    def start_background_checks(self) -> None:
        """Start background health checking."""
        if self.background_enabled:
            self._logger.warning("background_checks_already_running")
            return

        self.background_enabled = True
        self._stop_event.clear()
        self._background_thread = threading.Thread(
            target=self._background_check_loop,
            daemon=True,
            name="health-checker"
        )
        self._background_thread.start()

        self._logger.info("background_checks_started",
                         interval=self.check_interval)

    def stop_background_checks(self) -> None:
        """Stop background health checking."""
        if not self.background_enabled:
            return

        self.background_enabled = False
        self._stop_event.set()

        if self._background_thread:
            self._background_thread.join(timeout=5.0)
            self._background_thread = None

        self._logger.info("background_checks_stopped")

    def _background_check_loop(self) -> None:
        """Background check loop."""
        while not self._stop_event.is_set():
            try:
                # Run all checks
                health = self.check()

                # Log if unhealthy
                if not health.is_healthy():
                    self._logger.warning("system_unhealthy",
                                       status=health.status.value,
                                       unhealthy_checks=[
                                           c.name for c in health.checks
                                           if c.status != HealthStatus.HEALTHY
                                       ])

            except Exception as e:
                self._logger.error("background_check_error", error=str(e))

            # Wait for next interval
            self._stop_event.wait(self.check_interval)


# Global health checker instance
_health_checker: Optional[HealthChecker] = None
_health_checker_lock = threading.Lock()


def get_health_checker() -> HealthChecker:
    """Get global health checker instance.
    
    Returns:
        Global HealthChecker instance
    """
    global _health_checker

    if _health_checker is None:
        with _health_checker_lock:
            if _health_checker is None:
                _health_checker = HealthChecker()

    return _health_checker


def reset_health_checker() -> None:
    """Reset the global health checker.

    Stops any running background monitoring thread and drops the shared
    instance, so checks registered on it (e.g. by
    ``register_monitoring_health_check``) do not leak across callers. Mirrors
    ``reset_metrics()`` in ``metrics.py``; primarily used to isolate tests.
    """
    global _health_checker
    with _health_checker_lock:
        if _health_checker is not None:
            _health_checker.stop_background_checks()
            _health_checker = None


def register_cache_health_check(cache_name: str, cache_instance: Any) -> None:
    """Register health check for a cache instance.
    
    Args:
        cache_name: Name of the cache (e.g., "L1", "L2")
        cache_instance: Cache instance with stats() method
    """
    def check_cache_health() -> HealthCheckResult:
        """Check cache health."""
        try:
            stats = cache_instance.stats()

            # Check if cache is responsive
            size = stats.get('size', 0)
            max_size = stats.get('max_size', 1)
            utilization = (size / max_size) * 100 if max_size > 0 else 0

            # Determine status based on utilization
            if utilization < 80:
                status = HealthStatus.HEALTHY
                message = f"Cache operating normally ({utilization:.1f}% full)"
            elif utilization < 95:
                status = HealthStatus.DEGRADED
                message = f"Cache utilization high ({utilization:.1f}% full)"
            else:
                status = HealthStatus.DEGRADED
                message = f"Cache nearly full ({utilization:.1f}% full)"

            return HealthCheckResult(
                name=f"cache_{cache_name}",
                status=status,
                message=message,
                details={
                    "size": size,
                    "max_size": max_size,
                    "utilization": utilization,
                    "hit_rate": stats.get('hit_rate', 0),
                }
            )

        except Exception as e:
            return HealthCheckResult(
                name=f"cache_{cache_name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache check failed: {str(e)}"
            )

    checker = get_health_checker()
    checker.register_check(f"cache_{cache_name}", check_cache_health)


def register_system_health_check() -> None:
    """Register system resource health check."""
    def check_system_health() -> HealthCheckResult:
        """Check system resources."""
        try:
            # Try to import psutil for system metrics
            try:
                import psutil

                # Check memory
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # Check CPU
                cpu_percent = psutil.cpu_percent(interval=0.1)

                # Determine status
                if memory_percent < 80 and cpu_percent < 80:
                    status = HealthStatus.HEALTHY
                    message = "System resources normal"
                elif memory_percent < 90 and cpu_percent < 90:
                    status = HealthStatus.DEGRADED
                    message = "System resources elevated"
                else:
                    status = HealthStatus.DEGRADED
                    message = "System resources high"

                return HealthCheckResult(
                    name="system_resources",
                    status=status,
                    message=message,
                    details={
                        "memory_percent": memory_percent,
                        "cpu_percent": cpu_percent,
                        "memory_available_mb": memory.available / (1024 * 1024),
                    }
                )

            except ImportError:
                # psutil not available, return healthy with limited info
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="System monitoring unavailable (psutil not installed)",
                    details={"psutil_available": False}
                )

        except Exception as e:
            return HealthCheckResult(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"System check failed: {str(e)}"
            )

    checker = get_health_checker()
    checker.register_check("system_resources", check_system_health)


def register_monitoring_health_check() -> None:
    """Register monitoring system health check."""
    def check_monitoring_health() -> HealthCheckResult:
        """Check monitoring system."""
        try:
            from src.monitoring.metrics import get_metrics_collector

            metrics = get_metrics_collector()
            metrics_data = metrics.get_metrics()

            # Check if metrics are being collected. The real hit/miss counts
            # live nested under cache.L1/L2 (see MetricsCollector.get_metrics /
            # CacheMetrics.to_dict); the old flat 'cache_hits'/'cache_misses'
            # keys never existed, so total_operations was always 0.
            cache = metrics_data.get('cache', {})
            l1 = cache.get('L1', {})
            l2 = cache.get('L2', {})
            total_operations = (
                l1.get('hits', 0) + l1.get('misses', 0) +
                l2.get('hits', 0) + l2.get('misses', 0)
            )

            if total_operations > 0:
                status = HealthStatus.HEALTHY
                message = "Monitoring system operational"
            else:
                status = HealthStatus.HEALTHY
                message = "Monitoring system ready (no operations yet)"

            return HealthCheckResult(
                name="monitoring",
                status=status,
                message=message,
                details={
                    "total_operations": total_operations,
                    "metrics_available": True,
                }
            )

        except Exception as e:
            return HealthCheckResult(
                name="monitoring",
                status=HealthStatus.DEGRADED,
                message=f"Monitoring check failed: {str(e)}"
            )

    checker = get_health_checker()
    checker.register_check("monitoring", check_monitoring_health)
