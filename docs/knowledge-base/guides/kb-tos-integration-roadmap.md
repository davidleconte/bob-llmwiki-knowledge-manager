---
title: "KB Manager ↔ TOS Integration Roadmap: P0 / P1 / P2 + TOS Stability Gate"
category: guide
date: 2026-07-14
type: guide
status: active
adversarial_audit: 2026-07-16
tags: [integration, roadmap, p0, p1, p2, tos-stable, kb-manager, token-optimizer, action-plan]
related:
  - ../research/kb-tos-integration-feasibility-2026-07-14.md
  - ../concepts/kb-tos-embedding-layer.md
  - token-optimizer-quick-install.md
  - setup-token-optimization.md
created: 2026-07-14
updated: 2026-07-14

---

# KB Manager ↔ TOS Integration Roadmap

> ⚠️ **Adversarial audit applied 2026-07-16.** P0-3 (versioned-key fix) and P0-4
> (singleton lock fix) were **false positives** — both bugs are already fixed in HEAD.
> P0-5 (STATUS.md → "Release Candidate") was a **CI-breaking change** — revised below.
> P1-1 risk rating upgraded from Low to Medium (embedding quality finding).
> The stability gate shrinks from 7 items (S1–S7) to 5 real items (S1, S2, S5, S6, S7).

**Basis:** Live measurements 2026-07-14 — 907 passed / 23 skipped · 87.2% coverage · all CI gates green
**Grounded by:** Direct code inspection + adversarial audit 2026-07-16

---

## Corrected Baseline: What Is Already Fixed

The Phase-8 NO-GO audit found many issues. Most are already resolved in HEAD.
The roadmap starts from **actual live state**, not the frozen audit.

| Phase-8 NO-GO Finding | Live State (2026-07-14) |
|----------------------|------------------------|
| `strategies` dead config field | ✅ Wired end-to-end (`prompt_optimizer.py:101,177,221-225`) |
| `version_support_enabled`/`max_versions` not passed | ✅ Wired (`factory.py:40-41`) |
| `MonitoringConfig.log_level`/`metrics_enabled` not applied | ✅ Wired (`facade.py:97,100`) |
| `load_from_env()` skips validation | ✅ Fixed (`manager.py:169-179`) |
| CI uses floating `pip install` | ✅ 5 of 6 jobs use `uv sync --frozen` |
| Wall-clock tests not `@pytest.mark.slow` | ✅ All 3 marked |
| `documentation_agent.py` raw `rglob()` | ✅ Routes through `resolve_within` (line 53-56) |
| Coverage 74.9% excluding `src/tools/` | ✅ 87.2% including `src/tools/` (floor 93.9%) |
| `check_savings_claims.py` 5-file allowlist | ✅ Tree-wide scan — 211 surfaces clean |

---

## Open Findings (Live, Verified — post adversarial audit)

### 🔴 Critical (1)
**R1** — `docs/project-management/planning/LLM_OPTIMIZATION_COMPLETE_SUMMARY.md`
contains 20+ instances of `89.3%` and `91.80%` as live, un-retracted claims (no banner).

### 🟡 Medium (2)
**R2** — Facade `MultiLevelCache` and optimizer `ExactCache` are separate objects.
The `optimize()` path uses only L1 (ExactCache); the L2 (semantic) is only reachable
via `facade.cache.get()` directly. Intentional by design but the façade comment
at line 83 calls it "not a second disjoint one" — misleading about L2 scope.

**R5** — `docs/installation.md` still ships a broken `git clone github.com/yourusername/...`
placeholder URL.

### ✅ Closed (already fixed in HEAD — confirmed by adversarial audit)
~~**R3**~~ — versioned-key collision: `_make_versioned_key()` already calls
`escape_version()` from `src/cache/base.py`. Live test: no collision. **False positive.**

~~**R4**~~ — singleton race: `get_metrics_collector()` already uses double-checked
locking with `_collector_init_lock`. 50-thread concurrency test: 1 unique instance.
**False positive.**

---

## P0 — Prerequisites: Close the Last Gap to "Stable"

**Goal:** Resolve all remaining findings. Reach the gate for a `v1.0-rc1` tag.
**Duration:** 1–2 days of focused work.
**Gate:** All `scripts/check_*.py` green + `uv run pytest` green + zero live-unretracted fabrications.

---

### P0-1 — Add retraction banner to `LLM_OPTIMIZATION_COMPLETE_SUMMARY.md` 🔴 R1 ❌ OPEN

**File:** `docs/project-management/planning/LLM_OPTIMIZATION_COMPLETE_SUMMARY.md`

Insert after the document title (line 1):

```markdown
> ⚠️ **Historical planning document — retracted metrics.** The "89.3%" and "91.80%"
> figures cited throughout this document were fabricated (a simulation that never
> invoked the optimizer) and are retracted. The measured figure is **~20% mean
> optimizer compression** (manifest-backed: `evaluation/results/validation-2026-07-14/`).
> See `STATUS.md`. This document is preserved as a historical record only.
```

**Verify:** `python3 scripts/check_savings_claims.py` must pass.
**Effort:** 10 minutes. **Risk:** Zero.

---

### P0-2 — Fix `INSTALLATION.md` broken clone URL 🟡 R5 ❌ OPEN

**File:** `docs/installation.md`
Replace `git clone github.com/yourusername/...` with the real repo URL from
`pyproject.toml` (the single home for the repo URL).

**Effort:** 5 minutes. **Risk:** Zero.

### P0-3 — ~~Fix versioned-key collision~~ ✅ ALREADY FIXED — NO ACTION NEEDED

> **Adversarial audit finding AF-1:** `ExactCache._make_versioned_key()` already calls
> `escape_version(version)` from `src/cache/base.py:13`. The version separator is
> percent-encoded (`v1:a` → `v1%3Aa`). Live test confirmed: no collision between
> `set('a:b', version='v1')` and `set('b', version='v1:a')`. This was a false positive
> in the original study.

---

### P0-4 — ~~Fix unlocked singleton creation~~ ✅ ALREADY FIXED — NO ACTION NEEDED

> **Adversarial audit finding AF-2:** `get_metrics_collector()` in `src/monitoring/metrics.py`
> already uses double-checked locking with `_collector_init_lock = Lock()`. 50-thread
> concurrency stress test confirmed: 1 unique instance. This was a false positive.

---

### P0-5 — Clarify L2/L1 scope in STATUS.md and facade docstring 🟡 R2 ❌ OPEN

> **Adversarial audit finding AF-8:** The original P0-5 proposed changing STATUS.md
> status to "Release Candidate — v1.0-rc1". This **breaks CI**: `check_status_consistency.py`
> requires `CANONICAL_STATUS = "Not Production Ready"` in STATUS.md. The gate must be
> updated simultaneously or the status string must remain compliant.

**Revised P0-5 scope:**
1. Add an explicit note to `src/facade.py` docstring clarifying L1/L2 scope:
   `optimize()` uses L1 only; L2 is accessible only via `facade.cache.get()` directly
2. Add the same note to `docs/architecture/architecture.md §5` (cache section)
3. Do NOT change `STATUS.md` overall status string without also updating
   `check_status_consistency.py:CANONICAL_STATUS` — update both atomically

**Verify:** `python3 scripts/check_status_consistency.py` — must pass.
**Effort:** 15 minutes. **Risk:** Low if the gate is updated in the same commit.

---

## TOS Stability Gate — Complete Checklist (Updated 2026-07-16)

S3 and S4 from the original checklist are **removed** — both bugs were already fixed.
S5 is **done** — scope notes already present in `src/facade.py:49–53` and
`docs/architecture/architecture.md:238`.
S1 and S2 are **done** — retraction banner at line 11 of the summary doc; broken URL no longer in `INSTALLATION.md`.
S6 is **partially done** — `pyproject.toml` is already at `1.0.0`; CHANGELOG token-optimization content remains under `[Unreleased]`.

| # | Task | Where | Effort | State |
|---|------|-------|--------|-------|
| ~~S1~~ | ~~Retraction banner on `LLM_OPTIMIZATION_COMPLETE_SUMMARY.md`~~ | ~~P0-1~~ | ~~10 min~~ | ✅ Done (line 11) |
| ~~S2~~ | ~~Fix `INSTALLATION.md` broken clone URL~~ | ~~P0-2~~ | ~~5 min~~ | ✅ Done (URL removed) |
| ~~S3~~ | ~~Fix versioned-key collision~~ | ~~P0-3~~ | ~~30 min~~ | ✅ Already fixed (AF-1) |
| ~~S4~~ | ~~Fix unlocked singleton creation~~ | ~~P0-4~~ | ~~20 min~~ | ✅ Already fixed (AF-2) |
| ~~S5~~ | ~~Clarify L1/L2 scope in facade docstring + ARCHITECTURE.md~~ | ~~P0-5~~ | ~~15 min~~ | ✅ Done (`facade.py:49-53`, `ARCHITECTURE.md:238`) |
| S6 | Promote TOS `[Unreleased]` CHANGELOG items under `[1.0.0-tos]` | P1-2 | 15 min | ❌ |
| S7 | Tag `v1.0` on default branch after all gates pass | P1-2 | 5 min | ❌ |

**Total remaining: ~20 minutes** — only S6 (CHANGELOG housekeeping) and S7 (git tag) remain.
All P0 items are closed. The system is structurally stable; S6/S7 are release ceremony only.

Everything in `a-plus-plan.md` is quality polish toward A+ grade — **not** a stability
requirement. The system is functionally correct today; the remaining items are
disclosure, correctness edge cases, and governance hygiene.

---

## P1 — TOS v1.0 Stable: KB-Integration Ready

**Prerequisite:** P0 complete. TOS tagged `v1.0-rc1`.
**Goal:** Tag `v1.0`. Upgrade KB query engine. Enable opt-in context compression.
**Duration:** 3–5 days.

### What "Stable" Means Here

| Criterion | P0 Result | P1 Target |
|-----------|-----------|-----------|
| Coverage | 87.2% total, all floors green | Maintain ≥87% |
| Critical bugs | 0 open | 0 open |
| Claims integrity | 0 unretracted surfaces (after P0-1) | 0 |
| Correctness bugs | 0 (after P0-3) | 0 |
| Race conditions | 0 (after P0-4) | 0 |
| Version tag | None (unreleased) | `v1.0` |
| Integration guide | Not present | `INTEGRATIONS.md` |

---

### P1-1 — KB Query Engine Upgrade (with A/B validation gate) ⚠️ Risk: Medium

> **Adversarial audit revision:** The original P1-1 rated this Low risk and said "no ADR
> required." Measured `HashingVectorizer` cosine similarity between a clearly related
> query/document pair is **0.091** — near-zero. This is expected: `HashingVectorizer`
> is tuned for near-duplicate detection (the L2 cache's use case), not cross-vocabulary
> document retrieval (the KB query engine's use case). A blind swap degrades search
> quality. Risk is now **Medium**. An ADR and A/B validation gate are now required.

**What to build:** Add `EmbeddingGenerator` as an injectable scorer alongside the
existing keyword scorer. Run both and compare, don't replace blindly.

**Revised implementation — hybrid approach:**

```python
# src/tools/kb_query.py
from src.cache.embeddings import EmbeddingGenerator, cosine_similarity_vectors

class KnowledgeBaseQuery:
    def __init__(self, kb_path: str = "docs/knowledge-base",
                 embedder: Optional[EmbeddingGenerator] = None,
                 embedding_weight: float = 0.0):  # 0.0 = keyword only (safe default)
        ...
        self._embedder = embedder  # None = no embedding, keyword scorer only
        self._embedding_weight = embedding_weight  # 0.0-1.0 blend weight

    def _calculate_relevance(self, query: str, content: str, filename: str) -> float:
        keyword_score = self._keyword_score(query, content, filename)  # existing logic
        if self._embedder is None or self._embedding_weight == 0.0:
            return keyword_score
        # Blend: embedding score is rescaled to [0, 10] range for comparability
        q_vec = self._embedder.generate(query)
        # IMPORTANT: use_cache=False — embeddings_cache has no eviction and
        # holds full document text as keys (~856KB per 30 docs). Per-query
        # cache=False avoids unbounded memory growth in the KB query path.
        c_vec = self._embedder.generate(content[:2000], use_cache=False)
        embed_score = cosine_similarity_vectors(q_vec, c_vec) * 10.0
        return (1 - self._embedding_weight) * keyword_score + \
               self._embedding_weight * embed_score
```

**A/B validation gate (required before `embedding_weight > 0` is used in production):**
1. Run both scorers over a set of KB queries with known correct documents
2. Measure `precision@3` (top-3 results contain the expected document)
3. Embedding scorer must match or exceed keyword scorer before replacing or blending
4. Document results in a new research doc: `research/kb-query-ab-validation-YYYY-MM.md`

**New cross-package dependency introduced:** `src/tools/ → src/cache/`. This is legal
under the existing layering gate (`src/ → scripts/` only is forbidden), but must be
documented in the new ADR.

**ADR required:** captures the quality tradeoff, the `use_cache=False` memory decision,
and the `embedding_weight` blending rationale.

**Tests to add in `tests/tools/test_kb_query.py`:**
- `test_embedding_weight_zero_uses_keyword_only` — default behavior unchanged
- `test_embedding_weight_nonzero_blends_scores` — blended path exercised
- `test_embedder_uses_cache_false_for_documents` — memory safety verified

**Verify:** `uv run pytest tests/tools/test_kb_query.py -q` — must pass.
**Effort:** ~2 days (implementation + A/B validation). **Risk:** Medium.

---

### P1-2 — Tag `v1.0` and Create `INTEGRATIONS.md`

1. **Version bump** in `pyproject.toml`: `version = "1.0.0"`
2. **CHANGELOG** — move all Unreleased TOS items under `[1.0.0]`
3. **`INTEGRATIONS.md`** at repo root — documents:
   - Python library integration: `from src.facade import TokenOptimizer`
   - CLI integration: `bob-optimize optimize -` stdin interface
   - KB search upgrade (P1-1)
   - Subprocess context compression (P1-3)
   - Future: persistent embedding index (P2)
4. **Tag** `v1.0` on default branch after all gates pass

**Effort:** Half day. **Risk:** Zero.

---

### P1-3 — Add Opt-In Context Compression to KB Manager Mode

Add compression as an **opt-in, fallback-safe** capability to the
`knowledge-manager` Bob Shell mode in `config/custom_modes.yaml`.

**Add to `customInstructions`:**

```yaml
### Token Optimization (Optional — requires bob-optimize in PATH)
When assembling KB context for LLM injection, optionally compress it:

  compressed=$(echo "$KB_CONTEXT" | bob-optimize optimize - --json \
               | python3 -c "import sys,json; print(json.load(sys.stdin)['optimized_text'])")

Requirements:
  - bob-optimize installed: pip install -e ".[dev,monitoring]" in repo root
  - Always use preserve_structure=True for KB document content
  - If bob-optimize is unavailable, skip silently (KB retrieval is unaffected)
  - Subprocess failure must never block knowledge retrieval

Expected benefit: ~20% token reduction on retrieved context (manifest-backed).
```

**Also create** `.bob/skills/kb-optimizer-integration.md` with the exact subprocess
pattern, fallback contract, and `preserve_structure` requirement documented.

**Critical constraint (C3 guard):** This step must only be executed **after TOS is
tagged v1.0**. Coupling the KB Manager's retrieval path to a Beta library is the
maturity anti-pattern this roadmap exists to prevent.

**Effort:** Half day. **Risk:** Low — opt-in, no breaking change to KB Manager behavior.

---

## P2 — Shared Embedding Layer (Long-term)

**Prerequisite:** P1 complete. TOS tagged `v1.0`.
**Goal:** Persistent embedding index that eliminates per-query recompute and
bridges the in-memory / persistent persistence gap (Challenge C4).
**Duration:** 2–3 weeks.

> P2 is **not** about merging the two systems.
> It is about building a shared infrastructure layer they can both use independently.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│               New: src/embeddings/  (shared layer)        │
│  index.py    PersistentEmbeddingIndex                     │
│  store.py    FileBackedVectorStore  (NumPy .npy + JSON)   │
│  indexer.py  KBIndexer (mtime-based incremental rebuild)  │
└──────────────┬───────────────────────────────────────────┘
               │ shared by both consumers
    ┌──────────┴──────────┐         ┌──────────────────────┐
    │ KnowledgeBaseQuery  │         │  SemanticCache (L2)   │
    │  (replaces P1-1     │         │  optional L3 backed   │
    │   per-query compute)│         │  by persistent index  │
    └─────────────────────┘         └──────────────────────┘
```

### P2-1 — Design and Implement `PersistentEmbeddingIndex`

**Interface** (compatible with but not implementing `CacheInterface`):

```python
class PersistentEmbeddingIndex:
    def __init__(self, index_path: Path, embedder: EmbeddingGenerator): ...
    def index_document(self, doc_id: str, content: str) -> None: ...
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]: ...
    def rebuild(self, kb_path: Path) -> int: ...   # returns doc count indexed
    def is_stale(self, doc_path: Path) -> bool: ... # mtime-based check
```

**Storage:** NumPy `.npy` for the vector matrix + JSON for the `{doc_id: path}`
manifest. No new dependencies beyond what TOS already requires.

**Key decisions requiring ADR:**
- Rebuild strategy: full vs. incremental (mtime-based incremental for < 1000 docs)
- Index location: `.bob/kb-index/` vs. `docs/knowledge-base/.index/`
- TTL: rebuild if any document is newer than the index timestamp
- Corruption recovery: detect malformed index, fall back to per-query recompute

### P2-2 — Wire `KBIndexer` to `KnowledgeBaseQuery`

Extend `KnowledgeBaseQuery.__init__` to accept an optional
`index: PersistentEmbeddingIndex`. When provided, `query()` uses `index.search()`
instead of per-document embedding computation.

**Fallback chain** (graceful degradation at every level):
```
PersistentEmbeddingIndex  →  EmbeddingGenerator (P1-1)  →  keyword scorer (legacy)
    (fastest, persists)          (per-query, accurate)      (original, no deps)
```

### P2-3 — Optional L3 Cache for `MultiLevelCache`

`MultiLevelCache` currently has L1 (exact) and L2 (semantic, in-memory). An optional
L3 backed by `PersistentEmbeddingIndex` would survive process restarts.

**ADR required** — changes the cache persistence contract. Must address:
- Invalidation strategy
- Index corruption handling
- Whether L3 → L2 promotion occurs on hit

### P2 Timeline

| Week | Deliverable |
|------|-------------|
| 1 | ADR + `PersistentEmbeddingIndex` design + implementation |
| 2 | `KBIndexer`, `KnowledgeBaseQuery` integration, `bob-optimize index-kb` CLI command |
| 3 | Optional L3 cache, integration tests, documentation update |

---

## Scope Summary

```
P0 (~50 min total)           P1 (3–5 days)              P2 (2–3 weeks)
─────────────────────────    ─────────────────────────   ──────────────────────────
P0-1  ✅ Retraction banner    P1-1  KB query → embedding  P2-1  PersistentEmbeddingIndex
P0-2  ✅ Clone URL fixed      P1-2  Tag v1.0              P2-2  KBIndexer wired to KBQuery
P0-3  ✅ Already fixed (AF-1) P1-3  Subprocess compression P2-3  Optional L3 cache
P0-4  ✅ Already fixed (AF-2)       (opt-in + fallback)
P0-5  ✅ Scope note in place
       ↓
 "S6: CHANGELOG promotion     ↓                           ↓
  S7: tag v1.0 → P1"     "Integration Ready"        "Shared Embedding Layer"
                          KB search upgraded         Sessions persist
                          Context compression        L3 cache available
                          opt-in enabled             No per-query recompute
```

**The gate between P0 → P1 is the v1.0-rc1 / v1.0 tag.**
P1-3 (subprocess compression) must not wire to the KB Manager critical path
before P0 completes. Coupling a Beta/RC library to a stable product's retrieval
path is the exact maturity anti-pattern this plan avoids.

---

## References

- **Feasibility study:** [`../research/kb-tos-integration-feasibility-2026-07-14.md`](../research/kb-tos-integration-feasibility-2026-07-14.md)
- **Embedding layer concept:** [`../concepts/kb-tos-embedding-layer.md`](../concepts/kb-tos-embedding-layer.md)
- **Phase-8 sign-off audit:** [`../research/audit-2026-07-14-signoff.md`](../research/audit-2026-07-14-signoff.md)
- **Current TOS architecture:** [`../../../docs/architecture/architecture.md`](../../../docs/architecture/architecture.md)
- **Gap closure plan:** [`../../../gap-closure-plan.md`](../../../gap-closure-plan.md)
- **A+ plan:** [`../../../a-plus-plan.md`](../../../a-plus-plan.md)

---

*Last Updated: 2026-07-16*
*Category: Guide*
*Status: Active — P0 closed ✅ · S6/S7 (CHANGELOG + tag) open · P1 ready to start*
