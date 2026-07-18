---
title: "Cache API Reference"
category: references
tags: [references]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Cache API Reference

## Overview
Complete API reference for the Token Optimization System's caching layer. This document covers all cache classes, methods, parameters, and return types.

## Module: src.cache

### CacheInterface (Abstract Base Class)

**File**: `src/cache/base.py`

Abstract base class defining the common interface for all cache implementations.

#### Methods

##### `get(key: str) -> Optional[str]`

Retrieve a value from the cache.

**Parameters**:
- `key` (str): The cache key to lookup

**Returns**:
- `Optional[str]`: The cached value if found, `None` otherwise

**Example**:
```python
from src.cache import ExactCache

cache = ExactCache()
result = cache.get("my_key")
if result:
    print(f"Found: {result}")
else:
    print("Cache miss")
```

##### `set(key: str, value: str) -> None`

Store a key-value pair in the cache.

**Parameters**:
- `key` (str): The cache key
- `value` (str): The value to store

**Returns**: None

**Example**:
```python
cache.set("my_key", "my_value")
```

##### `clear() -> None`

Remove all entries from the cache.

**Returns**: None

**Example**:
```python
cache.clear()
print("Cache cleared")
```

##### `get_stats() -> Dict[str, Any]`

Get cache statistics.

**Returns**:
- `Dict[str, Any]`: Dictionary containing cache statistics

**Statistics Keys**:
- `hits` (int): Number of successful lookups
- `misses` (int): Number of failed lookups
- `total_requests` (int): Total number of get() calls
- `hit_rate` (float): Ratio of hits to total requests (0.0-1.0)

**Example**:
```python
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']*100:.1f}%")
print(f"Total requests: {stats['total_requests']}")
```

---

### ExactCache

**File**: `src/cache/exact_cache.py`

Fast exact-match cache using SHA-256 hashing with LRU eviction.

#### Constructor

##### `__init__(max_size: int = 1000)`

Initialize an exact match cache.

**Parameters**:
- `max_size` (int, optional): Maximum number of entries. Default: 1000

**Example**:
```python
from src.cache import ExactCache

# Default size
cache = ExactCache()

# Custom size
cache = ExactCache(max_size=500)
```

#### Methods

Inherits all methods from `CacheInterface`.

##### `get(key: str) -> Optional[str]`

Retrieve value using exact key match (SHA-256 hash).

**Performance**: O(1) average case, <1ms

**Parameters**:
- `key` (str): The exact key to lookup

**Returns**:
- `Optional[str]`: Cached value if exact match found, `None` otherwise

**Example**:
```python
cache = ExactCache()
cache.set("What is Python?", "Python is a programming language")

# Exact match - returns value
result = cache.get("What is Python?")  # Hit

# Different text - returns None
result = cache.get("What is python?")  # Miss (case sensitive)
```

##### `set(key: str, value: str) -> None`

Store key-value pair with LRU tracking.

**Performance**: O(1)

**Behavior**:
- If cache is full, removes least recently used entry
- Updates access time for existing keys

**Parameters**:
- `key` (str): Cache key (will be hashed with SHA-256)
- `value` (str): Value to store

**Example**:
```python
cache = ExactCache(max_size=2)
cache.set("key1", "value1")
cache.set("key2", "value2")
cache.set("key3", "value3")  # Evicts key1 (LRU)
```

##### `get_stats() -> Dict[str, Any]`

Get cache statistics including size information.

**Returns**:
```python
{
    "hits": int,              # Successful lookups
    "misses": int,            # Failed lookups
    "total_requests": int,    # hits + misses
    "hit_rate": float,        # hits / total_requests
    "size": int,              # Current number of entries
    "max_size": int           # Maximum capacity
}
```

**Example**:
```python
stats = cache.get_stats()
print(f"Cache utilization: {stats['size']}/{stats['max_size']}")
```

---

### SemanticCache

**File**: `src/cache/semantic_cache.py`

Similarity-based cache using TF-IDF embeddings and cosine similarity.

#### Constructor

##### `__init__(max_size: int = 500, threshold: float = 0.85)`

Initialize a semantic similarity cache.

**Parameters**:
- `max_size` (int, optional): Maximum number of entries. Default: 500
- `threshold` (float, optional): Minimum similarity score (0.0-1.0). Default: 0.85

**Example**:
```python
from src.cache import SemanticCache

# Default configuration
cache = SemanticCache()

# Custom configuration
cache = SemanticCache(max_size=250, threshold=0.80)
```

#### Methods

Inherits all methods from `CacheInterface`.

##### `get(key: str) -> Optional[str]`

Retrieve value using semantic similarity matching.

**Performance**: O(n) where n = cache size, <100ms typical

**Algorithm**:
1. Generate TF-IDF embedding for query
2. Compare with all cached embeddings using cosine similarity
3. Return value if best match exceeds threshold

**Parameters**:
- `key` (str): Query text to match semantically

**Returns**:
- `Optional[str]`: Value of best matching entry if similarity ≥ threshold, `None` otherwise

**Example**:
```python
cache = SemanticCache(threshold=0.85)
cache.set("How do I install Python?", "Use pip install...")

# Semantically similar - returns value
result = cache.get("What's the process for installing Python?")  # Hit (similarity ~0.90)

# Not similar enough - returns None
result = cache.get("How do I cook pasta?")  # Miss (similarity ~0.20)
```

##### `set(key: str, value: str) -> None`

Store key-value pair with TF-IDF embedding.

**Performance**: O(m) where m = text length

**Behavior**:
- Generates and stores TF-IDF embedding
- If cache is full, removes oldest entry (FIFO)

**Parameters**:
- `key` (str): Cache key (will be embedded)
- `value` (str): Value to store

**Example**:
```python
cache = SemanticCache()
cache.set("Explain decorators", "Decorators modify function behavior...")
```

##### `get_stats() -> Dict[str, Any]`

Get cache statistics including similarity information.

**Returns**:
```python
{
    "hits": int,              # Successful semantic matches
    "misses": int,            # No match above threshold
    "total_requests": int,    # hits + misses
    "hit_rate": float,        # hits / total_requests
    "size": int,              # Current number of entries
    "max_size": int,          # Maximum capacity
    "threshold": float        # Similarity threshold
}
```

**Example**:
```python
stats = cache.get_stats()
print(f"Semantic threshold: {stats['threshold']}")
print(f"Hit rate: {stats['hit_rate']*100:.1f}%")
```

---

### MultiLevelCache

**File**: `src/cache/multi_level_cache.py`

Orchestrates L1 (exact) and L2 (semantic) caches with automatic promotion.

#### Constructor

##### `__init__(l1_cache: CacheInterface, l2_cache: CacheInterface)`

Initialize multi-level cache with L1 and L2 implementations.

**Parameters**:
- `l1_cache` (CacheInterface): Fast exact-match cache (typically ExactCache)
- `l2_cache` (CacheInterface): Slower semantic cache (typically SemanticCache)

**Example**:
```python
from src.cache import ExactCache, SemanticCache, MultiLevelCache

l1 = ExactCache(max_size=1000)
l2 = SemanticCache(max_size=500, threshold=0.85)
cache = MultiLevelCache(l1, l2)
```

#### Methods

##### `get(key: str) -> Optional[str]`

Retrieve value with L1→L2 fallback and automatic promotion.

**Performance**:
- L1 hit: <1ms
- L2 hit: <100ms (includes promotion to L1)
- Both miss: <100ms

**Algorithm**:
1. Try L1 cache (exact match)
2. If L1 miss, try L2 cache (semantic match)
3. If L2 hit, promote to L1 for future speed
4. Return result or None

**Parameters**:
- `key` (str): Cache key to lookup

**Returns**:
- `Optional[str]`: Cached value if found in L1 or L2, `None` otherwise

**Example**:
```python
cache = MultiLevelCache(l1, l2)

# First request - L2 hit, promoted to L1
result = cache.get("How to use decorators?")  # ~100ms

# Second identical request - L1 hit
result = cache.get("How to use decorators?")  # <1ms
```

##### `set(key: str, value: str) -> None`

Store key-value pair in both L1 and L2 caches.

**Performance**: O(1) for L1 + O(m) for L2

**Parameters**:
- `key` (str): Cache key
- `value` (str): Value to store

**Example**:
```python
cache.set("my_query", "my_response")
# Now stored in both L1 and L2
```

##### `clear() -> None`

Clear both L1 and L2 caches.

**Example**:
```python
cache.clear()
print("All caches cleared")
```

##### `get_stats() -> Dict[str, Any]`

Get combined statistics from both cache levels.

**Returns**:
```python
{
    "l1_hits": int,              # L1 successful lookups
    "l1_misses": int,            # L1 failed lookups
    "l1_hit_rate": float,        # L1 hit rate
    "l2_hits": int,              # L2 successful lookups
    "l2_misses": int,            # L2 failed lookups
    "l2_hit_rate": float,        # L2 hit rate
    "promotions": int,           # L2→L1 promotions
    "combined_hit_rate": float,  # Overall hit rate
    "total_requests": int        # Total get() calls
}
```

**Example**:
```python
stats = cache.get_stats()
print(f"L1 Hit Rate: {stats['l1_hit_rate']*100:.1f}%")
print(f"L2 Hit Rate: {stats['l2_hit_rate']*100:.1f}%")
print(f"Combined: {stats['combined_hit_rate']*100:.1f}%")
print(f"Promotions: {stats['promotions']}")
```

---

### EmbeddingGenerator

**File**: `src/cache/embeddings.py`

Generates TF-IDF embeddings for semantic similarity matching.

#### Constructor

##### `__init__(max_features: int = 1000)`

Initialize TF-IDF embedding generator.

**Parameters**:
- `max_features` (int, optional): Maximum vocabulary size. Default: 1000

**Example**:
```python
from src.cache.embeddings import EmbeddingGenerator

embeddings = EmbeddingGenerator(max_features=500)
```

#### Methods

##### `get_embedding(text: str) -> np.ndarray`

Generate TF-IDF embedding vector for text.

**Performance**: O(m) where m = text length

**Parameters**:
- `text` (str): Input text to embed

**Returns**:
- `np.ndarray`: TF-IDF embedding vector (shape: [max_features])

**Example**:
```python
embeddings = EmbeddingGenerator()
vector = embeddings.get_embedding("How to use Python decorators?")
print(f"Embedding shape: {vector.shape}")  # (1000,)
```

##### `cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float`

Calculate cosine similarity between two embedding vectors.

**Performance**: O(n) where n = vector dimension

**Parameters**:
- `vec1` (np.ndarray): First embedding vector
- `vec2` (np.ndarray): Second embedding vector

**Returns**:
- `float`: Similarity score (0.0-1.0)
  - 1.0 = identical
  - 0.0 = completely different

**Example**:
```python
embeddings = EmbeddingGenerator()
vec1 = embeddings.get_embedding("Python decorators")
vec2 = embeddings.get_embedding("Python function wrappers")
similarity = embeddings.cosine_similarity(vec1, vec2)
print(f"Similarity: {similarity:.2f}")  # ~0.85
```

---

## Usage Examples

### Example 1: Basic ExactCache Usage

```python
from src.cache import ExactCache

# Initialize cache
cache = ExactCache(max_size=100)

# Store values
cache.set("user:123", "John Doe")
cache.set("user:456", "Jane Smith")

# Retrieve values
user = cache.get("user:123")
print(user)  # "John Doe"

# Check statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']*100:.1f}%")
```

### Example 2: SemanticCache with Similarity

```python
from src.cache import SemanticCache

# Initialize with custom threshold
cache = SemanticCache(max_size=50, threshold=0.80)

# Store documentation
cache.set(
    "How do I install packages in Python?",
    "Use pip: pip install package_name"
)

# Query with different wording
result = cache.get("What's the way to add Python packages?")
print(result)  # "Use pip: pip install package_name"
```

### Example 3: MultiLevelCache with Promotion

```python
from src.cache import ExactCache, SemanticCache, MultiLevelCache

# Setup multi-level cache
l1 = ExactCache(max_size=1000)
l2 = SemanticCache(max_size=500, threshold=0.85)
cache = MultiLevelCache(l1, l2)

# First query - stores in both caches
cache.set("What is Python?", "Python is a programming language")

# Exact match - L1 hit (<1ms)
result = cache.get("What is Python?")

# Similar query - L2 hit, promoted to L1 (~100ms)
result = cache.get("Can you explain Python?")

# Same similar query again - now L1 hit (<1ms)
result = cache.get("Can you explain Python?")

# Check promotion statistics
stats = cache.get_stats()
print(f"Promotions: {stats['promotions']}")
```

### Example 4: Cache Statistics Monitoring

```python
from src.cache import MultiLevelCache, ExactCache, SemanticCache

cache = MultiLevelCache(
    ExactCache(max_size=1000),
    SemanticCache(max_size=500, threshold=0.85)
)

# Simulate requests
for i in range(100):
    key = f"query_{i % 20}"  # 20 unique queries, repeated
    result = cache.get(key)
    if not result:
        cache.set(key, f"response_{i}")

# Analyze performance
stats = cache.get_stats()
print(f"""
Cache Performance Report:
========================
L1 Hit Rate: {stats['l1_hit_rate']*100:.1f}%
L2 Hit Rate: {stats['l2_hit_rate']*100:.1f}%
Combined Hit Rate: {stats['combined_hit_rate']*100:.1f}%
Total Requests: {stats['total_requests']}
Promotions: {stats['promotions']}
""")
```

## Performance Characteristics

### ExactCache
- **Lookup**: O(1) average, <1ms
- **Storage**: O(1)
- **Memory**: ~5KB per entry
- **Best For**: Identical repeated queries

### SemanticCache
- **Lookup**: O(n) where n = cache size, <100ms
- **Storage**: O(m) where m = text length
- **Memory**: ~20KB per entry (includes embedding)
- **Best For**: Similar but not identical queries

### MultiLevelCache
- **L1 Hit**: <1ms
- **L2 Hit**: <100ms (includes promotion)
- **Both Miss**: <100ms
- **Memory**: L1 + L2 combined (~15MB typical)

## Error Handling

All cache methods handle errors gracefully:

```python
from src.cache import ExactCache

cache = ExactCache()

# Invalid key type - raises TypeError
try:
    cache.get(123)  # Must be string
except TypeError as e:
    print(f"Error: {e}")

# Empty key - returns None
result = cache.get("")  # None

# None value - raises ValueError
try:
    cache.set("key", None)  # Must be string
except ValueError as e:
    print(f"Error: {e}")
```

## Thread Safety

**Note**: Current implementation is **not thread-safe**. For concurrent access:

```python
import threading
from src.cache import ExactCache

cache = ExactCache()
lock = threading.Lock()

def safe_get(key):
    with lock:
        return cache.get(key)

def safe_set(key, value):
    with lock:
        cache.set(key, value)
```

## Related Documents
- [Multi-Level Caching Concept](../concepts/multi-level-caching.md) - Architecture overview
- [Token Optimization Concept](../concepts/token-optimization.md) - System overview
- [Setup Guide](../guides/setup-token-optimization.md) - Installation instructions
- [Performance Benchmarks](../research/performance-benchmarks.md) - Real-world measurements

## References
- [System Architecture](../../architecture/ARCHITECTURE.md) - Complete architecture
- [ADR-002: Caching Strategy](../../adr/002-caching-strategy.md) - Design decisions
- [Source Code](../../../src/cache/) - Implementation files

---
*Last Updated: 2026-07-13*
*Category: Reference*
