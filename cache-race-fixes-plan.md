# Cache Race Fixes Plan

**Branch:** `fix-multilevel-cache-race`  
**Scope:** All residual thread-safety and correctness issues in `src/cache/` identified by the 2026-07-18 audit.  
**Non-goals:** No behaviour changes to cache eviction, similarity scoring, or CLI surface. No new public API. No performance regressions below SLA targets.  
**Approach:** One sub-task per issue. Each sub-task adds a failing regression test first, then applies the minimal source fix, then verifies the full suite still passes. All changes stay inside `src/cache/` and `tests/cache/` / `tests/concurrency/`.

---

## Sub-Task 1 — Add `_stats_lock` to `MultiLevelCache` and protect all counter operations

**Status:** `[ ] pending`

**Intent**  
`MultiLevelCache` has no lock of its own. Its four stats counters (`l1_hits`, `l2_hits`, `misses`, `l3_hits`) are plain `int` fields incremented in `get()` and `query_l3()` and read in `hit_rate()`, `l1_hit_rate()`, `l2_hit_rate()`, and `stats()`. The GIL makes individual `+= 1` safe, but the read-modify-write triple in the rate methods is not atomic under concurrent `get()` calls. Additionally, `clear()` and `reset_stats()` zero the counters without holding any lock, so a concurrent `get()` between the clear of sub-caches and the zeroing of counters can produce a phantom miss that is then silently lost.

**Decision:** Add a single `_stats_lock = threading.RLock()` and acquire it around every counter mutation (in `get()`, `query_l3()`) and every counter read (in `hit_rate()`, `l1_hit_rate()`, `l2_hit_rate()`, `stats()`). Counter resets in `clear()` and `reset_stats()` must also be inside the lock.

**Expected Outcomes**
- `MultiLevelCache.__init__` creates `self._stats_lock = threading.RLock()`
- `get()` acquires `_stats_lock` before `self.l1_hits += 1`, `self.l2_hits += 1`, and `self.misses += 1`
- `query_l3()` acquires `_stats_lock` before `self.l3_hits += 1`
- `hit_rate()`, `l1_hit_rate()`, `l2_hit_rate()` snapshot `l1, l2, m = self.l1_hits, self.l2_hits, self.misses` under `_stats_lock` before computing
- `stats()` acquires `_stats_lock` around the `total_requests` block
- `clear()` acquires `_stats_lock` around the four counter resets
- `reset_stats()` acquires `_stats_lock` around the three counter resets (and fixes missing `l3_hits = 0` — see Sub-Task 6)
- A new regression test `test_stats_counters_never_race_with_concurrent_gets` passes and would have failed before the fix
- All 1088 existing tests continue to pass

**Todo List**
1. Write a regression test in `tests/concurrency/test_cache_concurrency.py` inside `TestMultiLevelCacheConcurrency`: spin mutator threads calling `cache.get()` and `cache.set()` concurrently while reader threads call `cache.hit_rate()`, `cache.l1_hit_rate()`, `cache.l2_hit_rate()`, and `cache.stats()` in a loop; use `sys.setswitchinterval(1e-7)` in a `try/finally`; assert no exceptions and that `hit_rate()` returns a value in `[0, 100]`. (Pattern: mirror `test_size_stats_never_race_with_mutation`.)
2. In `src/cache/multi_level_cache.py` `__init__`, add `import threading` (already imported via `typing` chain — verify) and add `self._stats_lock = threading.RLock()` after the existing `_metrics` assignment.
3. Wrap the `self.l1_hits += 1` increment inside `get()` (line 151) in `with self._stats_lock`.
4. Wrap the `self.l2_hits += 1` increment inside `get()` (line 166) in `with self._stats_lock`.
5. Wrap the `self.misses += 1` increment inside `get()` (line 198) in `with self._stats_lock`.
6. Wrap the `self.l3_hits += 1` increment inside `query_l3()` (line 233) in `with self._stats_lock`.
7. Rewrite `hit_rate()` to snapshot counters under `_stats_lock` into local variables before computing the rate.
8. Rewrite `l1_hit_rate()` identically.
9. Rewrite `l2_hit_rate()` identically.
10. In `stats()`, snapshot `l1_hits`, `l2_hits`, `l3_hits`, `misses` under `_stats_lock` into local variables, then compute `total_requests` and all rate fields from those locals.
11. In `clear()`, move the four counter resets inside `with self._stats_lock`.
12. In `reset_stats()`, move the three counter resets inside `with self._stats_lock`.
13. Run `uv run pytest tests/concurrency/ tests/cache/ -q` — must be green.

**Relevant Context**
- `src/cache/multi_level_cache.py`: `__init__` line 57; `get()` lines 132–205; `query_l3()` lines 207–239; `hit_rate()` lines 293–302; `l1_hit_rate()` lines 304–313; `l2_hit_rate()` lines 315–324; `stats()` lines 326–362; `clear()` lines 262–270; `reset_stats()` lines 490–497
- `tests/concurrency/test_cache_concurrency.py`: `test_size_stats_never_race_with_mutation` lines 369–416 — exact pattern to mirror
- `ExactCache._synchronized` decorator in `src/cache/exact_cache.py` lines 24–41 — lock pattern reference
- `SemanticCache._lock` (RLock) in `src/cache/semantic_cache.py` line 81 — lock pattern reference

---

## Sub-Task 2 — Fix `_lookup_times` deque: snapshot before iteration

**Status:** `[ ] pending`

**Intent**  
`MultiLevelCache._lookup_times` is a `deque(maxlen=10_000)` that `get()` appends to on every call (lines 153, 186, 200). `stats()` (line 333) and `average_lookup_time_ms()` (line 438) compute `sum(self._lookup_times) / len(self._lookup_times)` without holding any lock. A concurrent `append()` or `clear()` between the `bool` check, the `sum()`, and the `len()` can cause a `ZeroDivisionError` or an incorrect mean. The fix is to take a snapshot of the deque under the same `_stats_lock` added in Sub-Task 1 before computing.

**Expected Outcomes**
- `stats()` uses `times = list(self._lookup_times)` inside `_stats_lock` then computes from `times`
- `average_lookup_time_ms()` does the same snapshot
- `_lookup_times.append()` in `get()` is inside `_stats_lock` (or accepted as GIL-safe append — deque.append is atomic, but cleaner to include for consistency)
- `_lookup_times.clear()` in `clear()` and `reset_stats()` is inside `_stats_lock` (already gated by Sub-Task 1)
- A new regression test `test_lookup_times_never_zero_divides_under_concurrency` passes

**Todo List**
1. Write a regression test in `tests/cache/test_multi_level_cache.py` (append after `TestMultiLevelCacheTTL`): populate a `MultiLevelCache`, then call `stats()` and `average_lookup_time_ms()` from 10 threads while another thread continuously calls `reset_stats()`; assert no exceptions raised.
2. In `stats()` (lines 333–335 of `src/cache/multi_level_cache.py`), replace the bare `sum(self._lookup_times) / len(self._lookup_times)` pattern: acquire `_stats_lock`, copy deque to a local list `times`, release lock, compute from `times`.
3. In `average_lookup_time_ms()` (lines 436–438), apply the same snapshot pattern.
4. `_lookup_times.append()` calls in `get()` must be inside the same `_stats_lock` block for strict consistency — pull each append inside the lock alongside the counter increment that precedes it.
5. Run `uv run pytest tests/cache/test_multi_level_cache.py tests/concurrency/ -q` — must be green.

**Relevant Context**
- `src/cache/multi_level_cache.py`: lines 153, 186, 200 (appends in `get()`); lines 333–335 (`stats()`); lines 436–438 (`average_lookup_time_ms()`)
- `_stats_lock` added in Sub-Task 1 — reuse it here; no new lock needed

---

## Sub-Task 3 — Fix `SemanticCache.get_entry()`: add lock

**Status:** `[ ] pending`

**Intent**  
`SemanticCache.get_entry()` (lines 641–642) reads `self.entries` directly without acquiring `self._lock`. It is called from `MultiLevelCache.get()` on the L2-to-L1 promotion path. A concurrent `set()`, `_evict_lru()`, or `clear()` on L2 can cause `self.entries` to change mid-read. The fix is one line: acquire `self._lock` via the `with self._lock` pattern already used by every other method in this class.

**Expected Outcomes**
- `get_entry()` acquires `self._lock` before `self.entries.get(versioned_key)`
- The return value and type signature are unchanged
- A regression test `test_get_entry_never_raises_under_concurrent_eviction` passes
- All existing semantic cache tests pass

**Todo List**
1. Write a regression test in `tests/cache/test_semantic_cache.py` (append after `TestSemanticCacheTTL`): populate a `SemanticCache` near capacity; then in 5 threads continuously call `cache.get_entry(key)` while 5 other threads continuously call `cache.set(key, value)` and `cache.clear()`; use `sys.setswitchinterval(1e-7)` in a `try/finally`; assert no exceptions.
2. In `src/cache/semantic_cache.py` `get_entry()` (line 641), wrap the body in `with self._lock:`.
3. Run `uv run pytest tests/cache/test_semantic_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/semantic_cache.py`: `get_entry()` lines 631–642; `_lock` initialized line 81
- Every other data-touching method uses `with self._lock:` — this is an omission, not a design choice
- `MultiLevelCache.get()` line 172: `l2_entry = self.l2_cache.get_entry(key, version)` — the call site that triggers the race

---

## Sub-Task 4 — Fix `SemanticCache.migrate()`: hold lock for full duration

**Status:** `[ ] pending`

**Intent**  
`SemanticCache.migrate()` collects entries to migrate under `self._lock`, releases the lock, then calls `self.set()` for each entry outside the lock. Between the snapshot and each `set()` call, another thread can evict the entry being migrated or write the `to_version` key with different data. The subsequent `set()` then silently overwrites the concurrent write (TOCTOU). Since `self._lock` is a `threading.RLock` (reentrant), `set()` can be called while `migrate()` holds the outer lock without deadlock. The fix is to extend the `with self._lock:` block to encompass the `set()` loop.

**Expected Outcomes**
- The `with self._lock:` block in `migrate()` covers both the collection phase and all `set()` calls
- The `migrated` counter increment moves inside the lock
- A regression test `test_migrate_is_atomic_no_interleaved_writes` passes
- All existing cache tests pass

**Todo List**
1. Write a regression test in `tests/cache/test_semantic_cache.py`: call `cache.migrate("v1", "v2")` from one thread while another thread continuously calls `cache.set(key, "concurrent_value", "v2")`; assert that after migration completes, every key that should be in `v2` is present and no version mismatch exceptions were raised. Use `sys.setswitchinterval(1e-7)`.
2. In `src/cache/semantic_cache.py` `migrate()` (lines 668–688): extend the `with self._lock:` block to include the `for base_key, entry in entries_to_migrate:` loop and move the `migrated += 1` increment inside the loop, inside the lock.
3. Remove the comment `"(set() has its own lock)"` — it is no longer the reason for correctness; replace with a comment explaining the RLock re-entry.
4. Move the `self._logger.info(...)` call to after the `with` block (logging with lock held is fine but can increase contention — keep it outside).
5. Run `uv run pytest tests/cache/test_semantic_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/semantic_cache.py`: `migrate()` lines 654–688; `_lock = threading.RLock()` line 81
- `set()` uses `with self._lock:` on line 328 — RLock re-entry is safe
- `ExactCache.migrate()` (Sub-Task 5) is a separate issue and must not be conflated

---

## Sub-Task 5 — Fix `ExactCache.migrate()`: make the no-op visible

**Status:** `[ ] pending`

**Intent**  
`ExactCache.migrate()` (lines 446–478) is decorated with `@_synchronized` and appears to iterate `self.cache.items()`, but the second loop is a `pass` no-op. The fundamental reason is that SHA-256 is irreversible: the original key string cannot be recovered from the hashed key stored in the cache, so migration to a new version key is impossible without the original. The method returns `migrated = 0` and emits a misleading `"cache_migration … migrated=0"` log, which is indistinguishable from "nothing matched the version filter". `MultiLevelCache.migrate()` sums L1 and L2 results and logs the total, making the limitation invisible to callers.

**Decision:** Preserve the no-op behaviour (the limitation is real and fundamental) but make it explicit:
- Replace the dead pass-loop with a single comment-and-early-return pattern
- Change the log event to `"cache_migration_skipped"` with a `reason="irreversible_hash"` field
- Add a docstring note to `ExactCache.migrate()` explicitly stating "always returns 0"
- Add a note to `MultiLevelCache.migrate()` docstring: "L1 always contributes 0 (hashed keys are not reversible)"

**Expected Outcomes**
- `ExactCache.migrate()` body has no dead `for hashed_key, entry` loop
- Log event is `"cache_migration_skipped"` with `reason="irreversible_hash"`
- `MultiLevelCache.migrate()` docstring documents the L1 limitation
- A regression test `test_exact_cache_migrate_always_returns_zero` documents the known behaviour
- All existing migration tests pass

**Todo List**
1. Write a test in `tests/cache/test_exact_cache.py` (or extend existing migration test): assert `ExactCache.migrate("v1", "v2")` returns `0` regardless of cache contents, and verify the log event name is `"cache_migration_skipped"`.
2. In `src/cache/exact_cache.py` `migrate()`: remove the dead collection loop and pass loop; replace with `self._logger.info("cache_migration_skipped", reason="irreversible_hash", from_version=from_version, to_version=to_version); return 0`.
3. Update the docstring of `ExactCache.migrate()` to state the hash-irreversibility constraint and that the method always returns 0.
4. In `src/cache/multi_level_cache.py` `migrate()` docstring, add: "Note: L1 always contributes 0 migrated entries because ExactCache keys are irreversible SHA-256 hashes."
5. Add an entry to `CHANGELOG.md` under `## Fixed` for this issue (M-2: ExactCache.migrate silent no-op made visible).
6. Run `uv run pytest tests/cache/ -q` — must be green.

**Relevant Context**
- `src/cache/exact_cache.py`: `migrate()` lines 445–478; `@_synchronized` wraps the whole method
- `src/cache/multi_level_cache.py`: `migrate()` lines 440–464
- Tests: `tests/cache/test_exact_cache.py` — check for any existing migration test before adding

---

## Sub-Task 6 — Fix `MultiLevelCache.reset_stats()`: add missing `l3_hits` reset

**Status:** `[ ] pending`

**Intent**  
`MultiLevelCache.reset_stats()` (lines 490–497) resets `l1_hits`, `l2_hits`, and `misses` but **not** `l3_hits`. `clear()` (lines 262–270) does reset `l3_hits`. This asymmetry means a caller who uses `reset_stats()` to checkpoint stats will see a cumulative `l3_hits` counter that spans across the checkpoint. The fix is one line: add `self.l3_hits = 0` inside the `_stats_lock` block added by Sub-Task 1.

**Expected Outcomes**
- `reset_stats()` resets all four counters: `l1_hits`, `l2_hits`, `misses`, `l3_hits`
- A test `test_reset_stats_clears_l3_hits` passes
- The test `test_clear` still verifies all four counters are zeroed by `clear()`

**Todo List**
1. Verify the existing `test_reset_stats` test in `tests/cache/test_multi_level_cache.py` — confirm it does not already assert on `l3_hits` (likely does not, since L3 is opt-in).
2. Add `test_reset_stats_clears_l3_hits` in `TestMultiLevelCacheL3`: create a cache with an `l3_index` mock; call `query_l3()` to produce an `l3_hits > 0`; call `reset_stats()`; assert `cache.l3_hits == 0`.
3. In `src/cache/multi_level_cache.py` `reset_stats()` (line 490), add `self.l3_hits = 0` inside the `_stats_lock` block (placed alongside the other counter resets from Sub-Task 1).
4. Run `uv run pytest tests/cache/test_multi_level_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/multi_level_cache.py`: `reset_stats()` lines 490–497; `clear()` lines 262–270
- `TestMultiLevelCacheL3` in `tests/cache/test_multi_level_cache.py` — correct class for L3-related tests
- `_stats_lock` block from Sub-Task 1 is the right place to add this

---

## Sub-Task 7 — Fix `MultiLevelCache.get_with_level()`: respect `l1_enabled`/`l2_enabled`

**Status:** `[ ] pending`

**Intent**  
`MultiLevelCache.get_with_level()` (lines 396–416) calls `self.l1_cache.get()` and `self.l2_cache.get()` unconditionally. The main `get()` path guards both calls behind `self.l1_enabled` and `self.l2_enabled` flags (set by `CacheConfig`). If a caller disables L1 via config and then calls `get_with_level()`, they will silently get results from the disabled level — a violation of the config contract. The fix mirrors the guard pattern from `get()`.

**Expected Outcomes**
- `get_with_level()` skips `l1_cache.get()` when `self.l1_enabled is False`
- `get_with_level()` skips `l2_cache.get()` when `self.l2_enabled is False`
- A test `test_get_with_level_respects_disabled_flags` passes
- Existing `test_get_with_level` still passes

**Todo List**
1. Add test `test_get_with_level_respects_disabled_flags` in `TestMultiLevelCache` in `tests/cache/test_multi_level_cache.py`: create a `MultiLevelCache(l1_enabled=False)`; set a key; assert `get_with_level(key)` returns `None` (because L1 is the only level the key exists in after `set()` is called — verify if `set()` also respects the flag, as it does per lines 257–260).
2. In `src/cache/multi_level_cache.py` `get_with_level()` (lines 406–416): wrap the L1 block in `if self.l1_enabled:` and the L2 block in `if self.l2_enabled:`.
3. Run `uv run pytest tests/cache/test_multi_level_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/multi_level_cache.py`: `get_with_level()` lines 396–416; `get()` lines 132–205 (the reference implementation with guards)
- `set()` lines 254–260 already respects `l1_enabled`/`l2_enabled` — `get_with_level()` must be consistent

---

## Sub-Task 8 — Full suite validation and ADR note

**Status:** `[ ] pending`

**Intent**  
After all individual fixes are applied, run the complete test suite (excluding load/performance) to confirm no regressions. Run ruff and mypy over the changed files. Add a brief note to `docs/adr/README.md` cross-referencing the race-fix work, and update `CHANGELOG.md` with the fix entries.

**Expected Outcomes**
- `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q` passes with at least 1095 tests (1088 existing + 7 new regression tests — one per sub-task)
- `uv run ruff check src/cache/ tests/cache/ tests/concurrency/` exits 0
- `uv run mypy src/cache/ --ignore-missing-imports` exits 0
- `CHANGELOG.md` has entries under `## Fixed` for each of the 7 issues

**Todo List**
1. Run `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q --tb=short` — record pass count.
2. Run `uv run ruff check src/cache/ tests/cache/ tests/concurrency/` and fix any new lint errors.
3. Run `uv run mypy src/cache/ --ignore-missing-imports` and fix any new type errors.
4. Run `uv run python scripts/check_coverage_by_package.py` — confirm all per-package floors are still met (no floor may be lowered).
5. Add entries to `CHANGELOG.md` under `## Fixed` for all remaining sub-tasks (ST-1 through ST-4 and ST-6 through ST-7) not already covered by ST-5.
6. Confirm `STATUS.md` does not need updating (the gate thresholds are unchanged; the new tests just add to the passing count).

**Relevant Context**
- `CHANGELOG.md` at repo root — existing `## Fixed` section format
- `STATUS.md` — `fail_under` gate is in `pyproject.toml`; coverage threshold unchanged
- `docs/adr/README.md` — cross-reference only; no new ADR needed for these fixes

---

## Execution Order

Sub-tasks 1 and 2 must be done in order (Sub-Task 2 reuses `_stats_lock` from Sub-Task 1).  
Sub-tasks 3, 4, 5, 6, and 7 are independent of each other and of 1/2, but should follow 1 and 2 to keep the lock model stable.  
Sub-task 8 is always last.

```
[1: _stats_lock counters] → [2: _lookup_times snapshot]
[3: get_entry lock]        → independent
[4: migrate() TOCTOU]      → independent
[5: ExactCache.migrate]    → independent
[6: l3_hits reset_stats]   → after 1 (uses _stats_lock block)
[7: get_with_level flags]  → independent
                all → [8: full suite + CHANGELOG]
```
