# Concurrency Reference — `src/cache/`

This file is the **operational concurrency reference** for the `src/cache/` package.
Read it before modifying any field, method, or lock in `ExactCache`, `SemanticCache`,
or `MultiLevelCache`. The narrative history (root-cause analysis, fix rounds 1–4) is
in the KB at
[`docs/knowledge-base/research/cache-race-fix-lessons-2026-07.md`](../../docs/knowledge-base/research/cache-race-fix-lessons-2026-07.md).

---

## Lock Inventory

| Class | File | Lock | Mechanism |
|---|---|---|---|
| `ExactCache` | `exact_cache.py` | `self._lock` | `_synchronized` decorator wrapping `threading.RLock` |
| `SemanticCache` | `semantic_cache.py` | `self._lock` | `threading.RLock()` on the instance |
| `MultiLevelCache` | `multi_level_cache.py` | `self._stats_lock` | `threading.RLock()` guards counters and flags only |

`MultiLevelCache` does **not** hold a lock over its sub-caches. Each sub-cache
is internally thread-safe under its own lock. `_stats_lock` only guards the
counters (`l1_hits`, `l2_hits`, `l3_hits`, `misses`) and the `promote_l2_hits`
flag that live directly on the `MultiLevelCache` instance.

---

## Lock Ordering Rule

```
SemanticCache._lock  must always be acquired BEFORE  MultiLevelCache._stats_lock
```

There is exactly **one call path** in the current code that creates this ordering:

```
MultiLevelCache.stats()
  └── self.l2_cache.average_similarity_score()   ← acquires SemanticCache._lock
```

At the point `average_similarity_score()` is called, `_stats_lock` is already
released (the counter snapshot block has exited). The ordering is therefore safe.

**Deadlock risk:** Any future code that calls a method acquiring `_stats_lock`
from *inside* `SemanticCache._lock` would invert this order and create a deadlock.
Before adding such a call, verify the full acquisition chain.

---

## Snapshot Pattern

**Rule:** Any method that reads two or more guarded fields to compute a derived
value (`hit_rate`, `total_hits`, `stats()`) must snapshot **all** fields in a
**single** lock block, then compute from the local copies outside the lock.

### Wrong — two separate reads (TOCTOU window)

```python
# BAD: a thread switch between the two reads produces a mathematically invalid rate
rate = (self.l1_hits / (self.l1_hits + self.l2_hits + self.misses)) * 100
```

### Correct — single lock block, compute outside

```python
# GOOD: consistent snapshot, arithmetic outside the lock
with self._stats_lock:
    l1 = self.l1_hits
    l2 = self.l2_hits
    l3 = self.l3_hits
    m  = self.misses

total = l1 + l2 + l3 + m
rate  = ((l1 + l2 + l3) / total * 100) if total else 0.0
```

### Cross-class field reads

Reading a field owned by another class's lock requires going through a
**lock-guarded accessor** on the owner class, not a direct attribute access.

```python
# BAD: self.l2_cache.similarity_threshold read without SemanticCache._lock
threshold = self.l2_cache.similarity_threshold

# GOOD: lock-guarded accessor on the owner
threshold = self.l2_cache.get_threshold()   # acquires SemanticCache._lock internally
```

**Exception:** Fields that are assigned once in `__init__` and never mutated
afterwards (e.g. `max_size`) are safe to read directly. Document this invariant
with an inline comment at each read site so future maintainers do not need to
re-derive it.

---

## `stats()` Is the Concurrency Canary

`stats()` reads every guarded field simultaneously to produce a consistent
snapshot. It is where all snapshot-consistency failures manifest first.

**Rule for adding a new counter or flag to `MultiLevelCache`:**

1. Add the field to `__init__` (initialize under `_stats_lock` is not required
   for initialization, but all subsequent reads/writes must be).
2. Add the increment/decrement inside the appropriate `with self._stats_lock:` block.
3. Add the field to the snapshot block at the top of `stats()` **in the same
   commit** that adds the field.
4. Add the field to `CacheStatsSnapshot` in `src/cache/base.py` **in the same
   commit** — mypy will then enforce its presence at the construction site.
5. Add the field to the `reset_stats()` and `clear()` zero-out blocks.

Deferring step 3, 4, or 5 to a later commit creates a race window that will
survive until a future audit catches it.

---

## 4-Tier Audit Checklist

Run this checklist after any concurrency change to `src/cache/`. T1 is a
grep-level pass (~2 min); T2–T4 each take 10–15 minutes.

```
T1 — Structural (grep-based)
[ ] Every field incremented/decremented/cleared outside __init__ is inside a lock block
[ ] No dict/list iteration on a shared container without a lock

T2 — Snapshot consistency (per-method read)
[ ] Every multi-field read in stats() / hit_rate() / average_*() snapshots all
    fields in a single lock block before computing
[ ] No field read twice (double call to size(), double deque sum+len) — snapshot once

T3 — Cross-class boundary (cross-file grep)
[ ] Every self.other_cache.field read uses a lock-guarded accessor on the owner class
[ ] No direct attribute access on a sub-cache object that writes to that attribute
    under its own lock

T4 — Alternative paths (method comparison)
[ ] Every public method that performs a lookup (get, get_with_level, contains, etc.)
    either delegates to the canonical method or explicitly replicates all accounting
[ ] Search for methods calling self.l1_cache.get / self.l2_cache.get directly —
    they must also update hit counters and promotion logic

Artifact hygiene
[ ] No plan/scratch .md files at repo root
[ ] No orphaned README*.md duplicates
```

---

## References

- [`multi_level_cache.py`](multi_level_cache.py) — counters, flags, `stats()`, promotion
- [`semantic_cache.py`](semantic_cache.py) — `self._lock`, `get_threshold()`, `average_similarity_score()`
- [`exact_cache.py`](exact_cache.py) — `_synchronized` decorator, `snapshot_keys()`
- [`base.py`](base.py) — `CacheStats` accumulator, `CacheStatsSnapshot` frozen dataclass
- [KB narrative](../../docs/knowledge-base/research/cache-race-fix-lessons-2026-07.md) — Rounds 1–4 root-cause analysis
- [Audit methodology](../../docs/knowledge-base/research/iterative-audit-lessons-2026-07.md) — why the audit tiers exist

---

*Last updated: 2026-07-18 · Branch: fix-multilevel-cache-race*
