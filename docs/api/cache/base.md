# base

Base cache interface with version support.

This module defines the abstract base class for all cache implementations,
providing a common interface and version support for cache evolution.

## Functions

### `escape_version(version: str) -> str`

Percent-escape ``version`` so it can never contain the ``:`` delimiter.

Cache keys are built as ``f"{escape_version(version)}:{key}"``. Escaping the
version's ``:`` (and the ``%`` escape char itself) makes that encoding
*injective* over ``(version, key)`` pairs. Without it the raw
``f"{version}:{key}"`` collides: ``set('b', version='v1:a')`` and
``set('a:b', version='v1')`` both render ``'v1:a:b'``, so the second write
silently overwrites the first and a reader gets the wrong content. Both L1
(:class:`ExactCache`) and L2 (:class:`SemanticCache`) use this so their keys
stay consistent (``MultiLevelCache.size()`` cross-hashes between them).


### `unescape_version(escaped: str) -> str`

Inverse of :func:`escape_version` (recovers the original version string).


## Classes

### `CacheEntry`

Cache entry with metadata and access tracking.

Attributes:
    response: Cached response value
    metadata: Optional metadata dictionary
    timestamp: Creation timestamp
    last_access: Last access timestamp
    access_count: Number of times accessed

#### Methods

##### `access() -> None`

Record an access to this entry.


##### `age_seconds() -> float`

Calculate age of entry in seconds.

Returns:
    Age in seconds since creation


##### `idle_seconds() -> float`

Calculate idle time in seconds.

Returns:
    Seconds since last access



### `CacheStats`

Cache statistics tracker.

Attributes:
    hits: Number of cache hits
    misses: Number of cache misses
    evictions: Number of evictions

#### Methods

##### `record_hit() -> None`

Record a cache hit.


##### `record_miss() -> None`

Record a cache miss.


##### `record_eviction() -> None`

Record an eviction.


##### `hit_rate() -> float`

Calculate hit rate as percentage.

Returns:
    Hit rate (0-100)


##### `reset() -> None`

Reset all statistics.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.

Returns:
    Dictionary with statistics



### `CacheStatsSnapshot`

Immutable point-in-time snapshot of ``MultiLevelCache.stats()``.

All fields are populated at construction time inside a single lock block
in ``MultiLevelCache.stats()``.  The frozen dataclass makes the assembly
contract structural: mypy catches a missing field at the construction call
site, so the snapshot-discipline failures found in Rounds 1–4 cannot
recur silently.

**Do not mutate field values after construction** — ``frozen=True``
enforces this at runtime.

See ``src/cache/CONCURRENCY.md`` for the snapshot pattern and the rule
that every new counter added to ``MultiLevelCache`` must be added here
in the same commit.

Attributes:
    total_requests: Total get() + query_l3() calls (hits + misses).
    total_hits: Total L1 + L2 + L3 hits.
    total_misses: Total cache misses.
    hit_rate: Overall hit ratio expressed as a percentage (range 0–100).
    avg_lookup_time_ms: Rolling average lookup latency in milliseconds.
    version: Cache version string.
    l1_hits: L1 (exact) cache hit count.
    l1_hit_rate: L1 cache hit ratio expressed as a percentage (range 0–100).
    l1_size: Current number of entries in L1.
    l1_max_size: Maximum capacity of L1 (construction-time constant).
    l1_utilization: l1_size / l1_max_size * 100.
    l2_hits: L2 (semantic) cache hit count.
    l2_hit_rate: L2 cache hit ratio expressed as a percentage (range 0–100).
    l2_size: Current number of entries in L2.
    l2_max_size: Maximum capacity of L2 (construction-time constant).
    l2_utilization: l2_size / l2_max_size * 100.
    l2_similarity_threshold: Active cosine-similarity threshold for L2.
    l2_avg_similarity: Rolling average similarity score for L2 hits.
    l3_hits: L3 (persistent index) hit count (0 when no L3 is wired).
    promote_l2_hits: Whether L2→L1 promotion is currently enabled.
    unique_entries: Deduplicated key count across L1 ∪ L2.

#### Methods

##### `to_dict() -> Dict[str, Any]`

Return a plain ``dict`` with the same shape as the pre-dataclass
``MultiLevelCache.stats()`` return value.

All existing callers (30+ sites across 10 files) continue to receive
a ``dict`` and require no changes.



### `CacheInterface(ABC)`

Abstract base class for cache implementations with version support.

All cache implementations must inherit from this class and implement
the required methods. Version support enables cache evolution without
breaking existing cached data.

Attributes:
    VERSION: Default cache version (class attribute)

#### Methods

##### `get(key: str, version: Optional[str]) -> Optional[str]`

Retrieve cached value for key.

Args:
    key: Cache key
    version: Optional version to retrieve from (defaults to current)

Returns:
    Cached value if found, None otherwise


##### `set(key: str, value: str, version: Optional[str], metadata: Optional[Dict[str, Any]]) -> None`

Store key-value pair in cache.

Args:
    key: Cache key
    value: Value to cache
    version: Optional version to store in (defaults to current)
    metadata: Optional metadata to store with entry


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


##### `migrate(from_version: str, to_version: str) -> int`

Migrate entries from one version to another.

Default implementation raises NotImplementedError.
Subclasses should override if migration is supported.

Args:
    from_version: Source version
    to_version: Target version

Returns:
    Number of entries migrated

Raises:
    NotImplementedError: If migration not supported


##### `cleanup_version(version: str) -> int`

Remove all entries for a specific version.

Default implementation raises NotImplementedError.
Subclasses should override if version cleanup is supported.

Args:
    version: Version to clean up

Returns:
    Number of entries removed

Raises:
    NotImplementedError: If cleanup not supported


##### `get_entry(key: str, version: Optional[str]) -> Optional[CacheEntry]`

Get full cache entry with metadata.

Default implementation returns None.
Subclasses should override to provide entry details.

Args:
    key: Cache key
    version: Optional version

Returns:
    CacheEntry if found, None otherwise


##### `contains(key: str, version: Optional[str]) -> bool`

Check if key exists in cache.

Default implementation uses get().
Subclasses may override for efficiency.

Args:
    key: Cache key
    version: Optional version

Returns:
    True if key exists, False otherwise


##### `reset_stats() -> None`

Reset statistics counters.

Default implementation does nothing.
Subclasses should override to reset their statistics.


