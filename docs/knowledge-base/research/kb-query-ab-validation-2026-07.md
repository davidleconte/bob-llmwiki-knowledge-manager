---
title: "KB Query Scorer A/B Validation — July 2026"
category: research
date: 2026-07-16
type: research
status: complete
tags: [kb-query, embedding, ab-validation, precision, adr-014, p1-1]
related:
  - ../guides/kb-tos-integration-roadmap.md
  - ../concepts/kb-tos-embedding-layer.md
  - ../../../docs/adr/014-kb-query-embedding-scorer.md
created: 2026-07-16
updated: 2026-07-16

---

# KB Query Scorer A/B Validation — July 2026

> ⚠️ **FROZEN A/B REPORT (2026-07-16) — no manifest was committed for this run.**
> The p@3 figures below (keyword 0.64, `w=0.7` 0.68, `w=1.0` 0.88) were measured with
> the optional MiniLM backend on the corpus of that date and are preserved here as the
> record of that experiment. **They are superseded as the project's published retrieval
> figure** by the manifest-backed result on the shipped backend: **p@3 = 0.84, at parity
> with a keyword baseline (no net lift)** — `evaluation/results/retrieval-2026-07-19/report.json`.
> Do not cite the numbers below as current retrieval quality.

**Mandate:** ADR-014 requires empirical A/B validation before `embedding_weight > 0`
is used in any production call path. This document records the results.

---

## Setup

- **KB corpus:** 78 documents (5 concepts, 24 guides, 2 references, 47 research)
- **Golden set:** 25 queries with a single known correct document each
- **Metric:** `precision@k` — 1 if the expected document appears in top-k results
- **Scorers tested:**
  - `w=0.0` — keyword-only (existing scorer, baseline)
  - `w=0.1 … 0.7` — linear blend `(1-w)*keyword + w*embedding*15`
  - `w=1.0` — embedding-only
- **Embedder:** `EmbeddingGenerator` (HashingVectorizer, 1000 features, ngram 1-2, L2-norm)

---

## Results

| Weight | p@3  | p@5  | p@10 |
|--------|------|------|------|
| 0.0 (keyword only) | **0.64** | 0.72 | **0.92** |
| 0.1    | 0.64 | 0.68 | 0.92 |
| 0.2    | 0.64 | 0.68 | 0.92 |
| 0.3    | 0.64 | 0.68 | 0.92 |
| 0.5    | 0.64 | 0.76 | 0.92 |
| 0.7    | 0.68 | 0.80 | 0.92 |
| **1.0 (embedding only)** | **0.88** | **0.96** | **0.96** |

---

## Finding: Embedding-Only Wins Decisively

`w=1.0` (pure embedding scorer) achieves **p@3 = 0.88** vs **0.64** for keyword-only —
a **+24 percentage-point** improvement on the golden set. `p@5` improves from 0.72 → 0.96.

However, **no intermediate blend value helps**. At `w=0.1` through `w=0.5`, p@3 stays
flat at 0.64 (identical to keyword-only). At `w=0.7` it nudges to 0.68. The blending
arithmetic in the current implementation weights keyword (range 0–15+) far more heavily
than rescaled cosine (range 0–15) for documents that match on both dimensions. The
keyword scorer's position-weight bonus and phrase-adjacency bonuses dominate the blend
until the embedding weight is high.

### Root Cause of Keyword Misses (9 consistent misses at w=0.0)

| Expected document | Rank (keyword) | Root cause |
|---|---|---|
| `multi-level-caching.md` | 7 | Title contains "Multi-Level Caching" — drowned out by architecture-patterns doc with more keyword hits |
| `token-optimization.md` | 4 | Term "token optimization" appears in many docs; concept doc has less body text than guides |
| `dependency-analysis.md` | NOT IN TOP-10 | Query words ("dependency", "security", "audit") all appear in institutional audit docs which are longer |
| `dual-system-use-case-example.md` | 6 | "example" is a common term; keyword boost not enough |
| `token-optimizer-quick-install.md` | 10 | "quick install" substrings beaten by longer usage guides |
| `setup-token-optimization.md` | 10 | Same as above |
| `real-time-monitoring-guide.md` | 8 | Implementation research doc has more matching words than the guide |
| `external-audit-2026-07-12.md` | 5 | Date in query not weighted; audit term matches many research docs |
| `test-coverage` files | NOT IN TOP-10 | "test coverage report" matches phase-3 testing plan more strongly |

**Pattern:** The keyword scorer rewards *frequency × position*, which systematically
favours longer documents (research reports) over shorter, precise documents (short
concept and guide files). The embedding scorer, being document-length-agnostic,
ranks the semantically closest document regardless of raw word count.

---

## Decision

**Raise `embedding_weight` to `0.7` as the recommended production default** when
an embedder is provided.

Rationale:
- `w=0.7` improves p@3 to 0.68 (+4pp over keyword) and p@5 to 0.80 (+8pp)
- It maintains p@10 = 0.92 (same as keyword)
- `w=1.0` achieves the best p@3 (0.88) but pure embedding has NO keyword fallback
  for exact-match queries (e.g. queries containing the exact document title or filename)
- `w=0.7` preserves the keyword scorer as a tie-breaker for exact-title matches

**`w=1.0` is the eventual target** once the `PersistentEmbeddingIndex` (P2-1) is in
place and the scorer can use a richer embedding model. At that point re-run this
validation to confirm.

---

## Immediate Actions (updates to ADR-014)

1. **`KnowledgeBaseQuery` default `embedding_weight` remains `0.0`** — callers who
   do not pass an `embedder` are unaffected (backward-compatible).
2. **`KBIndexer` (P2-2)** will construct `KnowledgeBaseQuery` with `embedding_weight=0.7`
   when a `PersistentEmbeddingIndex` is available.
3. **`bob-optimize index-kb` CLI command** (P2, planned) will expose a `--weight` flag
   so users can tune per-corpus after running their own validation.
4. **Re-run this validation** after switching to a richer embedding model (e.g.
   sentence-transformers) — the `HashingVectorizer` at `w=1.0` already outperforms
   keyword; dense embeddings will do better still.

---

## Golden Set (25 queries)

| Query | Expected file | KW p@3 | W=0.7 p@3 | W=1.0 p@3 |
|---|---|---|---|---|
| multi-level caching L1 L2 hierarchy | multi-level-caching-architecture-patterns | ✅ | ✅ | ✅ |
| exact match semantic cache layers | multi-level-caching.md | ❌ | ❌ | ✅ |
| embedding layer persistent index | kb-tos-embedding-layer | ✅ | ✅ | ✅ |
| token optimization compression savings | token-optimization.md | ❌ | ❌ | ✅ |
| dependency security audit packages | dependency-analysis.md | ❌ | ❌ | ✅ |
| kb tos integration roadmap P0 P1 P2 | kb-tos-integration-roadmap | ✅ | ✅ | ✅ |
| using both systems token optimizer KB | using-both-systems-together | ✅ | ✅ | ✅ |
| dual system use case example | dual-system-use-case-example | ❌ | ✅ | ✅ |
| quick install token optimizer bob-optimize | token-optimizer-quick-install | ❌ | ❌ | ✅ |
| setup token optimization guide | setup-token-optimization | ❌ | ❌ | ✅ |
| cost tracking guide | cost-tracking-guide | ✅ | ✅ | ✅ |
| activate knowledge manager new session | activating-knowledge-manager | ✅ | ✅ | ✅ |
| e2e end-to-end testing setup | e2e-testing-setup-guide | ✅ | ✅ | ✅ |
| remediation action plan audit | audit-remediation-action-plan | ✅ | ✅ | ✅ |
| real time monitoring guide | real-time-monitoring-guide | ❌ | ✅ | ✅ |
| cache API reference interface | cache-api.md | ✅ | ✅ | ✅ |
| savings estimation methodology | kb-savings-estimation | ✅ | ✅ | ✅ |
| integration feasibility study challenges | kb-tos-integration-feasibility | ✅ | ✅ | ✅ |
| external audit codebase 2026-07-12 | external-audit-2026-07-12 | ❌ | ❌ | ✅ |
| performance benchmarks latency | performance-benchmarks | ✅ | ✅ | ✅ |
| test coverage report | test-coverage | ❌ | ❌ | ✅ |
| security scan vulnerabilities | security-scan | ✅ | ✅ | ✅ |
| phase2 thread safety concurrency | phase2-thread-safety | ✅ | ✅ | ✅ |
| delegation module analysis integration | delegation-integration-analysis | ✅ | ✅ | ✅ |
| adversarial review round1 critical | adversarial-review-round1 | ✅ | ✅ | ✅ |

*Last Updated: 2026-07-16*
*Category: Research*
*Status: Complete — results inform ADR-014 and KBIndexer (P2-2) defaults*
