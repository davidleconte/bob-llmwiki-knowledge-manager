---
title: Cache Thread-Safety Audit — Rounds 1–4 Lessons Learned
category: research
tags: [cache, thread-safety, concurrency, semantic-cache, multi-level-cache, exact-cache, race-condition, regression-testing, cross-class-lock, stats-snapshot]
created: 2026-07-18
updated: 2026-07-18
status: active
priority: P1
branch: fix-multilevel-cache-race
---

# Cache Thread-Safety Audit — Rounds 1–4 Lessons Learned

## Objective

Document the full root-cause analysis, fix strategy, and lessons from two rounds
of cache thread-safety audits on `src/cache/` (branch `fix-multilevel-cache-race`).
These gaps survived the institutional audit and the Phase 2 concurrency hardening
because they required precise GIL-analysis knowledge to spot. This document is the
single compact reference so future sessions do not re-derive from raw source.

---

## Background

The `src/cache/` package contains three cache classes:

| Class | File | Lock mechanism |
|---|---|---|
| `ExactCache` | `src/cache/exact_cache.py` | `_synchronized` decorator wrapping `threading.RLock` |
| `SemanticCache` | `src/cache/semantic_cache.py` | `self._lock = threading.RLock()` |
| `MultiLevelCache` | `src/cache/multi_level_cache.py` | `self._stats_lock = threading.RLock()` (added Round 1) |

Phase 2 (2026-07-13) fixed the first wave of thread-safety issues (RLock deadlock,
`dict.items()` iteration under mutation). A post-Phase-2 audit on the
`fix-multilevel-cache-race` branch found four subsequent waves of subtler races
(Rounds 1–4), each discovered by auditing from scratch after the previous round's
fixes were confirmed green.

---

## Findings

### Round 4 — Cross-class threshold read and `unique_entries` stale snapshot (S-1, S-2, S-3, S-4)

**Root cause:** `stats()` read two values — `self.l2_cache.similarity_threshold` and
`unique_entries` — after the `_stats_lock` block closed, at a different moment in
time than the counter/size snapshots. The threshold read was also unguarded across
class boundaries.

**Specific issues:**

| ID | Class | Method | Issue |
|---|---|---|---|
| S-1 | `MultiLevelCache.stats()` / `SemanticCache` | `stats()` | `self.l2_cache.similarity_threshold` read without `SemanticCache._lock`; concurrent `update_threshold()` races against the read |
| S-2 | `MultiLevelCache` | `stats()` | `self.size()` called after `_stats_lock` released; `unique_entries` is at a different moment than `l1_size` / `l2_size` |
| S-3 | Root directory | — | Stale plan files `cache-race-fixes-plan.md`, `cache-race-fixes-round2-plan.md` superseded by CHANGELOG; deleted |
| S-4 | Root directory | — | `README2.md` orphaned duplicate of `README.md`; deleted |

**Fix patterns (Round 4):**

```python
# S-1: new lock-guarded accessor on SemanticCache
def get_threshold(self) -> float:
    with self._lock:
        return self.similarity_threshold

# MultiLevelCache.stats() uses it instead of direct attribute access
l2_threshold = self.l2_cache.get_threshold()   # ← was: self.l2_cache.similarity_threshold

# S-2: inline key-union computation alongside snapshot_keys() calls already in stats()
unique = len(
    set(self.l1_cache.snapshot_keys())
    | set(self.l1_cache._hash_key(
            self.l2_cache._make_versioned_key(
                self.l2_cache._extract_base_key(k),
                self.l2_cache._extract_version(k))
          )
          for k in self.l2_cache.snapshot_keys())
)
# ← was: "unique_entries": self.size()   (re-read both sub-caches after lock release)
```

**Test evidence:** `TestStatsThresholdAndUniqueEntries` — 3 tests:
- `test_stats_l2_similarity_threshold_via_lock`: round-trip update → stats()
- `test_stats_unique_entries_consistent_with_sizes`: bound check (unique ≤ l1+l2 sum)
- `test_stats_l2_similarity_threshold_race`: concurrent threshold-flip race detector

---

### Round 1 — MultiLevelCache stats lock (Sub-Tasks 1–6)

**Root cause:** `MultiLevelCache` had no lock of its own. Stats counters
(`l1_hits`, `l2_hits`, `misses`, `l3_hits`) were plain `int` fields incremented
in `get()` and `query_l3()` without synchronisation.

**Specific races:**

| ID | Location | Race window |
|---|---|---|
| R-1 | `hit_rate()` / `l1_hit_rate()` / `l2_hit_rate()` | Read-modify-write triple non-atomic under concurrent `get()` |
| R-2 | `stats()` | Multiple counter reads without snapshot → inconsistent totals |
| R-3 | `clear()` / `reset_stats()` | Counters zeroed without lock; concurrent `get()` between sub-cache clear and counter reset produces phantom miss |
| R-4 | `_lookup_times` deque | `sum()` / `len()` across concurrent `append()` → potential `ZeroDivisionError` or incorrect mean |
| R-5 | `enable/disable_promotion()` | Write to `promote_l2_hits` flag without lock |
| R-6 | `reset_stats()` | Missing `l3_hits = 0` reset |

**Fix pattern (Round 1):**
- Added `self._stats_lock = threading.RLock()` to `MultiLevelCache.__init__`
- All counter increments in `get()` / `query_l3()` wrapped in `with self._stats_lock`
- All rate-method reads snapshot locals under `_stats_lock` before computing
- `stats()` snapshots all four counters + deque under `_stats_lock`
- `clear()` and `reset_stats()` acquire `_stats_lock` around resets
- `enable/disable_promotion()` and the `promote_l2_hits` flag read in `stats()` guarded by `_stats_lock`

**Test evidence:** 6 new race-detector regression tests added to
`tests/concurrency/test_cache_concurrency.py` and `tests/cache/test_multi_level_cache.py`.

---

### Round 3 — `get()` promote-flag race and `get_with_level()` stats bypass (O-1, O-2)

**Root cause:** Two issues survived Rounds 1 and 2 because the audit focused on
explicit stat-counter accesses; these were control-flow reads and a silent alternative
code path.

**Specific issues:**

| ID | Class | Method | Issue |
|---|---|---|---|
| O-1 | `MultiLevelCache` | `get()` | `promote_l2_hits` read outside `_stats_lock` after L2 hit; concurrent `enable/disable_promotion()` races between counter increment and promotion decision |
| O-2 | `MultiLevelCache` | `get_with_level()` | Re-implemented two-level lookup without calling `get()`; `l1_hits`/`l2_hits`/`misses`/`_lookup_times` never updated; L2→L1 promotion silently skipped |

**Fix patterns (Round 3):**

```python
# O-1: snapshot flag inside the same _stats_lock block as the counter increment
with self._stats_lock:
    self.l2_hits += 1
    self._lookup_times.append(time.time() - start_time)
    do_promote = self.promote_l2_hits   # ← moved inside the lock

if do_promote and self.l1_enabled:     # ← uses local snapshot, not live field
    ...

# O-2: delegate to self.get(), infer level from counter delta
with self._stats_lock:
    l1_before = self.l1_hits
    l2_before = self.l2_hits

result = self.get(key, version)        # ← all accounting happens inside get()
if result is None:
    return None

with self._stats_lock:
    if self.l1_hits > l1_before:
        return (result, "L1")
    if self.l2_hits > l2_before:
        return (result, "L2")
return (result, "L1")                  # unreachable fallback
```

**Test evidence:** `TestMultiLevelCachePromoteFlagRace` (concurrent flag-flip +
getter, asserts no exceptions and counter consistency) and
`TestGetWithLevelStatsAccounting` (3 deterministic tests: l1_hits, misses,
hit_rate parity with `get()`). Total test count: 1102 → 1106.

---

### Round 2 — SemanticCache residuals and ExactCache snapshot (N-1 through N-5)

**Root cause:** SemanticCache's `_similarity_scores` list and `similarity_threshold`
scalar both had unguarded reads that raced against writes held under `self._lock`.
ExactCache's `stats()` called `self.size()` twice producing a TOCTOU window.

**Specific races:**

| ID | Class | Method | Race window |
|---|---|---|---|
| N-1a | `SemanticCache` | `average_similarity_score()` | Read `_similarity_scores` without lock while `get()` appends inside `self._lock` |
| N-1b | `SemanticCache` | `reset_stats()` | `_similarity_scores.clear()` outside lock; concurrent `get()` appends between clear and lock release leaks score across reset boundary |
| N-2 | `SemanticCache` | `update_threshold()` | Unsynchronised write to `self.similarity_threshold`; `get()` reads inside `self._lock` |
| N-3a | `MultiLevelCache` | `enable/disable_promotion()` | Write to `promote_l2_hits` flag unsynchronised with `stats()` snapshot |
| N-3b | `MultiLevelCache` | `stats()` | `promote_l2_hits` read outside `_stats_lock` block |
| N-4 | `ExactCache` | `stats()` | `self.size()` called twice; eviction between calls → `size > utilization×capacity` contradiction |
| N-5 | `SemanticCache` | `stats()` | Advisory: `self._lock` held when calling `embedding_generator.cache_size()`; comment added warning callers not to re-acquire |

**Fix patterns (Round 2):**

```python
# N-1: average_similarity_score() — snapshot under lock, compute outside
def average_similarity_score(self) -> float:
    with self._lock:
        scores = list(self._similarity_scores)
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

# N-1: reset_stats() — clear under lock, serialise against _finalize_hit() appends
def reset_stats(self) -> None:
    with self._lock:
        self._stats.reset()
        self._similarity_scores.clear()

# N-2: update_threshold() — guard write with self._lock
def update_threshold(self, new_threshold: float) -> None:
    with self._lock:
        self.similarity_threshold = new_threshold

# N-4: ExactCache.stats() — snapshot size() once
def stats(self) -> CacheStats:
    n = self.size()   # single call; both 'size' and 'utilization' derive from n
    ...

# N-4: MultiLevelCache.stats() — snapshot l1_size and l2_size once
def stats(self) -> dict:
    l1_size = self.l1_cache.size()
    l2_size = self.l2_cache.size()
    ...
```

**Test evidence:** 6 additional regression tests covering each race scenario.
Total cache + concurrency tests after both rounds: `tests/cache/` 115 passed +
`tests/concurrency/` 64+ passed.

---

## Why the GIL Does Not Save You Here

A recurring misconception: "Python's GIL makes `+= 1` atomic, so we're fine."

**What the GIL guarantees:** Individual bytecodes execute without pre-emption.
A single `INPLACE_ADD` is safe in isolation.

**What the GIL does NOT guarantee:**

1. **Semantic invariants across multiple reads/writes.** `hit_rate()` reads three
   counters (`l1_hits`, `l2_hits`, `misses`) in sequence. Each individual read is
   GIL-safe. But a thread switch between any two reads leaves the computed rate
   reflecting a mix of old and new values — mathematically invalid.

2. **List snapshot consistency.** `sum(self._scores) / len(self._scores)`: the
   list can be cleared between `sum()` and `len()` by another thread. CPython's
   GIL makes each method call atomic, but the compound expression is not.

3. **Flag/counter pairing.** A flag (`promote_l2_hits`) and a counter that must
   be read together for a consistent snapshot can be separated by a thread switch,
   even though each individual read is GIL-atomic.

**Rule of thumb:** If correctness requires two or more values to be read as a
consistent snapshot, those reads must be wrapped in a single lock acquisition —
regardless of the GIL.

---

## Lock Ordering

The cache classes use two locks. The ordering rule (to prevent deadlock) is:

```
self._lock (SemanticCache)   always acquired BEFORE  self._stats_lock (MultiLevelCache)
```

`MultiLevelCache.stats()` calls `self.l2_cache.average_similarity_score()`, which
acquires `SemanticCache._lock`. At that call point `_stats_lock` is already held.
The advisory comment in `SemanticCache.stats()` documents that `self._lock` must
not be re-acquired by `embedding_generator.cache_size()`.

No current code path inverts this order. Any future change that calls `_stats_lock`
from inside `SemanticCache._lock` would create a deadlock risk and must be reviewed.

---

## Test Strategy Applied

Both rounds used the same discipline:

1. **Regression test first** — write a test that is demonstrably related to the
   race (often using `sys.setswitchinterval(1e-7)` to maximise pre-emption) and
   confirm it would fail before the fix.
2. **Minimal source fix** — change only the synchronisation boundary; no
   behaviour, API, or performance changes.
3. **Full suite green** — `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance`
   must pass at ≥89% coverage with `ruff` and `mypy` clean.

**Test count progression:**

| State | Tests passing |
|---|---|
| Pre-Round-1 | 1 088 |
| Post-Round-1 | 1 096 |
| Post-Round-2 | 1 102 |
| Post-Round-3 | 1 106 |
| Post-Round-4 | 1 109 |

---

## Coverage and Quality Gates (post-fix)

| Gate | Value |
|---|---|
| Total tests | 1 109 passed / 23 skipped |
| Global coverage | 89.6% |
| Delegation package | 84% (floor 70%) |
| ruff | Clean |
| mypy | Clean (0 errors, annotation-unchecked notes only) |
| SLA load tests | All 7 non-soak tests pass (`LOAD_TEST_ASSERT=1`) |

---

## Conclusions

### Recommendations

1. **One lock per stateful class, not per method** — a class with multiple fields
   that must be read as a consistent snapshot needs a single lock guarding all of
   them. Do not add per-field locks; they create inconsistency windows and
   deadlock risk.

2. **Snapshot before compute** — any method that reads two or more guarded fields
   to compute a derived value (rate, average, total) must snapshot all fields under
   the lock in a single block, then compute from the locals outside.

3. **Lock writes to all fields read by `stats()`** — `stats()` is the canary: if
   any field it reads is also written anywhere without the lock, that is a race.
   Treat `stats()` as the authoritative list of "fields that must be guarded".

4. **GIL-atomicity ≠ semantic consistency** — document this distinction in code
   review checklists. The GIL makes individual bytecodes safe; it does not make
   invariants safe.

5. **Advisory lock-order comments are load-bearing** — the N-5 comment in
   `SemanticCache.stats()` is not cosmetic; it is the only thing preventing a
   future maintainer from re-acquiring `self._lock` inside a call that is already
   made with `self._lock` held.

### Next Steps

- [ ] Add a `CONCURRENCY.md` note in `src/cache/` summarising the lock-order rule
      and the snapshot pattern, so the next contributor does not have to re-derive it
- [ ] Run `uv run pytest tests/concurrency/ -v` in CI at normal switch interval;
      consider adding a nightly run with `sys.setswitchinterval(1e-7)` as a canary
- [ ] Consider `@dataclass`-backed stats snapshot objects so `stats()` always
      returns a single consistent read of a frozen snapshot — eliminates the
      snapshot discipline requirement from every future reader

## Sources

- [`src/cache/multi_level_cache.py`](../../../src/cache/multi_level_cache.py) — primary fix target (Rounds 1, 3, 4)
- [`src/cache/semantic_cache.py`](../../../src/cache/semantic_cache.py) — primary fix target (Rounds 2, 4)
- [`src/cache/exact_cache.py`](../../../src/cache/exact_cache.py) — N-4 fix target (Round 2)
- [`tests/concurrency/test_cache_concurrency.py`](../../../tests/concurrency/test_cache_concurrency.py) — race-detector regression tests
- [`tests/cache/test_multi_level_cache.py`](../../../tests/cache/test_multi_level_cache.py) — Rounds 1, 3, 4 regression tests
- [`tests/cache/test_semantic_cache.py`](../../../tests/cache/test_semantic_cache.py) — Round 2 regression tests
- [`CHANGELOG.md`](../../../CHANGELOG.md) — v1.1.0 Fixed section (Rounds 1–4)

## Related Documents

- [Cache Thread-Safety Audit — Round 5 Lessons Learned](./cache-race-fix-round5-2026-07.md)
- [Iterative Audit Methodology — Lessons Learned](./iterative-audit-lessons-2026-07.md)
- [Multi-Level Caching](../concepts/multi-level-caching.md)
- [Multi-Level Caching Architecture Patterns](../concepts/multi-level-caching-architecture-patterns.md)
- [Phase 2 Thread Safety Fixes Complete](./phase2-thread-safety-fixes-complete.md)
- [Phase 2 Concurrency Test Results](./phase2-concurrency-test-results.md)
- [Cache API Reference](../references/cache-api.md)

---
*Last Updated: 2026-07-18*
*Category: Research*
