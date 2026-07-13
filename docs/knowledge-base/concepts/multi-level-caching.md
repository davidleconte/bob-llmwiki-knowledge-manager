# Multi-Level Caching

## Overview
Multi-level caching is a hierarchical caching strategy that combines multiple cache layers with different performance characteristics to optimize both speed and hit rate. The Token Optimization System implements a two-tier cache (L1 and L2) with automatic promotion to balance exact matching speed with semantic similarity flexibility.

## Key Points
- **L1 Cache (ExactCache)**: Fast exact-match cache using SHA-256 hashing with <1ms lookup time
- **L2 Cache (SemanticCache)**: Similarity-based cache using TF-IDF embeddings with <100ms lookup time
- **Automatic Promotion**: L2 hits are automatically promoted to L1 for faster future access
- **Combined Hit Rate**: Target of 23.33% (L1: 15-18%, L2: 5-8%)
- **Graceful Degradation**: Falls through cache levels sequentially on miss

## Details

### Architecture

The multi-level cache orchestrates two distinct caching strategies:

```
Request → L1 (Exact Match) → Hit? → Return (<1ms)
              ↓ Miss
         L2 (Semantic) → Hit? → Promote to L1 → Return (<100ms)
              ↓ Miss
         Process Request (Full optimization pipeline)
```

### L1: ExactCache

**Purpose**: Ultra-fast exact matching for repeated queries

**Implementation**:
- Hash-based lookup using SHA-256
- LRU (Least Recently Used) eviction policy
- Default capacity: 1000 entries
- Memory footprint: ~5MB

**Performance**:
- Lookup time: O(1) average case, <1ms
- Storage time: O(1)
- Target hit rate: 15-18%

**Use Cases**:
- Identical repeated queries
- Frequently accessed prompts
- Deterministic operations

### L2: SemanticCache

**Purpose**: Flexible matching for similar but not identical queries

**Implementation**:
- TF-IDF embeddings for text representation
- Cosine similarity matching (threshold: 0.85)
- Default capacity: 500 entries
- Memory footprint: ~10MB

**Performance**:
- Lookup time: O(n) where n = cache size, <100ms
- Embedding generation: O(m) where m = text length
- Target hit rate: 5-8%

**Use Cases**:
- Paraphrased queries
- Queries with minor variations
- Semantically equivalent requests

### Cache Promotion Strategy

When L2 returns a hit, the system automatically promotes the entry to L1:

1. **L2 Hit Detected**: Semantic match found above threshold
2. **Promotion**: Entry copied to L1 with original query as key
3. **Future Access**: Subsequent identical queries hit L1 directly
4. **Performance Gain**: Future lookups improve from ~100ms to <1ms

**Benefits**:
- Learns from usage patterns
- Optimizes frequently accessed similar queries
- Reduces L2 lookup overhead over time

### Cache Statistics

The system tracks comprehensive metrics:

```python
{
    "l1_hits": 150,           # Exact matches
    "l1_misses": 850,         # L1 misses
    "l1_hit_rate": 0.15,      # 15%
    "l2_hits": 68,            # Semantic matches
    "l2_misses": 782,         # L2 misses
    "l2_hit_rate": 0.08,      # 8%
    "promotions": 68,         # L2→L1 promotions
    "combined_hit_rate": 0.218 # 21.8% total
}
```

## Examples

### Example 1: Exact Match (L1 Hit)

```python
from src.cache import MultiLevelCache, ExactCache, SemanticCache

# Initialize cache
cache = MultiLevelCache(
    l1_cache=ExactCache(max_size=1000),
    l2_cache=SemanticCache(max_size=500, threshold=0.85)
)

# First request - cache miss
query = "What is the capital of France?"
result = cache.get(query)  # None (miss)

# Store result
cache.set(query, "Paris")

# Second identical request - L1 hit
result = cache.get(query)  # "Paris" (<1ms)
```

### Example 2: Semantic Match (L2 Hit with Promotion)

```python
# Original query stored
cache.set("How do I install Python?", "Use pip install...")

# Similar query - L2 hit
similar_query = "What's the process for installing Python?"
result = cache.get(similar_query)  # "Use pip install..." (<100ms)

# Promotion occurred - now in L1
result = cache.get(similar_query)  # "Use pip install..." (<1ms)
```

### Example 3: Cache Miss (Full Pipeline)

```python
# Completely new query
new_query = "Explain quantum computing"
result = cache.get(new_query)  # None (miss both L1 and L2)

# System proceeds to full optimization pipeline
# Result eventually stored in both caches
```

## Related Documents
- [Token Optimization](./token-optimization.md) - Overall optimization strategy
- [Cache API Reference](../references/cache-api.md) - Detailed API documentation
- [Setting Up Token Optimization System](../guides/setup-token-optimization.md) - Installation guide
- [Performance Benchmarks](../research/performance-benchmarks.md) - Real-world performance data

## References
- [System Architecture](../../architecture/ACTUAL_SYSTEM_ARCHITECTURE.md) - Complete system design
- [ADR-002: Caching Strategy](../../adr/002-caching-strategy.md) - Architecture decision
- [ADR-006: Cache Strategy](../../adr/006-cache-strategy.md) - Multi-level design rationale

---
*Last Updated: 2026-07-13*
*Category: Concept*
