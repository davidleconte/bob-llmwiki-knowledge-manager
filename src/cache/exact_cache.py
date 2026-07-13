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
from src.monitoring import get_logger, get_metrics_collector


class ExactCache(CacheInterface):
    """L1 cache for exact prompt matches.
    
    Uses SHA-256 hashing for key generation and OrderedDict for LRU eviction.
    Provides fast O(1) lookups for exact matches.
    
    Attributes:
        max_size: Maximum number of entries (default: 1000)
        cache: OrderedDict storing cache entries
        stats: Cache statistics tracker
        track_costs: Whether to track costs with CostTracker
    """
    
    def __init__(self, max_size: int = 1000, track_costs: bool = False):
        """Initialize exact cache.
        
        Args:
            max_size: Maximum number of entries before eviction
            track_costs: Whether to track costs with CostTracker
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self.track_costs = track_costs
        
        # Initialize monitoring
        self._logger = get_logger("cache.exact")
        self._metrics = get_metrics_collector()
        
        # Initialize cost tracker if enabled
        self._cost_tracker = None
        if self.track_costs:
            try:
                from src.monitoring.cost_tracker import get_cost_tracker
                self._cost_tracker = get_cost_tracker()
            except ImportError:
                self.track_costs = False
        
        self._logger.info("exact_cache_initialized", max_size=max_size, track_costs=track_costs)
    
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
        start_time = time.time()
        hashed_key = self._hash_key(key)
        
        if hashed_key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(hashed_key)
            
            # Update entry access stats
            entry = self.cache[hashed_key]
            entry.access()
            
            # Record hit
            self._stats.record_hit()
            latency_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self._metrics.record_cache_hit("L1", latency_ms)
            
            # Log hit
            self._logger.debug("cache_hit", 
                             cache_level="L1",
                             key_hash=hashed_key[:8],
                             latency_ms=latency_ms,
                             access_count=entry.access_count)
            
            # Track cost savings if enabled
            if self.track_costs and self._cost_tracker:
                # Estimate tokens saved (from metadata if available)
                tokens_saved = entry.metadata.get('tokens', 0)
                if tokens_saved > 0:
                    self._cost_tracker.record_cache_hit(tokens_saved)
            
            return entry.response
        
        # Record miss
        self._stats.record_miss()
        latency_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        self._metrics.record_cache_miss("L1")
        
        # Log miss
        self._logger.debug("cache_miss",
                         cache_level="L1",
                         key_hash=hashed_key[:8],
                         latency_ms=latency_ms)
        
        return None
    
    def set(self, key: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in cache.
        
        Args:
            key: The cache key (prompt)
            response: The response to cache
            metadata: Optional metadata (tokens, quality, etc.)
        """
        hashed_key = self._hash_key(key)
        is_update = hashed_key in self.cache
        
        # Check if we need to evict
        if not is_update and len(self.cache) >= self.max_size:
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
        
        # Update cache size metric
        self._metrics.update_cache_size("L1", len(self.cache))
        
        # Log cache set
        self._logger.debug("cache_set",
                         cache_level="L1",
                         key_hash=hashed_key[:8],
                         is_update=is_update,
                         cache_size=len(self.cache),
                         response_length=len(response))
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            # Remove first item (least recently used)
            evicted_key, evicted_entry = self.cache.popitem(last=False)
            self._stats.record_eviction()
            
            # Record metrics
            self._metrics.record_cache_eviction("L1")
            
            # Log eviction
            self._logger.debug("cache_eviction",
                             cache_level="L1",
                             evicted_key_hash=evicted_key[:8],
                             cache_size=len(self.cache),
                             access_count=evicted_entry.access_count)
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        entries_cleared = len(self.cache)
        self.cache.clear()
        self._stats.reset()
        
        # Log clear
        self._logger.info("cache_cleared",
                        cache_level="L1",
                        entries_cleared=entries_cleared)
    
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
