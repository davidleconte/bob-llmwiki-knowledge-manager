"""Exact match cache (L1) implementation with version support.

This module implements a hash-based exact match cache with LRU eviction.
Provides O(1) lookup time for exact prompt matches.

Target metrics:
- Lookup latency: <1ms
- Hit rate: workload-dependent (measured per run by the Phase-5 validation
  harness, not a fixed target; the old "23.33% theoretical" figure is retired)
- Memory: Configurable max size with LRU eviction
"""

import hashlib
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional

from src.cache.base import CacheEntry, CacheInterface, CacheStats, escape_version
from src.monitoring import get_logger, get_metrics_collector


class ExactCache(CacheInterface):
    """L1 cache for exact prompt matches with version support.

    Uses SHA-256 hashing for key generation and OrderedDict for LRU eviction.
    Provides fast O(1) lookups for exact matches. Supports versioning for
    cache evolution without breaking existing cached data.

    Attributes:
        VERSION: Current cache version
        max_size: Maximum number of entries (default: 1000)
        cache: OrderedDict storing cache entries
        stats: Cache statistics tracker
        track_costs: Whether to track costs with CostTracker
    """

    VERSION: str = "v1"  # Current cache version

    def __init__(
        self,
        max_size: int = 1000,
        track_costs: bool = False,
        ttl_seconds: Optional[float] = None,
        clock: Callable[[], float] = time.time,
    ):
        """Initialize exact cache.

        Args:
            max_size: Maximum number of entries before eviction
            track_costs: Whether to track costs with CostTracker
            ttl_seconds: Optional entry time-to-live. When set, an entry older
                than this (by creation timestamp) is treated as a miss and
                evicted on read. ``None`` disables expiry (default), preserving
                behaviour for callers that don't opt in.
            clock: Time source for stamping/expiry, injectable for
                deterministic tests. Defaults to ``time.time``.
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive when set")

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._clock = clock
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

        self._logger.info(
            "exact_cache_initialized",
            max_size=max_size,
            track_costs=track_costs,
            version=self.VERSION,
        )

    def _make_versioned_key(self, key: str, version: Optional[str] = None) -> str:
        """Create versioned cache key.

        Args:
            key: Base key (prompt)
            version: Version string (defaults to current VERSION)

        Returns:
            Versioned key string
        """
        if version is None:
            version = self.VERSION
        # Escape the version so a colon inside it cannot be confused with the
        # version/key delimiter (injective encoding -- see escape_version).
        return f"{escape_version(version)}:{key}"

    def _hash_key(self, key: str) -> str:
        """Generate SHA-256 hash of key.

        Args:
            key: The key to hash (versioned key)

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve cached response for exact key match.

        Args:
            key: The cache key (prompt)
            version: Optional version (defaults to current VERSION)

        Returns:
            Cached response if found, None otherwise
        """
        start_time = time.time()
        versioned_key = self._make_versioned_key(key, version)
        hashed_key = self._hash_key(versioned_key)

        if hashed_key in self.cache:
            entry = self.cache[hashed_key]

            # Enforce TTL: an entry older than ttl_seconds (by creation
            # timestamp, not last access) is expired -> evict and report a miss.
            if (
                self.ttl_seconds is not None
                and (self._clock() - entry.timestamp) > self.ttl_seconds
            ):
                del self.cache[hashed_key]
                self._stats.record_miss()
                self._metrics.record_cache_miss("L1")
                self._logger.debug(
                    "cache_expired",
                    cache_level="L1",
                    key_hash=hashed_key[:8],
                    version=version or self.VERSION,
                    ttl_seconds=self.ttl_seconds,
                )
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(hashed_key)

            # Update entry access stats
            entry.access()

            # Record hit
            self._stats.record_hit()
            latency_ms = (time.time() - start_time) * 1000

            # Record metrics
            self._metrics.record_cache_hit("L1", latency_ms)

            # Log hit
            self._logger.debug(
                "cache_hit",
                cache_level="L1",
                key_hash=hashed_key[:8],
                version=version or self.VERSION,
                latency_ms=latency_ms,
                access_count=entry.access_count,
            )

            # Track cost savings if enabled
            if self.track_costs and self._cost_tracker:
                # Estimate tokens saved (from metadata if available)
                tokens_saved = entry.metadata.get("tokens", 0)
                if tokens_saved > 0:
                    self._cost_tracker.record_cache_hit(tokens_saved)

            return entry.response

        # Record miss
        self._stats.record_miss()
        latency_ms = (time.time() - start_time) * 1000

        # Record metrics
        self._metrics.record_cache_miss("L1")

        # Log miss
        self._logger.debug(
            "cache_miss",
            cache_level="L1",
            key_hash=hashed_key[:8],
            version=version or self.VERSION,
            latency_ms=latency_ms,
        )

        return None

    def set(
        self,
        key: str,
        value: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store response in cache.

        Args:
            key: The cache key (prompt)
            value: The response to cache
            version: Optional version (defaults to current VERSION)
            metadata: Optional metadata (tokens, quality, etc.)
        """
        versioned_key = self._make_versioned_key(key, version)
        hashed_key = self._hash_key(versioned_key)
        is_update = hashed_key in self.cache

        # Check if we need to evict
        if not is_update and len(self.cache) >= self.max_size:
            self._evict_lru()

        # Create cache entry
        if metadata is None:
            metadata = {}

        # Add version to metadata
        metadata["version"] = version or self.VERSION

        entry = CacheEntry(response=value, metadata=metadata, timestamp=self._clock())

        # Store and move to end (most recently used)
        self.cache[hashed_key] = entry
        self.cache.move_to_end(hashed_key)

        # Update cache size metric
        self._metrics.update_cache_size("L1", len(self.cache))

        # Log cache set
        self._logger.debug(
            "cache_set",
            cache_level="L1",
            key_hash=hashed_key[:8],
            version=version or self.VERSION,
            is_update=is_update,
            cache_size=len(self.cache),
            response_length=len(value),
        )

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            # Remove first item (least recently used)
            evicted_key, evicted_entry = self.cache.popitem(last=False)
            self._stats.record_eviction()

            # Record metrics
            self._metrics.record_cache_eviction("L1")

            # Log eviction
            self._logger.debug(
                "cache_eviction",
                cache_level="L1",
                evicted_key_hash=evicted_key[:8],
                version=evicted_entry.metadata.get("version", "unknown"),
                cache_size=len(self.cache),
                access_count=evicted_entry.access_count,
            )

    def clear(self) -> None:
        """Clear all entries from cache."""
        entries_cleared = len(self.cache)
        self.cache.clear()
        self._stats.reset()

        # Log clear
        self._logger.info("cache_cleared", cache_level="L1", entries_cleared=entries_cleared)

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
            "version": self.VERSION,
        }

    def get_entry(self, key: str, version: Optional[str] = None) -> Optional[CacheEntry]:
        """Get full cache entry (for testing/debugging).

        Args:
            key: The cache key
            version: Optional version

        Returns:
            CacheEntry if found, None otherwise
        """
        versioned_key = self._make_versioned_key(key, version)
        hashed_key = self._hash_key(versioned_key)
        return self.cache.get(hashed_key)

    def contains(self, key: str, version: Optional[str] = None) -> bool:
        """Check if key exists in cache.

        Args:
            key: The cache key
            version: Optional version

        Returns:
            True if key exists, False otherwise
        """
        versioned_key = self._make_versioned_key(key, version)
        hashed_key = self._hash_key(versioned_key)
        return hashed_key in self.cache

    def evict(self, key: str, version: Optional[str] = None) -> bool:
        """Manually evict a specific key.

        Args:
            key: The cache key to evict
            version: Optional version

        Returns:
            True if key was evicted, False if not found
        """
        versioned_key = self._make_versioned_key(key, version)
        hashed_key = self._hash_key(versioned_key)
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

    def migrate(self, from_version: str, to_version: str) -> int:
        """Migrate entries from one version to another.

        Creates new versioned entries for all entries matching from_version.
        Original entries are preserved.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            Number of entries migrated
        """
        migrated = 0
        entries_to_migrate = []

        # Collect entries to migrate
        for hashed_key, entry in self.cache.items():
            if entry.metadata.get("version") == from_version:
                entries_to_migrate.append((hashed_key, entry))

        # Migrate entries
        for hashed_key, entry in entries_to_migrate:
            # Extract original key from metadata if available
            # For now, we can't reverse the hash, so we skip migration
            # This is a limitation of the hash-based approach
            pass

        self._logger.info(
            "cache_migration", from_version=from_version, to_version=to_version, migrated=migrated
        )

        return migrated

    def cleanup_version(self, version: str) -> int:
        """Remove all entries for a specific version.

        Args:
            version: Version to clean up

        Returns:
            Number of entries removed
        """
        removed = 0
        keys_to_remove = []

        # Collect keys to remove
        for hashed_key, entry in self.cache.items():
            if entry.metadata.get("version") == version:
                keys_to_remove.append(hashed_key)

        # Remove entries
        for hashed_key in keys_to_remove:
            del self.cache[hashed_key]
            removed += 1

        self._logger.info("version_cleanup", version=version, removed=removed)

        return removed

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._stats.reset()
