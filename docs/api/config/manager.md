# manager

Configuration manager with validation and runtime updates.

Provides centralized configuration management with:
- Environment-specific settings (dev, staging, prod)
- Runtime configuration updates
- Configuration validation
- Version tracking
- Thread-safe operations

## Functions

### `get_config(environment: str) -> ConfigManager`

Get global configuration manager instance.

Args:
    environment: Environment name (dev, staging, prod)

Returns:
    ConfigManager instance

Example:
    >>> config = get_config()
    >>> cache_config = config.get_cache_config()


### `merge_dicts(b: Dict, update: Dict) -> Dict`

Recursively merge dictionaries.


## Classes

### `ConfigVersion`

Configuration version information.


### `ConfigManager`

Thread-safe configuration manager with validation and versioning.

Features:
- Environment-specific configurations (dev, staging, prod)
- Runtime configuration updates with validation
- Configuration versioning and change tracking
- Thread-safe operations
- Default fallback values

Example:
    >>> config = ConfigManager()
    >>> config.load_from_file('config.json')
    >>> cache_config = config.get_cache_config()
    >>> config.update({'cache.l1.max_size': 2000})

#### Methods

##### `__init__(environment: str)`

Initialize configuration manager.

Args:
    environment: Environment name (dev, staging, prod)


##### `get_instance(cls, environment: str) -> 'ConfigManager'`

Get singleton instance of ConfigManager.

Args:
    environment: Environment name

Returns:
    ConfigManager instance


##### `load_from_file(filepath: str) -> None`

Load configuration from JSON file.

Args:
    filepath: Path to configuration file

Raises:
    ValidationError: If configuration is invalid
    FileNotFoundError: If file doesn't exist


##### `load_from_env() -> None`

Load configuration from environment variables.

Environment variables should be prefixed with 'CONFIG_' and use
double underscores for nesting (e.g., CONFIG_CACHE__L1__MAX_SIZE).


##### `update(updates: Dict[str, Any]) -> None`

Update configuration at runtime.

Args:
    updates: Dictionary of configuration updates using dot notation
            (e.g., {'cache.l1.max_size': 2000})

Raises:
    ValidationError: If updates are invalid

Example:
    >>> config.update({'cache.l1.max_size': 2000})
    >>> config.update({'optimizer.max_tokens': 8192})


##### `get(key: str, default: Any) -> Any`

Get configuration value using dot notation.

Args:
    key: Configuration key in dot notation (e.g., 'cache.l1.max_size')
    default: Default value if key not found

Returns:
    Configuration value or default

Example:
    >>> max_size = config.get('cache.l1.max_size')
    >>> threshold = config.get('cache.l2.similarity_threshold', 0.85)


##### `get_cache_config() -> CacheConfig`

Get cache configuration.

Returns:
    CacheConfig instance


##### `get_optimizer_config() -> OptimizerConfig`

Get optimizer configuration.

Returns:
    OptimizerConfig instance


##### `get_monitoring_config() -> MonitoringConfig`

Get monitoring configuration.

Returns:
    MonitoringConfig instance


##### `get_all() -> Dict[str, Any]`

Get complete configuration.

Returns:
    Complete configuration dictionary


##### `get_schema() -> ConfigSchema`

Get configuration as schema object.

Returns:
    ConfigSchema instance


##### `get_version_history() -> List[Dict[str, Any]]`

Get configuration version history.

Returns:
    List of version information dictionaries


##### `save_to_file(filepath: str) -> None`

Save current configuration to file.

Args:
    filepath: Path to save configuration


##### `reset() -> None`

Reset configuration to defaults.


