"""Integration tests for cache and configuration management."""

import pytest

from src.cache import ExactCache, MultiLevelCache, SemanticCache
from src.config import ConfigManager


class TestCacheConfigIntegration:
    """Test suite for cache and config integration."""

    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        ConfigManager._instance = None
        return ConfigManager(environment="test")

    def test_l1_cache_uses_config(self, config_manager):
        """Test L1 cache respects configuration settings."""
        # Update config
        config_manager.update(
            {
                "cache.l1.max_size": 500,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = ExactCache(
            max_size=cache_config.l1_max_size,
        )

        # Verify cache uses config values
        assert cache.max_size == 500

    def test_l2_cache_uses_config(self, config_manager):
        """Test L2 cache respects configuration settings."""
        config_manager.update(
            {
                "cache.l2.max_size": 5000,
                "cache.l2.similarity_threshold": 0.9,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = SemanticCache(
            max_size=cache_config.l2_max_size,
            similarity_threshold=cache_config.l2_similarity_threshold,
        )

        assert cache.max_size == 5000
        assert cache.similarity_threshold == 0.9

    def test_multilevel_cache_uses_config(self, config_manager):
        """Test MultiLevelCache respects configuration settings."""
        config_manager.update(
            {
                "cache.l1.max_size": 300,
                "cache.l2.max_size": 3000,
                "cache.l1.enabled": True,
                "cache.l2.enabled": True,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = MultiLevelCache(
            l1_max_size=cache_config.l1_max_size,
            l2_max_size=cache_config.l2_max_size,
            l1_enabled=cache_config.l1_enabled,
            l2_enabled=cache_config.l2_enabled,
        )

        assert cache.l1_cache.max_size == 300
        assert cache.l2_cache.max_size == 3000

    def test_runtime_config_update_affects_new_cache(self, config_manager):
        """Test runtime config updates affect newly created caches."""
        # Create cache with initial config
        cache_config = config_manager.get_cache_config()
        cache1 = ExactCache(max_size=cache_config.l1_max_size)
        assert cache1.max_size == 1000  # default

        # Update config
        config_manager.update({"cache.l1.max_size": 2000})

        # Create new cache with updated config
        cache_config = config_manager.get_cache_config()
        cache2 = ExactCache(max_size=cache_config.l1_max_size)
        assert cache2.max_size == 2000

        # Old cache unchanged
        assert cache1.max_size == 1000

    def test_cache_with_version_support_config(self, config_manager):
        """Test cache version support respects configuration."""
        config_manager.update(
            {
                "cache.version_support.enabled": True,
                "cache.version_support.max_versions": 3,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = ExactCache(max_size=cache_config.l1_max_size)

        # Test version support
        cache.set("key1", "value1", version="v1")
        cache.set("key1", "value2", version="v2")
        cache.set("key1", "value3", version="v3")

        assert cache.get("key1", version="v1") == "value1"
        assert cache.get("key1", version="v2") == "value2"
        assert cache.get("key1", version="v3") == "value3"

    def test_cache_disabled_via_config(self, config_manager):
        """Test disabling cache levels via configuration."""
        config_manager.update(
            {
                "cache.l1.enabled": False,
                "cache.l2.enabled": True,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = MultiLevelCache(
            l1_enabled=cache_config.l1_enabled,
            l2_enabled=cache_config.l2_enabled,
        )

        # L1 disabled, operations should still work
        cache.set("key1", "value1")
        result = cache.get("key1")
        assert result == "value1"

    def test_config_respects_cache_sizes(self, config_manager):
        """Test cache respects size configuration."""
        config_manager.update(
            {
                "cache.l1.max_size": 100,
            }
        )

        cache_config = config_manager.get_cache_config()
        cache = ExactCache(max_size=cache_config.l1_max_size)

        assert cache.max_size == 100

    def test_config_validation_prevents_invalid_cache_config(self, config_manager):
        """Test config validation prevents invalid cache configurations."""
        from src.config.validator import ValidationError

        # Try to set L2 smaller than L1 (should fail)
        with pytest.raises(ValidationError):
            config_manager.update(
                {
                    "cache.l1.max_size": 10000,
                    "cache.l2.max_size": 1000,
                }
            )

    def test_multiple_caches_share_config(self, config_manager):
        """Test multiple cache instances can share configuration."""
        config_manager.update(
            {
                "cache.l1.max_size": 750,
                "cache.l2.max_size": 7500,
            }
        )

        cache_config = config_manager.get_cache_config()

        # Create multiple caches with same config
        cache1 = MultiLevelCache(
            l1_max_size=cache_config.l1_max_size,
            l2_max_size=cache_config.l2_max_size,
        )
        cache2 = MultiLevelCache(
            l1_max_size=cache_config.l1_max_size,
            l2_max_size=cache_config.l2_max_size,
        )

        assert cache1.l1_cache.max_size == cache2.l1_cache.max_size == 750
        assert cache1.l2_cache.max_size == cache2.l2_cache.max_size == 7500
