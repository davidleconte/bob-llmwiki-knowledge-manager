---
title: "Knowledge Graph Usage Guide"
category: guides
tags: [guides]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Knowledge Graph Usage Guide

## Overview

This guide covers the complete workflow for building, persisting, querying, and
interpreting the KB knowledge graph (`src/graph/`). It assumes the Python Token
Optimization System is installed (`pip install -e ".[dev,monitoring]"`).

For the conceptual background — what the graph is, why it exists, and what each
module does — see the [Knowledge Graph Layer concept](../concepts/knowledge-graph-layer.md).

## Prerequisites

- Python ≥ 3.11, `pip install -e ".[dev,monitoring]"` or `uv sync`
- A KB directory at `docs/knowledge-base/` (or any path you pass to `--kb-path`)
- Recommended: MiniLM backend for best retrieval quality

```bash
# MiniLM on Apple Silicon (fastest)
pip install -e ".[mlx]"

# MiniLM cross-platform (CPU / Linux / Intel Mac)
pip install sentence-transformers

# Neither installed? Falls back to hashing — KB retrieval still works
```

## Steps

### Step 1: Build the embedding index (prerequisite)

The graph builder queries the embedding index for semantic edges. Build it first:

```bash
bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
```

Or from Python:

```python
from pathlib import Path
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex

embedder = EmbeddingGenerator(backend="minilm")
index = PersistentEmbeddingIndex(embedder=embedder)
index.rebuild(Path("docs/knowledge-base"))
print(f"Indexed {len(index)} chunks")
```

The index is stored at `.bob/kb-index/` and is incremental — only changed files are
re-embedded on subsequent runs.

### Step 2: Build and persist the graph

```bash
bob-optimize graph-build --kb-path docs/knowledge-base
```

Or from Python:

```python
from pathlib import Path
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH

KB_PATH = Path("docs/knowledge-base")
embedder = EmbeddingGenerator(backend="minilm")
index = PersistentEmbeddingIndex(embedder=embedder)

graph = KnowledgeGraphBuilder(
    kb_path=KB_PATH,
    index=index,
    semantic_threshold=0.30,   # validated default — do not lower without re-running golden set
).build()

GraphStore().save(DEFAULT_GRAPH_PATH, graph, {"built_at": "2026-07-18"})
print(f"Nodes: {len(graph.nodes)}   Edges: {len(graph.edges)}")
```

The graph is stored at `.bob/kb-graph.json` (atomic write — safe to interrupt).

### Step 3: Run a structural health report

```bash
bob-optimize graph-health --kb-path docs/knowledge-base
```

Expected output:

```
KB Graph Health Report
======================
Nodes:           80
Edges:         2836  (163 explicit + 2654 semantic + 19 broken)
Orphans:          13  (documents with no explicit inbound links)
Broken links:     19

Top hubs (most inbound links):
  12  concepts/multi-level-caching.md
   9  concepts/token-optimization.md
   7  guides/setup-token-optimization.md
   ...

PageRank top-5:
  0.0421  concepts/multi-level-caching.md
  0.0318  concepts/token-optimization.md
  ...
```

### Step 4: Fix orphan documents

For each orphan reported, open the document and add a `related:` frontmatter key
pointing to at least one other KB document:

```yaml
---
title: My Concept
date: 2026-07-18
related:
  - concepts/token-optimization.md
  - guides/setup-token-optimization.md
---
```

Then rebuild the graph (`Step 2`) to confirm the orphan count drops.

### Step 5: Query the graph

**Graph-aware KB search (CLI):**

```bash
bob-optimize graph-query "caching strategy" \
  --kb-path docs/knowledge-base \
  --graph-weight 0.0          # validated safe default
```

**Graph-aware KB search (Python):**

```python
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH
from src.tools.kb_query import KnowledgeBaseQuery

graph = GraphStore().load(DEFAULT_GRAPH_PATH)   # None if not yet built

kb = KnowledgeBaseQuery(
    "docs/knowledge-base",
    embedder=embedder,
    embedding_weight=1.0,
    graph=graph,
    graph_weight=0.0,   # raise only after re-running golden-set validation
)
results = kb.query("caching strategy", max_results=10)
for r in results:
    print(f"  {r.score:.3f}  {r.doc_id}")
```

**Multi-hop traversal:**

```python
neighbourhood = graph.neighbours("concepts/token-optimization.md", depth=2)
for doc_id, info in sorted(neighbourhood.items(), key=lambda x: x[1]["distance"]):
    print(f"  distance={info['distance']}  {doc_id}")
```

**Shortest path between two documents:**

```python
path = graph.path(
    "concepts/multi-level-caching.md",
    "guides/setup-token-optimization.md"
)
print(" → ".join(path) if path else "no path")
```

## Verification

After building, verify the graph is healthy:

```bash
bob-optimize graph-health --kb-path docs/knowledge-base
```

Expected indicators of a healthy graph:

| Metric | Healthy | Investigate if… |
|--------|---------|-----------------|
| Orphan count | < 20% of node count | > 40% — most documents are disconnected |
| Broken links | 0 | Any — indicates deleted/renamed files with stale refs |
| Hub count | ≥ 3 hubs with > 5 inbound | 0 — no conceptual anchors exist |
| Semantic edges | > 5× explicit edges | 0 — embedding index not built or threshold too high |

## Troubleshooting

### T1 — `GraphStore().load()` returns `None`

**Cause:** The graph has not been built yet, or `.bob/kb-graph.json` was deleted.  
**Fix:** Run `bob-optimize graph-build --kb-path docs/knowledge-base`.

### T2 — Orphan count is unexpectedly high after a build

**Cause:** Most documents lack `related:` frontmatter, and the semantic threshold (0.30)
is too high for the embedding backend in use.  
**Fix (short-term):** Add `related:` frontmatter to key documents.  
**Fix (long-term):** Switch to MiniLM — hashing p@3=0.60 vs MiniLM p@3=0.88 on
the same corpus; semantic edges are much more accurate with MiniLM.

### T3 — `semantic_threshold` produces too many or too few edges

**Cause:** The 0.30 threshold was validated on a MiniLM-encoded 80-doc corpus.
HashingVectorizer cosine scores are compressed toward zero.  
**Fix:** Use `EmbeddingGenerator(backend="minilm")`. If you must use hashing, lower
the threshold — but expect noisier edges and re-run your golden-set evaluation.

### T4 — `graph-build` fails with `"index not built"`

**Cause:** `PersistentEmbeddingIndex` has not been synced yet.  
**Fix:** Run `bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic` first.

## Best Practices

1. **Rebuild after adding documents.** The graph is a snapshot — it does not
   auto-update when the KB changes. Rebuild after any batch of new documents.

2. **Use `related:` frontmatter consistently.** Explicit edges are more reliable
   than semantic edges for closely related documents in the same category.

3. **Keep `graph_weight=0.0` until your corpus grows.** The validated result on
   80 documents showed no retrieval uplift from PageRank blending. Re-test once you
   exceed ~200 documents or change your embedding model.

4. **Check `graph-health` before a KB audit.** Broken links and orphans are the
   fastest indicators that the KB needs maintenance.

5. **Commit `.bob/kb-graph.json`.** The graph file is small (JSON, ~50 KB for
   80 documents) and makes `graph-health` available without a rebuild in CI.

## Related Documents

- [Knowledge Graph Layer](../concepts/knowledge-graph-layer.md) — concept + module breakdown
- [KB-TOS Shared Embedding Layer](../concepts/kb-tos-embedding-layer.md)
- [ADR-017: Knowledge Graph Layer](../../adr/017-knowledge-graph-layer.md)
- [Live Validation Report](../research/graph-validation-2026-07-17.md)

## References

- [Architecture §3b — KB query dataflow](../../architecture/ARCHITECTURE.md)
- [INTEGRATIONS.md §6 — P3 Graph Layer](../../../INTEGRATIONS.md)

---
*Last Updated: 2026-07-18*
*Category: Guide*
