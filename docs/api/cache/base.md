# base

Base cache interface with version support.

This module defines the abstract base class for all cache implementations,
providing a common interface and version support for cache evolution.

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


