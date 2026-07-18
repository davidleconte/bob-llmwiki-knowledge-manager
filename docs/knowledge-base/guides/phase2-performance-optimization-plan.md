---
title: "Phase 2: Performance Optimization - Implementation Plan"
category: guide
date: 2026-07-13
status: active
priority: P1
tags: [phase2, performance, optimization, benchmarks, profiling]
related:
  - ./kb-tos-integration-roadmap.md
  - ../research/full-technical-design-retro-2026-07.md
created: 2026-07-13
updated: 2026-07-13

---

# Phase 2: Performance Optimization - Implementation Plan

## Executive Summary

**Purpose:** Optimize system performance to meet latency and throughput targets  
**Timeline:** 2 weeks (Week 3-4 of remediation plan)  
**Approach:** Measure → Optimize → Validate  
**Success Criteria:** L1 <1ms, L2 <100ms, Optimization <50ms (p95)

---

## Phase 2 Scope

Based on the remediation plan, Phase 2 addresses 5 high-priority issues:

### H-1: Vocabulary Drift (1-2 weeks)
**Problem:** Semantic cache degrades over time as vocabulary evolves  
**Impact:** Cache hit rate drops, performance degrades  
**Solution:** Implement vocabulary monitoring and cache refresh

### H-2: O(n) L2 Lookup (1-2 weeks)
**Problem:** Linear search through L2 cache is slow  
**Impact:** L2 lookup can exceed 100ms target  
**Solution:** Implement FAISS for approximate nearest neighbor search

### H-5: Concurrency Tests (1 week)
**Problem:** No tests for concurrent access  
**Impact:** Race conditions, data corruption possible  
**Solution:** Add comprehensive concurrency tests

### H-8: Performance Tests (1 week)
**Problem:** No performance benchmarks or regression tests  
**Impact:** Performance degradation undetected  
**Solution:** Add pytest-benchmark performance tests

### H-9: Health Checks (2-3 days)
**Problem:** No health check endpoint  
**Impact:** Cannot monitor system health  
**Solution:** Add health check with component status

---

## Implementation Strategy

### Week 1: Measurement & Hot Path Optimization

**Days 1-2: Performance Baseline**
- Add pytest-benchmark for performance tests
- Measure current performance (L1, L2, optimization)
- Profile hot paths with cProfile
- Identify bottlenecks

**Days 3-4: Cache Optimization**
- Optimize hash computation in ExactCache
- Implement FAISS for L2 cache (H-2)
- Add cache warming strategies
- Optimize eviction logic

**Day 5: Concurrency Testing**
- Add thread-safety tests (H-5)
- Test race conditions
- Validate lock mechanisms
- Stress test with high concurrency

### Week 2: Advanced Optimization & Validation

**Days 1-2: Token Counting Optimization**
- Cache token counts for repeated text
- Batch token counting
- Optimize encoding lookup
- Profile and optimize

**Days 3-4: Monitoring & Health Checks**
- Implement vocabulary drift monitoring (H-1)
- Add health check endpoint (H-9)
- Add performance metrics
- Add alerting thresholds

**Day 5: Validation & Documentation**
- Run full performance test suite
- Validate all targets met
- Document performance characteristics
- Create tuning guide

---

## Detailed Implementation

### H-8: Performance Tests (Priority 1)

**Why First:** Need baseline before optimization

#### Design Phase

**Performance Targets:**
- L1 Cache Lookup: <1ms (p95)
- L2 Cache Lookup: <100ms (p95)
- Token Counting: <10ms per 1000 tokens
- Optimization: <50ms per prompt (p95)
- Overall Latency: <100ms (p95)

**Test Structure:**

```python
# tests/performance/test_cache_performance.py

import pytest
from src.cache import ExactCache, SemanticCache, MultiLevelCache

@pytest.mark.benchmark(group="cache")
class TestCachePerformance:
    """Performance benchmarks for cache operations."""
    
    def test_l1_lookup_performance(self, benchmark):
        """Benchmark L1 cache lookup."""
        cache = ExactCache(max_size=1000)
        
        # Populate cache
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Benchmark lookup
        result = benchmark(cache.get, "key_50")
        
        assert result == "value_50"
        
        # Verify performance
        stats = benchmark.stats
        assert stats['mean'] < 0.001  # <1ms mean
        assert stats['stddev'] < 0.0005  # Low variance
    
    def test_l1_set_performance(self, benchmark):
        """Benchmark L1 cache set."""
        cache = ExactCache(max_size=1000)
        
        def set_operation():
            cache.set("test_key", "test_value")
        
        benchmark(set_operation)
        
        stats = benchmark.stats
        assert stats['mean'] < 0.001  # <1ms mean
    
    def test_l2_lookup_performance(self, benchmark):
        """Benchmark L2 cache lookup."""
        cache = SemanticCache(max_size=500)
        
        # Populate cache
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")
        
        # Benchmark lookup
        result = benchmark(cache.get, "prompt_25")
        
        # Verify performance
        stats = benchmark.stats
        assert stats['mean'] < 0.100  # <100ms mean
    
    def test_multilevel_cache_performance(self, benchmark):
        """Benchmark multi-level cache."""
        cache = MultiLevelCache(
            l1_max_size=1000,
            l2_max_size=500
        )
        
        # Populate
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Benchmark (should hit L1)
        result = benchmark(cache.get, "key_50")
        
        assert result == "value_50"
        
        stats = benchmark.stats
        assert stats['mean'] < 0.001  # L1 hit should be <1ms
    
    def test_cache_eviction_performance(self, benchmark):
        """Benchmark cache eviction."""
        cache = ExactCache(max_size=100)
        
        # Fill cache
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Benchmark eviction (add one more)
        def trigger_eviction():
            cache.set("new_key", "new_value")
        
        benchmark(trigger_eviction)
        
        stats = benchmark.stats
        assert stats['mean'] < 0.002  # Eviction should be fast
```

**Token Counter Performance:**

```python
# tests/performance/test_optimizer_performance.py

import pytest
from src.optimizer import TokenCounter, PromptOptimizer

@pytest.mark.benchmark(group="optimizer")
class TestOptimizerPerformance:
    """Performance benchmarks for optimizer."""
    
    def test_token_counting_performance(self, benchmark):
        """Benchmark token counting."""
        counter = TokenCounter()
        text = "This is a test prompt " * 50  # ~1000 tokens
        
        result = benchmark(counter.count_tokens, text)
        
        assert result > 0
        
        stats = benchmark.stats
        assert stats['mean'] < 0.010  # <10ms for 1000 tokens
    
    def test_batch_token_counting_performance(self, benchmark):
        """Benchmark batch token counting."""
        counter = TokenCounter()
        texts = [f"Test prompt {i}" for i in range(100)]
        
        result = benchmark(counter.count_tokens_batch, texts)
        
        assert len(result) == 100
        
        stats = benchmark.stats
        assert stats['mean'] < 0.100  # <100ms for 100 prompts
    
    def test_optimization_performance(self, benchmark):
        """Benchmark prompt optimization."""
        optimizer = PromptOptimizer(
            max_tokens=4096,
            target_reduction=0.3
        )
        
        prompt = "This is a test prompt with some repeated repeated words. " * 10
        
        result = benchmark(optimizer.optimize, prompt)
        
        assert result['optimized_tokens'] < result['original_tokens']
        
        stats = benchmark.stats
        assert stats['mean'] < 0.050  # <50ms per optimization
```

**Running Benchmarks:**

```bash
# Run all performance tests
pytest tests/performance/ -v --benchmark-only

# Run specific group
pytest tests/performance/ -v --benchmark-only --benchmark-group=cache

# Generate HTML report
pytest tests/performance/ --benchmark-only --benchmark-autosave \
  --benchmark-save-data --benchmark-histogram

# Compare with baseline
pytest tests/performance/ --benchmark-only \
  --benchmark-compare=0001 --benchmark-compare-fail=mean:10%
```

#### Validation Phase

**Acceptance Criteria:**
- [ ] All performance tests pass
- [ ] L1 lookup <1ms (p95)
- [ ] L2 lookup <100ms (p95)
- [ ] Token counting <10ms per 1000 tokens
- [ ] Optimization <50ms (p95)
- [ ] Benchmark reports generated
- [ ] Baseline established for regression testing

---

### H-2: O(n) L2 Lookup Optimization (Priority 2)

**Why Second:** Biggest performance bottleneck

#### Design Phase

**Problem Analysis:**
- Current: Linear search through all L2 entries
- Complexity: O(n) where n = cache size
- Impact: 100ms+ for large caches (500+ entries)

**Solution: FAISS Integration**

```
┌─────────────────────────────────────────┐
│         FAISS-Optimized L2 Cache        │
├─────────────────────────────────────────┤
│                                         │
│  1. Encode prompt → embedding           │
│  2. FAISS search → k nearest neighbors  │
│  3. Check similarity threshold          │
│  4. Return best match if above threshold│
│                                         │
│  Complexity: O(log n) with FAISS index  │
│  Target: <100ms for 10,000 entries      │
│                                         │
└─────────────────────────────────────────┘
```

**Implementation:**

```python
# src/cache/semantic_cache_faiss.py

import faiss
import numpy as np
from typing import Optional, List, Tuple
from sentence_transformers import SentenceTransformer

from src.cache.base import CacheInterface, CacheEntry

class FAISSSemanticCache(CacheInterface):
    """Semantic cache with FAISS for fast similarity search."""
    
    def __init__(
        self,
        max_size: int = 500,
        similarity_threshold: float = 0.85,
        model_name: str = "all-MiniLM-L6-v2",
        index_type: str = "IVF"
    ):
        """Initialize FAISS semantic cache.
        
        Args:
            max_size: Maximum cache entries
            similarity_threshold: Minimum similarity for hit
            model_name: Sentence transformer model
            index_type: FAISS index type (Flat, IVF, HNSW)
        """
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        
        # Initialize sentence transformer
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = self._create_index(index_type)
        
        # Store cache entries
        self.entries: List[CacheEntry] = []
        self.keys: List[str] = []
    
    def _create_index(self, index_type: str) -> faiss.Index:
        """Create FAISS index.
        
        Args:
            index_type: Index type (Flat, IVF, HNSW)
            
        Returns:
            FAISS index
        """
        if index_type == "Flat":
            # Exact search (baseline)
            return faiss.IndexFlatIP(self.embedding_dim)
        
        elif index_type == "IVF":
            # Inverted file index (faster, approximate)
            nlist = 100  # Number of clusters
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            index = faiss.IndexIVFFlat(
                quantizer,
                self.embedding_dim,
                nlist,
                faiss.METRIC_INNER_PRODUCT
            )
            return index
        
        elif index_type == "HNSW":
            # Hierarchical NSW (fastest, approximate)
            index = faiss.IndexHNSWFlat(
                self.embedding_dim,
                32,  # M parameter
                faiss.METRIC_INNER_PRODUCT
            )
            return index
        
        else:
            raise ValueError(f"Unknown index type: {index_type}")
    
    def _encode(self, text: str) -> np.ndarray:
        """Encode text to embedding.
        
        Args:
            text: Text to encode
            
        Returns:
            Normalized embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Normalize for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.astype('float32')
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache using similarity search.
        
        Args:
            key: Cache key (prompt)
            
        Returns:
            Cached value if similarity above threshold, else None
        """
        if len(self.entries) == 0:
            return None
        
        # Encode query
        query_embedding = self._encode(key)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search FAISS index
        k = min(5, len(self.entries))  # Top 5 candidates
        similarities, indices = self.index.search(query_embedding, k)
        
        # Check best match
        best_idx = indices[0][0]
        best_similarity = similarities[0][0]
        
        if best_similarity >= self.similarity_threshold:
            entry = self.entries[best_idx]
            
            # Update access time
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            return entry.value
        
        return None
    
    def set(self, key: str, value: str) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key (prompt)
            value: Value to cache
        """
        # Check if key exists
        existing_idx = self._find_exact_match(key)
        if existing_idx is not None:
            # Update existing entry
            self.entries[existing_idx].value = value
            self.entries[existing_idx].last_accessed = time.time()
            return
        
        # Evict if at capacity
        if len(self.entries) >= self.max_size:
            self._evict_lru()
        
        # Encode and add to index
        embedding = self._encode(key)
        embedding = embedding.reshape(1, -1)
        
        # Add to FAISS index
        self.index.add(embedding)
        
        # Add entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            access_count=1,
            last_accessed=time.time()
        )
        self.entries.append(entry)
        self.keys.append(key)
    
    def _find_exact_match(self, key: str) -> Optional[int]:
        """Find exact key match.
        
        Args:
            key: Key to find
            
        Returns:
            Index if found, else None
        """
        try:
            return self.keys.index(key)
        except ValueError:
            return None
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if len(self.entries) == 0:
            return
        
        # Find LRU entry
        lru_idx = min(
            range(len(self.entries)),
            key=lambda i: self.entries[i].last_accessed
        )
        
        # Remove from entries and keys
        del self.entries[lru_idx]
        del self.keys[lru_idx]
        
        # Rebuild FAISS index (expensive but necessary)
        self._rebuild_index()
    
    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from current entries."""
        # Create new index
        index_type = type(self.index).__name__
        self.index = self._create_index(index_type)
        
        # Re-add all embeddings
        if len(self.entries) > 0:
            embeddings = np.array([
                self._encode(key) for key in self.keys
            ])
            self.index.add(embeddings)
    
    def clear(self) -> None:
        """Clear cache."""
        self.entries.clear()
        self.keys.clear()
        
        # Reset index
        index_type = type(self.index).__name__
        self.index = self._create_index(index_type)
```

**Performance Comparison:**

```python
# tests/performance/test_faiss_performance.py

import pytest
from src.cache import SemanticCache, FAISSSemanticCache

@pytest.mark.benchmark(group="l2-optimization")
class TestFAISSPerformance:
    """Compare FAISS vs linear search performance."""
    
    @pytest.fixture
    def populated_caches(self):
        """Create populated caches for testing."""
        linear_cache = SemanticCache(max_size=1000)
        faiss_cache = FAISSSemanticCache(max_size=1000)
        
        # Populate with 500 entries
        for i in range(500):
            prompt = f"Test prompt number {i} with some content"
            result = f"Result {i}"
            linear_cache.set(prompt, result)
            faiss_cache.set(prompt, result)
        
        return linear_cache, faiss_cache
    
    def test_linear_search_performance(self, benchmark, populated_caches):
        """Benchmark linear search."""
        linear_cache, _ = populated_caches
        
        result = benchmark(linear_cache.get, "Test prompt number 250")
        
        assert result is not None
        
        stats = benchmark.stats
        print(f"Linear search: {stats['mean']*1000:.2f}ms")
    
    def test_faiss_search_performance(self, benchmark, populated_caches):
        """Benchmark FAISS search."""
        _, faiss_cache = populated_caches
        
        result = benchmark(faiss_cache.get, "Test prompt number 250")
        
        assert result is not None
        
        stats = benchmark.stats
        print(f"FAISS search: {stats['mean']*1000:.2f}ms")
        assert stats['mean'] < 0.100  # <100ms
    
    def test_scalability(self):
        """Test performance at different cache sizes."""
        sizes = [100, 500, 1000, 5000]
        
        for size in sizes:
            # Create and populate cache
            cache = FAISSSemanticCache(max_size=size)
            for i in range(size):
                cache.set(f"prompt_{i}", f"result_{i}")
            
            # Measure lookup time
            import time
            start = time.time()
            result = cache.get(f"prompt_{size//2}")
            elapsed = time.time() - start
            
            print(f"Size {size}: {elapsed*1000:.2f}ms")
            assert elapsed < 0.100  # Should scale well
```

#### Validation Phase

**Acceptance Criteria:**
- [ ] FAISS integration complete
- [ ] L2 lookup <100ms for 10,000 entries
- [ ] Performance tests pass
- [ ] Accuracy maintained (>85% similarity threshold)
- [ ] Memory usage acceptable
- [ ] Documentation updated

---

### H-5: Concurrency Tests (Priority 3)

**Why Third:** Critical for production reliability

#### Design Phase

**Test Scenarios:**
1. Concurrent reads (multiple threads reading)
2. Concurrent writes (multiple threads writing)
3. Mixed read/write (realistic workload)
4. Race conditions (edge cases)
5. Deadlock detection

**Implementation:**

```python
# tests/concurrency/test_cache_concurrency.py

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.cache import ExactCache, MultiLevelCache

class TestCacheConcurrency:
    """Test cache thread safety."""
    
    def test_concurrent_reads(self):
        """Test multiple threads reading simultaneously."""
        cache = ExactCache(max_size=1000)
        
        # Populate cache
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Concurrent reads
        def read_operation(thread_id):
            results = []
            for i in range(100):
                result = cache.get(f"key_{i}")
                results.append(result)
            return results
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(read_operation, i)
                for i in range(10)
            ]
            
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all reads succeeded
        assert len(results) == 10
        for result_list in results:
            assert len(result_list) == 100
            assert all(r is not None for r in result_list)
    
    def test_concurrent_writes(self):
        """Test multiple threads writing simultaneously."""
        cache = ExactCache(max_size=1000)
        
        def write_operation(thread_id):
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(write_operation, i)
                for i in range(10)
            ]
            
            # Wait for completion
            for f in as_completed(futures):
                f.result()
        
        # Verify all writes succeeded
        stats = cache.get_stats()
        assert stats['size'] == 1000  # 10 threads * 100 writes
    
    def test_mixed_read_write(self):
        """Test mixed read/write workload."""
        cache = ExactCache(max_size=1000)
        
        # Pre-populate
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")
        
        def mixed_operation(thread_id):
            for i in range(50):
                if i % 2 == 0:
                    # Read
                    cache.get(f"key_{i}")
                else:
                    # Write
                    cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(mixed_operation, i)
                for i in range(10)
            ]
            
            for f in as_completed(futures):
                f.result()
        
        # Verify cache is consistent
        stats = cache.get_stats()
        assert stats['size'] > 0
        assert stats['size'] <= 1000
    
    def test_race_condition_detection(self):
        """Test for race conditions in cache operations."""
        cache = ExactCache(max_size=100)
        
        # Shared counter
        counter = {'value': 0}
        lock = threading.Lock()
        
        def increment_operation():
            for _ in range(1000):
                # Read-modify-write without proper locking
                # (intentionally racy to test detection)
                current = counter['value']
                time.sleep(0.0001)  # Increase chance of race
                counter['value'] = current + 1
        
        # Run without lock (should have races)
        counter['value'] = 0
        threads = [
            threading.Thread(target=increment_operation)
            for _ in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify race condition occurred
        assert counter['value'] < 10000  # Should be less due to races
        
        # Now test with proper locking
        def safe_increment_operation():
            for _ in range(1000):
                with lock:
                    current = counter['value']
                    time.sleep(0.0001)
                    counter['value'] = current + 1
        
        counter['value'] = 0
        threads = [
            threading.Thread(target=safe_increment_operation)
            for _ in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no race condition
        assert counter['value'] == 10000
    
    def test_deadlock_detection(self):
        """Test for potential deadlocks."""
        cache1 = ExactCache(max_size=100)
        cache2 = ExactCache(max_size=100)
        
        def operation_a():
            for _ in range(100):
                cache1.set("key_a", "value_a")
                cache2.set("key_b", "value_b")
        
        def operation_b():
            for _ in range(100):
                cache2.set("key_c", "value_c")
                cache1.set("key_d", "value_d")
        
        # Run with timeout to detect deadlock
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(operation_a)
            future_b = executor.submit(operation_b)
            
            try:
                future_a.result(timeout=5.0)
                future_b.result(timeout=5.0)
            except TimeoutError:
                pytest.fail("Deadlock detected")
    
    def test_stress_test(self):
        """Stress test with high concurrency."""
        cache = MultiLevelCache(
            l1_max_size=1000,
            l2_max_size=500
        )
        
        def stress_operation(thread_id):
            for i in range(1000):
                if i % 3 == 0:
                    cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                elif i % 3 == 1:
                    cache.get(f"key_{thread_id}_{i}")
                else:
                    cache.clear()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(stress_operation, i)
                for i in range(20)
            ]
            
            for f in as_completed(futures):
                f.result()
        
        # Verify cache is still functional
        cache.set("test", "value")
        assert cache.get("test") == "value"
```

#### Validation Phase

**Acceptance Criteria:**
- [ ] All concurrency tests pass
- [ ] No race conditions detected
- [ ] No deadlocks detected
- [ ] Stress test passes
- [ ] Thread-safety verified
- [ ] Documentation updated

---

### H-1: Vocabulary Drift Monitoring (Priority 4)

**Why Fourth:** Important for long-term cache effectiveness

#### Design Phase

**Problem:** Semantic cache degrades as vocabulary evolves

**Solution:** Monitor vocabulary drift and trigger cache refresh

```python
# src/monitoring/vocabulary_monitor.py

import numpy as np
from typing import List, Dict, Optional
from collections import deque
from dataclasses import dataclass
import time

@dataclass
class VocabularySnapshot:
    """Snapshot of vocabulary at a point in time."""
    timestamp: float
    embeddings: np.ndarray
    terms: List[str]
    centroid: np.ndarray

class VocabularyMonitor:
    """Monitor vocabulary drift in semantic cache."""
    
    def __init__(
        self,
        window_size: int = 1000,
        drift_threshold: float = 0.15,
        check_interval: int = 100
    ):
        """Initialize vocabulary monitor.
        
        Args:
            window_size: Number of recent terms to track
            drift_threshold: Threshold for drift detection (0-1)
            check_interval: Check drift every N operations
        """
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.check_interval = check_interval
        
        # Track recent terms
        self.recent_terms: deque = deque(maxlen=window_size)
        self.recent_embeddings: deque = deque(maxlen=window_size)
        
        # Baseline snapshot
        self.baseline: Optional[VocabularySnapshot] = None
        
        # Drift history
        self.drift_history: List[float] = []
        
        # Operation counter
        self.operation_count = 0
    
    def add_term(self, term: str, embedding: np.ndarray) -> None:
        """Add term to monitoring.
        
        Args:
            term: Term text
            embedding: Term embedding
        """
        self.recent_terms.append(term)
        self.recent_embeddings.append(embedding)
        self.operation_count += 1
        
        # Check drift periodically
        if self.operation_count % self.check_interval == 0:
            self.check_drift()
    
    def create_baseline(self) -> None:
        """Create baseline vocabulary snapshot."""
        if len(self.recent_embeddings) < 100:
            return  # Need minimum data
        
        embeddings = np.array(list(self.recent_embeddings))
        centroid = np.mean(embeddings, axis=0)
        
        self.baseline = VocabularySnapshot(
            timestamp=time.time(),
            embeddings=embeddings.copy(),
            terms=list(self.recent_terms),
            centroid=centroid
        )
    
    def check_drift(self) -> float:
        """Check vocabulary drift.
        
        Returns:
            Drift score (0-1, higher = more drift)
        """
        if self.baseline is None:
            self.create_baseline()
            return 0.0
        
        if len(self.recent_embeddings) < 100:
            return 0.0
        
        # Calculate current centroid
        current_embeddings = np.array(list(self.recent_embeddings))
        current_centroid = np.mean(current_embeddings, axis=0)
        
        # Calculate drift (cosine distance)
        similarity = np.dot(current_centroid, self.baseline.centroid)
        drift = 1.0 - similarity
        
        self.drift_history.append(drift)
        
        return drift
    
    def needs_refresh(self) -> bool:
        """Check if cache needs refresh due to drift.
        
        Returns:
            True if drift exceeds threshold
        """
        if len(self.drift_history) == 0:
            return False
        
        recent_drift = np.mean(self.drift_history[-10:])
        return recent_drift > self.drift_threshold
    
    def get_drift_report(self) -> Dict[str, any]:
        """Get drift monitoring report.
        
        Returns:
            Report dictionary
        """
        if len(self.drift_history) == 0:
            return {
                'status': 'insufficient_data',
                'drift': 0.0,
                'needs_refresh': False
            }
        
        current_drift = self.drift_history[-1]
        avg_drift = np.mean(self.drift_history)
        max_drift = np.max(self.drift_history)
        
        return {
            'status': 'monitoring',
            'current_drift': current_drift,
            'average_drift': avg_drift,
            'max_drift': max_drift,
            'needs_refresh': self.needs_refresh(),
            'baseline_age': time.time() - self.baseline.timestamp if self.baseline else 0,
            'terms_tracked': len(self.recent_terms),
            'checks_performed': len(self.drift_history)
        }
```

#### Validation Phase

**Acceptance Criteria:**
- [ ] Vocabulary monitoring implemented
- [ ] Drift detection working
- [ ] Refresh triggers correctly
- [ ] Performance impact minimal
- [ ] Tests pass
- [ ] Documentation updated

---

### H-9: Health Checks (Priority 5)

**Why Last:** Quick win, enables monitoring

#### Design Phase

**Health Check Endpoint:**

```python
# src/monitoring/health.py

from typing import Dict, List
from dataclasses import dataclass
import time

@dataclass
class ComponentHealth:
    """Health status of a component."""
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    error_rate: float
    message: str

class HealthChecker:
    """System health checker."""
    
    def __init__(self):
        """Initialize health checker."""
        self.components = {}
        self.last_check = 0
        self.check_interval = 60  # seconds
    
    def register_component(self, name: str, check_fn):
        """Register component for health checking.
        
        Args:
            name: Component name
            check_fn: Function that returns (status, latency, error_rate, message)
        """
        self.components[name] = check_fn
    
    def check_health(self) -> Dict[str, any]:
        """Check system health.
        
        Returns:
            Health report
        """
        now = time.time()
        
        # Check each component
        component_health = []
        overall_status = "healthy"
        
        for name, check_fn in self.components.items():
            try:
                status, latency, error_rate, message = check_fn()
                
                health = ComponentHealth(
                    name=name,
                    status=status,
                    latency_ms=latency,
                    error_rate=error_rate,
                    message=message
                )
                component_health.append(health)
                
                # Update overall status
                if status == "unhealthy":
                    overall_status = "unhealthy"
                elif status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
                    
            except Exception as e:
                health = ComponentHealth(
                    name=name,
                    status="unhealthy",
                    latency_ms=0,
                    error_rate=1.0,
                    message=f"Health check failed: {str(e)}"
                )
                component_health.append(health)
                overall_status = "unhealthy"
        
        self.last_check = now
        
        return {
            'status': overall_status,
            'timestamp': now,
            'components': [
                {
                    'name': h.name,
                    'status': h.status,
                    'latency_ms': h.latency_ms,
                    'error_rate': h.error_rate,
                    'message': h.message
                }
                for h in component_health
            ]
        }
```

#### Validation Phase

**Acceptance Criteria:**
- [ ] Health check endpoint implemented
- [ ] All components registered
- [ ] Status reporting accurate
- [ ] Performance impact minimal
- [ ] Tests pass
- [ ] Documentation updated

---

## Success Criteria

### Performance Targets

- [ ] L1 Cache Lookup: <1ms (p95) ✓
- [ ] L2 Cache Lookup: <100ms (p95) ✓
- [ ] Token Counting: <10ms per 1000 tokens ✓
- [ ] Optimization: <50ms per prompt (p95) ✓
- [ ] Overall Latency: <100ms (p95) ✓

### Test Coverage

- [ ] Performance tests: 100% coverage
- [ ] Concurrency tests: 100% coverage
- [ ] All tests passing
- [ ] Benchmark baseline established

### Documentation

- [ ] Performance characteristics documented
- [ ] Tuning guide created
- [ ] API documentation updated
- [ ] Troubleshooting guide added

---

## Risk Mitigation

### Performance Risks

**Risk:** FAISS integration breaks existing functionality  
**Mitigation:** Comprehensive tests, gradual rollout  
**Contingency:** Keep linear search as fallback

**Risk:** Performance targets not met  
**Mitigation:** Profile and optimize hot paths  
**Contingency:** Adjust targets based on real-world data

**Risk:** Memory usage increases significantly  
**Mitigation:** Memory profiling, optimization  
**Contingency:** Reduce cache sizes, add memory limits

---

## Next Steps

1. **Week 1 Day 1-2:** Add performance tests (H-8)
2. **Week 1 Day 3-4:** Implement FAISS optimization (H-2)
3. **Week 1 Day 5:** Add concurrency tests (H-5)
4. **Week 2 Day 1-2:** Optimize token counting
5. **Week 2 Day 3-4:** Add vocabulary monitoring (H-1) and health checks (H-9)
6. **Week 2 Day 5:** Validation and documentation

---

**Status:** Ready to implement  
**Created:** 2026-07-13  
**Owner:** Performance Team  
**Next Review:** End of Week 1
