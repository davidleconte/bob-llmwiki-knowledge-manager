"""Configuration manager with validation and runtime updates.

Provides centralized configuration management with:
- Environment-specific settings (dev, staging, prod)
- Runtime configuration updates
- Configuration validation
- Version tracking
- Thread-safe operations
"""

import os
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .schema import ConfigSchema, CacheConfig, OptimizerConfig, MonitoringConfig
from .validator import ConfigValidator, ValidationError


@dataclass
class ConfigVersion:
    """Configuration version information."""
    version: str
    timestamp: float
    changes: List[str]


class ConfigManager:
    """Thread-safe configuration manager with validation and versioning.
    
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
    """
    
    _instance: Optional['ConfigManager'] = None
    _lock = threading.Lock()
    
    def __init__(self, environment: str = 'dev'):
        """Initialize configuration manager.
        
        Args:
            environment: Environment name (dev, staging, prod)
        """
        self.environment = environment
        self._config: Dict[str, Any] = {}
        self._validator = ConfigValidator()
        self._versions: List[ConfigVersion] = []
        self._update_lock = threading.Lock()
        
        # Load default configuration
        self._load_defaults()
    
    @classmethod
    def get_instance(cls, environment: str = 'dev') -> 'ConfigManager':
        """Get singleton instance of ConfigManager.
        
        Args:
            environment: Environment name
            
        Returns:
            ConfigManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(environment)
        return cls._instance
    
    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config = {
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
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            filepath: Path to configuration file
            
        Raises:
            ValidationError: If configuration is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(path, 'r') as f:
            config_data = json.load(f)
        
        # Validate configuration
        self._validator.validate(config_data)
        
        # Merge with defaults
        with self._update_lock:
            self._merge_config(config_data)
            self._add_version('load_from_file', [f'Loaded from {filepath}'])
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables.
        
        Environment variables should be prefixed with 'CONFIG_' and use
        double underscores for nesting (e.g., CONFIG_CACHE__L1__MAX_SIZE).
        """
        env_config: Dict[str, Any] = {}
        
        for key, value in os.environ.items():
            if key.startswith('CONFIG_'):
                # Remove prefix and convert to nested dict
                config_key = key[7:].lower()  # Remove 'CONFIG_'
                parts = config_key.split('__')
                
                # Build nested structure
                current = env_config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert value to appropriate type
                try:
                    current[parts[-1]] = json.loads(value)
                except json.JSONDecodeError:
                    current[parts[-1]] = value
        
        if env_config:
            with self._update_lock:
                self._merge_config(env_config)
                self._add_version('load_from_env', ['Loaded from environment'])
    
    def _compute_merge(self, base: Dict[str, Any], new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Return ``base`` with ``new_config`` recursively merged in.

        Pure: does not mutate ``self._config``, so the result can be validated
        before being committed.

        Args:
            base: Base configuration to merge into (not mutated at top level)
            new_config: New configuration to merge
        """
        def merge_dicts(b: Dict, update: Dict) -> Dict:
            """Recursively merge dictionaries."""
            result = b.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        return merge_dicts(base, new_config)

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into the active config.

        Args:
            new_config: New configuration to merge
        """
        self._config = self._compute_merge(self._config, new_config)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration at runtime.
        
        Args:
            updates: Dictionary of configuration updates using dot notation
                    (e.g., {'cache.l1.max_size': 2000})
                    
        Raises:
            ValidationError: If updates are invalid
            
        Example:
            >>> config.update({'cache.l1.max_size': 2000})
            >>> config.update({'optimizer.max_tokens': 8192})
        """
        # Convert dot notation to nested dict
        nested_updates: Dict[str, Any] = {}
        changes: List[str] = []
        
        for key, value in updates.items():
            parts = key.split('.')
            current = nested_updates
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
            changes.append(f'{key}={value}')
        
        # Build a candidate, validate it, then commit atomically. On a
        # validation failure self._config is left unchanged (no partial state),
        # and the whole compute-validate-commit runs under the update lock.
        with self._update_lock:
            candidate = self._compute_merge(self._config, nested_updates)
            self._validator.validate(candidate)
            self._config = candidate
            self._add_version('runtime_update', changes)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'cache.l1.max_size')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            >>> max_size = config.get('cache.l1.max_size')
            >>> threshold = config.get('cache.l2.similarity_threshold', 0.85)
        """
        parts = key.split('.')
        current = self._config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration.
        
        Returns:
            CacheConfig instance
        """
        cache_data = self._config.get('cache', {})
        return CacheConfig(
            l1_max_size=cache_data.get('l1', {}).get('max_size', 1000),
            l1_ttl_seconds=cache_data.get('l1', {}).get('ttl_seconds', 3600),
            l1_enabled=cache_data.get('l1', {}).get('enabled', True),
            l2_max_size=cache_data.get('l2', {}).get('max_size', 10000),
            l2_ttl_seconds=cache_data.get('l2', {}).get('ttl_seconds', 86400),
            l2_similarity_threshold=cache_data.get('l2', {}).get('similarity_threshold', 0.85),
            l2_enabled=cache_data.get('l2', {}).get('enabled', True),
            version_support_enabled=cache_data.get('version_support', {}).get('enabled', True),
            max_versions=cache_data.get('version_support', {}).get('max_versions', 5),
        )
    
    def get_optimizer_config(self) -> OptimizerConfig:
        """Get optimizer configuration.
        
        Returns:
            OptimizerConfig instance
        """
        opt_data = self._config.get('optimizer', {})
        return OptimizerConfig(
            max_tokens=opt_data.get('max_tokens', 4096),
            target_reduction=opt_data.get('target_reduction', 0.3),
            min_quality_score=opt_data.get('min_quality_score', 0.8),
            strategies=opt_data.get('strategies', ['remove_whitespace', 'compress_repeated']),
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration.
        
        Returns:
            MonitoringConfig instance
        """
        mon_data = self._config.get('monitoring', {})
        return MonitoringConfig(
            enabled=mon_data.get('enabled', True),
            log_level=mon_data.get('log_level', 'INFO'),
            metrics_enabled=mon_data.get('metrics_enabled', True),
            health_check_interval=mon_data.get('health_check_interval', 60),
        )
    
    def get_all(self) -> Dict[str, Any]:
        """Get complete configuration.
        
        Returns:
            Complete configuration dictionary
        """
        with self._update_lock:
            return self._config.copy()
    
    def get_schema(self) -> ConfigSchema:
        """Get configuration as schema object.
        
        Returns:
            ConfigSchema instance
        """
        return ConfigSchema(
            cache=self.get_cache_config(),
            optimizer=self.get_optimizer_config(),
            monitoring=self.get_monitoring_config(),
        )
    
    def _add_version(self, source: str, changes: List[str]) -> None:
        """Add configuration version.
        
        Args:
            source: Source of changes (e.g., 'load_from_file', 'runtime_update')
            changes: List of changes made
        """
        import time
        
        version = ConfigVersion(
            version=f'v{len(self._versions) + 1}',
            timestamp=time.time(),
            changes=changes,
        )
        self._versions.append(version)
        
        # Keep only last 10 versions
        if len(self._versions) > 10:
            self._versions = self._versions[-10:]
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get configuration version history.
        
        Returns:
            List of version information dictionaries
        """
        return [asdict(v) for v in self._versions]
    
    def save_to_file(self, filepath: str) -> None:
        """Save current configuration to file.
        
        Args:
            filepath: Path to save configuration
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        with self._update_lock:
            self._load_defaults()
            self._versions.clear()
            self._add_version('reset', ['Reset to defaults'])


# Global configuration instance
_global_config: Optional[ConfigManager] = None


def get_config(environment: str = 'dev') -> ConfigManager:
    """Get global configuration manager instance.
    
    Args:
        environment: Environment name (dev, staging, prod)
        
    Returns:
        ConfigManager instance
        
    Example:
        >>> config = get_config()
        >>> cache_config = config.get_cache_config()
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager.get_instance(environment)
    return _global_config
