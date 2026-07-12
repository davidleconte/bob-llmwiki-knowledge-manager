"""Exact match cache (L1) implementation.

This module implements a hash-based exact match cache with LRU eviction.
Provides O(1) lookup time for exact prompt matches.

Target metrics:
- Lookup latency: <1ms
- Hit rate contribution: ~15-20% of total 23.33%
- Memory: Configurable max size with LRU eviction
"""

import hashlib
import time
from collections import OrderedDict
from typing import Optional, Dict, Any

from src.cache.base import CacheInterface, CacheEntry, CacheStats


class ExactCache(CacheInterface):
    """L1 cache for exact prompt matches.
    
    Uses SHA-256 hashing for key generation and OrderedDict for LRU eviction.
    Provides fast O(1) lookups for exact matches.
    
    Attributes:
        max_size: Maximum number of entries (default: 1000)
        cache: OrderedDict storing cache entries
        stats: Cache statistics tracker
    """
    
    def __init__(self, max_size: int = 1000):
        """Initialize exact cache.
        
        Args:
            max_size: Maximum number of entries before eviction
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
    
    def _hash_key(self, key: str) -> str:
        """Generate SHA-256 hash of key.
        
        Args:
            key: The key to hash (usually a prompt)
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(key.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve cached response for exact key match.
        
        Args:
            key: The cache key (prompt)
            
        Returns:
            Cached response if found, None otherwise
        """
        hashed_key = self._hash_key(key)
        
        if hashed_key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(hashed_key)
            
            # Update entry access stats
            entry = self.cache[hashed_key]
            entry.access()
            
            # Record hit
            self._stats.record_hit()
            
            return entry.response
        
        # Record miss
        self._stats.record_miss()
        return None
    
    def set(self, key: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in cache.
        
        Args:
            key: The cache key (prompt)
            response: The response to cache
            metadata: Optional metadata (tokens, quality, etc.)
        """
        hashed_key = self._hash_key(key)
        
        # Check if we need to evict
        if hashed_key not in self.cache and len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Create cache entry
        if metadata is None:
            metadata = {}
        
        entry = CacheEntry(
            response=response,
            metadata=metadata,
            timestamp=time.time()
        )
        
        # Store and move to end (most recently used)
        self.cache[hashed_key] = entry
        self.cache.move_to_end(hashed_key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            # Remove first item (least recently used)
            self.cache.popitem(last=False)
            self._stats.record_eviction()
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.cache.clear()
        self._stats.reset()
    
    def size(self) -> int:
        """Get number of entries in cache.
        
        Returns:
            Number of cached entries
        """
        return len(self.cache)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        return self._stats.hit_rate()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            **self._stats.to_dict(),
            "size": self.size(),
            "max_size": self.max_size,
            "utilization": (self.size() / self.max_size) * 100,
        }
    
    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get full cache entry (for testing/debugging).
        
        Args:
            key: The cache key
            
        Returns:
            CacheEntry if found, None otherwise
        """
        hashed_key = self._hash_key(key)
        return self.cache.get(hashed_key)
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if key exists, False otherwise
        """
        hashed_key = self._hash_key(key)
        return hashed_key in self.cache
    
    def evict(self, key: str) -> bool:
        """Manually evict a specific key.
        
        Args:
            key: The cache key to evict
            
        Returns:
            True if key was evicted, False if not found
        """
        hashed_key = self._hash_key(key)
        if hashed_key in self.cache:
            del self.cache[hashed_key]
            self._stats.record_eviction()
            return True
        return False
    
    def get_oldest_entry(self) -> Optional[tuple[str, CacheEntry]]:
        """Get the oldest (LRU) entry without removing it.
        
        Returns:
            Tuple of (key, entry) for oldest entry, or None if empty
        """
        if not self.cache:
            return None
        
        # First item is oldest (LRU)
        key = next(iter(self.cache))
        return (key, self.cache[key])
    
    def get_newest_entry(self) -> Optional[tuple[str, CacheEntry]]:
        """Get the newest (MRU) entry without removing it.
        
        Returns:
            Tuple of (key, entry) for newest entry, or None if empty
        """
        if not self.cache:
            return None
        
        # Last item is newest (MRU)
        key = next(reversed(self.cache))
        return (key, self.cache[key])
