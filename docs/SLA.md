# Service Level Agreement (SLA) — Token Optimization System

**Version:** 1.0  
**Effective date:** 2026-07-18  
**Status:** Active  
**Scope:** `bob-optimize` CLI / `TokenOptimizer` facade and sub-components  
**Deployment target:** Local Python library (single-machine, local-only, no network service)

---

## Deployment context

The Token Optimization System is a **local library and CLI**, not a network service.
It has no uptime SLA, no concurrent-user model, and no on-call rotation.
The SLAs below are **latency and throughput targets** for a single-operator workstation
running on developer-class hardware (Apple M3 Pro or equivalent x86 laptop, Python 3.11+).

> Formal uptime / availability SLAs are explicitly **not claimed** here. See [`STATUS.md`](STATUS.md).

---

## Latency SLAs

All targets are **p99 wall-clock latency** measured from API call to return value on a
warm process (model and cache initialized). "Warm" means the `TokenOptimizer` has been
instantiated and at least one request processed; cold-start initialization is excluded
from all latency targets.

### Cache Layer

| Operation | p99 Target | Measured baseline (M3 Pro) | Notes |
|---|---|---|---|
| L1 exact-cache hit | ≤ 750 µs | 144 µs | O(1) dict lookup; includes Python call overhead |
| L1 exact-cache miss | ≤ 300 µs | 61 µs | Hash miss + fallthrough |
| L1 eviction (LRU) | ≤ 360 µs | 71 µs | OrderedDict pop + insert |
| L2 semantic hit (50 entries) | ≤ 4.5 ms | 1.5 ms | Cosine scan over 50 vectors |
| L2 semantic hit (200 entries) | ≤ 1.5 ms | 484 µs | Cosine scan over 200 vectors |
| MultiLevel cache L1 hit | ≤ 750 µs | 164 µs | L1 hit; L2 not reached |
| MultiLevel cache full miss | ≤ 1.3 ms | 428 µs | L1 + L2 miss |

### Token Counting

| Input size | p99 Target | Measured baseline | Notes |
|---|---|---|---|
| Empty string | ≤ 165 µs | 33 µs | tiktoken BPE warm |
| ~100 tokens | ≤ 180 µs | 36 µs | Typical short prompt |
| ~1 000 tokens | ≤ 1.8 ms | 366 µs | Medium document |
| ~10 000 tokens | ≤ 13 ms | 2.6 ms | Large context |

### Prompt Optimization

| Scenario | p99 Target | Measured baseline | Notes |
|---|---|---|---|
| Simple prompt | ≤ 7.5 ms | 1.5 ms | Tokenize + rule pass |
| Complex prompt | ≤ 3.5 ms | 707 µs | Multi-paragraph |
| Cache-hit pipeline | ≤ 750 µs | 151 µs | Full facade, L1 hit |
| Cold pipeline (no cache) | ≤ 3.5 ms | 695 µs | Full facade, L1+L2 miss |

---

## Throughput SLAs

| Scenario | Minimum throughput | Notes |
|---|---|---|
| Sustained single-threaded optimize | ≥ 50 req/s | p50 < 20 ms per request |
| Concurrent optimize (4 threads) | ≥ 100 req/s combined | Thread-safe under RLock |
| Sustained optimize (60 s soak) | ≥ 50 req/s, p99 ≤ 100 ms | No degradation over time |
| Cache fill (1 000 entries) | ≤ 2 s total | Bulk L1 population |

---

## Quality SLAs

| Metric | Target | Measured (N=183, 2026-07-14) |
|---|---|---|
| Lossless compression savings | ≥ 15% mean | 20.0% mean (95% CI [18.9%, 21.2%]) — manifest: `evaluation/results/validation-2026-07-14/manifest.json` |
| Null-test pass (shuffled input savings < threshold) | Must pass | PASS |
| tiktoken active (not estimated) | Always | PASS |

Quality provenance: `evaluation/results/validation-2026-07-14/manifest.json` (data hash, code SHA, config, seed)

---

## Concurrency SLAs

The cache layer uses `threading.RLock` for thread safety. Targets:

| Scenario | Target | Notes |
|---|---|---|
| 4 concurrent writers, L1 cache | No deadlock, no corruption | RLock is reentrant-safe |
| 4 concurrent readers + 1 writer | No starvation within 100 ms | Writer priority not guaranteed |
| Post-soak cache integrity | All written keys retrievable (≤5% miss allowed) | Entries evicted correctly, no phantom hits |

---

## What is NOT covered by this SLA

- Windows operating system (not tested in CI — planned for next release)
- Real-LLM API call latency (network-bound; outside library scope)
- Cold-start initialization time (`TokenOptimizer()` constructor, ~2 s with MiniLM model load)
- Batch operations beyond 1 000 items per call
- Memory-constrained environments (< 512 MB RAM)

---

## Measurement methodology

All latency baselines were measured using `pytest-benchmark` (5.2.3) on:
- **Hardware:** Apple M3 Pro (Darwin arm64, P-cores 4.05 GHz)
- **Python:** 3.12.10, CPython
- **Process state:** warm (≥ 1 prior request)
- **Thresholds:** measured `stats.max` (approx p99) × 3–5× safety margin

Load and soak targets are verified by `tests/load/test_load_soak.py`, run via
`pytest tests/load/ -v`. Results are informational on CI (not blocking) and
asserting on local developer hardware.

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-18 | Initial SLA v1.0 — latency, throughput, quality, concurrency targets defined |
