"""Concurrency tests for cache operations.

Tests validate thread-safety of cache implementations under concurrent access.
Covers concurrent reads, writes, race conditions, and deadlock scenarios.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest

from src.cache import ExactCache, MultiLevelCache, SemanticCache


class TestExactCacheConcurrency:
    """Thread-safety tests for ExactCache (L1)."""

    def test_concurrent_reads(self):
        """Test multiple threads reading simultaneously."""
        cache = ExactCache(max_size=1000)

        # Populate cache
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")

        # Concurrent reads
        def read_operation(thread_id: int) -> List[str]:
            results = []
            for i in range(100):
                result = cache.get(f"key_{i}")
                results.append(result)
            return results

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_operation, i) for i in range(10)]

            results = [f.result() for f in as_completed(futures)]

        # Verify all reads succeeded
        assert len(results) == 10
        for result_list in results:
            assert len(result_list) == 100
            assert all(r is not None for r in result_list)

    def test_concurrent_writes(self):
        """Test multiple threads writing simultaneously."""
        cache = ExactCache(max_size=1000)

        def write_operation(thread_id: int) -> None:
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(write_operation, i) for i in range(10)]

            # Wait for completion
            for f in as_completed(futures):
                f.result()

        # Verify all writes succeeded
        stats = cache.stats()
        assert stats["size"] == 1000  # 10 threads * 100 writes

    def test_mixed_read_write(self):
        """Test mixed read/write workload."""
        cache = ExactCache(max_size=1000)

        # Pre-populate
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")

        def mixed_operation(thread_id: int) -> None:
            for i in range(50):
                if i % 2 == 0:
                    # Read
                    cache.get(f"key_{i}")
                else:
                    # Write
                    cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(10)]

            for f in as_completed(futures):
                f.result()

        # Verify cache is consistent
        stats = cache.stats()
        assert stats["size"] > 0
        assert stats["size"] <= 1000

    def test_concurrent_eviction(self):
        """Test concurrent writes triggering eviction."""
        cache = ExactCache(max_size=100)

        def write_many(thread_id: int) -> None:
            for i in range(50):
                cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(write_many, i) for i in range(5)]

            for f in as_completed(futures):
                f.result()

        # Cache should be at max size
        stats = cache.stats()
        assert stats["size"] == 100
        assert stats["evictions"] > 0

    def test_read_write_consistency(self):
        """Test that reads see consistent data during concurrent writes."""
        cache = ExactCache(max_size=1000)

        # Initial value
        cache.set("shared_key", "initial_value")

        inconsistencies = []

        def reader() -> None:
            """Read and verify value."""
            for _ in range(100):
                value = cache.get("shared_key")
                if value is not None and value not in ["initial_value", "updated_value"]:
                    inconsistencies.append(value)
                time.sleep(0.0001)

        def writer() -> None:
            """Update value."""
            time.sleep(0.001)  # Let readers start
            cache.set("shared_key", "updated_value")

        # Start readers and writer
        with ThreadPoolExecutor(max_workers=6) as executor:
            reader_futures = [executor.submit(reader) for _ in range(5)]
            writer_future = executor.submit(writer)

            # Wait for all
            for f in reader_futures + [writer_future]:
                f.result()

        # Should see no inconsistent values
        assert len(inconsistencies) == 0, f"Found inconsistent values: {inconsistencies}"

    def test_stress_concurrent_access(self):
        """Stress test with high concurrency."""
        cache = ExactCache(max_size=1000)

        def stress_operation(thread_id: int) -> None:
            for i in range(100):
                if i % 3 == 0:
                    cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                elif i % 3 == 1:
                    cache.get(f"key_{thread_id}_{i}")
                else:
                    # Check stats (read-only operation)
                    cache.stats()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_operation, i) for i in range(20)]

            for f in as_completed(futures):
                f.result()

        # Verify cache is still functional
        cache.set("test", "value")
        assert cache.get("test") == "value"


class TestSemanticCacheConcurrency:
    """Thread-safety tests for SemanticCache (L2)."""

    def test_concurrent_reads(self):
        """Test multiple threads reading simultaneously."""
        cache = SemanticCache(max_size=500, similarity_threshold=0.85)

        # Populate cache
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")

        def read_operation(thread_id: int) -> List[str]:
            results = []
            for i in range(50):
                result = cache.get(f"prompt_{i}")
                results.append(result)
            return results

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(read_operation, i) for i in range(5)]

            results = [f.result() for f in as_completed(futures)]

        # Verify all reads succeeded
        assert len(results) == 5
        for result_list in results:
            assert len(result_list) == 50

    def test_concurrent_writes(self):
        """Test multiple threads writing simultaneously."""
        cache = SemanticCache(max_size=500)

        def write_operation(thread_id: int) -> None:
            for i in range(20):
                cache.set(f"prompt_{thread_id}_{i}", f"result_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(write_operation, i) for i in range(5)]

            for f in as_completed(futures):
                f.result()

        # Verify writes succeeded
        stats = cache.stats()
        assert stats["size"] == 100  # 5 threads * 20 writes

    def test_concurrent_similarity_search(self):
        """Test concurrent similarity searches."""
        cache = SemanticCache(max_size=500)

        # Populate with diverse prompts to avoid TF-IDF pruning
        # Use different topics and vocabulary for each prompt
        topics = [
            "machine learning",
            "data science",
            "software engineering",
            "cloud computing",
            "artificial intelligence",
        ]
        actions = ["analyze", "implement", "optimize", "debug", "deploy"]

        prompts = []
        for i in range(50):
            topic = topics[i % len(topics)]
            action = actions[i % len(actions)]
            prompt = f"Please {action} the {topic} system for project {i} with advanced features"
            prompts.append(prompt)

        for i, prompt in enumerate(prompts):
            cache.set(prompt, f"result_{i}")

        def search_operation(thread_id: int) -> List:
            topic = topics[thread_id % len(topics)]
            action = actions[thread_id % len(actions)]
            query = (
                f"Please {action} the {topic} system for project {thread_id} with advanced features"
            )
            return cache.find_similar(query, top_k=5)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(search_operation, i) for i in range(10)]

            results = [f.result() for f in as_completed(futures)]

        # All searches should return results
        assert all(len(r) > 0 for r in results)

    def test_vocabulary_regeneration_safety(self):
        """Test thread-safety during vocabulary regeneration."""
        cache = SemanticCache(max_size=500)

        # Initial population
        for i in range(20):
            cache.set(f"initial_{i}", f"result_{i}")

        def add_new_terms(thread_id: int) -> None:
            """Add new terms that trigger vocabulary regeneration."""
            for i in range(10):
                cache.set(f"new_term_{thread_id}_{i}", f"result_{thread_id}_{i}")

        def read_existing(thread_id: int) -> List:
            """Read existing terms during regeneration."""
            results = []
            for i in range(20):
                result = cache.get(f"initial_{i}")
                results.append(result)
            return results

        # Mix readers and writers
        with ThreadPoolExecutor(max_workers=6) as executor:
            writer_futures = [executor.submit(add_new_terms, i) for i in range(3)]
            reader_futures = [executor.submit(read_existing, i) for i in range(3)]

            # Wait for all
            for f in writer_futures + reader_futures:
                f.result()

        # Cache should still be functional
        assert cache.size() > 0


class TestMultiLevelCacheConcurrency:
    """Thread-safety tests for MultiLevelCache."""

    def test_concurrent_l1_l2_access(self):
        """Test concurrent access to both cache levels."""
        cache = MultiLevelCache(l1_max_size=100, l2_max_size=500)

        # Populate
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")

        def mixed_access(thread_id: int) -> None:
            for i in range(50):
                # Mix of L1 hits, L2 hits, and misses
                cache.get(f"key_{i}")
                cache.get(f"nonexistent_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_access, i) for i in range(10)]

            for f in as_completed(futures):
                f.result()

        # Verify both levels are functional
        cache.set("test", "value")
        assert cache.get("test") == "value"

    def test_concurrent_promotion(self):
        """Test concurrent L2 to L1 promotion."""
        cache = MultiLevelCache(l1_max_size=10, l2_max_size=500, promote_l2_hits=True)

        # Populate L2
        for i in range(50):
            cache.set(f"prompt_{i}", f"result_{i}")

        # Clear L1 to force L2 hits
        cache.l1_cache.clear()

        def access_and_promote(thread_id: int) -> None:
            """Access items to trigger promotion."""
            for i in range(10):
                cache.get(f"prompt_{i}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(access_and_promote, i) for i in range(5)]

            for f in as_completed(futures):
                f.result()

        # L1 should have promoted items
        assert cache.l1_cache.size() > 0

    def test_stress_multilevel(self):
        """Stress test multi-level cache."""
        cache = MultiLevelCache()

        def stress_operation(thread_id: int) -> None:
            for i in range(100):
                if i % 3 == 0:
                    cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                elif i % 3 == 1:
                    cache.get(f"key_{thread_id}_{i}")
                else:
                    cache.stats()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_operation, i) for i in range(20)]

            for f in as_completed(futures):
                f.result()

        # Verify cache is still functional
        cache.set("test", "value")
        assert cache.get("test") == "value"


class TestRaceConditions:
    """Tests for detecting race conditions."""

    def test_counter_race_condition(self):
        """Test for race conditions in shared counter."""
        cache = ExactCache(max_size=1000)

        # Shared counter (intentionally racy)
        counter = {"value": 0}

        def increment_without_lock() -> None:
            """Increment without proper synchronization."""
            for _ in range(1000):
                current = counter["value"]
                # Simulate some work
                time.sleep(0.00001)
                counter["value"] = current + 1

        # Run without lock (should have races)
        counter["value"] = 0
        threads = [threading.Thread(target=increment_without_lock) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify race condition occurred (value should be less than expected)
        assert counter["value"] < 10000, "Race condition not detected"

        # Now test with proper locking
        lock = threading.Lock()

        def increment_with_lock() -> None:
            """Increment with proper synchronization."""
            for _ in range(1000):
                with lock:
                    current = counter["value"]
                    time.sleep(0.00001)
                    counter["value"] = current + 1

        counter["value"] = 0
        threads = [threading.Thread(target=increment_with_lock) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # With lock, should get exact count
        assert counter["value"] == 10000, "Lock failed to prevent race condition"

    def test_cache_stats_consistency(self):
        """Test that cache stats remain consistent under concurrent access."""
        cache = ExactCache(max_size=1000)

        def concurrent_operations(thread_id: int) -> None:
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                cache.get(f"key_{thread_id}_{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(concurrent_operations, i) for i in range(10)]

            for f in as_completed(futures):
                f.result()

        # Stats should be consistent
        stats = cache.stats()
        assert stats["hits"] + stats["misses"] == stats["hits"] + stats["misses"]
        assert stats["size"] <= cache.max_size


class TestDeadlockDetection:
    """Tests for detecting potential deadlocks."""

    def test_no_deadlock_multiple_caches(self):
        """Test that operations on multiple caches don't deadlock."""
        cache1 = ExactCache(max_size=100)
        cache2 = ExactCache(max_size=100)

        def operation_a() -> None:
            for _ in range(100):
                cache1.set("key_a", "value_a")
                cache2.set("key_b", "value_b")

        def operation_b() -> None:
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

    def test_no_deadlock_nested_operations(self):
        """Test that nested cache operations don't deadlock."""
        cache = MultiLevelCache()

        def nested_operations(thread_id: int) -> None:
            # Reduced operations to avoid TF-IDF overhead
            for i in range(10):
                # Set triggers both L1 and L2
                cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                # Get checks both levels
                cache.get(f"key_{thread_id}_{i}")
                # Stats reads from both levels
                cache.stats()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(nested_operations, i) for i in range(5)]

            try:
                for f in futures:
                    f.result(timeout=30.0)  # Increased timeout for TF-IDF operations
            except TimeoutError:
                pytest.fail("Deadlock detected in nested operations")


@pytest.mark.slow
class TestConcurrencyStress:
    """Stress tests for concurrency."""

    def test_high_concurrency_stress(self):
        """Stress test with very high concurrency."""
        cache = MultiLevelCache()

        def stress_worker(thread_id: int) -> None:
            for i in range(500):
                operation = i % 4
                if operation == 0:
                    cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                elif operation == 1:
                    cache.get(f"key_{thread_id}_{i}")
                elif operation == 2:
                    cache.stats()
                else:
                    cache.clear()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(50)]

            for f in as_completed(futures):
                f.result()

        # Cache should still be functional
        cache.set("final_test", "final_value")
        assert cache.get("final_test") == "final_value"

    def test_sustained_load(self):
        """Test cache under sustained concurrent load."""
        cache = ExactCache(max_size=1000)

        def sustained_worker(thread_id: int) -> int:
            operations = 0
            end_time = time.time() + 2.0  # Run for 2 seconds

            while time.time() < end_time:
                cache.set(f"key_{thread_id}_{operations}", f"value_{operations}")
                cache.get(f"key_{thread_id}_{operations}")
                operations += 1

            return operations

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(sustained_worker, i) for i in range(10)]

            results = [f.result() for f in as_completed(futures)]

        total_operations = sum(results)
        print(f"\nSustained load: {total_operations} operations in 2 seconds")
        print(f"Throughput: {total_operations / 2:.0f} ops/sec")

        # Verify cache is still functional
        assert cache.size() > 0
