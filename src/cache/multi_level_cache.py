"""Multi-level cache combining L1 (exact) and L2 (semantic) caches with version support.

This module implements a two-level caching strategy:
- L1: ExactCache for fast exact matches (<1ms)
- L2: SemanticCache for semantic similarity matches (<100ms)

L2 hits are promoted to L1 for future fast access.

Target metrics:
- Overall lookup latency: <100ms
- Combined hit rate: 23.33%
- L1 hit rate: ~15-18%
- L2 hit rate: ~5-8%
"""

import time
from typing import Optional, Dict, Any, Tuple

from src.cache.base import CacheInterface
from src.cache.exact_cache import ExactCache
from src.cache.semantic_cache import SemanticCache
from src.monitoring import get_logger, get_metrics_collector


class MultiLevelCache(CacheInterface):
    """Two-level cache with exact (L1) and semantic (L2) matching with version support.
    
    Provides fast exact matches via L1 and semantic fallback via L2.
    Automatically promotes L2 hits to L1 for improved performance.
    Supports versioning for cache evolution without breaking existing cached data.
    
    Attributes:
        VERSION: Current cache version
        l1_cache: ExactCache for fast exact matches
        l2_cache: SemanticCache for semantic similarity
        promote_l2_hits: Whether to promote L2 hits to L1
        l1_hits: Count of L1 cache hits
        l2_hits: Count of L2 cache hits
        misses: Count of cache misses
    """
    
    VERSION: str = "v1"  # Current cache version
    
    def __init__(self,
                 l1_max_size: int = 1000,
                 l2_max_size: int = 500,
                 similarity_threshold: float = 0.85,
                 promote_l2_hits: bool = True,
                 l1_ttl_seconds: Optional[float] = None,
                 l2_ttl_seconds: Optional[float] = None):
        """Initialize multi-level cache.

        Args:
            l1_max_size: Maximum size for L1 cache
            l2_max_size: Maximum size for L2 cache
            similarity_threshold: Similarity threshold for L2
            promote_l2_hits: Whether to promote L2 hits to L1
            l1_ttl_seconds: Optional TTL for L1 entries (None disables expiry).
            l2_ttl_seconds: Optional TTL for L2 entries (None disables expiry).
                Threaded through so CacheConfig's ttl_seconds actually reaches
                the caches instead of being silently inert.
        """
        self.l1_cache = ExactCache(max_size=l1_max_size, ttl_seconds=l1_ttl_seconds)
        self.l2_cache = SemanticCache(
            max_size=l2_max_size,
            similarity_threshold=similarity_threshold,
            ttl_seconds=l2_ttl_seconds
        )
        self.promote_l2_hits = promote_l2_hits
        
        # Initialize monitoring
        self._logger = get_logger("cache.multi_level")
        self._metrics = get_metrics_collector()
        
        # Statistics
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
        self._lookup_times: list[float] = []
        
        self._logger.info("multi_level_cache_initialized",
                        l1_max_size=l1_max_size,
                        l2_max_size=l2_max_size,
                        similarity_threshold=similarity_threshold,
                        promote_l2_hits=promote_l2_hits,
                        version=self.VERSION)
    
    def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve cached response, trying L1 then L2.
        
        Args:
            key: The cache key (prompt)
            version: Optional version (defaults to current VERSION)
            
        Returns:
            Cached response if found in L1 or L2, None otherwise
        """
        start_time = time.time()
        
        # Try L1 first (fast exact match)
        result = self.l1_cache.get(key, version)
        if result is not None:
            self.l1_hits += 1
            latency_ms = (time.time() - start_time) * 1000
            self._lookup_times.append(time.time() - start_time)
            
            self._logger.debug("multi_level_hit",
                             cache_level="L1",
                             version=version or self.VERSION,
                             latency_ms=latency_ms)
            return result
        
        # Try L2 (semantic similarity)
        result = self.l2_cache.get(key, version)
        if result is not None:
            self.l2_hits += 1
            latency_ms = (time.time() - start_time) * 1000
            
            # Promote to L1 for future fast access
            if self.promote_l2_hits:
                # Get metadata from L2 if available
                l2_entry = self.l2_cache.get_entry(key, version)
                metadata = l2_entry.metadata if l2_entry else {}
                self.l1_cache.set(key, result, version, metadata)
                
                # Record promotion
                self._metrics.record_cache_promotion()
                
                self._logger.debug("cache_promotion",
                                 from_level="L2",
                                 to_level="L1",
                                 version=version or self.VERSION)
            
            self._lookup_times.append(time.time() - start_time)
            
            self._logger.debug("multi_level_hit",
                             cache_level="L2",
                             version=version or self.VERSION,
                             latency_ms=latency_ms,
                             promoted=self.promote_l2_hits)
            return result
        
        # Cache miss
        self.misses += 1
        latency_ms = (time.time() - start_time) * 1000
        self._lookup_times.append(time.time() - start_time)
        
        self._logger.debug("multi_level_miss",
                         version=version or self.VERSION,
                         latency_ms=latency_ms)
        return None
    
    def set(self, key: str, value: str, version: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store response in both L1 and L2 caches.
        
        Args:
            key: The cache key (prompt)
            value: The response to cache
            version: Optional version (defaults to current VERSION)
            metadata: Optional metadata
        """
        # Store in both caches
        self.l1_cache.set(key, value, version, metadata)
        self.l2_cache.set(key, value, version, metadata)
    
    def clear(self) -> None:
        """Clear both L1 and L2 caches."""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
        self._lookup_times.clear()
    
    def size(self) -> int:
        """Get total number of unique entries across both caches.
        
        Returns:
            Number of unique cached entries
        """
        # Count unique keys across both caches
        # L1 uses hashed keys, L2 uses versioned keys
        l1_keys = set(self.l1_cache.cache.keys())
        l2_keys = set(self.l1_cache._hash_key(self.l2_cache._make_versioned_key(
            self.l2_cache._extract_base_key(k), 
            self.l2_cache._extract_version(k)
        )) for k in self.l2_cache.embeddings.keys())
        return len(l1_keys | l2_keys)
    
    def hit_rate(self) -> float:
        """Calculate overall cache hit rate.
        
        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.l1_hits + self.l2_hits + self.misses
        if total == 0:
            return 0.0
        return ((self.l1_hits + self.l2_hits) / total) * 100
    
    def l1_hit_rate(self) -> float:
        """Calculate L1 cache hit rate.
        
        Returns:
            L1 hit rate as percentage (0-100)
        """
        total = self.l1_hits + self.l2_hits + self.misses
        if total == 0:
            return 0.0
        return (self.l1_hits / total) * 100
    
    def l2_hit_rate(self) -> float:
        """Calculate L2 cache hit rate.
        
        Returns:
            L2 hit rate as percentage (0-100)
        """
        total = self.l1_hits + self.l2_hits + self.misses
        if total == 0:
            return 0.0
        return (self.l2_hits / total) * 100
    
    def stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.l1_hits + self.l2_hits + self.misses
        avg_lookup_time = (
            sum(self._lookup_times) / len(self._lookup_times)
            if self._lookup_times else 0.0
        )
        
        return {
            # Overall stats
            "total_requests": total_requests,
            "total_hits": self.l1_hits + self.l2_hits,
            "total_misses": self.misses,
            "hit_rate": self.hit_rate(),
            "avg_lookup_time_ms": avg_lookup_time * 1000,
            "version": self.VERSION,
            
            # L1 stats
            "l1_hits": self.l1_hits,
            "l1_hit_rate": self.l1_hit_rate(),
            "l1_size": self.l1_cache.size(),
            "l1_max_size": self.l1_cache.max_size,
            "l1_utilization": (self.l1_cache.size() / self.l1_cache.max_size) * 100,
            
            # L2 stats
            "l2_hits": self.l2_hits,
            "l2_hit_rate": self.l2_hit_rate(),
            "l2_size": self.l2_cache.size(),
            "l2_max_size": self.l2_cache.max_size,
            "l2_utilization": (self.l2_cache.size() / self.l2_cache.max_size) * 100,
            "l2_similarity_threshold": self.l2_cache.similarity_threshold,
            "l2_avg_similarity": self.l2_cache.average_similarity_score(),
            
            # Configuration
            "promote_l2_hits": self.promote_l2_hits,
            "unique_entries": self.size(),
        }
    
    def get_l1_cache(self) -> ExactCache:
        """Get L1 cache instance.
        
        Returns:
            ExactCache instance
        """
        return self.l1_cache
    
    def get_l2_cache(self) -> SemanticCache:
        """Get L2 cache instance.
        
        Returns:
            SemanticCache instance
        """
        return self.l2_cache
    
    def update_similarity_threshold(self, threshold: float) -> None:
        """Update L2 similarity threshold.
        
        Args:
            threshold: New threshold value (0-1)
        """
        self.l2_cache.update_threshold(threshold)
    
    def enable_promotion(self) -> None:
        """Enable L2 to L1 promotion."""
        self.promote_l2_hits = True
    
    def disable_promotion(self) -> None:
        """Disable L2 to L1 promotion."""
        self.promote_l2_hits = False
    
    def get_with_level(self, key: str, version: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """Get cached response with cache level information.
        
        Args:
            key: The cache key (prompt)
            version: Optional version
            
        Returns:
            Tuple of (response, level) where level is 'L1' or 'L2', or None
        """
        # Try L1
        result = self.l1_cache.get(key, version)
        if result is not None:
            return (result, "L1")
        
        # Try L2
        result = self.l2_cache.get(key, version)
        if result is not None:
            return (result, "L2")
        
        return None
    
    def contains(self, key: str, version: Optional[str] = None) -> bool:
        """Check if key exists in either cache.
        
        Args:
            key: The cache key
            version: Optional version
            
        Returns:
            True if key exists in L1 or L2, False otherwise
        """
        return self.l1_cache.contains(key, version) or self.l2_cache.contains(key, version)
    
    def average_lookup_time_ms(self) -> float:
        """Get average lookup time in milliseconds.
        
        Returns:
            Average lookup time in ms
        """
        if not self._lookup_times:
            return 0.0
        return (sum(self._lookup_times) / len(self._lookup_times)) * 1000
    
    def migrate(self, from_version: str, to_version: str) -> int:
        """Migrate entries from one version to another in both caches.
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            Total number of entries migrated across both caches
        """
        l1_migrated = self.l1_cache.migrate(from_version, to_version)
        l2_migrated = self.l2_cache.migrate(from_version, to_version)
        
        total_migrated = l1_migrated + l2_migrated
        
        self._logger.info("multi_level_migration",
                        from_version=from_version,
                        to_version=to_version,
                        l1_migrated=l1_migrated,
                        l2_migrated=l2_migrated,
                        total_migrated=total_migrated)
        
        return total_migrated
    
    def cleanup_version(self, version: str) -> int:
        """Remove all entries for a specific version from both caches.
        
        Args:
            version: Version to clean up
            
        Returns:
            Total number of entries removed across both caches
        """
        l1_removed = self.l1_cache.cleanup_version(version)
        l2_removed = self.l2_cache.cleanup_version(version)
        
        total_removed = l1_removed + l2_removed
        
        self._logger.info("multi_level_cleanup",
                        version=version,
                        l1_removed=l1_removed,
                        l2_removed=l2_removed,
                        total_removed=total_removed)
        
        return total_removed
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
        self._lookup_times.clear()
        self.l1_cache.reset_stats()
        self.l2_cache.reset_stats()
