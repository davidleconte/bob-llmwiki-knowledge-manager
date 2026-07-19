# exact_cache

Exact match cache (L1) implementation with version support.

This module implements a hash-based exact match cache with LRU eviction.
Provides O(1) lookup time for exact prompt matches.

Target metrics:
- Lookup latency: <1ms
- Hit rate: workload-dependent (measured per run by the Phase-5 validation
  harness, not a fixed target; the old "23.33% theoretical" figure is retired)
- Memory: Configurable max size with LRU eviction

## Functions

### `_synchronized(method)`

Run ``method`` while holding ``self._lock`` (a re-entrant ``RLock``).

``ExactCache`` relied on CPython GIL-atomicity for single-key ops, which is
safe for point mutations but NOT for *iteration*: a thread walking the dict
(e.g. ``MultiLevelCache.size()`` snapshotting keys, or ``migrate`` /
``get_oldest_entry``) could see it change size mid-walk and raise
``RuntimeError: dictionary changed size during iteration``. Serialising every
dict-touching method on one re-entrant lock closes that race; RLock lets
``set`` call ``_evict_lru`` without self-deadlock.


### `wrapper(self)`


## Classes

### `ExactCache(CacheInterface)`

L1 cache for exact prompt matches with version support.

Uses SHA-256 hashing for key generation and OrderedDict for LRU eviction.
Provides fast O(1) lookups for exact matches. Supports versioning for
cache evolution without breaking existing cached data.

Attributes:
    VERSION: Current cache version
    max_size: Maximum number of entries (default: 1000)
    cache: OrderedDict storing cache entries
    stats: Cache statistics tracker
    track_costs: Whether to track costs with CostTracker

#### Methods

##### `__init__(max_size: int, track_costs: bool, ttl_seconds: Optional[float], clock: Callable[[], float], version_support_enabled: bool, max_versions: int)`

Initialize exact cache.

Args:
    max_size: Maximum number of entries before eviction
    track_costs: Whether to track costs with CostTracker
    ttl_seconds: Optional entry time-to-live. When set, an entry older
        than this (by creation timestamp) is treated as a miss and
        evicted on read. ``None`` disables expiry (default), preserving
        behaviour for callers that don't opt in.
    clock: Time source for stamping/expiry, injectable for
        deterministic tests. Defaults to ``time.time``.
    version_support_enabled: Whether versioned key prefixes are applied.
        When ``False``, keys are stored without a version prefix —
        useful for callers that do not need key-format migration. Comes
        from :attr:`~src.config.schema.CacheConfig.version_support_enabled`.
    max_versions: Maximum number of historic versions to retain during
        :meth:`migrate`. Unused version slots are not pre-allocated;
        this is a cap on ``migrate()`` history depth.


##### `get(key: str, version: Optional[str]) -> Optional[str]`

Retrieve cached response for exact key match.

Args:
    key: The cache key (prompt)
    version: Optional version (defaults to current VERSION)

Returns:
    Cached response if found, None otherwise


##### `set(key: str, value: str, version: Optional[str], metadata: Optional[Dict[str, Any]]) -> None`

Store response in cache.

Args:
    key: The cache key (prompt)
    value: The response to cache
    version: Optional version (defaults to current VERSION)
    metadata: Optional metadata (tokens, quality, etc.)


##### `clear() -> None`

Clear all entries from cache.


##### `size() -> int`

Get number of entries in cache.

Returns:
    Number of cached entries


##### `snapshot_keys() -> list[str]`

Return a point-in-time copy of the cache keys, taken under the lock.

Callers (e.g. ``MultiLevelCache.size()``) must iterate this list, never
``self.cache`` directly, so a concurrent ``set``/eviction cannot mutate the
dict mid-iteration.


##### `hit_rate() -> float`

Calculate cache hit rate.

Returns:
    Hit rate as percentage (0-100)


##### `stats() -> Dict[str, Any]`

Get cache statistics.

Snapshot ``size`` once so that ``"size"`` and ``"utilization"`` are
consistent even if a concurrent eviction runs between the two calls.

Returns:
    Dictionary with cache statistics


##### `get_entry(key: str, version: Optional[str]) -> Optional[CacheEntry]`

Get full cache entry (for testing/debugging).

Args:
    key: The cache key
    version: Optional version

Returns:
    CacheEntry if found, None otherwise


##### `contains(key: str, version: Optional[str]) -> bool`

Check if key exists in cache.

Args:
    key: The cache key
    version: Optional version

Returns:
    True if key exists, False otherwise


##### `evict(key: str, version: Optional[str]) -> bool`

Manually evict a specific key.

Args:
    key: The cache key to evict
    version: Optional version

Returns:
    True if key was evicted, False if not found


##### `get_oldest_entry() -> Optional[tuple[str, CacheEntry]]`

Get the oldest (LRU) entry without removing it.

Returns:
    Tuple of (key, entry) for oldest entry, or None if empty


##### `get_newest_entry() -> Optional[tuple[str, CacheEntry]]`

Get the newest (MRU) entry without removing it.

Returns:
    Tuple of (key, entry) for newest entry, or None if empty


##### `migrate(from_version: str, to_version: str) -> int`

Migrate entries from one version to another.

.. note::
    **Always returns 0.**  ExactCache stores prompts as irreversible
    SHA-256 hashes.  Without the original key string it is impossible to
    reconstruct a new versioned entry, so migration between version
    namespaces is not supported.  The log event ``cache_migration_skipped``
    (with ``reason="irreversible_hash"``) is emitted so callers can
    distinguish "nothing to migrate" from "migration not supported".

Args:
    from_version: Source version (ignored — keys are not reversible)
    to_version: Target version (ignored — keys are not reversible)

Returns:
    Always 0.


##### `cleanup_version(version: str) -> int`

Remove all entries for a specific version.

Args:
    version: Version to clean up

Returns:
    Number of entries removed


##### `reset_stats() -> None`

Reset statistics counters.


