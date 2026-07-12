# semantic_cache

Semantic similarity cache (L2) implementation.

This module implements a semantic similarity cache using embeddings and
cosine similarity. Provides approximate matches for semantically similar prompts.

Target metrics:
- Lookup latency: <100ms
- Similarity threshold: 0.85 (configurable)
- Hit rate contribution: ~5-8% of total 23.33%

## Classes

### `SemanticCache(CacheInterface)`

L2 cache for semantically similar prompts.

Uses TF-IDF embeddings and cosine similarity to find similar prompts.
Slower than exact cache but provides fuzzy matching.

Attributes:
    similarity_threshold: Minimum similarity score (0-1) for cache hit
    max_size: Maximum number of entries
    embeddings: Dictionary mapping prompts to embeddings
    responses: Dictionary mapping prompts to responses
    metadata_store: Dictionary mapping prompts to metadata
    embedding_generator: Embedding generator instance
    stats: Cache statistics tracker

#### Methods

##### `__init__(similarity_threshold: float, max_size: int)`

Initialize semantic cache.

Args:
    similarity_threshold: Minimum similarity for cache hit (0-1)
    max_size: Maximum number of entries before eviction


##### `get(key: str) -> Optional[str]`

Retrieve cached response for semantically similar key.

Args:
    key: The cache key (prompt)
    
Returns:
    Cached response if similar match found, None otherwise


##### `set(key: str, response: str, metadata: Optional[Dict[str, Any]]) -> None`

Store response in cache with embedding.

Args:
    key: The cache key (prompt)
    response: The response to cache
    metadata: Optional metadata


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


##### `find_similar(key: str, top_k: int) -> List[Tuple[str, float, str]]`

Find top-k most similar cached prompts.

Args:
    key: Query prompt
    top_k: Number of results to return
    
Returns:
    List of (prompt, similarity, response) tuples


##### `get_with_similarity(key: str) -> Optional[Tuple[str, float]]`

Get cached response with similarity score.

Args:
    key: The cache key (prompt)
    
Returns:
    Tuple of (response, similarity_score) if found, None otherwise


##### `contains_similar(key: str) -> bool`

Check if semantically similar key exists in cache.

Args:
    key: The cache key
    
Returns:
    True if similar key exists, False otherwise


##### `update_threshold(new_threshold: float) -> None`

Update similarity threshold.

Args:
    new_threshold: New threshold value (0-1)


##### `get_entry(key: str) -> Optional[CacheEntry]`

Get full cache entry.

Args:
    key: The cache key
    
Returns:
    CacheEntry if found, None otherwise


##### `average_similarity_score() -> float`

Get average similarity score for cache hits.

Returns:
    Average similarity score (0-1)


