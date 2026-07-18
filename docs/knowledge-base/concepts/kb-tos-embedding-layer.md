---
title: "KB-TOS Shared Embedding Layer"
date: 2026-07-14
type: concept
status: proposed
adversarial_audit: 2026-07-16
tags: [architecture, embedding, kb-manager, token-optimizer, p2, persistent-index, integration, compact-summary]
related:
  - ../research/kb-tos-integration-feasibility-2026-07-14.md
  - ../guides/kb-tos-integration-roadmap.md
  - multi-level-caching.md
  - token-optimization.md
  - knowledge-graph-layer.md
  - delegation-analysis-pipeline.md
---

# KB-TOS Shared Embedding Layer

> ⚠️ **Adversarial audit applied 2026-07-16.** Two factual errors corrected:
> (1) `.bob/` is **not gitignored** — the storage rationale is revised.
> (2) Embedding dimension in CLI example was `47 × 1024` (wrong) — corrected to `47 × 1000`.
> Memory risk of `EmbeddingGenerator.embeddings_cache` documented in Quality Attributes.

## Overview

A proposed infrastructure layer (`src/embeddings/`) that both the Knowledge Manager
query engine and the Token Optimization System's semantic cache can share. It solves
the two deepest integration challenges identified in the feasibility study:

1. **C4 — In-memory vs. persistent persistence mismatch:** TOS's L2 cache is in-memory
   only; the KB's value is persistence across sessions. A `FileBackedVectorStore` bridges
   this gap without touching either system's core logic.
2. **C5 — Duplicate TF-IDF implementations:** `kb_query.py` and `semantic_cache.py`
   implement the same algorithm class independently. A shared `EmbeddingGenerator` wrapper
   unifies them at the infrastructure level.

This concept is the target architecture for **P2** in the integration roadmap.

---

## Key Points

- The embedding layer is **shared infrastructure, not a merged system** — both KB Manager
  and TOS use it independently via their own entry points
- It uses only dependencies TOS already has (`numpy`, `scikit-learn`) — no new installs
- It is designed as an optional enhancement; both systems fall back gracefully without it
- P1 (`EmbeddingGenerator` injection into `KnowledgeBaseQuery`) is the stepping stone
  that makes P2 safe to build

---

## Design

### Component Map

```
src/embeddings/                        ← new shared layer (P2)
├── __init__.py
├── index.py     PersistentEmbeddingIndex
├── store.py     FileBackedVectorStore
└── indexer.py   KBIndexer

src/cache/embeddings.py                ← already exists (EmbeddingGenerator)
src/tools/kb_query.py                  ← upgraded in P1 to inject EmbeddingGenerator
src/cache/semantic_cache.py            ← optionally upgraded in P2 to use L3
src/cache/multi_level_cache.py         ← optionally extended with L3 in P2
```

### `PersistentEmbeddingIndex`

The core new class. Stores computed embeddings on disk so they survive process restarts
and do not need to be recomputed on every Bob Shell session.

```python
class PersistentEmbeddingIndex:
    """Disk-backed embedding index for semantic document search.

    Storage layout:
      <index_path>/vectors.npy     — float32 matrix [N × embedding_dim]
      <index_path>/manifest.json   — {doc_id: {path, mtime, hash}}

    Thread-safety: single-writer (KBIndexer), multiple-reader (KBQuery / SemanticCache).
    """

    def __init__(self, index_path: Path, embedder: EmbeddingGenerator): ...

    def index_document(self, doc_id: str, content: str) -> None:
        """Compute and store the embedding for one document."""

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Return (doc_id, similarity_score) pairs for the top-k matches."""

    def rebuild(self, kb_path: Path) -> int:
        """Full rebuild: re-embed all documents under kb_path. Returns count."""

    def update(self, kb_path: Path) -> int:
        """Incremental update: only re-embed documents newer than their stored mtime."""

    def is_stale(self, doc_path: Path) -> bool:
        """True if doc_path has been modified since it was last indexed."""
```

### `FileBackedVectorStore`

Pure I/O layer under `PersistentEmbeddingIndex`. Decoupled for testability.

```python
class FileBackedVectorStore:
    """Read/write the .npy matrix and manifest.json atomically.

    Writes are atomic: write to <file>.tmp then rename. Reads are safe
    (read-only mmap on .npy). On read of a corrupt file, raises
    CorruptIndexError so callers can trigger a rebuild.
    """
```

### `KBIndexer`

Orchestrates `PersistentEmbeddingIndex.update()` at the right times:

```python
class KBIndexer:
    """Rebuild or update the persistent embedding index.

    Usage:
        # From CLI (added to bob-optimize in P2):
        bob-optimize index-kb --kb-path docs/knowledge-base

        # Programmatic (called by KnowledgeBaseQuery on first use):
        indexer = KBIndexer(index_path, embedder)
        indexer.ensure_fresh(kb_path)  # incremental update if stale
    """
```

---

## Storage Layout

```
.bob/kb-index/                ← default location (co-located with Bob config)
├── vectors.npy               ← float32 matrix, one row per document
├── manifest.json             ← {doc_id: {path, mtime, content_hash, indexed_at}}
└── metadata.json             ← {embedder_class, embedding_dim, kb_path, built_at}
```

**Why `.bob/kb-index/` not `docs/knowledge-base/.index/`:**
- `.bob/` is **not currently in `.gitignore`** *(adversarial audit finding AF-6:
  `git check-ignore .bob/` returns nothing)*. The index location choice still makes
  sense, but the rationale must be: add `.bob/kb-index/` to `.gitignore` as part of
  P2 implementation — index files are machine-generated, large binary artifacts, and
  should never be committed.
- Index files are machine-local (different machines produce identical but
  independently-generated copies — no need to share via git)
- Keeps `docs/` clean of generated binary artifacts

**Index invalidation rules:**
1. `metadata.json` `embedder_class` differs from current → full rebuild
2. Any document's `mtime` is newer than its `indexed_at` → incremental update
3. `vectors.npy` is missing or corrupt → full rebuild with `CorruptIndexError` logged
4. `manifest.json` is missing → full rebuild

---

## Integration Points

### Into `KnowledgeBaseQuery` (P2-2)

```python
class KnowledgeBaseQuery:
    def __init__(
        self,
        kb_path: str = "docs/knowledge-base",
        embedder: Optional[EmbeddingGenerator] = None,
        index: Optional[PersistentEmbeddingIndex] = None,   # P2 addition
    ):
        ...

    def query(self, query: str, ...) -> Dict:
        if self._index and not self._index.is_stale(self.kb_path):
            # Fast path: persistent index (P2)
            return self._query_from_index(query, ...)
        elif self._embedder:
            # Medium path: per-query embedding (P1)
            return self._query_with_embeddings(query, ...)
        else:
            # Slow path: keyword scoring (legacy)
            return self._query_keyword(query, ...)
```

### Into `MultiLevelCache` as Optional L3 (P2-3)

```
L1 ExactCache     — exact SHA-256 match       — <1ms    — in-memory
L2 SemanticCache  — cosine similarity ≥0.85  — <100ms  — in-memory
L3 PersistentEmbeddingIndex  — cosine search  — <500ms  — disk, survives restarts
```

L3 is strictly optional. `MultiLevelCache` gains an optional `l3_index: Optional[PersistentEmbeddingIndex]` constructor parameter, defaulting to `None`. An L3 hit promotes to L2 (same L2→L1 promotion pattern already in use).

---

## Quality Attributes

| Attribute | Target | Verification |
|-----------|--------|-------------|
| **Latency (full rebuild)** | < 5s for 200 docs | Benchmark: `bob-optimize index-kb` |
| **Latency (incremental)** | < 500ms for 1–5 changed docs | Unit test with mocked mtime |
| **Search latency** | < 50ms for 200-doc index | `pytest tests/embeddings/ -m slow` |
| **Corruption recovery** | Raises `CorruptIndexError`, triggers rebuild | Regression test |
| **Determinism** | Same corpus + config → same index | Property test with fixed seed |
| **No new deps** | Only `numpy`, `scikit-learn` (already required) | `pyproject.toml` unchanged |
| **Memory (EmbeddingGenerator cache)** | `use_cache=False` for document embeddings; `use_cache=True` for query embeddings only | Unit test confirms no full-text key in cache after indexing |

**Memory note (adversarial audit finding AF-5):** `EmbeddingGenerator.embeddings_cache`
stores full text strings as dict keys with no eviction on that dict (only `self.corpus`
has LRU). Measured: 856KB key memory for 30 docs (~5.7MB projected for 200 docs).
`KBIndexer.index_document()` must call `embedder.generate(content, use_cache=False)`
to avoid accumulating all document text in memory during a full index rebuild.

---

## Examples

### Example 1: CLI Index Build

```bash
# Initial build (first use)
bob-optimize index-kb --kb-path docs/knowledge-base

# Output:
# Indexed 47 documents in 1.3s
# Index written to .bob/kb-index/ (vectors.npy: 47 × 1000)
# Note: embedding dim is 1000 (EmbeddingGenerator default max_features=1000)

# Incremental update (subsequent runs, only 2 docs changed)
bob-optimize index-kb --kb-path docs/knowledge-base
# Updated 2 documents in 0.08s (45 unchanged)
```

### Example 2: KBQuery with Persistent Index

```python
from pathlib import Path
from src.tools.kb_query import KnowledgeBaseQuery
from src.embeddings.index import PersistentEmbeddingIndex
from src.cache.embeddings import EmbeddingGenerator

embedder = EmbeddingGenerator()
index = PersistentEmbeddingIndex(Path(".bob/kb-index"), embedder)
index.update(Path("docs/knowledge-base"))  # incremental, fast on second run

kb = KnowledgeBaseQuery(index=index)
results = kb.query("how does the semantic cache work")
# Returns ranked results using persistent embeddings — no per-query recompute
```

---

## Decisions Required (ADR Topics)

Before implementing P2, the following must be documented in ADRs:

| # | Decision | Options |
|---|---------|---------|
| ADR-014 | Index storage location | `.bob/kb-index/` vs. `docs/knowledge-base/.index/` |
| ADR-015 | Rebuild strategy | Full rebuild vs. mtime-based incremental |
| ADR-016 | L3 cache invalidation | Version-based vs. content-hash vs. mtime |
| ADR-017 | L3 promotion policy | L3 → L2 promotion on hit (same as L2→L1) vs. read-only |

---

## Related Documents

- **Integration feasibility study:** [`../research/kb-tos-integration-feasibility-2026-07-14.md`](../research/kb-tos-integration-feasibility-2026-07-14.md)
- **P0/P1/P2 roadmap:** [`../guides/kb-tos-integration-roadmap.md`](../guides/kb-tos-integration-roadmap.md)
- **Multi-level caching concept:** [`multi-level-caching.md`](multi-level-caching.md)
- **Token optimization concept:** [`token-optimization.md`](token-optimization.md)
- **Existing embedding infrastructure:** `src/cache/embeddings.py`
- **Existing KB query tool:** `src/tools/kb_query.py`
- **Current cache architecture:** `docs/architecture/architecture.md §5`

---

*Last Updated: 2026-07-16 (adversarial audit corrections)*
*Category: Concept*
*Status: Proposed — target architecture for P2*
