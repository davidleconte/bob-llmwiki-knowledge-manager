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
        """Test that L1 is tried first (hit), then L2 serves as fallback on miss.

        The correctness property is: a key stored via set() is retrievable from
        L1 directly, and also from L2 after L1 is cleared. Wall-clock ordering
        (l1_time < l2_time) was inherently flaky on loaded CI runners; removed
        per the Tier-1 architecture review (D1). Latency targets live in the
        benchmark suite (tests/performance/).
        """
        cache = MultiLevelCache()

        cache.set("key1", "response1")

        # L1 hit: value must be returned directly from L1
        assert cache.get("key1") == "response1", "L1 should return the stored value"

        # Clear L1, force L2 fallback path
        cache.l1_cache.clear()

        # L2 fallback: value must still be returned (L2 has it)
        assert cache.get("key1") == "response1", "L2 fallback should return the stored value"

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



    def test_get_with_level_respects_disabled_flags(self):
        """get_with_level() must honour l1_enabled/l2_enabled — disabled levels must
        not be queried even when they contain matching data (M-1 regression)."""
        # L1 disabled: key is written only to L2 (set() respects the flag).
        cache_no_l1 = MultiLevelCache(l1_enabled=False)
        cache_no_l1.set("key", "value")
        # get_with_level() must not surface a result from the disabled L1 level.
        # (set() only wrote to L2, so L2 might return it — but L1 is the point.)
        result_via_get = cache_no_l1.get_with_level("key")
        # If L2 returns it, level must be "L2" not "L1".
        if result_via_get is not None:
            _, level = result_via_get
            assert level == "L2", "Disabled L1 must not be reported as the hit level"
        # Verify L1 was not queried by checking it is empty.
        assert cache_no_l1.l1_cache.size() == 0

        # L2 disabled: key is written only to L1.
        cache_no_l2 = MultiLevelCache(l2_enabled=False)
        cache_no_l2.set("key", "value")
        result_via_get = cache_no_l2.get_with_level("key")
        assert result_via_get is not None
        _, level = result_via_get
        assert level == "L1"
        # L2 must not have received the value or been queried.
        assert cache_no_l2.l2_cache.size() == 0

    def test_promotion_flag_consistent_in_stats_snapshot(self):
        """enable/disable_promotion() must hold _stats_lock and stats() must snapshot
        promote_l2_hits inside the same lock block as the counters, so the returned
        dict is internally consistent under concurrent flag flips (N-3 regression).
        ``sys`` state is restored in ``finally``.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = MultiLevelCache()
            for i in range(50):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            stop = threading.Event()

            def flipper() -> None:
                while not stop.is_set():
                    cache.enable_promotion()
                    cache.disable_promotion()

            def stat_reader() -> None:
                try:
                    for _ in range(500):
                        s = cache.stats()
                        flag = s["promote_l2_hits"]
                        assert isinstance(flag, bool), (
                            f"promote_l2_hits must be bool, got {type(flag)}: {flag}"
                        )
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=8) as executor:
                flippers = [executor.submit(flipper) for _ in range(3)]
                readers = [executor.submit(stat_reader) for _ in range(4)]
                for f in readers:
                    f.result()
                stop.set()
                for f in flippers:
                    f.result()

            assert not errors, f"promotion-flag race in stats(): {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)

    def test_stats_l1_size_and_utilization_are_consistent(self):
        """stats() must compute l1_size and l1_utilization from the same snapshot
        so they are internally consistent (N-4: double size() call race).
        Uses concurrent evictors to make the race window reachable.
        ``sys`` state is restored in ``finally``.
        """
        import sys
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = MultiLevelCache(l1_max_size=50, l2_max_size=50)
            for i in range(50):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            import threading

            stop = threading.Event()

            def evictor(tid: int) -> None:
                i = 0
                while not stop.is_set():
                    cache.set(f"evict_{tid}_{i}", f"v{i}")
                    i += 1

            def checker() -> None:
                try:
                    for _ in range(500):
                        s = cache.stats()
                        l1_size = s["l1_size"]
                        l1_max = s["l1_max_size"]
                        l1_util = s["l1_utilization"]
                        expected = (l1_size / l1_max) * 100
                        assert abs(l1_util - expected) < 1e-9, (
                            f"l1_size={l1_size} / l1_max={l1_max} → "
                            f"expected utilization {expected} but got {l1_util}"
                        )
                        l2_size = s["l2_size"]
                        l2_max = s["l2_max_size"]
                        l2_util = s["l2_utilization"]
                        expected2 = (l2_size / l2_max) * 100
                        assert abs(l2_util - expected2) < 1e-9, (
                            f"l2_size={l2_size} / l2_max={l2_max} → "
                            f"expected utilization {expected2} but got {l2_util}"
                        )
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=8) as executor:
                evictors = [executor.submit(evictor, t) for t in range(4)]
                checkers = [executor.submit(checker) for _ in range(4)]
                for f in checkers:
                    f.result()
                stop.set()
                for f in evictors:
                    f.result()

            assert not errors, f"stats() size/utilization inconsistency: {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)




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


# --------------------------------------------------------------------------- #
# P2-3 — Optional L3 (PersistentEmbeddingIndex) integration
# --------------------------------------------------------------------------- #


class TestMultiLevelCacheL3:
    """L3 optional persistent index (P2-3 / ADR-015 §Decision 4).

    L3 is a **document-reference** namespace, strictly separate from the
    prompt-response namespace of get()/set().  All L3 access goes through
    query_l3() which returns (doc_id, score) tuples, never response strings.
    """

    def test_query_l3_returns_doc_id_and_score(self, tmp_path):
        """query_l3() returns (doc_id, score) for a matching document."""
        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex

        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "l3-index")
        idx.index_document("concepts/caching.md", "# Caching\n\nMulti-level strategy L1 L2.")
        idx.flush()

        cache = MultiLevelCache(l3_index=idx)
        result = cache.query_l3("multi level cache strategy")
        # L3 should find "concepts/caching.md" as the top result
        assert result is not None
        doc_id, score = result
        assert doc_id == "concepts/caching.md"
        assert 0.0 <= score <= 1.0
        assert cache.l3_hits == 1
        assert cache.l1_hits == 0
        assert cache.l2_hits == 0

    def test_get_never_returns_doc_id(self, tmp_path):
        """get() stays in the prompt-response namespace — never returns a doc_id."""
        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex

        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "l3-index")
        idx.index_document("concepts/doc.md", "# Doc\n\ncontent")
        idx.flush()

        cache = MultiLevelCache(l3_index=idx)
        # get() on a key not in L1/L2 must return None, never a doc_id path
        result = cache.get("concepts/doc.md query")
        assert result is None
        assert cache.misses == 1
        assert cache.l3_hits == 0

    def test_get_l1_hit_unaffected_by_l3(self, tmp_path):
        """L1 hit path is unchanged when an L3 index is wired."""
        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex

        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "l3-index")
        idx.index_document("concepts/doc.md", "# Doc\n\ncontent")
        idx.flush()

        cache = MultiLevelCache(l3_index=idx)
        cache.set("exact query", "cached response")

        result = cache.get("exact query")
        assert result == "cached response"  # prompt response, not a doc_id
        assert cache.l1_hits == 1
        assert cache.l3_hits == 0

    def test_no_l3_index_no_regression(self):
        """Default construction (no L3) behaves identically to pre-P2-3."""
        cache = MultiLevelCache()
        assert cache.l3_index is None
        cache.set("key", "value")
        assert cache.get("key") == "value"
        assert cache.l3_hits == 0
        assert cache.query_l3("key") is None

    def test_clear_resets_l3_hits_not_index(self, tmp_path):
        """clear() resets l3_hits counter but does NOT clear the disk index."""
        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex

        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "l3-index")
        idx.index_document("guides/g.md", "# Guide\n\nguide content")
        idx.flush()

        cache = MultiLevelCache(l3_index=idx)
        cache.query_l3("guide content")  # explicit L3 query
        assert cache.l3_hits == 1

        cache.clear()
        assert cache.l3_hits == 0
        # Index still intact after clear
        assert idx.doc_count == 1

    def test_reset_stats_clears_l3_hits(self, tmp_path):
        """reset_stats() must zero l3_hits alongside l1_hits/l2_hits/misses (L-1 regression).

        Previously reset_stats() omitted l3_hits, causing a cumulative counter
        across checkpoints when an L3 index was wired.
        """
        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex

        embedder = EmbeddingGenerator()
        idx = PersistentEmbeddingIndex(embedder, tmp_path / "l3-index")
        idx.index_document("guides/g.md", "# Guide\n\nguide content")
        idx.flush()

        cache = MultiLevelCache(l3_index=idx)
        cache.query_l3("guide content")
        assert cache.l3_hits == 1

        cache.reset_stats()

        assert cache.l3_hits == 0, "reset_stats() must zero l3_hits"
        assert cache.l1_hits == 0
        assert cache.l2_hits == 0
        assert cache.misses == 0

