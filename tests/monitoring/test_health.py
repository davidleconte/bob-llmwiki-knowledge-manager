"""Tests for health check system."""

import threading
import time
from unittest.mock import Mock, patch

from src.monitoring.health import (
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
    get_health_checker,
    register_monitoring_health_check,
)


class TestHealthCheckResult:
    """Tests for HealthCheckResult."""

    def test_create_healthy_result(self):
        """Test creating a healthy result."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good"
        )

        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        assert result.is_healthy()

    def test_create_unhealthy_result(self):
        """Test creating an unhealthy result."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.UNHEALTHY,
            message="Something wrong"
        )

        assert not result.is_healthy()

    def test_result_with_details(self):
        """Test result with additional details."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            details={"metric": 42, "status": "ok"}
        )

        assert result.details["metric"] == 42
        assert result.details["status"] == "ok"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="OK",
            details={"key": "value"}
        )

        data = result.to_dict()

        assert data["name"] == "test_check"
        assert data["status"] == "healthy"
        assert data["message"] == "OK"
        assert data["details"]["key"] == "value"
        assert "timestamp" in data
        assert "duration_ms" in data


class TestSystemHealth:
    """Tests for SystemHealth."""

    def test_create_system_health(self):
        """Test creating system health."""
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY),
            HealthCheckResult("check2", HealthStatus.HEALTHY),
        ]

        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            checks=checks
        )

        assert health.status == HealthStatus.HEALTHY
        assert len(health.checks) == 2
        assert health.is_healthy()

    def test_unhealthy_system(self):
        """Test unhealthy system."""
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY),
            HealthCheckResult("check2", HealthStatus.UNHEALTHY),
        ]

        health = SystemHealth(
            status=HealthStatus.UNHEALTHY,
            checks=checks
        )

        assert not health.is_healthy()

    def test_to_dict(self):
        """Test converting system health to dictionary."""
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY),
        ]

        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            checks=checks
        )

        data = health.to_dict()

        assert data["status"] == "healthy"
        assert len(data["checks"]) == 1
        assert "timestamp" in data
        assert "version" in data


class TestHealthChecker:
    """Tests for HealthChecker."""

    def test_create_health_checker(self):
        """Test creating health checker."""
        checker = HealthChecker(check_interval=30.0)

        assert checker.check_interval == 30.0
        assert not checker.background_enabled
        assert len(checker.checks) == 0

    def test_register_check(self):
        """Test registering a health check."""
        checker = HealthChecker()

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        checker.register_check("my_check", my_check)

        assert "my_check" in checker.checks

    def test_unregister_check(self):
        """Test unregistering a health check."""
        checker = HealthChecker()

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        checker.register_check("my_check", my_check)
        checker.unregister_check("my_check")

        assert "my_check" not in checker.checks

    def test_run_single_check(self):
        """Test running a single health check."""
        checker = HealthChecker()

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY, "OK")

        checker.register_check("my_check", my_check)
        health = checker.check()

        assert health.status == HealthStatus.HEALTHY
        assert len(health.checks) == 1
        assert health.checks[0].name == "my_check"
        assert health.checks[0].message == "OK"

    def test_run_multiple_checks(self):
        """Test running multiple health checks."""
        checker = HealthChecker()

        def check1():
            return HealthCheckResult("check1", HealthStatus.HEALTHY)

        def check2():
            return HealthCheckResult("check2", HealthStatus.HEALTHY)

        checker.register_check("check1", check1)
        checker.register_check("check2", check2)

        health = checker.check()

        assert health.status == HealthStatus.HEALTHY
        assert len(health.checks) == 2

    def test_unhealthy_check_affects_overall_status(self):
        """Test that unhealthy check affects overall status."""
        checker = HealthChecker()

        def healthy_check():
            return HealthCheckResult("healthy", HealthStatus.HEALTHY)

        def unhealthy_check():
            return HealthCheckResult("unhealthy", HealthStatus.UNHEALTHY)

        checker.register_check("healthy", healthy_check)
        checker.register_check("unhealthy", unhealthy_check)

        health = checker.check()

        assert health.status == HealthStatus.UNHEALTHY
        assert not health.is_healthy()

    def test_degraded_status(self):
        """Test degraded status."""
        checker = HealthChecker()

        def healthy_check():
            return HealthCheckResult("healthy", HealthStatus.HEALTHY)

        def degraded_check():
            return HealthCheckResult("degraded", HealthStatus.DEGRADED)

        checker.register_check("healthy", healthy_check)
        checker.register_check("degraded", degraded_check)

        health = checker.check()

        assert health.status == HealthStatus.DEGRADED

    def test_check_specific_check(self):
        """Test running a specific check."""
        checker = HealthChecker()

        def check1():
            return HealthCheckResult("check1", HealthStatus.HEALTHY)

        def check2():
            return HealthCheckResult("check2", HealthStatus.HEALTHY)

        checker.register_check("check1", check1)
        checker.register_check("check2", check2)

        health = checker.check(name="check1")

        assert len(health.checks) == 1
        assert health.checks[0].name == "check1"

    def test_check_handles_exception(self):
        """Test that check handles exceptions gracefully."""
        checker = HealthChecker()

        def failing_check():
            raise RuntimeError("Check failed")

        checker.register_check("failing", failing_check)

        health = checker.check()

        assert health.status == HealthStatus.UNHEALTHY
        assert len(health.checks) == 1
        assert health.checks[0].status == HealthStatus.UNHEALTHY
        assert "Check failed" in health.checks[0].message

    def test_get_last_results(self):
        """Test getting cached results."""
        checker = HealthChecker()

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        checker.register_check("my_check", my_check)
        checker.check()

        results = checker.get_last_results()

        assert "my_check" in results
        assert results["my_check"].status == HealthStatus.HEALTHY

    def test_background_checks(self):
        """Test background health checking."""
        checker = HealthChecker(check_interval=0.1)

        check_count = {"count": 0}

        def counting_check():
            check_count["count"] += 1
            return HealthCheckResult("counter", HealthStatus.HEALTHY)

        checker.register_check("counter", counting_check)

        # Start background checks
        checker.start_background_checks()
        assert checker.background_enabled

        # Wait for a few checks
        time.sleep(0.35)

        # Stop background checks
        checker.stop_background_checks()
        assert not checker.background_enabled

        # Should have run at least 2-3 times
        assert check_count["count"] >= 2

    def test_background_checks_already_running(self):
        """Test starting background checks when already running."""
        checker = HealthChecker(check_interval=1.0)

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        checker.register_check("my_check", my_check)

        checker.start_background_checks()
        checker.start_background_checks()  # Should log warning

        checker.stop_background_checks()

    def test_stop_background_checks_when_not_running(self):
        """Test stopping background checks when not running."""
        checker = HealthChecker()
        checker.stop_background_checks()  # Should not raise


class TestGlobalHealthChecker:
    """Tests for global health checker."""

    def test_get_health_checker_singleton(self):
        """Test that get_health_checker returns singleton."""
        checker1 = get_health_checker()
        checker2 = get_health_checker()

        assert checker1 is checker2


class TestCacheHealthCheck:
    """Tests for cache health check registration."""

    def test_register_cache_health_check(self):
        """Test registering cache health check."""
        # Create mock cache
        mock_cache = Mock()
        mock_cache.stats.return_value = {
            'size': 50,
            'max_size': 100,
            'hit_rate': 75.0,
        }

        checker = HealthChecker()

        # Register check
        def check_cache():
            stats = mock_cache.stats()
            size = stats['size']
            max_size = stats['max_size']
            utilization = (size / max_size) * 100

            return HealthCheckResult(
                name="cache_L1",
                status=HealthStatus.HEALTHY,
                message=f"Cache operating normally ({utilization:.1f}% full)",
                details=stats
            )

        checker.register_check("cache_L1", check_cache)

        # Run check
        health = checker.check()

        assert health.status == HealthStatus.HEALTHY
        assert len(health.checks) == 1
        assert health.checks[0].details['size'] == 50
        assert health.checks[0].details['max_size'] == 100

    def test_cache_health_degraded_high_utilization(self):
        """Test cache health degraded when utilization high."""
        mock_cache = Mock()
        mock_cache.stats.return_value = {
            'size': 85,
            'max_size': 100,
            'hit_rate': 75.0,
        }

        checker = HealthChecker()

        def check_cache():
            stats = mock_cache.stats()
            size = stats['size']
            max_size = stats['max_size']
            utilization = (size / max_size) * 100

            if utilization >= 80:
                status = HealthStatus.DEGRADED
                message = f"Cache utilization high ({utilization:.1f}% full)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Cache operating normally ({utilization:.1f}% full)"

            return HealthCheckResult(
                name="cache_L1",
                status=status,
                message=message,
                details=stats
            )

        checker.register_check("cache_L1", check_cache)

        health = checker.check()

        assert health.status == HealthStatus.DEGRADED
        assert "high" in health.checks[0].message.lower()

    def test_cache_health_unhealthy_on_error(self):
        """Test cache health unhealthy when check fails."""
        mock_cache = Mock()
        mock_cache.stats.side_effect = RuntimeError("Cache error")

        checker = HealthChecker()

        def check_cache():
            try:
                mock_cache.stats()
                return HealthCheckResult("cache_L1", HealthStatus.HEALTHY)
            except Exception as e:
                return HealthCheckResult(
                    name="cache_L1",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Cache check failed: {str(e)}"
                )

        checker.register_check("cache_L1", check_cache)

        health = checker.check()

        assert health.status == HealthStatus.UNHEALTHY
        assert "failed" in health.checks[0].message.lower()


class TestSystemHealthCheck:
    """Tests for system health check."""

    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    def test_system_health_check_with_psutil(self, mock_cpu, mock_memory):
        """Test system health check with psutil available."""
        # Mock system metrics
        mock_memory.return_value = Mock(
            percent=50.0,
            available=4 * 1024 * 1024 * 1024  # 4GB
        )
        mock_cpu.return_value = 30.0

        checker = HealthChecker()

        def check_system():
            try:
                import psutil
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=0.1)

                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="System resources normal",
                    details={
                        "memory_percent": memory.percent,
                        "cpu_percent": cpu_percent,
                    }
                )
            except ImportError:
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="System monitoring unavailable"
                )

        checker.register_check("system_resources", check_system)

        health = checker.check()

        assert health.status == HealthStatus.HEALTHY
        assert health.checks[0].details["memory_percent"] == 50.0
        assert health.checks[0].details["cpu_percent"] == 30.0

    def test_system_health_check_without_psutil(self):
        """Test system health check without psutil."""
        checker = HealthChecker()

        def check_system():
            try:
                import psutil
                return HealthCheckResult("system_resources", HealthStatus.HEALTHY)
            except ImportError:
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="System monitoring unavailable (psutil not installed)",
                    details={"psutil_available": False}
                )

        checker.register_check("system_resources", check_system)

        # This will work regardless of whether psutil is installed
        health = checker.check()

        assert health.status == HealthStatus.HEALTHY


class TestMonitoringHealthCheck:
    """Tests for monitoring health check."""

    def test_monitoring_health_reflects_real_cache_operations(self):
        """The monitoring check must report REAL cache activity (C-8 regression).

        Previously ``check_monitoring_health`` read flat ``cache_hits`` /
        ``cache_misses`` keys that ``MetricsCollector.get_metrics()`` never
        exposes -- the real counts live nested under ``cache.L1``/``cache.L2``
        as ``hits``/``misses``. So ``total_operations`` was ALWAYS 0 and a busy
        system was reported as idle ("no operations yet"). This drives the real
        registered check against the real collector.
        """
        from src.monitoring.metrics import get_metrics_collector

        collector = get_metrics_collector()
        collector.reset()
        collector.record_cache_hit("L1", 1.0)
        collector.record_cache_hit("L1", 1.0)
        collector.record_cache_miss("L2")

        register_monitoring_health_check()
        checker = get_health_checker()
        health = checker.check("monitoring")

        monitoring = next(c for c in health.checks if c.name == "monitoring")
        # 2 L1 hits + 1 L2 miss = 3 real operations, not the always-0 default.
        assert monitoring.details["total_operations"] == 3
        assert monitoring.message == "Monitoring system operational"


class TestHealthCheckConcurrency:
    """Tests for health check thread-safety."""

    def test_concurrent_health_checks(self):
        """Test running health checks concurrently."""
        checker = HealthChecker()

        def my_check():
            time.sleep(0.01)  # Simulate work
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        checker.register_check("my_check", my_check)

        # Run checks concurrently
        results = []

        def run_check():
            health = checker.check()
            results.append(health)

        threads = [threading.Thread(target=run_check) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All checks should succeed
        assert len(results) == 10
        assert all(h.status == HealthStatus.HEALTHY for h in results)

    def test_concurrent_register_unregister(self):
        """Test concurrent register/unregister operations."""
        checker = HealthChecker()

        def my_check():
            return HealthCheckResult("my_check", HealthStatus.HEALTHY)

        def register_checks():
            for i in range(10):
                checker.register_check(f"check_{i}", my_check)

        def unregister_checks():
            time.sleep(0.01)
            for i in range(10):
                checker.unregister_check(f"check_{i}")

        t1 = threading.Thread(target=register_checks)
        t2 = threading.Thread(target=unregister_checks)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Should not crash
        health = checker.check()
        assert health is not None
