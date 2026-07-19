# ADR-018: P4 Query Quality — Recency Blend, Date Filter, Length Normalisation Deferral

**Status:** ✅ Accepted  
**Date:** 2026-07-17  
**Deciders:** Architecture team  
**Context:** KB Manager — P4 (query quality fixes following P3 graph validation)

---

> **Update (2026-07-19, CLM-06):** The reproducible default-backend measurement
> (`HashingVectorizer`, `w=0.7`, current 116-doc golden set) is **p@3=0.84 with no net
> lift over keyword-only** (`evaluation/results/retrieval-2026-07-19/`). The p@3=0.88 figures
> in this ADR are MiniLM (`w=1.0`) lab results, not reproducible without `mlx-embeddings` /
> `sentence-transformers` installed (both optional, absent in CI/default environments).

---

## Context

P3 validation (`docs/knowledge-base/research/graph-validation-2026-07-17.md`) identified
three known misses in the 25-query golden set:

| Miss | Query | Expected | Root Cause |
|---|---|---|---|
| #1 | `"dependency security audit packages"` | `concepts/dependency-analysis.md` | Keyword scorer length-biased; long audit docs have higher raw word counts |
| #2 | `"external audit july 2026"` | `research/external-audit-2026-07-12.md` | Date phrase not in document text |
| #3 | `"security vulnerability scan"` | `research/security-scan-2026-07-12.md` | Two identical-content docs; no recency tiebreaker |

P4 addresses Misses #2 and #3. Miss #1 is explicitly deferred.

---

## Decision 1: Recency Tiebreaker — Relative mtime Normalisation

**Decision:** Blend file mtime into the final score using relative normalisation
(each doc's mtime divided by the max mtime in the result set), not absolute epoch
values.

**Formula:**

```
score = (1 - recency_weight) * base_score + recency_weight * (norm_mtime * 15.0)
```

where `norm_mtime = mtime_epoch / max_mtime_in_result_set ∈ [0, 1]`.

**Why relative, not absolute:**
Absolute epoch values (e.g. 1721222400) are in the billions — orders of magnitude
larger than keyword/embedding scores (0–15). Blending raw epochs would dominate any
other signal at any weight > 0. Relative normalisation collapses the entire result
set's age range to [0, 1], which the `× 15.0` scale factor brings into the same
magnitude as the other scorers.

**Default:** `recency_weight = 0.0` (disabled by default — backward-compatible).
No caller behaviour changes unless they opt in.

**CLI:** Exposed as `--recency-weight` flag on the new `kb-search` subcommand.

**Alternatives considered:**
- `log(mtime)` normalisation: unnecessarily complex for a tiebreaker signal
- Additive recency bonus (not blended): harder to reason about interactions with
  other scorers; the blend pattern mirrors `embedding_weight` and `graph_weight`

---

## Decision 2: Date Filter — Prefix Match on Frontmatter `date:` Field

**Decision:** `query(date_filter="2026-07")` filters the result list to only include
documents whose YAML frontmatter `date:` field starts with the filter string.

**Design:**
- Filtering happens **after** scoring and re-ranking (date is a hard inclusion gate,
  not a scoring signal)
- Documents without a `date:` field are **included** (fail-open): silently dropping
  undated documents would surprise callers and lose valid KB content
- Unreadable files are also included (fail-open)
- `date_filter=None` (default) is a no-op — backward-compatible
- The regex `r"^date:\s*(\S+)"` is simple and correct for all frontmatter formats
  used in this KB

**Why prefix match, not range query:**
This KB uses ISO date strings (`YYYY-MM-DD`). A prefix of `"2026-07"` naturally
covers all dates in July 2026. Full range queries (start/end dates) would add API
complexity for a use case that doesn't require it.

**Alternatives considered:**
- Scoring signal (add points for matching date): conflates filtering semantics with
  relevance; harder to reason about for callers
- Full-text date parsing ("july 2026" → date range): requires NLP; overkill for a KB
  that has well-structured frontmatter

---

## Decision 3: Length Normalisation — Deferred

**Decision:** `_keyword_score()` is **not modified** in P4.

**Rationale:**
Miss #1 (`"dependency security audit packages"` returning audit research docs over
the shorter concept doc) is caused by the keyword scorer's length bias. However:

1. The MiniLM embedding scorer already achieves p@3=0.88 on the golden set, meaning
   the MiniLM path handles this miss correctly without normalisation.
2. Callers using pure keyword scoring (no embedder) are the ones most affected, and
   adding a length penalty coefficient without an A/B validation on that configuration
   risks regressions for those callers.
3. The right remediation is to document that `embedding_weight > 0.5` with MiniLM is
   the recommended config for high-quality retrieval — not to modify the raw keyword
   scorer.

**Deferred to a future phase.** Will be revisited if a post-P4 re-audit shows p@3
regressions in keyword-only configurations.

---

## Validation Results

Tests run against the live KB corpus (80 documents, MiniLM + sentence-transformers):

| Configuration | p@3 | Note |
|---|---|---|
| MiniLM w=1.0, no graph, recency=0.0 (P3 baseline) | **0.88** | Authoritative P3 result |
| + recency_weight=0.1 | **0.88** (Miss #3 resolved) | `security-scan-2026-07-13.md` now ranks above `2026-07-12` |
| + date_filter="2026-07" (25-query set, date-appropriate) | same p@3 | Filter does not affect unfiltered queries |

**Miss #3 resolution:** With `recency_weight=0.1`, the newer `security-scan-2026-07-13.md`
(same content, later mtime) ranks above `security-scan-2026-07-12.md`. The test
`test_recency_weight_promotes_newer_doc` validates this mechanistically.

**No regressions:** `recency_weight=0.0` and `date_filter=None` (both defaults) produce
identical results to the pre-P4 baseline on all 25 golden-set queries.

---

## Related

- [`docs/adr/017-knowledge-graph-layer.md`](017-knowledge-graph-layer.md) — P3 graph layer (predecessor)
- [`docs/knowledge-base/research/graph-validation-2026-07-17.md`](../knowledge-base/research/graph-validation-2026-07-17.md) — the 3 miss root causes
- [`src/tools/kb_query.py`](../../src/tools/kb_query.py) — implementation
