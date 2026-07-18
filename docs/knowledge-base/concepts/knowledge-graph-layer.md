# Knowledge Graph Layer (P3)

## Overview

The knowledge graph layer (`src/graph/`) builds a **property graph over the KB document
corpus** for structural health analysis, multi-hop traversal, and PageRank-based
re-ranking of search results. It is opt-in, fully backward-compatible, and shipped as
part of the Python Token Optimization System. Every KB document becomes a node; every
explicit cross-reference and every semantically similar document pair becomes an edge.

## Key Points

- **Two edge types:** explicit (frontmatter `related:` lists + inline `[text](path)`
  links) and semantic (cosine similarity ≥ 0.30 from `PersistentEmbeddingIndex`)
- **Four modules:** `graph.py` · `builder.py` · `ranker.py` · `store.py` — each
  independently usable
- **Validated defaults:** `semantic_threshold=0.30`, `graph_weight=0.0` (confirmed
  on 80-doc corpus — graph adds value via structural analysis, not score blending)
- **CLI entry points:** `bob-optimize graph-build` · `graph-query` · `graph-health`

## Details

### Module Responsibilities

| Module | Class | Responsibility |
|--------|-------|----------------|
| `src/graph/graph.py` | `KnowledgeGraph` | Adjacency dict, BFS traversal, PageRank (power method, damping=0.85, tol=1e-6), `orphans()`, `hubs()` |
| `src/graph/builder.py` | `KnowledgeGraphBuilder` | Walks KB files; parses frontmatter `related:` + inline links for **explicit** edges; queries `PersistentEmbeddingIndex` per document and applies max-aggregation for **semantic** edges |
| `src/graph/ranker.py` | `GraphRanker` | Lazy PageRank cache; `rerank()` blend formula: `final = (1−w)·similarity + w·pagerank·15.0` |
| `src/graph/store.py` | `GraphStore` | Atomic `os.replace`-based JSON persistence to `.bob/kb-graph.json` |

### NodeProps (10 fields)

Every node stores:

| Field | Source | Added |
|-------|--------|-------|
| `title` | Frontmatter `title:` or `# H1` | P3 |
| `category` | KB directory name | P3 |
| `tags` | Frontmatter `tags:` | P3 |
| `date` | Frontmatter `date:` | P3 |
| `type` | Frontmatter `type:` | P3 |
| `status` | Frontmatter `status:` | P3 |
| `mtime_epoch` | `path.stat().st_mtime` | P4 |
| `content_length` | `len(content)` chars | P4 |
| `description` | First body paragraph ≤ 200 chars | P4 |
| `related_refs` | Raw frontmatter `related:` list | P4 |

P4 fields have backward-compatible defaults; old `.bob/kb-graph.json` files load cleanly.

### Edge Types

| Type | Weight | Source | Excluded from PageRank? |
|------|--------|--------|------------------------|
| `explicit` | 1.0 | Frontmatter `related:` + inline links | No |
| `semantic` | cosine score (0.30–1.0) | `PersistentEmbeddingIndex` similarity | No |
| `broken` | 0.0 | Link target not found on disk | Yes |

### PageRank Re-ranking

`GraphRanker.rerank()` blends the embedding similarity score with the document's
PageRank:

```
final_score = (1 − graph_weight) × similarity + graph_weight × pagerank × 15.0
```

`graph_weight=0.0` is the validated default — it disables score blending while leaving
structural analysis fully functional. Raise it only after re-running the golden-set
validation on your corpus. See [ADR-017](../../adr/017-knowledge-graph-layer.md).

## Benefits

| Benefit | Problem Solved | Measured Outcome |
|---------|----------------|------------------|
| **Orphan detection** | Documents with no inbound links are invisible to retrieval | 80-doc corpus: 39 orphans; semantic edges rescued 26 (13 explicit orphans remain) |
| **Hub identification** | Conceptual anchors of the KB are not discoverable without traversal | `graph.hubs(top_k=5)` returns most-cited documents by inbound-link count |
| **Broken-link detection** | Cross-references to deleted/renamed files silently rot | Builder stores `"broken"` edges; `graph-health` reports them |
| **Multi-hop traversal** | Documents 2+ hops away are invisible to keyword + embedding search | `graph.neighbours(doc_id, depth=2)` returns all documents within N hops |
| **PageRank re-ranking** | Embedding similarity treats all documents as equally authoritative | Score blending available when corpus grows; safe-off default avoids regression |
| **Structural health CLI** | No visibility into KB connectivity without querying every file | `bob-optimize graph-health` prints orphan count, hubs, broken links, PageRank top-10 |

## Examples

### Build the graph (Python)

```python
from pathlib import Path
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH

KB_PATH = Path("docs/knowledge-base")
embedder = EmbeddingGenerator(backend="minilm")
index = PersistentEmbeddingIndex(embedder=embedder)
index.rebuild(KB_PATH)

graph = KnowledgeGraphBuilder(kb_path=KB_PATH, index=index).build()
GraphStore().save(DEFAULT_GRAPH_PATH, graph)
print(f"Nodes: {len(graph.nodes)}  Edges: {len(graph.edges)}")
```

### Structural health (Python)

```python
orphans = graph.orphans(edge_types=["explicit"])
for doc_id, count in graph.hubs(top_k=5):
    print(f"  {count:3d} inbound  {doc_id}")
```

### CLI

```bash
bob-optimize graph-build  --kb-path docs/knowledge-base
bob-optimize graph-health --kb-path docs/knowledge-base
bob-optimize graph-query  "caching strategy" --kb-path docs/knowledge-base
```

## Related Documents

- [Knowledge Graph Usage Guide](../guides/knowledge-graph-usage-guide.md)
- [KB-TOS Shared Embedding Layer](./kb-tos-embedding-layer.md)
- [Multi-Level Caching](./multi-level-caching.md)
- [ADR-017: Knowledge Graph Layer](../../adr/017-knowledge-graph-layer.md)
- [Live Validation Report](../research/graph-validation-2026-07-17.md)

## References

- [Architecture §5 — Knowledge Graph](../../architecture/ARCHITECTURE.md)
- [INTEGRATIONS.md §6 — P3 Graph Layer](../../../INTEGRATIONS.md)

---
*Last Updated: 2026-07-18*
*Category: Concept*
