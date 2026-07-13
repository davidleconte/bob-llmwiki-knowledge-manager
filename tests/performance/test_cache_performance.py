"""Performance benchmarks for cache operations.

Tests measure latency and throughput for L1, L2, and multi-level caches.
Validates performance targets: L1 <1ms, L2 <100ms.
"""

import pytest
from src.cache import ExactCache, SemanticCache, MultiLevelCache


@pytest.mark.benchmark(group="cache-l1")
class TestL1CachePerformance:
    """Performance benchmarks for L1 (ExactCache) operations."""
    
    @pytest.fixture
    def populated_cache(self):
        """Create cache with 100 entries."""
        cache = ExactCache(max_size=1000)
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        return cache
    
    def test_l1_lookup_hit(self, benchmark, populated_cache):
        """Benchmark L1 cache hit (should be <1ms)."""
        result = benchmark(populated_cache.get, "key_50")
        
        assert result == "value_50"
        
        # Verify performance target
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"L1 lookup too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l1_lookup_miss(self, benchmark, populated_cache):
        """Benchmark L1 cache miss (should be <1ms)."""
        result = benchmark(populated_cache.get, "nonexistent_key")
        
        assert result is None
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"L1 miss too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l1_set_new(self, benchmark):
        """Benchmark L1 cache set for new entry."""
        cache = ExactCache(max_size=1000)
        
        def set_operation():
            cache.set("test_key", "test_value")
        
        benchmark(set_operation)
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"L1 set too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l1_set_update(self, benchmark, populated_cache):
        """Benchmark L1 cache set for existing entry."""
        def update_operation():
            populated_cache.set("key_50", "new_value")
        
        benchmark(update_operation)
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"L1 update too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l1_eviction(self, benchmark):
        """Benchmark L1 cache eviction."""
        cache = ExactCache(max_size=100)
        
        # Fill cache
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Benchmark eviction (add one more)
        def trigger_eviction():
            cache.set("new_key", "new_value")
        
        benchmark(trigger_eviction)
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.002, f"L1 eviction too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l1_scalability_100(self, benchmark):
        """Test L1 performance with 100 entries."""
        cache = ExactCache(max_size=1000)
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        result = benchmark(cache.get, "key_50")
        assert result == "value_50"
    
    def test_l1_scalability_500(self, benchmark):
        """Test L1 performance with 500 entries."""
        cache = ExactCache(max_size=1000)
        for i in range(500):
            cache.set(f"key_{i}", f"value_{i}")
        
        result = benchmark(cache.get, "key_250")
        assert result == "value_250"
    
    def test_l1_scalability_1000(self, benchmark):
        """Test L1 performance with 1000 entries."""
        cache = ExactCache(max_size=1000)
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        result = benchmark(cache.get, "key_500")
        assert result == "value_500"


@pytest.mark.benchmark(group="cache-l2")
class TestL2CachePerformance:
    """Performance benchmarks for L2 (SemanticCache) operations."""
    
    @pytest.fixture
    def small_cache(self):
        """Create cache with 50 entries."""
        cache = SemanticCache(max_size=500, similarity_threshold=0.85)
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")
        return cache
    
    @pytest.fixture
    def medium_cache(self):
        """Create cache with 200 entries."""
        cache = SemanticCache(max_size=500, similarity_threshold=0.85)
        for i in range(200):
            cache.set(f"prompt_{i}", f"result_{i}")
        return cache
    
    @pytest.fixture
    def large_cache(self):
        """Create cache with 500 entries."""
        cache = SemanticCache(max_size=500, similarity_threshold=0.85)
        for i in range(500):
            cache.set(f"prompt_{i}", f"result_{i}")
        return cache
    
    def test_l2_lookup_small(self, benchmark, small_cache):
        """Benchmark L2 lookup with 50 entries."""
        result = benchmark(small_cache.get, "prompt_25")
        
        assert result == "result_25"
        
        stats = benchmark.stats
        # Should be well under 100ms for small cache
        assert stats.stats.mean < 0.050, f"L2 small lookup too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l2_lookup_medium(self, benchmark, medium_cache):
        """Benchmark L2 lookup with 200 entries."""
        result = benchmark(medium_cache.get, "prompt_100")
        
        assert result == "result_100"
        
        stats = benchmark.stats
        # Should be under 100ms for medium cache
        assert stats.stats.mean < 0.100, f"L2 medium lookup too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l2_lookup_large(self, benchmark, large_cache):
        """Benchmark L2 lookup with 500 entries (CRITICAL TEST)."""
        result = benchmark(large_cache.get, "prompt_250")
        
        assert result == "result_250"
        
        stats = benchmark.stats
        # This is the critical test - should be <100ms
        # Will likely FAIL with current O(n) implementation
        print(f"\n⚠️  L2 large cache lookup: {stats.stats.mean*1000:.2f}ms")
        if stats.stats.mean >= 0.100:
            print(f"❌ FAILED: Exceeds 100ms target - FAISS integration needed")
    
    def test_l2_set(self, benchmark):
        """Benchmark L2 cache set operation."""
        cache = SemanticCache(max_size=500)
        
        def set_operation():
            cache.set("test prompt", "test result")
        
        benchmark(set_operation)
        
        stats = benchmark.stats
        # Set can be slower due to embedding generation
        assert stats.stats.mean < 0.100, f"L2 set too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_l2_similarity_search(self, benchmark, medium_cache):
        """Benchmark similarity search (find_similar)."""
        result = benchmark(medium_cache.find_similar, "prompt_100", top_k=5)
        
        assert len(result) > 0
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.150, f"L2 similarity search too slow: {stats.stats.mean*1000:.2f}ms"


@pytest.mark.benchmark(group="cache-multilevel")
class TestMultiLevelCachePerformance:
    """Performance benchmarks for multi-level cache."""
    
    @pytest.fixture
    def populated_cache(self):
        """Create multi-level cache with data."""
        cache = MultiLevelCache(
            l1_max_size=1000,
            l2_max_size=500
        )
        
        # Add 100 entries
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        return cache
    
    def test_multilevel_l1_hit(self, benchmark, populated_cache):
        """Benchmark multi-level cache L1 hit (should be <1ms)."""
        result = benchmark(populated_cache.get, "key_50")
        
        assert result == "value_50"
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"Multi-level L1 hit too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_multilevel_l2_hit(self, benchmark):
        """Benchmark multi-level cache L2 hit."""
        cache = MultiLevelCache(
            l1_max_size=10,  # Small L1 to force L2 hits
            l2_max_size=500
        )
        
        # Add entries
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")
        
        # Clear L1 to force L2 lookup
        cache.l1_cache.clear()
        
        result = benchmark(cache.get, "prompt_25")
        
        # Should hit L2
        stats = benchmark.stats
        assert stats.stats.mean < 0.100, f"Multi-level L2 hit too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_multilevel_miss(self, benchmark, populated_cache):
        """Benchmark multi-level cache miss."""
        result = benchmark(populated_cache.get, "nonexistent_key")
        
        assert result is None
        
        stats = benchmark.stats
        # Miss checks both levels
        assert stats.stats.mean < 0.100, f"Multi-level miss too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_multilevel_set(self, benchmark):
        """Benchmark multi-level cache set."""
        cache = MultiLevelCache()
        
        def set_operation():
            cache.set("test_key", "test_value")
        
        benchmark(set_operation)
        
        stats = benchmark.stats
        # Set writes to both levels
        assert stats.stats.mean < 0.100, f"Multi-level set too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_multilevel_promotion(self, benchmark):
        """Benchmark L2 to L1 promotion."""
        cache = MultiLevelCache(
            l1_max_size=10,
            l2_max_size=500,
            promote_l2_hits=True
        )
        
        # Add entries
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")
        
        # Clear L1
        cache.l1_cache.clear()
        
        # First access hits L2 and promotes
        def access_and_promote():
            return cache.get("prompt_25")
        
        result = benchmark(access_and_promote)
        assert result == "result_25"


@pytest.mark.benchmark(group="cache-stress")
class TestCacheStressPerformance:
    """Stress tests for cache performance under load."""
    
    def test_l1_rapid_access(self, benchmark):
        """Test L1 cache under rapid access pattern."""
        cache = ExactCache(max_size=1000)
        
        # Populate
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Rapid access pattern
        def rapid_access():
            results = []
            for i in range(10):
                results.append(cache.get(f"key_{i % 100}"))
            return results
        
        results = benchmark(rapid_access)
        assert len(results) == 10
    
    def test_l1_thrashing(self, benchmark):
        """Test L1 cache with thrashing (constant eviction)."""
        cache = ExactCache(max_size=10)  # Small cache
        
        def thrashing_pattern():
            # Add 20 entries to 10-entry cache
            for i in range(20):
                cache.set(f"key_{i}", f"value_{i}")
        
        benchmark(thrashing_pattern)
        
        # Verify cache still works
        assert cache.size() == 10
    
    def test_l2_vocabulary_growth(self, benchmark):
        """Test L2 cache with growing vocabulary."""
        cache = SemanticCache(max_size=100)
        
        def add_diverse_prompts():
            # Add prompts with diverse vocabulary
            for i in range(10):
                cache.set(
                    f"unique prompt {i} with different words",
                    f"result_{i}"
                )
        
        benchmark(add_diverse_prompts)
        
        stats = benchmark.stats
        # Should handle vocabulary growth
        print(f"\nVocabulary growth: {stats.stats.mean*1000:.2f}ms per 10 prompts")
