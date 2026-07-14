"""Minimal integration tests for configuration management."""

import pytest

from src.cache import ExactCache, MultiLevelCache, SemanticCache
from src.config import ConfigManager


class TestConfigIntegrationMinimal:
    """Minimal integration tests focusing on configuration."""

    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        ConfigManager._instance = None
        return ConfigManager(environment='test')

    def test_cache_config_integration(self, config_manager):
        """Test cache configuration integration."""
        config_manager.update({
            'cache.l1.max_size': 500,
            'cache.l2.max_size': 5000,
        })

        cache_config = config_manager.get_cache_config()

        # Create caches with config
        l1 = ExactCache(max_size=cache_config.l1_max_size)
        l2 = SemanticCache(max_size=cache_config.l2_max_size)

        assert l1.max_size == 500
        assert l2.max_size == 5000

    def test_multilevel_cache_config_integration(self, config_manager):
        """Test multilevel cache configuration integration."""
        config_manager.update({
            'cache.l1.max_size': 300,
            'cache.l2.max_size': 3000,
        })

        cache_config = config_manager.get_cache_config()
        cache = MultiLevelCache(
            l1_max_size=cache_config.l1_max_size,
            l2_max_size=cache_config.l2_max_size,
        )

        assert cache.l1_cache.max_size == 300
        assert cache.l2_cache.max_size == 3000

    def test_optimizer_config_values(self, config_manager):
        """Test optimizer configuration values."""
        config_manager.update({
            'optimizer.max_tokens': 8192,
            'optimizer.target_reduction': 0.4,
        })

        opt_config = config_manager.get_optimizer_config()

        assert opt_config.max_tokens == 8192
        assert opt_config.target_reduction == 0.4

    def test_monitoring_config_values(self, config_manager):
        """Test monitoring configuration values."""
        config_manager.update({
            'monitoring.log_level': 'DEBUG',
            'monitoring.health_check_interval': 30,
        })

        mon_config = config_manager.get_monitoring_config()

        assert mon_config.log_level == 'DEBUG'
        assert mon_config.health_check_interval == 30

    def test_config_validation_integration(self, config_manager):
        """Test configuration validation integration."""
        from src.config.validator import ValidationError

        # Invalid config should be rejected
        with pytest.raises(ValidationError):
            config_manager.update({
                'cache.l1.max_size': 10000,
                'cache.l2.max_size': 1000,  # L2 < L1 (invalid)
            })

    def test_config_version_tracking(self, config_manager):
        """Test configuration version tracking."""
        initial_versions = len(config_manager.get_version_history())

        config_manager.update({'cache.l1.max_size': 2000})

        history = config_manager.get_version_history()
        assert len(history) > initial_versions

    def test_all_component_configs_accessible(self, config_manager):
        """Test all component configurations are accessible."""
        cache_config = config_manager.get_cache_config()
        opt_config = config_manager.get_optimizer_config()
        mon_config = config_manager.get_monitoring_config()

        # All configs should be accessible
        assert cache_config is not None
        assert opt_config is not None
        assert mon_config is not None

        # All should have expected attributes
        assert hasattr(cache_config, 'l1_max_size')
        assert hasattr(opt_config, 'max_tokens')
        assert hasattr(mon_config, 'log_level')
