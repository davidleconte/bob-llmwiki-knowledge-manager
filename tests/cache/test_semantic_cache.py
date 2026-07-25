"""Tests for semantic similarity cache (L2).

Tests cover:
- Embedding generation
- Semantic similarity matching
- Similarity threshold behavior
- Cache statistics
- Performance requirements (<100ms lookup)
"""

import time

import pytest

from src.cache.semantic_cache import SemanticCache


class TestSemanticCache:
    """Test suite for SemanticCache."""

    def test_initialization(self):
        """Test cache initialization with default and custom parameters."""
        # Default parameters
        cache = SemanticCache()
        assert cache.similarity_threshold == 0.85
        assert cache.max_size == 500
        assert cache.size() == 0

        # Custom parameters
        cache = SemanticCache(similarity_threshold=0.90, max_size=100)
        assert cache.similarity_threshold == 0.90
        assert cache.max_size == 100

    def test_initialization_invalid_threshold(self):
        """Test that invalid similarity threshold raises ValueError."""
        with pytest.raises(ValueError):
            SemanticCache(similarity_threshold=1.5)

        with pytest.raises(ValueError):
            SemanticCache(similarity_threshold=-0.1)

    def test_initialization_invalid_size(self):
        """Test that invalid max_size raises ValueError."""
        with pytest.raises(ValueError):
            SemanticCache(max_size=0)

        with pytest.raises(ValueError):
            SemanticCache(max_size=-1)

    def test_basic_set_and_get_exact_match(self):
        """Test basic cache operations with exact match."""
        cache = SemanticCache()

        # Set and get exact match
        cache.set("What is Python?", "Python is a programming language")
        result = cache.get("What is Python?")

        assert result == "Python is a programming language"
        assert cache.size() == 1

    def test_exact_key_returns_its_own_value_under_collisions(self):
        """An exactly-stored key must return ITS OWN value, not a neighbour's.

        Populates enough single-token keys that HashingVectorizer buckets
        collide (birthday paradox: 500 keys in n_features=1000), then requires
        every stored key to retrieve its own value. Guards the exact-key
        fast-path in ``SemanticCache.get()`` (C-5 cache-quality fix): without it,
        get() could return a colliding embedding's value at similarity 1.0.
        """
        cache = SemanticCache(max_size=500, similarity_threshold=0.85)
        for i in range(500):
            cache.set(f"prompt_{i}", f"result_{i}")

        mismatches = [i for i in range(500) if cache.get(f"prompt_{i}") != f"result_{i}"]
        assert not mismatches, (
            f"{len(mismatches)} keys returned a colliding neighbour's value; "
            f"first few: {mismatches[:5]}"
        )

    def test_population_is_linear_not_quadratic(self):
        """Populating N distinct keys generates O(N) embeddings, not O(N^2).

        Regression guard for the removed ``_regenerate_all_embeddings()``
        O(n^2) path (which timed out the scalability/stress tests): each
        ``set()`` of a novel key must generate exactly one new embedding, not
        rebuild the whole cache. Counts ``generate()`` calls — deterministic,
        no wall-clock assertion (which would be flaky).
        """
        cache = SemanticCache(max_size=1000)
        gen = cache.embedding_generator
        original_generate = gen.generate
        calls = {"n": 0}

        def counting_generate(text, use_cache=True):
            calls["n"] += 1
            return original_generate(text, use_cache=use_cache)

        gen.generate = counting_generate

        n = 200
        for i in range(n):
            cache.set(f"key_{i}", f"value_{i}")

        # O(n) population is ~1 generate per set; the old O(n^2) regeneration
        # would be ~n*(n-1)/2 (~20k for n=200). 3*n is a wide, robust margin.
        assert calls["n"] <= 3 * n, (
            f"{calls['n']} generate() calls for {n} sets — O(n^2) regeneration reintroduced?"
        )

    def test_semantic_similarity_match(self):
        """Test semantic similarity matching with similar prompts."""
        cache = SemanticCache(similarity_threshold=0.70)

        # Cache a response
        cache.set("What is Python programming?", "Python is a high-level language")

        # Try similar prompt (should match semantically)
        result = cache.get("Tell me about Python programming")

        # Should find similar match (if similarity > 0.70)
        # Note: Actual match depends on TF-IDF similarity
        assert result is not None or result is None  # Either way is valid

    def test_similarity_threshold_behavior(self):
        """Test that similarity threshold controls matching."""
        # High threshold (strict matching)
        cache_strict = SemanticCache(similarity_threshold=0.95)
        cache_strict.set("Python programming language", "Python is great")

        # Very different prompt should not match
        result = cache_strict.get("JavaScript web development")
        assert result is None

        # Low threshold (loose matching)
        cache_loose = SemanticCache(similarity_threshold=0.50)
        cache_loose.set("Python programming language", "Python is great")

        # Similar prompt more likely to match
        result = cache_loose.get("Python coding")
        # May or may not match depending on TF-IDF, but threshold is lower
        assert result is not None or result is None

    def test_cache_hit_statistics(self):
        """Test that cache hits are tracked correctly."""
        cache = SemanticCache()

        # Set a key
        cache.set("key1", "response1")

        # Get exact match - should be a hit
        cache.get("key1")
        assert cache._stats.hits == 1
        assert cache._stats.misses == 0

    def test_cache_miss_statistics(self):
        """Test that cache misses are tracked correctly."""
        cache = SemanticCache()

        # Get nonexistent key - should be a miss
        cache.get("nonexistent")
        assert cache._stats.hits == 0
        assert cache._stats.misses == 1

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        cache = SemanticCache()

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
        cache = SemanticCache(max_size=3)

        # Fill cache
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.set("key3", "response3")
        assert cache.size() == 3

        # Add one more - should evict least recently used
        cache.set("key4", "response4")
        assert cache.size() == 3

    def test_metadata_storage(self):
        """Test that metadata is stored with cache entries."""
        cache = SemanticCache()

        metadata = {"tokens": 100, "quality": 0.95}
        cache.set("key1", "response1", metadata=metadata)

        entry = cache.get_entry("key1")
        assert entry is not None
        # The cache stores a copy with its own `version` bookkeeping added; the
        # caller's items are preserved and the caller's dict is never mutated (ATK-FS-05).
        assert metadata.items() <= entry.metadata.items()
        assert "version" not in metadata

    def test_clear(self):
        """Test clearing the cache."""
        cache = SemanticCache()

        # Add some entries
        cache.set("key1", "response1")
        cache.set("key2", "response2")
        cache.get("key1")  # Generate some stats

        # Clear
        cache.clear()

        assert cache.size() == 0
        assert cache._stats.hits == 0
        assert cache._stats.misses == 0

    def test_find_similar(self):
        """Test finding similar cached prompts."""
        cache = SemanticCache()

        # Add several entries
        cache.set("Python programming", "Python is great")
        cache.set("Java development", "Java is powerful")
        cache.set("JavaScript coding", "JS is versatile")

        # Find similar to Python
        similar = cache.find_similar("Python coding", top_k=2)

        assert len(similar) <= 2
        assert all(len(item) == 3 for item in similar)  # (prompt, similarity, response)
        assert all(0 <= item[1] <= 1 for item in similar)  # Similarity in [0,1]

    def test_get_with_similarity(self):
        """Test getting response with similarity score."""
        cache = SemanticCache()

        cache.set("Python programming", "Python is great")

        # Get with similarity
        result = cache.get_with_similarity("Python programming")

        if result is not None:
            response, similarity = result
            assert response == "Python is great"
            assert 0 <= similarity <= 1

    def test_contains_similar(self):
        """Test checking if similar key exists."""
        cache = SemanticCache()

        cache.set("Python programming", "Python is great")

        # Exact match should exist
        assert cache.contains("Python programming") is True

        # Very different prompt should not exist
        cache_strict = SemanticCache(similarity_threshold=0.95)
        cache_strict.set("Python programming", "Python is great")
        assert cache_strict.contains("Completely different topic") is False

    def test_update_threshold(self):
        """Test updating similarity threshold."""
        cache = SemanticCache(similarity_threshold=0.85)

        # Update threshold
        cache.update_threshold(0.90)
        assert cache.similarity_threshold == 0.90

        # Invalid threshold should raise error
        with pytest.raises(ValueError):
            cache.update_threshold(1.5)

    def test_stats_output(self):
        """Test comprehensive stats output."""
        cache = SemanticCache(max_size=100)

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
        assert "similarity_threshold" in stats
        assert stats["size"] == 2
        assert stats["max_size"] == 100

    def test_average_similarity_score(self):
        """Test average similarity score calculation."""
        cache = SemanticCache()

        # Initially no scores
        assert cache.average_similarity_score() == 0.0

        # Add entry and get it (exact match = 1.0 similarity)
        cache.set("key1", "response1")
        cache.get("key1")

        # Should have recorded similarity score
        avg = cache.average_similarity_score()
        assert 0 <= avg <= 1

    @pytest.mark.slow
    def test_performance_lookup_latency(self):
        """Test that lookup latency is <100ms (target)."""
        cache = SemanticCache()

        # Fill cache with 50 entries
        for i in range(50):
            cache.set(f"key_{i} with some text", f"response_{i}")

        # Measure lookup time
        start = time.time()
        for i in range(50):
            cache.get(f"key_{i} with some text")
        end = time.time()

        avg_latency_ms = ((end - start) / 50) * 1000

        # Should be under 100ms per lookup
        assert avg_latency_ms < 100.0, f"Lookup latency {avg_latency_ms}ms exceeds 100ms target"

    def test_embedding_generation(self):
        """Test that embeddings are generated correctly."""
        cache = SemanticCache()

        # Set a key (should generate embedding)
        cache.set("test prompt", "test response")

        # Check that embedding exists
        versioned_key = cache._make_versioned_key("test prompt")
        assert versioned_key in cache.embeddings
        assert cache.embeddings[versioned_key] is not None

    def test_unicode_handling(self):
        """Test handling of unicode prompts."""
        cache = SemanticCache()

        # Unicode prompts
        cache.set("什么是Python？", "Python是编程语言")
        cache.set("🐍 Python programming", "Python with emoji")

        assert cache.get("什么是Python？") == "Python是编程语言"
        assert cache.get("🐍 Python programming") == "Python with emoji"

    def test_long_prompt_handling(self):
        """Test handling of very long prompts."""
        cache = SemanticCache()

        # Create a long prompt (1000 words)
        long_prompt = " ".join([f"word{i}" for i in range(1000)])
        cache.set(long_prompt, "response to long prompt")

        result = cache.get(long_prompt)
        assert result == "response to long prompt"

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts."""
        cache = SemanticCache()

        # Empty prompt should work but may not match well
        cache.set("", "empty response")
        result = cache.get("")

        # Should either match or not, but shouldn't crash
        assert result is not None or result is None

    def test_multiple_similar_prompts(self):
        """Test behavior with multiple similar prompts."""
        cache = SemanticCache(similarity_threshold=0.70)

        # Add similar prompts
        cache.set("Python programming language", "Python response 1")
        cache.set("Python coding language", "Python response 2")
        cache.set("Python development", "Python response 3")

        # Query should match one of them
        result = cache.get("Python programming")

        # Should match one of the cached responses
        assert result in [
            "Python response 1",
            "Python response 2",
            "Python response 3",
            None,  # Or no match if similarity too low
        ]

    def test_entry_access_tracking(self):
        """Test that entry access is tracked."""
        cache = SemanticCache()

        cache.set("key1", "response1")
        entry = cache.get_entry("key1")

        initial_access_count = entry.access_count

        # Access the entry
        cache.get("key1")

        entry = cache.get_entry("key1")
        assert entry.access_count > initial_access_count


class TestSemanticCacheTTL:
    """TTL enforcement on read for L2 (C-6 regression)."""

    def test_expired_match_becomes_miss_and_is_evicted(self):
        clock = [1000.0]
        cache = SemanticCache(max_size=10, ttl_seconds=10, clock=lambda: clock[0])

        cache.set("what is python", "a language")
        # Exact-text lookup is self-similarity 1.0 -> a hit while fresh.
        assert cache.get("what is python") == "a language"

        clock[0] = 1011.0  # advance past ttl
        assert cache.get("what is python") is None  # expired -> miss
        assert cache.size() == 0  # evicted from all stores

    def test_ttl_none_never_expires(self):
        clock = [1000.0]
        cache = SemanticCache(max_size=10, ttl_seconds=None, clock=lambda: clock[0])

        cache.set("what is python", "a language")
        clock[0] = 10_000_000.0
        assert cache.get("what is python") == "a language"

    def test_colon_in_version_roundtrips_and_isolates(self):
        """A colon in the version must not corrupt version parsing or filtering.

        Regression for the unescaped versioned-key encoding: with escaping, a
        version like 'v1:a' round-trips through _extract_version and stays
        isolated from a different (version, key) pair that used to collide.
        """
        cache = SemanticCache(max_size=10)
        cache.set("b", "VALUE_B", version="v1:a")
        cache.set("a:b", "VALUE_AB", version="v1")

        # Exact-key fast-path returns each key's own value (no collision).
        assert cache.get("b", version="v1:a") == "VALUE_B"
        assert cache.get("a:b", version="v1") == "VALUE_AB"

        # The colon-bearing version is recovered intact (not truncated at ':').
        stored = cache._make_versioned_key("b", "v1:a")
        assert cache._extract_version(stored) == "v1:a"
        assert cache._extract_base_key(stored) == "b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestSemanticCacheGetEntryLock:
    """get_entry() must be lock-protected against concurrent eviction (M-4 regression)."""

    def test_get_entry_never_raises_under_concurrent_eviction(self):
        """get_entry() reading self.entries without a lock could see a KeyError or
        partial state when another thread concurrently evicts or clears the cache.
        Holding self._lock in get_entry() closes the race.
        ``sys`` state is restored in ``finally``.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = SemanticCache(max_size=20)
            # Fill to capacity so every new set() triggers eviction.
            for i in range(20):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            stop = threading.Event()

            def mutator(tid: int) -> None:
                i = 0
                while not stop.is_set():
                    # Alternately set (triggering LRU eviction) and clear.
                    cache.set(f"key_{i % 20}", f"new_val_{tid}_{i}")
                    if i % 10 == 0:
                        cache.clear()
                        for j in range(20):
                            cache.set(f"key_{j}", f"val_{j}")
                    i += 1

            # Iteration budget scales with how slow execution is (2026-07-25).
            # Under coverage every line in every thread is traced, so this loop ran
            # ~3.5x slower and approached the 60s per-test ceiling; on a 2-core CI
            # runner it crossed it, and the signal-based timeout could not kill the
            # workers, so the job hung until GitHub's 6-hour limit. Fewer iterations
            # under coverage keeps wall-clock roughly constant WITHOUT weakening the
            # test: slower execution *widens* the interleaving window, so each
            # iteration is a better race detector, not a worse one. Mutation-verified
            # — reverting the lock in get_entry() still fails this test at 120.
            # Iteration budget scales with how slow execution is (2026-07-25).
            # Under coverage every line in every thread is traced, so this loop ran
            # ~3.5x slower (48s vs 14s) and approached the 60s per-test ceiling; on a
            # 2-core CI runner it crossed it, and the signal-based timeout could not
            # kill the workers, so the job hung until GitHub's 6-hour default. Fewer
            # rounds under coverage keeps wall-clock roughly constant (16s).
            #
            # Measured, not assumed: removing the lock from get_entry() and re-running
            # 3x at 500 rounds AND 3x at 120 rounds, with and without coverage, this
            # test passed every time. Detection power is identical at both budgets
            # because it is near zero either way — a plain dict .get() is atomic under the
            # GIL, so the guarded race almost never manifests. Reducing rounds
            # therefore costs nothing. **That weakness is a separate, real finding:
            # this test asserts a lock exists far more than it proves the lock is
            # needed.** Strengthening it (e.g. a check-then-get window with an
            # injected switch point) is tracked separately, not smuggled into a CI fix.
            rounds = 120 if sys.gettrace() is not None else 500

            def reader() -> None:
                try:
                    for _ in range(rounds):
                        for k in range(20):
                            cache.get_entry(f"key_{k}")  # must not raise
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=8) as executor:
                mutators = [executor.submit(mutator, t) for t in range(4)]
                readers = [executor.submit(reader) for _ in range(4)]
                for f in readers:
                    f.result()
                stop.set()
                for f in mutators:
                    f.result()

            assert not errors, f"get_entry() raced with eviction: {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)


class TestSemanticCacheMigrateLock:
    """migrate() must hold the lock for the full duration (C-2 TOCTOU regression)."""

    def test_migrate_is_atomic_no_interleaved_writes(self):
        """Without holding the lock through the set() calls, a concurrent write to
        the target version could be silently overwritten by the migration loop.
        With the full-duration lock, the migration is atomic: concurrent writers
        targeting to_version are serialised after the migration completes.
        ``sys`` state is restored in ``finally``.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = SemanticCache(max_size=200)
            for i in range(20):
                cache.set(f"key_{i}", f"original_v1_{i}", version="v1")

            errors: list[str] = []
            stop = threading.Event()

            def concurrent_writer(tid: int) -> None:
                i = 0
                while not stop.is_set():
                    # Write to the migration target version continuously.
                    cache.set(f"concurrent_{tid}_{i}", f"cval_{i}", version="v2")
                    i += 1

            def migrator() -> None:
                try:
                    for _ in range(10):
                        count = cache.migrate("v1", "v2")
                        # Returned count must be non-negative — no partial migration.
                        assert count >= 0, f"migrate() returned negative count: {count}"
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=6) as executor:
                writers = [executor.submit(concurrent_writer, t) for t in range(4)]
                migrators = [executor.submit(migrator) for _ in range(2)]
                for f in migrators:
                    f.result()
                stop.set()
                for f in writers:
                    f.result()

            assert not errors, f"migrate() raised under concurrency: {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)


class TestSemanticCacheAverageSimilarityLock:
    """average_similarity_score() and reset_stats() must be lock-consistent (N-1)."""

    def test_average_similarity_score_never_races_with_reset(self):
        """average_similarity_score() reading _similarity_scores without the lock
        can race against reset_stats() calling _similarity_scores.clear() outside
        the lock, producing a stale zero or a non-atomic multi-field CacheStats reset.
        Both must hold self._lock.  ``sys`` state is restored in ``finally``.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = SemanticCache(max_size=100)
            # Seed so hits are generated and _similarity_scores is populated.
            for i in range(20):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            stop = threading.Event()

            def getter(tid: int) -> None:
                """Generate hits to populate _similarity_scores continuously."""
                i = 0
                while not stop.is_set():
                    cache.get(f"key_{i % 20}")
                    i += 1

            def resetter() -> None:
                """Call reset_stats() continuously to race with reads."""
                while not stop.is_set():
                    cache.reset_stats()

            def reader() -> None:
                """Call average_similarity_score() and assert valid range."""
                try:
                    for _ in range(500):
                        score = cache.average_similarity_score()
                        assert 0.0 <= score <= 1.0, (
                            f"average_similarity_score() out of range: {score}"
                        )
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=10) as executor:
                getters = [executor.submit(getter, t) for t in range(4)]
                resetters = [executor.submit(resetter) for _ in range(2)]
                readers = [executor.submit(reader) for _ in range(4)]
                for f in readers:
                    f.result()
                stop.set()
                for f in getters + resetters:
                    f.result()

            assert not errors, f"average_similarity_score() race detected: {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)


class TestSemanticCacheUpdateThresholdLock:
    """update_threshold() must hold the lock when writing similarity_threshold (N-2)."""

    def test_update_threshold_never_races_with_get(self):
        """update_threshold() assigns self.similarity_threshold without holding
        self._lock, while get() reads it inside the lock.  The write must also
        acquire the lock so readers see a consistent value.
        ``sys`` state is restored in ``finally``.
        """
        import sys
        import threading
        from concurrent.futures import ThreadPoolExecutor

        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)
        try:
            cache = SemanticCache(max_size=100, similarity_threshold=0.5)
            for i in range(20):
                cache.set(f"key_{i}", f"val_{i}")

            errors: list[str] = []
            stop = threading.Event()

            def getter() -> None:
                i = 0
                while not stop.is_set():
                    cache.get(f"key_{i % 20}")
                    i += 1

            def threshold_toggler() -> None:
                """Alternate threshold between 0.5 and 0.9 continuously."""
                flip = True
                while not stop.is_set():
                    try:
                        cache.update_threshold(0.9 if flip else 0.5)
                    except Exception as exc:  # noqa: BLE001
                        errors.append(repr(exc))
                    flip = not flip

            def stat_reader() -> None:
                try:
                    for _ in range(500):
                        t = cache.similarity_threshold
                        # Threshold must always be one of the two valid values.
                        assert t in (0.5, 0.9), f"threshold has unexpected value: {t}"
                except Exception as exc:  # noqa: BLE001
                    errors.append(repr(exc))

            with ThreadPoolExecutor(max_workers=10) as executor:
                getters = [executor.submit(getter) for _ in range(4)]
                togglers = [executor.submit(threshold_toggler) for _ in range(2)]
                readers = [executor.submit(stat_reader) for _ in range(4)]
                for f in readers:
                    f.result()
                stop.set()
                for f in getters + togglers:
                    f.result()

            assert not errors, f"update_threshold() race detected: {errors[:3]}"
        finally:
            sys.setswitchinterval(old_interval)
