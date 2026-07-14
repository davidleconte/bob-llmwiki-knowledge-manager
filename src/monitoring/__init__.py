"""
Monitoring module for the Token Optimization System.

Provides structured logging, metrics collection, and health checking
for production monitoring and debugging.
"""

from .health import (
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
    get_health_checker,
    register_cache_health_check,
    register_monitoring_health_check,
    register_system_health_check,
)
from .logger import LoggerFactory, LogLevel, StructuredLogger, configure_logging, get_logger
from .metrics import (
    CacheMetrics,
    LatencyStats,
    MetricsCollector,
    OptimizationMetrics,
    TruncationMetrics,
    get_metrics_collector,
    reset_metrics,
)

__all__ = [
    # Logger
    "StructuredLogger",
    "LoggerFactory",
    "LogLevel",
    "get_logger",
    "configure_logging",
    # Metrics
    "MetricsCollector",
    "CacheMetrics",
    "OptimizationMetrics",
    "TruncationMetrics",
    "LatencyStats",
    "get_metrics_collector",
    "reset_metrics",
    # Health
    "HealthChecker",
    "HealthStatus",
    "HealthCheckResult",
    "SystemHealth",
    "get_health_checker",
    "register_cache_health_check",
    "register_system_health_check",
    "register_monitoring_health_check",
]
