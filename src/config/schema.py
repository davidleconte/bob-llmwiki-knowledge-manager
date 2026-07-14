"""Configuration schema definitions.

Defines typed configuration structures for all system components.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CacheConfig:
    """Cache configuration settings.
    
    Attributes:
        l1_max_size: Maximum number of entries in L1 cache
        l1_ttl_seconds: Time-to-live for L1 cache entries (seconds)
        l1_enabled: Whether L1 cache is enabled
        l2_max_size: Maximum number of entries in L2 cache
        l2_ttl_seconds: Time-to-live for L2 cache entries (seconds)
        l2_similarity_threshold: Minimum similarity score for L2 cache hits
        l2_enabled: Whether L2 cache is enabled
        version_support_enabled: Whether version support is enabled
        max_versions: Maximum number of versions to keep per key
    """
    l1_max_size: int = 1000
    l1_ttl_seconds: int = 3600
    l1_enabled: bool = True
    l2_max_size: int = 10000
    l2_ttl_seconds: int = 86400
    l2_similarity_threshold: float = 0.85
    l2_enabled: bool = True
    version_support_enabled: bool = True
    max_versions: int = 5


@dataclass
class OptimizerConfig:
    """Optimizer configuration settings.
    
    Attributes:
        max_tokens: Maximum tokens allowed in optimized output
        target_reduction: Target token reduction ratio (0.0-1.0)
        min_quality_score: Minimum quality score to accept optimization
        strategies: List of optimization strategies to apply
    """
    max_tokens: int = 4096
    target_reduction: float = 0.3
    min_quality_score: float = 0.8
    strategies: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize default strategies if not provided."""
        if self.strategies is None:
            self.strategies = ['remove_whitespace', 'compress_repeated']


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings.
    
    Attributes:
        enabled: Whether monitoring is enabled
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        metrics_enabled: Whether metrics collection is enabled
        health_check_interval: Health check interval in seconds
    """
    enabled: bool = True
    log_level: str = 'INFO'
    metrics_enabled: bool = True
    health_check_interval: int = 60


@dataclass
class ConfigSchema:
    """Complete configuration schema.
    
    Attributes:
        cache: Cache configuration
        optimizer: Optimizer configuration
        monitoring: Monitoring configuration
    """
    cache: CacheConfig
    optimizer: OptimizerConfig
    monitoring: MonitoringConfig
