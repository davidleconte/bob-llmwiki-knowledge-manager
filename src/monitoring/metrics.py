"""
Metrics collection module for the Token Optimization System.

Provides comprehensive performance metrics tracking including cache hit rates,
latency percentiles, token savings, and system health indicators.
"""

import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock, RLock
from typing import Any, Deque, Dict, Optional


@dataclass
class LatencyStats:
    """Statistics for latency measurements."""

    count: int = 0
    total: float = 0.0
    min: float = float("inf")
    max: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    recent: Deque[float] = field(default_factory=lambda: deque(maxlen=1000))

    def record(self, latency: float) -> None:
        """Record a latency measurement.

        O(1): appends to the bounded window and updates running aggregates only.
        Percentiles are computed lazily on read (:meth:`_recompute_percentiles`),
        not here. ATK-DOS-05/06: the previous implementation sorted the whole
        window (up to 1000 elements) on *every* record — and callers invoke
        record() while holding the collector's shared lock, so that O(k log k)
        sort serialised every recorded operation across all threads.
        """
        self.count += 1
        self.total += latency
        self.min = min(self.min, latency)
        self.max = max(self.max, latency)
        self.recent.append(latency)

    def _recompute_percentiles(self) -> None:
        """Refresh p50/p95/p99 from the recent window. O(k log k); read path only."""
        if not self.recent:
            return
        sorted_recent = sorted(self.recent)
        k = len(sorted_recent)
        self.p50 = statistics.median(sorted_recent)
        self.p95 = sorted_recent[min(int(k * 0.95), k - 1)]
        self.p99 = sorted_recent[min(int(k * 0.99), k - 1)]

    def get_average(self) -> float:
        """Get average latency."""
        return self.total / self.count if self.count > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (recomputes percentiles from the recent window)."""
        self._recompute_percentiles()
        return {
            "count": self.count,
            "avg_ms": round(self.get_average(), 2),
            "min_ms": round(self.min, 2) if self.min != float("inf") else 0.0,
            "max_ms": round(self.max, 2),
            "p50_ms": round(self.p50, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
        }


@dataclass
class CacheMetrics:
    """Metrics for cache operations."""

    hits: int = 0
    misses: int = 0
    promotions: int = 0
    evictions: int = 0
    size: int = 0
    latency: LatencyStats = field(default_factory=LatencyStats)

    def record_hit(self, latency_ms: float) -> None:
        """Record cache hit."""
        self.hits += 1
        self.latency.record(latency_ms)

    def record_miss(self) -> None:
        """Record cache miss."""
        self.misses += 1

    def record_promotion(self) -> None:
        """Record cache promotion."""
        self.promotions += 1

    def record_eviction(self) -> None:
        """Record cache eviction."""
        self.evictions += 1

    def get_hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.hits + self.misses,
            "hit_rate_percent": round(self.get_hit_rate(), 2),
            "promotions": self.promotions,
            "evictions": self.evictions,
            "size": self.size,
            "latency": self.latency.to_dict(),
        }


@dataclass
class OptimizationMetrics:
    """Metrics for optimization operations."""

    count: int = 0
    total_original_tokens: int = 0
    total_optimized_tokens: int = 0
    total_savings: int = 0
    latency: LatencyStats = field(default_factory=LatencyStats)

    def record_optimization(
        self, original_tokens: int, optimized_tokens: int, latency_ms: float
    ) -> None:
        """Record optimization operation."""
        self.count += 1
        self.total_original_tokens += original_tokens
        self.total_optimized_tokens += optimized_tokens
        self.total_savings += original_tokens - optimized_tokens
        self.latency.record(latency_ms)

    def get_average_savings_percent(self) -> float:
        """Calculate average savings percentage."""
        if self.total_original_tokens == 0:
            return 0.0
        return self.total_savings / self.total_original_tokens * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "total_original_tokens": self.total_original_tokens,
            "total_optimized_tokens": self.total_optimized_tokens,
            "total_savings": self.total_savings,
            "avg_savings_percent": round(self.get_average_savings_percent(), 2),
            "latency": self.latency.to_dict(),
        }


@dataclass
class TruncationMetrics:
    """Metrics for truncation operations."""

    count: int = 0
    strategy_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_original_length: int = 0
    total_truncated_length: int = 0
    latency: LatencyStats = field(default_factory=LatencyStats)

    def record_truncation(
        self, strategy: str, original_length: int, truncated_length: int, latency_ms: float
    ) -> None:
        """Record truncation operation."""
        self.count += 1
        self.strategy_usage[strategy] += 1
        self.total_original_length += original_length
        self.total_truncated_length += truncated_length
        self.latency.record(latency_ms)

    def get_average_reduction_percent(self) -> float:
        """Calculate average reduction percentage."""
        if self.total_original_length == 0:
            return 0.0
        reduction = self.total_original_length - self.total_truncated_length
        return reduction / self.total_original_length * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "strategy_usage": dict(self.strategy_usage),
            "total_original_length": self.total_original_length,
            "total_truncated_length": self.total_truncated_length,
            "avg_reduction_percent": round(self.get_average_reduction_percent(), 2),
            "latency": self.latency.to_dict(),
        }


class MetricsCollector:
    """
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
    """

    def __init__(self):
        """Initialize metrics collector."""
        # Reentrant: get_metrics()/get_summary() hold the lock and then call
        # get_combined_cache_hit_rate(), which re-acquires it. A plain Lock
        # self-deadlocked on every get_metrics() call (previously misdiagnosed
        # as a "Python 3.14" issue and the tests were skipped).
        self._lock = RLock()
        self._start_time = time.time()

        # Cache metrics
        self.l1_cache = CacheMetrics()
        self.l2_cache = CacheMetrics()

        # Optimization metrics
        self.optimization = OptimizationMetrics()

        # Truncation metrics
        self.truncation = TruncationMetrics()

        # Error tracking
        self.errors: Dict[str, int] = defaultdict(int)

        # Request tracking
        self.total_requests = 0
        self.request_latency = LatencyStats()

    def record_cache_hit(self, cache_level: str, latency_ms: float) -> None:
        """
        Record cache hit.

        Args:
            cache_level: Cache level (L1 or L2)
            latency_ms: Lookup latency in milliseconds
        """
        with self._lock:
            if cache_level == "L1":
                self.l1_cache.record_hit(latency_ms)
            elif cache_level == "L2":
                self.l2_cache.record_hit(latency_ms)

    def record_cache_miss(self, cache_level: str) -> None:
        """
        Record cache miss.

        Args:
            cache_level: Cache level (L1 or L2)
        """
        with self._lock:
            if cache_level == "L1":
                self.l1_cache.record_miss()
            elif cache_level == "L2":
                self.l2_cache.record_miss()

    def record_cache_promotion(self) -> None:
        """Record L2 to L1 cache promotion."""
        with self._lock:
            self.l1_cache.record_promotion()

    def record_cache_eviction(self, cache_level: str) -> None:
        """
        Record cache eviction.

        Args:
            cache_level: Cache level (L1 or L2)
        """
        with self._lock:
            if cache_level == "L1":
                self.l1_cache.record_eviction()
            elif cache_level == "L2":
                self.l2_cache.record_eviction()

    def update_cache_size(self, cache_level: str, size: int) -> None:
        """
        Update cache size.

        Args:
            cache_level: Cache level (L1 or L2)
            size: Current cache size
        """
        with self._lock:
            if cache_level == "L1":
                self.l1_cache.size = size
            elif cache_level == "L2":
                self.l2_cache.size = size

    def record_optimization(
        self, original_tokens: int, optimized_tokens: int, latency_ms: float
    ) -> None:
        """
        Record optimization operation.

        Args:
            original_tokens: Original token count
            optimized_tokens: Optimized token count
            latency_ms: Optimization latency in milliseconds
        """
        with self._lock:
            self.optimization.record_optimization(original_tokens, optimized_tokens, latency_ms)

    def record_truncation(
        self, strategy: str, original_length: int, truncated_length: int, latency_ms: float
    ) -> None:
        """
        Record truncation operation.

        Args:
            strategy: Truncation strategy used
            original_length: Original text length
            truncated_length: Truncated text length
            latency_ms: Truncation latency in milliseconds
        """
        with self._lock:
            self.truncation.record_truncation(
                strategy, original_length, truncated_length, latency_ms
            )

    def record_request(self, latency_ms: float) -> None:
        """
        Record request completion.

        Args:
            latency_ms: Total request latency in milliseconds
        """
        with self._lock:
            self.total_requests += 1
            self.request_latency.record(latency_ms)

    def record_error(self, error_type: str) -> None:
        """
        Record error occurrence.

        Args:
            error_type: Type of error
        """
        with self._lock:
            self.errors[error_type] += 1

    def get_combined_cache_hit_rate(self) -> float:
        """
        Calculate combined cache hit rate.

        Returns:
            Combined hit rate percentage
        """
        with self._lock:
            total_hits = self.l1_cache.hits + self.l2_cache.hits
            total_requests = (
                self.l1_cache.hits
                + self.l1_cache.misses
                + self.l2_cache.hits
                + self.l2_cache.misses
            )
            return (total_hits / total_requests * 100) if total_requests > 0 else 0.0

    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.

        Returns:
            Dictionary containing all metrics
        """
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "uptime_seconds": round(self.get_uptime_seconds(), 2),
                "cache": {
                    "L1": self.l1_cache.to_dict(),
                    "L2": self.l2_cache.to_dict(),
                    "combined_hit_rate_percent": round(self.get_combined_cache_hit_rate(), 2),
                },
                "optimization": self.optimization.to_dict(),
                "truncation": self.truncation.to_dict(),
                "requests": {
                    "total": self.total_requests,
                    "latency": self.request_latency.to_dict(),
                },
                "errors": dict(self.errors),
            }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary metrics.

        Returns:
            Dictionary containing summary metrics
        """
        metrics = self.get_metrics()
        return {
            "uptime_seconds": metrics["uptime_seconds"],
            "total_requests": metrics["requests"]["total"],
            "cache_hit_rate_percent": metrics["cache"]["combined_hit_rate_percent"],
            "avg_token_savings_percent": metrics["optimization"]["avg_savings_percent"],
            "avg_request_latency_ms": metrics["requests"]["latency"]["avg_ms"],
            "total_errors": sum(metrics["errors"].values()),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._start_time = time.time()
            self.l1_cache = CacheMetrics()
            self.l2_cache = CacheMetrics()
            self.optimization = OptimizationMetrics()
            self.truncation = TruncationMetrics()
            self.errors.clear()
            self.total_requests = 0
            self.request_latency = LatencyStats()


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None
# Lock that serialises first-time singleton initialisation (C8 fix).
# Double-checked locking: the outer `is None` check avoids lock contention on
# every hot-path call; the inner check under the lock prevents two threads that
# both passed the outer check from each creating a separate instance.
_collector_init_lock = Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector instance.

    Returns:
        MetricsCollector instance
    """
    global _global_collector
    if _global_collector is None:
        with _collector_init_lock:
            if _global_collector is None:
                _global_collector = MetricsCollector()
    return _global_collector


def reset_metrics() -> None:
    """Reset global metrics collector."""
    global _global_collector
    if _global_collector is not None:
        _global_collector.reset()
