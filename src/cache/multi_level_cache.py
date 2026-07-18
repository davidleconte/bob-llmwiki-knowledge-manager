"""Multi-level cache combining L1 (exact), L2 (semantic), and optional L3 (persistent).

This module implements a three-level caching strategy:
- L1: ExactCache for fast exact matches (<1ms)
- L2: SemanticCache for semantic similarity matches (<100ms)
- L3: Optional PersistentEmbeddingIndex (P2-3, ADR-015) — survives process restarts

L2 hits are promoted to L1 for future fast access.
L3 hits are **not** promoted to L2 (separate namespaces per ADR-015 §Decision 4).

Type contract:
- ``get()`` / ``set()`` operate on the **prompt-response** namespace (L1+L2 only).
  They always return a cached *response* string or ``None`` — never a document path.
- ``query_l3()`` operates on the **document-reference** namespace (L3 only).
  It returns a ``(doc_id, score)`` tuple or ``None``.  Callers must not mix the
  two APIs — see ADR-015 §Decision 4 and the L3 type-contract note in INTEGRATIONS.md.

Target metrics:
- Overall lookup latency: <100ms
- Hit rates are workload-dependent, measured per run by the Phase-5 validation
  harness -- not fixed targets. The old "23.33% combined / 15-18% L1 / 5-8% L2"
  figures were never validated and are retired.
"""

import threading
import time
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

if TYPE_CHECKING:
    from src.embeddings.index import PersistentEmbeddingIndex

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

    def __init__(
        self,
        l1_max_size: int = 1000,
        l2_max_size: int = 10000,
        similarity_threshold: float = 0.85,
        promote_l2_hits: bool = True,
        l1_ttl_seconds: Optional[float] = None,
        l2_ttl_seconds: Optional[float] = None,
        l1_enabled: bool = True,
        l2_enabled: bool = True,
        version_support_enabled: bool = True,
        max_versions: int = 5,
        l3_index: Optional["PersistentEmbeddingIndex"] = None,
    ):
        """Initialize multi-level cache.

        Args:
            l1_max_size: Maximum size for L1 cache
            l2_max_size: Maximum size for L2 cache. Default 10000 matches
                CacheConfig.l2_max_size (and keeps L2 > L1, the config's business
                rule); the old 500 default contradicted both.
            similarity_threshold: Similarity threshold for L2
            promote_l2_hits: Whether to promote L2 hits to L1
            l1_ttl_seconds: Optional TTL for L1 entries (None disables expiry).
            l2_ttl_seconds: Optional TTL for L2 entries (None disables expiry).
                Threaded through so CacheConfig's ttl_seconds actually reaches
                the caches instead of being silently inert.
            l1_enabled: Whether the L1 (exact) level participates in get/set.
                When False, L1 is bypassed and no L2->L1 promotion occurs.
            l2_enabled: Whether the L2 (semantic) level participates in get/set.
                When False, L2 is bypassed. Both flags come from CacheConfig.
            version_support_enabled: Forwarded to :class:`~src.cache.exact_cache.ExactCache`.
                When ``False``, L1 stores keys without version prefixes.
            max_versions: Forwarded to :class:`~src.cache.exact_cache.ExactCache`.
                Cap on migrate() history depth.
        """
        self.l1_cache = ExactCache(
            max_size=l1_max_size,
            ttl_seconds=l1_ttl_seconds,
            version_support_enabled=version_support_enabled,
            max_versions=max_versions,
        )
        self.l2_cache = SemanticCache(
            max_size=l2_max_size,
            similarity_threshold=similarity_threshold,
            ttl_seconds=l2_ttl_seconds,
        )
        self.promote_l2_hits = promote_l2_hits
        self.l1_enabled = l1_enabled
        self.l2_enabled = l2_enabled
        # L3: optional persistent index (ADR-015 §P2-3). Not promoted to L2.
        self.l3_index: Optional["PersistentEmbeddingIndex"] = l3_index
        self.l3_hits = 0

        # Initialize monitoring
        self._logger = get_logger("cache.multi_level")
        self._metrics = get_metrics_collector()

        # Statistics — all mutations and reads are serialised by _stats_lock so
        # that hit_rate() / stats() snapshots are consistent under concurrent get()
        # calls and clear() / reset_stats() resets are atomic.
        self._stats_lock = threading.RLock()
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
        self._lookup_times: deque[float] = deque(maxlen=10_000)

        self._logger.info(
            "multi_level_cache_initialized",
            l1_max_size=l1_max_size,
            l2_max_size=l2_max_size,
            similarity_threshold=similarity_threshold,
            promote_l2_hits=promote_l2_hits,
            l1_enabled=l1_enabled,
            l2_enabled=l2_enabled,
            version=self.VERSION,
        )

    def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve cached *response*, trying L1 then L2.

        This method is strictly in the **prompt-response** namespace.  It never
        touches L3.  Use :meth:`query_l3` to search the persistent document index.

        Args:
            key: The cache key (prompt)
            version: Optional version (defaults to current VERSION)

        Returns:
            Cached response string if found in L1 or L2, ``None`` otherwise.
            The returned value is always a prompt *response*, never a document path.
        """
        start_time = time.time()

        # Try L1 first (fast exact match), unless L1 is disabled by config.
        result = self.l1_cache.get(key, version) if self.l1_enabled else None
        if result is not None:
            latency_ms = (time.time() - start_time) * 1000
            with self._stats_lock:
                self.l1_hits += 1
                self._lookup_times.append(time.time() - start_time)

            self._logger.debug(
                "multi_level_hit",
                cache_level="L1",
                version=version or self.VERSION,
                latency_ms=latency_ms,
            )
            return result

        # Try L2 (semantic similarity), unless L2 is disabled by config.
        result = self.l2_cache.get(key, version) if self.l2_enabled else None
        if result is not None:
            latency_ms = (time.time() - start_time) * 1000
            with self._stats_lock:
                self.l2_hits += 1
                self._lookup_times.append(time.time() - start_time)

            # Promote to L1 for future fast access (only if L1 is enabled).
            if self.promote_l2_hits and self.l1_enabled:
                # Get metadata from L2 if available
                l2_entry = self.l2_cache.get_entry(key, version)
                metadata = l2_entry.metadata if l2_entry else {}
                self.l1_cache.set(key, result, version, metadata)

                # Record promotion
                self._metrics.record_cache_promotion()

                self._logger.debug(
                    "cache_promotion",
                    from_level="L2",
                    to_level="L1",
                    version=version or self.VERSION,
                )

            self._logger.debug(
                "multi_level_hit",
                cache_level="L2",
                version=version or self.VERSION,
                latency_ms=latency_ms,
                promoted=self.promote_l2_hits,
            )
            return result

        # Cache miss (L3 is a separate namespace — use query_l3() for doc search)
        latency_ms = (time.time() - start_time) * 1000
        with self._stats_lock:
            self.misses += 1
            self._lookup_times.append(time.time() - start_time)

        self._logger.debug(
            "multi_level_miss", version=version or self.VERSION, latency_ms=latency_ms
        )
        return None

    def query_l3(self, query: str, top_k: int = 1) -> Optional[Tuple[str, float]]:
        """Search the L3 persistent document index.

        This method is strictly in the **document-reference** namespace — entirely
        separate from the prompt-response namespace of :meth:`get` / :meth:`set`.
        It returns a ``(doc_id, score)`` pair, **not** a cached response string.

        Returns ``None`` if no L3 index is wired or no results meet the index
        threshold.  Increments ``l3_hits`` on a successful match.

        Args:
            query: Free-text query to search the persistent index.
            top_k: Maximum number of results to retrieve from the index.
                   Only the best result is returned; ``top_k`` controls the
                   internal search breadth.

        Returns:
            ``(doc_id, score)`` for the best match, or ``None`` if no L3 index
            is attached or the search returns no results.
        """
        if self.l3_index is None:
            return None
        results = self.l3_index.search(query, top_k=top_k)
        if not results:
            return None
        doc_id, score = results[0]
        with self._stats_lock:
            self.l3_hits += 1
        self._logger.debug(
            "multi_level_hit",
            cache_level="L3",
            score=round(score, 3),
        )
        return doc_id, score

    def set(
        self,
        key: str,
        value: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store response in both L1 and L2 caches.

        Args:
            key: The cache key (prompt)
            value: The response to cache
            version: Optional version (defaults to current VERSION)
            metadata: Optional metadata
        """
        # Store in each enabled level.
        if self.l1_enabled:
            self.l1_cache.set(key, value, version, metadata)
        if self.l2_enabled:
            self.l2_cache.set(key, value, version, metadata)

    def clear(self) -> None:
        """Clear L1 and L2 caches (L3 index is NOT cleared — disk-backed)."""
        self.l1_cache.clear()
        self.l2_cache.clear()
        with self._stats_lock:
            self.l1_hits = 0
            self.l2_hits = 0
            self.l3_hits = 0
            self.misses = 0
            self._lookup_times.clear()

    def size(self) -> int:
        """Get total number of unique entries across both caches.

        Returns:
            Number of unique cached entries
        """
        # Count unique keys across both caches. L1 uses hashed keys, L2 uses
        # versioned keys. Take each sub-cache's keys via its lock-protected
        # snapshot -- never iterate the live dicts here, or a concurrent set/
        # eviction raises "dictionary changed size during iteration".
        l1_keys = set(self.l1_cache.snapshot_keys())
        l2_keys = set(
            self.l1_cache._hash_key(
                self.l2_cache._make_versioned_key(
                    self.l2_cache._extract_base_key(k), self.l2_cache._extract_version(k)
                )
            )
            for k in self.l2_cache.snapshot_keys()
        )
        return len(l1_keys | l2_keys)

    def hit_rate(self) -> float:
        """Calculate overall cache hit rate.

        Returns:
            Hit rate as percentage (0-100)
        """
        with self._stats_lock:
            l1, l2, m = self.l1_hits, self.l2_hits, self.misses
        total = l1 + l2 + m
        if total == 0:
            return 0.0
        return ((l1 + l2) / total) * 100

    def l1_hit_rate(self) -> float:
        """Calculate L1 cache hit rate.

        Returns:
            L1 hit rate as percentage (0-100)
        """
        with self._stats_lock:
            l1, l2, m = self.l1_hits, self.l2_hits, self.misses
        total = l1 + l2 + m
        if total == 0:
            return 0.0
        return (l1 / total) * 100

    def l2_hit_rate(self) -> float:
        """Calculate L2 cache hit rate.

        Returns:
            L2 hit rate as percentage (0-100)
        """
        with self._stats_lock:
            l1, l2, m = self.l1_hits, self.l2_hits, self.misses
        total = l1 + l2 + m
        if total == 0:
            return 0.0
        return (l2 / total) * 100

    def stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._stats_lock:
            l1_hits = self.l1_hits
            l2_hits = self.l2_hits
            misses = self.misses
            promote_l2_hits = self.promote_l2_hits
        total_requests = l1_hits + l2_hits + misses
        hit_rate = ((l1_hits + l2_hits) / total_requests * 100) if total_requests else 0.0
        l1_hit_rate = (l1_hits / total_requests * 100) if total_requests else 0.0
        l2_hit_rate = (l2_hits / total_requests * 100) if total_requests else 0.0

        # Snapshot sizes once so "l1_size" and "l1_utilization" (and the L2
        # equivalents) are consistent within a single stats() call even if
        # concurrent evictions run between the two reads.
        l1_size = self.l1_cache.size()
        l2_size = self.l2_cache.size()

        return {
            # Overall stats
            "total_requests": total_requests,
            "total_hits": l1_hits + l2_hits,
            "total_misses": misses,
            "hit_rate": hit_rate,
            "avg_lookup_time_ms": self.average_lookup_time_ms(),
            "version": self.VERSION,
            # L1 stats
            "l1_hits": l1_hits,
            "l1_hit_rate": l1_hit_rate,
            "l1_size": l1_size,
            "l1_max_size": self.l1_cache.max_size,
            "l1_utilization": (l1_size / self.l1_cache.max_size) * 100,
            # L2 stats
            "l2_hits": l2_hits,
            "l2_hit_rate": l2_hit_rate,
            "l2_size": l2_size,
            "l2_max_size": self.l2_cache.max_size,
            "l2_utilization": (l2_size / self.l2_cache.max_size) * 100,
            "l2_similarity_threshold": self.l2_cache.similarity_threshold,
            "l2_avg_similarity": self.l2_cache.average_similarity_score(),
            # Configuration
            "promote_l2_hits": promote_l2_hits,
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
        with self._stats_lock:
            self.promote_l2_hits = True

    def disable_promotion(self) -> None:
        """Disable L2 to L1 promotion."""
        with self._stats_lock:
            self.promote_l2_hits = False

    def get_with_level(self, key: str, version: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """Get cached response with cache level information.

        Respects :attr:`l1_enabled` and :attr:`l2_enabled` flags — disabled
        levels are skipped, consistent with the behaviour of :meth:`get`.

        Args:
            key: The cache key (prompt)
            version: Optional version

        Returns:
            Tuple of (response, level) where level is 'L1' or 'L2', or None
        """
        # Try L1 (skip if disabled by config)
        if self.l1_enabled:
            result = self.l1_cache.get(key, version)
            if result is not None:
                return (result, "L1")

        # Try L2 (skip if disabled by config)
        if self.l2_enabled:
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
        with self._stats_lock:
            times = list(self._lookup_times)
        if not times:
            return 0.0
        return (sum(times) / len(times)) * 1000

    def migrate(self, from_version: str, to_version: str) -> int:
        """Migrate entries from one version to another in both caches.

        .. note::
            L1 always contributes 0 migrated entries because
            :class:`~src.cache.exact_cache.ExactCache` stores keys as
            irreversible SHA-256 hashes and cannot reconstruct the original
            key string required for re-insertion under a new version prefix.
            Only L2 (:class:`~src.cache.semantic_cache.SemanticCache`) performs
            actual migration.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            Total number of entries migrated across both caches (L1 always 0)
        """
        l1_migrated = self.l1_cache.migrate(from_version, to_version)
        l2_migrated = self.l2_cache.migrate(from_version, to_version)

        total_migrated = l1_migrated + l2_migrated

        self._logger.info(
            "multi_level_migration",
            from_version=from_version,
            to_version=to_version,
            l1_migrated=l1_migrated,
            l2_migrated=l2_migrated,
            total_migrated=total_migrated,
        )

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

        self._logger.info(
            "multi_level_cleanup",
            version=version,
            l1_removed=l1_removed,
            l2_removed=l2_removed,
            total_removed=total_removed,
        )

        return total_removed

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._stats_lock:
            self.l1_hits = 0
            self.l2_hits = 0
            self.l3_hits = 0
            self.misses = 0
            self._lookup_times.clear()
        self.l1_cache.reset_stats()
        self.l2_cache.reset_stats()
