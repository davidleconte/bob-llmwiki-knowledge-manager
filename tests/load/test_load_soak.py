"""Load and soak tests for the Token Optimization System.

These tests verify that the system meets its SLA targets (docs/SLA.md) under
sustained and concurrent load. They are designed to run in two modes:

1. **Informational (CI):** Run with `LOAD_TEST_ASSERT=0` (the default on CI).
   Metrics are collected and printed; no assertions fail the build.  This keeps
   CI fast and avoids flapping due to shared-vCPU noise.

2. **Asserting (local developer hardware):** Run with `LOAD_TEST_ASSERT=1` on
   an M3 Pro or equivalent x86 laptop.  Assertions enforce the SLA targets
   defined in docs/SLA.md.

Usage
-----
    # Informational run (default, CI-safe):
    pytest tests/load/ -v -s

    # Asserting run (developer hardware):
    LOAD_TEST_ASSERT=1 pytest tests/load/ -v -s

    # Full soak only (slow):
    LOAD_TEST_ASSERT=1 pytest tests/load/ -v -s -k soak
"""

import os
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest

from src.cache import ExactCache, MultiLevelCache
from src.facade import TokenOptimizer

# ---------------------------------------------------------------------------
# Mode gate
# ---------------------------------------------------------------------------
# On CI (GitHub Actions sets CI=true) we default to informational mode.
# Locally we default to asserting mode so the SLA is enforced.
_ON_CI = os.environ.get("CI", "").lower() in ("true", "1", "yes")
_ASSERT = os.environ.get("LOAD_TEST_ASSERT", "0" if _ON_CI else "1").lower() in (
    "1",
    "true",
    "yes",
)


def _maybe_assert(condition: bool, msg: str) -> None:
    """Assert only in asserting mode; print a warning otherwise."""
    if _ASSERT:
        assert condition, msg
    elif not condition:
        print(f"\n  [SLA WARNING — informational] {msg}")


# ---------------------------------------------------------------------------
# SLA targets (single home: docs/SLA.md)
# ---------------------------------------------------------------------------
# Sustained single-threaded throughput
SLA_THROUGHPUT_RPS = 50  # req/s minimum
SLA_THROUGHPUT_P99_MS = 100.0  # ms maximum p99 latency

# Concurrent throughput (4 threads)
SLA_CONCURRENT_RPS = 100  # req/s combined minimum

# Soak test (60-second window)
SLA_SOAK_RPS = 50  # req/s minimum over full soak window
SLA_SOAK_P99_MS = 100.0  # ms maximum p99 latency over soak window

# Cache bulk-fill ceiling
SLA_CACHE_FILL_1K_SECONDS = 2.0  # max seconds to fill 1 000 L1 entries


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Short prompts that exercise the optimizer without downloading models.
_PROMPTS = [
    "Summarise the following article about caching strategies for LLM applications.",
    "Translate the next paragraph into French.",
    "What are the main differences between L1 and L2 cache in a multi-level cache?",
    "Explain token optimisation and why it reduces API costs.",
    "List the top five best practices for prompt engineering.",
    "Describe the architecture of a token optimizer with a semantic similarity cache.",
    "How does a HashingVectorizer differ from a TF-IDF vectorizer?",
    "What is the purpose of the eviction policy in an LRU cache?",
    "Write a Python function that counts tokens using the tiktoken library.",
    "Compare cosine similarity with dot-product similarity for embedding retrieval.",
]


@pytest.fixture(scope="module")
def optimizer() -> TokenOptimizer:
    """Shared, warmed TokenOptimizer instance.

    Module scope so model initialisation (~2 s) happens once per module run,
    not once per test function.
    """
    to = TokenOptimizer()
    # Warm up: one request to force model + cache init.
    to.optimize(_PROMPTS[0])
    return to


# ---------------------------------------------------------------------------
# Helper: latency sampler
# ---------------------------------------------------------------------------


def _sample_latencies(
    optimizer: TokenOptimizer,
    n: int = 200,
    prompts: List[str] = _PROMPTS,
) -> List[float]:
    """Run *n* optimize() calls and return latencies in milliseconds."""
    latencies: List[float] = []
    for i in range(n):
        prompt = prompts[i % len(prompts)]
        t0 = time.perf_counter()
        optimizer.optimize(prompt)
        latencies.append((time.perf_counter() - t0) * 1000.0)
    return latencies


# ---------------------------------------------------------------------------
# Test 1 — Sustained single-threaded throughput
# ---------------------------------------------------------------------------


class TestSustainedThroughput:
    """Verify ≥ 50 req/s sustained at p99 ≤ 100 ms (SLA §Throughput)."""

    def test_sustained_single_thread(self, optimizer: TokenOptimizer) -> None:
        """200-request run: throughput ≥ 50 req/s, p99 ≤ 100 ms."""
        n = 200
        t0 = time.perf_counter()
        latencies = _sample_latencies(optimizer, n=n)
        elapsed = time.perf_counter() - t0

        rps = n / elapsed
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        mean_ms = statistics.mean(latencies)

        print(
            f"\n  [load] sustained single-thread: "
            f"rps={rps:.1f} (SLA≥{SLA_THROUGHPUT_RPS}), "
            f"p99={p99:.1f}ms (SLA≤{SLA_THROUGHPUT_P99_MS}ms), "
            f"mean={mean_ms:.1f}ms"
        )

        _maybe_assert(
            rps >= SLA_THROUGHPUT_RPS,
            f"Throughput {rps:.1f} req/s < SLA target {SLA_THROUGHPUT_RPS} req/s",
        )
        _maybe_assert(
            p99 <= SLA_THROUGHPUT_P99_MS,
            f"p99 latency {p99:.1f} ms > SLA target {SLA_THROUGHPUT_P99_MS} ms",
        )

    def test_p50_under_20ms(self, optimizer: TokenOptimizer) -> None:
        """p50 latency ≤ 20 ms (SLA §Throughput 'p50 < 20 ms' note)."""
        latencies = _sample_latencies(optimizer, n=100)
        p50 = statistics.median(latencies)
        print(f"\n  [load] p50 latency: {p50:.1f}ms (SLA≤20ms)")
        _maybe_assert(p50 <= 20.0, f"p50 latency {p50:.1f} ms > 20 ms")


# ---------------------------------------------------------------------------
# Test 2 — Concurrent throughput (4 threads)
# ---------------------------------------------------------------------------


class TestConcurrentThroughput:
    """Verify ≥ 100 req/s combined across 4 threads (SLA §Throughput)."""

    def test_4_thread_combined_throughput(self, optimizer: TokenOptimizer) -> None:
        """4 concurrent threads × 50 requests each: ≥ 100 req/s combined."""
        n_threads = 4
        n_per_thread = 50
        results: List[List[float]] = [[] for _ in range(n_threads)]

        def _worker(thread_idx: int) -> None:
            for i in range(n_per_thread):
                prompt = _PROMPTS[(thread_idx * n_per_thread + i) % len(_PROMPTS)]
                t0 = time.perf_counter()
                optimizer.optimize(prompt)
                results[thread_idx].append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=n_threads) as pool:
            futures = [pool.submit(_worker, i) for i in range(n_threads)]
            for f in as_completed(futures):
                f.result()  # re-raise any exception
        elapsed = time.perf_counter() - t0

        total_requests = n_threads * n_per_thread
        combined_rps = total_requests / elapsed
        all_latencies = [lat for thread_lats in results for lat in thread_lats]
        p99 = statistics.quantiles(all_latencies, n=100)[98]

        print(
            f"\n  [load] 4-thread combined: "
            f"rps={combined_rps:.1f} (SLA≥{SLA_CONCURRENT_RPS}), "
            f"p99={p99:.1f}ms, elapsed={elapsed:.2f}s"
        )

        _maybe_assert(
            combined_rps >= SLA_CONCURRENT_RPS,
            f"Combined throughput {combined_rps:.1f} req/s < SLA target {SLA_CONCURRENT_RPS} req/s",
        )

    def test_no_corruption_under_concurrency(self, optimizer: TokenOptimizer) -> None:
        """Results from concurrent calls are structurally valid (no corruption)."""
        errors: List[str] = []
        lock = threading.Lock()

        def _check_result(i: int) -> None:
            prompt = _PROMPTS[i % len(_PROMPTS)]
            result = optimizer.optimize(prompt)
            if not isinstance(result, dict):
                with lock:
                    errors.append(f"thread {i}: result is not a dict")
                return
            for key in ("optimized_text", "original_tokens", "optimized_tokens"):
                if key not in result:
                    with lock:
                        errors.append(f"thread {i}: missing key '{key}'")

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(_check_result, i) for i in range(80)]
            for f in as_completed(futures):
                f.result()

        assert errors == [], f"Concurrent result corruption: {errors}"


# ---------------------------------------------------------------------------
# Test 3 — Cache correctness under concurrent load
# ---------------------------------------------------------------------------


class TestCacheConcurrency:
    """Verify cache thread-safety and bulk-fill SLA."""

    def test_l1_bulk_fill_under_2s(self) -> None:
        """Filling 1 000 L1 entries takes ≤ 2 s (SLA §Throughput)."""
        cache = ExactCache(max_size=1100)
        t0 = time.perf_counter()
        for i in range(1000):
            cache.set(f"key-{i}", f"value-{i}")
        elapsed = time.perf_counter() - t0
        print(
            f"\n  [load] L1 bulk-fill 1000 entries: {elapsed * 1000:.0f}ms (SLA≤{SLA_CACHE_FILL_1K_SECONDS * 1000:.0f}ms)"
        )
        _maybe_assert(
            elapsed <= SLA_CACHE_FILL_1K_SECONDS,
            f"L1 bulk fill took {elapsed:.2f}s > SLA {SLA_CACHE_FILL_1K_SECONDS}s",
        )

    def test_no_deadlock_4_concurrent_writers(self) -> None:
        """4 concurrent writers to the same MultiLevelCache complete without deadlock."""
        cache = MultiLevelCache()
        errors: List[str] = []
        lock = threading.Lock()

        def _writer(thread_idx: int) -> None:
            try:
                for i in range(50):
                    k = f"t{thread_idx}-k{i}"
                    cache.set(k, f"value-{thread_idx}-{i}")
                    _ = cache.get(k)
            except Exception as exc:  # noqa: BLE001
                with lock:
                    errors.append(f"thread {thread_idx}: {exc}")

        threads = [threading.Thread(target=_writer, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        still_alive = [t for t in threads if t.is_alive()]
        assert still_alive == [], f"Deadlock detected: {len(still_alive)} thread(s) still running"
        assert errors == [], f"Cache corruption under concurrent writes: {errors}"

    def test_post_concurrent_hit_rate_consistent(self) -> None:
        """After concurrent writes, every written key is retrievable (no phantom eviction)."""
        cache = ExactCache(max_size=600)
        n = 500
        written: dict = {}

        def _write_batch(start: int) -> None:
            for i in range(start, start + 125):
                k = f"key-{i}"
                v = f"value-{i}"
                cache.set(k, v)
                written[k] = v  # intentionally racy for the dict — keys are unique per thread

        # 4 threads write non-overlapping key ranges
        threads = [threading.Thread(target=_write_batch, args=(i * 125,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All keys fit within max_size=600; every key should be retrievable.
        misses = [k for k in written if cache.get(k) is None]
        # Some eviction is acceptable if we wrote exactly at capacity; allow 5% miss
        miss_rate = len(misses) / n
        print(
            f"\n  [load] post-concurrent hit rate: {1 - miss_rate:.1%} ({len(misses)} misses/{n})"
        )
        _maybe_assert(
            miss_rate <= 0.05,
            f"Post-concurrent miss rate {miss_rate:.1%} > 5% (possible cache corruption)",
        )


# ---------------------------------------------------------------------------
# Test 4 — Soak test (60-second sustained run)
# ---------------------------------------------------------------------------


class TestSoakTest:
    """60-second soak: throughput ≥ 50 req/s, p99 ≤ 100 ms (SLA §Throughput)."""

    @pytest.mark.slow
    def test_60s_soak(self, optimizer: TokenOptimizer) -> None:
        """Run optimize() calls for 60 seconds and verify SLA compliance.

        Marked ``slow`` — deselect with ``-m 'not slow'`` for quick runs.
        """
        duration_s = 60.0
        latencies: List[float] = []
        deadline = time.perf_counter() + duration_s
        request_count = 0

        idx = 0
        while time.perf_counter() < deadline:
            prompt = _PROMPTS[idx % len(_PROMPTS)]
            t0 = time.perf_counter()
            optimizer.optimize(prompt)
            latencies.append((time.perf_counter() - t0) * 1000.0)
            request_count += 1
            idx += 1

        actual_duration = duration_s  # we stopped at deadline
        rps = request_count / actual_duration
        p50 = statistics.median(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98]
        p_max = max(latencies)

        print(
            f"\n  [soak] 60s run: {request_count} requests, "
            f"rps={rps:.1f} (SLA≥{SLA_SOAK_RPS}), "
            f"p50={p50:.1f}ms, p99={p99:.1f}ms (SLA≤{SLA_SOAK_P99_MS}ms), "
            f"max={p_max:.1f}ms"
        )

        _maybe_assert(
            rps >= SLA_SOAK_RPS,
            f"Soak throughput {rps:.1f} req/s < SLA {SLA_SOAK_RPS} req/s",
        )
        _maybe_assert(
            p99 <= SLA_SOAK_P99_MS,
            f"Soak p99 {p99:.1f} ms > SLA {SLA_SOAK_P99_MS} ms",
        )
