# Documentation Update Plan — P3 Knowledge Graph + MiniLM Backend

**File:** `docs/project-management/planning/documentation-update-plan.md`
**Status:** Confirmed — ready for implementation
**Design decisions confirmed:**
- Diagrams: all Mermaid (flowchart TD + sequenceDiagram), matching existing doc style
- API docs: hand-authored to match docs/api/embeddings/index.md style
- README graph section: full subsection with code example, equivalent to embedding index section
- CHANGELOG: P3 goes into [Unreleased], not a new version tag
**Scope:** All documentation and diagrams that need updating after (a) the P3 knowledge graph layer (`src/graph/`), (b) the MiniLM dual-backend fix in `src/cache/embeddings.py`, and (c) the PersistentEmbeddingIndex split (manifest.json / staleness.json) in `src/embeddings/`.

---

## Top-Level Overview

Six surfaces need updating. They fall into two groups:

**Group A — Living technical docs (require new Mermaid diagrams)**

1. `docs/architecture/ARCHITECTURE.md` — the single authoritative architecture document. Missing the entire graph package in §2 component overview, §3 runtime dataflow, and §5 components. All four existing diagrams need a companion graph-layer diagram added. New diagrams: a full-system component flowchart (adding `src/graph/`), a KB query graph-aware sequence diagram, and a Document → Chunk → Embedding → Graph pipeline flowchart.

2. `docs/api/` — auto-generated API reference. `src/graph/` (7 exported symbols across 4 modules) and `src/embeddings/chunker.py` are entirely absent. `docs/api/README.md` must be updated. Individual API doc files must be generated for `graph/builder`, `graph/graph`, `graph/ranker`, `graph/store`, and `embeddings/chunker`.

**Group B — Integration and status docs (prose + code examples)**

3. `INTEGRATIONS.md` — missing a P3 section for the graph layer. The existing P1/P2 sections set the pattern; P3 must follow it with working code examples.

4. `CHANGELOG.md` — P3 entirely absent from version history.

5. `README.md` — graph capabilities not in "What's in the box" or the CLI reference.

6. `STATUS.md` — P3 completion not explicitly noted in the roadmap field.

**Out of scope:** `docs/ARCHITECTURE.md` (covers the Bash KB Manager, not the Python system), `docs/adr/` entries (ADR-017 is complete), `docs/knowledge-base/` KB documents (already updated).

---

## Sub-Tasks

---

### Sub-Task 1: Architecture document — add graph layer to all sections and diagrams

**Intent:** Make `docs/architecture/ARCHITECTURE.md` accurate for the P3 state of the codebase. Every section that describes the component landscape must acknowledge `src/graph/`. Three new Mermaid diagrams must be published.

**Expected Outcomes:**
- §2 component overview: `src/graph/` appears in the "Not shown, deliberately separate" list alongside `src/embeddings/` (same opt-in, injection-pattern status).
- §3 runtime dataflow: A second sequenceDiagram added for the KB query path, showing `KnowledgeBaseQuery` receiving optional `index=` (P2) and `graph=` (P3) injections and the `GraphRanker.rerank()` post-processing step.
- §5 components: A new `src/graph/` bullet documenting `KnowledgeGraph`, `KnowledgeGraphBuilder`, `GraphStore`, `GraphRanker`, `DEFAULT_GRAPH_PATH`, edge types (explicit/semantic/broken), PageRank defaults (damping=0.85, tol=1e-6), and JSON persistence path (`.bob/kb-graph.json`).
- §5 components: The `src/cache/EmbeddingGenerator` entry is updated to describe the **dual-backend fallback chain**: `mlx-embeddings` → `sentence-transformers` → `hashing`.
- §5 components: The `src/embeddings/` entry mentions the `manifest.json` / `staleness.json` split (AF-1 fix).
- Three new Mermaid diagrams (see below).

**Diagrams to produce:**

*Diagram A — Full system component map (replaces/extends existing §2 flowchart)*

Add a second flowchart showing the KB subsystems (opt-in, not on optimize() path):
- `KnowledgeBaseQuery` as the central node
- Input: `embedder` (optional, P1), `index` (optional, P2), `graph` (optional, P3)
- Output: ranked results
- `KnowledgeGraphBuilder` builds graph from `KB filesystem` + `PersistentEmbeddingIndex`
- `GraphStore` persists to `.bob/kb-graph.json`
- `GraphRanker` re-ranks results

*Diagram B — Graph-aware KB query sequence diagram (new §3b)*

A sequenceDiagram with participants: `CLI`, `KnowledgeBaseQuery`, `PersistentEmbeddingIndex`, `GraphRanker`, `KnowledgeGraph`.

Steps:
1. CLI calls `kb.query(text, max_results=10)`
2. `KnowledgeBaseQuery` calls `index.search(text, top_k=40)` (P2 fast path)
3. `KnowledgeBaseQuery` scores and sorts candidate results
4. If `graph` is injected and `graph_weight > 0`: calls `GraphRanker.rerank(results, weight)`
5. `GraphRanker` fetches `pagerank_scores()` (lazy-cached)
6. `GraphRanker` blends: `final = (1-w)*similarity + w*pagerank*15.0`
7. Returns re-ranked results

*Diagram C — Document-to-graph pipeline (new §5b flowchart)*

A flowchart from raw KB documents to the persisted graph:
- `KB *.md files` → `MarkdownChunker` (##-boundary + GFM table extraction) → chunk texts with `file#slug` IDs
- Chunks → `EmbeddingGenerator` (mlx / sentence-transformers / hashing fallback) → float32 vectors
- Vectors → `FileBackedVectorStore` → `.bob/kb-index/vectors.npy` + `manifest.json` + `staleness.json`
- `KB *.md files` → frontmatter `related:` + inline `[text](path)` links → explicit edges
- `PersistentEmbeddingIndex.search()` (per-document cosine) → `max`-aggregated document scores → semantic edges (threshold=0.30)
- All edges + nodes → `KnowledgeGraph` → `GraphStore` → `.bob/kb-graph.json`

**Todo List:**
1. Read the current §2, §3, §5 of `docs/architecture/ARCHITECTURE.md` to see exact line numbers.
2. Add `src/graph/` to the "Not shown, deliberately separate" paragraph after `src/embeddings/`.
3. Add Diagram A (KB subsystem flowchart) after the existing §2 flowchart, in a new "KB subsystem" subheading.
4. Add Diagram B (graph-aware query sequence) as §3b after the existing §3 sequenceDiagram.
5. Update §5 `src/cache/` bullet to describe the dual-backend chain.
6. Update §5 `src/embeddings/` bullet to mention `manifest.json`/`staleness.json` split.
7. Add §5 `src/graph/` bullet with all four modules, edge types, PageRank defaults, persistence path.
8. Add Diagram C (Document-to-graph pipeline) inside the new §5 graph bullet.
9. Update `Last updated` date to `2026-07-17`.

**Relevant Context:**
- `docs/architecture/ARCHITECTURE.md` — current file; all existing diagrams are valid Mermaid
- `src/graph/__init__.py` — exported symbols and module docstring
- `src/graph/builder.py` — `_CATEGORIES`, `_normalise_kb_link`, `KnowledgeGraphBuilder.build()`
- `src/graph/ranker.py` — `PAGERANK_SCALE = 15.0`, `rerank()` blend formula
- `src/graph/store.py` — `DEFAULT_GRAPH_PATH = Path(".bob/kb-graph.json")`
- `src/cache/embeddings.py` — `_try_load_minilm()` dual-backend chain (mlx → st → hashing)
- `src/embeddings/store.py` — `STALENESS_FILE = "staleness.json"`
- ADR-017 Validation section — `semantic_threshold=0.30`, `graph_weight=0.0`

**Status:** [ ] pending

---

### Sub-Task 2: API reference — generate and register src/graph/ + embeddings/chunker

**Intent:** The auto-generated API reference (`docs/api/`) is missing `src/graph/` entirely (7 symbols across 4 modules) and `src/embeddings/chunker.py`. The CI `docs-freshness` gate enforces that this tree matches `src/`; it is currently failing silently because `scripts/generate_api_docs.py` must be re-run.

**Expected Outcomes:**
- New directory `docs/api/graph/` containing:
  - `builder.md` — `KnowledgeGraphBuilder` class + methods
  - `graph.md` — `KnowledgeGraph`, `NodeProps`, `Edge` classes
  - `ranker.md` — `GraphRanker` class + `PAGERANK_SCALE` constant
  - `store.md` — `GraphStore` class + `DEFAULT_GRAPH_PATH` constant
- New file `docs/api/embeddings/chunker.md` — `MarkdownChunker` class
- `docs/api/README.md` updated with:
  - New `## Graph` section listing all four graph modules
  - `chunker` entry added to `## Embeddings` section
- The `generate_api_docs.py --check` CI gate passes

**Todo List:**
1. Run `scripts/generate_api_docs.py` (or equivalent logic) to produce API docs for all four `src/graph/*.py` files and `src/embeddings/chunker.py`.
2. Since the script processes `src/` recursively by subdirectory, the simplest path is to: read each source file, extract classes/functions/constants, and write the output markdown using the same format as existing files in `docs/api/embeddings/index.md`.
3. Create `docs/api/graph/builder.md`, `docs/api/graph/graph.md`, `docs/api/graph/ranker.md`, `docs/api/graph/store.md`.
4. Create `docs/api/embeddings/chunker.md`.
5. Update `docs/api/README.md` to add `## Graph` section and the `chunker` entry.

**Relevant Context:**
- `docs/api/embeddings/index.md` — the format to replicate (module docstring, Constants, Functions, Classes)
- `src/graph/graph.py` — `KnowledgeGraph`, `NodeProps`, `Edge` dataclasses; `pagerank()`, `orphans()`, `hubs()`, `neighbours()`, `path()`
- `src/graph/builder.py` — `KnowledgeGraphBuilder`, `build()`, `build_explicit()`, `build_semantic()`; helpers `_parse_frontmatter`, `_normalise_kb_link`
- `src/graph/ranker.py` — `GraphRanker`, `pagerank_scores()`, `rerank()`, `neighbourhood_context()`; `PAGERANK_SCALE`
- `src/graph/store.py` — `GraphStore`, `save()`, `load()`, `delete()`; `DEFAULT_GRAPH_PATH`
- `src/embeddings/chunker.py` — `MarkdownChunker`, `chunk()`
- `scripts/generate_api_docs.py` — `APIDocGenerator.extract_module_info()`, `generate_module_doc()` for format reference

**Status:** [ ] pending

---

### Sub-Task 3: INTEGRATIONS.md — add P3 section (graph layer)

**Intent:** `INTEGRATIONS.md` documents how to wire each integration point (P1, P2) into `KnowledgeBaseQuery`. P3 (graph layer) is entirely absent. Callers who want multi-hop traversal, KB health checks, or PageRank re-ranking have nowhere to look.

**Expected Outcomes:**
- New `## 6. P3 — Knowledge Graph Layer (Shipped — P3 complete)` section, mirroring the style of the P2 section (§5).
- Section covers four use cases with working code examples:
  - **Graph build:** `KnowledgeGraphBuilder(kb_path, index).build()` + `GraphStore.save()`
  - **Graph-aware query:** `KnowledgeBaseQuery(..., graph=graph, graph_weight=0.3)` with note that `graph_weight=0.0` is the validated safe default (MiniLM p@3=0.88, no uplift from graph on this corpus, no regression).
  - **KB health:** `graph.orphans()`, `graph.hubs()`, `graph.pagerank()` — or `bob-optimize graph-health`
  - **Multi-hop traversal:** `graph.neighbours(doc_id, depth=2)`, `graph.path(a, b)`
- MiniLM backend usage note: `EmbeddingGenerator(backend="minilm")` now resolves via `sentence-transformers` when `mlx-embeddings` is absent.
- Warning box: `graph_weight=0.0` is the validated default; do not raise without re-running golden-set validation after any embedding model change.
- References: ADR-017, `graph-validation-2026-07-17.md`.
- Update `## References` section at bottom to add ADR-017 and graph validation doc.

**Todo List:**
1. Read current `INTEGRATIONS.md` P2 section (§5) as style template.
2. Write §6 with four subsections: Graph Build, Graph Query, KB Health, Multi-hop Traversal.
3. Write code examples for each (consistent with existing `from src.xxx import Xxx` pattern).
4. Add warning box about `graph_weight` default.
5. Add note about MiniLM dual-backend.
6. Update `## References` at bottom.

**Relevant Context:**
- `INTEGRATIONS.md` §5 — P2 pattern to replicate
- `src/graph/__init__.py` — public API surface
- `src/tools/kb_query.py` — `KnowledgeBaseQuery.__init__` signature (`graph=None`, `graph_weight=0.0`)
- `docs/adr/017-knowledge-graph-layer.md` — validated defaults
- `docs/knowledge-base/research/graph-validation-2026-07-17.md` — the authoritative live test results

**Status:** [ ] pending

---

### Sub-Task 4: CHANGELOG.md — add P3 release entry

**Intent:** The P3 knowledge-graph layer shipped with validated test results and represents a distinct, user-visible capability. It is not in the changelog. This makes version history inaccurate.

**Expected Outcomes:**
- New `## [1.0.1-tos-p3] - 2026-07-17` release section (as a patch on top of `1.0.0-tos`).
- Documents in `### Added`:
  - `src/graph/` — pure-Python property graph (`KnowledgeGraph`, `KnowledgeGraphBuilder`, `GraphStore`, `GraphRanker`)
  - Two edge types: explicit (frontmatter `related:` + inline links) and semantic (cosine ≥ 0.30 threshold)
  - PageRank-based re-ranking blended into `KnowledgeBaseQuery` via optional `graph=` / `graph_weight=` injection
  - JSON persistence at `.bob/kb-graph.json` (atomic write, gitignored)
  - CLI commands: `bob-optimize graph-build`, `graph-query`, `graph-health`
  - Live validation: 80 docs, 2 836 edges, p@3=0.88 on MiniLM (no regression, no uplift)
- Documents in `### Changed`:
  - `EmbeddingGenerator(backend="minilm")` now resolves via `sentence-transformers` as a second fallback when `mlx-embeddings` is not installed (fallback chain: mlx → sentence-transformers → hashing)
- Documents in `### Fixed`:
  - AF-1: `FileBackedVectorStore` flush/reload shape mismatch (manifest.json / staleness.json split)
  - AF-2: `is_stale()` always returning True with non-default KB paths
  - AF-4: private `_embedder` access replaced with public `embedder` property

**Todo List:**
1. Read current `CHANGELOG.md` to confirm exact placement (new section goes between `[Unreleased]` and `[1.0.0-tos]` entries).
2. Write `## [1.0.1-tos-p3] - 2026-07-17` section.
3. Write `### Added`, `### Changed`, `### Fixed` subsections.
4. Keep entries concise (one-line summaries with file references where helpful).

**Relevant Context:**
- `CHANGELOG.md` — existing format; entries are concise with parenthetical source references
- `src/graph/__init__.py` — canonical list of exported symbols
- `docs/knowledge-base/research/adversarial-audit-embeddings-chunker-2026-07-17.md` — AF-1/AF-2/AF-4 bug descriptions
- `docs/knowledge-base/research/graph-validation-2026-07-17.md` — validated metrics

**Status:** [ ] pending

---

### Sub-Task 5: README.md — surface graph capabilities

**Intent:** `README.md` is the project entry point. The graph layer is a significant, user-visible capability that is completely absent from it. Two sections need updating: the "What's in the box" capability summary and the CLI reference.

**Expected Outcomes:**
- The Token Optimization System capabilities table (§`System capabilities` or equivalent) gains a new row for the graph layer listing: multi-hop KB traversal, orphan/hub detection, PageRank re-ranking, `bob-optimize graph-build/query/health`.
- The CLI commands reference section gains three new `bob-optimize` subcommands: `graph-build`, `graph-query`, `graph-health`.
- The optional-dependencies table (MiniLM section) is updated to show `sentence-transformers` as an alternative install path alongside `mlx-embeddings`.
- `STATUS.md` system table (in README) continues to show "Beta — Not Production Ready" (no change to maturity claim; the graph layer does not change maturity).

**Todo List:**
1. Read the relevant sections of `README.md` (approximately lines 1–120 have been read; need to read the CLI table and system capabilities sections, typically around lines 120–200).
2. Find the capabilities or "What's in the box" table.
3. Add graph row.
4. Find the CLI subcommands section.
5. Add three graph subcommand entries.
6. Find the optional-dependency / MiniLM installation section.
7. Add `sentence-transformers` as alternative to `mlx-embeddings`.

**Relevant Context:**
- `README.md` — needs reading past line 120 to confirm exact section names and line numbers
- `src/cli.py` — `graph-build`, `graph-query`, `graph-health` argument parser entries
- `docs/architecture/ARCHITECTURE.md §5` — MiniLM backend description to mirror

**Status:** [ ] pending

---

### Sub-Task 6: STATUS.md — update P3 in roadmap field

**Intent:** The `STATUS.md` roadmap field currently reads: `Phases 0–8 complete + A+ gap closure … P2 integration (KB Manager ↔ TOS) …`. P3 (graph layer) is shipped and validated but the roadmap field does not mention it. Since `STATUS.md` is the canonical maturity source, it should reflect the current feature set.

**Expected Outcomes:**
- The `Roadmap` row in the status table is updated to include: `P3 (Knowledge Graph Layer): src/graph/ — property graph, PageRank re-ranking, KB health, CLI graph-build/query/health — shipped and validated (2026-07-17, ADR-017).`
- The `As of` date is updated from `2026-07-16` to `2026-07-17`.
- The maturity (`Beta — Not Production Ready`) and grade (`≈ A`) do NOT change — the graph layer does not affect the institutional audit grade.

**Todo List:**
1. Read `STATUS.md` to confirm exact field values and line numbers.
2. Update `As of` date field.
3. Update `Roadmap` field to append P3 completion note after the P2 paragraph.

**Relevant Context:**
- `STATUS.md` — current content (read above, lines 1–29)
- `scripts/check_status_consistency.py` — CI validator that must keep passing; no maturity claim changes are made

**Status:** [ ] pending

---

## Ordering and Dependencies

Sub-tasks are mostly independent but have one ordering constraint:
- **Sub-Task 1** (architecture doc) should be done first — it produces the canonical diagrams that Sub-Task 5 (README) may reference.
- **Sub-Tasks 2–6** can be done in any order after Sub-Task 1.
- **Sub-Task 2** (API reference) is the most mechanical and should be validated against the CI `docs-freshness` gate after completion.

Recommended order: 1 → 2 → 3 → 4 → 5 → 6.

---

## Design Decisions (confirmed)

1. **Diagram style**: All Mermaid, matching existing doc style — `flowchart TD` for component maps, `sequenceDiagram` for query flows.
2. **API docs**: Hand-authored to match `docs/api/embeddings/index.md` style exactly.
3. **README scope**: Full dedicated "Knowledge Graph" subsection with description, 10-line code example, and CLI commands — equivalent prominence to embedding index section.
4. **CHANGELOG**: P3 goes into `[Unreleased]`, not a new version tag.
