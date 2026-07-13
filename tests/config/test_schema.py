"""Tests for configuration schema."""

import pytest

from src.config.schema import (
    CacheConfig,
    OptimizerConfig,
    MonitoringConfig,
    ConfigSchema,
)


class TestCacheConfig:
    """Test suite for CacheConfig."""
    
    def test_default_values(self):
        """Test CacheConfig default values."""
        config = CacheConfig()
        
        assert config.l1_max_size == 1000
        assert config.l1_ttl_seconds == 3600
        assert config.l1_enabled is True
        assert config.l2_max_size == 10000
        assert config.l2_ttl_seconds == 86400
        assert config.l2_similarity_threshold == 0.85
        assert config.l2_enabled is True
        assert config.version_support_enabled is True
        assert config.max_versions == 5
    
    def test_custom_values(self):
        """Test CacheConfig with custom values."""
        config = CacheConfig(
            l1_max_size=2000,
            l1_ttl_seconds=7200,
            l1_enabled=False,
            l2_max_size=20000,
            l2_ttl_seconds=172800,
            l2_similarity_threshold=0.9,
            l2_enabled=False,
            version_support_enabled=False,
            max_versions=10,
        )
        
        assert config.l1_max_size == 2000
        assert config.l1_ttl_seconds == 7200
        assert config.l1_enabled is False
        assert config.l2_max_size == 20000
        assert config.l2_ttl_seconds == 172800
        assert config.l2_similarity_threshold == 0.9
        assert config.l2_enabled is False
        assert config.version_support_enabled is False
        assert config.max_versions == 10
    
    def test_partial_custom_values(self):
        """Test CacheConfig with partial custom values."""
        config = CacheConfig(
            l1_max_size=1500,
            l2_similarity_threshold=0.95,
        )
        
        assert config.l1_max_size == 1500
        assert config.l2_similarity_threshold == 0.95
        # Other values should be defaults
        assert config.l1_ttl_seconds == 3600
        assert config.l2_max_size == 10000


class TestOptimizerConfig:
    """Test suite for OptimizerConfig."""
    
    def test_default_values(self):
        """Test OptimizerConfig default values."""
        config = OptimizerConfig()
        
        assert config.max_tokens == 4096
        assert config.target_reduction == 0.3
        assert config.min_quality_score == 0.8
        assert config.strategies == ['remove_whitespace', 'compress_repeated']
    
    def test_custom_values(self):
        """Test OptimizerConfig with custom values."""
        config = OptimizerConfig(
            max_tokens=8192,
            target_reduction=0.5,
            min_quality_score=0.9,
            strategies=['remove_whitespace', 'remove_comments'],
        )
        
        assert config.max_tokens == 8192
        assert config.target_reduction == 0.5
        assert config.min_quality_score == 0.9
        assert config.strategies == ['remove_whitespace', 'remove_comments']
    
    def test_strategies_default_initialization(self):
        """Test strategies default initialization in __post_init__."""
        config = OptimizerConfig(
            max_tokens=4096,
            target_reduction=0.3,
            min_quality_score=0.8,
        )
        
        assert config.strategies is not None
        assert isinstance(config.strategies, list)
        assert len(config.strategies) > 0


class TestMonitoringConfig:
    """Test suite for MonitoringConfig."""
    
    def test_default_values(self):
        """Test MonitoringConfig default values."""
        config = MonitoringConfig()
        
        assert config.enabled is True
        assert config.log_level == 'INFO'
        assert config.metrics_enabled is True
        assert config.health_check_interval == 60
    
    def test_custom_values(self):
        """Test MonitoringConfig with custom values."""
        config = MonitoringConfig(
            enabled=False,
            log_level='DEBUG',
            metrics_enabled=False,
            health_check_interval=30,
        )
        
        assert config.enabled is False
        assert config.log_level == 'DEBUG'
        assert config.metrics_enabled is False
        assert config.health_check_interval == 30
    
    def test_log_levels(self):
        """Test different log levels."""
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            config = MonitoringConfig(log_level=level)
            assert config.log_level == level


class TestConfigSchema:
    """Test suite for ConfigSchema."""
    
    def test_creation(self):
        """Test ConfigSchema creation."""
        cache = CacheConfig()
        optimizer = OptimizerConfig()
        monitoring = MonitoringConfig()
        
        schema = ConfigSchema(
            cache=cache,
            optimizer=optimizer,
            monitoring=monitoring,
        )
        
        assert schema.cache is cache
        assert schema.optimizer is optimizer
        assert schema.monitoring is monitoring
    
    def test_with_custom_configs(self):
        """Test ConfigSchema with custom configurations."""
        cache = CacheConfig(l1_max_size=2000)
        optimizer = OptimizerConfig(max_tokens=8192)
        monitoring = MonitoringConfig(log_level='DEBUG')
        
        schema = ConfigSchema(
            cache=cache,
            optimizer=optimizer,
            monitoring=monitoring,
        )
        
        assert schema.cache.l1_max_size == 2000
        assert schema.optimizer.max_tokens == 8192
        assert schema.monitoring.log_level == 'DEBUG'
    
    def test_nested_access(self):
        """Test accessing nested configuration values."""
        schema = ConfigSchema(
            cache=CacheConfig(l1_max_size=1500),
            optimizer=OptimizerConfig(target_reduction=0.4),
            monitoring=MonitoringConfig(health_check_interval=45),
        )
        
        # Access nested values
        assert schema.cache.l1_max_size == 1500
        assert schema.cache.l2_similarity_threshold == 0.85  # default
        assert schema.optimizer.target_reduction == 0.4
        assert schema.optimizer.min_quality_score == 0.8  # default
        assert schema.monitoring.health_check_interval == 45
        assert schema.monitoring.enabled is True  # default
