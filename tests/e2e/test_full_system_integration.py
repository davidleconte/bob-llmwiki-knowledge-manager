"""Simplified full system integration tests."""

import pytest

from src.cache import MultiLevelCache
from src.config import ConfigManager
from src.monitoring import get_metrics_collector
from src.optimizer import PromptOptimizer


class TestFullSystemIntegration:
    """Test suite for full system integration."""

    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        ConfigManager._instance = None
        manager = ConfigManager(environment='test')

        # Set up comprehensive configuration
        manager.update({
            'cache.l1.max_size': 500,
            'cache.l2.max_size': 5000,
            'cache.l1.enabled': True,
            'cache.l2.enabled': True,
            'optimizer.max_tokens': 4096,
            'optimizer.target_reduction': 0.3,
            'monitoring.enabled': True,
            'monitoring.metrics_enabled': True,
        })

        return manager

    def test_config_provides_values_to_all_components(self, config_manager):
        """Test configuration provides values to all system components."""
        cache_config = config_manager.get_cache_config()
        opt_config = config_manager.get_optimizer_config()
        mon_config = config_manager.get_monitoring_config()

        # Verify all configs are accessible
        assert cache_config.l1_max_size == 500
        assert cache_config.l2_max_size == 5000
        assert opt_config.max_tokens == 4096
        assert mon_config.enabled is True

    @pytest.mark.xfail(strict=True, reason="Phase 4: config not wired to runtime — PromptOptimizer rejects config kwarg")
    def test_cache_and_optimizer_work_together(self, config_manager):
        """Test cache and optimizer can work together."""
        cache_config = config_manager.get_cache_config()
        opt_config = config_manager.get_optimizer_config()

        cache = MultiLevelCache(
            l1_max_size=cache_config.l1_max_size,
            l2_max_size=cache_config.l2_max_size,
        )

        optimizer = PromptOptimizer(
            max_tokens=opt_config.max_tokens,
            target_reduction=opt_config.target_reduction,
        )

        # Optimize and cache
        prompt = "Test prompt"
        result = optimizer.optimize(prompt)
        cache.set('test_key', result['optimized_text'])

        # Retrieve from cache
        cached = cache.get('test_key')
        assert cached == result['optimized_text']

    def test_metrics_collector_tracks_operations(self, config_manager):
        """Test metrics collector tracks operations."""
        mon_config = config_manager.get_monitoring_config()
        assert mon_config.metrics_enabled is True

        metrics = get_metrics_collector()

        # Record some metrics
        metrics.record_cache_hit('L1', 0.5)
        metrics.record_optimization(100, 80, 5.0)

        stats = metrics.get_metrics()
        # get_metrics() nests under cache.<level> and optimization (C-8), not flat keys.
        assert stats['cache']['L1']['hits'] > 0
        assert stats['optimization']['count'] > 0

    def test_config_updates_affect_new_instances(self, config_manager):
        """Test configuration updates affect newly created instances."""
        # Initial config
        cache_config = config_manager.get_cache_config()
        cache1 = MultiLevelCache(l1_max_size=cache_config.l1_max_size)
        assert cache1.l1_cache.max_size == 500

        # Update config
        config_manager.update({'cache.l1.max_size': 1000})

        # New instance uses updated config
        cache_config = config_manager.get_cache_config()
        cache2 = MultiLevelCache(l1_max_size=cache_config.l1_max_size)
        assert cache2.l1_cache.max_size == 1000
