"""Base cache interface with version support.

This module defines the abstract base class for all cache implementations,
providing a common interface and version support for cache evolution.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time


@dataclass
class CacheEntry:
    """Cache entry with metadata and access tracking.
    
    Attributes:
        response: Cached response value
        metadata: Optional metadata dictionary
        timestamp: Creation timestamp
        last_access: Last access timestamp
        access_count: Number of times accessed
    """
    response: str
    metadata: Dict[str, Any]
    timestamp: float
    last_access: float = None
    access_count: int = 0
    
    def __post_init__(self):
        """Initialize last_access if not set."""
        if self.last_access is None:
            self.last_access = self.timestamp
    
    def access(self) -> None:
        """Record an access to this entry."""
        self.last_access = time.time()
        self.access_count += 1
    
    def age_seconds(self) -> float:
        """Calculate age of entry in seconds.
        
        Returns:
            Age in seconds since creation
        """
        return time.time() - self.timestamp
    
    def idle_seconds(self) -> float:
        """Calculate idle time in seconds.
        
        Returns:
            Seconds since last access
        """
        return time.time() - self.last_access


@dataclass
class CacheStats:
    """Cache statistics tracker.
    
    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of evictions
    """
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    
    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1
    
    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1
    
    def record_eviction(self) -> None:
        """Record an eviction."""
        self.evictions += 1
    
    def hit_rate(self) -> float:
        """Calculate hit rate as percentage.
        
        Returns:
            Hit rate (0-100)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def reset(self) -> None:
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "total_requests": self.hits + self.misses,
            "hit_rate": self.hit_rate()
        }


class CacheInterface(ABC):
    """Abstract base class for cache implementations with version support.
    
    All cache implementations must inherit from this class and implement
    the required methods. Version support enables cache evolution without
    breaking existing cached data.
    
    Attributes:
        VERSION: Default cache version (class attribute)
    """
    
    VERSION: str = "v1"  # Default version for all caches
    
    @abstractmethod
    def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve cached value for key.
        
        Args:
            key: Cache key
            version: Optional version to retrieve from (defaults to current)
            
        Returns:
            Cached value if found, None otherwise
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, version: Optional[str] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store key-value pair in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            version: Optional version to store in (defaults to current)
            metadata: Optional metadata to store with entry
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from cache."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get number of entries in cache.
        
        Returns:
            Number of cached entries
        """
        pass
    
    @abstractmethod
    def hit_rate(self) -> float:
        """Calculate cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        pass
    
    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        pass
    
    def migrate(self, from_version: str, to_version: str) -> int:
        """Migrate entries from one version to another.
        
        Default implementation raises NotImplementedError.
        Subclasses should override if migration is supported.
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            Number of entries migrated
            
        Raises:
            NotImplementedError: If migration not supported
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support migration. "
            "Override this method to enable version migration."
        )
    
    def cleanup_version(self, version: str) -> int:
        """Remove all entries for a specific version.
        
        Default implementation raises NotImplementedError.
        Subclasses should override if version cleanup is supported.
        
        Args:
            version: Version to clean up
            
        Returns:
            Number of entries removed
            
        Raises:
            NotImplementedError: If cleanup not supported
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support version cleanup. "
            "Override this method to enable version cleanup."
        )
    
    def get_entry(self, key: str, version: Optional[str] = None) -> Optional[CacheEntry]:
        """Get full cache entry with metadata.
        
        Default implementation returns None.
        Subclasses should override to provide entry details.
        
        Args:
            key: Cache key
            version: Optional version
            
        Returns:
            CacheEntry if found, None otherwise
        """
        return None
    
    def contains(self, key: str, version: Optional[str] = None) -> bool:
        """Check if key exists in cache.
        
        Default implementation uses get().
        Subclasses may override for efficiency.
        
        Args:
            key: Cache key
            version: Optional version
            
        Returns:
            True if key exists, False otherwise
        """
        return self.get(key, version) is not None
    
    def reset_stats(self) -> None:
        """Reset statistics counters.
        
        Default implementation does nothing.
        Subclasses should override to reset their statistics.
        """
        pass
