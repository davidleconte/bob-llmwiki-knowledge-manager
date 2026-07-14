# validator

Configuration validator with comprehensive validation rules.

Validates configuration against schema and business rules.

## Classes

### `ValidationError(Exception)`

Configuration validation error.


### `ConfigValidator`

Validates configuration against schema and business rules.

Performs validation of:
- Required fields
- Type checking
- Value ranges
- Business logic constraints

Example:
    >>> validator = ConfigValidator()
    >>> validator.validate(config_dict)

#### Methods

##### `__init__()`

Initialize validator with validation rules.


##### `validate(config: Dict[str, Any]) -> None`

Validate configuration against rules.

Args:
    config: Configuration dictionary to validate

Raises:
    ValidationError: If configuration is invalid


##### `validate_partial(config: Dict[str, Any], path: Optional[str]) -> None`

Validate partial configuration update.

Args:
    config: Partial configuration to validate
    path: Optional path to validate (e.g., 'cache.l1')

Raises:
    ValidationError: If configuration is invalid


