# Load & Soak Tests

These tests verify that the Token Optimization System meets its SLA targets
under sustained and concurrent load. See [`docs/SLA.md`](../../docs/SLA.md) for
the full SLA specification.

## Files

| File | Purpose |
|---|---|
| `test_load_soak.py` | Sustained throughput, concurrent load, cache concurrency, 60-s soak |

## Running

```bash
# Informational run (always-safe, CI default — no assertions):
pytest tests/load/ -v -s

# Asserting run (developer hardware — enforces SLA targets from docs/SLA.md):
LOAD_TEST_ASSERT=1 pytest tests/load/ -v -s

# Skip the 60-second soak test for a fast sanity check:
LOAD_TEST_ASSERT=1 pytest tests/load/ -v -s -m "not slow"

# Full soak only:
LOAD_TEST_ASSERT=1 pytest tests/load/ -v -s -k soak
```

## Test classes

| Class | SLA target | Requests |
|---|---|---|
| `TestSustainedThroughput` | ≥ 50 req/s, p99 ≤ 100 ms | 200 (single thread) |
| `TestConcurrentThroughput` | ≥ 100 req/s combined | 200 (4 threads × 50) |
| `TestCacheConcurrency` | Bulk fill ≤ 2 s; no deadlock; no corruption | 200–500 entries |
| `TestSoakTest` | ≥ 50 req/s, p99 ≤ 100 ms | ~3 000–6 000 (60 s) |

## CI behaviour

The `load` CI job runs `pytest tests/load/ -v -s -m "not slow"` with
`LOAD_TEST_ASSERT=0` (informational). It reports metrics but never fails the
build due to latency variance on shared vCPUs. The 60-second soak is excluded
from CI (too slow for a PR gate).

Run locally with `LOAD_TEST_ASSERT=1` before merging performance-sensitive changes.
