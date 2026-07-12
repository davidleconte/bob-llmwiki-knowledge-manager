"""Base classes and interfaces for caching system.

This module defines the abstract interfaces and data structures used
throughout the caching system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time


@dataclass
class CacheEntry:
    """Represents a cached item with metadata.
    
    Attributes:
        response: The cached response content
        metadata: Additional metadata (tokens, quality, etc.)
        timestamp: When the entry was cached (Unix timestamp)
        access_count: Number of times this entry was accessed
        last_access: Last access timestamp
    """
    response: str
    metadata: Dict[str, Any]
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    
    def __post_init__(self):
        """Initialize last_access to timestamp if not set."""
        if self.last_access == 0.0:
            self.last_access = self.timestamp
    
    def access(self) -> None:
        """Record an access to this entry."""
        self.access_count += 1
        self.last_access = time.time()
    
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.timestamp
    
    def idle_seconds(self) -> float:
        """Get time since last access in seconds."""
        return time.time() - self.last_access


class CacheInterface(ABC):
    """Abstract interface for cache implementations.
    
    All cache implementations must provide these methods.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieve cached response for key.
        
        Args:
            key: The cache key (usually prompt or hash)
            
        Returns:
            Cached response if found, None otherwise
        """
        pass
    
    @abstractmethod
    def set(self, key: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in cache.
        
        Args:
            key: The cache key
            response: The response to cache
            metadata: Optional metadata about the response
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


class CacheStats:
    """Track cache statistics.
    
    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of evicted entries
        total_lookups: Total number of lookups
    """
    
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0
        self.total_lookups: int = 0
    
    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1
        self.total_lookups += 1
    
    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1
        self.total_lookups += 1
    
    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1
    
    def hit_rate(self) -> float:
        """Calculate hit rate percentage.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        if self.total_lookups == 0:
            return 0.0
        return (self.hits / self.total_lookups) * 100
    
    def miss_rate(self) -> float:
        """Calculate miss rate percentage.
        
        Returns:
            Miss rate as percentage (0-100)
        """
        if self.total_lookups == 0:
            return 0.0
        return (self.misses / self.total_lookups) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary.
        
        Returns:
            Dictionary with all statistics
        """
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "total_lookups": self.total_lookups,
            "hit_rate": self.hit_rate(),
            "miss_rate": self.miss_rate(),
        }
    
    def reset(self) -> None:
        """Reset all statistics to zero."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_lookups = 0
