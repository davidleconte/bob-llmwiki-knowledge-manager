---
title: "Mnemox Knowledge Builder — Full Technical Design Retro-Engineering"
category: research
tags: [architecture, retro-engineering, knowledge-graph, token-optimizer, embeddings, use-cases, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
related:
  - ../concepts/knowledge-graph-layer.md
  - ../concepts/kb-tos-embedding-layer.md
  - ../concepts/token-optimization.md
  - ../concepts/multi-level-caching.md
  - ../concepts/delegation-analysis-pipeline.md
  - ../research/kb-tos-integration-feasibility-2026-07-14.md
  - ../research/graph-validation-2026-07-17.md
  - ../guides/kb-tos-integration-roadmap.md
---

# Mnemox Knowledge Builder — Full Technical Design Retro-Engineering

> **Purpose:** Complete business/functional/use-case-driven architecture derived from
> the live codebase and KB. All numbers are manifest-backed. Covers both sub-systems,
> the shared embedding layer, the knowledge graph, the delegation pipeline, and the
> full economic model.

---

## 1. The Business Problem

### 1.1 Core Pain Points

| Cost Type | Root Cause | Consequence |
|---|---|---|
| **Re-derivation cost** | Session amnesia — no persistent knowledge | Same questions answered at full token price every session |
| **Token inflation cost** | Verbose context assembly — no compression | Every prompt padded with redundancy and filler |
| **Context pollution cost** | Unfiltered retrieval — no graph-guided relevance | LLM receives tangentially related content that dilutes precision |
| **Context dislocation cost** | Unstructured retrieval — no semantic ordering | Retrieved chunks lose narrative coherence; meaning degrades |

### 1.2 Business Objective

Build a **knowledge-first AI development system** that:
1. Eliminates re-derivation by persisting structured, cross-referenced knowledge that survives across sessions
2. Compresses every prompt chain without meaning degradation, using embedding-backed lossless optimization
3. Surfaces the most relevant knowledge through a property graph that understands document authority and semantic kinship
4. Measures honestly — every savings claim is manifest-backed, never fabricated

---

## 2. System Decomposition — Two Products, One Repository

The system has **two distinct but complementary sub-systems** operating in sequence:

```
KB Manager (Bash/YAML, ~500 LOC)          Token Optimization System (Python, ~3,500 LOC)
  Human-in-the-loop, conversational    +    Synchronous, sub-50ms p95, CLI + library
  VALUE: eliminates re-derivation           VALUE: ~20% lossless compression (N=183, manifest)
                    │                                        │
                    └──────── SHARED EMBEDDING LAYER (P2) ──┘
                                  src/embeddings/
                                        │
                              KNOWLEDGE GRAPH (P3)
                                  src/graph/
                                        │
                           DELEGATION PIPELINE (P4)
                               src/delegation/
```

---

## 3. Functional Requirements and Use Cases

### UC-1: Persistent Knowledge Capture
**Goal:** Never re-derive the same technical knowledge twice.
`Session N: derive → write to KB → Session N+1: read KB (0 re-derivation tokens)`

- `FR-1.1` KB documents persist as structured Markdown with YAML frontmatter
- `FR-1.2` 4-category taxonomy: `concepts/`, `guides/`, `references/`, `research/`
- `FR-1.3` Cross-references: `related:` frontmatter list + relative inline links
- `FR-1.4` Master `INDEX.md` maintains an authoritative catalogue

### UC-2: Intelligent KB Query
**Goal:** Retrieve the most relevant KB documents, ranked by semantic relevance and graph authority.

```
query → keyword scorer (always)
      → embedding scorer (P2, EmbeddingGenerator, blend at embedding_weight=0.7)
      → graph re-ranker (P3, GraphRanker, graph_weight=0.0 default)
```

**Measured quality (live, N=80 docs, golden set N=25):**

| Configuration | P@3 |
|---|---|
| Keyword-only | 0.44 |
| Hashing embedding | 0.60 |
| **MiniLM-L6-v2 embedding** | **0.88** |
| MiniLM + graph (any weight) | 0.88 (neutral on this corpus) |

### UC-3: Prompt Chain Compression
**Goal:** Remove redundancy from a prompt without degrading meaning.
**Measured:** ~20% mean savings (95% CI [19%, 21%], N=183, manifest: `evaluation/results/validation-2026-07-14/`)

- `FR-3.1` Whitespace normalization
- `FR-3.2` Redundancy removal (filler words, verbal hedges, repetition)
- `FR-3.3` Structure preservation (Markdown headers, code blocks, GFM tables)
- `FR-3.4` Quality gate: `min_quality_score=0.8` — reject over-aggressive optimization
- `FR-3.5` Token counting via tiktoken BPE (`tiktoken_active` flag distinguishes from chars/4 fallback)

### UC-4: Recompute Avoidance (Multi-Level Cache)
**Goal:** Return a prior result for 0 tokens when the same or semantically similar prompt recurs.

```
L1 ExactCache     (SHA-256)          → < 750 µs p99  — in-memory
L2 SemanticCache  (cosine ≥ 0.85)    → < 4.5 ms p99  — in-memory, with L2→L1 promotion
L3 PersistentEmbeddingIndex          → < 500 ms       — disk-backed, optional
```

**Thread-safety:** 14 races fixed through 5 audit rounds; RLock protects all mutable state.

### UC-5: KB-Aware Parallel Repository Analysis (Delegation Pipeline)
**Goal:** Run 6 analysis agents in parallel; compress output; write as KB research documents.

```
Phase 1 (sequential): ResearchAgent → loads KB context via KnowledgeBaseQuery
Phase 2 (parallel):   SecurityAgent · PerformanceAgent · QualityAgent
                      ArchitectureAgent · DocumentationAgent
                      → each result → TokenOptimizer.optimize() → KB research doc
```

- `FR-5.1` ResearchAgent runs first to prevent re-analysis of known issues
- `FR-5.2` Each agent report compressed (~20% reduction) before writing
- `FR-5.3` Output is standard KB research documents (frontmatter, cross-references)
- `FR-5.4` Path containment via `safe_paths.resolve_within`; `../` escapes rejected
- `FR-5.5` One-way layering: `delegation → TokenOptimizer`; never the reverse

### UC-6: Knowledge Graph Structural Health
**Goal:** Understand connectivity, authority, and stale-link status of the KB.

| Feature | CLI | Output |
|---|---|---|
| Build graph | `graph-build --kb-path` | Property graph: nodes=docs, explicit+semantic+broken edges |
| Health report | `graph-health` | Orphan count, hub list, broken links, PageRank top-10 |
| Neighbourhood | `graph-query <doc_id>` | All docs within N hops |
| Orphan detection | `graph.orphans()` | Docs with zero inbound explicit links |
| Hub identification | `graph.hubs(top_k=5)` | Most-cited documents by inbound degree |

**Live validation (80-doc corpus, MiniLM):**

| Metric | Value |
|---|---|
| Total nodes | 80 (now 116 after this session's corpus growth) |
| Explicit edges | 163 |
| Semantic edges (cosine ≥ 0.30) | 2,654 |
| Broken edges | 19 |
| Structural orphans (explicit only) | 39 |
| Rescued by semantic edges | 26 (67%) |
| Build time (warm) | ~45 ms |

---

## 4. The Knowledge Graph Power

### 4.1 Failure Modes Without a Graph

```
❌ Orphan documents  — 49% of KB (39/80) had zero inbound explicit links → invisible to traversal
❌ Dead links        — cross-references silently rot on rename/delete
❌ No authority signal — all documents treated as equally relevant
❌ Limited reach     — documents 2+ hops away invisible to keyword + embedding search
```

### 4.2 What the Graph Adds

```
Explicit edges   (weight=1.0)    — deliberate authorial intent (frontmatter related: + inline links)
Semantic edges   (weight=cosine) — discovered kinship (PersistentEmbeddingIndex, threshold ≥ 0.30)
PageRank scores                  — structural authority (power method, damping=0.85)

Re-ranking: final = (1−gw) × embedding_similarity + gw × pagerank × 15.0
```

### 4.3 Why `graph_weight=0.0` Is the Validated Default

On a tight-topic corpus (all documents about the same project), MiniLM embeddings produce a **dense semantic graph** — nearly every pair exceeds the 0.30 threshold. PageRank becomes nearly uniform (max 1.6× min). The PageRank term (`gw × PR × 15 ≈ 0.3 × 0.020 × 15 ≈ 0.09`) is small relative to the cosine delta between top candidates. P@3 is identical at all graph weights 0.1–0.5.

**The graph's primary value is structural analysis** (orphan/hub/broken-link detection), not score blending. On a larger, more diverse corpus, PageRank would provide discriminating authority signal.

### 4.4 The Compounding Knowledge Capital Effect

```
Without graph: KB growth adds NOISE (orphaned docs, dead links, invisible authority)
With graph:    KB growth adds SIGNAL (every well-linked new doc raises PageRank of all related docs)
```

The MORE sessions accumulate in the KB, the CHEAPER and MORE PRECISE each new session is.

---

## 5. The Embedding-Backed Token Optimizer

### 5.1 Three Layers — Never Blended

```
LAYER 1 — CACHE (recompute avoidance)
  L1 ExactCache: SHA-256, O(1), < 750µs p99
  L2 SemanticCache: cosine ≥ 0.85, < 4.5ms p99
  L3 PersistentEmbeddingIndex: disk, optional
  Economics: hit avoids ALL downstream tokens for that call
  Rate: workload-dependent (function of request stream repeat rate)

LAYER 2 — OPTIMIZER (lossless compression) ← THE ONLY MEASURED SAVINGS HEADLINE
  Whitespace normalization + redundancy removal + structure preservation
  Quality gate: min_quality_score=0.8
  Measured: ~20% mean (95% CI [19%, 21%], N=183, manifest-backed)
  Token counter: tiktoken BPE (tiktoken_active flag)

LAYER 3 — TRUNCATION (lossy budget fit — NEVER counted as savings)
  4 strategies: Simple · Priority · Semantic · SlidingWindow
  Auto-selected by content type
  Reported separately; excluded from savings figure
```

### 5.2 The Embedding Backend Priority Chain

```
Priority 1: mlx-embeddings (Apple Silicon, ~2–4 ms warm, Neural Engine)
Priority 2: sentence-transformers/all-MiniLM-L6-v2 (~5–20 ms, cross-platform)
Priority 3: HashingVectorizer (stateless bag-of-ngrams, <1 ms, always available)
```

| Backend | P@3 | Use case |
|---|---|---|
| Hashing (fallback) | 0.60 | L2 cache (near-duplicate detection) |
| **MiniLM-L6-v2** | **0.88** | KB retrieval, graph semantic edges |

Each backend is used where it belongs — hashing for the L2 semantic cache (repeated prompts), MiniLM for KB retrieval (cross-vocabulary semantic search).

### 5.3 The "No Degraded Meaning" Contract

1. **Quality gate** — optimizer rejected if `_estimate_quality()` < 0.8
2. **Null test** — shuffled/high-entropy input must produce < 5% compression (real optimizer finds no redundancy in random text)
3. **Structure preservation flag** — `preserve_structure=True` enforced when TOS processes KB-sourced structured content

### 5.4 The "No Polluted Context" Contract

1. Graph-guided retrieval — orphan detection + PageRank authority ranking surfaces central documents over peripheral noise
2. Semantic similarity threshold — L2 cache requires cosine ≥ 0.85; KB graph edges require cosine ≥ 0.30
3. ResearchAgent KB preflight — delegation pipeline loads prior KB findings before analysis, preventing duplicate research

---

## 6. Component Technical Specifications

### `TokenOptimizer` facade (`src/facade.py`)
Single public API surface. 7 public methods back 13 CLI subcommands. Holds no business logic.

### `MultiLevelCache` (`src/cache/`)
L1 ExactCache (SHA-256, LRU 1000 entries) + L2 SemanticCache (HashingVectorizer cosine, 500 entries) + optional L3 disk index. 14 races fixed through 5 audit rounds.

### `PromptOptimizer` (`src/optimizer/`)
`target_reduction=0.30`, `min_quality_score=0.80`, tiktoken BPE counting.

### `PersistentEmbeddingIndex` (`src/embeddings/index.py`)
Storage: `.bob/kb-index/vectors.npy` + `manifest.json` (chunk rows) + `staleness.json` (file-level sentinels). Invariant: `matrix.shape[0] == len(manifest)`. Incremental mtime/hash rebuild.

### `KnowledgeGraph` (`src/graph/graph.py`)
10-field `NodeProps`, 3 edge types (explicit/semantic/broken), `pagerank(damping=0.85)`, `orphans()`, `hubs()`, `neighbours(depth)`.

### `GraphRanker` (`src/graph/ranker.py`)
`final = (1−gw)×sim + gw×PR×15.0`, `gw=0.0` validated default, `PAGERANK_SCALE=15.0`.

### `AnalysisPipeline` (`src/delegation/pipeline.py`)
6 agents, ThreadPoolExecutor, ResearchAgent first, each report through `TokenOptimizer`, output as KB research docs. One-way dependency on TOS.

---

## 7. Economic Model

**Bobcoin** = `token_count × price_per_token × 1000` (model-agnostic cost unit, single home: `src/pricing.py`)

| Savings Lever | Mechanism | Figure | Applicability |
|---|---|---|---|
| Re-derivation avoidance | KB Manager | Structural (0 tokens for known answers) | Workload-dependent |
| Optimizer compression | TOS | ~20% mean (N=183, manifest-backed) | Every novel prompt |
| Cache recompute-avoidance | TOS | 0 tokens for hits | Workload repeat rate |
| Graph-guided retrieval | KB+Graph | P@3 0.44 → 0.88 (+100%) | KB-assisted sessions |

**Honesty constraint:** No blended totals. Each lever measured separately. `check_savings_claims.py` CI gate enforces this — every published percentage must cite a manifest.

---

## 8. Quality Gates (CI-Enforced)

| Gate | What | How |
|---|---|---|
| Layering | `src/` never imports `scripts/` | `check_layering.py`, AST-based |
| One value home | Version, pricing, coverage floor each have one canonical source | `check_value_homes.py` |
| Manifest-backed claims | Every savings % cites a manifest | `check_savings_claims.py` |
| Null test | Optimizer on shuffled text → < 5% savings | `src/validation/` |
| Coverage | ≥ 80% global; per-package floors | `check_coverage_by_package.py` |

**Status (2026-07-18):** 1,112 tests / 0 failures, 89.82% coverage, all 5 per-package floors met, ruff + mypy clean.

---

## 9. SLA Summary

| Operation | p99 Target | Measured (M3 Pro) |
|---|---|---|
| L1 exact-cache hit | ≤ 750 µs | 144 µs |
| L2 semantic hit (50 entries) | ≤ 4.5 ms | 1.5 ms |
| Prompt optimization (cold pipeline) | ≤ 3.5 ms | 695 µs |
| Sustained single-threaded optimize | ≥ 50 req/s | — |
| Lossless compression savings | ≥ 15% mean | 20.0% mean |

---

## 10. Open Gaps

| ID | Issue | Action |
|---|---|---|
| G-1 | `graph_weight=0.0` neutral on current corpus | Grow corpus diversity; re-run golden set when uplift expected |
| G-2 | `EmbeddingGenerator.embeddings_cache` has no eviction on dict keys | Use `use_cache=False` for document indexing; cache only query embeddings |
| G-3 | `sentence-transformers` not wired as second MiniLM path | Wire in `EmbeddingGenerator`; tracked in ADR-015 follow-up |
| G-4 | 13 structural orphans remain after semantic edge rescue | Add explicit `related:` cross-references |
| G-5 | Date-based queries miss (e.g. "external audit july 2026") | Add `recency_weight` or `date_filter` to specific query patterns |
| G-6 | Context compression requires TOS v1.0 stability tag | Tag TOS stable; add fallback contract to subprocess integration |

---

## Related Documents

- [Knowledge Graph Layer](../concepts/knowledge-graph-layer.md)
- [KB-TOS Shared Embedding Layer](../concepts/kb-tos-embedding-layer.md)
- [Token Optimization](../concepts/token-optimization.md)
- [Multi-Level Caching](../concepts/multi-level-caching.md)
- [Delegation Analysis Pipeline](../concepts/delegation-analysis-pipeline.md)
- [KB-TOS Integration Feasibility Study](../research/kb-tos-integration-feasibility-2026-07-14.md)
- [Graph Validation — July 2026](../research/graph-validation-2026-07-17.md)
- [Architecture](../../../docs/architecture/architecture.md)
- [INTEGRATIONS.md](../../../INTEGRATIONS.md)
- [SLA](../../../docs/sla.md)

---
*Created: 2026-07-18 — derived from live codebase and KB in one session*
*Category: Research*
