# Cache Remediation & Validation Plan

**Branch:** `fix-multilevel-cache-race`
**Scope:** Five targeted changes to `src/cache/` — two code fixes, one new
documentation file, one code comment, and one new `CacheStatsSnapshot` dataclass
— plus the corresponding regression tests. No API surface changes, no refactors
outside the sub-tasks listed.

---

## Top-Level Overview

The audit identified five items not yet addressed by Rounds 1–4:

| ID | Sub-Task | Severity | Nature |
|---|---|---|---|
| A | 1 | Medium | `stats()`: `l3_hits` missing from snapshot and return dict; `total_hits` silently excludes L3 |
| B | 2 | Medium | `contains()`: ignores `l1_enabled` / `l2_enabled`; can return `True` for a level `get()` would skip |
| C | 3 | Low (hygiene) | No `CONCURRENCY.md`; lock-order rule and 4-tier checklist exist only in the KB |
| D | 4 | Low (fragility note) | `max_size` cross-class reads in `stats()` undocumented; safe today but historically the same pattern as S-1 |
| E | 5 | Low (structural) | No `CacheStatsSnapshot` dataclass; snapshot discipline enforced by convention not structure |

Each sub-task is independent and must leave the full test suite green before the
next one begins.

---

## Design Decisions

### Q1 — Sub-task ordering
**Decision:** 1 → 2 → 3 → 4 → 5 (as recommended). Code fixes first, documentation
second, structural improvement last.

### Q2 — Location of `CONCURRENCY.md`
**Decision:** `src/cache/CONCURRENCY.md` (co-located with the code it documents).
Rationale: a contributor modifying `src/cache/` browses that directory in their
editor. A file under `docs/` requires them to know to look there. The KB doc at
`docs/knowledge-base/research/iterative-audit-lessons-2026-07.md` remains the
narrative history; `src/cache/CONCURRENCY.md` is the operational reference.

### Q3 — `CacheStatsSnapshot` dataclass: include or defer?
**Decision: Include as Sub-Task 5.** Full rationale below.

**The case for including it now:**

The current `stats()` method returns a plain `dict` containing 25 keys snapshotted
from five different sources (`_stats_lock` block, two `size()` calls, one
`get_threshold()` call, one `average_similarity_score()` call). Every field added to
this dict in the future requires the author to manually place the read in the correct
lock block — and to know which lock block is correct. Rounds 1–4 found a new
snapshot-discipline failure in `stats()` in every single round. The pattern has
already cost four fix iterations. A frozen dataclass makes the discipline structural:
the type system enforces that a snapshot object is assembled once (all reads in one
place) and is thereafter immutable.

**What it is not:**
- It is not a refactor of the caching logic.
- It does not change the public `stats()` return type from the caller's perspective
  (callers receive a `dict` via the existing `.to_dict()` method on the dataclass,
  just as `CacheStats` already has `to_dict()`).
- It does not change the lock structure.

**Concrete benefit (measured from research):**
- `stats()` currently has 25 keys and 30+ call sites across 10 files.
- The codebase already has one `@dataclass(frozen=True)` precedent
  (`Document` in `src/validation/corpus.py`).
- The existing `CacheStats` accumulator already has a `to_dict()` method — the
  pattern is established in this codebase.
- Sub-Task 1 adds a 26th key (`l3_hits`). Without the dataclass, the next field
  addition will require the same "remember to add it to the lock block" manual
  discipline. With the dataclass, mypy will raise a `TypeError` at construction
  time if any field is omitted from the snapshot.

**Risk:** Adding Sub-Task 5 touches `stats()` a second time after Sub-Task 1.
This is acceptable because Sub-Task 1 will be green and committed before Sub-Task 5
begins, and Sub-Task 5 does not change the dict keys — only wraps them.

---

## Sub-Task 1 — Fix `stats()`: include `l3_hits` in snapshot and return dict

### Intent

`stats()` snapshots `l1_hits`, `l2_hits`, `misses`, and `promote_l2_hits` under
`_stats_lock` (lines 349–353) but never snapshots `l3_hits`. The return dict omits
the `"l3_hits"` key entirely and computes `"total_hits"` as `l1_hits + l2_hits`,
silently excluding all L3 activity. Any caller that wires a `PersistentEmbeddingIndex`
and calls `stats()["l3_hits"]` receives a `KeyError`. Even without explicit keyed
access, `total_requests` will diverge from the true lookup count when L3 is active
(hits are missing from the numerator while the denominator is correct).

### Expected Outcomes

- `stats()["l3_hits"]` returns the current `l3_hits` counter value (integer ≥ 0).
- `stats()["total_hits"]` equals `l1_hits + l2_hits + l3_hits`.
- The new value is taken from a snapshot made inside the same `_stats_lock` block
  as the other counters, guaranteeing it is consistent with the rest of the dict.
- All existing tests continue to pass unchanged.
- A new test in `TestMultiLevelCacheL3` asserts both the key presence and value
  correctness after a sequence of L3 queries.

### Todo List

1. In `src/cache/multi_level_cache.py`, locate the `with self._stats_lock:` block
   at the top of `stats()` (lines 349–353). Add `l3_hits = self.l3_hits` as the
   fourth counter snapshotted in that block (after `misses`, before
   `promote_l2_hits`).

2. In the `stats()` return dict (lines 385–410), make two changes:
   - Change `"total_hits": l1_hits + l2_hits` to `"total_hits": l1_hits + l2_hits + l3_hits`.
   - Add `"l3_hits": l3_hits` as a new key in the L3 or overall stats section.

3. In `tests/cache/test_multi_level_cache.py`, add a new test method
   `test_stats_includes_l3_hits` to the `TestMultiLevelCacheL3` class (after line 719).
   The test must:
   - Construct a `MultiLevelCache` with a real `PersistentEmbeddingIndex` (following
     the pattern of `test_reset_stats_clears_l3_hits` at line 699).
   - Call `cache.query_l3(...)` N times until `cache.l3_hits == N`.
   - Assert `cache.stats()["l3_hits"] == N`.
   - Assert `cache.stats()["total_hits"] == N` (when no L1/L2 queries were made).
   - Assert `"l3_hits"` is present in the `stats()` return dict (key existence check).

4. Run `uv run pytest tests/cache/test_multi_level_cache.py -v` and confirm all
   tests pass with no new failures.

### Relevant Context

- **Snapshot block to extend:** `src/cache/multi_level_cache.py` lines 349–353
- **Return dict to patch:** `src/cache/multi_level_cache.py` lines 385–410
  - `"total_hits"` is at line 388; `l3_hits` increment is at line 243 under `_stats_lock`
- **Pattern to follow for the new test:** `test_reset_stats_clears_l3_hits`
  at `tests/cache/test_multi_level_cache.py` lines 699–722
- **Lock evidence:** `query_l3()` already increments under `_stats_lock` (line 242);
  `clear()` and `reset_stats()` already zero it under the same lock (lines 279, 569)

### Status

`[x] done`

---

## Sub-Task 2 — Fix `contains()`: respect `l1_enabled` / `l2_enabled`

### Intent

`contains()` at line 492 unconditionally queries both sub-caches:

```python
return self.l1_cache.contains(key, version) or self.l2_cache.contains(key, version)
```

This violates the contract established by `get()` and `set()`, which both gate
sub-cache access on the `l1_enabled` / `l2_enabled` flags. The inconsistency can
produce a false positive: when `l1_enabled=False`, `contains()` returns `True`
for a key that was written only to L1 (which `set()` also skips when the flag is
False — but if any data exists in L1 from a prior state), while `get()` would
return `None`. Caller code that uses `contains()` as a pre-flight check before
`get()` would behave incorrectly.

The fix aligns `contains()` with `get()` and `set()` by gating each sub-cache
query behind its flag.

### Expected Outcomes

- `contains()` with `l1_enabled=False` does not query L1; returns a result based
  solely on L2 (if `l2_enabled` is True).
- `contains()` with `l2_enabled=False` does not query L2; returns a result based
  solely on L1 (if `l1_enabled` is True).
- `contains()` with both flags True behaves identically to the current implementation.
- All existing tests continue to pass unchanged.
- A new test asserts the flag-gating behaviour, mirroring the pattern of
  `test_get_with_level_respects_disabled_flags` (lines 442–466).

### Todo List

1. In `src/cache/multi_level_cache.py`, rewrite `contains()` (lines 482–492) to
   match the gating pattern used by `get()`:

   ```python
   def contains(self, key: str, version: Optional[str] = None) -> bool:
       if self.l1_enabled and self.l1_cache.contains(key, version):
           return True
       if self.l2_enabled and self.l2_cache.contains(key, version):
           return True
       return False
   ```

   The short-circuit semantics of the original `or` expression are preserved:
   if L1 returns `True`, L2 is not queried. The new form makes the flag-gating
   explicit.

2. In `tests/cache/test_multi_level_cache.py`, add a new test method
   `test_contains_respects_disabled_flags` to `TestMultiLevelCache` (adjacent to
   `test_contains` at line 239). The test must:
   - Create `MultiLevelCache(l1_enabled=False)`, set a key via `cache.set("k","v")`,
     and assert `cache.l1_cache.size() == 0` (set() skips L1 too).
     Then assert `cache.contains("k") is True` (found in L2) and that the L1 sub-cache
     was not responsible (verifiable because `cache.l1_cache.size() == 0`).
   - Create `MultiLevelCache(l2_enabled=False)`, set a key, assert
     `cache.l2_cache.size() == 0`, then assert `cache.contains("k") is True`
     (found in L1).
   - Create `MultiLevelCache(l1_enabled=False, l2_enabled=False)`, set a key,
     and assert `cache.contains("k") is False` (both disabled, neither queried).

3. Run `uv run pytest tests/cache/test_multi_level_cache.py -v` and confirm all
   tests pass.

### Relevant Context

- **Method to fix:** `src/cache/multi_level_cache.py` lines 482–492
- **Reference pattern — `get()` gating:** lines 153 (`if self.l1_enabled`) and 169 (`if self.l2_enabled`)
- **Reference pattern — `set()` gating:** lines 267–270
- **Reference test pattern:** `test_get_with_level_respects_disabled_flags` at
  `tests/cache/test_multi_level_cache.py` lines 442–466
- **Note:** `set()` with `l1_enabled=False` writes only to L2, so after
  `MultiLevelCache(l1_enabled=False).set("k","v")` the key genuinely lives only
  in L2 — `contains()` must return `True` via L2, not via L1.

### Status

`[x] done`

---

## Sub-Task 3 — Create `src/cache/CONCURRENCY.md`

### Intent

The 4-tier audit checklist and the lock-order rule currently exist only in the KB
at `docs/knowledge-base/research/iterative-audit-lessons-2026-07.md`. A contributor
modifying `src/cache/` will not check the KB before making a change. Without an
in-tree reference, the next N-5 / S-1 pattern will be introduced again. The file
must live beside the code it documents.

### Expected Outcomes

- `src/cache/CONCURRENCY.md` exists and is committed.
- The file contains: the lock inventory table, the lock-ordering rule, the snapshot
  pattern with a code example, and the complete 4-tier audit checklist verbatim from
  the KB doc.
- No source code is modified; this sub-task is documentation only.
- `uv run pytest tests/` continues to pass (no test impact expected).

### Todo List

1. Create `src/cache/CONCURRENCY.md` with the following sections in order:
   - **Overview** — one paragraph stating this file is the in-tree concurrency
     reference for `src/cache/`; the KB doc is the narrative history.
   - **Lock Inventory** — a three-row table matching the one in the KB doc:
     `ExactCache` / `_synchronized` decorator / `threading.RLock`;
     `SemanticCache` / `self._lock = threading.RLock()`;
     `MultiLevelCache` / `self._stats_lock = threading.RLock()`.
   - **Lock Ordering Rule** — exact rule from the KB doc:
     `SemanticCache._lock` must always be acquired BEFORE
     `MultiLevelCache._stats_lock`. Document the one current call path that
     creates this ordering (`MultiLevelCache.stats()` → `l2_cache.average_similarity_score()`).
     State that any future code path that acquires `_stats_lock` inside
     `SemanticCache._lock` creates a deadlock risk.
   - **Snapshot Pattern** — explain the rule "snapshot all fields in one lock
     block, compute outside the lock". Include a minimal before/after code snippet
     illustrating the wrong pattern (two reads outside a lock) versus the correct
     pattern (snapshot + compute).
   - **4-Tier Audit Checklist** — verbatim from the KB doc (T1 through T4 +
     Artifact hygiene), formatted as a runnable checklist.
   - **References** — links to `multi_level_cache.py`, `semantic_cache.py`,
     `exact_cache.py`, and the KB research doc.

2. Verify the file renders correctly in Markdown (no broken tables or headings).

3. Run `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q`
   and confirm zero failures (documentation change; no code touched).

### Relevant Context

- **Source material:** `docs/knowledge-base/research/iterative-audit-lessons-2026-07.md`
  lines 192–220 (checklist) and lines 253–272 (lock-order and lock inventory)
- **Source material:** `docs/knowledge-base/research/cache-race-fix-lessons-2026-07.md`
  lines 255–272 (lock ordering section)
- **Destination:** `src/cache/CONCURRENCY.md` (does not yet exist; confirmed by
  `ls src/cache/`)
- **N-5 advisory comment** (the only in-code reference today) is at
  `src/cache/semantic_cache.py` lines 511–514 — the new doc supersedes it as
  the authoritative reference but does not replace the comment.

### Status

`[x] done`

---

## Sub-Task 4 — Document `max_size` cross-class reads in `stats()`

### Intent

`stats()` reads `self.l1_cache.max_size` and `self.l2_cache.max_size` directly
(lines 397–404) outside any lock. These reads are safe today because `max_size`
is assigned once in `__init__` and never mutated afterwards in either sub-cache.
However, the audit established that the exact same access pattern for
`similarity_threshold` (also set in `__init__`, also readable without a lock at
first glance) required adding a `get_threshold()` accessor in Round 4 once it
became mutable via `update_threshold()`. Without a comment, the next reader
cannot distinguish "safe because immutable" from "not yet broken because no
resizing API exists yet". A one-line comment at each read site prevents either
(a) a future audit flagging these as S-1 regressions, or (b) a future contributor
adding a `resize()` method and forgetting to add a guarded accessor.

### Expected Outcomes

- Each of the four `max_size` reads in `stats()` (lines 397, 398, 403, 404) has
  an inline or block comment stating the field is construction-time-only and safe
  to read without the lock.
- No functional code changes.
- No test changes.
- All tests continue to pass.

### Todo List

1. In `src/cache/multi_level_cache.py`, add an inline comment above or beside the
   four `max_size` reads in `stats()`. A single block comment covering all four is
   acceptable:

   ```python
   # max_size is construction-time-only (set in __init__, never mutated).
   # Direct attribute reads are safe without a lock. If a resize() API is
   # ever added, add a get_max_size() accessor following the get_threshold()
   # pattern (S-1 fix) and update these four lines.
   "l1_max_size": self.l1_cache.max_size,
   "l1_utilization": (l1_size / self.l1_cache.max_size) * 100,
   ...
   "l2_max_size": self.l2_cache.max_size,
   "l2_utilization": (l2_size / self.l2_cache.max_size) * 100,
   ```

2. Run `uv run pytest tests/cache/test_multi_level_cache.py -v` and confirm all
   tests pass (comment-only change; no failures expected).

### Relevant Context

- **Lines to annotate:** `src/cache/multi_level_cache.py` lines 397, 398, 403, 404
- **Precedent pattern:** `get_threshold()` accessor in `src/cache/semantic_cache.py`
  lines 623–634 (added in S-1 fix, Round 4)
- **Risk note:** `max_size` is read in `_evict_lru()` of `SemanticCache` (line 333)
  and `ExactCache` (comparable location) — both within their own lock, so no cross-
  class issue there. Only the reads in `MultiLevelCache.stats()` are cross-class.

### Status

`[x] done`

---

## Validation Gate (all sub-tasks)

After all four sub-tasks are complete, run the full validation suite:

```bash
# Fast gate (cache + concurrency)
uv run pytest tests/cache/ tests/concurrency/ -v

# Full gate (excluding load/performance)
uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q

# Linting and type checking
uv run ruff check src/cache/ tests/cache/
uv run mypy src/cache/
```

**Pass criteria:**
- Zero new test failures
- Zero new ruff violations
- Zero new mypy errors (annotation-unchecked notes are acceptable)
- `stats()["l3_hits"]` key present and correct (Sub-Task 1)
- `contains()` with disabled flags returns correct result (Sub-Task 2)
- `src/cache/CONCURRENCY.md` exists and renders correctly (Sub-Task 3)
- Inline comment on `max_size` reads in `stats()` (Sub-Task 4)

---

---

## Sub-Task 5 — Introduce `CacheStatsSnapshot` frozen dataclass

### Intent

`stats()` currently assembles 25 keys from five different read sites (counter
snapshot under `_stats_lock`, two `size()` calls, `get_threshold()`, and
`average_similarity_score()`). Each field added in the future requires its author
to manually place the read in the correct lock block. Rounds 1–4 found a new
`stats()` snapshot-consistency failure in every single round — the convention-based
discipline is demonstrably insufficient. A `@dataclass(frozen=True)` makes the
assembly point explicit and structural: all fields are populated at construction
time in one place, and the object is immutable after that. mypy will catch a
missing field at construction time; a dict cannot.

The existing `CacheStats` accumulator (in `src/cache/base.py`) already has a
`to_dict()` method, establishing the pattern. The only frozen dataclass precedent
in the codebase is `Document` in `src/validation/corpus.py`. Sub-Task 5 follows
both precedents.

The public `stats()` signature does not change: callers still receive a `dict`.
The dataclass is an internal assembly vehicle, not a new API surface.

### Expected Outcomes

- A `@dataclass(frozen=True)` class `CacheStatsSnapshot` exists in
  `src/cache/base.py` with typed fields for all 26 keys currently returned by
  `MultiLevelCache.stats()` (25 existing + `l3_hits` added in Sub-Task 1).
- `CacheStatsSnapshot` has a `to_dict()` method returning the same `dict` shape
  as the current `stats()` return value (key names and value types unchanged).
- `MultiLevelCache.stats()` assembles one `CacheStatsSnapshot` instance and
  returns `snapshot.to_dict()`. The lock structure is unchanged.
- All existing tests pass without modification (same dict shape, same key names).
- One new test asserts that `stats()` returns a dict with all 26 expected keys and
  that the types of selected fields match the dataclass field types.
- mypy reports zero new errors.

### Todo List

1. In `src/cache/base.py`, define `CacheStatsSnapshot` as a
   `@dataclass(frozen=True)` after the existing `CacheStats` class. Fields must
   exactly match the 26 keys returned by `stats()` after Sub-Task 1, with correct
   Python types:

   | Field name | Type | Source in current `stats()` |
   |---|---|---|
   | `total_requests` | `int` | `l1_hits + l2_hits + l3_hits + misses` |
   | `total_hits` | `int` | `l1_hits + l2_hits + l3_hits` |
   | `total_misses` | `int` | `misses` |
   | `hit_rate` | `float` | computed from totals |
   | `avg_lookup_time_ms` | `float` | `average_lookup_time_ms()` |
   | `version` | `str` | `self.VERSION` |
   | `l1_hits` | `int` | snapshot |
   | `l1_hit_rate` | `float` | computed |
   | `l1_size` | `int` | `l1_cache.size()` |
   | `l1_max_size` | `int` | `l1_cache.max_size` |
   | `l1_utilization` | `float` | computed |
   | `l2_hits` | `int` | snapshot |
   | `l2_hit_rate` | `float` | computed |
   | `l2_size` | `int` | `l2_cache.size()` |
   | `l2_max_size` | `int` | `l2_cache.max_size` |
   | `l2_utilization` | `float` | computed |
   | `l2_similarity_threshold` | `float` | `get_threshold()` |
   | `l2_avg_similarity` | `float` | `average_similarity_score()` |
   | `l3_hits` | `int` | snapshot (added Sub-Task 1) |
   | `promote_l2_hits` | `bool` | snapshot |
   | `unique_entries` | `int` | computed inline |

   Add a `to_dict(self) -> Dict[str, Any]` method that returns
   `dataclasses.asdict(self)` (or an explicit dict — either is acceptable).

2. In `src/cache/multi_level_cache.py`, rewrite the `stats()` return statement to
   construct a `CacheStatsSnapshot` instance from the already-computed local
   variables (all variables snapshotted under `_stats_lock` or computed from
   them). Return `snapshot.to_dict()`. The lock structure (the `with self._stats_lock:`
   block, the two `size()` calls, `get_threshold()`, `average_similarity_score()`)
   is not changed — only the final assembly of the return value changes.

3. Add `from src.cache.base import CacheStatsSnapshot` to the imports in
   `multi_level_cache.py`.

4. In `tests/cache/test_multi_level_cache.py`, add a new test
   `test_stats_returns_all_expected_keys` to `TestMultiLevelCache`. The test must:
   - Call `cache.stats()` after a few `set()` / `get()` operations.
   - Assert that all 26 expected keys are present in the returned dict.
   - Assert selected field types: `total_requests` is `int`,
     `hit_rate` is `float`, `promote_l2_hits` is `bool`.
   - This test acts as a regression guard: if a future `stats()` change drops or
     renames a key, this test will catch it.

5. Run `uv run mypy src/cache/` and confirm zero new errors.

6. Run `uv run pytest tests/cache/ tests/concurrency/ -v` and confirm all tests
   pass.

### Relevant Context

- **Existing pattern:** `CacheStats` in `src/cache/base.py` is already a
  `@dataclass` with a `to_dict()` method — the same pattern applied to the
  accumulator; Sub-Task 5 applies it to the snapshot.
- **Only frozen dataclass in codebase:** `Document` in `src/validation/corpus.py`
  at line 29 — confirms `@dataclass(frozen=True)` is an accepted pattern here.
- **All 17 mutation sites** for `l1_hits`, `l2_hits`, `l3_hits`, `misses` are
  guarded by `_stats_lock` (confirmed in research). The snapshot block already
  captures them correctly. Sub-Task 5 only changes how the assembled locals are
  returned — no lock changes required.
- **30+ call sites** across 10 files all read the dict; none reference
  `CacheStatsSnapshot` directly. `to_dict()` maintains full backward compatibility.
- **mypy:** `@dataclass(frozen=True)` fields without defaults require positional
  or keyword arguments at construction time. mypy will flag a missing field as a
  `TypeError` at the `CacheStatsSnapshot(...)` call site in `stats()` — this is
  the structural enforcement the plan aims to achieve.

### Status

`[x] done`

---

## Validation Gate (all sub-tasks)

After all five sub-tasks are complete, run the full validation suite:

```bash
# Fast gate (cache + concurrency)
uv run pytest tests/cache/ tests/concurrency/ -v

# Full gate (excluding load/performance)
uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q

# Linting and type checking
uv run ruff check src/cache/ tests/cache/
uv run mypy src/cache/
```

**Pass criteria:**
- Zero new test failures
- Zero new ruff violations
- Zero new mypy errors (annotation-unchecked notes are acceptable)
- `stats()["l3_hits"]` key present and correct (Sub-Task 1)
- `contains()` with disabled flags returns correct result (Sub-Task 2)
- `src/cache/CONCURRENCY.md` exists and renders correctly (Sub-Task 3)
- Inline comment on `max_size` reads in `stats()` (Sub-Task 4)
- `CacheStatsSnapshot` dataclass exists in `src/cache/base.py` with all 26 typed
  fields; `stats()` returns `snapshot.to_dict()` (Sub-Task 5)
- All 26 expected keys present in `stats()` return dict (new regression test)

---

## Ordering Rationale

1 → 2 → 3 → 4 → 5. Sub-Tasks 1 and 2 carry code risk and go first; their tests
validate correctness before anything else changes. Sub-Task 3 (documentation) and
Sub-Task 4 (comment) have zero code risk and go next. Sub-Task 5 touches `stats()`
a second time but only rewrites the assembly step, not the lock structure or key
set — it must come after Sub-Task 1 so the 26th key (`l3_hits`) is already present
when the dataclass field table is written.

---

*Created: 2026-07-18*
*Updated: 2026-07-18 — added Sub-Task 5 (CacheStatsSnapshot) and design decisions*
*Branch: fix-multilevel-cache-race*
