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

    @pytest.mark.slow
    def test_performance_lookup_latency(self):
        """Test that L1 cache returns correct values for all 100 entries.

        Latency validation (< 1 ms target) lives in the benchmark suite
        (tests/performance/) which has a saved baseline and a 25% regression
        threshold. Wall-clock assertions here were inherently flaky on slow CI
        runners; removed per the Tier-1 architecture review (D1).
        """
        cache = ExactCache()

        # Fill cache with 100 entries
        for i in range(100):
            cache.set(f"key_{i}", f"response_{i}")

        # All 100 entries must be retrievable with correct values
        for i in range(100):
            assert cache.get(f"key_{i}") == f"response_{i}", (
                f"key_{i} returned wrong value from L1 cache"
            )

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

    def test_version_support_disabled(self):
        """When version_support_enabled=False, set/get round-trips correctly.

        Regression: CacheConfig.version_support_enabled and max_versions were
        validated and stored in the manifest config but never passed to
        ExactCache.__init__, so version_support_enabled=False was silently ignored.
        """
        cache = ExactCache(version_support_enabled=False, max_versions=3)

        cache.set("key1", "response1")
        cache.set("key2", "response2")

        assert cache.get("key1") == "response1"
        assert cache.get("key2") == "response2"
        assert cache.size() == 2
        assert cache.version_support_enabled is False

    def test_version_support_enabled_default(self):
        """Default ExactCache has version_support_enabled=True."""
        cache = ExactCache()
        assert cache.version_support_enabled is True
        assert cache.max_versions == 5

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"


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


class TestExactCacheMigrate:
    """ExactCache.migrate() always returns 0 — SHA-256 keys are not reversible (M-2)."""

    def test_migrate_always_returns_zero(self):
        """ExactCache stores keys as irreversible SHA-256 hashes, so it is
        impossible to reconstruct the original key string for re-insertion under
        a new version prefix.  migrate() must return 0 and log
        'cache_migration_skipped' rather than silently returning 0 as if nothing
        matched the version filter.
        """
        cache = ExactCache(max_size=100)
        for i in range(10):
            cache.set(f"key_{i}", f"val_{i}", version="v1")

        result = cache.migrate("v1", "v2")

        assert result == 0
        # Cache contents are unchanged — no new v2 entries written.
        assert cache.size() == 10

    def test_migrate_returns_zero_on_empty_cache(self):
        """migrate() on an empty cache also returns 0 cleanly."""
        cache = ExactCache(max_size=100)
        assert cache.migrate("v1", "v2") == 0

    def test_migrate_returns_zero_when_version_not_present(self):
        """migrate() returns 0 when no entries match from_version."""
        cache = ExactCache(max_size=100)
        cache.set("key", "val", version="v3")
        assert cache.migrate("v1", "v2") == 0


class TestExactCacheStatsConsistency:
    """stats() must return a consistent size/utilization pair (N-4).

    Before the fix, stats() called self.size() twice — once for "size" and once
    for "utilization".  A concurrent eviction between the two calls could yield
    a snapshot where utilization does not match size:
        utilization != size * 100 / max_size
    The fix snapshots `n = self.size()` once and reuses it for both fields.
    """

    def test_stats_size_and_utilization_are_consistent_no_concurrency(self):
        """Baseline: single-threaded — size and utilization always agree."""
        cache = ExactCache(max_size=50)
        for i in range(30):
            cache.set(f"key_{i}", f"val_{i}")

        s = cache.stats()
        expected_utilization = s["size"] * 100 / s["max_size"]
        assert s["utilization"] == expected_utilization, (
            f"utilization {s['utilization']} does not match "
            f"size {s['size']} / max_size {s['max_size']}"
        )

    def test_stats_size_and_utilization_consistent_under_concurrent_eviction(self):
        """Race-detector: concurrent evictors must not cause size/utilization mismatch.

        With the old double self.size() call an evictor running between the two
        reads could produce a snapshot where
            utilization != size * 100 / max_size.
        The fix snapshots n = self.size() once so both fields are always derived
        from the same measurement.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            max_size = 20
            cache = ExactCache(max_size=max_size)
            for i in range(max_size):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            stop = threading.Event()
            counter = [0]

            def evictor() -> None:
                """Continuously add and clear entries to provoke evictions."""
                i = max_size
                while not stop.is_set():
                    cache.set(f"extra_{i}", f"val_{i}")
                    i += 1

            def stat_checker() -> None:
                try:
                    for _ in range(1_000):
                        s = cache.stats()
                        expected = s["size"] * 100 / s["max_size"]
                        assert s["utilization"] == expected, (
                            f"Inconsistent snapshot: size={s['size']}, "
                            f"utilization={s['utilization']}, expected={expected}"
                        )
                        counter[0] += 1
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=10) as executor:
                evictors = [executor.submit(evictor) for _ in range(4)]
                checkers = [executor.submit(stat_checker) for _ in range(4)]
                for f in checkers:
                    f.result()
                stop.set()
                for f in evictors:
                    f.result()

            assert not errors, f"stats() inconsistency detected: {errors[:3]}"
            assert counter[0] >= 3_000, f"Too few stat checks ran: {counter[0]}"
        finally:
            sys.setswitchinterval(old_interval)
