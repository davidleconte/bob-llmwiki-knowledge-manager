# multi_level_cache

Multi-level cache combining L1 (exact), L2 (semantic), and optional L3 (persistent).

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

## Classes

### `MultiLevelCache(CacheInterface)`

Two-level cache with exact (L1) and semantic (L2) matching with version support.

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

#### Methods

##### `__init__(l1_max_size: int, l2_max_size: int, similarity_threshold: float, promote_l2_hits: bool, l1_ttl_seconds: Optional[float], l2_ttl_seconds: Optional[float], l1_enabled: bool, l2_enabled: bool, version_support_enabled: bool, max_versions: int, l3_index: Optional['PersistentEmbeddingIndex'])`

Initialize multi-level cache.

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


##### `get(key: str, version: Optional[str]) -> Optional[str]`

Retrieve cached *response*, trying L1 then L2.

This method is strictly in the **prompt-response** namespace.  It never
touches L3.  Use :meth:`query_l3` to search the persistent document index.

Args:
    key: The cache key (prompt)
    version: Optional version (defaults to current VERSION)

Returns:
    Cached response string if found in L1 or L2, ``None`` otherwise.
    The returned value is always a prompt *response*, never a document path.


##### `query_l3(query: str, top_k: int) -> Optional[Tuple[str, float]]`

Search the L3 persistent document index.

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


##### `set(key: str, value: str, version: Optional[str], metadata: Optional[Dict[str, Any]]) -> None`

Store response in both L1 and L2 caches.

Args:
    key: The cache key (prompt)
    value: The response to cache
    version: Optional version (defaults to current VERSION)
    metadata: Optional metadata


##### `clear() -> None`

Clear L1 and L2 caches (L3 index is NOT cleared — disk-backed).


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


##### `get_with_level(key: str, version: Optional[str]) -> Optional[Tuple[str, str]]`

Get cached response with cache level information.

Args:
    key: The cache key (prompt)
    version: Optional version

Returns:
    Tuple of (response, level) where level is 'L1' or 'L2', or None


##### `contains(key: str, version: Optional[str]) -> bool`

Check if key exists in either cache.

Args:
    key: The cache key
    version: Optional version

Returns:
    True if key exists in L1 or L2, False otherwise


##### `average_lookup_time_ms() -> float`

Get average lookup time in milliseconds.

Returns:
    Average lookup time in ms


##### `migrate(from_version: str, to_version: str) -> int`

Migrate entries from one version to another in both caches.

Args:
    from_version: Source version
    to_version: Target version

Returns:
    Total number of entries migrated across both caches


##### `cleanup_version(version: str) -> int`

Remove all entries for a specific version from both caches.

Args:
    version: Version to clean up

Returns:
    Total number of entries removed across both caches


##### `reset_stats() -> None`

Reset statistics counters.


