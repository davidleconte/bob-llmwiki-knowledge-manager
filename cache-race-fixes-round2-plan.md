# Cache Race Fixes — Round 2 Plan

**Branch:** `fix-multilevel-cache-race`
**Scope:** Five new findings (N-1 through N-5) from the post-round-1 audit.
**Non-goals:** No behaviour changes to eviction, similarity scoring, or public API signatures.
  No performance regressions below SLA targets. No new public methods.
**Approach:** Same discipline as round 1 — regression test first (must be demonstrably
  relevant to the race), then minimal source fix, then targeted pytest green, then full
  suite + ruff + mypy + coverage floors in the final sub-task.

---

## Sub-Task A — Lock `SemanticCache.average_similarity_score()` and
                 move `_similarity_scores.clear()` in `reset_stats()` inside the lock

**Status:** `[ ] pending`

### Technical Specification

**Files changed:** `src/cache/semantic_cache.py`

**Problem (N-1):**

Two independent races on `_similarity_scores: List[float]`:

1. **`average_similarity_score()` reads without lock.**
   `_finalize_hit()` (called from inside `get()` which holds `self._lock`) appends to
   `_similarity_scores` on line 287. `average_similarity_score()` reads the list on lines
   655–657 without acquiring `self._lock`. `MultiLevelCache.stats()` calls this method at
   line 376, meaning every `cache.stats()` call has an unlocked read of `_similarity_scores`
   racing against concurrent `get()` calls.

   The specific window: the boolean guard `if not self._similarity_scores` passes (list is
   non-empty), then a concurrent `reset_stats()` calls `_similarity_scores.clear()`, then
   `sum(self._similarity_scores)` runs on an empty list — but `len()` still returns 0,
   giving `0 / 0` only if `len()` is also called after the clear. In CPython the `list`
   methods are GIL-atomic individually, so `ZeroDivisionError` is unlikely in practice.
   However the **semantic invariant** — "average of hits recorded so far" — is violated
   when the read races with a reset, and the result is silently wrong.

2. **`reset_stats()` clears `_similarity_scores` outside `self._lock`.**
   `reset_stats()` on lines 736–739 calls `self._similarity_scores.clear()` with no lock.
   Concurrently, `get()` holds `self._lock` and appends to `_similarity_scores` via
   `_finalize_hit()`. CPython's GIL makes list.append/clear individually atomic, but the
   sequence `append(); clear()` interleaved as `clear(); append()` produces a non-empty
   list after a reset — effectively leaking one score across the reset boundary.

**Exact before state:**

```
# average_similarity_score() — line 649–657
def average_similarity_score(self) -> float:
    if not self._similarity_scores:
        return 0.0
    return sum(self._similarity_scores) / len(self._similarity_scores)

# reset_stats() — lines 736–739
def reset_stats(self) -> None:
    self._stats.reset()
    self._similarity_scores.clear()
```

**Exact after state:**

```
# average_similarity_score() — acquires lock, snapshots list
def average_similarity_score(self) -> float:
    with self._lock:
        scores = list(self._similarity_scores)
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

# reset_stats() — clears under lock to serialise against _finalize_hit() appends
def reset_stats(self) -> None:
    with self._lock:
        self._stats.reset()
        self._similarity_scores.clear()
```

Note: `_stats.reset()` moves inside `self._lock` too. `CacheStats` fields are plain ints;
individually GIL-atomic, but the multi-field reset (`hits=0; misses=0; evictions=0`)
is not atomic as a group. Holding `self._lock` makes the three-field reset consistent with
concurrent `get()` / `set()` calls which also hold `self._lock` when they call
`_stats.record_hit()` / `_stats.record_miss()`.

**Expected Outcomes**
- `average_similarity_score()` acquires `self._lock`, snapshots `_similarity_scores` into
  a local list, releases the lock, then computes from the local list.
- `reset_stats()` wraps both `self._stats.reset()` and `self._similarity_scores.clear()`
  inside `with self._lock:`.
- `SemanticCache.stats()` already computes `avg_similarity` under `self._lock` (lines
  495–500) — no change needed there.
- A regression test `test_average_similarity_score_never_races_with_reset` passes.
- All existing semantic cache tests pass unchanged.

**Todo List**
1. Write regression test in `tests/cache/test_semantic_cache.py` (append new class
   `TestSemanticCacheAverageSimilarityLock`): populate cache with N entries; run 4 getter
   threads calling `cache.average_similarity_score()` in a loop while 2 resetter threads
   call `cache.reset_stats()` continuously; use `sys.setswitchinterval(1e-7)` / `finally`;
   assert no exceptions and every return value is in `[0.0, 1.0]`.
2. In `src/cache/semantic_cache.py` `average_similarity_score()` (lines 649–657):
   replace bare list read with `with self._lock: scores = list(self._similarity_scores)`,
   then compute from `scores`.
3. In `src/cache/semantic_cache.py` `reset_stats()` (lines 736–739): wrap both
   `self._stats.reset()` and `self._similarity_scores.clear()` inside `with self._lock:`.
4. Run `uv run pytest tests/cache/test_semantic_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/semantic_cache.py`: `average_similarity_score()` lines 649–657;
  `_finalize_hit()` line 287 (appends under `self._lock`); `reset_stats()` lines 736–739;
  `stats()` lines 487–513 (already computes avg under lock — verify no double-lock needed)
- `src/cache/multi_level_cache.py` line 376: calls `self.l2_cache.average_similarity_score()`
  from `stats()` — outside any lock on the MLC side, so the L2 lock is the only guard

---

## Sub-Task B — Lock `SemanticCache.update_threshold()` and
                 snapshot `similarity_threshold` in `SemanticCache.stats()`

**Status:** `[ ] pending`

### Technical Specification

**Files changed:** `src/cache/semantic_cache.py`

**Problem (N-2):**

`update_threshold()` (lines 620–629) assigns `self.similarity_threshold = new_threshold`
without holding `self._lock`. `SemanticCache.get()` reads `self.similarity_threshold` at
line 216 inside `with self._lock:`. So the race is: `get()` holds `self._lock` and reads
the threshold; concurrently (on another thread), `update_threshold()` writes the threshold
without the lock. CPython float assignment is GIL-atomic, so no torn value is possible,
but the pattern is inconsistent: every other state-mutating method acquires `self._lock`.

Additionally, `SemanticCache.stats()` reads `self.similarity_threshold` on line 509 inside
the existing `with self._lock:` block — that read is already safe. The only unsafe site is
the write in `update_threshold()`.

**Exact before state:**

```
# update_threshold() — lines 620–629
def update_threshold(self, new_threshold: float) -> None:
    if not 0 <= new_threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    self.similarity_threshold = new_threshold
```

**Exact after state:**

```
# update_threshold() — write under lock
def update_threshold(self, new_threshold: float) -> None:
    if not 0 <= new_threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    with self._lock:
        self.similarity_threshold = new_threshold
```

**Expected Outcomes**
- `update_threshold()` acquires `self._lock` before the assignment.
- Validation (`if not 0 <= new_threshold <= 1`) stays outside the lock (read-only, no
  shared state; no reason to hold the lock during validation).
- A regression test `test_update_threshold_never_races_with_get` passes.
- All existing threshold tests pass unchanged.

**Todo List**
1. Write regression test in `tests/cache/test_semantic_cache.py` (append to
   `TestSemanticCacheGetEntryLock` class or add a new class): populate cache; run 4 getter
   threads and 2 threshold-update threads concurrently; use `sys.setswitchinterval(1e-7)`;
   assert no exceptions.
2. In `src/cache/semantic_cache.py` `update_threshold()` (line 629): wrap the
   `self.similarity_threshold = new_threshold` assignment in `with self._lock:`.
3. Run `uv run pytest tests/cache/test_semantic_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/semantic_cache.py`: `update_threshold()` lines 620–629; `get()` line 216
  reads `self.similarity_threshold` inside `with self._lock:`; `stats()` line 509 reads it
  inside the same lock
- `src/cache/multi_level_cache.py` `update_similarity_threshold()` line 404: the MLC entry
  point that delegates here — no additional locking needed at that level

---

## Sub-Task C — Lock `MultiLevelCache.enable_promotion()` / `disable_promotion()`
                 and snapshot `promote_l2_hits` in `stats()`

**Status:** `[ ] pending`

### Technical Specification

**Files changed:** `src/cache/multi_level_cache.py`

**Problem (N-3):**

`enable_promotion()` (line 408) and `disable_promotion()` (line 412) write
`self.promote_l2_hits` without `self._stats_lock`. `get()` reads `self.promote_l2_hits`
at line 177 without the lock (it is not a stats counter so `_stats_lock` was not applied
there in round 1). `stats()` reads `self.promote_l2_hits` at line 378 also without the
lock. CPython bool assignment is GIL-atomic, so no torn read is possible. But `stats()`
promises a consistent snapshot: the counter fields are now snapshotted atomically, while
the flag is read outside any lock. A call to `disable_promotion()` between the counter
snapshot and the flag read would produce a dict that reports `promote_l2_hits=False` while
the counters reflect a period when promotion was enabled — a semantically misleading
snapshot.

`get()` reading `promote_l2_hits` outside `_stats_lock` is intentional — it is a
config-like flag, not a stats counter, and adding the lock to every L2 hit path would add
contention with no meaningful safety benefit (the flag is not a per-operation invariant;
an in-flight `get()` observing the old flag value while a concurrent `disable_promotion()`
fires is correct — the promotion decision was made before the disable). The only fix needed
is the write and the stats snapshot.

**Exact before state:**

```
# enable_promotion() — line 406–408
def enable_promotion(self) -> None:
    self.promote_l2_hits = True

# disable_promotion() — lines 410–412
def disable_promotion(self) -> None:
    self.promote_l2_hits = False

# stats() — line 378 (outside any lock)
    "promote_l2_hits": self.promote_l2_hits,
```

**Exact after state:**

```
# enable_promotion()
def enable_promotion(self) -> None:
    with self._stats_lock:
        self.promote_l2_hits = True

# disable_promotion()
def disable_promotion(self) -> None:
    with self._stats_lock:
        self.promote_l2_hits = False

# stats() — extend the existing _stats_lock snapshot block to include the flag
with self._stats_lock:
    l1_hits = self.l1_hits
    l2_hits = self.l2_hits
    misses = self.misses
    promote_l2_hits = self.promote_l2_hits   # ← add this line
...
    "promote_l2_hits": promote_l2_hits,      # ← use the local
```

**Expected Outcomes**
- `enable_promotion()` and `disable_promotion()` acquire `_stats_lock`.
- `stats()` snapshots `promote_l2_hits` inside the same `_stats_lock` block as the counters.
- A regression test `test_promotion_flag_consistent_in_stats_snapshot` passes.
- All existing promotion-flag tests pass unchanged.

**Todo List**
1. Write regression test in `tests/cache/test_multi_level_cache.py` (append to
   `TestMultiLevelCache`): call `enable_promotion()` / `disable_promotion()` from 2 threads
   while 4 threads hammer `stats()` and assert the returned `"promote_l2_hits"` is always
   a bool (never raises, never returns a non-bool). Assert no exceptions.
2. In `src/cache/multi_level_cache.py` `enable_promotion()` (line 408): wrap assignment
   in `with self._stats_lock:`.
3. In `src/cache/multi_level_cache.py` `disable_promotion()` (line 412): wrap assignment
   in `with self._stats_lock:`.
4. In `src/cache/multi_level_cache.py` `stats()` (lines 346–349): add
   `promote_l2_hits = self.promote_l2_hits` inside the existing `with self._stats_lock:`
   block; use `promote_l2_hits` local on line 378.
5. Run `uv run pytest tests/cache/test_multi_level_cache.py -q` — must be green.

**Relevant Context**
- `src/cache/multi_level_cache.py`: `enable_promotion()` line 406; `disable_promotion()`
  line 410; `stats()` lines 346–380; `_stats_lock` block currently lines 346–349
- `get()` line 177 reads `promote_l2_hits` without lock intentionally — flag semantics
  (in-flight decision), not counter semantics. Do not add lock there.

---

## Sub-Task D — Eliminate double-`size()` calls in `ExactCache.stats()`
                 and `MultiLevelCache.stats()`

**Status:** `[ ] pending`

### Technical Specification

**Files changed:** `src/cache/exact_cache.py`, `src/cache/multi_level_cache.py`

**Problem (N-4):**

**ExactCache.stats()** (lines 360–366) calls `self.size()` twice:

```python
"size": self.size(),                                    # acquires _lock → releases
"max_size": self.max_size,
"utilization": (self.size() / self.max_size) * 100,    # acquires _lock again
```

Between the two `size()` calls a concurrent eviction can reduce the dict. The resulting
`stats()` dict reports `"size": 5, "utilization": 0.4%` (size=4 on second call) — an
internally inconsistent snapshot. No crash; silently misleading.

**MultiLevelCache.stats()** (lines 366–374) calls `self.l1_cache.size()` three times and
`self.l2_cache.size()` three times in succession, with no lock spanning all six calls:

```python
"l1_size": self.l1_cache.size(),          # L1 lock → release
"l1_max_size": self.l1_cache.max_size,
"l1_utilization": (self.l1_cache.size() / self.l1_cache.max_size) * 100,  # L1 lock again
"l2_size": self.l2_cache.size(),          # L2 lock → release
"l2_max_size": self.l2_cache.max_size,
"l2_utilization": (self.l2_cache.size() / self.l2_cache.max_size) * 100,  # L2 lock again
```

Same risk: a concurrent eviction between the first and second `size()` pair gives
inconsistent size/utilization within the same stats dict.

**Exact before state — `ExactCache.stats()`:**

```python
return {
    **self._stats.to_dict(),
    "size": self.size(),
    "max_size": self.max_size,
    "utilization": (self.size() / self.max_size) * 100,
    "version": self.VERSION,
}
```

**Exact after state — `ExactCache.stats()`:**

```python
n = self.size()   # single lock acquisition; n is stable for the rest of the method
return {
    **self._stats.to_dict(),
    "size": n,
    "max_size": self.max_size,
    "utilization": (n / self.max_size) * 100,
    "version": self.VERSION,
}
```

**Exact before state — `MultiLevelCache.stats()` (lines 366–374):**

```python
"l1_size": self.l1_cache.size(),
"l1_max_size": self.l1_cache.max_size,
"l1_utilization": (self.l1_cache.size() / self.l1_cache.max_size) * 100,
# L2 stats
"l2_hits": l2_hits,
"l2_hit_rate": l2_hit_rate,
"l2_size": self.l2_cache.size(),
"l2_max_size": self.l2_cache.max_size,
"l2_utilization": (self.l2_cache.size() / self.l2_cache.max_size) * 100,
```

**Exact after state — `MultiLevelCache.stats()`:**

```python
# Snapshot sub-cache sizes once each to keep size/utilization consistent.
l1_size = self.l1_cache.size()
l2_size = self.l2_cache.size()
...
"l1_size": l1_size,
"l1_max_size": self.l1_cache.max_size,
"l1_utilization": (l1_size / self.l1_cache.max_size) * 100,
...
"l2_size": l2_size,
"l2_max_size": self.l2_cache.max_size,
"l2_utilization": (l2_size / self.l2_cache.max_size) * 100,
```

**Expected Outcomes**
- `ExactCache.stats()` calls `self.size()` exactly once; both `"size"` and
  `"utilization"` use the same snapshot value `n`.
- `MultiLevelCache.stats()` calls `l1_cache.size()` and `l2_cache.size()` exactly once
  each; all three L1 and all three L2 fields use the local snapshots.
- A regression test `test_stats_size_and_utilization_are_consistent` passes for both
  classes.
- All existing stats tests pass unchanged.

**Todo List**
1. Write regression test for `ExactCache` in `tests/cache/test_exact_cache.py` (append to
   `TestExactCache`): verify that `stats()` returns a dict where
   `size * 100 / max_size == utilization` (within floating-point tolerance) — this would
   fail before the fix if a concurrent eviction fires between the two `size()` calls. Use
   `sys.setswitchinterval(1e-7)` with concurrent evictors.
2. Write regression test for `MultiLevelCache` in `tests/cache/test_multi_level_cache.py`
   (append to `TestMultiLevelCache`): same pattern — assert
   `stats()["l1_size"] * 100 / stats()["l1_max_size"] == approx(stats()["l1_utilization"])`
   and same for L2, under concurrent mutation.
3. In `src/cache/exact_cache.py` `stats()` (lines 360–366): introduce `n = self.size()`
   and replace both `self.size()` calls with `n`.
4. In `src/cache/multi_level_cache.py` `stats()` (lines 340–380): add
   `l1_size = self.l1_cache.size()` and `l2_size = self.l2_cache.size()` before the return
   dict; replace the four `self.l1_cache.size()` / `self.l2_cache.size()` calls in the
   dict with the locals.
5. Run `uv run pytest tests/cache/ -q` — must be green.

**Relevant Context**
- `src/cache/exact_cache.py`: `stats()` lines 354–366
- `src/cache/multi_level_cache.py`: `stats()` lines 340–380; `l1_cache.size()` uses
  `@_synchronized`; `l2_cache.size()` uses `with self._lock:` — both are individually safe
  but not jointly atomic

---

## Sub-Task E — Add inline lock-order comment in `SemanticCache.stats()`

**Status:** `[ ] pending`

### Technical Specification

**Files changed:** `src/cache/semantic_cache.py`

**Problem (N-5):**

`SemanticCache.stats()` (lines 487–513) holds `self._lock` across the entire dict
construction including a call to `self.embedding_generator.cache_size()` (line 511).
`EmbeddingGenerator.cache_size()` is currently a GIL-atomic `len()` with no locking.
If a lock is ever added to `EmbeddingGenerator` (e.g., to protect its `corpus` dict),
and if `EmbeddingGenerator` internally calls back into a `SemanticCache` method, a
lock-order cycle would deadlock. This is advisory — no code change is needed now, but
the dependency must be documented so future authors do not introduce a cycle.

**Exact before state — line 511:**

```python
"embedding_cache_size": self.embedding_generator.cache_size(),
```

**Exact after state — line 511:**

```python
# EmbeddingGenerator.cache_size() is currently lock-free (plain len()).
# If a lock is added to EmbeddingGenerator in the future, verify it cannot
# re-acquire self._lock (lock-order cycle → deadlock).
"embedding_cache_size": self.embedding_generator.cache_size(),
```

**Expected Outcomes**
- Three-line comment added immediately above the `embedding_generator.cache_size()` call.
- No functional change; no new test needed.
- `uv run ruff check src/cache/semantic_cache.py` exits 0.

**Todo List**
1. In `src/cache/semantic_cache.py` line 511: insert the three-line comment directly above
   the `embedding_generator.cache_size()` call.
2. Run `uv run ruff check src/cache/semantic_cache.py` — must exit 0.

**Relevant Context**
- `src/cache/semantic_cache.py`: `stats()` lines 487–513; `embedding_generator` is a
  `HashingVectorizer`-backed `EmbeddingGenerator` with no locks today
- `src/cache/embeddings.py`: the `EmbeddingGenerator` implementation — verify `cache_size()`
  is still lock-free before writing the comment

---

## Sub-Task F — Full suite validation + coverage floors + CHANGELOG

**Status:** `[ ] pending`

### Technical Specification

**Expected Outcomes**
- `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q` passes with at
  least 1100 tests (1096 existing + ≥4 new regression tests from sub-tasks A–D).
- `uv run ruff check src/cache/ tests/cache/ tests/concurrency/` exits 0.
- `uv run mypy src/cache/ --ignore-missing-imports` exits 0.
- `uv run python scripts/check_coverage_by_package.py` confirms all per-package floors
  still met.
- `CHANGELOG.md` has entries under `## Fixed` for N-1 through N-4 and `## Changed` (or
  inline comment) for N-5.
- `STATUS.md` requires no change (gate thresholds unchanged).

**Todo List**
1. Run `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q --tb=short`
   — record pass count.
2. Run `uv run ruff check src/cache/ tests/cache/ tests/concurrency/` — fix any new lint
   errors.
3. Run `uv run mypy src/cache/ --ignore-missing-imports` — fix any new type errors.
4. Run `uv run python scripts/check_coverage_by_package.py` — all floors must still be met.
5. Append entries to `CHANGELOG.md` under `## Fixed` (in `[1.1.0]` section) for N-1, N-2,
   N-3, and N-4.
6. Confirm `STATUS.md` does not need updating.

**Relevant Context**
- `CHANGELOG.md`: existing `## Fixed` block in `[1.1.0]` section — append after the last
  round-1 entry
- `pyproject.toml`: `fail_under` gate — unchanged
- `scripts/check_coverage_by_package.py`: per-package floors

---

## Execution Order

Sub-tasks A, B, C, and D are mutually independent (different methods in different or same
files with no shared dependencies). Sub-task E has no code dependencies. All must precede F.

```
[A: average_similarity_score + reset_stats lock]  ─┐
[B: update_threshold lock]                          ├─→ [F: full suite + CHANGELOG]
[C: enable/disable_promotion + stats snapshot]      │
[D: double-size() elimination]                     ─┘
[E: lock-order comment — no tests, trivially safe]  → can be done in any order
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| `average_similarity_score()` snapshots list then releases lock before computing | Minimises lock-hold time; `sum()/len()` on a local list is safe outside the lock |
| `reset_stats()` moves `_stats.reset()` inside `self._lock` | `CacheStats` multi-field reset is not atomic as a group; serialising with `get()`/`set()` which also hold `self._lock` is the correct fix |
| `update_threshold()` validation stays outside lock | Read-only guard on caller's input; no shared state; no benefit to holding the lock during a `raise` |
| `enable/disable_promotion()` use `_stats_lock` not a new lock | `promote_l2_hits` is snapshotted in `stats()` which already holds `_stats_lock`; same lock = same critical section |
| `get()` does NOT lock around `promote_l2_hits` read | Flag semantics, not counter semantics; an in-flight get() observing the previous flag value is correct behaviour, not a race |
| `ExactCache.stats()` uses a local `n` | Eliminates the double-`size()` inconsistency with zero lock overhead |
| `MultiLevelCache.stats()` uses `l1_size`/`l2_size` locals | Same pattern; no new locking needed — each `size()` call is already lock-protected internally |
