# ADR-015: PersistentEmbeddingIndex — Design Decisions

**Status:** ✅ Accepted
**Date:** 2026-07-16
**Deciders:** Architecture team
**Context:** KB Manager ↔ TOS integration — P2-1 (shared embedding layer)

---

## Context

`EmbeddingGenerator` (P1-1) recomputes vectors on every `query()` call. For a 78-doc
KB at ~19ms/query that is acceptable, but it scales linearly with corpus size and
re-embeds the same unchanged documents on every Bob Shell session.

The A/B validation (2026-07-16) confirmed that the embedding scorer at `w=0.7`
meaningfully outperforms the keyword scorer (p@3: 0.68 vs 0.64; p@5: 0.80 vs 0.72).
A persistent index eliminates per-session recompute entirely.

Four design decisions must be made before implementation.

---

## Decision 1: Index Storage Location

**Decision:** `.bob/kb-index/`

**Rationale:**
- `.bob/` is already the workspace-local config directory used by this project
- The index is derived data (regenerable from the corpus); it must NOT be committed
- `.bob/kb-index/` will be added to `.gitignore` in this PR
- Alternative (`docs/knowledge-base/.index/`) would embed generated binaries inside
  the KB tree — clutters the knowledge base and risks accidental commits

**Structure:**
```
.bob/kb-index/
├── vectors.npy        ← float32 matrix [N × 1000]
└── manifest.json      ← {doc_id: {path, mtime, content_hash}}
```

---

## Decision 2: Rebuild Strategy

**Decision:** Incremental mtime-based rebuild (add/update changed docs, skip unchanged)

**Rationale:**
- Full rebuild on 78 docs takes ~250ms — acceptable for startup, excessive for every
  session when most documents haven't changed
- mtime comparison is O(N) filesystem stat calls — cheap
- content_hash in manifest catches cases where mtime was reset (e.g. `git checkout`)
- Corruption recovery: if `vectors.npy` fails to load or has wrong shape, fall back
  to full rebuild (never raise to caller)

**Algorithm:**
```
for doc in kb_docs:
    if doc not in manifest OR doc.mtime != manifest[doc].mtime:
        re-embed doc, update manifest row
rebuild vectors.npy from all manifest entries
```

---

## Decision 3: Corruption Recovery

**Decision:** Silent full-rebuild on any load failure, never raise to caller

**Rationale:**
- A corrupted index (partial write, wrong shape, missing file) must degrade gracefully
- The recovery path is: `vectors.npy` load fails → delete index dir → full rebuild
- If rebuild itself fails (disk full, etc.) → log warning, return empty search results
- `KnowledgeBaseQuery` must remain functional at the keyword-only level regardless

---

## Decision 4: L3 → L2 Promotion

**Decision:** No automatic promotion from L3 index to L2 SemanticCache

**Rationale:**
- L2 `SemanticCache` is keyed on prompt text; L3 is keyed on KB doc ID — different
  namespaces, different invalidation semantics
- Auto-promotion would require serialising KB doc embeddings back into the prompt
  cache, which crosses the system boundary this integration is designed to avoid
- P2-3 (optional L3 for MultiLevelCache) addresses the TOS-side persistence
  separately; the two are independent

---

## Interface Contract

```python
# src/embeddings/index.py
class PersistentEmbeddingIndex:
    def __init__(self, index_path: Path, embedder: EmbeddingGenerator) -> None: ...

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Return [(doc_id, score), ...] sorted descending. doc_id = relative KB path."""

    def index_document(self, doc_id: str, content: str) -> None:
        """Embed content and update the in-memory index (not yet flushed to disk)."""

    def rebuild(self, kb_path: Path) -> int:
        """Full or incremental rebuild. Returns count of docs indexed. Flushes to disk."""

    def is_stale(self, doc_path: Path) -> bool:
        """True if doc_path mtime or hash differs from manifest entry."""

    def flush(self) -> None:
        """Write vectors.npy + manifest.json atomically (tmp → rename)."""
```

```python
# src/embeddings/store.py
class FileBackedVectorStore:
    """Low-level NumPy .npy + JSON manifest r/w. Used only by PersistentEmbeddingIndex."""
    def load(self, index_path: Path) -> Tuple[np.ndarray, Dict]: ...
    def save(self, index_path: Path, matrix: np.ndarray, manifest: Dict) -> None: ...
```

```python
# src/embeddings/indexer.py
class KBIndexer:
    """Drives PersistentEmbeddingIndex over a KB directory tree."""
    def __init__(self, kb_path: Path, index: PersistentEmbeddingIndex) -> None: ...
    def sync(self) -> int:
        """Incremental sync: re-embed changed docs, return count of updated docs."""
```

---

## Consequences

### Added dependencies
None. NumPy (`np.save`/`np.load`) and `json` are already available.

### New `.gitignore` entry
`.bob/kb-index/` must be added to prevent committing binary index files.

### New package `src/embeddings/`
Introduces a third cross-package dependency: `src/embeddings/ → src/cache/embeddings.py`.
Legal under the layering gate.

### CLI extension (future)
`bob-optimize index-kb [--kb-path PATH] [--weight FLOAT]` — planned for P2 completion.
Not implemented in this ADR.

## Related
- A/B validation: `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md`
- ADR-014: `docs/adr/014-kb-query-embedding-scorer.md`
- Roadmap P2: `docs/knowledge-base/guides/kb-tos-integration-roadmap.md`
- Concept: `docs/knowledge-base/concepts/kb-tos-embedding-layer.md`
