"""Tests for configuration validator."""

import pytest

from src.config.validator import ConfigValidator, ValidationError


class TestConfigValidator:
    """Test suite for ConfigValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a ConfigValidator instance."""
        return ConfigValidator()
    
    @pytest.fixture
    def valid_config(self):
        """Create a valid configuration."""
        return {
            'cache': {
                'l1': {
                    'max_size': 1000,
                    'ttl_seconds': 3600,
                    'enabled': True,
                },
                'l2': {
                    'max_size': 10000,
                    'ttl_seconds': 86400,
                    'similarity_threshold': 0.85,
                    'enabled': True,
                },
                'version_support': {
                    'enabled': True,
                    'max_versions': 5,
                },
            },
            'optimizer': {
                'max_tokens': 4096,
                'target_reduction': 0.3,
                'min_quality_score': 0.8,
                'strategies': ['remove_whitespace', 'compress_repeated'],
            },
            'monitoring': {
                'enabled': True,
                'log_level': 'INFO',
                'metrics_enabled': True,
                'health_check_interval': 60,
            },
        }
    
    def test_valid_configuration(self, validator, valid_config):
        """Test validation of valid configuration."""
        # Should not raise any exception
        validator.validate(valid_config)
    
    def test_missing_required_field(self, validator, valid_config):
        """Test validation fails for missing required field."""
        del valid_config['cache']['l1']['max_size']
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'Missing required field' in str(exc_info.value)
        assert 'cache.l1.max_size' in str(exc_info.value)
    
    def test_invalid_type(self, validator, valid_config):
        """Test validation fails for invalid type."""
        valid_config['cache']['l1']['max_size'] = '1000'  # Should be int
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'Invalid type' in str(exc_info.value)
    
    def test_value_below_minimum(self, validator, valid_config):
        """Test validation fails for value below minimum."""
        valid_config['cache']['l1']['max_size'] = 0
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'below minimum' in str(exc_info.value)
    
    def test_value_above_maximum(self, validator, valid_config):
        """Test validation fails for value above maximum."""
        valid_config['cache']['l1']['max_size'] = 200000
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'exceeds maximum' in str(exc_info.value)
    
    def test_invalid_log_level(self, validator, valid_config):
        """Test validation fails for invalid log level."""
        valid_config['monitoring']['log_level'] = 'INVALID'
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'Invalid value' in str(exc_info.value)
        assert 'log_level' in str(exc_info.value)
    
    def test_invalid_strategy(self, validator, valid_config):
        """Test validation fails for invalid strategy."""
        valid_config['optimizer']['strategies'] = ['invalid_strategy']
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'Invalid values' in str(exc_info.value)
    
    def test_empty_strategies_list(self, validator, valid_config):
        """Test validation fails for empty strategies list."""
        valid_config['optimizer']['strategies'] = []
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'too short' in str(exc_info.value)
    
    def test_l2_smaller_than_l1(self, validator, valid_config):
        """Test validation fails when L2 cache is smaller than L1."""
        valid_config['cache']['l1']['max_size'] = 10000
        valid_config['cache']['l2']['max_size'] = 1000
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'L2 cache size' in str(exc_info.value)
        assert 'must be larger' in str(exc_info.value)
    
    def test_l2_ttl_shorter_than_l1(self, validator, valid_config):
        """Test validation fails when L2 TTL is shorter than L1."""
        valid_config['cache']['l1']['ttl_seconds'] = 86400
        valid_config['cache']['l2']['ttl_seconds'] = 3600
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'L2 cache TTL' in str(exc_info.value)
        assert 'must be longer' in str(exc_info.value)
    
    def test_aggressive_reduction_with_high_quality(self, validator, valid_config):
        """Test validation fails for aggressive reduction with high quality requirement."""
        valid_config['optimizer']['target_reduction'] = 0.8
        valid_config['optimizer']['min_quality_score'] = 0.95
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'too aggressive' in str(exc_info.value)
    
    def test_version_support_validation(self, validator, valid_config):
        """Test validation of version support settings."""
        valid_config['cache']['version_support']['max_versions'] = 1
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'max_versions' in str(exc_info.value)
        assert 'at least 2' in str(exc_info.value)
    
    def test_optional_version_support(self, validator, valid_config):
        """Test that version_support is optional."""
        del valid_config['cache']['version_support']
        
        # Should not raise exception
        validator.validate(valid_config)
    
    def test_version_support_disabled(self, validator, valid_config):
        """Test version support can be disabled."""
        valid_config['cache']['version_support']['enabled'] = False
        valid_config['cache']['version_support']['max_versions'] = 1
        
        # Should not raise exception when disabled
        validator.validate(valid_config)
    
    def test_multiple_validation_errors(self, validator, valid_config):
        """Test multiple validation errors are reported."""
        valid_config['cache']['l1']['max_size'] = -1
        valid_config['monitoring']['log_level'] = 'INVALID'
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        error_msg = str(exc_info.value)
        # Should contain multiple errors
        assert 'below minimum' in error_msg or 'Invalid value' in error_msg
    
    def test_valid_log_levels(self, validator, valid_config):
        """Test all valid log levels."""
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            valid_config['monitoring']['log_level'] = level
            validator.validate(valid_config)
    
    def test_valid_strategies(self, validator, valid_config):
        """Test all valid strategies."""
        strategies = [
            ['remove_whitespace'],
            ['compress_repeated'],
            ['remove_comments'],
            ['shorten_names'],
            ['remove_whitespace', 'compress_repeated'],
            ['remove_whitespace', 'compress_repeated', 'remove_comments', 'shorten_names'],
        ]
        
        for strategy_list in strategies:
            valid_config['optimizer']['strategies'] = strategy_list
            validator.validate(valid_config)
    
    def test_boundary_values(self, validator, valid_config):
        """Test boundary values for numeric fields."""
        # Test minimum values
        valid_config['cache']['l1']['max_size'] = 1
        valid_config['cache']['l2']['max_size'] = 2  # Must be larger than L1
        valid_config['cache']['l1']['ttl_seconds'] = 1
        valid_config['cache']['l2']['ttl_seconds'] = 2  # Must be longer than L1
        validator.validate(valid_config)
        
        # Test maximum values
        valid_config['cache']['l1']['max_size'] = 100000
        valid_config['cache']['l2']['max_size'] = 1000000
        valid_config['cache']['l1']['ttl_seconds'] = 86400 * 7
        valid_config['cache']['l2']['ttl_seconds'] = 86400 * 30
        validator.validate(valid_config)
    
    def test_similarity_threshold_range(self, validator, valid_config):
        """Test similarity threshold must be between 0 and 1."""
        # Test minimum
        valid_config['cache']['l2']['similarity_threshold'] = 0.0
        validator.validate(valid_config)
        
        # Test maximum
        valid_config['cache']['l2']['similarity_threshold'] = 1.0
        validator.validate(valid_config)
        
        # Test below minimum
        valid_config['cache']['l2']['similarity_threshold'] = -0.1
        with pytest.raises(ValidationError):
            validator.validate(valid_config)
        
        # Test above maximum
        valid_config['cache']['l2']['similarity_threshold'] = 1.1
        with pytest.raises(ValidationError):
            validator.validate(valid_config)
    
    def test_validate_partial_cache_config(self, validator):
        """Test partial validation of cache configuration."""
        partial_config = {
            'max_size': 2000,
            'ttl_seconds': 7200,
            'enabled': True,
        }
        
        # Should not raise exception
        validator.validate_partial(partial_config, 'cache.l1')
    
    def test_validate_partial_invalid_path(self, validator):
        """Test partial validation with invalid path."""
        partial_config = {'max_size': 2000}
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_partial(partial_config, 'invalid.path')
        
        assert 'Unknown configuration path' in str(exc_info.value)
    
    def test_validate_partial_invalid_value(self, validator):
        """Test partial validation with invalid value."""
        partial_config = {
            'l1': {
                'max_size': -1,
            },
        }
        
        with pytest.raises(ValidationError):
            validator.validate_partial(partial_config, 'cache')
    
    def test_nested_dict_validation(self, validator, valid_config):
        """Test validation of nested dictionary structures."""
        # Add deeply nested invalid value
        valid_config['cache']['l1']['max_size'] = 'invalid'
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(valid_config)
        
        assert 'cache.l1.max_size' in str(exc_info.value)


class TestValidationError:
    """Test suite for ValidationError."""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError('Test error message')
        assert str(error) == 'Test error message'
    
    def test_validation_error_with_multiple_messages(self):
        """Test ValidationError with multiple messages."""
        messages = [
            'Error 1: Invalid value',
            'Error 2: Missing field',
            'Error 3: Type mismatch',
        ]
        error = ValidationError('\n'.join(messages))
        
        error_str = str(error)
        for msg in messages:
            assert msg in error_str
