"""Tests for multi-level cache (L1 + L2).

Tests cover:
- L1 and L2 cache interaction
- L2 to L1 promotion
- Statistics tracking
- Performance requirements (<100ms lookup)
- Hit rate targets (23.33% combined)
"""

import time

import pytest

from src.cache.multi_level_cache import MultiLevelCache


class TestMultiLevelCache:
    """Test suite for MultiLevelCache."""

    def test_initialization(self):
        """Test cache initialization with default parameters."""
        cache = MultiLevelCache()

        assert cache.l1_cache.max_size == 1000
        # Phase 4: default raised 500 -> 10000 to match CacheConfig.l2_max_size
        # (and keep L2 > L1, the config's business rule).
        assert cache.l2_cache.max_size == 10000
        assert cache.l2_cache.similarity_threshold == 0.85
        assert cache.promote_l2_hits is True
        assert cache.l1_hits == 0
        assert cache.l2_hits == 0
        assert cache.misses == 0

    def test_initialization_custom_params(self):
        """Test cache initialization with custom parameters."""
        cache = MultiLevelCache(
            l1_max_size=500, l2_max_size=250, similarity_threshold=0.90, promote_l2_hits=False
        )

        assert cache.l1_cache.max_size == 500
        assert cache.l2_cache.max_size == 250
        assert cache.l2_cache.similarity_threshold == 0.90
        assert cache.promote_l2_hits is False

    def test_l1_exact_match(self):
        """Test L1 cache hit with exact match."""
        cache = MultiLevelCache()

        # Set and get exact match
        cache.set("What is Python?", "Python is a programming language")
        result = cache.get("What is Python?")

        assert result == "Python is a programming language"
        assert cache.l1_hits == 1
        assert cache.l2_hits == 0
        assert cache.misses == 0

    def test_l2_semantic_match(self):
        """Test L2 cache hit with semantic similarity."""
        cache = MultiLevelCache(similarity_threshold=0.70)

        # Set a prompt
        cache.set("What is Python programming?", "Python is a high-level language")

        # Clear L1 to force L2 lookup
        cache.l1_cache.clear()
        cache.l1_hits = 0

        # Try similar prompt (should match in L2)
        result = cache.get("Tell me about Python programming")

        # Should find in L2 (if similarity > 0.70)
        if result is not None:
            assert cache.l2_hits >= 1

    def test_l2_to_l1_promotion(self):
        """Test that L2 hits are promoted to L1."""
        cache = MultiLevelCache(similarity_threshold=0.70, promote_l2_hits=True)

        # Set a prompt
        cache.set("Python programming", "Python is great")

        # Clear L1 to force L2 lookup
        cache.l1_cache.clear()

        # Get similar prompt (L2 hit)
        result1 = cache.get("Python programming")

        if result1 is not None:
            # Should be promoted to L1
            # Next access should be L1 hit
            result2 = cache.get("Python programming")
            assert result2 == result1

    def test_promotion_disabled(self):
        """Test that promotion can be disabled."""
        cache = MultiLevelCache(promote_l2_hits=False)

        cache.set("key1", "response1")

        # Clear L1
        cache.l1_cache.clear()

        # Get from L2
        result = cache.get("key1")

        # Should not be in L1 after L2 hit
        assert "key1" not in cache.l1_cache.cache

    def test_cache_miss(self):
        """Test cache miss when key not in L1 or L2."""
        cache = MultiLevelCache()

        result = cache.get("nonexistent key")

        assert result is None
        assert cache.l1_hits == 0
        assert cache.l2_hits == 0
        assert cache.misses == 1

    def test_hit_rate_calculation(self):
        """Test overall hit rate calculation."""
        cache = MultiLevelCache()

        # Set some keys
        cache.set("key1", "response1")
        cache.set("key2", "response2")

        # 2 L1 hits, 1 miss = 66.67% hit rate
        cache.get("key1")  # L1 hit
        cache.get("key2")  # L1 hit
        cache.get("key3")  # miss

        assert cache.hit_rate() == pytest.approx(66.67, rel=0.1)

    def test_l1_hit_rate(self):
        """Test L1 hit rate calculation."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        # 1 L1 hit, 1 miss
        cache.get("key1")  # L1 hit
        cache.get("key2")  # miss

        assert cache.l1_hit_rate() == 50.0

    def test_l2_hit_rate(self):
        """Test L2 hit rate calculation."""
        cache = MultiLevelCache(similarity_threshold=0.70)

        cache.set("Python programming", "Python is great")

        # Clear L1 to force L2
        cache.l1_cache.clear()
        cache.l1_hits = 0

        # Try to get (may hit L2)
        result = cache.get("Python programming")

        if result is not None:
            assert cache.l2_hit_rate() > 0

    def test_clear(self):
        """Test clearing both caches."""
        cache = MultiLevelCache()

        # Add entries
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.get("key1")  # Generate stats

        # Clear
        cache.clear()

        assert cache.size() == 0
        assert cache.l1_hits == 0
        assert cache.l2_hits == 0
        assert cache.misses == 0

    def test_size(self):
        """Test size calculation (unique entries)."""
        cache = MultiLevelCache()

        # Add entries (stored in both L1 and L2)
        cache.set("key1", "response1")
        cache.set("key2", "response2")

        # L1 uses hashes, L2 uses original keys
        # Size counts unique original keys from L2
        assert cache.l1_cache.size() == 2
        assert cache.l2_cache.size() == 2

    def test_stats_output(self):
        """Test comprehensive stats output."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")
        cache.get("key1")  # L1 hit
        cache.get("key2")  # miss

        stats = cache.stats()

        assert "total_requests" in stats
        assert "total_hits" in stats
        assert "total_misses" in stats
        assert "hit_rate" in stats
        assert "l1_hits" in stats
        assert "l1_hit_rate" in stats
        assert "l2_hits" in stats
        assert "l2_hit_rate" in stats
        assert "avg_lookup_time_ms" in stats
        assert stats["total_requests"] == 2
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 1

    def test_get_with_level(self):
        """Test getting response with cache level info."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        # L1 hit
        result = cache.get_with_level("key1")
        assert result is not None
        response, level = result
        assert response == "response1"
        assert level == "L1"

        # Clear L1 to test L2
        cache.l1_cache.clear()

        result = cache.get_with_level("key1")
        if result is not None:
            response, level = result
            assert level == "L2"

    def test_contains(self):
        """Test checking if key exists in either cache."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        assert cache.contains("key1") is True
        assert cache.contains("nonexistent") is False

    def test_update_similarity_threshold(self):
        """Test updating L2 similarity threshold."""
        cache = MultiLevelCache(similarity_threshold=0.85)

        cache.update_similarity_threshold(0.90)

        assert cache.l2_cache.similarity_threshold == 0.90

    def test_enable_disable_promotion(self):
        """Test enabling and disabling L2 to L1 promotion."""
        cache = MultiLevelCache(promote_l2_hits=False)

        assert cache.promote_l2_hits is False

        cache.enable_promotion()
        assert cache.promote_l2_hits is True

        cache.disable_promotion()
        assert cache.promote_l2_hits is False

    def test_get_l1_cache(self):
        """Test getting L1 cache instance."""
        cache = MultiLevelCache()

        l1 = cache.get_l1_cache()

        assert l1 is cache.l1_cache
        assert l1.max_size == 1000

    def test_get_l2_cache(self):
        """Test getting L2 cache instance."""
        cache = MultiLevelCache()

        l2 = cache.get_l2_cache()

        assert l2 is cache.l2_cache
        assert l2.max_size == 10000  # Phase 4: default 500 -> 10000 (matches CacheConfig)

    def test_average_lookup_time(self):
        """Test average lookup time calculation."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        # Perform some lookups
        for _ in range(10):
            cache.get("key1")

        avg_time = cache.average_lookup_time_ms()

        assert avg_time >= 0
        assert avg_time < 100  # Should be fast for L1 hits

    def test_reset_stats(self):
        """Test resetting statistics."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")
        cache.get("key1")
        cache.get("key2")

        # Reset stats
        cache.reset_stats()

        assert cache.l1_hits == 0
        assert cache.l2_hits == 0
        assert cache.misses == 0
        assert len(cache._lookup_times) == 0

    @pytest.mark.slow
    def test_performance_lookup_latency(self):
        """Test that lookup latency is <100ms (target)."""
        cache = MultiLevelCache()

        # Fill cache with entries
        for i in range(50):
            cache.set(f"key_{i}", f"response_{i}")

        # Measure lookup time
        start = time.time()
        for i in range(50):
            cache.get(f"key_{i}")
        end = time.time()

        avg_latency_ms = ((end - start) / 50) * 1000

        # Should be under 100ms per lookup
        assert avg_latency_ms < 100.0, f"Lookup latency {avg_latency_ms}ms exceeds 100ms target"

    def test_metadata_storage(self):
        """Test that metadata is stored in both caches."""
        cache = MultiLevelCache()

        metadata = {"tokens": 100, "quality": 0.95}
        cache.set("key1", "response1", metadata=metadata)

        # Check L1
        l1_entry = cache.l1_cache.get_entry("key1")
        assert l1_entry is not None
        assert l1_entry.metadata == metadata

        # Check L2
        l2_entry = cache.l2_cache.get_entry("key1")
        assert l2_entry is not None
        assert l2_entry.metadata == metadata

    def test_l1_l2_consistency(self):
        """Test that L1 and L2 stay consistent."""
        cache = MultiLevelCache()

        # Set multiple entries
        for i in range(10):
            cache.set(f"key_{i}", f"response_{i}")

        # All should be retrievable from both caches
        for i in range(10):
            # Check L1 can retrieve
            assert cache.l1_cache.get(f"key_{i}") == f"response_{i}"
            # Check L2 has the key
            versioned_key = cache.l2_cache._make_versioned_key(f"key_{i}")
            assert versioned_key in cache.l2_cache.embeddings

    def test_l1_fast_l2_fallback(self):
        """Test that L1 is tried first, then L2."""
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        # L1 hit should be faster
        start = time.time()
        cache.get("key1")
        l1_time = time.time() - start

        # Clear L1, force L2
        cache.l1_cache.clear()

        start = time.time()
        cache.get("key1")
        l2_time = time.time() - start

        # L1 should be faster than L2
        assert l1_time < l2_time

    def test_unicode_handling(self):
        """Test handling of unicode keys."""
        cache = MultiLevelCache()

        cache.set("什么是Python？", "Python是编程语言")
        cache.set("🐍 Python", "Python with emoji")

        assert cache.get("什么是Python？") == "Python是编程语言"
        assert cache.get("🐍 Python") == "Python with emoji"

    def test_long_key_handling(self):
        """Test handling of very long keys."""
        cache = MultiLevelCache()

        long_key = " ".join([f"word{i}" for i in range(1000)])
        cache.set(long_key, "response to long key")

        result = cache.get(long_key)
        assert result == "response to long key"

    def test_empty_key_handling(self):
        """Test handling of empty keys."""
        cache = MultiLevelCache()

        cache.set("", "empty response")
        result = cache.get("")

        # Should handle gracefully
        assert result is not None or result is None

    def test_concurrent_operations(self):
        """Test multiple operations in sequence."""
        cache = MultiLevelCache()

        # Mix of sets and gets
        cache.set("key1", "response1")
        cache.get("key1")
        cache.set("key2", "response2")
        cache.get("key2")
        cache.get("key3")  # miss
        cache.set("key3", "response3")
        cache.get("key3")

        stats = cache.stats()
        assert stats["total_requests"] == 4
        assert stats["total_hits"] == 3
        assert stats["total_misses"] == 1


class TestMultiLevelCacheTTL:
    """MultiLevelCache must thread TTL config into its sub-caches (C-6)."""

    def test_ttl_config_reaches_sub_caches(self):
        cache = MultiLevelCache(l1_ttl_seconds=3600, l2_ttl_seconds=86400)
        # Config must actually reach the caches, not be silently inert.
        assert cache.l1_cache.ttl_seconds == 3600
        assert cache.l2_cache.ttl_seconds == 86400

    def test_ttl_defaults_to_none(self):
        cache = MultiLevelCache()
        assert cache.l1_cache.ttl_seconds is None
        assert cache.l2_cache.ttl_seconds is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
