# multi_level_cache

Multi-level cache combining L1 (exact) and L2 (semantic) caches.

This module implements a two-level caching strategy:
- L1: ExactCache for fast exact matches (<1ms)
- L2: SemanticCache for semantic similarity matches (<100ms)

L2 hits are promoted to L1 for future fast access.

Target metrics:
- Overall lookup latency: <100ms
- Combined hit rate: 23.33%
- L1 hit rate: ~15-18%
- L2 hit rate: ~5-8%

## Classes

### `MultiLevelCache(CacheInterface)`

Two-level cache with exact (L1) and semantic (L2) matching.

Provides fast exact matches via L1 and semantic fallback via L2.
Automatically promotes L2 hits to L1 for improved performance.

Attributes:
    l1_cache: ExactCache for fast exact matches
    l2_cache: SemanticCache for semantic similarity
    promote_l2_hits: Whether to promote L2 hits to L1
    l1_hits: Count of L1 cache hits
    l2_hits: Count of L2 cache hits
    misses: Count of cache misses

#### Methods

##### `__init__(l1_max_size: int, l2_max_size: int, similarity_threshold: float, promote_l2_hits: bool)`

Initialize multi-level cache.

Args:
    l1_max_size: Maximum size for L1 cache
    l2_max_size: Maximum size for L2 cache
    similarity_threshold: Similarity threshold for L2
    promote_l2_hits: Whether to promote L2 hits to L1


##### `get(key: str) -> Optional[str]`

Retrieve cached response, trying L1 then L2.

Args:
    key: The cache key (prompt)
    
Returns:
    Cached response if found in L1 or L2, None otherwise


##### `set(key: str, response: str, metadata: Optional[Dict[str, Any]]) -> None`

Store response in both L1 and L2 caches.

Args:
    key: The cache key (prompt)
    response: The response to cache
    metadata: Optional metadata


##### `clear() -> None`

Clear both L1 and L2 caches.


##### `size() -> int`

Get total number of unique entries across both caches.

Returns:
    Number of unique cached entries


##### `hit_rate() -> float`

Calculate overall cache hit rate.

Returns:
    Hit rate as percentage (0-100)


##### `l1_hit_rate() -> float`

Calculate L1 cache hit rate.

Returns:
    L1 hit rate as percentage (0-100)


##### `l2_hit_rate() -> float`

Calculate L2 cache hit rate.

Returns:
    L2 hit rate as percentage (0-100)


##### `stats() -> Dict[str, Any]`

Get comprehensive cache statistics.

Returns:
    Dictionary with cache statistics


##### `get_l1_cache() -> ExactCache`

Get L1 cache instance.

Returns:
    ExactCache instance


##### `get_l2_cache() -> SemanticCache`

Get L2 cache instance.

Returns:
    SemanticCache instance


##### `update_similarity_threshold(threshold: float) -> None`

Update L2 similarity threshold.

Args:
    threshold: New threshold value (0-1)


##### `enable_promotion() -> None`

Enable L2 to L1 promotion.


##### `disable_promotion() -> None`

Disable L2 to L1 promotion.


##### `get_with_level(key: str) -> Optional[Tuple[str, str]]`

Get cached response with cache level information.

Args:
    key: The cache key (prompt)
    
Returns:
    Tuple of (response, level) where level is 'L1' or 'L2', or None


##### `contains(key: str) -> bool`

Check if key exists in either cache.

Args:
    key: The cache key
    
Returns:
    True if key exists in L1 or L2, False otherwise


##### `average_lookup_time_ms() -> float`

Get average lookup time in milliseconds.

Returns:
    Average lookup time in ms


##### `reset_stats() -> None`

Reset statistics counters.


