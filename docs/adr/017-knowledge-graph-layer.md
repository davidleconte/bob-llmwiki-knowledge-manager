# ADR-017: Knowledge Graph Layer — Design Decisions

**Status:** ✅ Accepted  
**Date:** 2026-07-17  
**Deciders:** Architecture team  
**Context:** KB Manager — P3 (graph layer over persistent embedding index)  

---

> **Update (2026-07-19, CLM-06):** The reproducible default-backend measurement
> (`HashingVectorizer`, `w=0.7`, current 116-doc golden set) is **p@3=0.84 with no net
> lift over keyword-only** (`evaluation/results/retrieval-2026-07-19/`). The p@3=0.88 figures
> in this ADR are MiniLM (`w=1.0`) lab results, not reproducible without `mlx-embeddings` /
> `sentence-transformers` installed (both optional, absent in CI/default environments).

---

## Context

The KB Manager query engine (`src/tools/kb_query.py`) can retrieve documents by
keyword or semantic similarity, but it has no awareness of the *relational
structure* between documents. The following capabilities are impossible with the
current architecture:

- "Show me everything connected to this document within 2 hops"
- "Which documents are orphaned (no inbound links)?"
- "Which documents are the most referenced hubs?"
- "Re-rank search results by how important a document is in the KB graph"

A property graph layer solves all four. Six design decisions govern how it is
implemented.

---

## Decision 1: Pure-Python Adjacency Dict vs NetworkX

**Decision:** Pure-Python `dict[str, list[Edge]]` adjacency list.

**Rationale:**

The KB has 78 documents at the time of writing. Even at the projected 500-document
ceiling, a pure-Python adjacency dict is sufficient:

| Operation | Pure-Python | NetworkX |
|---|---|---|
| Add node | O(1) | O(1) |
| Add edge | O(1) amortized | O(1) |
| BFS to depth 2 | O(V+E) | O(V+E) |
| PageRank (100 iter) | < 10ms at 500 nodes | < 10ms |
| Dependency weight | 0 bytes | ~30 MB |

NetworkX provides no functional benefit at this scale and adds a 30 MB
install-time dependency. The system adds no external dependencies for this
feature (only `dataclasses`, `collections`, `re`, `json`, `pathlib` from stdlib).

**Alternatives considered:**
- NetworkX: dropped (dependency overhead exceeds benefit at ≤ 500 nodes)
- Graph databases (Neo4j, etc.): dropped (operational overhead, no offline use)
- RDF/SPARQL (rdflib): dropped (overkill; SPARQL query language is unnecessary for traversal queries)

---

## Decision 2: File-Level Nodes (Not Chunk-Level)

**Decision:** Graph nodes represent **source files** (`category/filename.md`),
not embedding chunks (`category/filename.md#slug`).

**Rationale:**

The `PersistentEmbeddingIndex` operates at chunk granularity
(`category/file.md#slug`). The graph must operate at document granularity because:

1. Cross-references in markdown always point to files, not sections:
   `[See caching](../knowledge-base/concepts/multi-level-caching.md)` never `../concepts/caching.md#performance-targets`
2. Users reason about *documents*, not chunks, when navigating the KB
3. At 78 documents, chunk-level nodes (estimated ~400–600) would create a
   5–8× explosion in node count and edge count with no retrieval benefit

**Semantic edge derivation rule:** When computing semantic similarity between two
documents `A` and `B`, aggregate chunk-level cosine scores using `max`:

```
sim(A, B) = max { cosine(chunk_i_of_A, chunk_j_of_B) for all chunk pairs }
```

`max` is chosen over `mean` because a strong match in one section of both
documents is sufficient evidence that the documents are related. `mean` would
dilute a strong match across many weakly-related chunks.

---

## Decision 3: Two Edge Types — Explicit and Semantic

**Decision:** Two typed, weighted edges.

| Type | Source | Weight | Directionality |
|---|---|---|---|
| `explicit` | Frontmatter `related:` field | 1.0 | Directed (A cites B) |
| `explicit` | Inline markdown `[text](path)` links | 1.0 | Directed |
| `semantic` | Cosine similarity ≥ threshold | similarity score ∈ (0.3, 1.0] | Bidirectional |

**Explicit edge rationale:** These are author-stated relationships. Weight is
always 1.0 (equal authority regardless of link position). Direction is preserved
(A→B means "A references B") to enable hub detection (high inbound count = hub).

**Semantic edge rationale:** Implicit connections that no author wrote down. Two
documents covering the same concept will have high cosine similarity even without
explicit links. Default threshold of 0.3 is validated empirically in Sub-Task 8.

**Broken links:** If a `related:` entry or markdown link points to a file that
does not exist in the KB, the edge is still recorded with `weight=0.0` and
`edge_type="broken"`. This surfaces documentation health issues.

**Alternatives considered:**
- Tag-based co-occurrence edges (docs sharing 3+ tags): deferred to a later
  iteration — at 78 documents, tags are inconsistently applied and would produce
  noisy edges. Revisit when the KB has ≥ 200 consistently tagged documents.
- Temporal edges (recent docs cite older ones): not applicable to this corpus.

---

## Decision 4: Persistence Format and Location

**Decision:** Single JSON file at `.bob/kb-graph.json`.

**Storage layout:**

```json
{
  "nodes": {
    "category/filename.md": {
      "title": "Document Title",
      "category": "concepts",
      "tags": ["tag1", "tag2"],
      "date": "2026-07-13",
      "type": "concept",
      "status": "active"
    }
  },
  "edges": [
    {
      "source": "concepts/caching.md",
      "target": "guides/setup.md",
      "type": "explicit",
      "weight": 1.0,
      "label": "Setting Up Token Optimization"
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

**Rationale:**
- JSON is human-readable and diff-friendly (unlike binary formats)
- A single flat file is simpler than a directory structure for a small graph
- At 78 nodes and estimated 300–500 edges, the file is < 200 KB
- `os.replace()` atomic writes (same pattern as `FileBackedVectorStore`) prevent torn writes
- `.bob/kb-graph.json` must be added to `.gitignore` — it is a derived artifact

**Alternatives considered:**
- SQLite (`kb-graph.db`): more powerful queries but adds complexity for no benefit at this scale
- GraphML / GEXF: standard formats but not human-readable and require parsing libraries
- Separate `nodes.json` + `edges.json`: unnecessary split; single file is coherent

---

## Decision 5: PageRank Parameters

**Decision:** Iterative power method with:
- Damping factor: **0.85**
- Max iterations: **100**
- Convergence tolerance: **1e-6** (L∞ norm of per-node score delta)

**Rationale:**
- `d=0.85` is the canonical Google PageRank default, validated across decades of research
- 100 iterations is more than sufficient for convergence on a 500-node graph
  (typical convergence at < 20 iterations empirically)
- L∞ norm (max absolute delta) is the tightest convergence check — ensures every
  node's score has stabilised, not just the average

**Edge weight handling:** Semantic edges use their cosine similarity score as
the PageRank transition weight. Explicit edges use weight 1.0. Broken-link edges
(weight 0.0) are excluded from the transition matrix.

---

## Decision 6: Semantic Threshold Default

**Decision:** Default semantic edge threshold = **0.3**.

**Rationale:**

The A/B validation (ADR-014) measured `HashingVectorizer` cosine similarity
between clearly related query-document pairs at ~0.091. This reflects the
known weakness of `HashingVectorizer` for cross-vocabulary matching.

For document-to-document similarity (both sides are full documents, not a short
query), scores are higher. The 0.3 threshold is a calibration starting point:

- Below 0.1: near-random pairs; too noisy
- 0.1–0.3: weakly related; includeable but adds noise
- 0.3–0.5: moderately related; good signal-to-noise
- Above 0.5: strongly related; high confidence

**Validation requirement:** Sub-Task 8 must measure the ratio of semantic edges
to explicit edges at threshold 0.3. If the ratio exceeds 10:1 (too many weak
connections), raise threshold to 0.5. The validated threshold is recorded in
this ADR's "Validation" section below.

---

## Decision 7: Optional Injection into KnowledgeBaseQuery

**Decision:** `KnowledgeBaseQuery` gains two new optional constructor parameters:
`graph: Optional[KnowledgeGraph] = None` and `graph_weight: float = 0.0`.

**Contract:**
- `graph=None` or `graph_weight=0.0` → zero change in behaviour (fully backward-compatible)
- `graph_weight > 0.0` requires `graph is not None` (validated at construction)
- Score blend formula matches existing `embedding_weight` pattern:
  ```
  final = (1 - graph_weight) * similarity_score + graph_weight * pagerank_score * 15.0
  ```
  where `PAGERANK_SCALE = 15.0` is chosen to place PageRank scores on the same
  magnitude scale as keyword scores (range 0–15+) and rescaled embedding scores
  (cosine × 15).

**Rationale:** The optional injection pattern is already validated by ADR-014
(embedding scorer injection) and ADR-015 (persistent index injection). Reusing
the same pattern ensures API consistency and zero risk to existing callers.

---

## Consequences

### Positive

- Multi-hop traversal becomes a O(V+E) BFS — no repeated filesystem scans
- Orphan detection is O(E) — immediate KB health visibility
- PageRank provides a stable, corpus-wide importance signal independent of any single query
- Zero new runtime dependencies
- Graph is fully transparent (JSON file, human-readable)
- Backward-compatible at every callsite

### Negative

- Graph must be rebuilt when KB changes (same model as the embedding index)
- In-memory graph grows linearly with corpus: ~1 MB per 500 nodes at typical edge density
- `HashingVectorizer` semantic edges have limited quality (same limitation as ADR-014);
  semantic edges are advisory, not authoritative
- Two-process concurrent writes to `.bob/kb-graph.json` will race (same constraint as
  the embedding index; acceptable for a single-user local tool)

### Neutral

- `get_cross_references()` in `KnowledgeBaseQuery` is not replaced — both the
  graph's `neighbours()` and the original method remain available. Users choose.
- ADR-016 (no TruncationConfig) is unaffected — graph layer is independent

---

## Implementation

See `docs/project-management/planning/knowledge-graph-plan.md` for the full
sub-task breakdown and `src/graph/` for implementation.

**File inventory:**

| File | Role |
|---|---|
| `src/graph/graph.py` | `KnowledgeGraph`, `NodeProps`, `Edge` dataclasses |
| `src/graph/builder.py` | `KnowledgeGraphBuilder` — filesystem + index → graph |
| `src/graph/store.py` | `GraphStore` — atomic JSON persistence |
| `src/graph/ranker.py` | `GraphRanker` — PageRank + re-ranking |
| `.bob/kb-graph.json` | Generated artifact (add to `.gitignore`) |

---

## Validation

**Results from Sub-Task 8 live validation (2026-07-17, 80-doc corpus):**

Validated with **two embedding backends**: `HashingVectorizer` (fallback) and
`MiniLM-L6-v2` via `sentence-transformers==4.0.2` (authoritative, since
`mlx-embeddings` is not installed but `sentence-transformers` is).

| Metric | Required | Hashing | MiniLM | Status |
|---|---|---|---|---|
| `uv run pytest tests/graph/` | All pass | 182/182 pass | — | ✅ |
| Graph build on live KB | < 5s | 88 ms | ~90 ms | ✅ |
| Orphan count | Documented | 40→13 | 39→13 | ✅ |
| Semantic / explicit edge ratio | ≤ 10:1 | 17:1 ⚠️ | 16:1 ⚠️ | see note |
| p@3 (embedding only) | ≥ 0.88 baseline | 0.60 | **0.88** | ✅ (MiniLM; lab, unmanifested — superseded by report.json) |
| p@3 with `graph_weight=0.3` | ≥ baseline, no regression | 0.60 | 0.88 | ✅ (lab, unmanifested — superseded by report.json) |

> ⚠️ **On the semantic/explicit ratio:** Both backends exceed 10:1 because this
> corpus is a single-topic project (all documents are about the same Python
> system). The guideline was written for a broader-topic corpus. At threshold
> 0.50, the MiniLM ratio drops to 14.8:1 — still above the guideline — so
> raising threshold does not resolve it. The semantic edges are advisory only
> (excluded from `graph_weight=0.0` default path) and do not affect correctness.

> ⚠️ **On the `mlx-embeddings` / `sentence-transformers` gap:** `EmbeddingGenerator`
> falls back to `"hashing"` when `mlx-embeddings` is absent, even if
> `sentence-transformers` is installed. This is a known gap: see the follow-up
> action item below.

**Validated defaults (confirmed by Sub-Task 8, MiniLM authoritative run):**

| Parameter | Validated Value | Notes |
|---|---|---|
| `semantic_threshold` | **0.30** | Rescues 26/39 orphans; stable from 0.20–0.40 with MiniLM |
| `graph_weight` default | **0.0** | No p@3 uplift on MiniLM corpus (lab, unmanifested; superseded by report.json); safe conservative default |
| `graph_weight` max tested | 0.5 | No regression at any tested weight (0.1–0.5) on MiniLM |

**Follow-up action item (ADR-015 amendment):** Wire `sentence-transformers` as a
second `"minilm"` path in `EmbeddingGenerator.__init__()`, so the `"minilm"`
backend activates when either `mlx-embeddings` OR `sentence-transformers` is
installed. Currently only `mlx-embeddings` activates it; `sentence-transformers`
is a no-op despite being the same model (MiniLM-L6-v2).

**Full validation report:**
`docs/knowledge-base/research/graph-validation-2026-07-17.md`

---

## References

- ADR-014: KB query embedding scorer — optional injection pattern precedent
- ADR-015: Persistent embedding index — chunk-level vs file-level design, storage
- `src/embeddings/store.py`: atomic write pattern reference
- `src/tools/kb_query.py:60-78`: constructor injection pattern reference
- `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md`: golden-set baseline
- `docs/project-management/planning/knowledge-graph-plan.md`: full implementation plan
