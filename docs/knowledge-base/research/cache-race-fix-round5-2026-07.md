---
title: Cache Thread-Safety Audit — Round 5 Lessons Learned
category: research
tags: [cache, thread-safety, concurrency, stats-snapshot, CacheStatsSnapshot, dataclass, contains, l3_hits, frozen-dataclass, structural-enforcement]
created: 2026-07-18
updated: 2026-07-18
status: active
priority: P1
branch: fix-multilevel-cache-race
---

# Cache Thread-Safety Audit — Round 5 Lessons Learned

## Objective

Document the three remaining gaps found after Rounds 1–4 were confirmed green, and
the structural improvement (`CacheStatsSnapshot`) that makes future gaps
self-detecting at build time. This document is the compact reference so future
sessions do not re-derive from the `fix-multilevel-cache-race` branch history.

Prior rounds are documented in
[`cache-race-fix-lessons-2026-07.md`](./cache-race-fix-lessons-2026-07.md).

---

## Background

After Rounds 1–4 closed 14 races (R-1–R-6, N-1–N-4, O-1–O-2, S-1–S-2) and the full
suite reached 1109 tests passing, a fresh T1–T4 audit pass on the same code found
three further issues and motivated one structural improvement.

| Round | IDs | Nature |
|---|---|---|
| 5A | A | `stats()` omits `l3_hits` from snapshot and return dict |
| 5B | B | `contains()` ignores `l1_enabled` / `l2_enabled` flags |
| 5C | C–D | `CONCURRENCY.md` missing; `max_size` reads undocumented |
| 5E | E | No structural enforcement of snapshot discipline |

---

## Findings

### Round 5A — `l3_hits` missing from `stats()` (Bug — Medium)

**Root cause:** The `with self._stats_lock:` snapshot block in `stats()` captured
`l1_hits`, `l2_hits`, `misses`, and `promote_l2_hits` but never `l3_hits`.
The return dict had no `"l3_hits"` key, and `"total_hits"` was computed as
`l1_hits + l2_hits`, silently excluding all L3 activity.

**Impact:**
- Any caller accessing `stats()["l3_hits"]` received a `KeyError`.
- `total_hits` diverged from the true lookup count when an L3 index was wired.
- The discrepancy was invisible — no exception, just silent under-counting.

**Why it survived Rounds 1–4:** `l3_hits` was added to `reset_stats()` and `clear()`
correctly (those had explicit `l3_hits = 0` lines). The `stats()` snapshot block
was not updated in the same commit. This is the exact pattern that `CacheStatsSnapshot`
(5E) is designed to prevent.

**Fix:**
```python
# stats() snapshot block — add l3_hits alongside the other counters
with self._stats_lock:
    l1_hits = self.l1_hits
    l2_hits = self.l2_hits
    l3_hits = self.l3_hits          # ← added
    misses = self.misses
    promote_l2_hits = self.promote_l2_hits

# return dict
"total_hits": l1_hits + l2_hits + l3_hits,   # ← was l1_hits + l2_hits
"l3_hits": l3_hits,                           # ← new key
```

**Test added:** `test_stats_includes_l3_hits` in `TestMultiLevelCacheL3` —
asserts key presence, value equality, `total_hits` includes L3, and
`total_requests == total_hits + total_misses` invariant.

---

### Round 5B — `contains()` ignores `l1_enabled` / `l2_enabled` (Bug — Medium)

**Root cause:** `contains()` at line 492 queried both sub-caches unconditionally:

```python
# Before fix (WRONG)
return self.l1_cache.contains(key, version) or self.l2_cache.contains(key, version)
```

`get()` gates on `self.l1_enabled` (line 153) and `self.l2_enabled` (line 169).
`set()` gates on both flags (lines 267–270). `contains()` skipped both.

**Impact:**  When `l1_enabled=False`, `contains()` could return `True` for a key
that `get()` would skip entirely — a false positive that breaks caller pre-flight
checks. When `l2_enabled=False`, the same for L2.

**Why it survived Rounds 1–4:** Rounds 1–4 focused on locking and snapshot
discipline. The `l1_enabled` / `l2_enabled` flag-consistency audit (T4 —
alternative paths) was not applied to `contains()`, only to `get_with_level()`.

**Fix:**
```python
def contains(self, key, version=None) -> bool:
    if self.l1_enabled and self.l1_cache.contains(key, version):
        return True
    if self.l2_enabled and self.l2_cache.contains(key, version):
        return True
    return False
```

Short-circuit semantics of the original `or` expression are preserved.
L1 is tried first; if `True`, L2 is not queried.

**Test added:** `test_contains_respects_disabled_flags` in `TestMultiLevelCache` —
covers L1-off (found in L2), L2-off (found in L1), both-off (returns False).

---

### Round 5C — `CONCURRENCY.md` missing (Hygiene — Low)

**Gap:** The 4-tier audit checklist and lock-order rule (`SemanticCache._lock`
before `MultiLevelCache._stats_lock`) existed only in the KB at
`docs/knowledge-base/research/iterative-audit-lessons-2026-07.md`. No contributor
modifying `src/cache/` would find them without knowing to check the KB.

**Fix:** Created `src/cache/concurrency.md` co-located with the code, containing:
- Lock inventory table (3 classes, 3 mechanisms)
- Lock-ordering rule with the one live call path that creates it
- Snapshot pattern with before/after code examples
- 4-tier audit checklist (T1–T4 + artifact hygiene), verbatim from KB
- Rule for adding new counters: "add to stats(), dataclass, reset_stats(), and
  clear() **in the same commit**"
- References to KB narrative docs

**Rule established:** The advisory N-5 comment in `SemanticCache.stats()` remains;
`CONCURRENCY.md` supersedes it as the authoritative reference.

---

### Round 5D — `max_size` cross-class reads undocumented (Fragility — Low)

**Gap:** `stats()` reads `self.l1_cache.max_size` and `self.l2_cache.max_size`
directly at lines 397–404, outside any lock. This is safe today because `max_size`
is set in `__init__` and never mutated. But `similarity_threshold` had exactly the
same profile — "set in `__init__`, seemed safe to read directly" — until
`update_threshold()` made it mutable and Round 4 required adding `get_threshold()`.

Without a comment, the next reader cannot distinguish "safe because immutable" from
"not yet broken because no `resize()` API exists yet."

**Fix:** Added a 4-line block comment at the read sites documenting the
construction-time-only invariant and pointing to the `get_threshold()` pattern
as the model to follow if a `resize()` API is ever added.

---

### Round 5E — No structural enforcement of snapshot discipline (`CacheStatsSnapshot`)

**Root cause (structural, not a bug):** Every field added to `MultiLevelCache`
that should appear in `stats()` requires its author to manually:
1. Snapshot it in the `_stats_lock` block
2. Add it to the return dict
3. Add it to `reset_stats()` and `clear()`

Rounds 1–4 found a `stats()` snapshot failure **in every single round**.
The discipline is demonstrably not held by convention alone.

**Fix:** Introduced `CacheStatsSnapshot` — a `@dataclass(frozen=True)` in
`src/cache/base.py` with 21 typed fields covering all keys returned by `stats()`.

```python
@dataclass(frozen=True)
class CacheStatsSnapshot:
    total_requests: int
    total_hits: int
    total_misses: int
    hit_rate: float
    avg_lookup_time_ms: float
    version: str
    l1_hits: int
    l1_hit_rate: float
    l1_size: int
    l1_max_size: int
    l1_utilization: float
    l2_hits: int
    l2_hit_rate: float
    l2_size: int
    l2_max_size: int
    l2_utilization: float
    l2_similarity_threshold: float
    l2_avg_similarity: float
    l3_hits: int
    promote_l2_hits: bool
    unique_entries: int

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
```

`MultiLevelCache.stats()` now assembles a `CacheStatsSnapshot` instance and returns
`snapshot.to_dict()`. The lock structure is unchanged. All 30+ call sites continue
to receive a plain `dict` — no API change.

**What structural enforcement buys:**
- mypy raises a `TypeError` at the `CacheStatsSnapshot(...)` call site if any field
  is missing — the 5A bug (`l3_hits` omitted) would have been caught at
  type-check time, not in a Round-5 audit.
- The field table is the **visible, diffable snapshot contract** — reviewed on
  every PR that touches `stats()`.
- `@dataclass(frozen=True)` prevents post-construction mutation, making the
  snapshot semantics explicit.

**Precedents used:**
- `CacheStats` in `base.py` is already a `@dataclass` with `to_dict()` —
  same pattern applied to the mutable accumulator; 5E applies it to the snapshot.
- `Document` in `src/validation/corpus.py` is the only existing `frozen=True`
  dataclass in the project — confirms the pattern is accepted.

**Test added:** `test_stats_returns_all_expected_keys` in `TestMultiLevelCache` —
asserts all 21 expected keys are present and selected fields have correct types
(`int`, `float`, `bool`, `str`). Acts as a regression guard for future key
additions or renames.

---

## Test Count Progression

| State | Tests passing |
|---|---|
| Post-Round-4 | 1 109 |
| Post-Round-5 | **1 112** (+3) |

New tests: `test_stats_includes_l3_hits`, `test_contains_respects_disabled_flags`,
`test_stats_returns_all_expected_keys`.

---

## Key Principle: Structural Enforcement > Convention

The core lesson of Round 5 is that four rounds of auditing the same `stats()` method
did not prevent a fifth gap. The right response is not a fifth audit pass — it is
making the discipline structural so the compiler/type-checker enforces it.

**The hierarchy, from weakest to strongest:**

| Enforcement level | Example | When it catches the gap |
|---|---|---|
| Convention | "remember to add to stats()" | Never — human memory fails |
| Documentation | `CONCURRENCY.md` rule | At code review (if reviewer checks) |
| Test | `test_stats_returns_all_expected_keys` | At CI run (after the PR is written) |
| **Type system** | `CacheStatsSnapshot` required field | At `mypy` / build time |

`CacheStatsSnapshot` moves snapshot-discipline failures from "caught in Round N audit"
to "caught by mypy before the PR can merge."

---

## Rule: New Counter Checklist

When adding a new counter or flag to `MultiLevelCache`:

```
[ ] Add field to __init__ (initialize to 0 / False)
[ ] Add increment inside correct with self._stats_lock: block
[ ] Add field to CacheStatsSnapshot in src/cache/base.py — mypy will enforce stats()
[ ] Add field to stats() CacheStatsSnapshot constructor (mypy guides you here)
[ ] Add field to reset_stats() zero-out block under _stats_lock
[ ] Add field to clear() zero-out block under _stats_lock
[ ] Write a regression test asserting the counter appears in stats() output
```

All seven steps must be in the same commit. Deferring any step creates a gap that
survives until the next audit.

---

## Coverage and Quality Gates (post-Round-5)

| Gate | Value |
|---|---|
| Total tests | 1 112 passed / 23 skipped |
| Cache + concurrency tests | 146 / 146 |
| Global coverage | ≥80% (floor enforced by pyproject.toml) |
| ruff | Clean |
| mypy | Clean (0 errors, annotation-unchecked notes only) |

---

## Sources

- [`src/cache/multi_level_cache.py`](../../../src/cache/multi_level_cache.py) — A, B, D fixes
- [`src/cache/base.py`](../../../src/cache/base.py) — E: `CacheStatsSnapshot` definition
- [`src/cache/concurrency.md`](../../../src/cache/CONCURRENCY.md) — C: in-tree reference
- [`tests/cache/test_multi_level_cache.py`](../../../tests/cache/test_multi_level_cache.py) — new regression tests

## Related Documents

- [Cache Thread-Safety Audit — Rounds 1–4](./cache-race-fix-lessons-2026-07.md)
- [Iterative Audit Methodology — Lessons Learned](./iterative-audit-lessons-2026-07.md)
- [Multi-Level Caching](../concepts/multi-level-caching.md)
- [Cache API Reference](../references/cache-api.md)

---
*Last Updated: 2026-07-18*
*Category: Research*
