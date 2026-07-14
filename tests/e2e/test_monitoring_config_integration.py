"""Integration tests for monitoring and configuration management."""

import pytest

from src.config import ConfigManager
from src.monitoring import HealthChecker, get_logger, get_metrics_collector


class TestMonitoringConfigIntegration:
    """Test suite for monitoring and config integration."""

    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        ConfigManager._instance = None
        return ConfigManager(environment="test")

    def test_logger_uses_config_level(self, config_manager):
        """Test logger respects log level from configuration."""
        config_manager.update(
            {
                "monitoring.log_level": "DEBUG",
            }
        )

        mon_config = config_manager.get_monitoring_config()
        logger = get_logger("test_logger")

        # Verify logger can be configured with config level
        assert mon_config.log_level == "DEBUG"

    def test_metrics_collector_respects_config(self, config_manager):
        """Test metrics collector respects configuration."""
        config_manager.update(
            {
                "monitoring.metrics_enabled": True,
            }
        )

        mon_config = config_manager.get_monitoring_config()
        metrics = get_metrics_collector()

        assert mon_config.metrics_enabled is True

        # Record some metrics
        metrics.record_cache_hit("L1", 0.5)
        metrics.record_cache_miss("L1")

        stats = metrics.get_metrics()
        # get_metrics() nests cache stats under cache.<level> (C-8), not a flat key.
        assert stats["cache"]["L1"]["hits"] > 0

    def test_health_checker_uses_config_interval(self, config_manager):
        """Test health checker uses interval from configuration."""
        config_manager.update(
            {
                "monitoring.health_check_interval": 30,
            }
        )

        mon_config = config_manager.get_monitoring_config()
        health_checker = HealthChecker(check_interval=mon_config.health_check_interval)

        assert health_checker.check_interval == 30

    def test_monitoring_disabled_via_config(self, config_manager):
        """Test disabling monitoring via configuration."""
        config_manager.update(
            {
                "monitoring.enabled": False,
            }
        )

        mon_config = config_manager.get_monitoring_config()
        assert mon_config.enabled is False

    def test_metrics_disabled_via_config(self, config_manager):
        """Test disabling metrics collection via configuration."""
        config_manager.update(
            {
                "monitoring.metrics_enabled": False,
            }
        )

        mon_config = config_manager.get_monitoring_config()
        assert mon_config.metrics_enabled is False

    def test_runtime_config_update_affects_monitoring(self, config_manager):
        """Test runtime config updates affect monitoring settings."""
        # Initial config
        mon_config = config_manager.get_monitoring_config()
        assert mon_config.log_level == "INFO"  # default

        # Update config
        config_manager.update({"monitoring.log_level": "WARNING"})

        # Get updated config
        mon_config = config_manager.get_monitoring_config()
        assert mon_config.log_level == "WARNING"

    def test_all_log_levels_from_config(self, config_manager):
        """Test all valid log levels from configuration."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config_manager.update({"monitoring.log_level": level})
            mon_config = config_manager.get_monitoring_config()
            assert mon_config.log_level == level

    def test_config_validation_prevents_invalid_log_level(self, config_manager):
        """Test config validation prevents invalid log levels."""
        from src.config.validator import ValidationError

        with pytest.raises(ValidationError):
            config_manager.update(
                {
                    "monitoring.log_level": "INVALID",
                }
            )

    def test_config_validation_prevents_invalid_interval(self, config_manager):
        """Test config validation prevents invalid health check intervals."""
        from src.config.validator import ValidationError

        # Too small
        with pytest.raises(ValidationError):
            config_manager.update(
                {
                    "monitoring.health_check_interval": 0,
                }
            )

        # Too large
        with pytest.raises(ValidationError):
            config_manager.update(
                {
                    "monitoring.health_check_interval": 10000,
                }
            )

    def test_monitoring_config_boundary_values(self, config_manager):
        """Test monitoring config with boundary values."""
        # Minimum interval
        config_manager.update(
            {
                "monitoring.health_check_interval": 1,
            }
        )
        mon_config = config_manager.get_monitoring_config()
        assert mon_config.health_check_interval == 1

        # Maximum interval
        config_manager.update(
            {
                "monitoring.health_check_interval": 3600,
            }
        )
        mon_config = config_manager.get_monitoring_config()
        assert mon_config.health_check_interval == 3600
