"""Tests for exact match cache (L1).

Tests cover:
- Basic get/set operations
- LRU eviction
- Cache statistics
- Performance requirements (<1ms lookup)
"""

import time

import pytest

from src.cache.exact_cache import ExactCache


class TestExactCache:
    """Test suite for ExactCache."""

    def test_initialization(self):
        """Test cache initialization with default and custom sizes."""
        # Default size
        cache = ExactCache()
        assert cache.max_size == 1000
        assert cache.size() == 0

        # Custom size
        cache = ExactCache(max_size=500)
        assert cache.max_size == 500
        assert cache.size() == 0

    def test_initialization_invalid_size(self):
        """Test that invalid max_size raises ValueError."""
        with pytest.raises(ValueError):
            ExactCache(max_size=0)

        with pytest.raises(ValueError):
            ExactCache(max_size=-1)

    def test_basic_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = ExactCache()

        # Set and get
        cache.set("test_key", "test_response")
        result = cache.get("test_key")

        assert result == "test_response"
        assert cache.size() == 1

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = ExactCache()
        result = cache.get("nonexistent")

        assert result is None

    def test_cache_hit_statistics(self):
        """Test that cache hits are tracked correctly."""
        cache = ExactCache()

        # Set a key
        cache.set("key1", "response1")

        # First get - should be a hit
        cache.get("key1")
        assert cache._stats.hits == 1
        assert cache._stats.misses == 0

        # Second get - another hit
        cache.get("key1")
        assert cache._stats.hits == 2
        assert cache._stats.misses == 0

    def test_cache_miss_statistics(self):
        """Test that cache misses are tracked correctly."""
        cache = ExactCache()

        # Get nonexistent key - should be a miss
        cache.get("nonexistent")
        assert cache._stats.hits == 0
        assert cache._stats.misses == 1

        # Another miss
        cache.get("another_nonexistent")
        assert cache._stats.hits == 0
        assert cache._stats.misses == 2

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        cache = ExactCache()

        # Set some keys
        cache.set("key1", "response1")
        cache.set("key2", "response2")

        # 2 hits, 2 misses = 50% hit rate
        cache.get("key1")  # hit
        cache.get("key2")  # hit
        cache.get("key3")  # miss
        cache.get("key4")  # miss

        assert cache.hit_rate() == 50.0

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = ExactCache(max_size=3)

        # Fill cache
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.set("key3", "response3")
        assert cache.size() == 3

        # Add one more - should evict key1 (oldest)
        cache.set("key4", "response4")
        assert cache.size() == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key4") == "response4"  # New entry exists

    def test_lru_access_updates_order(self):
        """Test that accessing a key updates its position in LRU."""
        cache = ExactCache(max_size=3)

        # Fill cache
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.set("key3", "response3")

        # Access key1 to make it most recently used
        cache.get("key1")

        # Add new key - should evict key2 (now oldest)
        cache.set("key4", "response4")
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key1") == "response1"  # Still exists

    def test_metadata_storage(self):
        """Test that metadata is stored with cache entries."""
        cache = ExactCache()

        metadata = {"tokens": 100, "quality": 0.95}
        cache.set("key1", "response1", metadata=metadata)

        entry = cache.get_entry("key1")
        assert entry is not None
        assert entry.metadata == metadata

    def test_entry_access_tracking(self):
        """Test that entry access count and timestamp are tracked."""
        cache = ExactCache()

        cache.set("key1", "response1")
        entry = cache.get_entry("key1")

        initial_access_count = entry.access_count
        initial_last_access = entry.last_access

        # Wait a bit and access again
        time.sleep(0.01)
        cache.get("key1")

        entry = cache.get_entry("key1")
        assert entry.access_count > initial_access_count
        assert entry.last_access > initial_last_access

    def test_clear(self):
        """Test clearing the cache."""
        cache = ExactCache()

        # Add some entries
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.get("key1")  # Generate some stats

        # Clear
        cache.clear()

        assert cache.size() == 0
        assert cache._stats.hits == 0
        assert cache._stats.misses == 0

    def test_contains(self):
        """Test checking if key exists in cache."""
        cache = ExactCache()

        cache.set("key1", "response1")

        assert cache.contains("key1") is True
        assert cache.contains("nonexistent") is False

    def test_manual_eviction(self):
        """Test manually evicting a specific key."""
        cache = ExactCache()

        cache.set("key1", "response1")
        cache.set("key2", "response2")

        # Evict key1
        result = cache.evict("key1")
        assert result is True
        assert cache.get("key1") is None
        assert cache.get("key2") == "response2"

        # Try to evict nonexistent key
        result = cache.evict("nonexistent")
        assert result is False

    def test_get_oldest_entry(self):
        """Test getting the oldest (LRU) entry."""
        cache = ExactCache()

        # Empty cache
        assert cache.get_oldest_entry() is None

        # Add entries
        cache.set("key1", "response1")
        time.sleep(0.01)
        cache.set("key2", "response2")

        # Oldest should be key1
        key, entry = cache.get_oldest_entry()
        assert entry.response == "response1"

    def test_get_newest_entry(self):
        """Test getting the newest (MRU) entry."""
        cache = ExactCache()

        # Empty cache
        assert cache.get_newest_entry() is None

        # Add entries
        cache.set("key1", "response1")
        time.sleep(0.01)
        cache.set("key2", "response2")

        # Newest should be key2
        key, entry = cache.get_newest_entry()
        assert entry.response == "response2"

    def test_stats_output(self):
        """Test comprehensive stats output."""
        cache = ExactCache(max_size=100)

        # Add some entries and generate stats
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.get("key1")  # hit
        cache.get("key3")  # miss

        stats = cache.stats()

        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
        assert "max_size" in stats
        assert "utilization" in stats
        assert stats["size"] == 2
        assert stats["max_size"] == 100
        assert stats["utilization"] == 2.0  # 2/100 * 100

    def test_performance_lookup_latency(self):
        """Test that lookup latency is <1ms (target)."""
        cache = ExactCache()

        # Fill cache with 100 entries
        for i in range(100):
            cache.set(f"key_{i}", f"response_{i}")

        # Measure lookup time
        start = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        end = time.time()

        avg_latency_ms = ((end - start) / 100) * 1000

        # Should be well under 1ms per lookup
        assert avg_latency_ms < 1.0, f"Lookup latency {avg_latency_ms}ms exceeds 1ms target"

    def test_hash_collision_handling(self):
        """Test that different keys with same hash are handled correctly."""
        cache = ExactCache()

        # These are different keys
        cache.set("key1", "response1")
        cache.set("key2", "response2")

        # Should retrieve correct responses
        assert cache.get("key1") == "response1"
        assert cache.get("key2") == "response2"

    def test_large_response_storage(self):
        """Test storing large responses."""
        cache = ExactCache()

        # Create a large response (1MB)
        large_response = "x" * (1024 * 1024)
        cache.set("large_key", large_response)

        result = cache.get("large_key")
        assert result == large_response
        assert len(result) == 1024 * 1024

    def test_unicode_key_handling(self):
        """Test handling of unicode keys."""
        cache = ExactCache()

        # Unicode keys
        cache.set("键1", "响应1")
        cache.set("🔑2", "📝2")

        assert cache.get("键1") == "响应1"
        assert cache.get("🔑2") == "📝2"

    def test_entry_age_calculation(self):
        """Test cache entry age calculation."""
        cache = ExactCache()

        cache.set("key1", "response1")
        entry = cache.get_entry("key1")

        # Age should be very small (just created)
        assert entry.age_seconds() < 1.0

        # Wait and check again
        time.sleep(0.1)
        assert entry.age_seconds() >= 0.1

    def test_entry_idle_time_calculation(self):
        """Test cache entry idle time calculation."""
        cache = ExactCache()

        cache.set("key1", "response1")

        # Access immediately
        cache.get("key1")
        entry = cache.get_entry("key1")
        assert entry.idle_seconds() < 0.1

        # Wait and check idle time
        time.sleep(0.1)
        assert entry.idle_seconds() >= 0.1


class TestExactCacheTTL:
    """TTL enforcement on read (C-6 regression).

    Previously ttl_seconds was configured (l1=3600) but never plumbed into any
    cache or checked on get(): an entry lived until LRU eviction regardless of
    age, so the TTL config was silently inert. These use an injected clock for
    deterministic time control (no time.sleep).
    """

    def test_get_returns_miss_after_ttl_expiry(self):
        clock = [1000.0]
        cache = ExactCache(max_size=10, ttl_seconds=10, clock=lambda: clock[0])

        cache.set("key1", "response1")
        assert cache.get("key1") == "response1"  # fresh hit at t=1000

        clock[0] = 1011.0  # advance past ttl (11 > 10)
        assert cache.get("key1") is None  # expired -> miss
        assert cache.size() == 0  # evicted on the expired read

    def test_entry_within_ttl_is_a_hit(self):
        clock = [1000.0]
        cache = ExactCache(max_size=10, ttl_seconds=10, clock=lambda: clock[0])

        cache.set("key1", "response1")
        clock[0] = 1009.0  # still within ttl (9 < 10)
        assert cache.get("key1") == "response1"
        assert cache.size() == 1

    def test_ttl_none_never_expires(self):
        clock = [1000.0]
        cache = ExactCache(max_size=10, ttl_seconds=None, clock=lambda: clock[0])

        cache.set("key1", "response1")
        clock[0] = 10_000_000.0  # far in the future
        assert cache.get("key1") == "response1"  # no ttl -> no expiry

    def test_versioned_key_no_collision_across_version_key_boundary(self):
        """A colon inside the version must not collide with the version/key join.

        Regression for the unescaped ``f"{version}:{key}"`` encoding: ('b',
        version='v1:a') and ('a:b', version='v1') both rendered 'v1:a:b', so the
        second write clobbered the first and a reader got the wrong content.
        With version-escaping the two keys are distinct.
        """
        cache = ExactCache(max_size=10)
        cache.set("b", "VALUE_B", version="v1:a")
        cache.set("a:b", "VALUE_AB", version="v1")

        assert cache.get("b", version="v1:a") == "VALUE_B"
        assert cache.get("a:b", version="v1") == "VALUE_AB"
        assert cache.size() == 2  # two distinct entries, no overwrite


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
