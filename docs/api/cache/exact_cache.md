# exact_cache

Exact match cache (L1) implementation with version support.

This module implements a hash-based exact match cache with LRU eviction.
Provides O(1) lookup time for exact prompt matches.

Target metrics:
- Lookup latency: <1ms
- Hit rate: workload-dependent (measured per run by the Phase-5 validation
  harness, not a fixed target; the old "23.33% theoretical" figure is retired)
- Memory: Configurable max size with LRU eviction

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

##### `__init__(max_size: int, track_costs: bool, ttl_seconds: Optional[float], clock: Callable[[], float])`

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


##### `hit_rate() -> float`

Calculate cache hit rate.

Returns:
    Hit rate as percentage (0-100)


##### `stats() -> Dict[str, Any]`

Get cache statistics.

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

Creates new versioned entries for all entries matching from_version.
Original entries are preserved.

Args:
    from_version: Source version
    to_version: Target version

Returns:
    Number of entries migrated


##### `cleanup_version(version: str) -> int`

Remove all entries for a specific version.

Args:
    version: Version to clean up

Returns:
    Number of entries removed


##### `reset_stats() -> None`

Reset statistics counters.


