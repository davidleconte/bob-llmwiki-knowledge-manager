"""Configuration validator with comprehensive validation rules.

Validates configuration against schema and business rules.
"""

from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Configuration validation error."""
    pass


class ConfigValidator:
    """Validates configuration against schema and business rules.
    
    Performs validation of:
    - Required fields
    - Type checking
    - Value ranges
    - Business logic constraints
    
    Example:
        >>> validator = ConfigValidator()
        >>> validator.validate(config_dict)
    """

    def __init__(self):
        """Initialize validator with validation rules."""
        self._rules = self._build_validation_rules()

    def _build_validation_rules(self) -> Dict[str, Any]:
        """Build validation rules for configuration.
        
        Returns:
            Dictionary of validation rules
        """
        return {
            'cache': {
                'required': True,
                'type': dict,
                'fields': {
                    'l1': {
                        'required': True,
                        'type': dict,
                        'fields': {
                            'max_size': {
                                'required': True,
                                'type': int,
                                'min': 1,
                                'max': 100000,
                            },
                            'ttl_seconds': {
                                'required': True,
                                'type': int,
                                'min': 1,
                                'max': 86400 * 7,  # 1 week
                            },
                            'enabled': {
                                'required': True,
                                'type': bool,
                            },
                        },
                    },
                    'l2': {
                        'required': True,
                        'type': dict,
                        'fields': {
                            'max_size': {
                                'required': True,
                                'type': int,
                                'min': 1,
                                'max': 1000000,
                            },
                            'ttl_seconds': {
                                'required': True,
                                'type': int,
                                'min': 1,
                                'max': 86400 * 30,  # 30 days
                            },
                            'similarity_threshold': {
                                'required': True,
                                'type': float,
                                'min': 0.0,
                                'max': 1.0,
                            },
                            'enabled': {
                                'required': True,
                                'type': bool,
                            },
                        },
                    },
                    'version_support': {
                        'required': False,
                        'type': dict,
                        'fields': {
                            'enabled': {
                                'required': True,
                                'type': bool,
                            },
                            'max_versions': {
                                'required': True,
                                'type': int,
                                'min': 1,
                                'max': 100,
                            },
                        },
                    },
                },
            },
            'optimizer': {
                'required': True,
                'type': dict,
                'fields': {
                    'max_tokens': {
                        'required': True,
                        'type': int,
                        'min': 1,
                        'max': 1000000,
                    },
                    'target_reduction': {
                        'required': True,
                        'type': float,
                        'min': 0.0,
                        'max': 1.0,
                    },
                    'min_quality_score': {
                        'required': True,
                        'type': float,
                        'min': 0.0,
                        'max': 1.0,
                    },
                    'strategies': {
                        'required': True,
                        'type': list,
                        'min_length': 1,
                        'allowed_values': [
                            'remove_whitespace',
                            'compress_repeated',
                            'remove_comments',
                            'shorten_names',
                        ],
                    },
                },
            },
            'monitoring': {
                'required': True,
                'type': dict,
                'fields': {
                    'enabled': {
                        'required': True,
                        'type': bool,
                    },
                    'log_level': {
                        'required': True,
                        'type': str,
                        'allowed_values': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    },
                    'metrics_enabled': {
                        'required': True,
                        'type': bool,
                    },
                    'health_check_interval': {
                        'required': True,
                        'type': int,
                        'min': 1,
                        'max': 3600,
                    },
                },
            },
        }

    def validate(self, config: Dict[str, Any]) -> None:
        """Validate configuration against rules.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValidationError: If configuration is invalid
        """
        errors: List[str] = []

        # Validate against rules
        self._validate_dict(config, self._rules, '', errors)

        # Only validate business logic if no type errors
        if not errors:
            self._validate_business_logic(config, errors)

        if errors:
            raise ValidationError('\n'.join(errors))

    def _validate_dict(
        self,
        data: Dict[str, Any],
        rules: Dict[str, Any],
        path: str,
        errors: List[str],
    ) -> None:
        """Recursively validate dictionary against rules.
        
        Args:
            data: Data to validate
            rules: Validation rules
            path: Current path in configuration
            errors: List to accumulate errors
        """
        for key, rule in rules.items():
            current_path = f'{path}.{key}' if path else key

            # Check required fields
            if rule.get('required', False) and key not in data:
                errors.append(f'Missing required field: {current_path}')
                continue

            if key not in data:
                continue

            value = data[key]

            # Check type
            expected_type = rule.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f'Invalid type for {current_path}: '
                    f'expected {expected_type.__name__}, got {type(value).__name__}'
                )
                continue

            # Check nested fields
            if 'fields' in rule and isinstance(value, dict):
                self._validate_dict(value, rule['fields'], current_path, errors)

            # Check numeric ranges
            if 'min' in rule and value < rule['min']:
                errors.append(
                    f'Value for {current_path} is below minimum: '
                    f'{value} < {rule["min"]}'
                )

            if 'max' in rule and value > rule['max']:
                errors.append(
                    f'Value for {current_path} exceeds maximum: '
                    f'{value} > {rule["max"]}'
                )

            # Check allowed values
            if 'allowed_values' in rule:
                if isinstance(value, list):
                    invalid = [v for v in value if v not in rule['allowed_values']]
                    if invalid:
                        errors.append(
                            f'Invalid values for {current_path}: {invalid}. '
                            f'Allowed: {rule["allowed_values"]}'
                        )
                elif value not in rule['allowed_values']:
                    errors.append(
                        f'Invalid value for {current_path}: {value}. '
                        f'Allowed: {rule["allowed_values"]}'
                    )

            # Check list length
            if 'min_length' in rule and isinstance(value, list):
                if len(value) < rule['min_length']:
                    errors.append(
                        f'List {current_path} is too short: '
                        f'{len(value)} < {rule["min_length"]}'
                    )

    def _validate_business_logic(
        self,
        config: Dict[str, Any],
        errors: List[str],
    ) -> None:
        """Validate business logic constraints.
        
        Args:
            config: Configuration to validate
            errors: List to accumulate errors
        """
        # L2 cache should be larger than L1
        cache = config.get('cache', {})
        l1_size = cache.get('l1', {}).get('max_size', 0)
        l2_size = cache.get('l2', {}).get('max_size', 0)

        if l2_size <= l1_size:
            errors.append(
                f'L2 cache size ({l2_size}) must be larger than '
                f'L1 cache size ({l1_size})'
            )

        # L2 TTL should be longer than L1
        l1_ttl = cache.get('l1', {}).get('ttl_seconds', 0)
        l2_ttl = cache.get('l2', {}).get('ttl_seconds', 0)

        if l2_ttl <= l1_ttl:
            errors.append(
                f'L2 cache TTL ({l2_ttl}s) must be longer than '
                f'L1 cache TTL ({l1_ttl}s)'
            )

        # Target reduction should be reasonable
        optimizer = config.get('optimizer', {})
        target_reduction = optimizer.get('target_reduction', 0)
        min_quality = optimizer.get('min_quality_score', 0)

        if target_reduction > 0.7 and min_quality > 0.9:
            errors.append(
                f'Target reduction ({target_reduction}) is too aggressive '
                f'for high quality requirement ({min_quality})'
            )

        # Version support validation
        version_support = cache.get('version_support', {})
        if version_support.get('enabled', False):
            max_versions = version_support.get('max_versions', 0)
            if max_versions < 2:
                errors.append(
                    f'max_versions ({max_versions}) must be at least 2 '
                    f'when version support is enabled'
                )

    def validate_partial(
        self,
        config: Dict[str, Any],
        path: Optional[str] = None,
    ) -> None:
        """Validate partial configuration update.
        
        Args:
            config: Partial configuration to validate
            path: Optional path to validate (e.g., 'cache.l1')
            
        Raises:
            ValidationError: If configuration is invalid
        """
        errors: List[str] = []

        if path:
            # Validate specific path
            parts = path.split('.')
            rules = self._rules

            for part in parts:
                if part not in rules:
                    errors.append(f'Unknown configuration path: {path}')
                    break
                rules = rules[part].get('fields', {})

            if not errors:
                # For partial validation, temporarily mark all fields as optional
                self._validate_dict_partial(config, rules, path, errors)
        else:
            # Validate entire config (but don't require all fields)
            self._validate_dict_partial(config, self._rules, '', errors)

        if errors:
            raise ValidationError('\n'.join(errors))

    def _validate_dict_partial(
        self,
        data: Dict[str, Any],
        rules: Dict[str, Any],
        path: str,
        errors: List[str],
    ) -> None:
        """Validate dictionary for partial updates (no required field checks).
        
        Args:
            data: Data to validate
            rules: Validation rules
            path: Current path in configuration
            errors: List to accumulate errors
        """
        for key, value in data.items():
            if key not in rules:
                continue

            rule = rules[key]
            current_path = f'{path}.{key}' if path else key

            # Check type
            expected_type = rule.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f'Invalid type for {current_path}: '
                    f'expected {expected_type.__name__}, got {type(value).__name__}'
                )
                continue

            # Check nested fields
            if 'fields' in rule and isinstance(value, dict):
                self._validate_dict_partial(value, rule['fields'], current_path, errors)

            # Check numeric ranges
            if 'min' in rule and value < rule['min']:
                errors.append(
                    f'Value for {current_path} is below minimum: '
                    f'{value} < {rule["min"]}'
                )

            if 'max' in rule and value > rule['max']:
                errors.append(
                    f'Value for {current_path} exceeds maximum: '
                    f'{value} > {rule["max"]}'
                )

            # Check allowed values
            if 'allowed_values' in rule:
                if isinstance(value, list):
                    invalid = [v for v in value if v not in rule['allowed_values']]
                    if invalid:
                        errors.append(
                            f'Invalid values for {current_path}: {invalid}. '
                            f'Allowed: {rule["allowed_values"]}'
                        )
                elif value not in rule['allowed_values']:
                    errors.append(
                        f'Invalid value for {current_path}: {value}. '
                        f'Allowed: {rule["allowed_values"]}'
                    )

            # Check list length
            if 'min_length' in rule and isinstance(value, list):
                if len(value) < rule['min_length']:
                    errors.append(
                        f'List {current_path} is too short: '
                        f'{len(value)} < {rule["min_length"]}'
                    )
