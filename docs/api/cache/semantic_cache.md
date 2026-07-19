# semantic_cache

Semantic similarity cache (L2) implementation with version support.

This module implements a semantic similarity cache using embeddings and
cosine similarity. Provides approximate matches for semantically similar prompts.

Target metrics:
- Lookup latency: <100ms
- Similarity threshold: 0.85 (configurable)
- Hit rate is workload-dependent, measured per run by the Phase-5 validation
  harness -- not a fixed target. The old "~5-8% of 23.33%" figure is retired.

## Classes

### `SemanticCache(CacheInterface)`

L2 cache for semantically similar prompts with version support.

Uses stateless HashingVectorizer embeddings and cosine similarity to find
similar prompts. An exact-key fast-path in ``get()`` guarantees an
exactly-stored key returns its own value (never a hash-colliding neighbour's);
the similarity search is the fallback for non-exact, semantically-close keys.
Slower than exact cache but provides fuzzy matching. Supports versioning
for cache evolution without breaking existing cached data.

Attributes:
    VERSION: Current cache version
    similarity_threshold: Minimum similarity score (0-1) for cache hit
    max_size: Maximum number of entries
    embeddings: Dictionary mapping versioned prompts to embeddings
    responses: Dictionary mapping versioned prompts to responses
    metadata_store: Dictionary mapping versioned prompts to metadata
    embedding_generator: Embedding generator instance
    stats: Cache statistics tracker

#### Methods

##### `__init__(similarity_threshold: float, max_size: int, track_costs: bool, ttl_seconds: Optional[float], clock: Callable[[], float])`

Initialize semantic cache.

Args:
    similarity_threshold: Minimum similarity for cache hit (0-1)
    max_size: Maximum number of entries before eviction
    track_costs: Whether to track costs with CostTracker
    ttl_seconds: Optional entry time-to-live. When set, a matched entry
        older than this (by creation timestamp) is treated as a miss and
        evicted on read. ``None`` disables expiry (default).
    clock: Time source for stamping/expiry, injectable for
        deterministic tests. Defaults to ``time.time``.


##### `get(key: str, version: Optional[str]) -> Optional[str]`

Retrieve cached response for semantically similar key.

Thread-safe: Uses lock to protect shared state.

Args:
    key: The cache key (prompt)
    version: Optional version (defaults to current VERSION)

Returns:
    Cached response if similar match found, None otherwise


##### `set(key: str, value: str, version: Optional[str], metadata: Optional[Dict[str, Any]]) -> None`

Store response in cache with embedding.

Thread-safe: Uses lock to protect shared state.

Args:
    key: The cache key (prompt)
    value: The response to cache
    version: Optional version (defaults to current VERSION)
    metadata: Optional metadata


##### `clear() -> None`

Clear all entries from cache.

Thread-safe: Uses lock to protect shared state.


##### `size() -> int`

Get number of entries in cache.

Thread-safe: Uses lock to protect shared state.

Returns:
    Number of cached entries


##### `snapshot_keys() -> list`

Return a point-in-time copy of the embedding keys, taken under the lock.

Callers (e.g. ``MultiLevelCache.size()``) must iterate this list, never
``self.embeddings`` directly, so a concurrent ``set``/eviction cannot mutate
the dict mid-iteration.


##### `hit_rate() -> float`

Calculate cache hit rate.

Returns:
    Hit rate as percentage (0-100)


##### `stats() -> Dict[str, Any]`

Get cache statistics.

Thread-safe: Uses lock to protect shared state.

Returns:
    Dictionary with cache statistics


##### `find_similar(key: str, top_k: int, version: Optional[str]) -> List[Tuple[str, float, str]]`

Find top-k most similar cached prompts.

Thread-safe: Uses lock to protect shared state.

Args:
    key: Query prompt
    top_k: Number of results to return
    version: Optional version to search within

Returns:
    List of (prompt, similarity, response) tuples


##### `get_with_similarity(key: str, version: Optional[str]) -> Optional[Tuple[str, float]]`

Get cached response with similarity score.

Thread-safe: Uses lock to protect shared state.

Args:
    key: The cache key (prompt)
    version: Optional version

Returns:
    Tuple of (response, similarity_score) if found, None otherwise


##### `contains(key: str, version: Optional[str]) -> bool`

Check if semantically similar key exists in cache.

Args:
    key: The cache key
    version: Optional version

Returns:
    True if similar key exists, False otherwise


##### `get_threshold() -> float`

Return the current similarity threshold under ``self._lock``.

Thread-safe read for callers (e.g. ``MultiLevelCache.stats()``) that
need a consistent snapshot of the threshold without holding their own
lock.  Mirrors the pattern of :meth:`average_similarity_score`.

Returns:
    Current similarity threshold (0-1).


##### `update_threshold(new_threshold: float) -> None`

Update similarity threshold.

Args:
    new_threshold: New threshold value (0-1)


##### `get_entry(key: str, version: Optional[str]) -> Optional[CacheEntry]`

Get full cache entry.

Thread-safe: Uses lock to protect shared state. The entries dict can be
mutated by a concurrent set(), _evict_lru(), or clear() — acquiring
self._lock here prevents a read of a partially-removed entry.

Args:
    key: The cache key
    version: Optional version

Returns:
    CacheEntry if found, None otherwise


##### `average_similarity_score() -> float`

Get average similarity score for cache hits.

Thread-safe: Takes a snapshot of ``_similarity_scores`` under
``self._lock`` so that a concurrent ``reset_stats()`` cannot clear the
list between the ``if not`` guard and the ``sum()`` call.

Returns:
    Average similarity score (0-1)


##### `migrate(from_version: str, to_version: str) -> int`

Migrate entries from one version to another.

Thread-safe: Holds ``self._lock`` (a re-entrant ``RLock``) for the full
duration — both the collection phase and all ``set()`` calls — so the
migration is atomic with respect to concurrent writers.  ``set()`` also
acquires ``self._lock``, which is safe because ``RLock`` allows
re-entrant acquisition from the same thread.

Creates new versioned entries for all entries matching from_version.
Original entries are preserved.

Args:
    from_version: Source version
    to_version: Target version

Returns:
    Number of entries migrated


##### `cleanup_version(version: str) -> int`

Remove all entries for a specific version.

Thread-safe: Uses lock to protect shared state.

Args:
    version: Version to clean up

Returns:
    Number of entries removed


##### `reset_stats() -> None`

Reset statistics counters.

Thread-safe: Both ``_stats.reset()`` and ``_similarity_scores.clear()``
are performed atomically under ``self._lock`` so that a concurrent
``average_similarity_score()`` or ``stats()`` call cannot observe a
half-reset state.


