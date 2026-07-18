---
title: "Cache Thread-Safety Patterns"
category: concept
tags: [cache, thread-safety, concurrency, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Cache Thread-Safety Patterns

## Overview
The `src/cache/` package uses three interacting lock boundaries. Correctness requires four audit tiers — structural, snapshot consistency, cross-class reads, and alternative paths. Python's GIL does not substitute for explicit locking at any tier.

## Key Points
- One `RLock` per stateful class; never per-field locks
- **Snapshot before compute** — read all correlated fields in a single `with lock:` block, then compute from locals outside
- Cross-class field reads must use a lock-guarded accessor on the owner class
- `stats()` is the concurrency canary — if any field it reads is written anywhere without the lock, that is a race
- The GIL makes individual bytecodes atomic; it does not make multi-field invariants consistent

## Details

### Lock Map

| Class | Lock | Guards |
|---|---|---|
| `ExactCache` | `_lock` (RLock, via `_synchronized` decorator) | all public mutations |
| `SemanticCache` | `self._lock` (RLock) | `_similarity_scores`, `similarity_threshold`, cache dict |
| `MultiLevelCache` | `self._stats_lock` (RLock) | `l1_hits`, `l2_hits`, `misses`, `l3_hits`, `_lookup_times`, `promote_l2_hits` |

**Lock ordering (deadlock prevention):**
```
SemanticCache._lock  →  MultiLevelCache._stats_lock
```
Always acquired in this order. `MultiLevelCache.stats()` holds `_stats_lock` and then calls into `SemanticCache` methods — those methods must not re-acquire `_lock` in a way that inverts the order.

### The Four Audit Tiers

**T1 — Structural:** Missing locks entirely.
```bash
# Grep for mutations on shared fields outside lock blocks
grep -n "self\.\(l1_hits\|l2_hits\|misses\|l3_hits\) [+\-]=" src/cache/multi_level_cache.py
```

**T2 — Snapshot consistency:** Multiple reads of guarded fields in separate statements.
```python
# Wrong — thread switch between reads produces invalid rate
return self.l1_hits / (self.l1_hits + self.l2_hits + self.misses)

# Correct — snapshot once
with self._stats_lock:
    l1, l2, miss = self.l1_hits, self.l2_hits, self.misses
return l1 / (l1 + l2 + miss) if (l1 + l2 + miss) > 0 else 0.0
```

**T3 — Cross-class reads:** One class reads a field owned by another class's lock.
```python
# Wrong — SemanticCache._lock not held by MultiLevelCache
threshold = self.l2_cache.similarity_threshold

# Correct — guarded accessor on the owner class
threshold = self.l2_cache.get_threshold()   # SemanticCache.get_threshold() wraps with self._lock
```

**T4 — Alternative paths:** A method duplicates lookup logic without delegating to the canonical method, silently skipping all accounting.
```python
# Wrong — get_with_level() re-implements lookup, misses l1_hits/l2_hits/misses/promotion
def get_with_level(self, key, version):
    result = self.l1_cache.get(key)  # accounting never fires
    ...

# Correct — delegate to canonical, infer level from counter delta
def get_with_level(self, key, version):
    with self._stats_lock:
        l1_before = self.l1_hits
    result = self.get(key, version)   # all accounting fires inside get()
    with self._stats_lock:
        level = "L1" if self.l1_hits > l1_before else "L2"
    return (result, level)
```

### Why the GIL Does Not Save You

| Claim | True? | Why |
|---|---|---|
| `self.counter += 1` is atomic | ✅ Single bytecode | GIL guarantees single bytecode atomicity |
| Reading two counters is consistent | ❌ | Thread switch can occur between the two reads |
| `sum(list) / len(list)` is safe | ❌ | List can be cleared between `sum()` and `len()` |
| Flag + counter read together is consistent | ❌ | Thread switch between reads produces invalid combination |

**Rule of thumb:** If correctness requires two or more values to be read as a consistent snapshot, those reads must be in a single `with lock:` block — regardless of the GIL.

### stats() as the Canary
`stats()` is the only method that reads every guarded field simultaneously. Any race manifests there first.

**Checklist for every field added to a stateful cache class:**
1. Is the write inside the correct lock? 
2. Is the read in `stats()` inside the same lock block as all other fields it must be consistent with?
3. If the field comes from another object, is it accessed via a lock-guarded accessor?
4. Is `reset_stats()` resetting it under the lock?

### Race History Summary

| Round | IDs | Tier | Pattern |
|---|---|---|---|
| Phase 2 | — | T1 | Missing `_stats_lock` entirely on `MultiLevelCache` |
| Round 2 | N-1–N-4 | T2 | `SemanticCache` field reads outside `self._lock` |
| Round 3 | O-1, O-2 | T2, T4 | Promote-flag read split; `get_with_level` bypass |
| Round 4 | S-1, S-2 | T3, T2 | Cross-class threshold read; `unique_entries` TOCTOU |

## Examples

### Correct stats() snapshot pattern
```python
def stats(self) -> dict:
    with self._stats_lock:
        l1      = self.l1_hits
        l2      = self.l2_hits
        miss    = self.misses
        l3      = self.l3_hits
        promote = self.promote_l2_hits
        times   = list(self._lookup_times)   # snapshot deque
    l2_threshold = self.l2_cache.get_threshold()  # guarded accessor
    l1_size = self.l1_cache.size()
    l2_size = self.l2_cache.size()
    return {"l1_hits": l1, "l2_hits": l2, ...}
```

### Correct lock-guarded accessor pattern
```python
# On SemanticCache — called by MultiLevelCache without holding SemanticCache._lock
def get_threshold(self) -> float:
    with self._lock:
        return self.similarity_threshold
```

## Related Documents
- [Multi-Level Caching](./multi-level-caching.md)
- [Multi-Level Caching Architecture Patterns](./multi-level-caching-architecture-patterns.md)
- [Iterative Audit Methodology](./iterative-audit-methodology.md)
- [Cache Thread-Safety Audit — Rounds 1–4](../research/cache-race-fix-lessons-2026-07.md)
- [Cache Thread-Safety Audit — Round 5](../research/cache-race-fix-round5-2026-07.md)
- [Cache API Reference](../references/cache-api.md)

## References
- `src/cache/multi_level_cache.py` — primary implementation
- `src/cache/semantic_cache.py` — `_lock` owner
- `src/cache/concurrency.md` — lock-order rule and snapshot pattern reference
- `tests/concurrency/test_cache_concurrency.py` — race-detector regression tests

---
*Last Updated: 2026-07-18*
*Category: Concept*
