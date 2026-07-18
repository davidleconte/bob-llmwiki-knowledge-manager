---
title: KB Leveraging Across Mode Switches — Lessons Learned
category: research
tags: [knowledge-base, mode-switch, bobcoins, leveraging, agents-md, session-analysis]
created: 2026-07-18
updated: 2026-07-18
status: active
priority: P1
---

# KB Leveraging Across Mode Switches — Lessons Learned

## Objective

Understand how and when the Knowledge Base is actually leveraged during a Bob
session that spans multiple modes, measure the real savings that occurred, and
identify the structural gaps that prevented full leveraging.

## Background

This session (2026-07-18) involved the following mode transitions:

```
knowledge-manager → agent → knowledge-manager → agent
```

Tasks performed: MCP diagnosis, savings measurement guide, automated test suite
(`tests/validation/test_km_savings.py`), 19-pair corpus measurement, README update,
AGENTS.md KB-first protocol.

---

## Findings

### Finding 1: KB was leveraged for strategy, not for implementation

**What happened:**
KB docs were read for conceptual and strategic tasks — understanding the savings
model, the measurement methodology, existing analysis. Those reads replaced much
larger raw-source reads (full research reports, full analysis documents).

KB docs were NOT used for implementation work — writing the test file required
reading raw source because KB docs describe *what* the system does, not the exact
function signatures, return shapes, and fixture patterns needed to write code.

**Evidence:**

| KB doc read | Tokens saved vs raw source |
|---|---|
| `concepts/token-optimization.md` | ~4,200 tokens (vs full `src/optimizer/` tree) |
| `concepts/multi-level-caching.md` | ~3,900 tokens (vs `src/cache/` tree) |
| `research/bobcoin-savings-analysis-2026-07-14.md` | ~4,500 tokens (vs re-deriving) |
| `references/kb-savings-estimation-methodology.md` | ~2,200 tokens (vs re-deriving) |

**Conclusion:** KB docs at the concept/research level are high-value. API-level
detail (exact function signatures, fixture patterns) is legitimately absent — that
is correct KB design.

---

### Finding 2: One genuine miss — cost-tracking-guide.md

`src/monitoring/cost_tracker.py` was read raw when
`docs/knowledge-base/guides/cost-tracking-guide.md` existed and covered the same
content at a useful level. The KB-first protocol was not yet in AGENTS.md at that
point in the session, so the miss was structural, not behavioural.

**Tokens wasted:** ~3,450 (the raw file) instead of ~3,200 (the KB guide) — small
in absolute terms, but the pattern matters at scale.

---

### Finding 3: AGENTS.md had a broken architecture pointer (blocking)

`"Read architecture first — Check ACTUAL_SYSTEM_ARCHITECTURE.md"` pointed at a
file deleted in a prior session. Any mode following this instruction would get a
file-not-found, fall back to raw source, and pay full codebase read cost.

**Fix applied:** Replaced with correct pointers to `docs/architecture/ARCHITECTURE.md`
(TOS) and `docs/kb-manager/ARCHITECTURE.md` (KB Manager).

---

### Finding 4: Mode switches reset context — KB is not auto-loaded

When switching from knowledge-manager to agent mid-session, the context window
resets. KB docs read in the previous mode are gone. The new mode starts cold.

**Consequence:** Without an explicit KB-first instruction in AGENTS.md, every
mode switch is a full cold start at raw-source cost, even when relevant KB docs exist.

**Fix applied:** New "KB-First Protocol" section added at the top of AGENTS.md,
injected into every mode on every session, with a task-to-KB-doc lookup table.

---

### Finding 5: The 19-pair measurement revealed a KB design anti-pattern

Running the shadow comparison on 19 real source→KB file pairs showed that 9 of 19
pairs had **negative savings** — the KB doc was larger than the raw source.

Root cause: those "KB docs" are comprehensive guides, research reports, and
implementation plans — legitimate KB artefacts serving a different purpose
(documentation, planning) rather than compact summaries for re-derivation avoidance.

**Two distinct KB document roles confirmed:**

| Role | Purpose | Re-derivation saving |
|---|---|---|
| **Compact summary** | Replaces reading raw source | ✅ ~51% (N=10, CI [38%, 64%]) |
| **Guide / research / plan** | Documentation, decision records | ❌ 0% or negative |

Both are valuable. Only the first type saves Bobcoins on source queries.

---

## Analysis

### What "KB leveraged" actually means

There are three distinct senses in which the KB can be leveraged, and they have
different values:

1. **Retrieval** — A KB doc answers a query that would otherwise require reading
   raw source. This is re-derivation avoidance. Measured at ~51% token saving on
   well-formed pairs.

2. **Guidance** — AGENTS.md points agents at KB docs as the first step for
   recurring task types. This fires automatically on every session start,
   regardless of mode.

3. **Compounding** — Each session that writes a new KB doc increases the hit rate
   for future sessions. The investment is front-loaded; the return accumulates.

This session contributed to all three: it read existing KB docs (retrieval), fixed
AGENTS.md to make guidance systematic (guidance), and wrote new KB docs and test
harnesses that future sessions can retrieve (compounding).

### The AGENTS.md gap was the single largest structural deficiency

The KB had good content. The problem was that no mode other than knowledge-manager
had any instruction to look there. Without AGENTS.md carrying the KB-first protocol,
the KB was invisible to Plan mode, Agent mode, and any custom mode.

**After this session:** every mode receives the KB-first table at session start.
The re-derivation saving is now structural (always fires) rather than opportunistic
(fires only when the agent happens to remember).

---

## Conclusions

### Recommendations

1. **Keep AGENTS.md KB-first table current** — when a new high-value KB doc is
   added (concept or well-formed summary), add it to the task-type lookup table in
   AGENTS.md. Stale pointers are worse than no pointers (they cause file-not-found
   fallback to raw source).

2. **Distinguish KB doc types when measuring savings** — compact summaries and
   comprehensive guides serve different purposes. Measure re-derivation savings only
   on the compact-summary population; don't penalise guides for being large.

3. **For implementation tasks, KB docs are insufficient** — raw source reads are
   legitimately required for exact function signatures, return types, and fixture
   patterns. The KB should cover the *why* and *what*; the code covers the *how*.
   Don't over-index on KB coverage for implementation-level detail.

4. **Session cost is dominated by implementation, not by strategic queries** —
   the large token costs in this session were test-writing (reading 6+ source files)
   and measurement scripting. KB docs did not and could not replace those. Focus
   KB investment on the queries that recur across many sessions (architecture,
   configuration, API shape) not on one-off implementation details.

5. **The null guard is the right defensive mechanism** — `check_for_verbatim_duplication()`
   and the shadow comparison test correctly surface KB docs that provide no
   re-derivation saving. Run the measurement harness periodically to catch newly
   mismatched pairs.

### Next Steps

- [ ] Run `tests/validation/test_km_savings.py` monthly to detect KB docs that
      have grown larger than their sources (stale or scope-creep)
- [ ] Add a "compact summary" tag to KB docs that are designed for re-derivation
      avoidance, to distinguish them from guides/research/plans in the index
- [ ] Consider adding per-task token-cost logging to future sessions to build a
      real shadow-comparison dataset over time (Guide §2)

## Sources

- [`tests/validation/test_km_savings.py`](../../../tests/validation/test_km_savings.py) — 32-test automated measurement harness
- [`docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md`](../guides/km-bobcoin-savings-measurement-guide.md) — measurement protocol
- [`docs/knowledge-base/research/bobcoin-savings-analysis-2026-07-14.md`](./bobcoin-savings-analysis-2026-07-14.md) — theoretical analysis
- [`AGENTS.md`](../../../AGENTS.md) — KB-first protocol (updated this session)
- README.md §10 — published savings claims

## Related Documents

- [Bobcoin Savings Analysis 2026-07-14](./bobcoin-savings-analysis-2026-07-14.md)
- [KM Bobcoin Savings Measurement Guide](../guides/km-bobcoin-savings-measurement-guide.md)
- [KB Savings Estimation Methodology](../references/kb-savings-estimation-methodology.md)
- [Token Optimization](../concepts/token-optimization.md)
- [Cost Tracking Lessons Learned](./cost-tracking-lessons-learned.md)

---
*Last Updated: 2026-07-18*
*Category: Research*
