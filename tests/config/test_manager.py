"""Tests for configuration manager."""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.config.manager import ConfigManager, get_config, ConfigVersion
from src.config.validator import ValidationError


class TestConfigManager:
    """Test suite for ConfigManager."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a fresh ConfigManager instance."""
        # Reset singleton
        ConfigManager._instance = None
        return ConfigManager(environment='test')
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                'cache': {
                    'l1': {
                        'max_size': 2000,
                        'ttl_seconds': 7200,
                        'enabled': True,
                    },
                    'l2': {
                        'max_size': 20000,
                        'ttl_seconds': 172800,
                        'similarity_threshold': 0.9,
                        'enabled': True,
                    },
                },
                'optimizer': {
                    'max_tokens': 8192,
                    'target_reduction': 0.4,
                    'min_quality_score': 0.85,
                    'strategies': ['remove_whitespace'],
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'DEBUG',
                    'metrics_enabled': True,
                    'health_check_interval': 30,
                },
            }
            json.dump(config, f)
            filepath = f.name
        
        yield filepath
        
        # Cleanup
        Path(filepath).unlink(missing_ok=True)
    
    def test_initialization(self, config_manager):
        """Test ConfigManager initialization."""
        assert config_manager.environment == 'test'
        assert config_manager._config is not None
        assert 'cache' in config_manager._config
        assert 'optimizer' in config_manager._config
        assert 'monitoring' in config_manager._config
    
    def test_default_configuration(self, config_manager):
        """Test default configuration values."""
        # Cache defaults
        assert config_manager.get('cache.l1.max_size') == 1000
        assert config_manager.get('cache.l1.ttl_seconds') == 3600
        assert config_manager.get('cache.l1.enabled') is True
        assert config_manager.get('cache.l2.max_size') == 10000
        assert config_manager.get('cache.l2.similarity_threshold') == 0.85
        
        # Optimizer defaults
        assert config_manager.get('optimizer.max_tokens') == 4096
        assert config_manager.get('optimizer.target_reduction') == 0.3
        
        # Monitoring defaults
        assert config_manager.get('monitoring.enabled') is True
        assert config_manager.get('monitoring.log_level') == 'INFO'
    
    def test_get_with_default(self, config_manager):
        """Test get method with default value."""
        assert config_manager.get('nonexistent.key', 'default') == 'default'
        assert config_manager.get('cache.l1.max_size', 999) == 1000
    
    def test_load_from_file(self, config_manager, temp_config_file):
        """Test loading configuration from file."""
        config_manager.load_from_file(temp_config_file)
        
        assert config_manager.get('cache.l1.max_size') == 2000
        assert config_manager.get('cache.l2.similarity_threshold') == 0.9
        assert config_manager.get('optimizer.max_tokens') == 8192
        assert config_manager.get('monitoring.log_level') == 'DEBUG'
    
    def test_load_from_nonexistent_file(self, config_manager):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            config_manager.load_from_file('/nonexistent/config.json')
    
    def test_load_from_invalid_file(self, config_manager):
        """Test loading invalid configuration raises ValidationError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Invalid config (L2 size smaller than L1)
            config = {
                'cache': {
                    'l1': {'max_size': 10000, 'ttl_seconds': 3600, 'enabled': True},
                    'l2': {'max_size': 1000, 'ttl_seconds': 86400, 'similarity_threshold': 0.85, 'enabled': True},
                },
                'optimizer': {
                    'max_tokens': 4096,
                    'target_reduction': 0.3,
                    'min_quality_score': 0.8,
                    'strategies': ['remove_whitespace'],
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'INFO',
                    'metrics_enabled': True,
                    'health_check_interval': 60,
                },
            }
            json.dump(config, f)
            filepath = f.name
        
        try:
            with pytest.raises(ValidationError):
                config_manager.load_from_file(filepath)
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_load_from_env(self, config_manager):
        """Test loading configuration from environment variables."""
        env_vars = {
            'CONFIG_CACHE__L1__MAX_SIZE': '3000',
            'CONFIG_OPTIMIZER__MAX_TOKENS': '16384',
            'CONFIG_MONITORING__LOG_LEVEL': 'WARNING',
        }
        
        with patch.dict(os.environ, env_vars):
            config_manager.load_from_env()
        
        assert config_manager.get('cache.l1.max_size') == 3000
        assert config_manager.get('optimizer.max_tokens') == 16384
        assert config_manager.get('monitoring.log_level') == 'WARNING'
    
    def test_update_configuration(self, config_manager):
        """Test runtime configuration updates."""
        updates = {
            'cache.l1.max_size': 5000,
            'optimizer.target_reduction': 0.5,
        }
        
        config_manager.update(updates)
        
        assert config_manager.get('cache.l1.max_size') == 5000
        assert config_manager.get('optimizer.target_reduction') == 0.5
    
    def test_update_invalid_configuration(self, config_manager):
        """Test updating with invalid values raises ValidationError."""
        with pytest.raises(ValidationError):
            config_manager.update({'cache.l1.max_size': -1})

    def test_update_rolls_back_on_validation_error(self, config_manager):
        """A failed update must not mutate the live config (atomicity, C-4).

        Previously update() merged into self._config *before* validating, with
        no rollback, so a ValidationError left the config corrupted.
        """
        original = config_manager.get('cache.l1.max_size')
        with pytest.raises(ValidationError):
            config_manager.update({'cache.l1.max_size': -1})
        # The invalid value must NOT have been committed.
        assert config_manager.get('cache.l1.max_size') == original
        # A subsequent valid update must still work (config not left corrupt).
        config_manager.update({'cache.l1.max_size': 2000})
        assert config_manager.get('cache.l1.max_size') == 2000

    def test_get_cache_config(self, config_manager):
        """Test getting cache configuration."""
        cache_config = config_manager.get_cache_config()
        
        assert cache_config.l1_max_size == 1000
        assert cache_config.l1_ttl_seconds == 3600
        assert cache_config.l1_enabled is True
        assert cache_config.l2_max_size == 10000
        assert cache_config.l2_similarity_threshold == 0.85
        assert cache_config.version_support_enabled is True
        assert cache_config.max_versions == 5
    
    def test_get_optimizer_config(self, config_manager):
        """Test getting optimizer configuration."""
        opt_config = config_manager.get_optimizer_config()
        
        assert opt_config.max_tokens == 4096
        assert opt_config.target_reduction == 0.3
        assert opt_config.min_quality_score == 0.8
        assert 'remove_whitespace' in opt_config.strategies
    
    def test_get_monitoring_config(self, config_manager):
        """Test getting monitoring configuration."""
        mon_config = config_manager.get_monitoring_config()
        
        assert mon_config.enabled is True
        assert mon_config.log_level == 'INFO'
        assert mon_config.metrics_enabled is True
        assert mon_config.health_check_interval == 60
    
    def test_get_all(self, config_manager):
        """Test getting complete configuration."""
        all_config = config_manager.get_all()
        
        assert 'cache' in all_config
        assert 'optimizer' in all_config
        assert 'monitoring' in all_config
        assert isinstance(all_config, dict)
    
    def test_get_schema(self, config_manager):
        """Test getting configuration schema."""
        schema = config_manager.get_schema()
        
        assert schema.cache is not None
        assert schema.optimizer is not None
        assert schema.monitoring is not None
    
    def test_version_tracking(self, config_manager):
        """Test configuration version tracking."""
        initial_versions = len(config_manager.get_version_history())
        
        config_manager.update({'cache.l1.max_size': 2000})
        
        history = config_manager.get_version_history()
        assert len(history) > initial_versions
        assert any('cache.l1.max_size=2000' in v['changes'] for v in history)
    
    def test_save_to_file(self, config_manager):
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'config.json'
            
            config_manager.update({'cache.l1.max_size': 3000})
            config_manager.save_to_file(str(filepath))
            
            assert filepath.exists()
            
            with open(filepath) as f:
                saved_config = json.load(f)
            
            assert saved_config['cache']['l1']['max_size'] == 3000
    
    def test_reset(self, config_manager):
        """Test resetting configuration to defaults."""
        config_manager.update({'cache.l1.max_size': 5000})
        assert config_manager.get('cache.l1.max_size') == 5000
        
        config_manager.reset()
        assert config_manager.get('cache.l1.max_size') == 1000
    
    def test_singleton_pattern(self):
        """Test ConfigManager singleton pattern."""
        ConfigManager._instance = None
        
        instance1 = ConfigManager.get_instance('test')
        instance2 = ConfigManager.get_instance('test')
        
        assert instance1 is instance2
    
    def test_thread_safety(self, config_manager):
        """Test thread-safe configuration updates."""
        results = []
        
        def update_config(value):
            try:
                config_manager.update({'cache.l1.max_size': value})
                results.append(config_manager.get('cache.l1.max_size'))
            except Exception as e:
                results.append(e)
        
        threads = [
            threading.Thread(target=update_config, args=(i * 1000,))
            for i in range(1, 6)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All updates should succeed
        assert all(isinstance(r, int) for r in results)
        assert len(results) == 5
    
    def test_get_config_global(self):
        """Test global get_config function."""
        config1 = get_config('test')
        config2 = get_config('test')
        
        assert config1 is config2
        assert isinstance(config1, ConfigManager)


class TestConfigVersion:
    """Test suite for ConfigVersion."""
    
    def test_config_version_creation(self):
        """Test creating ConfigVersion."""
        version = ConfigVersion(
            version='v1',
            timestamp=time.time(),
            changes=['cache.l1.max_size=2000'],
        )
        
        assert version.version == 'v1'
        assert version.timestamp > 0
        assert len(version.changes) == 1
