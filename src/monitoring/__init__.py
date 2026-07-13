"""
Monitoring module for the Token Optimization System.

Provides structured logging, metrics collection, and health checking
for production monitoring and debugging.
"""

from .logger import (
    StructuredLogger,
    LoggerFactory,
    LogLevel,
    get_logger,
    configure_logging
)

from .metrics import (
    MetricsCollector,
    CacheMetrics,
    OptimizationMetrics,
    TruncationMetrics,
    LatencyStats,
    get_metrics_collector,
    reset_metrics
)

from .health import (
    HealthChecker,
    HealthStatus,
    HealthCheckResult,
    SystemHealth,
    get_health_checker,
    register_cache_health_check,
    register_system_health_check,
    register_monitoring_health_check,
)

from .vocabulary_drift import (
    VocabularySnapshot,
    DriftMetrics,
    VocabularyDriftMonitor,
    get_drift_monitor,
    configure_drift_monitor,
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
    
    # Vocabulary Drift
    "VocabularySnapshot",
    "DriftMetrics",
    "VocabularyDriftMonitor",
    "get_drift_monitor",
    "configure_drift_monitor",
]
