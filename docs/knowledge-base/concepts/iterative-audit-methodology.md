---
title: "Iterative Audit Methodology"
category: concept
tags: [audit, methodology, concurrency, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Iterative Audit Methodology

## Overview
A single audit pass on concurrency code almost never closes all races. Use four successive audit tiers — structural, snapshot consistency, cross-class reads, alternative paths — each requiring a different search lens. Stop only when all four tiers pass.

## Key Points
- "All fixed" after one audit pass is almost never true for concurrency code
- A passing test suite proves no *existing* test caught a race, not that no race exists
- `stats()` is the highest-value audit target in any stateful class — audit it at every tier
- Write a KB doc at the end of every fix session; the re-derivation saving on the next session pays for it in the first 5 minutes
- Alternative code paths that duplicate lookup logic silently skip all accounting

## Details

### The Four Audit Tiers

| Tier | What to look for | How to search | Typical time |
|---|---|---|---|
| **T1 — Structural** | Missing locks entirely; mutations outside any lock | `grep` for `+=`, `.clear()`, `del` on shared fields outside lock blocks | 5–10 min |
| **T2 — Snapshot consistency** | Multiple reads of guarded fields in separate statements | Read every read of each guarded field; verify they are in the same `with lock:` block | 10–15 min |
| **T3 — Cross-class reads** | One class reads a field owned by another class's lock without going through that lock | Enumerate all `self.other.field` accesses; verify each is via a guarded accessor on the owner | 10–15 min |
| **T4 — Alternative paths** | A method duplicates the canonical method's logic without delegating to it | Find all methods that call sub-cache methods directly; confirm they either delegate or replicate all accounting | 10 min |

**Order matters.** Run T1 first (fastest, broadest). Each subsequent tier requires the previous to be green. After a fix at any tier, re-run all previous tiers before moving forward.

### stats() as the Primary Audit Target
`stats()` is the only method that reads every guarded field simultaneously. Any snapshot-consistency failure manifests there first.

**Audit checklist for `stats()` at each tier:**
```
T1: Every field read is inside the correct lock block
T2: All fields that must be consistent are in a single lock block (not spread across multiple)
T3: Fields from other objects are accessed via guarded accessors, not direct attribute reads
T4: No field is populated by an alternative path that skips the canonical accounting
```

### Alternative Path Anti-Pattern
When a method duplicates lookup logic to add a variation (e.g. returning the cache level alongside the value), it typically omits the instrumentation the canonical method accumulated over time.

**Detection rule:** Find any public method that calls sub-cache methods directly (`self.l1_cache.get`, `self.l2_cache.get`) without calling the canonical method (`self.get`).

**Fix pattern — delegate and infer:**
```python
# Instead of re-implementing the lookup:
def get_with_level(self, key, version):
    with self._stats_lock:
        l1_before = self.l1_hits
    result = self.get(key, version)   # canonical path — all accounting fires
    with self._stats_lock:
        level = "L1" if self.l1_hits > l1_before else "L2"
    return (result, level) if result is not None else None
```

### Cross-Class Read Detection
After auditing a class in isolation, enumerate all `self.other.field` accesses and verify each is guarded by the owner's lock.

```python
# grep for cross-class field reads
grep -n "self\.l2_cache\.\|self\.l1_cache\." src/cache/multi_level_cache.py | grep -v "def \|#"
```

Any unguarded attribute access across a class boundary is suspect regardless of what other locks surround the call site.

### KB Compounding Within a Single Branch
Even within a single branch's lifetime, writing a KB doc at the end of a session and reading it at the start of the next one avoids re-deriving the lock mechanism, lock-order rule, and covered fields from raw source. Measured: ~3,200 tokens saved per session on `src/cache/multi_level_cache.py` re-reads.

### Regression Test Discipline
For each identified race:
1. Write a test that is demonstrably related to the race (use `sys.setswitchinterval(1e-7)` to maximise pre-emption)
2. Confirm the test would fail (or could fail) before the fix
3. Apply the minimal fix — synchronisation boundary only, no behaviour changes
4. Run the full suite: `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance`

Test count trajectory as a proxy for audit thoroughness:

| State | Tests |
|---|---|
| Pre-Round-1 (Phase 2 complete) | 1 088 |
| Post-Round-1 | 1 096 |
| Post-Round-2 | 1 102 |
| Post-Round-3 | 1 106 |
| Post-Round-4 | 1 109 |
| Post-Round-5 | 1 112 |

### Plan File Hygiene
Plan/scratch files belong in `docs/adr/` (decisions), `docs/project-management/plans/` (project artefacts), or deleted on merge. They do not belong at the repo root. Their presence at root signals the session that created them had no designated destination.

## Examples

### Audit Session Pattern
```
Session 1: T1 audit → fix structural gaps → suite green
Session 2: Read KB doc from session 1 → T2 audit → fix snapshot gaps → suite green
Session 3: Read KB doc from session 2 → T3+T4 audit → fix cross-class and path gaps → suite green
```

### Full Audit Checklist (src/cache/)
```
T1 — Structural
[ ] Every += / -= / .clear() / del on shared field is inside a lock block
[ ] No dict/list iteration on a shared container without a lock

T2 — Snapshot consistency
[ ] stats() / hit_rate() / average_*() snapshot all correlated fields in a single lock block
[ ] No field read twice (two calls to size(), sum+len on same deque) — snapshot once

T3 — Cross-class boundary
[ ] Every self.other_cache.field read uses a guarded accessor on the owner class
[ ] No direct attribute access on a sub-cache object that the sub-cache writes under its own lock

T4 — Alternative paths
[ ] Every public lookup method either delegates to self.get() or explicitly replicates all accounting
[ ] Methods calling self.l1_cache.get / self.l2_cache.get directly also update hit counters

Artifact hygiene
[ ] No plan/scratch .md files at repo root
[ ] No orphaned README*.md duplicates
```

## Related Documents
- [Cache Thread-Safety Patterns](./cache-thread-safety-patterns.md)
- [Multi-Level Caching](./multi-level-caching.md)
- [KB Document Types](./kb-document-types.md)
- [Iterative Audit — Lessons Learned](../research/iterative-audit-lessons-2026-07.md)
- [Cache Thread-Safety — Rounds 1–4](../research/cache-race-fix-lessons-2026-07.md)

## References
- `src/cache/concurrency.md` — lock-order rule, snapshot pattern reference
- `tests/concurrency/test_cache_concurrency.py` — race-detector regression tests
- `CHANGELOG.md` v1.1.0 — full fix record for Rounds 1–5

---
*Last Updated: 2026-07-18*
*Category: Concept*
