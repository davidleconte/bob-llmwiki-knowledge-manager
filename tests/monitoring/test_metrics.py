"""
Tests for the metrics collection module.
"""

import threading
import time

import pytest

from src.monitoring.metrics import (
    CacheMetrics,
    LatencyStats,
    MetricsCollector,
    OptimizationMetrics,
    TruncationMetrics,
    get_metrics_collector,
    reset_metrics,
)


class TestLatencyStats:
    """Test LatencyStats class."""

    def test_initialization(self):
        """Test latency stats initialization."""
        stats = LatencyStats()
        assert stats.count == 0
        assert stats.total == 0.0
        assert stats.min == float("inf")
        assert stats.max == 0.0

    def test_record_single(self):
        """Test recording single latency."""
        stats = LatencyStats()
        stats.record(10.5)

        assert stats.count == 1
        assert stats.total == 10.5
        assert stats.min == 10.5
        assert stats.max == 10.5

    def test_record_multiple(self):
        """Test recording multiple latencies."""
        stats = LatencyStats()
        stats.record(10.0)
        stats.record(20.0)
        stats.record(15.0)

        assert stats.count == 3
        assert stats.total == 45.0
        assert stats.min == 10.0
        assert stats.max == 20.0

    def test_get_average(self):
        """Test average calculation."""
        stats = LatencyStats()
        stats.record(10.0)
        stats.record(20.0)
        stats.record(30.0)

        assert stats.get_average() == 20.0

    def test_get_average_empty(self):
        """Test average with no data."""
        stats = LatencyStats()
        assert stats.get_average() == 0.0

    def test_percentiles(self):
        """Test percentile calculations."""
        stats = LatencyStats()
        for i in range(100):
            stats.record(float(i))

        assert stats.p50 == pytest.approx(49.5, rel=0.1)
        assert stats.p95 >= 90
        assert stats.p99 >= 95

    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = LatencyStats()
        stats.record(10.0)
        stats.record(20.0)

        data = stats.to_dict()
        assert data["count"] == 2
        assert data["avg_ms"] == 15.0
        assert data["min_ms"] == 10.0
        assert data["max_ms"] == 20.0


class TestCacheMetrics:
    """Test CacheMetrics class."""

    def test_initialization(self):
        """Test cache metrics initialization."""
        metrics = CacheMetrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.promotions == 0
        assert metrics.evictions == 0

    def test_record_hit(self):
        """Test recording cache hit."""
        metrics = CacheMetrics()
        metrics.record_hit(5.0)

        assert metrics.hits == 1
        assert metrics.latency.count == 1

    def test_record_miss(self):
        """Test recording cache miss."""
        metrics = CacheMetrics()
        metrics.record_miss()

        assert metrics.misses == 1

    def test_record_promotion(self):
        """Test recording cache promotion."""
        metrics = CacheMetrics()
        metrics.record_promotion()

        assert metrics.promotions == 1

    def test_record_eviction(self):
        """Test recording cache eviction."""
        metrics = CacheMetrics()
        metrics.record_eviction()

        assert metrics.evictions == 1

    def test_get_hit_rate(self):
        """Test hit rate calculation."""
        metrics = CacheMetrics()
        metrics.record_hit(1.0)
        metrics.record_hit(1.0)
        metrics.record_miss()

        assert metrics.get_hit_rate() == pytest.approx(66.67, rel=0.01)

    def test_get_hit_rate_no_requests(self):
        """Test hit rate with no requests."""
        metrics = CacheMetrics()
        assert metrics.get_hit_rate() == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = CacheMetrics()
        metrics.record_hit(5.0)
        metrics.record_miss()
        metrics.size = 100

        data = metrics.to_dict()
        assert data["hits"] == 1
        assert data["misses"] == 1
        assert data["total_requests"] == 2
        assert data["size"] == 100


class TestOptimizationMetrics:
    """Test OptimizationMetrics class."""

    def test_initialization(self):
        """Test optimization metrics initialization."""
        metrics = OptimizationMetrics()
        assert metrics.count == 0
        assert metrics.total_original_tokens == 0
        assert metrics.total_optimized_tokens == 0

    def test_record_optimization(self):
        """Test recording optimization."""
        metrics = OptimizationMetrics()
        metrics.record_optimization(1000, 800, 10.0)

        assert metrics.count == 1
        assert metrics.total_original_tokens == 1000
        assert metrics.total_optimized_tokens == 800
        assert metrics.total_savings == 200

    def test_get_average_savings_percent(self):
        """Test average savings calculation."""
        metrics = OptimizationMetrics()
        metrics.record_optimization(1000, 800, 10.0)
        metrics.record_optimization(2000, 1600, 15.0)

        # Total: 3000 original, 2400 optimized, 600 saved
        # Savings: 600/3000 = 20%
        assert metrics.get_average_savings_percent() == 20.0

    def test_get_average_savings_percent_no_data(self):
        """Test average savings with no data."""
        metrics = OptimizationMetrics()
        assert metrics.get_average_savings_percent() == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = OptimizationMetrics()
        metrics.record_optimization(1000, 800, 10.0)

        data = metrics.to_dict()
        assert data["count"] == 1
        assert data["total_original_tokens"] == 1000
        assert data["total_optimized_tokens"] == 800
        assert data["total_savings"] == 200


class TestTruncationMetrics:
    """Test TruncationMetrics class."""

    def test_initialization(self):
        """Test truncation metrics initialization."""
        metrics = TruncationMetrics()
        assert metrics.count == 0
        assert len(metrics.strategy_usage) == 0

    def test_record_truncation(self):
        """Test recording truncation."""
        metrics = TruncationMetrics()
        metrics.record_truncation("priority", 1000, 600, 5.0)

        assert metrics.count == 1
        assert metrics.strategy_usage["priority"] == 1
        assert metrics.total_original_length == 1000
        assert metrics.total_truncated_length == 600

    def test_strategy_usage_tracking(self):
        """Test strategy usage tracking."""
        metrics = TruncationMetrics()
        metrics.record_truncation("priority", 1000, 600, 5.0)
        metrics.record_truncation("simple", 500, 300, 3.0)
        metrics.record_truncation("priority", 800, 500, 4.0)

        assert metrics.strategy_usage["priority"] == 2
        assert metrics.strategy_usage["simple"] == 1

    def test_get_average_reduction_percent(self):
        """Test average reduction calculation."""
        metrics = TruncationMetrics()
        metrics.record_truncation("priority", 1000, 600, 5.0)
        metrics.record_truncation("simple", 1000, 800, 3.0)

        # Total: 2000 original, 1400 truncated, 600 reduced
        # Reduction: 600/2000 = 30%
        assert metrics.get_average_reduction_percent() == 30.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = TruncationMetrics()
        metrics.record_truncation("priority", 1000, 600, 5.0)

        data = metrics.to_dict()
        assert data["count"] == 1
        assert data["strategy_usage"]["priority"] == 1


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert collector.total_requests == 0
        assert collector.l1_cache.hits == 0
        assert collector.l2_cache.hits == 0

    def test_record_cache_hit_l1(self):
        """Test recording L1 cache hit."""
        collector = MetricsCollector()
        collector.record_cache_hit("L1", 0.5)

        assert collector.l1_cache.hits == 1
        assert collector.l2_cache.hits == 0

    def test_record_cache_hit_l2(self):
        """Test recording L2 cache hit."""
        collector = MetricsCollector()
        collector.record_cache_hit("L2", 50.0)

        assert collector.l1_cache.hits == 0
        assert collector.l2_cache.hits == 1

    def test_record_cache_miss(self):
        """Test recording cache miss."""
        collector = MetricsCollector()
        collector.record_cache_miss("L1")
        collector.record_cache_miss("L2")

        assert collector.l1_cache.misses == 1
        assert collector.l2_cache.misses == 1

    def test_record_cache_promotion(self):
        """Test recording cache promotion."""
        collector = MetricsCollector()
        collector.record_cache_promotion()

        assert collector.l1_cache.promotions == 1

    def test_record_cache_eviction(self):
        """Test recording cache eviction."""
        collector = MetricsCollector()
        collector.record_cache_eviction("L1")

        assert collector.l1_cache.evictions == 1

    def test_update_cache_size(self):
        """Test updating cache size."""
        collector = MetricsCollector()
        collector.update_cache_size("L1", 100)
        collector.update_cache_size("L2", 50)

        assert collector.l1_cache.size == 100
        assert collector.l2_cache.size == 50

    def test_record_optimization(self):
        """Test recording optimization."""
        collector = MetricsCollector()
        collector.record_optimization(1000, 800, 10.0)

        assert collector.optimization.count == 1
        assert collector.optimization.total_savings == 200

    def test_record_truncation(self):
        """Test recording truncation."""
        collector = MetricsCollector()
        collector.record_truncation("priority", 1000, 600, 5.0)

        assert collector.truncation.count == 1
        assert collector.truncation.strategy_usage["priority"] == 1

    def test_record_request(self):
        """Test recording request."""
        collector = MetricsCollector()
        collector.record_request(100.0)

        assert collector.total_requests == 1
        assert collector.request_latency.count == 1

    def test_record_error(self):
        """Test recording error."""
        collector = MetricsCollector()
        collector.record_error("ValueError")
        collector.record_error("ValueError")
        collector.record_error("TypeError")

        assert collector.errors["ValueError"] == 2
        assert collector.errors["TypeError"] == 1

    def test_get_combined_cache_hit_rate(self):
        """Test combined cache hit rate calculation."""
        collector = MetricsCollector()
        collector.record_cache_hit("L1", 0.5)
        collector.record_cache_hit("L1", 0.5)
        collector.record_cache_miss("L1")
        collector.record_cache_hit("L2", 50.0)
        collector.record_cache_miss("L2")

        # 3 hits, 2 misses = 60%
        assert collector.get_combined_cache_hit_rate() == 60.0

    def test_get_uptime_seconds(self):
        """Test uptime calculation."""
        collector = MetricsCollector()
        time.sleep(0.1)
        uptime = collector.get_uptime_seconds()
        assert uptime >= 0.1

    def test_get_metrics(self):
        """get_metrics() must return without deadlocking (C-8b regression).

        Previously ``get_metrics()`` held ``self._lock`` (a non-reentrant Lock)
        and then called ``get_combined_cache_hit_rate()``, which re-acquired the
        same lock -> permanent self-deadlock on EVERY call. It was misdiagnosed
        as a "Python 3.14" issue and skipped. We now run it in a worker thread
        with a bounded join so a regression fails fast instead of hanging the
        whole suite.
        """
        collector = MetricsCollector()
        collector.record_cache_hit("L1", 0.5)
        collector.record_cache_hit("L1", 0.5)
        collector.record_cache_miss("L2")
        collector.record_optimization(1000, 800, 10.0)
        collector.record_truncation("priority", 1000, 600, 5.0)
        collector.record_request(100.0)

        box = {}
        done = threading.Event()

        def _run():
            box["metrics"] = collector.get_metrics()
            done.set()

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        assert done.wait(timeout=5.0), (
            "get_metrics() deadlocked: self._lock re-acquired under itself"
        )

        metrics = box["metrics"]
        for key in (
            "timestamp",
            "uptime_seconds",
            "cache",
            "optimization",
            "truncation",
            "requests",
            "errors",
        ):
            assert key in metrics
        # The nested cache structure the health check depends on (C-8).
        assert metrics["cache"]["L1"]["hits"] == 2
        assert metrics["cache"]["L2"]["misses"] == 1
        # combined_hit_rate is exactly the path that used to deadlock: 2/3.
        assert metrics["cache"]["combined_hit_rate_percent"] == pytest.approx(66.67, abs=0.01)

    def test_get_summary(self):
        """get_summary() must not deadlock (C-8b regression; it calls get_metrics())."""
        collector = MetricsCollector()
        collector.record_cache_hit("L1", 0.5)
        collector.record_optimization(1000, 800, 10.0)
        collector.record_request(100.0)

        box = {}
        done = threading.Event()

        def _run():
            box["summary"] = collector.get_summary()
            done.set()

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        assert done.wait(timeout=5.0), "get_summary() deadlocked via get_metrics()"

        summary = box["summary"]
        for key in (
            "uptime_seconds",
            "total_requests",
            "cache_hit_rate_percent",
            "avg_token_savings_percent",
            "avg_request_latency_ms",
            "total_errors",
        ):
            assert key in summary

    def test_reset(self):
        """Test resetting metrics."""
        collector = MetricsCollector()
        collector.record_cache_hit("L1", 0.5)
        collector.record_optimization(1000, 800, 10.0)
        collector.record_request(100.0)

        collector.reset()

        assert collector.total_requests == 0
        assert collector.l1_cache.hits == 0
        assert collector.optimization.count == 0

    def test_thread_safety(self):
        """Concurrent recording is thread-safe (RLock; C-8b).

        Previously skipped as a "Python 3.14 hang" — the same misdiagnosis as
        ``get_metrics()``; the real cause was the non-reentrant lock, fixed by
        the RLock. Re-enabled and bounded by the suite ``--timeout``.
        """
        collector = MetricsCollector()

        def record_hits():
            for _ in range(100):
                collector.record_cache_hit("L1", 0.5)

        threads = [threading.Thread(target=record_hits) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert collector.l1_cache.hits == 1000


class TestGlobalFunctions:
    """Test global convenience functions.

    Formerly skipped for "state pollution" across the process-global
    singleton; the autouse ``_reset_monitoring_singletons`` fixture (plus this
    class's own ``setup_method`` reset) now isolates each test, so these run.
    """

    def setup_method(self):
        """Reset global state before each test."""
        reset_metrics()

    def test_get_metrics_collector(self):
        """Test getting global metrics collector."""
        collector = get_metrics_collector()
        assert isinstance(collector, MetricsCollector)

    def test_get_metrics_collector_singleton(self):
        """Test that global collector is singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        assert collector1 is collector2

    def test_reset_metrics(self):
        """Test resetting global metrics."""
        collector = get_metrics_collector()
        collector.record_cache_hit("L1", 0.5)

        reset_metrics()

        assert collector.l1_cache.hits == 0
