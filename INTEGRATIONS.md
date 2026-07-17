# Integrations Guide

This document describes how external systems and tools integrate with the
**Token Optimization System** (`src/`) and the **Bob Shell Knowledge Manager**
(`config/`, `scripts/`).

---

## 1. Python Library

```python
from src.facade import TokenOptimizer

optimizer = TokenOptimizer()                      # uses config singleton defaults
result = optimizer.optimize("Your prompt here")
print(result["optimized_text"])                   # compressed text
print(result["compression_ratio"])                # e.g. 0.80 → 20% smaller
```

`TokenOptimizer` composes the full stack (L1 exact cache, L2 semantic cache,
prompt optimizer, truncator, monitoring) from a single `ConfigSchema`.

**Compression baseline:** ~20% mean on real in-repo prose (95% CI ≈ [19%, 21%],
N=183; manifest-backed: `evaluation/results/validation-2026-07-14/`).

---

## 2. CLI (`bob-optimize`)

```bash
# Install (from repo root)
pip install -e ".[dev,monitoring]"

# Optimize a prompt from stdin
echo "Your long prompt here" | bob-optimize optimize -

# Optimize a file
bob-optimize optimize path/to/prompt.txt

# JSON output (machine-readable)
echo "prompt" | bob-optimize optimize - --json
```

The `--json` flag emits: `{"optimized_text": "...", "compression_ratio": 0.80,
"token_count_before": 120, "token_count_after": 96}`.

---

## 3. KB Query Engine (P1 — hybrid scoring)

The Knowledge Base query tool (`src/tools/kb_query.py`) supports an optional
`EmbeddingGenerator` scorer alongside its keyword scorer:

```python
from src.tools.kb_query import KnowledgeBaseQuery
from src.cache.embeddings import EmbeddingGenerator

# Default: keyword-only (safe, no new dependencies)
kb = KnowledgeBaseQuery("docs/knowledge-base")
results = kb.query("caching strategy")

# Experimental: hybrid scoring (requires A/B validation — see ADR-014)
embedder = EmbeddingGenerator()
kb = KnowledgeBaseQuery(
    "docs/knowledge-base",
    embedder=embedder,
    embedding_weight=0.3,   # 30% embedding, 70% keyword
)
results = kb.query("caching strategy")
```

> ⚠️ **Do not raise `embedding_weight` above 0 without running an A/B validation**
> (see ADR-014). The `HashingVectorizer` cosine similarity measured 0.091 on a
> related pair — near-zero. The keyword scorer may rank KB documents more accurately
> for exact-term queries.

---

## 4. KB Manager — Opt-In Context Compression (P1-3)

The `knowledge-manager` Bob Shell mode can optionally compress retrieved KB context
before injecting it into a prompt. This is **opt-in** and requires `bob-optimize`
in `PATH`.

See `.bob/skills/kb-optimizer-integration.md` for the exact subprocess pattern,
fallback contract, and `preserve_structure` requirement.

**Quick reference:**

```bash
# Compress KB context before LLM injection (in knowledge-manager mode)
compressed=$(echo "$KB_CONTEXT" | bob-optimize optimize - --json \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['optimized_text'])")
# If bob-optimize unavailable, $compressed will be empty — use $KB_CONTEXT as fallback
```

Expected benefit: ~20% token reduction on retrieved context (manifest-backed).
Subprocess failure **must never block** knowledge retrieval.

---

## 5. P2 — Persistent Embedding Index (Shipped — P2 complete)

`src/embeddings/PersistentEmbeddingIndex` bridges the in-memory TOS semantic cache
(L2, session-scoped) and the KB Manager's session-persistent document store. The
package ships three public classes:

- **`PersistentEmbeddingIndex`** — disk-backed index; lazy load, incremental rebuild,
  atomic NumPy writes, mtime/hash staleness detection, corruption recovery.
- **`KBIndexer`** — wraps the index with a `sync()` + `query()` interface at
  `embedding_weight=0.7` (A/B-validated; see ADR-014).
- **`FileBackedVectorStore`** — atomic `os.replace`-based `.npy` / JSON I/O layer.

Wire the index into `KnowledgeBaseQuery` for the P2 fast path:

```python
from src.embeddings.indexer import KBIndexer
from src.tools.kb_query import KnowledgeBaseQuery

indexer = KBIndexer("docs/knowledge-base")
indexer.sync()                          # rebuild any stale document embeddings

kb = KnowledgeBaseQuery("docs/knowledge-base", index=indexer.index)
results = kb.query("caching strategy")  # index fast-path, keyword tie-breaker
```

See [`docs/adr/015-persistent-embedding-index.md`](docs/adr/015-persistent-embedding-index.md)
for design decisions and [`docs/knowledge-base/concepts/kb-tos-embedding-layer.md`](docs/knowledge-base/concepts/kb-tos-embedding-layer.md)
for the architecture concept.

---

## References

- Architecture: `docs/architecture/ARCHITECTURE.md`
- KB integration study: `docs/knowledge-base/research/kb-tos-integration-feasibility-2026-07-14.md`
- Integration roadmap: `docs/knowledge-base/guides/kb-tos-integration-roadmap.md`
- ADR-014 (embedding scorer): `docs/adr/014-kb-query-embedding-scorer.md`
