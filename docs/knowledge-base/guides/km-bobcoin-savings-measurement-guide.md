---
title: "Knowledge Manager Bobcoin Savings — Measurement Guide"
category: guides
tags: [guides]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Knowledge Manager Bobcoin Savings — Measurement Guide

## Overview

How to establish **credible, evidence-backed** Bobcoin savings from the Knowledge Manager (KM)
in your own Bob Shell workspace. The guide distinguishes what can be *directly counted* from
what must be *estimated with stated assumptions*, and explains how to build a defensible
savings claim over time.

---

## Prerequisites

- Bob Shell with the `knowledge-manager` mode active in this workspace
- A project KB under `docs/knowledge-base/` with at least a few populated documents
- At least 2 weeks of working sessions on the same codebase
- (Optional) access to the `bob-optimize` CLI or `src/monitoring/` metrics for token counting

---

## The Two Savings Mechanisms

The KM saves Bobcoins through two distinct mechanisms. Measure them **separately**; never blend
them into a single headline figure.

| Mechanism | What is saved | How to measure |
|---|---|---|
| **Re-derivation avoidance** | Tokens Bob would spend re-reading and re-analysing the codebase | Shadow comparison (Section 2) |
| **Context compression** | Tokens from sending a compact KB snippet instead of raw source | Direct token count diff (Section 3) |

---

## Section 1 — Establish a Baseline (Do This First)

Before you can claim savings you need a baseline cost per task type.

### 1.1 Identify your top 3-5 recurring query types

Examples:
- "What is the architecture of subsystem X?"
- "How do I configure feature Y?"
- "What did we decide about Z?"

### 1.2 Run a baseline session without the KB

For each query type, open a **fresh Bob Shell session** with the knowledge-manager mode but
*without* pre-loading any KB documents. Let Bob answer purely from raw source.

Record in a simple log (e.g. `docs/knowledge-base/research/km-savings-log-YYYY-MM.md`):

```
Date         | Query type              | Mode  | Input tokens | Output tokens | Total BC
2026-07-20   | architecture overview   | raw   | 42,300       | 820           | ~0.44
2026-07-20   | configure logging       | raw   | 8,400        | 310           | ~0.09
```

Token counts: Bob Shell displays the session cost in BC after each message. Use those directly.

### 1.3 Run the same queries with the KB loaded

Repeat the same queries in the next session, but this time reference the relevant KB document
explicitly (e.g. *"See `docs/knowledge-base/concepts/token-optimization.md` for context"*).

Add to the same log:

```
Date         | Query type              | Mode  | Input tokens | Output tokens | Total BC
2026-07-21   | architecture overview   | kb    | 5,200        | 790           | ~0.06
2026-07-21   | configure logging       | kb    | 1,100        | 305           | ~0.015
```

### 1.4 Compute the per-query savings

```
savings_pct = (raw_bc - kb_bc) / raw_bc × 100
```

Example:
- Architecture query: (0.44 - 0.06) / 0.44 = **86% savings**
- Logging config query: (0.09 - 0.015) / 0.09 = **83% savings**

> **Honesty note:** These are *best-case* figures. The KB document must fully answer the query —
> if Bob still needs to consult raw source, savings shrink proportionally.

---

## Section 2 — Shadow Comparison (Ongoing)

Shadow comparison is the most rigorous method. Run it on a sample of real working sessions.

### Protocol

1. **Tag sessions** by whether the KB was the primary context source. Bob Shell doesn't do this
   automatically — add a one-line note at the start of each session in your log:
   `KB-primary | KB-assisted | raw`.

2. **After each session**, record BC cost from the Bob Shell session summary.

3. **Weekly roll-up:** Compute average BC per session for each tag.

4. **After 4 weeks:** Compare `KB-primary` vs `raw` averages. This gives you an
   empirically grounded savings figure for *your* workload.

### Minimal tracking template

Create `docs/knowledge-base/research/km-savings-log-YYYY-MM.md` and fill it in daily:

```markdown
# KM Savings Log — July 2026

| Date  | Query summary      | Mode        | BC spent | KB docs used         |
|-------|--------------------|-------------|----------|----------------------|
| 07-20 | Arch overview      | raw         | 0.44     | —                    |
| 07-21 | Arch overview      | kb-primary  | 0.06     | concepts/token-opt   |
| 07-22 | Add feature Y      | kb-assisted | 0.18     | guides/setup-tos     |
| 07-22 | Debug cache race   | raw         | 0.31     | —                    |
```

After 20+ entries per mode, average the two columns and apply:

```
measured_savings = (avg_raw_bc - avg_kb_primary_bc) / avg_raw_bc
```

---

## Section 3 — Direct Token Count Diff

For individual KB documents, you can measure the compression ratio directly.

### Using `bob-optimize`

```bash
# Count tokens in the raw source this KB doc summarises
bob-optimize count src/cache/embeddings.py

# Count tokens in the KB doc itself
bob-optimize count docs/knowledge-base/concepts/kb-tos-embedding-layer.md
```

The ratio is:

```
compression_ratio = kb_tokens / source_tokens
savings_pct       = (1 - compression_ratio) × 100
```

### Using tiktoken directly

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

with open("src/cache/embeddings.py") as f:
    source_tokens = len(enc.encode(f.read()))

with open("docs/knowledge-base/concepts/kb-tos-embedding-layer.md") as f:
    kb_tokens = len(enc.encode(f.read()))

savings = (1 - kb_tokens / source_tokens) * 100
print(f"KB compression: {savings:.1f}%  ({source_tokens} → {kb_tokens} tokens)")
```

This gives a **structural compression ratio** — the savings you get every time you use the KB
doc instead of the raw source. It doesn't depend on how often you ask the question.

---

## Section 4 — Compute an Amortised ROI Figure

A single savings percentage is misleading without accounting for the cost of *creating and
maintaining* the KB document.

### Formula

```
net_savings_bc = (queries_answered_from_kb × savings_per_query_bc)
               - kb_creation_bc
               - kb_maintenance_bc_per_month × months_used
```

### Worked example

```
KB doc: docs/knowledge-base/concepts/token-optimization.md

Creation cost:
  One research + write session: ~0.80 BC

Queries answered from this doc over 3 months:
  ~40 queries × 0.38 BC saved each = 15.2 BC gross savings

Maintenance cost:
  2 updates × 0.15 BC = 0.30 BC

Net savings over 3 months: 15.2 - 0.80 - 0.30 = 14.10 BC
ROI: 14.10 / (0.80 + 0.30) = 12.8× (1,280% return)
```

**Key levers:**
- More queries answered → higher ROI
- Shorter creation time → faster breakeven
- Stable codebase → lower maintenance cost

---

## Section 5 — Reporting Standards

Savings claims must include all four elements:

### Required elements

1. **Measurement method** — shadow comparison / direct token diff / session log
2. **Sample size** — number of sessions or queries
3. **Confidence range** — conservative / realistic / optimistic (see
   [`kb-savings-estimation-methodology.md`](../references/kb-savings-estimation-methodology.md))
4. **Applicability boundary** — what workload type the figure applies to

### Example compliant claim

> "Over 4 weeks of working on the Token Optimizer codebase (N=34 sessions),
> KB-primary sessions cost an average of 0.07 BC vs 0.38 BC for raw-source sessions —
> an **82% measured reduction** (conservative range: 70–85%) on architecture and
> configuration queries. This figure does not apply to debugging sessions or
> first-time exploratory tasks."

### Non-compliant claims to avoid

- ❌ "The KM saves 80% of your Bobcoins" (no sample, no boundary)
- ❌ "Combined savings: 20% + 80% = 100%" (additive fallacy)
- ❌ "Every session is 90% cheaper with the KM" (ignores raw-source fallback)

---

## Section 6 — When Savings Are Lower Than Expected

Common causes and how to diagnose them:

| Symptom | Likely cause | Fix |
|---|---|---|
| Bob still reads raw source after KB lookup | KB doc doesn't answer the query | Expand or split the KB doc |
| KB-primary BC close to raw | KB docs are too verbose | Apply the optimizer: `bob-optimize count <doc>` and trim |
| Savings degrade over time | KB is stale (code changed) | Run `bob-optimize analyze` → re-derive stale docs |
| Creation cost exceeds savings | Too many one-off queries | Only create KB docs for recurring topics |

---

## Section 7 — Automating the Log

For continuous tracking, add this to your session workflow:

```bash
# scripts/log-session-cost.sh
#!/usr/bin/env bash
# Usage: ./scripts/log-session-cost.sh "query summary" kb-primary 0.06 "concepts/token-opt"
DATE=$(date +%Y-%m-%d)
LOG="docs/knowledge-base/research/km-savings-log-$(date +%Y-%m).md"
echo "| $DATE | $1 | $2 | $3 | $4 |" >> "$LOG"
```

Or use the Token Optimization System's built-in tracker:

```python
from src.monitoring import get_metrics_collector

metrics = get_metrics_collector()
# After a KB-assisted session:
metrics.record_cache_hit("KB", savings_bc=0.38)
```

---

## Related Documents

- [Bobcoin Savings Analysis 2026-07-14](../research/bobcoin-savings-analysis-2026-07-14.md) — Theoretical analysis, scenarios, institutional audit
- [KB Savings Estimation Methodology](../references/kb-savings-estimation-methodology.md) — Confidence levels and estimation formulas
- [Token Optimization](../concepts/token-optimization.md) — TOS layer: ~20% measured compression
- [Multi-Level Caching](../concepts/multi-level-caching.md) — Cache hit-rate contribution
- [Cost Tracking Guide](./cost-tracking-guide.md) — Bobcoin budget management

## References

- [STATUS.md](../../../STATUS.md) — Current measured figures, manifest reference
- `evaluation/results/validation-2026-07-14/` — Manifest-backed optimizer validation

---

*Last Updated: 2026-07-18*
*Category: Guide*
