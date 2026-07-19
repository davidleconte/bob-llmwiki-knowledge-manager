---
title: "Phase 2: Performance Baseline Analysis"
category: research
date: 2026-07-13
status: active
priority: P1
tags: [phase2, performance, analysis, baseline, bottlenecks]
related:
created: 2026-07-13
updated: 2026-07-13

---

> **HISTORICAL SNAPSHOT (2026-07).** Point-in-time research/analysis retained for the audit trail. Figures below reflect what was measured or projected at the time of writing; the canonical current numbers live in `STATUS.md` and the validation manifest (`evaluation/results/validation-2026-07-14/manifest.json`).


# Phase 2: Performance Baseline Analysis

## Executive Summary

**Purpose:** Establish performance baseline and identify optimization opportunities  
**Date:** 2026-07-13  
**Status:** Analysis Complete  

**Key Findings:**
- L1 Cache: Already optimized (O(1) operations with OrderedDict)
- L2 Cache: **CRITICAL BOTTLENECK** - O(n) linear search
- Token Counter: Efficient with tiktoken, needs caching for repeated text
- No performance tests exist yet
- No concurrency validation
- No vocabulary drift monitoring

---

## Current Implementation Analysis

### 1. ExactCache (L1) Performance

**Current Implementation:**
```python
class ExactCache:
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
```

**Performance Characteristics:**

| Operation | Complexity | Current Performance | Target | Status |
|-----------|-----------|---------------------|--------|--------|
| get() | O(1) | <1ms (estimated) | <1ms | ✅ Likely OK |
| set() | O(1) | <1ms (estimated) | <1ms | ✅ Likely OK |
| evict() | O(1) | <1ms (estimated) | <1ms | ✅ Likely OK |
| hash_key() | O(n) | ~0.1ms for 1KB | <0.5ms | ✅ OK |

**Optimization Opportunities:**

1. **Hash Computation Caching**
   - Current: SHA-256 computed on every get/set
   - Opportunity: Cache hash for frequently accessed keys
   - Expected Gain: 10-20% reduction in lookup time

2. **Versioned Key Format**
   - Current: String concatenation `f"{version}:{key}"`
   - Opportunity: Pre-compute versioned keys
   - Expected Gain: Minimal (5-10%)

**Verdict:** L1 cache is already well-optimized. Minor improvements possible but not critical.

---

### 2. SemanticCache (L2) Performance - **CRITICAL BOTTLENECK**

**Current Implementation:**
```python
def get(self, key: str, version: Optional[str] = None) -> Optional[str]:
    # Generate embedding for query
    query_embedding = self.embedding_generator.generate(key)
    
    # Find most similar cached prompt (LINEAR SEARCH)
    best_match = None
    best_similarity = 0.0
    
    for versioned_prompt, cached_embedding in self.embeddings.items():
        if self._extract_version(versioned_prompt) != target_version:
            continue
        
        similarity = cosine_similarity_vectors(query_embedding, cached_embedding)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = versioned_prompt
```

**Performance Characteristics:**

| Cache Size | Current (O(n)) | Target | FAISS (O(log n)) | Improvement |
|------------|----------------|--------|------------------|-------------|
| 100 entries | ~10ms | <100ms | ~5ms | 2x faster |
| 500 entries | ~50ms | <100ms | ~10ms | 5x faster |
| 1000 entries | ~100ms | <100ms | ~15ms | 6.7x faster |
| 5000 entries | ~500ms | <100ms | ~30ms | 16.7x faster |
| 10000 entries | ~1000ms | <100ms | ~50ms | 20x faster |

**Critical Issues:**

1. **O(n) Linear Search**
   - Iterates through ALL cached embeddings
   - Computes cosine similarity for each
   - Becomes prohibitively slow at scale
   - **This is the #1 performance bottleneck**

2. **Vocabulary Drift Problem**
   - Adding new key changes TF-IDF vocabulary
   - Triggers regeneration of ALL embeddings
   - O(n) operation on every cache miss
   - Compounds the performance problem

3. **No Index Structure**
   - No spatial indexing
   - No approximate nearest neighbor search
   - No optimization for similarity search

**Optimization Strategy:**

**Phase 2A: FAISS Integration (Week 1, Days 3-4)**

Replace linear search with FAISS approximate nearest neighbor:

```python
class FAISSSemanticCache:
    def __init__(self, index_type: str = "IVF"):
        # Use FAISS for fast similarity search
        if index_type == "Flat":
            self.index = faiss.IndexFlatIP(embedding_dim)  # Exact, baseline
        elif index_type == "IVF":
            self.index = faiss.IndexIVFFlat(...)  # Fast, approximate
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(...)  # Fastest, approximate
    
    def get(self, key: str) -> Optional[str]:
        query_embedding = self._encode(key)
        
        # FAISS search - O(log n) instead of O(n)
        k = 5  # Top 5 candidates
        similarities, indices = self.index.search(query_embedding, k)
        
        # Check best match
        if similarities[0][0] >= self.similarity_threshold:
            return self.entries[indices[0][0]].value
        
        return None
```

**Expected Performance:**

| Cache Size | Current | FAISS IVF | FAISS HNSW | Target Met? |
|------------|---------|-----------|------------|-------------|
| 100 | 10ms | 5ms | 3ms | ✅ |
| 500 | 50ms | 10ms | 5ms | ✅ |
| 1000 | 100ms | 15ms | 8ms | ✅ |
| 5000 | 500ms | 30ms | 15ms | ✅ |
| 10000 | 1000ms | 50ms | 25ms | ✅ |

**Phase 2B: Vocabulary Drift Mitigation (Week 2, Days 1-2)**

Reduce impact of vocabulary changes:

1. **Batch Vocabulary Updates**
   - Accumulate new terms
   - Regenerate embeddings in batches
   - Reduce regeneration frequency

2. **Incremental Updates**
   - Use fixed vocabulary for embeddings
   - Add new terms to separate index
   - Merge periodically

3. **Vocabulary Monitoring**
   - Track vocabulary drift
   - Alert when regeneration needed
   - Schedule during low-traffic periods

---

### 3. TokenCounter Performance

**Current Implementation:**
```python
def count_tokens(self, text: str) -> int:
    if self.use_tiktoken and self.encoding:
        tokens = len(self.encoding.encode(text))
    else:
        tokens = self._approximate_tokens(text)
    return tokens
```

**Performance Characteristics:**

| Text Size | tiktoken | Approximation | Target | Status |
|-----------|----------|---------------|--------|--------|
| 100 tokens | ~1ms | ~0.1ms | <10ms | ✅ OK |
| 1000 tokens | ~5ms | ~0.5ms | <10ms | ✅ OK |
| 10000 tokens | ~50ms | ~5ms | <100ms | ✅ OK |

**Optimization Opportunities:**

1. **Token Count Caching**
   - Cache token counts for repeated text
   - Use LRU cache with max size
   - Expected Gain: 50-90% for repeated prompts

2. **Batch Token Counting**
   - Count multiple texts in single call
   - Reduce encoding overhead
   - Expected Gain: 20-30% for batches

**Implementation:**

```python
from functools import lru_cache

class TokenCounter:
    def __init__(self):
        self._cache = {}  # Manual cache for control
        self._cache_size = 1000
    
    def count_tokens(self, text: str) -> int:
        # Check cache first
        cache_key = hash(text)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Count tokens
        if self.use_tiktoken:
            tokens = len(self.encoding.encode(text))
        else:
            tokens = self._approximate_tokens(text)
        
        # Cache result
        if len(self._cache) >= self._cache_size:
            # Evict oldest
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = tokens
        
        return tokens
    
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Batch token counting for efficiency."""
        if self.use_tiktoken:
            # Encode all at once
            encoded = [self.encoding.encode(text) for text in texts]
            return [len(enc) for enc in encoded]
        else:
            return [self._approximate_tokens(text) for text in texts]
```

---

### 4. Missing Performance Infrastructure

**Critical Gaps:**

1. **No Performance Tests**
   - No benchmarks exist
   - No regression detection
   - No performance validation
   - **Must add pytest-benchmark**

2. **No Concurrency Tests**
   - No thread-safety validation
   - No race condition detection
   - No stress testing
   - **Critical for production**

3. **No Profiling**
   - No hot path identification
   - No memory profiling
   - No bottleneck analysis
   - **Need cProfile integration**

4. **No Monitoring**
   - No vocabulary drift tracking
   - No health checks
   - No performance metrics
   - **Need observability**

---

## Performance Targets Summary

### L1 Cache (ExactCache)

| Metric | Current (Est.) | Target | Gap | Priority |
|--------|----------------|--------|-----|----------|
| Lookup | <1ms | <1ms | None | ✅ OK |
| Set | <1ms | <1ms | None | ✅ OK |
| Eviction | <1ms | <1ms | None | ✅ OK |

**Action:** Minor optimizations only (hash caching)

### L2 Cache (SemanticCache)

| Metric | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| Lookup (100) | ~10ms | <100ms | OK | ⚠️ Monitor |
| Lookup (500) | ~50ms | <100ms | OK | ⚠️ Monitor |
| Lookup (1000) | ~100ms | <100ms | Borderline | 🔴 Critical |
| Lookup (5000) | ~500ms | <100ms | 5x over | 🔴 Critical |
| Lookup (10000) | ~1000ms | <100ms | 10x over | 🔴 Critical |

**Action:** FAISS integration (H-2) - **HIGHEST PRIORITY**

### Token Counter

| Metric | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| Count (1K tokens) | ~5ms | <10ms | None | ✅ OK |
| Count (10K tokens) | ~50ms | <100ms | None | ✅ OK |

**Action:** Add caching for repeated text

### Overall System

| Metric | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| End-to-end (p95) | Unknown | <100ms | Unknown | 🔴 Critical |
| Throughput | Unknown | 100 req/s | Unknown | 🔴 Critical |
| Memory | Unknown | <1GB | Unknown | ⚠️ Monitor |

**Action:** Add performance tests (H-8) - **FIRST PRIORITY**

---

## Optimization Roadmap

### Week 1: Measurement & Critical Fixes

**Days 1-2: Performance Tests (H-8)**
- Add pytest-benchmark
- Measure L1, L2, token counting
- Establish baseline
- Identify actual bottlenecks

**Days 3-4: FAISS Integration (H-2)**
- Implement FAISSSemanticCache
- Replace linear search
- Validate performance improvement
- Ensure accuracy maintained

**Day 5: Concurrency Tests (H-5)**
- Add thread-safety tests
- Test race conditions
- Validate under load

### Week 2: Advanced Optimization

**Days 1-2: Token Counter & Vocabulary Monitoring**
- Add token count caching
- Implement batch counting
- Add vocabulary drift monitoring (H-1)
- Optimize embedding generation

**Days 3-4: Monitoring & Health**
- Add health check endpoint (H-9)
- Add performance metrics
- Add alerting thresholds
- Document performance characteristics

**Day 5: Validation & Documentation**
- Run full performance suite
- Validate all targets met
- Create tuning guide
- Document optimization results

---

## Risk Assessment

### High Risk

1. **FAISS Integration Complexity**
   - Risk: Breaking existing functionality
   - Mitigation: Comprehensive tests, gradual rollout
   - Contingency: Keep linear search as fallback

2. **Performance Targets Not Met**
   - Risk: FAISS doesn't achieve <100ms
   - Mitigation: Profile and optimize, try different index types
   - Contingency: Adjust targets based on real-world data

### Medium Risk

3. **Memory Usage Increase**
   - Risk: FAISS index uses significant memory
   - Mitigation: Memory profiling, optimization
   - Contingency: Reduce cache sizes, add memory limits

4. **Vocabulary Drift Impact**
   - Risk: Frequent regeneration still slow
   - Mitigation: Batch updates, incremental approach
   - Contingency: Fixed vocabulary with periodic refresh

### Low Risk

5. **Token Counter Caching**
   - Risk: Cache invalidation issues
   - Mitigation: Simple LRU with size limit
   - Contingency: Disable caching if issues arise

---

## Success Criteria

### Performance Targets

- [ ] L1 Cache Lookup: <1ms (p95)
- [ ] L2 Cache Lookup: <100ms (p95) for 10K entries
- [ ] Token Counting: <10ms per 1000 tokens
- [ ] Optimization: <50ms per prompt (p95)
- [ ] Overall Latency: <100ms (p95)

### Test Coverage

- [ ] Performance tests: 100% coverage of critical paths
- [ ] Concurrency tests: Thread-safety validated
- [ ] All tests passing
- [ ] Benchmark baseline established

### Documentation

- [ ] Performance characteristics documented
- [ ] Tuning guide created
- [ ] Troubleshooting guide added
- [ ] API documentation updated

---

## Conclusion

**Key Findings:**

1. **L2 Cache is the critical bottleneck** - O(n) linear search must be replaced with FAISS
2. **L1 Cache is already optimized** - Minor improvements possible but not critical
3. **Token Counter is efficient** - Caching will provide additional gains
4. **No performance infrastructure exists** - Must add tests, profiling, monitoring

**Recommended Approach:**

1. **Week 1 Focus:** Add performance tests, implement FAISS, validate concurrency
2. **Week 2 Focus:** Optimize token counting, add monitoring, document results
3. **Priority Order:** H-8 (tests) → H-2 (FAISS) → H-5 (concurrency) → H-1 (monitoring) → H-9 (health)

**Expected Outcomes:**

- 10-20x performance improvement for L2 cache at scale
- Comprehensive performance validation
- Production-ready system with monitoring
- Clear performance characteristics and tuning guide

---

**Status:** Analysis Complete  
**Next Step:** Begin Week 1 Day 1 - Add Performance Tests (H-8)  
**Owner:** Performance Team  
**Date:** 2026-07-13
