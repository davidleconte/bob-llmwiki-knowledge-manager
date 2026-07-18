---
title: Iterative Audit Methodology — Lessons Learned
category: research
tags: [audit, methodology, thread-safety, iterative-review, regression-testing, technical-debt, kb-workflow, stats-snapshot, cross-class-lock]
created: 2026-07-18
updated: 2026-07-18
status: active
priority: P1
branch: fix-multilevel-cache-race
---

# Iterative Audit Methodology — Lessons Learned

## Objective

Capture the process patterns, anti-patterns, and workflow learnings from three
successive "audit and advise" sessions on the `fix-multilevel-cache-race` branch.
The content here is about *how to audit well*, not about the specific cache bugs
(those are in [`cache-race-fix-lessons-2026-07.md`](./cache-race-fix-lessons-2026-07.md)).

---

## Background

Three audit sessions ran on this branch within a single day:

| Session | Trigger | Rounds closed | Tests added |
|---|---|---|---|
| 1 | `audit and advise` (no KB context yet) | — (prior work reviewed) | — |
| 2 | `audit and advise` (post KB refresh) | O-1, O-2 | +4 (→ 1106) |
| 3 | `fix remaining items` | S-1, S-2, S-3, S-4 | +3 (→ 1109) |

The cascade — audit → fix → re-audit → more fixes → re-audit — is itself the
subject of this document.

---

## Findings

### Finding 1: "All fixed" after one audit pass is almost never true for concurrency code

**What happened:**  
Round 1 (Phase 2, 2026-07-13) fixed the most visible races: missing `_stats_lock`,
unguarded iteration. After those fixes the full suite passed. Yet four more rounds of
issues were found on the same code in subsequent sessions.

**Why:**  
Concurrency bugs have three distinct audit tiers that require different search strategies:

| Tier | What to look for | Typical tool |
|---|---|---|
| **T1 — Structural** | Missing locks entirely; mutation without any lock | Grep for `+=`, `.clear()`, `del` on shared fields outside lock blocks |
| **T2 — Snapshot consistency** | Multiple reads of guarded fields without a single lock block | Read all reads of each field; check they all occur inside the same `with self._lock` |
| **T3 — Cross-class / cross-boundary** | One class reads a field owned by another class's lock | Grep for `self.other_cache.field` outside the other class's lock |

Rounds 1–2 caught T1. Rounds 3–4 caught T2 and T3 respectively. Each tier requires
a fresh pass with a different search lens.

**Recommendation:**  
After any concurrency fix, re-run the audit at the *next tier* before declaring
closure. A passing test suite is necessary but not sufficient — it proves no
existing test caught a race, not that no race exists.

---

### Finding 2: Alternative code paths silently bypass accounting

**What happened (O-2):**  
`get_with_level()` was a second implementation of the two-level lookup that never
called `get()`. All stats accounting (`l1_hits`, `l2_hits`, `misses`,
`_lookup_times`) was silently missing for every call through this path. `hit_rate()`,
`stats()`, and `average_lookup_time_ms()` all silently under-reported.

**Root cause pattern:**  
When a method duplicates the logic of another method to add a small variation
(here: returning the cache level alongside the value), it often omits the
instrumentation the original accumulated over time.

**Detection rule:**  
Any public method that performs an operation similar to another public method
but does not call it is a candidate for this pattern. Search for methods that:
1. Call the same sub-cache methods (`self.l1_cache.get`, `self.l2_cache.get`)
2. Do not delegate to the canonical method (`self.get`)

**Fix pattern:**  
Delegate to the canonical method; infer the variation (level label) from observable
side-effects (counter delta under lock) rather than re-implementing the lookup:

```python
with self._stats_lock:
    l1_before = self.l1_hits
result = self.get(key, version)          # canonical path — all accounting fires
with self._stats_lock:
    level = "L1" if self.l1_hits > l1_before else "L2"
```

---

### Finding 3: Cross-class field reads are invisible to single-class audits

**What happened (S-1):**  
`MultiLevelCache.stats()` read `self.l2_cache.similarity_threshold` directly.
`SemanticCache.update_threshold()` writes it under `self._lock`. The read in
`stats()` was outside both `self._stats_lock` and `self.l2_cache._lock`.

**Why it was missed:**  
A per-class audit of `SemanticCache` would see `update_threshold()` is guarded —
correct. A per-class audit of `MultiLevelCache` would see its own `_stats_lock`
is used — correct. The gap only appears when auditing the *cross-class boundary*:
"for every field F owned by class B, find all reads of F in class A and verify
they are guarded by B's lock."

**Detection rule:**  
After auditing a class in isolation, enumerate all `self.other.field` accesses
in that class and verify each field is read via a lock-guarded accessor on the
owner class. An unguarded attribute access across a class boundary is always
suspect regardless of what locks surround it.

**Fix pattern:**  
Add a lock-guarded accessor (`get_threshold()`) to the owner class. Mirror the
`average_similarity_score()` pattern already established for `_similarity_scores`.
The accessor is minimal (3 lines) and makes the contract explicit.

---

### Finding 4: `stats()` is the highest-value audit target in any stateful class

**Pattern observed across all four rounds:**  
Every round found an issue in or called from `stats()`:
- Round 1: counter reads without `_stats_lock`
- Round 2: `promote_l2_hits` read outside lock block in `stats()`
- Round 3: `stats()` called `self.size()` twice producing TOCTOU
- Round 4: `stats()` read cross-class field without owner's lock; `unique_entries`
  snapshot at wrong moment

**Why `stats()` concentrates races:**  
`stats()` is the only method that reads *every* guarded field simultaneously to
produce a consistent snapshot. Any field that is not read atomically with the others
will be at a different moment in time. It is the natural aggregation point for
all snapshot-consistency failures in the class.

**Rule:**  
Treat `stats()` as the primary audit target. For every value it returns, ask:
1. Is the field read inside the correct lock?
2. Is it read in the same lock block as the other fields it must be consistent with?
3. If it comes from another object, is it read via a lock-guarded accessor?

---

### Finding 5: The KB-first protocol saves re-derivation even within a single session

**What happened:**  
The second audit session ("audit and advise") opened with the KB doc written at the
end of the first session (`cache-race-fix-lessons-2026-07.md`). The existing Round 1
and Round 2 findings were immediately available without re-reading source. The
session skipped directly to auditing for T2/T3 gaps rather than re-discovering T1.

**Measured saving:**  
~3,200 tokens not spent re-reading `multi_level_cache.py` from scratch. The prior
audit had already identified the lock mechanism, lock-order rule, and covered fields
— all of that was in the KB doc.

**Implication:**  
Even within a single branch's lifetime, writing a KB doc at the end of a session
and reading it at the start of the next one produces compounding value. The investment
is ~5 minutes of writing; the return is the full source-read cost on every subsequent
session that touches the same file.

---

### Finding 6: Plan files at the repo root are technical debt from their first commit

**What happened (S-3):**  
`cache-race-fixes-plan.md` and `cache-race-fixes-round2-plan.md` were created at
the root during the fix sessions to hold sub-task specifications. By the time the
fixes were complete, both were fully superseded: the CHANGELOG.md entries describe
every fix, the KB research doc summarises every finding, and the test files are the
ground truth. The plan files became noise that showed up in `git diff --stat` and
`ls` output.

**Rule:**  
Plan/scratch files belong in one of three places:
1. **`docs/adr/`** — if the decision is architectural and needs a permanent record
2. **A task-tracking tool** — if it is transient work breakdown
3. **Deleted on branch merge** — if it is session scaffolding

They do not belong at the repo root. The presence of a plan file at root signals
the session that created it did not have a designated place to put transient work.

---

## Audit Checklist Derived from These Sessions

For any future concurrency audit of `src/cache/`:

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

## Summary Table: Race Taxonomy

| ID range | Tier | Root cause pattern | Fix pattern |
|---|---|---|---|
| R-1–R-6 | T1 | No lock on `MultiLevelCache` counters | Add `_stats_lock`; wrap all reads/writes |
| N-1–N-4 | T2 | `SemanticCache` field reads outside `self._lock` | Snapshot under lock; single lock block |
| O-1 | T2 | Flag read split from counter increment | Snapshot flag inside same lock block as counter |
| O-2 | T4 | Alternative path bypassed canonical method | Delegate to canonical; infer label from delta |
| S-1 | T3 | Cross-class field read without owner's lock | Add `get_threshold()` accessor on owner |
| S-2 | T2 | `unique_entries` read after lock release | Inline computation alongside `snapshot_keys()` |

---

## Conclusions

### Recommendations

1. **Run all four audit tiers after every concurrency fix** — T1 is fast (grep);
   T2–T4 each take 10–15 minutes. Do not stop after T1 goes green.

2. **Add the audit checklist to `src/cache/CONCURRENCY.md`** (open `next step` from
   prior document) — a standing reference that any future contributor can follow.

3. **Write a KB doc at the end of every fix session** — even a short one. The
   re-derivation saving on the next session pays for it in the first 5 minutes.

4. **Do not create plan files at the repo root** — use `docs/adr/` for decisions
   or delete on merge. Plan file hygiene is enforced by the existing `git diff --stat`
   review gate.

5. **`stats()` is the concurrency canary** — any field added to the class that
   `stats()` should report must be added to `stats()` inside the correct lock block
   in the same commit that adds the field. Defer-and-patch creates a race window.

### Next Steps

- [ ] Create `src/cache/CONCURRENCY.md` with the lock-order rule, snapshot pattern,
      and the 4-tier audit checklist
- [ ] Add `tests/concurrency/` to the CI fast-path (currently skipped in coverage run)
- [ ] Consider a `CacheStatsSnapshot` dataclass so `stats()` returns a frozen object
      and the snapshot discipline is enforced structurally rather than by convention

## Sources

- [`src/cache/multi_level_cache.py`](../../../src/cache/multi_level_cache.py)
- [`src/cache/semantic_cache.py`](../../../src/cache/semantic_cache.py)
- [`src/cache/exact_cache.py`](../../../src/cache/exact_cache.py)
- [`tests/cache/test_multi_level_cache.py`](../../../tests/cache/test_multi_level_cache.py)
- [`tests/concurrency/test_cache_concurrency.py`](../../../tests/concurrency/test_cache_concurrency.py)
- [`CHANGELOG.md`](../../../CHANGELOG.md) — v1.1.0 Fixed sections (Rounds 1–4)

## Related Documents

- [Cache Thread-Safety Audit — Rounds 1–4 Lessons Learned](./cache-race-fix-lessons-2026-07.md)
- [Cache Thread-Safety Audit — Round 5 Lessons Learned](./cache-race-fix-round5-2026-07.md)
- [Repo Hygiene — Lessons Learned](./repo-hygiene-lessons-2026-07.md)
- [Phase 2 Thread Safety Fixes Complete](./phase2-thread-safety-fixes-complete.md)
- [Phase 2 Concurrency Test Results](./phase2-concurrency-test-results.md)
- [KB Leveraging Across Mode Switches — Lessons Learned](./kb-mode-switch-lessons-2026-07.md)
- [Multi-Level Caching](../concepts/multi-level-caching.md)
- [Cache API Reference](../references/cache-api.md)

---
*Last Updated: 2026-07-18*
*Category: Research*
