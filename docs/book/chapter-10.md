# Chapter 10: Retrieval — Embeddings, Graph, and What It Actually Buys

> **Live document.** This chapter is part of [Mnemox — The Complete Guide](table-of-contents.md). Numbers here cite a manifest or say they do not; [`STATUS.md`](../../STATUS.md) is the single home for maturity, coverage and test counts. Chapters 1–9 were written mid-2026 — where a chapter predates a subsystem, chapters 10–12 cover it.

*Added 2026-07-25. Chapters 1–9 predate the retrieval stack entirely.*

The knowledge base only pays for itself if the right document comes back. This chapter
covers the two subsystems built for that — a persistent embedding index (P2) and a
knowledge graph (P3) — and then reports the measured result, which is more interesting
than the design.

## 10.1 The problem with keyword search over a small corpus

A keyword scorer over ~116 documents is not obviously bad. The corpus is tight and
topical: nearly every document is about caching, tokens, retrieval or governance, so the
vocabulary overlaps heavily. That property cuts both ways — it makes keyword search
surprisingly competitive, and it makes embeddings less differentiating than intuition
suggests. Hold that thought until §10.5.

## 10.2 P2 — the persistent embedding index

`src/embeddings/` turns the KB into a searchable vector index:

- **`MarkdownChunker`** splits on `##` boundaries with GFM-table awareness, so a row is
  a coherent section rather than an arbitrary window. `MAX_CHUNKS_PER_DOC`
  (`src/limits.py`) bounds what one pathological document can contribute.
- **`EmbeddingGenerator`** resolves a backend through a priority fallback chain:
  `mlx-embeddings` → `sentence-transformers` (MiniLM) → `hashing`. The last is a
  stateless `HashingVectorizer` and is the **default**, because it needs no model
  download and no optional dependency.
- **`PersistentEmbeddingIndex`** stores `[N × dim]` float32 vectors under
  `.bob/kb-index/`, split into `manifest.json` (chunk rows) and `staleness.json`
  (file-level mtime/hash sentinels) so an unchanged corpus is never re-embedded.

The index is **opt-in and off the `optimize()` path**. It is injected into
`KnowledgeBaseQuery`; when absent, the query degrades to keyword scoring. That
degradation used to be silent — the index was constructed without its embedder and
nobody noticed the fallback — which is why `src/kb_paths.py` now centralises path
resolution so a writer and a reader cannot disagree about where the index lives.

## 10.3 P3 — the knowledge graph

`src/graph/` derives a property graph over KB documents:

- **Explicit edges** from frontmatter `related:` lists and inline links.
- **Semantic edges** from cosine similarity above a threshold, computed in one batched
  pass rather than pairwise (the naïve version was O(N²) and was a denial-of-service
  surface before A2).
- **`GraphRanker`** re-ranks results by blending PageRank into the similarity score.
- **`GraphStore`** persists atomically to `.bob/kb-graph.json`.

Graph re-ranking is also opt-in, via `graph=` on `KnowledgeBaseQuery`.

## 10.4 The query path, in order

`KnowledgeBaseQuery.query()` does two things before it scores anything, and both are
easy to miss:

1. **Clamps the query** to `MAX_QUERY_CHARS`, logging when it does.
2. **Excludes quarantined and archived documents** by trust tier — and, since
   ATK-MEM-02, refuses to honour a `trust_tier: verified` claim whose provenance
   signature does not verify (Chapter 11).

Only then does it run keyword scoring, optional embedding blending at
`embedding_weight`, and optional graph re-ranking.

## 10.5 What it measures — the honest result

This is the part worth reading twice.

On the shipped default backend, over the 116-document corpus and a 25-query golden set:

| | p@3 |
|---|---|
| Wired stack (hashing embeddings + blend) | **0.84** |
| Keyword-only baseline | **0.84** |
| **Net lift** | **none** |

Manifest: `evaluation/results/retrieval-2026-07-19/report.json`.

**The retrieval stack, as shipped, does not beat keyword search on this corpus.** That
is the measured result and the project publishes it.

A separate 2026-07-16 A/B run with the optional MiniLM backend reported a **superseded**
p@3 = 0.88 against a 0.64 keyword baseline (superseded by the committed figure in
`evaluation/results/retrieval-2026-07-19/report.json`). **No manifest was committed for
that run**, so it is a lab measurement, not a published figure. Earlier drafts of this
book and several other documents quoted 0.88 as though it were the project's retrieval
quality; the
2026-07-25 audit found no artifact backing it anywhere, and every live citation now
carries that caveat.

## 10.6 Why the honest answer is kept

Three reasons the parity result is published rather than buried:

1. **It is what the corpus supports.** A tight, topically-uniform corpus is close to the
   worst case for dense retrieval's advantage. The result is a fact about this corpus,
   not a verdict on embeddings.
2. **The graph layer's default reflects it.** `graph_weight` defaults to `0.0` —
   measured no uplift, so the conservative default is off. Shipping it on would have
   been a design decision made by hope.
3. **A stack that is wired but not yet better is still worth having.** The index and
   graph are the substrate the improvements plug into; the honest baseline is what makes
   a future improvement *legible* as an improvement.

## 10.7 What would move it

Named for the reader who wants to try, not as a roadmap promise:

- A corpus with genuine vocabulary diversity, where dense retrieval has room to win.
- A committed manifest for the MiniLM configuration, so the 0.88 becomes citable.
- The deferred query-quality work: length normalisation for short concept documents,
  and a date-aware filter for date-shaped queries — the two classes the golden set shows
  the current stack failing on (ADR-018).

---

**Next:** [Chapter 11 — Trust at the Read Boundary](chapter-11.md)
