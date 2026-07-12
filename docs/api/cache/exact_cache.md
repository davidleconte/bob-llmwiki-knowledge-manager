# exact_cache

Exact match cache (L1) implementation.

This module implements a hash-based exact match cache with LRU eviction.
Provides O(1) lookup time for exact prompt matches.

Target metrics:
- Lookup latency: <1ms
- Hit rate contribution: ~15-20% of total 23.33%
- Memory: Configurable max size with LRU eviction

## Classes

### `ExactCache(CacheInterface)`

L1 cache for exact prompt matches.

Uses SHA-256 hashing for key generation and OrderedDict for LRU eviction.
Provides fast O(1) lookups for exact matches.

Attributes:
    max_size: Maximum number of entries (default: 1000)
    cache: OrderedDict storing cache entries
    stats: Cache statistics tracker

#### Methods

##### `__init__(max_size: int)`

Initialize exact cache.

Args:
    max_size: Maximum number of entries before eviction


##### `get(key: str) -> Optional[str]`

Retrieve cached response for exact key match.

Args:
    key: The cache key (prompt)
    
Returns:
    Cached response if found, None otherwise


##### `set(key: str, response: str, metadata: Optional[Dict[str, Any]]) -> None`

Store response in cache.

Args:
    key: The cache key (prompt)
    response: The response to cache
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


##### `get_entry(key: str) -> Optional[CacheEntry]`

Get full cache entry (for testing/debugging).

Args:
    key: The cache key
    
Returns:
    CacheEntry if found, None otherwise


##### `contains(key: str) -> bool`

Check if key exists in cache.

Args:
    key: The cache key
    
Returns:
    True if key exists, False otherwise


##### `evict(key: str) -> bool`

Manually evict a specific key.

Args:
    key: The cache key to evict
    
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


