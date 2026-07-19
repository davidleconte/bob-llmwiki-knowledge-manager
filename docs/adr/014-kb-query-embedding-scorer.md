# ADR-014: KB Query Hybrid Embedding Scorer

**Status:** ✅ Accepted — A/B validation complete (2026-07-16)
**Date:** 2026-07-16
**Deciders:** Architecture team
**Context:** KB Manager ↔ Token Optimization System integration — P1-1

> **A/B validation result (2026-07-16):** embedding-only (`w=1.0`) achieves p@3=0.88
> vs keyword-only p@3=0.64 (+24pp). Recommended production default when embedder is
> present: `w=0.7` (p@3=0.68, p@5=0.80, keyword tie-breaker preserved).
> `KBIndexer` (P2-2) will use `w=0.7`. Full results in
> `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md`.

> **Update (2026-07-19, CLM-06):** The reproducible default-backend measurement
> (`HashingVectorizer`, `w=0.7`, current 116-doc golden set) is **p@3=0.84 with no net
> lift over keyword-only** (`evaluation/results/retrieval-2026-07-19/`). The p@3=0.88 cited
> above is a MiniLM (`w=1.0`) lab result, not reproducible without `mlx-embeddings` /
> `sentence-transformers` installed (both optional, absent in CI/default environments).

---

## Context

`src/tools/kb_query.py` uses keyword-frequency scoring with position weighting.
`src/cache/embeddings.py` provides a `HashingVectorizer`-backed `EmbeddingGenerator`
already present in the codebase.

The integration feasibility study (adversarial audit 2026-07-16) measured the
cosine-similarity of a clearly-related query/document pair using `HashingVectorizer`
at **0.091** — near-zero. This means a blind swap of the keyword scorer to the
embedding scorer would likely degrade search quality for KB retrieval.

The `EmbeddingGenerator.embeddings_cache` dict uses full text strings as keys
with no eviction. Measured at ~856 KB per 30 docs (~5.7 MB per 200 docs). Using
`use_cache=True` for large KB documents would grow the dict without bound.

## Decision

Inject `EmbeddingGenerator` as an **optional**, **injectable** scorer via a new
`embedder` and `embedding_weight` parameter on `KnowledgeBaseQuery.__init__`.

- `embedding_weight=0.0` (default): keyword-only — existing behaviour exactly
  preserved; zero performance impact; no import of `src.cache.embeddings`.
- `embedding_weight > 0`: linear blend of keyword score and rescaled cosine
  similarity. The import is lazy (only executed when the embedding path runs).
- Document content is embedded with `use_cache=False` to prevent unbounded
  memory growth (AF-5 finding). Query text uses `use_cache=True` (short, repeated).

## Consequences

### New cross-package dependency

`src/tools/` → `src/cache/` (lazy import, only when `embedding_weight > 0`).
This is legal under the layering gate (`src/ → scripts/` only is forbidden).
It is the first such coupling and is documented here.

### A/B validation gate (required before raising `embedding_weight` above 0)

Before wiring a non-zero `embedding_weight` into any production call path:

1. Build a golden set of KB queries with known correct documents.
2. Measure `precision@3` with keyword-only and with the blended scorer.
3. The blended scorer must match or exceed keyword precision before adoption.
4. Record results in `docs/knowledge-base/research/kb-query-ab-validation-YYYY-MM.md`.

Rationale: the 0.091 cosine similarity measurement means the `HashingVectorizer`
is tuned for near-duplicate detection (L2 cache use case), not cross-vocabulary
document retrieval. The A/B gate prevents a silent quality regression.

### Memory safety

`use_cache=False` on all document embeddings is non-negotiable. A reviewer must
ensure this does not regress. The three new tests in `tests/tools/test_kb_query.py`
(`TestEmbeddingScorer`) enforce this contract.

## Alternatives Considered

| Option | Rejected reason |
|--------|----------------|
| Blind swap keyword → embedding | Near-zero measured similarity; silent quality regression |
| Shared singleton embedder | Couples `KnowledgeBaseQuery` to a global; breaks test isolation |
| External embedding model (OpenAI etc.) | Introduces network dependency + cost on every KB search |
| Defer to P2 `PersistentEmbeddingIndex` | P2 requires P1 as a stepping stone; this ADR covers P1 |

## Related

- Feasibility study: `docs/knowledge-base/research/kb-tos-integration-feasibility-2026-07-14.md`
- Roadmap P1-1: `docs/knowledge-base/guides/kb-tos-integration-roadmap.md`
- Concept: `docs/knowledge-base/concepts/kb-tos-embedding-layer.md`
- Adversarial audit findings AF-4, AF-5 in the feasibility study

## Amendment — MiniLM backend (branch: fix-multilevel-cache-race, 2026-07)

**Context:** Following the A/B validation gate passing (p@3 = 0.88 embedding-only), step 3 of
the KB embedding pipeline improvement added an optional `backend="minilm"` to
`EmbeddingGenerator` in `src/cache/embeddings.py`. This amendment records the resolution of
the near-zero cosine similarity problem documented in the original ADR body.

### What changed

The core problem identified in this ADR — `HashingVectorizer` cosine similarity of **~0.091**
on semantically related pairs — is resolved by the new backend:

| Backend | Cosine sim (related pair) | Dim | Platform | Extra dep |
|---------|:------------------------:|:---:|----------|-----------|
| `"hashing"` (default) | ~0.091 | 1000 | All platforms | None |
| `"minilm"` (optional) | ~0.78 | 384 | macOS + Apple Silicon | `mlx-embeddings>=0.1` |

### No HuggingFace API key required

`mlx_embeddings.load("sentence-transformers/all-MiniLM-L6-v2")` downloads from the public
HuggingFace Hub. **No account, no token, no configuration is required.** On first use, the model
is downloaded once (~22 MB) to `~/.cache/huggingface/` and cached persistently across sessions.

### Fallback guarantee (A/B gate still applies)

When `mlx-embeddings` is absent (Linux, Intel Mac, CI), `EmbeddingGenerator` emits a
`UserWarning` and silently falls back to `"hashing"`. The A/B validation gate defined in this
ADR continues to apply to both backends: a non-zero `embedding_weight` must be validated before
raising above 0 in any production call path.

### Implementation reference

- `src/cache/embeddings.py` — `EmbeddingGenerator(backend=...)`, `_try_load_minilm()`, `_embed_minilm()`
- `pyproject.toml` — `[project.optional-dependencies] mlx = ["mlx-embeddings>=0.1"]`
- `docs/architecture/architecture.md §5` — component description updated
