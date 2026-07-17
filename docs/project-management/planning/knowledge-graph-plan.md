# Knowledge Graph Layer — Implementation Plan

**File:** `docs/project-management/planning/knowledge-graph-plan.md`  
**Status:** Draft — awaiting user confirmation  
**Scope:** `src/graph/`, `src/tools/kb_query.py` extension, `tests/graph/`, ADR-017  
**Prerequisite:** P2 persistent embedding index in place (done — `src/embeddings/`)  

---

## Top-Level Overview

### Goal

Build a lightweight, pure-Python, in-memory property graph over the KB document
corpus — persisted to a single JSON file between sessions — that enables:

1. **Multi-hop traversal:** "show me everything within 2 hops of this document"
2. **Structural health:** find orphaned documents, isolated clusters, hub documents
3. **Re-ranking:** blend PageRank importance into `KnowledgeBaseQuery` result ordering
4. **CLI commands:** `bob-optimize graph-build`, `graph-query`, `graph-health`

### Approach

- **No external graph library.** At ≤ 500 KB documents, a plain Python
  `dict[str, list[tuple]]` adjacency list is sufficient. NetworkX adds 30MB of
  dependency for no functional benefit at this scale.
- **Two edge types:** `explicit` (parsed from frontmatter `related:` + inline
  `[text](path)` markdown links) and `semantic` (cosine similarity above a
  configurable threshold, derived from the existing `PersistentEmbeddingIndex`).
- **File-level nodes only.** The embedding index operates at chunk level
  (`category/file.md#slug`) but the graph operates at **document level**
  (`category/file.md`). Semantic edges are derived by aggregating per-chunk
  similarity to a per-document score.
- **Optional injection pattern.** The graph is injected into
  `KnowledgeBaseQuery` the same way `embedder` and `index` are today — a
  `graph=None` constructor parameter. Zero impact on callers that don't use it.
- **ADR-017** documents the design decisions.

### Non-Goals

- Not a graph database (Neo4j, Dgraph, etc.)
- Not a real-time update system (graph is rebuilt on demand, like the embedding index)
- Not a visualisation tool (data model only; rendering is out of scope)
- Does not replace semantic search (graph re-ranking is additive, not a replacement)

---

## Architecture

### New Package: `src/graph/`

```
src/graph/
├── __init__.py          KnowledgeGraph (public API), exported symbols
├── builder.py           KnowledgeGraphBuilder — builds graph from KB filesystem
├── graph.py             KnowledgeGraph — in-memory property graph, query API
├── store.py             GraphStore — atomic JSON persistence (.bob/kb-graph.json)
└── ranker.py            GraphRanker — PageRank, neighbourhood traversal
```

### New Test Package: `tests/graph/`

```
tests/graph/
├── __init__.py
├── test_builder.py      KnowledgeGraphBuilder unit tests
├── test_graph.py        KnowledgeGraph unit tests (traversal, health)
├── test_store.py        GraphStore persistence tests
└── test_ranker.py       PageRank and neighbourhood tests
```

### Storage: `.bob/kb-graph.json`

```json
{
  "nodes": {
    "concepts/caching.md": {
      "title": "Multi-Level Caching",
      "category": "concepts",
      "tags": ["caching", "architecture"],
      "date": "2026-07-13",
      "type": "concept",
      "status": "active"
    }
  },
  "edges": [
    {
      "source": "concepts/caching.md",
      "target": "guides/setup-token-optimization.md",
      "type": "explicit",
      "weight": 1.0,
      "label": "Setting Up Token Optimization System"
    },
    {
      "source": "concepts/caching.md",
      "target": "concepts/token-optimization.md",
      "type": "semantic",
      "weight": 0.73,
      "label": null
    }
  ],
  "metadata": {
    "built_at": "2026-07-17T10:00:00",
    "kb_path": "docs/knowledge-base",
    "node_count": 78,
    "edge_count": 312,
    "semantic_threshold": 0.3
  }
}
```

### Integration Point: `KnowledgeBaseQuery`

```python
# Existing constructor — new graph= parameter added
KnowledgeBaseQuery(
    kb_path="docs/knowledge-base",
    embedder=None,
    embedding_weight=0.0,
    index=None,
    graph=None,            # ← new: KnowledgeGraph | None
    graph_weight=0.0,      # ← new: [0.0, 1.0] blend for PageRank re-ranking
)
```

When `graph` and `graph_weight > 0`, the final result score is:

```
final_score = (1 - graph_weight) * similarity_score
            + graph_weight       * pagerank_score * SCALE
```

---

## Sub-Tasks

---

### Sub-Task 1 — ADR-017: Knowledge Graph Layer Design Decision

**Status:** `[ ] pending`

**Intent**

Document the design decisions before any code is written. The ADR records the
trade-offs that future maintainers need to understand: why plain dict over
NetworkX, why file-level nodes over chunk-level, why two edge types, how
semantic edges are derived from the embedding index, and why PageRank is
blended rather than replacing the similarity scorer.

**Expected Outcomes**

- `docs/adr/017-knowledge-graph-layer.md` exists and covers:
  - Decision 1: pure-Python adjacency list vs NetworkX (scope: ≤ 500 docs)
  - Decision 2: file-level nodes (not chunk-level) and the aggregation rule
  - Decision 3: two edge types (explicit / semantic) and their weight semantics
  - Decision 4: persistence format (JSON, `.bob/kb-graph.json`, atomic writes)
  - Decision 5: PageRank damping default (0.85), max iterations (100), convergence tol (1e-6)
  - Decision 6: semantic threshold default (0.3) and validation criteria
  - Decision 7: optional injection into `KnowledgeBaseQuery` (backward-compatible)

**Todo List**

1. Create `docs/adr/017-knowledge-graph-layer.md`
2. Record all 7 decisions with context, options considered, and rationale
3. Add the ADR to the README table in `docs/adr/README.md`

**Relevant Context**

- Pattern: `docs/adr/014-kb-query-embedding-scorer.md`, `docs/adr/015-persistent-embedding-index.md`
- Frontmatter fields available on KB docs: `title`, `date`, `type`, `status`, `tags`, `related`
- `PersistentEmbeddingIndex.search()` returns `[(doc_id#slug, score)]` — chunks, not files
- ADR numbers already taken: 001–016

---

### Sub-Task 2 — `KnowledgeGraph` core data model (`src/graph/graph.py`)

**Status:** `[ ] pending`

**Intent**

Implement the in-memory property graph. This is the central data structure:
nodes are documents, edges are relationships. It owns the traversal and health
query API but does not own building (that is `KnowledgeGraphBuilder`) or
persistence (that is `GraphStore`).

**Expected Outcomes**

- `KnowledgeGraph` class with:
  - Internal representation: `dict[str, NodeProps]` for nodes,
    `dict[str, list[Edge]]` for adjacency (source → list of edges)
  - `add_node(doc_id, **props) → None`
  - `add_edge(source, target, edge_type, weight, label) → None`
  - `neighbours(doc_id, depth=1, edge_types=None) → dict` — BFS to given depth,
    returns `{doc_id: {distance, edges_traversed}}`
  - `orphans() → list[str]` — nodes with zero inbound explicit edges
  - `hubs(top_k=10) → list[(doc_id, inbound_count)]` — by inbound edge count
  - `path(source, target) → list[str] | None` — shortest path via BFS
  - `pagerank(damping=0.85, max_iter=100, tol=1e-6) → dict[str, float]`
  - `node_count`, `edge_count` properties
- `NodeProps` dataclass with fields: `title`, `category`, `tags`, `date`, `type`, `status`
- `Edge` dataclass with fields: `source`, `target`, `edge_type`, `weight`, `label`
- All methods are pure (no I/O, no filesystem)
- `tests/graph/test_graph.py` covers: add/query, BFS to depth 1/2, orphan detection,
  hub ranking, shortest path, PageRank convergence, empty graph edge cases

**Relevant Context**

- No external dependencies: `dict`, `collections.deque` for BFS
- `doc_id` format: `"category/filename.md"` (file-level, no `#slug`)
- Nodes can reference docs that exist in the KB filesystem or may be broken links
- PageRank: iterative power method, converge when L∞ norm of update < tol

---

### Sub-Task 3 — `GraphStore` persistence (`src/graph/store.py`)

**Status:** `[ ] pending`

**Intent**

Atomic JSON persistence for the graph — the same write-tmp-then-rename pattern
used by `FileBackedVectorStore`. Keeps I/O fully decoupled from graph logic.

**Expected Outcomes**

- `GraphStore` class with:
  - `save(graph_path, graph) → None` — serialises `KnowledgeGraph` to JSON atomically
  - `load(graph_path) → KnowledgeGraph | None` — returns `None` on missing or corrupt file
  - JSON format: `{nodes: {...}, edges: [...], metadata: {...}}` per the storage spec above
  - Atomic write: temp file in same directory + `os.replace()`
  - On corrupt JSON: log warning, return `None` (caller triggers full rebuild)
- `tests/graph/test_store.py` covers: roundtrip, missing file → None, corrupt JSON → None,
  write failure cleans temp file

**Relevant Context**

- Pattern: `src/embeddings/store.py:FileBackedVectorStore` — exact same pattern
- Default path: `.bob/kb-graph.json` (constant `DEFAULT_GRAPH_PATH`)
- JSON is human-readable (indent=2) — the file is small (≤ 500 nodes, ≤ 5000 edges)
- Must add `.bob/kb-graph.json` to `.gitignore` (generated artifact)

---

### Sub-Task 4 — `KnowledgeGraphBuilder` (`src/graph/builder.py`)

**Status:** `[ ] pending`

**Intent**

Walk the KB filesystem, parse frontmatter and markdown links, and call
`KnowledgeGraph.add_node()` / `add_edge()` to build a complete graph. This is
the only component that touches the filesystem or the embedding index.

**Expected Outcomes**

- `KnowledgeGraphBuilder` class with:
  - `__init__(kb_path, index=None, semantic_threshold=0.3)`
  - `build() → KnowledgeGraph` — full build from scratch
  - `build_explicit(graph) → int` — parse only frontmatter + inline links,
    return edge count added
  - `build_semantic(graph, index) → int` — derive edges from embedding similarity,
    return edge count added
  - Frontmatter parsing: use `re` to extract YAML `related:` list items
    (do NOT pull in a YAML library — the format is simple enough for a regex)
  - Inline link parsing: reuse the same regex as `get_cross_references()`
  - Broken links (target file does not exist): add edge with `weight=0.0`,
    record in metadata as `broken_link_count`
  - Semantic edge derivation: for each doc pair, aggregate chunk-level cosine
    scores from `PersistentEmbeddingIndex.search()` to a per-document score
    (max of chunk scores), add edge if ≥ `semantic_threshold`
- `tests/graph/test_builder.py` covers: explicit edges from frontmatter,
  explicit edges from inline links, broken link handling, semantic edges above
  threshold, semantic edges below threshold excluded, missing index graceful

**Relevant Context**

- `KnowledgeBaseQuery.get_cross_references()` at `src/tools/kb_query.py:417` —
  reuse/reference its link regex pattern, NOT the method itself (builder works
  on the filesystem directly, without a `KnowledgeBaseQuery` instance)
- `PersistentEmbeddingIndex.search(query, top_k)` — used for semantic edges;
  pass each doc's title+content as the "query" to find its nearest neighbours
- KB category dirs: `concepts`, `guides`, `references`, `research`
- Frontmatter `related:` items look like `  - ../category/filename.md` — need
  to normalise `../category/` to `category/` (strip leading `../`)

---

### Sub-Task 5 — `GraphRanker` (`src/graph/ranker.py`)

**Status:** `[ ] pending`

**Intent**

Encapsulate the scoring logic that blends graph PageRank into search result
ranking. Keeps scoring math out of `KnowledgeBaseQuery`.

**Expected Outcomes**

- `GraphRanker` class with:
  - `__init__(graph: KnowledgeGraph)`
  - `pagerank_scores() → dict[str, float]` — calls `graph.pagerank()` with
    defaults, caches result (recompute on call if not cached)
  - `rerank(results: list[dict], weight: float) → list[dict]` — takes the
    standard `KnowledgeBaseQuery.query()` result list, adds `graph_score` field,
    blends into `score`, re-sorts
  - Score blend formula:
    ```
    blended = (1 - weight) * similarity_score + weight * pagerank_score * PAGERANK_SCALE
    ```
    where `PAGERANK_SCALE = 15.0` (matches existing `embed_score * 15.0` rescaling)
  - `neighbourhood_context(doc_id, depth=1) → list[dict]` — BFS from doc_id,
    returns list of `{doc_id, title, distance, edge_type}` for display
  - `tests/graph/test_ranker.py` covers: reranking improves hub docs, low-PR docs
    not promoted, neighbourhood returns correct depth, weight=0.0 leaves scores unchanged

**Relevant Context**

- Score blending follows the exact same pattern as `_calculate_relevance()` in
  `src/tools/kb_query.py:257-272` — `(1-w)*kw + w*embed*15.0`
- `PAGERANK_SCALE = 15.0` is intentional: keeps the three scorers on the same
  magnitude scale (`keyword` ∈ [0, 15+], `embed*15` ∈ [0, 15], `pr*15` ∈ [0, 15])
- `pagerank_scores()` must lazy-compute and cache; graph topology doesn't change
  after `build()`

---

### Sub-Task 6 — Wire into `KnowledgeBaseQuery` (`src/tools/kb_query.py`)

**Status:** `[ ] pending`

**Intent**

Add the optional `graph` / `graph_weight` parameters to `KnowledgeBaseQuery`
following the same backward-compatible injection pattern used for `embedder` and
`index`. When graph is not provided, behaviour is identical to today.

**Expected Outcomes**

- `KnowledgeBaseQuery.__init__` gains two new parameters:
  - `graph: Optional[KnowledgeGraph] = None`
  - `graph_weight: float = 0.0`
- `graph_weight` validated in [0.0, 1.0] (same guard as `embedding_weight`)
- `query()` post-processing: after computing similarity scores, if
  `self._graph is not None and self._graph_weight > 0.0`, call
  `GraphRanker(self._graph).rerank(results, self._graph_weight)`
- `KBIndexer.query()` updated to pass `graph=self._index_graph` (optional; adds
  a `graph_path` constructor param defaulting to `DEFAULT_GRAPH_PATH`)
- Lazy import of `src.graph` (same pattern as `src.cache.embeddings`)
- Three new tests in `tests/tools/test_kb_query.py`:
  - `test_graph_weight_zero_unchanged` — results identical without graph
  - `test_graph_weight_nonzero_reranks` — hub doc ranked higher
  - `test_graph_none_with_nonzero_weight_uses_similarity_only` — graceful

**Relevant Context**

- Injection pattern: `src/tools/kb_query.py:60-78` (constructor)
- Existing weight validation: `src/tools/kb_query.py:74-75`
- Lazy import pattern for embedder: `src/tools/kb_query.py:263` (`from src.cache.embeddings import ...`)
- `src/graph/` → `src/tools/` direction is NOT allowed (circular); `src/tools/` → `src/graph/` IS allowed

---

### Sub-Task 7 — CLI commands (`src/cli.py` / `src/embeddings/indexer.py`)

**Status:** `[ ] pending`

**Intent**

Expose the graph layer to users through the existing `bob-optimize` CLI. Three
commands: `graph-build` (builds and saves), `graph-query` (neighbourhood +
search), `graph-health` (orphans, hubs, stats).

**Expected Outcomes**

- `src/cli.py` gains three new subcommands under the existing `argparse` structure:
  - `bob-optimize graph-build [--kb-path PATH] [--graph-path PATH] [--semantic-threshold FLOAT]`
    — builds graph and saves to `.bob/kb-graph.json`
  - `bob-optimize graph-query <doc_id> [--depth INT] [--top-k INT]`
    — prints neighbourhood + top-k similar docs
  - `bob-optimize graph-health [--graph-path PATH]`
    — prints orphan list, top-10 hubs, node/edge counts
- Output format: `--output json` (machine-readable) or `text` (default, human-readable)
- `KBIndexer` gains optional `graph_path: Path` parameter; `KBIndexer.sync()`
  optionally rebuilds the graph after the embedding index sync
- `tests/cli/test_cli.py` gains smoke tests for all three graph commands

**Relevant Context**

- Existing CLI: `src/cli.py` — read to understand current subparser structure
- Existing `KBIndexer.sync()` at `src/embeddings/indexer.py:47`
- Output format convention: look at `src/tools/kb_query.py:512-635` (main() text output)

---

### Sub-Task 8 — Validation plan execution

**Status:** `[ ] pending`

**Intent**

Run a measured validation of the graph layer against the live 78-document KB.
Record: edge counts by type, orphan count, PageRank top-10 vs intuition,
semantic edge quality at threshold 0.3 vs 0.5, re-ranking impact on golden set
queries from ADR-014.

**Expected Outcomes**

- `docs/knowledge-base/research/graph-validation-2026-07-<DATE>.md` exists with:
  - Node count, explicit edge count, semantic edge count
  - Orphan list (docs with zero inbound explicit edges) — actionable KB health finding
  - Top-10 PageRank hubs with their inbound edge counts
  - Comparison: keyword-only p@3 vs graph-reranked p@3 on the 25-query golden set
  - Recommended `semantic_threshold` and `graph_weight` defaults
  - Memory consumption: graph JSON file size, in-memory dict size
- ADR-017 updated with validation results if defaults change
- `docs/knowledge-base/INDEX.md` updated

**Relevant Context**

- Golden set: `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md` — 25 queries with known correct docs
- Live KB: 78 documents across 4 categories
- Semantic edge quality check: if `semantic_threshold=0.3` produces > 10x as many edges
  as explicit edges, raise threshold to 0.5

---

## Validation Plan Summary

The following assertions must all be true before this feature is considered complete.

### Unit test assertions

| Layer | Test File | Key Assertions |
|---|---|---|
| `KnowledgeGraph` | `tests/graph/test_graph.py` | BFS depth 1 returns only direct neighbours; BFS depth 2 returns transitive; orphan = zero inbound; PageRank converges in < 100 iter |
| `GraphStore` | `tests/graph/test_store.py` | Roundtrip exact; missing → None; corrupt → None; atomic write (temp cleaned on failure) |
| `KnowledgeGraphBuilder` | `tests/graph/test_builder.py` | Frontmatter `related:` → explicit edge; inline link → explicit edge; broken link recorded; semantic above threshold → semantic edge; semantic below threshold excluded |
| `GraphRanker` | `tests/graph/test_ranker.py` | weight=0.0 → scores unchanged; hub doc rises with weight > 0; neighbourhood depth respected |
| `KnowledgeBaseQuery` | `tests/tools/test_kb_query.py` | graph=None → original behaviour; graph_weight=0.0 → original behaviour; graph injected + weight > 0 → reranking applied |

### Integration assertions

| Scenario | How verified |
|---|---|
| Full build on live KB completes in < 5s | `time bob-optimize graph-build` |
| Reload from `.bob/kb-graph.json` correct | `GraphStore.load()` after `graph-build` in new process |
| Orphan count < 10 on live KB | `bob-optimize graph-health` |
| p@3 with `graph_weight=0.2` ≥ baseline p@3=0.88 | Golden-set evaluation in Sub-Task 8 |
| `.bob/kb-graph.json` in `.gitignore` | `git check-ignore .bob/kb-graph.json` returns the file |

### CI gates (existing, must remain green)

- `uv run pytest` — all existing tests pass
- `python3 scripts/check_layering.py` — no `src/ → scripts/` violations
- `python3 scripts/check_coverage_by_package.py` — coverage floor maintained

---

## Open Questions (resolved before implementation begins)

1. **Semantic edge direction:** Should semantic edges be bidirectional (A↔B same score)
   or directional (A→B if A's chunks match B's content better than B's chunks match A)?
   *Recommendation: bidirectional — cosine similarity is symmetric.*

2. **Frontmatter parsing depth:** Parse only `related:` or also `tags:` to build
   tag-based implicit edges (docs sharing 3+ tags get a `tag-co-occurrence` edge)?
   *Recommendation: `related:` only for now. Tag edges add noise at 78 docs.*

3. **Chunk-level vs doc-level aggregation:** When deriving semantic edges from the
   embedding index, use `max(chunk_scores)` per document pair or `mean(chunk_scores)`?
   *Recommendation: `max` — a strong match in one section is sufficient evidence.*

4. **`get_cross_references()` replacement vs extension:** Should the graph layer
   replace `get_cross_references()` with a graph-backed version, or remain additive?
   *Recommendation: additive — `get_cross_references()` stays; `KnowledgeGraph.neighbours()`
   is the graph-backed version. Users choose.*

---

## File Inventory

### New files

| File | Purpose |
|---|---|
| `src/graph/__init__.py` | Package exports |
| `src/graph/graph.py` | `KnowledgeGraph`, `NodeProps`, `Edge` dataclasses |
| `src/graph/builder.py` | `KnowledgeGraphBuilder` |
| `src/graph/store.py` | `GraphStore` |
| `src/graph/ranker.py` | `GraphRanker` |
| `tests/graph/__init__.py` | Test package |
| `tests/graph/test_graph.py` | Graph unit tests |
| `tests/graph/test_builder.py` | Builder unit tests |
| `tests/graph/test_store.py` | Store unit tests |
| `tests/graph/test_ranker.py` | Ranker unit tests |
| `docs/adr/017-knowledge-graph-layer.md` | Design decisions |
| `docs/knowledge-base/research/graph-validation-2026-07-<DATE>.md` | Validation results |

### Modified files

| File | Change |
|---|---|
| `src/tools/kb_query.py` | Add `graph=None`, `graph_weight=0.0` parameters; wire reranker |
| `src/embeddings/indexer.py` | Add optional graph rebuild after index sync |
| `src/cli.py` | Add `graph-build`, `graph-query`, `graph-health` subcommands |
| `src/graph/__init__.py` | Export `KnowledgeGraph`, `KnowledgeGraphBuilder`, `GraphStore`, `GraphRanker` |
| `.gitignore` | Add `.bob/kb-graph.json` |
| `docs/knowledge-base/INDEX.md` | Add validation research doc |
| `docs/adr/README.md` | Add ADR-017 row |

---

*Last Updated: 2026-07-17*
*Status: Draft — pending user confirmation*
