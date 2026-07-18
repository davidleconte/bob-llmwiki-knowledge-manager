---
title: "Multi-Level Caching Architecture Patterns"
category: concept
tags: [cache, architecture-patterns, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Multi-Level Caching Architecture Patterns

## Overview
Multi-level caching architecture patterns organize cache layers in a hierarchy to optimize the trade-off between speed, capacity, and cost. By combining fast but expensive caches (L1) with slower but larger caches (L2, L3), systems achieve both high performance and high hit rates. This pattern is fundamental to modern computing, from CPU caches to distributed web applications.

## Key Points
- **Hierarchical Organization**: Multiple cache tiers with decreasing speed and increasing capacity (L1 → L2 → L3 → Storage)
- **Automatic Promotion**: Frequently accessed data moves up the hierarchy for faster future access
- **Graceful Degradation**: Cache misses fall through to slower tiers, never failing completely
- **Locality Principle**: Exploits temporal locality (recent access) and spatial locality (nearby data)
- **Universal Pattern**: Applied at every computing layer from CPU to CDN to application caches

## Details

### Cache Hierarchy Fundamentals

Multi-level caching mirrors the memory hierarchy in computer architecture:

```
Speed ↑    Capacity ↓    Cost ↑
─────────────────────────────────
L1 Cache    (Fastest, Smallest, Most Expensive)
    ↓
L2 Cache    (Fast, Medium, Moderate Cost)
    ↓
L3 Cache    (Moderate, Large, Lower Cost)
    ↓
Storage     (Slowest, Largest, Cheapest)
```

**Key Characteristics by Level:**

| Level | Typical Latency | Typical Size | Use Case |
|-------|----------------|--------------|----------|
| L1 | <1ms | 10-1000 entries | Hot data, exact matches |
| L2 | 1-100ms | 100-10000 entries | Warm data, semantic matches |
| L3 | 100-1000ms | 1000-100000 entries | Cold data, persistent storage |
| Storage | >1000ms | Unlimited | Source of truth |

### Common Cache Patterns

#### 1. Cache-Aside (Lazy Loading)

**Pattern**: Application checks cache first, loads from storage on miss, then populates cache.

```
Request → Check L1 → Hit? → Return
              ↓ Miss
         Check L2 → Hit? → Promote to L1 → Return
              ↓ Miss
         Load from Storage → Populate L2 & L1 → Return
```

**Characteristics:**
- Application controls cache logic
- Cache failures don't break the system
- Stale data possible (no automatic invalidation)
- Most common pattern for application caches

**Use Cases:**
- Database query results
- API responses
- Computed values
- Session data

**Example:**
```python
def get_user(user_id):
    # Try L1 (in-memory)
    user = l1_cache.get(user_id)
    if user:
        return user
    
    # Try L2 (Redis)
    user = l2_cache.get(user_id)
    if user:
        l1_cache.set(user_id, user)  # Promote
        return user
    
    # Load from database
    user = database.get_user(user_id)
    l2_cache.set(user_id, user)
    l1_cache.set(user_id, user)
    return user
```

#### 2. Read-Through Cache

**Pattern**: Cache sits between application and storage, automatically loading on miss.

```
Request → Cache → Hit? → Return
              ↓ Miss
         Cache loads from Storage → Return
```

**Characteristics:**
- Cache handles loading logic
- Transparent to application
- Simpler application code
- Cache becomes critical dependency

**Use Cases:**
- ORM caching layers
- Proxy caches
- CDN edge caches
- Database query caches

**Example:**
```python
class ReadThroughCache:
    def get(self, key):
        value = self.cache.get(key)
        if value is None:
            value = self.storage.load(key)
            self.cache.set(key, value)
        return value
```

#### 3. Write-Through Cache

**Pattern**: Writes go to cache and storage synchronously, ensuring consistency.

```
Write → Cache → Storage → Confirm
```

**Characteristics:**
- Strong consistency (cache always matches storage)
- Higher write latency (synchronous)
- No data loss on cache failure
- Simpler consistency model

**Use Cases:**
- Financial transactions
- Critical data updates
- Systems requiring strong consistency
- Audit trails

**Example:**
```python
def update_user(user_id, data):
    # Write to storage first
    database.update_user(user_id, data)
    
    # Then update cache
    l1_cache.set(user_id, data)
    l2_cache.set(user_id, data)
    
    return data
```

#### 4. Write-Back (Write-Behind) Cache

**Pattern**: Writes go to cache immediately, asynchronously written to storage later.

```
Write → Cache → Confirm
         ↓ (async)
      Storage
```

**Characteristics:**
- Low write latency (asynchronous)
- Risk of data loss (if cache fails before write-back)
- Complex consistency management
- Higher throughput

**Use Cases:**
- High-write workloads
- Logging systems
- Analytics pipelines
- Non-critical data

**Example:**
```python
class WriteBackCache:
    def set(self, key, value):
        # Write to cache immediately
        self.cache.set(key, value)
        
        # Queue for async write-back
        self.write_queue.add((key, value))
        
        return True  # Return immediately
    
    def flush(self):
        # Background thread writes to storage
        while not self.write_queue.empty():
            key, value = self.write_queue.get()
            self.storage.write(key, value)
```

#### 5. Write-Around Cache

**Pattern**: Writes bypass cache, go directly to storage.

```
Write → Storage → Confirm
Read → Cache → Miss → Load from Storage → Cache
```

**Characteristics:**
- Avoids cache pollution from write-heavy data
- Read-after-write may miss cache
- Good for write-once, read-rarely data
- Simpler write path

**Use Cases:**
- Log files
- Backup data
- Archive systems
- Bulk imports

### Cache Eviction Policies

When cache is full, eviction policy determines what to remove:

#### LRU (Least Recently Used)
- **Strategy**: Evict least recently accessed item
- **Best For**: Temporal locality (recent data accessed again)
- **Implementation**: Doubly-linked list + hash map
- **Complexity**: O(1) access, O(1) eviction
- **Use Case**: General-purpose caching

#### LFU (Least Frequently Used)
- **Strategy**: Evict least frequently accessed item
- **Best For**: Popular items that should stay cached
- **Implementation**: Min-heap + hash map
- **Complexity**: O(1) access, O(log n) eviction
- **Use Case**: Content delivery, popular items

#### FIFO (First In, First Out)
- **Strategy**: Evict oldest item
- **Best For**: Simple, predictable behavior
- **Implementation**: Queue
- **Complexity**: O(1) access, O(1) eviction
- **Use Case**: Simple caches, circular buffers

#### TTL (Time To Live)
- **Strategy**: Evict expired items
- **Best For**: Time-sensitive data
- **Implementation**: Timestamp + periodic cleanup
- **Complexity**: O(1) access, O(n) cleanup
- **Use Case**: Session data, temporary results

#### ARC (Adaptive Replacement Cache)
- **Strategy**: Balances recency and frequency adaptively
- **Best For**: Mixed workloads
- **Implementation**: Two LRU lists (recent + frequent)
- **Complexity**: O(1) access, O(1) eviction
- **Use Case**: Database caches, file systems

### Cache Coherence and Consistency

**Problem**: Multiple cache levels can have different versions of the same data.

**Solutions:**

#### 1. Cache Invalidation
```python
def update_data(key, value):
    # Update storage
    storage.write(key, value)
    
    # Invalidate all cache levels
    l1_cache.delete(key)
    l2_cache.delete(key)
    l3_cache.delete(key)
```

#### 2. Cache Versioning
```python
def get_data(key, version):
    cached = cache.get(f"{key}:{version}")
    if cached:
        return cached
    
    data = storage.read(key)
    cache.set(f"{key}:{version}", data)
    return data
```

#### 3. Event-Driven Invalidation
```python
# Publisher
def update_data(key, value):
    storage.write(key, value)
    event_bus.publish("data.updated", key)

# Subscriber
def on_data_updated(key):
    l1_cache.delete(key)
    l2_cache.delete(key)
```

### Performance Characteristics

**Latency by Cache Level:**

```
L1 (In-Memory):     0.1-1ms    (CPU cache: nanoseconds)
L2 (Redis/Memcached): 1-10ms   (Network + memory)
L3 (Disk/SSD):      10-100ms   (Disk I/O)
Storage (Database): 100-1000ms (Query + I/O)
```

**Hit Rate Impact:**

```
Overall Latency = (L1_hit_rate × L1_latency) +
                  (L2_hit_rate × L2_latency) +
                  (L3_hit_rate × L3_latency) +
                  (miss_rate × storage_latency)

Example:
L1: 20% × 1ms    = 0.2ms
L2: 10% × 10ms   = 1.0ms
L3: 5% × 100ms   = 5.0ms
Miss: 65% × 500ms = 325ms
─────────────────────────
Total: 331.2ms average

With better hit rates:
L1: 40% × 1ms    = 0.4ms
L2: 30% × 10ms   = 3.0ms
L3: 20% × 100ms  = 20.0ms
Miss: 10% × 500ms = 50ms
─────────────────────────
Total: 73.4ms average (4.5× faster!)
```

### Distributed Caching Considerations

**Challenges:**
1. **Cache Coherence**: Keeping multiple cache nodes consistent
2. **Network Latency**: Remote cache slower than local
3. **Partitioning**: Distributing data across nodes
4. **Replication**: Balancing availability vs consistency
5. **Failure Handling**: Graceful degradation on node failure

**Patterns:**

#### Consistent Hashing
```python
def get_cache_node(key):
    hash_value = hash(key)
    node_index = hash_value % num_nodes
    return cache_nodes[node_index]
```

#### Replication
```python
def set_with_replication(key, value):
    primary = get_primary_node(key)
    replicas = get_replica_nodes(key)
    
    # Write to primary
    primary.set(key, value)
    
    # Async replicate
    for replica in replicas:
        replica.set_async(key, value)
```

## Examples

### Example 1: Web Application Cache Hierarchy

```python
class WebAppCache:
    def __init__(self):
        self.l1 = InMemoryCache(max_size=1000)      # 1ms
        self.l2 = RedisCache(host="redis")          # 10ms
        self.l3 = DatabaseCache(connection=db)      # 100ms
    
    def get_user_profile(self, user_id):
        # L1: In-process memory
        profile = self.l1.get(f"user:{user_id}")
        if profile:
            return profile
        
        # L2: Shared Redis
        profile = self.l2.get(f"user:{user_id}")
        if profile:
            self.l1.set(f"user:{user_id}", profile)
            return profile
        
        # L3: Database with query cache
        profile = self.l3.query(
            "SELECT * FROM users WHERE id = ?", 
            user_id
        )
        
        # Populate caches
        self.l2.set(f"user:{user_id}", profile, ttl=3600)
        self.l1.set(f"user:{user_id}", profile)
        
        return profile
```

### Example 2: CDN Cache Hierarchy

```
User Request
    ↓
Browser Cache (L1)      - 0ms (instant)
    ↓ miss
Edge CDN (L2)           - 10-50ms (geographic proximity)
    ↓ miss
Regional CDN (L3)       - 50-100ms (regional data center)
    ↓ miss
Origin Server (Storage) - 100-500ms (full request)
```

### Example 3: CPU-Style Cache Hierarchy

```python
class CPUStyleCache:
    """Mimics CPU cache hierarchy for application data."""
    
    def __init__(self):
        # L1: Tiny, ultra-fast (like CPU L1)
        self.l1 = LRUCache(max_size=100)
        
        # L2: Medium, fast (like CPU L2)
        self.l2 = LRUCache(max_size=1000)
        
        # L3: Large, moderate (like CPU L3)
        self.l3 = LRUCache(max_size=10000)
    
    def get(self, key):
        # Try L1 (fastest)
        value = self.l1.get(key)
        if value is not None:
            return value
        
        # Try L2
        value = self.l2.get(key)
        if value is not None:
            self.l1.set(key, value)  # Promote to L1
            return value
        
        # Try L3
        value = self.l3.get(key)
        if value is not None:
            self.l2.set(key, value)  # Promote to L2
            self.l1.set(key, value)  # Promote to L1
            return value
        
        # Cache miss - load from storage
        value = self.load_from_storage(key)
        
        # Populate all levels
        self.l3.set(key, value)
        self.l2.set(key, value)
        self.l1.set(key, value)
        
        return value
```

### Example 4: Token Optimization Multi-Level Cache

```python
class TokenOptimizerCache:
    """Real-world example from this project."""
    
    def __init__(self):
        # L1: Exact match (SHA-256 hash)
        self.l1 = ExactCache(max_size=1000)
        
        # L2: Semantic similarity (TF-IDF + cosine)
        self.l2 = SemanticCache(max_size=500, threshold=0.85)
    
    def get_optimized_prompt(self, prompt):
        # L1: Exact match (<1ms)
        result = self.l1.get(prompt)
        if result:
            return result
        
        # L2: Semantic match (<100ms)
        result = self.l2.get(prompt)
        if result:
            # Promote to L1 for future exact matches
            self.l1.set(prompt, result)
            return result
        
        # Cache miss - optimize prompt
        result = self.optimizer.optimize(prompt)
        
        # Store in both levels
        self.l2.set(prompt, result)
        self.l1.set(prompt, result)
        
        return result
```

## Related Documents
- [Multi-Level Caching](./multi-level-caching.md) - This project's specific implementation
- [Token Optimization](./token-optimization.md) - Use case for multi-level caching
- [Cache API Reference](../references/cache-api.md) - Implementation details
- [KB-TOS Shared Embedding Layer](./kb-tos-embedding-layer.md) - Proposed L3 persistent cache

## References
- [ADR-002: Hash-Based Caching Strategy](../../adr/002-caching-strategy.md) - L1 cache design
- [ADR-006: In-Memory Cache vs Distributed Cache](../../adr/006-cache-strategy.md) - Migration strategy
- [System Architecture](../../architecture/ARCHITECTURE.md) - Overall system design
- [Wikipedia: Cache (computing)](https://en.wikipedia.org/wiki/Cache_(computing))
- [Martin Fowler: Cache-Aside Pattern](https://martinfowler.com/bliki/TwoHardThings.html)
- [AWS: Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---
*Last Updated: 2026-07-16*
*Category: Concept*
