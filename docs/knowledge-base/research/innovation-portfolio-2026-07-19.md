---
title: Innovation Portfolio — Mnemox / bob-llmwiki-knowledge-manager
category: research
tags: [innovation, portfolio, mece, memory-layer, mcp, watsonx, advanced-rag, roadmap]
created: 2026-07-19
updated: 2026-07-19
status: active
provenance: Independent multi-agent innovation scan (Claude Cowork), 2026-07-19; companion to counter-audit-2026-07-19-independent.md; external claims carry source URLs
---

# Innovation Portfolio for Mnemox

**Engagement type:** Innovation scan and portfolio design — opportunity identification, scoring, concept briefs, sequencing, validation plans
**Methodology:** McKinsey MECE opportunity-space decomposition; three-horizons portfolio (70% near-term / 30% frontier per client direction); impact × differentiation × feasibility × strategic-fit scoring; three independent evidence streams (state-of-the-art research, competitive/ecosystem intelligence, codebase feasibility anchoring)
**Strategic parameters (client-set):** Hybrid MCP posture (native Bob core preserved; optional MCP extension surface permitted) · Balanced ambition · watsonx-ecosystem integration as a first-class opportunity space
**Companion document:** `counter-audit-2026-07-19-independent.md` — several innovations are explicitly gated on its Horizon-1 remediations

---

## 1. Executive Summary

### 1.1 Governing thought

The 2025–2026 evolution of the field has **validated Mnemox's architectural bets** — files-as-memory received first-party endorsement (Anthropic's memory tool and Agent Skills, the AGENTS.md standard), and graph-plus-PageRank retrieval received academic validation (HippoRAG 2, ICML 2025). Meanwhile, **no major vendor ships what Mnemox is structurally positioned to offer**: git-native, review-gated, provenance-disciplined, retrievable team memory. Every competitor forces a choice between auto-captured memory that is per-user and unauditable (Claude Code MEMORY.md, Cursor Memories, Windsurf local files) and shared rules that are static and lifeless (Copilot instructions, Amazon Q rules). The innovation portfolio therefore does not need to change Mnemox's direction; it needs to **finish the loop the field has now mapped** — reconciliation at write time, consolidation between sessions, learning from failure, trust tiers against poisoning — and **distribute the result everywhere** through an optional MCP surface and the watsonx ecosystem.

### 1.2 Situation — Complication — Question — Answer

**Situation.** Mnemox holds differentiated assets: a schema-disciplined 110-document KB, a validation harness with retraction discipline that is rare in the industry, a pure-Python knowledge graph, dual embedding backends, a delegation pipeline, and a deep CI. The counter-audit established that several of these assets are built but unwired.

**Complication.** The field is moving fast around four capabilities Mnemox lacks — failure-derived memory (Google ReasoningBank), write-time conflict reconciliation (Mem0's ADD/UPDATE/DELETE/NOOP), temporal supersession (Zep/Graphiti), and memory-poisoning defense (OWASP ASI06, MINJA >95% attack success) — while enterprise buying criteria consolidate around exactly the properties git provides: audit trails, review gates, rollback, residency. Separately, ETH Zurich's AGENTbench showed naive context files can *reduce* agent success by 3% while raising cost 20%+: unvalidated memory is now a documented liability, which makes Mnemox's measurement discipline a marketable moat rather than an internal virtue.

**Question.** Which innovations add the most value, in what order, and how should each be validated?

**Answer.** A 24-candidate portfolio organized into six MECE opportunity spaces, sequenced in three horizons: **H1 (weeks)** — ship the MCP server surface, the compact cold-start index, the Docling ingestion bridge, the retrieval-excellence pack, and the trust/quarantine tier, all of which are S/M-effort extensions of existing assets; **H2 (1–3 months)** — the memory-lifecycle intelligence layer (sleep-time consolidation, write-time reconciliation, temporal supersession, pitfalls memory, golden-set CI); **H3 (frontier)** — self-improving retrieval, lakehouse KB analytics, enterprise vector backends, Orchestrate publication, and standards-track portable memory. Three counter-audit remediations (retrieval wiring, index deletion lifecycle, review-gated writes) are hard prerequisites and are treated as such throughout.

### 1.3 The five headline opportunities

1. **Mnemox MCP Server** — expose `kb_search`, `get_note`, `traverse_graph`, `propose_memory` (write-gated) as an MCP server. S-effort: every capability is already a JSON-emitting function behind one facade, and the team already operates MCP servers (`.bob/mcp.json`). It makes the KB consumable by Claude Code, Cursor, and every MCP client — the git repo itself becomes the cross-assistant memory broker that OpenMemory-class products simulate with a SaaS vector store — and it can ship semantic retrieval on day one, quietly closing the audit's flagship wiring gap in the new surface.
2. **Compact Cold-Start Index ("3k-token boot")** — the audit measured a ~12–13k-token fixed cold-start. Per-document ≤200-character descriptions *already exist* in `kb-graph.json`; generating a compact, llms.txt-grammar index from them is nearly free, with RAPTOR-style lazy cluster summaries as tier two. Directly monetizable in Bobcoin terms and provable by the existing validation harness.
3. **Docling Ingestion Bridge ("documents in, governed knowledge out")** — five working Docling scripts already sit in `.bob/skills/ibm-docling/scripts/`; wiring them to the KB templates, frontmatter tooling, and near-duplicate check turns a markdown-only KB into a document-ingesting one. The strongest capability-per-line-of-new-code jump available, and maximally IBM-native: OpenRAG stops at retrieval — nobody ships document→curated-governed-note with page-level provenance.
4. **Memory-Lifecycle Intelligence ("the Gardener")** — a sleep-time consolidation agent implementing Karpathy's lint operation: Mem0-style ADD/UPDATE/DELETE/NOOP reconciliation at write time, near-duplicate merging (the all-pairs `doc_sim` map is computed today and discarded), episodic→semantic distillation of the 65-document research tier, temporal supersession frontmatter, and salience decay. This is the part of the LLM-wiki pattern that separates compounding wikis from rotting ones, and the field's consensus gap.
5. **Trust-Tiered Memory ("the only memory layer whose write path is a security control")** — provenance frontmatter, a `quarantined` status excluded from retrieval promotion, poisoning null-tests in the validation harness, and PR-reviewed memory writes. Memory poisoning is OWASP ASI06 with demonstrated >95% injection success in academic attacks; no shipping coding-assistant memory carries provenance or write validation. For IBM's FedRAMP/HIPAA/PCI-positioned Bob, this is the default-win enterprise claim.

### 1.4 Portfolio at a glance

| Horizon | Candidates | Effort envelope | Theme |
|---|---|---|---|
| H1 — Ship on existing assets (weeks) | 9 | S–M each | Distribution, cold-start economics, ingestion, retrieval quality, trust floor |
| H2 — Lifecycle intelligence (1–3 months) | 8 | M–L each | Consolidation, reconciliation, temporal knowledge, failure memory, evaluation |
| H3 — Frontier bets (3–6+ months) | 7 | L–XL each | Self-improving retrieval, lakehouse analytics, enterprise backends, standards, federation |

---

## 2. Methodology and Evidence Base

Three independent streams were executed in parallel: (1) a state-of-the-art research sweep across agent-memory systems (Letta/MemGPT, Mem0, Zep/Graphiti, LangMem, A-Mem, HippoRAG 1/2, MemoryBank, ReasoningBank, Memp), advanced RAG patterns (GraphRAG/LazyGraphRAG, RAPTOR, Self-RAG/CRAG, contextual retrieval, hybrid fusion), and token-economics practice; (2) a competitive and ecosystem scan covering the memory features of every major coding assistant, the MCP memory-server landscape, the AGENTS.md/llms.txt standardization picture, and the watsonx integration surfaces (watsonx.data/Milvus, OpenSearch+JVector, Docling, OpenRAG, Granite, Orchestrate); (3) a codebase feasibility pass mapping twelve candidate directions to existing modules, with effort classes and hidden enablers/blockers identified at file level. All external claims carry source URLs (Appendix B); all feasibility claims carry repository paths. Candidates were scored 1–5 on four criteria — client value, competitive differentiation, feasibility (asset leverage), and strategic fit with the chosen posture — and assembled into a MECE portfolio by value-creation mechanism.

**MECE opportunity-space decomposition** (by mechanism, so no candidate belongs to two spaces):

| Space | Mechanism | Question it answers |
|---|---|---|
| OS-1 Retrieval & context excellence | Improve the read path | Does the right knowledge reach the model at minimal token cost? |
| OS-2 Memory-lifecycle intelligence | Improve the store itself over time | Does the KB get better, not just bigger? |
| OS-3 Learning from experience | Acquire new classes of knowledge | Does the system learn from what happened, including failure? |
| OS-4 Trust & memory safety | Protect the write path | Can the team trust what memory says? |
| OS-5 Reach & interoperability | Distribute the capability | Can every assistant and standard consume it? |
| OS-6 Enterprise scale & watsonx ecosystem | Scale and monetize in IBM's stack | Does it win enterprise deals and challenge juries? |

---

## 3. Strategic Context: Where the Field Landed, Where Mnemox Stands

### 3.1 Convergent validation

Three of Mnemox's foundational choices are now industry- or academically-endorsed. Plain files as memory: Anthropic ships a file-based memory tool and folder-based Agent Skills with progressive disclosure; AGENTS.md became the de facto cross-vendor standard. Graph-augmented retrieval: HippoRAG 2 (ICML 2025) demonstrates that Personalized PageRank over a knowledge graph is a state-of-the-art memory substrate — direct validation of Mnemox's graph layer, with a specific upgrade path (query-seeded PPR instead of global PageRank). Curated-KB-over-RAG: the "Claude Code doesn't index" debate resolved toward hybrid — semantic index for discovery, agentic reading for precision — which is precisely the cost-curve position a curated wiki occupies.

### 3.2 The competitive white space

The cross-vendor pattern is a two-quadrant trap: git-versioned static rules (shareable, no lifecycle, no retrieval) versus SaaS/local auto-memories (lifecycle, but unshareable, unauditable, locked-in). Windsurf's own documentation tells users to move durable knowledge out of its memories into version control. Devin's approval-gated Knowledge is the only governance gesture among major vendors, and it is SaaS-resident. Nobody offers: memory rollback ("when did the agent learn the wrong thing?" — git bisect gives it for free), PR-reviewable memory diffs, poisoning-hardened write paths, or knowledge-utilization analytics. Standardization of portable agent memory is embryonic (a Merkle-DAG proposal on arXiv, May 2026; a W3C community group proposed 2026-05-18 and not yet launched) — git+markdown+frontmatter is arguably the most portable memory format shipping today, and Mnemox can claim the standards-track early-mover position with an exporter.

### 3.3 The gaps that matter

Against the research frontier, Mnemox lacks four capabilities, all cheap in a git/markdown substrate: failure-derived memory (ReasoningBank's pitfall distillation — the highest-leverage neglected memory class), write-time reconciliation (Mem0's four-operation merge loop), temporal supersession (Graphiti's bi-temporal invalidation — git already provides the transaction-time axis), and poisoning defense (trust tiers + provenance + quarantine). One empirical result reframes the whole product: ETH Zurich's AGENTbench found LLM-generated context files reduced agent success 3% and raised cost 20%+ — *unvalidated memory is a liability*. Mnemox's manifest-backed validation harness is thus not compliance overhead; it is the differentiator that makes "validated context" a product claim no competitor can currently make.

---

## 4. The Opportunity Spaces and Their Candidates

Each candidate: value / differentiation / feasibility / fit scored 1–5; effort S/M/L/XL; key leverage assets by path. Full register in Appendix A.

### OS-1 — Retrieval & context excellence

**C1. Retrieval-Excellence Pack** (V5 D3 F4 fit5 · effort M). Three compounding upgrades to the (post-audit-wiring) query path: (a) **query-seeded Personalized PageRank** — bias the graph walk from entities matched in the query (HippoRAG 2's load-bearing idea) instead of global PageRank; (b) **three-signal RRF fusion** — BM25-over-markdown + MiniLM dense + graph-PPR fused by reciprocal rank fusion, three cheap pure-Python channels approximating a rerank stack without a cross-encoder; (c) **metadata-contextualized chunk embedding** — prepend title/category/parent-concept/date to each chunk before embedding (Anthropic's contextual-retrieval result, up to 67% retrieval-failure reduction, achievable here with zero LLM calls because the situating metadata already exists as frontmatter). Leverage: `src/graph/ranker.py`, `src/embeddings/chunker.py`, `src/tools/kb_query.py`.
**C2. Compact Cold-Start Index** (V5 D4 F5 fit5 · S–M). See concept brief §5.2.
**C3. Retrieval-confidence gate (CRAG-style)** (V4 D3 F3 fit4 · M). Score retrieved chunks; below threshold, fall back to agentic grep over raw sources and **log the miss as a KB gap** for the maintainer loop — converting retrieval failures into a work queue.
**C4. Cache-aligned context assembly** (V4 D3 F4 fit4 · S). Deterministic, stable ordering of assembled context (schema → index → hot pages → volatile turn data) so the team shares one cached KB prefix; cache-read pricing is ~10% of base input price, making a team-shared prefix a direct Bobcoin multiplier. Measure hit rate as a KPI.

### OS-2 — Memory-lifecycle intelligence

**C5. Sleep-Time Consolidation Agent ("Gardener")** (V5 D5 F3 fit5 · M–L). See concept brief §5.4.
**C6. Write-time reconciliation (ADD/UPDATE/DELETE/NOOP)** (V5 D4 F3 fit5 · M). Before filing a new document, retrieve nearest existing claims (the embedding index) and emit a merge decision as a git diff instead of appending near-duplicates — Mem0's state machine, applied to markdown. Gated on: index deletion lifecycle (audit R8).
**C7. Temporal supersession** (V4 D4 F4 fit5 · M). `observed_at`/`superseded_by` frontmatter; `supersedes` typed edges (the graph's free-form `edge_type` accepts them today); lint treats contradiction as supersession, keeping history queryable — Graphiti's bi-temporal model, git-native.
**C8. RAPTOR-style lazy cluster summaries** (V3 D3 F4 fit4 · M). Detect KB regions with no concept page (clusters in the semantic graph lacking a summarizing node — "missing abstraction detection") and generate summary pages lazily on first need, cached as KB pages (LazyGraphRAG's cost lesson: don't pre-summarize).
**C9. Salience & decay scoring** (V3 D3 F3 fit4 · M). Access-count and last-retrieved tracking per page feeding an Ebbinghaus-style decay score; rarely-retrieved stale pages are flagged for archive/merge; frequently-retrieved pages become promotion candidates toward AGENTS.md. Depends on C13 logging.

### OS-3 — Learning from experience

**C10. Pitfalls memory (failure distillation)** (V5 D5 F3 fit5 · M). A `pitfalls/` page type distilled from failed runs — one insight per page ("verify X before Y"), injected for matching task types. ReasoningBank showed +8.3% WebArena / +4.6% SWE-Bench-Verified and ~3 fewer steps per task from exactly this memory class; it is the most neglected, highest-leverage knowledge type for a team assistant.
**C11. Procedural memory with execution counters** (V4 D4 F4 fit4 · M). Guides carry success/failure counters; a failed execution triggers a *revision pass on the existing page* rather than a new page (Memp's lifecycle); recurring how-to guides get promoted into `.bob/skills/` with skill-style "when to load me" frontmatter — closing the declarative→procedural loop on the existing 26-guide corpus and 30-skill layer.
**C12. Trajectory distillation v1** (V4 D4 F3 fit4 · M). Upgrade `scripts/mnemox-lessons.sh` (git-log → templated note — v0 exists with a designed in-session LLM slot) into a session-end pipeline producing *candidate* pages that enter quarantine (C15) pending review; compaction events near context limits also write episodic pages instead of throwaway scratch files.
**C13. Retrieval feedback logging** (V4 D4 F4 fit5 · S–M). Append-only log of (query, pages served, score components, task outcome). The query JSON already carries per-result score breakdowns, so the log format is nearly free; it is the substrate for C9 salience, C14 golden-set expansion, and H3 self-improving retrieval.
**C14. Golden retrieval set in CI** (V4 D3 F4 fit5 · M). Versioned query→expected-page pairs per KB category, recall@k asserted by the existing validation harness on every KB commit — this also repairs the audit's CLM-06 (p@3 without committed provenance) and operationalizes the "validated context" claim.

### OS-4 — Trust & memory safety

**C15. Trust-tiered memory & quarantine** (V5 D5 F4 fit5 · M). See concept brief §5.5.
**C16. Poisoning red-team suite** (V3 D4 F3 fit4 · M). Extend `evaluation/scripts/redteam_scenarios.py` + `evaluation/data/redteam/` into memory-poisoning null-tests: planted quarantined content must never surface in top-k or be promoted to AGENTS.md; MINJA-style injection scenarios asserted red in CI.
**C17. Memory rollback & time-travel UX** (V3 D4 F4 fit4 · S). Productize what git already gives: `mnemox bisect` ("when did the agent learn the wrong thing?"), point-in-time KB checkout for reproducing past agent behavior, signed commits for attributable writes. Zero competitors offer deterministic memory rollback; this is packaging, not research.

### OS-5 — Reach & interoperability

**C18. Mnemox MCP Server** (V5 D5 F5 fit5 · S). See concept brief §5.1.
**C19. llms.txt-grammar index** (V3 D3 F5 fit4 · S). Emit the compact index in llms.txt grammar (H2 sections, link + one-line description) so external tools consume the KB entry point natively; adoption evidence says coding agents are the one audience that genuinely fetches these files.
**C20. Standards-track portable memory exporter** (V3 D4 F3 fit3 · M). An exporter to the Portable-Agent-Memory shape (content-addressed entries, provenance DAG — near-isomorphic to git's object model) plus engagement with the proposed W3C AI Agent Memory Interop group: an early-mover, thought-leadership play with modest engineering.

### OS-6 — Enterprise scale & watsonx ecosystem

**C21. Docling Ingestion Bridge** (V5 D4 F5 fit5 · S–M). See concept brief §5.3.
**C22. Pluggable enterprise vector backend** (V4 D4 F3 fit5 · M–L). A `VectorIndexProtocol` extracted from `PersistentEmbeddingIndex` (search/index/delete/rebuild/is_stale) with Milvus (watsonx.data vector service) and OpenSearch+JVector implementations — "laptop-scale sidecar, certified scale-out path" (DataStax proved 1B vectors on OpenSearch+JVector; IBM is an OpenSearch Foundation Premier Member). Critical design note: define per-document *deletion* in the Protocol now, or every backend inherits the audit's lifecycle gap (CODE-04).
**C23. KB analytics in the lakehouse** (V4 D5 F3 fit5 · L). Sync KB git history, graph edges, and retrieval telemetry (C13) into Iceberg tables; Presto SQL over "which knowledge is used/stale/contradicted"; token-savings time series as ROI reporting. No memory vendor exposes knowledge-utilization analytics; a natural watsonx.data Premium story that the client is uniquely positioned to build and demo.
**C24. Orchestrate Agent Catalog publication + cost observability** (V3 D4 F3 fit4 · M). Publish the MCP surface into watsonx Orchestrate's Agent Catalog so non-coding enterprise agents (support, compliance) read the engineering KB; emit per-query telemetry in OpenTelemetry GenAI semantic conventions so cost-per-answer-declining-as-KB-grows becomes a measurable curve. Granite small models via watsonx.ai serve the sidecar's cheap LLM steps (consolidation summaries, reconciliation judgments) for air-gapped/regulated deployments.

---

## 5. Concept Briefs — Top Five

### 5.1 Mnemox MCP Server (C18 · H1 · effort S)

**Problem.** The KB's value is trapped inside Bob's mode system; meanwhile OpenMemory-class products prove demand for one memory shared across Claude Code/Cursor/Copilot, but broker it through an unauditable local vector store.
**Concept.** A FastMCP Python server (~200 lines) exposing tools `search_kb` (hybrid semantic — index+graph injected in-process, shipping the validated retrieval configuration on day one), `get_note`, `traverse_graph`, `kb_status` (health), and `propose_memory` (write-gated: proposals land in quarantine, never direct commits); resources = notes at stable URIs + the schema manifest. The git repo itself is the broker — read natively by Bob, via MCP by everything else. Enterprise auth arrives via MCP's 2026 extension mechanisms.
**Leverage.** `src/facade.py` one-line init; every CLI command already JSON-clean (`src/cli.py` `_emit`); `.bob/mcp.json` proves operational MCP experience, including a fully-specced dormant server config to crib. The repo's own `mcp-builder` skill applies.
**Risks.** Config singleton assumes cwd-relative paths (serve from repo root); write path must be quarantine-only to preserve the trust story.
**Validation.** Golden-set recall@k parity between native path and MCP path; latency budget (<100 ms local); a demo of Cursor + Claude Code + Bob all answering from the same KB commit.

### 5.2 Compact Cold-Start Index — "3k-token boot" (C2 · H1 · effort S–M)

**Problem.** The audit measured ~12–13k tokens of fixed cold-start load (AGENTS.md + a double-listing, never-pruned index) — the system built to save tokens spends five figures per session on its own map.
**Concept.** Tier 1: auto-generate `index-compact.md` from `kb-graph.json`, which already contains title, category, and a ≤200-character description for every document — one line per doc, llms.txt grammar (C19), Recent Additions capped, target <3k tokens; `.bob/settings.json` auto-loads the compact index instead. Tier 2: RAPTOR-style lazy cluster summaries for regions without a concept page. Combined with cache-aligned assembly (C4), the whole team shares one cached prefix.
**Leverage.** `NodeProps.description` + `_extract_description` (`src/graph/builder.py:367`) — the summaries are already extracted; generation is a read of the existing graph JSON.
**Risks.** The optimizer must stay out of this path until audit R3 lands (structure-flattening bug); description quality varies — spot-fix via the Gardener (C5).
**Validation.** Before/after cold-start token count measured by the existing validation harness with a manifest; retrieval-success delta on the golden set (compact index must not hurt task success — the ETH Zurich failure mode).

### 5.3 Docling Ingestion Bridge — "documents in, governed knowledge out" (C21 · H1 · effort S–M)

**Problem.** The KB is markdown-only; enterprise knowledge lives in PDF architecture docs, DOCX runbooks, PPTX decks. OpenRAG ingests documents into *search indexes*; nobody ships document → curated, schema-validated, provenance-carrying memory note.
**Concept.** Wire the five working Docling scripts already in `.bob/skills/ibm-docling/scripts/` (`docling_convert/chunk/batch/analyze/evaluate.py`) into a `bob-optimize ingest <file>` pipeline: Docling parse → knowledge-manager template mapping → frontmatter with source provenance (file hash, page refs, `provenance: untrusted` until reviewed — C15) → near-duplicate check via `index.search` → quarantined candidate page. Positioning: OpenRAG retrieves raw documents at scale; Mnemox stores the *vetted conclusions* with provenance links back — complementary, not competitive, with IBM's own stack.
**Leverage.** The most under-recognized asset in the repo: ingestion is ~70% built, sitting in the skills layer.
**Risks.** Auto-generated cross-links need quality gating; table-heavy documents need the chunker's table extraction path exercised.
**Validation.** Ingest a real architecture PDF corpus; measure retrieval precision on questions answerable only from ingested content; assert every ingested page carries complete provenance frontmatter.

### 5.4 The Gardener — sleep-time consolidation (C5+C6+C7 · H2 · effort M–L)

**Problem.** 65 of 110 KB documents are episodic research snapshots; near-duplicate concepts exist; semantic edge density (~39/node) is drifting toward noise; the audit showed the maintenance ritual cannot detect the corruption it accumulates. The LLM-wiki pattern lives or dies on the lint operation — the part implementations most often skip.
**Concept.** A scheduled offline agent (Letta's sleep-time compute, Karpathy's lint) running between sessions: (a) near-duplicate detection from the `doc_sim` all-pairs map that `build_semantic` computes today and throws away (`src/graph/builder.py:235`); (b) Mem0-style ADD/UPDATE/DELETE/NOOP reconciliation producing git diffs, not appends; (c) episodic→semantic distillation: research-tier pages older than N days summarized into concept pages, originals archived with `superseded_by`; (d) temporal supersession edges; (e) A-Mem-style neighborhood evolution — on ingest, re-open k-nearest pages and refresh their summaries/cross-links; (f) orphan/hub/edge-density health as regression metrics. All output lands as a reviewable branch (never auto-commit — audit R10), with LLM steps served by Granite via watsonx.ai or the dormant `external-llm` delegation server spec in `.bob/mcp.json`.
**Leverage.** Delegation coordinator (parallel waves, retry), `graph.orphans/hubs`, `mnemox.sh` as the scheduling hook, knowledge-manager templates as distillation targets.
**Prerequisites.** Audit R8 (index deletion lifecycle) — pruned docs must not leave stale vectors; R10 (review gate).
**Validation.** KB health scorecard before/after (doc count by tier, edges/node, duplicate pairs above 0.6 cosine, cold-start tokens); retrieval golden set must not regress; human review acceptance rate of Gardener proposals tracked as the quality KPI.

### 5.5 Trust-Tiered Memory (C15+C16+C17 · H1 floor, H2 full · effort M)

**Problem.** Memory poisoning is OWASP ASI06; academic attacks reach >95% injection success; a single poisoned write persists indefinitely because memory is trusted once written. No shipping coding-assistant memory carries provenance, trust scoring, or write validation. Mnemox's auto-commit (audit MEM-09) is currently the biggest liability of its strongest asset.
**Concept.** Three git-native controls: (a) **provenance frontmatter** on every write — `source:` human/agent/pipeline + session id, `provenance: trusted|untrusted` for externally-sourced content (the delegation pipeline already writes `generated_by`/`task_id` — extend, don't invent); (b) **quarantine tier** — `status: quarantined` filtered/downranked in `kb_query`, excluded from AGENTS.md promotion, cleared only by review (≈3 small changes; every field already parsed end-to-end); (c) **review-gated writes** — agent proposals land as branch diffs (PR-reviewed memory, the write-ahead-validation defense from the poisoning literature, on infrastructure enterprises already trust) — plus the rollback/time-travel packaging (C17). Sales line for regulated accounts: *memory that never leaves your git remote, every write attributable, every state restorable.*
**Leverage.** `safe_paths.resolve_within`, pipeline provenance pattern, `NodeProps.status` parsing, red-team seed in `evaluation/`.
**Validation.** Poisoning null-tests in CI (planted quarantined content never in top-k, never promoted); provenance-completeness gate in `validate-kb.sh`'s (repaired) successor; audit-trail demo: `git log --follow` on a memory page as the compliance artifact.

---

## 6. Sequencing, Dependencies, and the 70/30 Portfolio

### 6.1 Hard prerequisites from the counter-audit

Three remediations gate the portfolio and are not innovation work: **R2 wiring** (index+graph into production retrieval — without it, C1/C18 ship keyword-only), **R8 index deletion lifecycle** (without it, C5/C6/C21 accumulate stale vectors), **R10 review gate** (without it, C12/C15's trust story is hollow and C5's Gardener is a poisoning amplifier). Recommended: execute audit H1 first (≈1 sprint), then this portfolio's H1 — several items (C18's in-process wiring, C15's quarantine) actively *complete* audit remediations rather than compete with them.

### 6.2 Three horizons (70% H1+H2, 30% H3)

| Horizon | Contents | Exit criteria |
|---|---|---|
| **H1 (weeks)** | C18 MCP server · C2 compact index · C21 Docling bridge · C1 retrieval pack · C15 trust floor (provenance + quarantine) · C4 cache alignment · C13 retrieval logging · C19 llms.txt grammar · C17 rollback packaging | MCP demo across 3 assistants; cold start <3k tokens (manifest-backed); one PDF corpus ingested with provenance; golden-set recall improvement over keyword baseline published with manifest |
| **H2 (1–3 months)** | C5 Gardener · C6 reconciliation · C7 temporal supersession · C10 pitfalls memory · C11 procedural counters · C12 trajectory distillation · C14 golden-set CI · C16 red-team suite | Zero duplicate pairs >0.6 cosine; research tier ≤40% of corpus; pitfalls pages measurably reduce repeated failures on tracked tasks; poisoning tests red-teamed in CI |
| **H3 (3–6+ months)** | C22 enterprise vector backends · C23 lakehouse analytics · C24 Orchestrate + OTel · C20 standards exporter · C9 salience/decay · C3 confidence gate · multi-repo federation (from feasibility direction 7) | One org-scale deployment on Milvus or OpenSearch+JVector; knowledge-utilization dashboard live on Iceberg/Presto; cost-per-answer curve published; federation across ≥2 repos with namespaced doc_ids |

### 6.3 Strategic narrative for the watsonx Challenge

The portfolio composes into one sentence a jury can hold: *"Mnemox is the governed memory layer for the agentic enterprise — it turns every Bob session into auditable, compounding team knowledge (git-native, poisoning-hardened, measurably validated), ingests the documents IBM's own Docling parses, scales on the vector engines IBM backs (Milvus, OpenSearch+JVector), reports its ROI in the lakehouse IBM sells (watsonx.data), and serves that knowledge to every agent IBM orchestrates (Orchestrate, via MCP)."* Each clause is a shipped or scheduled feature, each number manifest-backed — the honesty machinery the counter-audit verified becomes the proof mechanism for the innovation claims.

---

## 7. Measurement and Validation Plan

Every innovation inherits the repository's own discipline: no number without a manifest. Program-level metrics, tracked as CI regression series: **cold-start tokens** (target <3,000; today ~12–13k); **retrieval precision** recall@k / p@3 on a *committed* golden set (repairing CLM-06); **KB health** — duplicate pairs >0.6 cosine, edges/node, orphan count, research-tier share, stale-doc count; **trust** — provenance-completeness %, quarantine leak count (must be zero, asserted by null-tests), review acceptance rate of agent proposals; **economics** — cache hit rate on the shared prefix, tokens saved vs baseline route per query (C13 log), cost-per-answer trend as the KB grows — the compounding claim, finally rendered as a measurable curve; **adoption** — MCP client count, foreign-repo deployments, ingested-document count. The ETH Zurich result is the standing caution: any feature that adds context must demonstrate non-negative task-success delta on the golden set before default-on.

---

## Appendix A — Scored Candidate Register

| ID | Candidate | Space | V | D | F | Fit | Effort | Horizon | Gated by |
|---|---|---|---|---|---|---|---|---|---|
| C18 | MCP server surface | OS-5 | 5 | 5 | 5 | 5 | S | H1 | R2 (for semantic parity) |
| C2 | Compact cold-start index | OS-1 | 5 | 4 | 5 | 5 | S–M | H1 | R3 (optimizer out of path) |
| C21 | Docling ingestion bridge | OS-6 | 5 | 4 | 5 | 5 | S–M | H1 | R8, C15 floor |
| C1 | Retrieval-excellence pack (PPR/RRF/contextual) | OS-1 | 5 | 3 | 4 | 5 | M | H1 | R2 |
| C15 | Trust tiers + quarantine + provenance | OS-4 | 5 | 5 | 4 | 5 | M | H1 | — |
| C4 | Cache-aligned context assembly | OS-1 | 4 | 3 | 4 | 4 | S | H1 | — |
| C13 | Retrieval feedback logging | OS-3 | 4 | 4 | 4 | 5 | S–M | H1 | — |
| C19 | llms.txt-grammar index | OS-5 | 3 | 3 | 5 | 4 | S | H1 | C2 |
| C17 | Rollback & time-travel packaging | OS-4 | 3 | 4 | 4 | 4 | S | H1 | — |
| C5 | Sleep-time consolidation (Gardener) | OS-2 | 5 | 5 | 3 | 5 | M–L | H2 | R8, R10 |
| C6 | Write-time reconciliation | OS-2 | 5 | 4 | 3 | 5 | M | H2 | R8 |
| C7 | Temporal supersession | OS-2 | 4 | 4 | 4 | 5 | M | H2 | C15 provenance |
| C10 | Pitfalls memory (failure distillation) | OS-3 | 5 | 5 | 3 | 5 | M | H2 | C12 or manual capture |
| C11 | Procedural memory + counters | OS-3 | 4 | 4 | 4 | 4 | M | H2 | C13 |
| C12 | Trajectory distillation v1 | OS-3 | 4 | 4 | 3 | 4 | M | H2 | R10, C15 |
| C14 | Golden retrieval set in CI | OS-3 | 4 | 3 | 4 | 5 | M | H2 | — |
| C16 | Poisoning red-team suite | OS-4 | 3 | 4 | 3 | 4 | M | H2 | C15 |
| C8 | Lazy cluster summaries | OS-2 | 3 | 3 | 4 | 4 | M | H2/H3 | C5 |
| C9 | Salience & decay scoring | OS-2 | 3 | 3 | 3 | 4 | M | H3 | C13 |
| C3 | Retrieval-confidence gate | OS-1 | 4 | 3 | 3 | 4 | M | H3 | C14 |
| C22 | Enterprise vector backends (Milvus/JVector) | OS-6 | 4 | 4 | 3 | 5 | M–L | H3 | R8 (delete in Protocol) |
| C23 | Lakehouse KB analytics (Iceberg/Presto) | OS-6 | 4 | 5 | 3 | 5 | L | H3 | C13 |
| C24 | Orchestrate publication + OTel cost observability | OS-6 | 3 | 4 | 3 | 4 | M | H3 | C18 |
| C20 | Portable-memory standards exporter | OS-5 | 3 | 4 | 3 | 3 | M | H3 | — |

## Appendix B — Key Sources (abridged; full URLs in evidence streams)

Agent memory: Letta sleep-time compute (letta.com/blog/sleep-time-compute, 2025-04-21); Mem0 (arXiv:2504.19413); Zep/Graphiti temporal KG (arXiv:2501.13956); A-Mem (arXiv:2502.12110, NeurIPS 2025); HippoRAG 2 (arXiv:2502.14802, ICML 2025); MemoryBank (arXiv:2305.10250, AAAI 2024); ReasoningBank (arXiv:2509.25140; research.google blog 2026-04-21); Memp (arXiv:2508.06433). Advanced RAG: LazyGraphRAG (Microsoft Research blog, 2024-11); Anthropic contextual retrieval (anthropic.com/engineering/contextual-retrieval); Anthropic context engineering & long-running harnesses (anthropic.com/engineering). Pattern: Karpathy llm-wiki gist (gist.github.com/karpathy, 2026-04-04). Competitive: Windsurf Cascade Memories docs; Cursor rules/memories docs & forum; GitHub Copilot Spaces changelog 2025-10-17; Cline Memory Bank docs; Devin DeepWiki/Knowledge; IBM Project Bob announcement (ibm.com/new/announcements/ibm-project-bob) and hands-on (suedbroecker.net, 2026-01-07); ETH Zurich AGENTbench context-file study (InfoQ, 2026-03). MCP: 2026 roadmap (blog.modelcontextprotocol.io); enterprise adoption stats (andrew.ooo, 2026-07); OpenMemory MCP (mem0.ai). Standards: Portable Agent Memory (arXiv:2605.11032); W3C AI Agent Memory Interop CG proposal (w3.org, 2026-05-18); llms.txt studies (Ahrefs; Rankability, 2026-07-17). watsonx: OpenRAG announcement (ibm.com, 2026-03-10); IBM OpenSearch Premier membership (linuxfoundation.org, 2025-11); DataStax 1B-vector case study (opensearch.org); watsonx.data release notes; Docling (docling-project GitHub; IBM Research blog). Security: OWASP ASI06 / memory-poisoning literature (arXiv:2601.05504, arXiv:2512.16962 MemoryGraft, Unit 42, christian-schneider.net 2026-02-26). Observability: OpenTelemetry GenAI conventions (opentelemetry.io/blog/2026/genai-observability).

*Companion to the 2026-07-19 independent counter-audit. Filed as a dated record under `docs/knowledge-base/research/`; STATUS.md remains the single source of truth for maturity claims; projections herein are scored hypotheses, not measured results — per the repository's own provenance rule.*
