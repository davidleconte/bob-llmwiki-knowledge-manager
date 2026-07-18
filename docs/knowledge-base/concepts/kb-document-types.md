---
title: "KB Document Types"
category: concept
tags: [knowledge-base, document-types, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# KB Document Types

## Overview
The knowledge base contains two fundamentally different document roles. Only **compact summaries** produce re-derivation savings. **Comprehensive documents** (guides, research, plans) serve documentation and decision purposes — measuring them against the re-derivation saving metric is a category error.

## Key Points
- A KB doc that is *larger* than its source is not a bad KB doc — it is likely a guide or research note serving a different purpose
- Only compact summaries targeted at "replace reading the raw source" produce Bobcoin savings
- Measure savings only on the compact-summary population; report them separately
- 10 of 19 real pairs in this repo meet the compact-summary bar (51% mean saving, CI [38%, 64%])
- The other 9 are legitimate guides/research with negative savings — correct by design

## Details

### The Two Roles

| Role | Purpose | Bobcoin saving | Examples |
|---|---|---|---|
| **Compact summary** | Replaces reading raw source on a recurring query | ✅ ~51% mean (N=10) | `concepts/token-optimization.md`, `concepts/multi-level-caching.md` |
| **Comprehensive document** | Documentation, decisions, guides, research logs | ❌ 0% or negative (by design) | `guides/setup-token-optimization.md`, `research/phase2-lessons-learned-*` |

### When to Create Each Type

**Create a compact summary when:**
- A source file or module is queried repeatedly across many sessions
- The query is about *what the system does*, not *how to implement something*
- A ~200-line digest would fully answer the recurring question vs. reading the full source

**Create a comprehensive document when:**
- Capturing a decision, process, or experimental finding for future reference
- The audience needs the full detail, not just a digest
- The document is a research note, guide, or plan — not a source replacement

### The Compact-Summary Tag
Tag compact summaries in frontmatter to distinguish them from other KB docs:
```yaml
---
title: Token Optimization
category: concept
tags: [token-optimization, cache, compact-summary]
---
```
The `compact-summary` tag marks docs that qualify for the re-derivation saving measurement.

### Re-Derivation Saving Measurement
Shadow comparison via `tests/validation/test_km_savings.py`:
```bash
uv run pytest tests/validation/test_km_savings.py -v
```
Reports per-pair savings. Pairs where the KB doc is larger than the source are expected for guides/research — filter to `compact-summary`-tagged docs for the savings headline.

### Stale-Pair Detection
Run monthly. A KB doc that once summarised a module may grow larger than its source over time (scope creep) or the source may shrink (refactor). The test catches this:
```
FAILED tests/validation/test_km_savings.py::test_well_formed_pairs_have_positive_savings
```

### AGENTS.md Lookup Table
Only compact summaries belong in the task-to-KB-doc lookup table in `AGENTS.md`. A guide or research note cannot replace reading raw source for implementation tasks.

```markdown
| Work on the cache    | `docs/knowledge-base/concepts/multi-level-caching.md`       |
| Understand token opt | `docs/knowledge-base/concepts/token-optimization.md`        |
```
Do not add guides or research notes here — they are background reading, not source substitutes.

## Examples

```
# Compact summary (saves Bobcoins on source queries)
docs/knowledge-base/concepts/token-optimization.md       # ~200 lines vs src/optimizer/ tree
docs/knowledge-base/concepts/multi-level-caching.md      # ~180 lines vs src/cache/ tree

# Comprehensive document (correct size; different purpose)
docs/knowledge-base/guides/setup-token-optimization.md   # step-by-step guide
docs/knowledge-base/research/phase2-lessons-learned.md   # historical record
docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md  # methodology
```

## Related Documents
- [Token Optimization](./token-optimization.md)
- [Multi-Level Caching](./multi-level-caching.md)
- [KB Leveraging Across Mode Switches](../research/kb-mode-switch-lessons-2026-07.md)
- [KM Bobcoin Savings Measurement Guide](../guides/km-bobcoin-savings-measurement-guide.md)
- [KB Savings Estimation Methodology](../references/kb-savings-estimation-methodology.md)

## References
- `tests/validation/test_km_savings.py` — 32-test shadow comparison harness
- `research/bobcoin-savings-analysis-2026-07-14.md` — theoretical savings model
- `research/kb-mode-switch-lessons-2026-07.md` — Finding 5: two KB document roles

---
*Last Updated: 2026-07-18*
*Category: Concept*
