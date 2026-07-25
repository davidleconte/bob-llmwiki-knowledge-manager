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

**Compression baseline:** 6.8% mean on real in-repo prose (95% CI [6.2%, 7.4%],
N=265; manifest-backed: `evaluation/results/validation-2026-07-25/`). Supersedes the
20.0% of 2026-07-14 — see `STATUS.md` for the measured before/after.

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

Expected benefit: ~7% token reduction on retrieved context (manifest-backed).
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

## 6. P3 — Knowledge Graph Layer (Shipped — P3 complete)

`src/graph/` provides a pure-Python property graph over KB documents. Four
capabilities are available independently:

### Graph build

```python
from pathlib import Path
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH

KB_PATH = Path("docs/knowledge-base")

# Build embedding index (P2 prerequisite — skip if already built)
embedder = EmbeddingGenerator(backend="minilm")   # uses sentence-transformers if mlx absent
index = PersistentEmbeddingIndex(embedder=embedder)
index.rebuild(KB_PATH)

# Build graph (explicit + semantic edges)
builder = KnowledgeGraphBuilder(kb_path=KB_PATH, index=index, semantic_threshold=0.30)
graph = builder.build()

# Persist to .bob/kb-graph.json
GraphStore().save(DEFAULT_GRAPH_PATH, graph, {"built_at": "2026-07-17"})
```

Or from the CLI:

```bash
bob-optimize graph-build --kb-path docs/knowledge-base
```

### Graph-aware KB query

```python
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH
from src.tools.kb_query import KnowledgeBaseQuery

# Load persisted graph
graph = GraphStore().load(DEFAULT_GRAPH_PATH)   # None if not yet built

kb = KnowledgeBaseQuery(
    "docs/knowledge-base",
    embedder=embedder,
    embedding_weight=1.0,
    graph=graph,
    graph_weight=0.0,   # validated safe default — see note below
)
results = kb.query("caching strategy", max_results=10)
```

> ⚠️ **`graph_weight=0.0` is the validated default.** On an 80-document corpus
> with MiniLM embeddings, graph re-ranking at any tested weight (0.1–0.5) produced
> identical p@3/p@5/p@10 to embedding-only (p@3=0.88, no uplift, no regression).
> That p@3=0.88 is a MiniLM (`w=1.0`) lab number not reproducible in CI (MiniLM needs
> the optional `mlx-embeddings`/`sentence-transformers`); on the shipped default backend
> (`HashingVectorizer`, `w=0.7`, current 116-doc golden set) the reproducible manifest-backed
> result is p@3=0.84 with no net lift over keyword-only (`evaluation/results/retrieval-2026-07-19/`).
> The safe default is `0.0` — do not raise it without re-running the golden-set
> validation after any embedding model or corpus change. See ADR-017 and
> [`docs/knowledge-base/research/graph-validation-2026-07-17.md`](docs/knowledge-base/research/graph-validation-2026-07-17.md).

Or from the CLI:

```bash
bob-optimize graph-query "caching strategy" --kb-path docs/knowledge-base
```

### KB health analysis

```python
# Orphaned documents (no inbound links)
orphans = graph.orphans(edge_types=["explicit"])   # 39 in 80-doc corpus
print(f"{len(orphans)} orphans: {orphans[:5]}")

# Hub documents (most inbound links)
for doc_id, count in graph.hubs(top_k=5):
    print(f"{count:3d} inbound  {doc_id}")

# PageRank scores
pr = graph.pagerank()
top5 = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:5]
```

Or from the CLI:

```bash
bob-optimize graph-health --kb-path docs/knowledge-base
```

### Multi-hop traversal

```python
# All documents within 2 hops of a given document
neighbourhood = graph.neighbours("concepts/token-optimization.md", depth=2)
for doc_id, info in neighbourhood.items():
    print(f"  distance={info['distance']}  {doc_id}")

# Shortest path between two documents
path = graph.path("concepts/multi-level-caching.md", "guides/setup-token-optimization.md")
print(" → ".join(path) if path else "no path")
```

### MiniLM backend note

`EmbeddingGenerator(backend="minilm")` resolves via a priority fallback chain:

1. **`mlx-embeddings`** (Apple Silicon, ~2–4 ms warm): `pip install -e ".[mlx]"`
2. **`sentence-transformers`** (cross-platform, ~5–20 ms warm): `pip install sentence-transformers`
3. **`"hashing"` fallback** (no deps, always available)

MiniLM (384-dim dense) delivers p@3=0.88 vs hashing (1000-dim bag-of-ngrams)
p@3=0.60 on the KB golden set — but that 0.88 is a MiniLM (`w=1.0`) lab number not
reproducible in CI (MiniLM needs the optional `mlx-embeddings`/`sentence-transformers`).
On the shipped default backend (`HashingVectorizer`, `w=0.7`, current 116-doc golden set)
the reproducible manifest-backed result is p@3=0.84 with no net lift over keyword-only
(`evaluation/results/retrieval-2026-07-19/`). Use MiniLM for best retrieval quality.

---

## References

- Architecture: `docs/architecture/architecture.md` (§3b, §5 graph section)
- KB integration study: `docs/knowledge-base/research/kb-tos-integration-feasibility-2026-07-14.md`
- Integration roadmap: `docs/knowledge-base/guides/kb-tos-integration-roadmap.md`
- ADR-014 (embedding scorer): `docs/adr/014-kb-query-embedding-scorer.md`
- ADR-017 (knowledge graph): `docs/adr/017-knowledge-graph-layer.md`
- Graph validation results: `docs/knowledge-base/research/graph-validation-2026-07-17.md`
