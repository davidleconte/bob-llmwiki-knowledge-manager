# base

Base classes and interfaces for caching system.

This module defines the abstract interfaces and data structures used
throughout the caching system.

## Classes

### `CacheEntry`

Represents a cached item with metadata.

Attributes:
    response: The cached response content
    metadata: Additional metadata (tokens, quality, etc.)
    timestamp: When the entry was cached (Unix timestamp)
    access_count: Number of times this entry was accessed
    last_access: Last access timestamp

#### Methods

##### `access() -> None`

Record an access to this entry.


##### `age_seconds() -> float`

Get age of entry in seconds.


##### `idle_seconds() -> float`

Get time since last access in seconds.



### `CacheInterface(ABC)`

Abstract interface for cache implementations.

All cache implementations must provide these methods.

#### Methods

##### `get(key: str) -> Optional[str]`

Retrieve cached response for key.

Args:
    key: The cache key (usually prompt or hash)
    
Returns:
    Cached response if found, None otherwise


##### `set(key: str, response: str, metadata: Optional[Dict[str, Any]]) -> None`

Store response in cache.

Args:
    key: The cache key
    response: The response to cache
    metadata: Optional metadata about the response


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



### `CacheStats`

Track cache statistics.

Attributes:
    hits: Number of cache hits
    misses: Number of cache misses
    evictions: Number of evicted entries
    total_lookups: Total number of lookups

#### Methods

##### `__init__()`


##### `record_hit() -> None`

Record a cache hit.


##### `record_miss() -> None`

Record a cache miss.


##### `record_eviction() -> None`

Record a cache eviction.


##### `hit_rate() -> float`

Calculate hit rate percentage.

Returns:
    Hit rate as percentage (0-100)


##### `miss_rate() -> float`

Calculate miss rate percentage.

Returns:
    Miss rate as percentage (0-100)


##### `to_dict() -> Dict[str, Any]`

Convert stats to dictionary.

Returns:
    Dictionary with all statistics


##### `reset() -> None`

Reset all statistics to zero.


