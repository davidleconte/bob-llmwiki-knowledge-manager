---
title: Independent Counter-Audit — Mnemox / bob-llmwiki-knowledge-manager
category: research
tags: [audit, counter-audit, mece, memory-layer, retrieval, governance, validation]
created: 2026-07-19
updated: 2026-07-19
status: active
provenance: Independent multi-agent counter-audit (Claude Cowork), 2026-07-19 snapshot; evidence cited as file:line against that snapshot
---

# Independent Counter-Audit of Mnemox (bob-llmwiki-knowledge-manager)

**Engagement type:** Independent counter-audit — audit, recommendations, target design, implementation and validation plans
**Methodology:** McKinsey MECE issue-tree decomposition; SCQA synthesis; impact × effort prioritization; adversarial claims reconciliation; empirical verification (test suite executed, gate scripts executed, CLI exercised)
**Posture:** Prior in-repo audit conclusions were deliberately ignored during analysis; all judgments were formed from source artifacts, then confronted with the repository's declarations
**Snapshot audited:** Working tree as of 2026-07-19 (no `.git` metadata in snapshot; environment-caused test artifacts identified and excluded from findings)

---

## 1. Executive Summary

### 1.1 Governing thought

Mnemox pairs **field-leading epistemic governance** — retraction of fabricated metrics, manifest-backed measurement, provenance-gated CI — with a **memory engine that is, as shipped, disconnected from its own retrieval path**. The validated hybrid retrieval stack (persistent embedding index, knowledge graph, p@3 = 0.88 configuration) exists, is tested, and is never invoked by any production code path. The route to production readiness is therefore not new features: it is **wiring, integrity repair, and independent verification**.

### 1.2 Situation — Complication — Question — Answer

**Situation.** Mnemox implements Karpathy's LLM-Wiki pattern as a native memory layer for IBM Bob: a git-versioned markdown knowledge base (110 documents), a schema layer (`AGENTS.md` + mode definitions), and a Python sidecar (~14,550 LOC, 12 packages) providing token optimization, multi-level caching, embeddings, a knowledge graph, and a validation harness. The repository declares "Beta — Not Production Ready" alongside a self-assessed weighted grade of "A+ (4.30/4.30)".

**Complication.** The counter-audit found that (i) the three retrieval tiers do not compose in any production path — the flagship precision claim (p@3 = 0.88) describes a configuration no user can reach; (ii) the default optimizer pipeline destroys document structure and can silently return an **empty string** for any prompt above 4,096 tokens; (iii) the knowledge base's integrity gates cannot fail — the link validator always reports success due to a subshell bug, while ~35–40 genuinely broken cross-references persist; and (iv) the current tree fails three of its own CI gates, and the A+ grade has no independent basis — the only independent verdict on file is a **NO-GO at 3.46/4.3** (2026-07-14).

**Question.** Is Mnemox's declared maturity trustworthy, and what is the shortest credible path to a production-ready, best-in-class code-assistant memory layer?

**Answer.** The declared *status* ("Beta — Not Production Ready") is **accurate and honest**; the declared *grade* (A+ 4.30/4.30) is **not substantiated**. The counter-audit weighted score is **2.9/5**. A three-horizon remediation program — H1 "Reconnect & Repair" (days), H2 "Lifecycle & Trust" (weeks), H3 "Compound & Prove" (months) — closes the gap with high confidence, because the required components already exist and are individually well-engineered.

### 1.3 Headline findings

Forty-six findings were registered: **3 Critical, 12 High, 14 Medium, 12 Low, 5 Informational**. The five that matter most:

1. **CODE-01/CODE-02 (Critical).** The persistent embedding index's query path can never return results — chunk identifiers (`file.md#slug`) fail a file-existence check and every candidate is silently discarded — and no production caller injects the index or graph into `KnowledgeBaseQuery` anyway. The entire P1–P3 investment (embeddings, index, graph) contributes nothing to what a session actually retrieves; `kb-search` is keyword-only, at the measured 0.64 (or 0.44) precision baseline, while `kb-status` prints "Full stack active — p@3=0.88".
2. **CODE-03/CODE-07 (Critical).** `optimize()` flattens all newlines (redundancy removal operates on whitespace-split tokens), then line-based truncation of the resulting single giant line returns `""`. Verified by execution: a 3,756-token input with `max_tokens=100` yields an empty output. The same pipeline corrupts the YAML frontmatter of KB documents that `analyze` writes — breaking date filtering and graph parsing downstream.
3. **MEM-02/MEM-03/MEM-04 (High).** The session auto-load pointer references `INDEX.md` while the file is `index.md` (silent cold-start failure on case-sensitive filesystems); a repo-wide kebab-case rename left ~35–40 broken cross-references including in `AGENTS.md` and `STATUS.md`; and `validate-kb.sh` always prints "✅ No broken links found" after listing the failures, never exiting non-zero.
4. **CLM-01/CLM-02 (High).** The tree fails its own gates (`check_savings_claims.py` on 12 surfaces including README; `check_value_homes.py` on version drift 1.0.0 vs 1.1.0; two genuine test failures), and the A+ (4.30/4.30) grade is self-conferred: the last independent audit artifact concludes NO-GO at 3.46/4.3, and no post-2026-07-14 audit artifact exists.
5. **Strengths worth stating with equal force.** The validation harness measures the real facade with a null test and reproducibility manifest — the ~20% compression claim (95% CI [18.9%, 21.2%], N=183) **survives adversarial reading**. Coverage claims reproduce (measured 89.68% vs claimed 89.82%, gate ≥80%). The fabrication of the withdrawn "68.96%" figure is handled with rare candor. Path containment, atomic persistence, and cache concurrency discipline are genuinely well-engineered.

### 1.4 Counter-audit scorecard

| Dimension (MECE) | Grade /5 | Rationale |
|---|---|---|
| D1 — Product correctness (optimizer, cache, truncation) | 2.5 | Truncation subsystem is trustworthy; optimizer can return empty output; L2→L1 promotion mislabels fuzzy matches as exact |
| D2 — Memory & retrieval architecture | 2.0 | Validated engine unwired; scoring algebra numerically inert (recency, PageRank); index lifecycle degrades monotonically |
| D3 — Knowledge-base integrity & maintenance | 2.5 | Maintenance ritual genuinely runs; but the gates that should catch corruption cannot fail, and corruption is accumulating |
| D4 — Claims, provenance & epistemic governance | 3.5 | Best-in-class honesty machinery and retraction discipline; undermined by guard rot and a self-conferred perfect grade |
| D5 — Engineering platform (tests, CI, security, governance) | 4.0 | 1,203 tests, ~90% coverage, 7-job CI with supply-chain gates, sound security posture; minor real failures |
| **Weighted overall** | **2.9 / 5** | **"Beta — Not Production Ready" confirmed; "A+ (4.30/4.30)" not confirmed** |

### 1.5 Recommendation portfolio (summary)

- **Horizon 1 — Reconnect & Repair (≈ 3–5 engineer-days).** Fix the `#slug` existence check; wire index + graph + validated `embedding_weight=0.7` into `kb-search`; make the optimizer structure-preserving and never-empty; fix `validate-kb.sh`; one-shot casing/link repair sweep; align versions; fix the two failing tests. Highest ROI in the entire program: the p@3 uplift from 0.64 → 0.88 is approximately 20 lines of wiring.
- **Horizon 2 — Lifecycle & Trust (≈ 2–4 weeks).** Index deletion/rebuild lifecycle with dimension enforcement; normalize all ranking signals to [0,1] before blending; replace KB auto-commit with a review gate; per-document provenance frontmatter; write-time near-duplicate consolidation; compact auto-generated index (< 3k tokens cold start); commit the p@3 golden set; commission an independent re-grade.
- **Horizon 3 — Compound & Prove (≈ 1–3 months).** Demonstrate the full write→retrieve→compound loop on a foreign repository; watsonx-correct tokenizer and pricing; real environment configuration; multi-user conflict arbitration; graph edge-density health regression metrics.

---

## 2. Engagement Scope and Methodology

### 2.1 MECE issue tree

The audit decomposed the question "Is Mnemox a trustworthy, production-grade code-assistant memory layer?" into five mutually exclusive, collectively exhaustive dimensions:

| Dimension | Question | Evidence stream |
|---|---|---|
| D1 Product correctness | Does the shipped Python product behave as specified? | Full `src/` code audit (all 12 packages), execution of suspect paths |
| D2 Memory & retrieval architecture | Does knowledge written ever come back, precisely, at acceptable cost? | End-to-end trace of write/read/maintenance paths; tier composition analysis |
| D3 KB integrity & maintenance | Is the stored knowledge internally consistent and maintained? | KB corpus inspection (110 docs), gate script execution, link verification |
| D4 Claims & epistemic governance | Do the repository's declarations match its artifacts? | Forensic claims register (17 claims), provenance tracing, grade genealogy |
| D5 Engineering platform | Do tests, CI, security and governance support the above? | Empirical test run (1,203 tests), CI gate inventory, security sweep |

Overlap control: wiring defects are counted once (D2) even where they surface as false claims (D4); casing defects are counted once per artifact class.

### 2.2 Evidence base

Four independent analysis streams were executed in parallel, each blind to the others' conclusions: (1) a first-principles code audit instructed to ignore all in-repo self-assessments; (2) a memory-systems specialist assessment against a six-dimension challenge taxonomy; (3) a forensic claims reconciliation — the only stream permitted to read the self-assessments; (4) an empirical verifier that installed the project, ran the suite, the coverage gate, the CLI, the validation harness, and every CI gate script locally. Convergence across blind streams (e.g., three streams independently surfaced the casing-rename fallout; two independently established the unwired retrieval stack) materially raises confidence in the findings.

### 2.3 Limitations

The snapshot excluded `.git`; five test failures attributable to that environment (git provenance, sentence-transformers absence, shared-container latency) were identified and excluded. Claims dependent on the proprietary IBM Bob runtime (Bobcoin billing, mode-picker UX, `save_memory` semantics) are unverifiable from the repository and are marked as such, not counted against the project. Precision figures (p@3) could not be re-measured because no golden set is committed (see CLM-06).

---

## 3. State of the Asset

### 3.1 Architecture map

~14,550 LOC across 12 packages, plus a 110-document knowledge base and a Bash orchestration layer:

| Component | LOC (≈) | Responsibility |
|---|---|---|
| `src/facade.py`, `src/factory.py` | 250 | `TokenOptimizer` facade; config→component builders; holds no business logic |
| `src/cache/` | 2,640 | L1 exact LRU cache; L2 semantic cache (embedding scan); `MultiLevelCache`; `EmbeddingGenerator` (HashingVectorizer / MiniLM) |
| `src/optimizer/` | 880 | `PromptOptimizer` (whitespace/redundancy/filler); `TokenCounter` (tiktoken or chars/4 fallback) |
| `src/truncation/` | 690 | Four strategies + dispatcher with enforced budget invariant — the most trustworthy subsystem |
| `src/embeddings/` | 790 | `PersistentEmbeddingIndex` (.npy + JSON manifest), markdown chunker, file-backed vector store, `KBIndexer` |
| `src/graph/` | 1,170 | Pure-Python property graph, frontmatter/link/semantic edge builder, PageRank, `GraphRanker`, atomic store |
| `src/tools/` | 1,670 | `KnowledgeBaseQuery` (keyword + optional embedding/index/graph/recency), component analyzer, batch reader, `safe_paths` |
| `src/delegation/` | 2,060 | Thread-pool coordinator, six regex-heuristic agents, `analyze_and_ingest` pipeline |
| `src/monitoring/` | 2,040 | Metrics, structured logging, health checks, Bobcoin cost tracking |
| `src/config/` | 920 | Dataclass schema, singleton manager, rule-based validator |
| `src/validation/` | 780 | Manifest-backed measurement harness with null test; refuses to gate on savings magnitude |
| `src/cli.py` + entry points | 600 | 15 subcommands over the facade, graph, KB and delegation layers |

Dependency direction is clean (no cycles; facade genuinely thin). The knowledge base holds 110 documents in four categories with template/frontmatter discipline enforced by scripts; a close-of-session ritual (`scripts/mnemox.sh`) demonstrably runs (timestamps match graph build metadata).

### 3.2 What is genuinely strong

1. **Honest validation harness** — measures the real facade, writes reproducibility manifests (data hash, code SHA, seed, library versions, `git_dirty`), includes a null test, and deliberately refuses to gate on savings magnitude ("gating a measurement re-incentivises fabrication").
2. **Retraction discipline** — the fabricated "68.96% / VALIDATED" episode is documented mechanism-by-mechanism, the fabricated artifact is retained under a banner as an audit record, and no living document reasserts the withdrawn numbers.
3. **Atomic persistence and path containment** — temp-file + `os.replace` everywhere, `allow_pickle=False` both directions, `resolve_within()` applied at tool entry points and re-applied to discovered leaves against symlink escapes.
4. **Cache concurrency discipline** — documented lock ordering, synchronized decorators with rationale, frozen stats snapshots, a dedicated `CONCURRENCY.md`.
5. **The compact-summary/comprehensive-doc taxonomy** — recognizing that only source-replacing digests save tokens, and tagging them — is conceptually sharper than either RAG (chunk everything) or memory files (append everything).
6. **CI depth** — 7 jobs: locked installs, coverage gate + per-package floors, ruff/mypy, layering gate, savings-claim provenance guard, status-consistency validator, SBOM + `pip-audit --strict`, benchmark trending, informational load job.

---

## 4. Audit Findings by Dimension

Severity legend: **C** Critical (product promise broken) · **H** High (materially misleading or degrading) · **M** Medium · **L** Low · **I** Informational. Every finding carries file:line evidence in the consolidated register (Appendix A).

### 4.1 D1 — Product correctness

The optimizer's default pipeline is the core defect. `_remove_redundancy` flattens every newline (`text.split()` + `" ".join()`); `_truncate_to_limit` then binary-searches over `splitlines()` of what is now one giant line and returns `""` when it exceeds budget. Because `OptimizerConfig.max_tokens` defaults to 4,096 and the facade applies it, **any prompt above 4,096 tokens is silently reduced to nothing** by `bob-optimize optimize` (CODE-03, verified by execution). The same pipeline corrupts the KB documents the delegation pipeline writes — frontmatter flattened to one line, breaking `date:` filtering and graph frontmatter parsing — while the reported compression ratio reads a key the optimizer never emits, so it is always 1.0 (CODE-07).

In the cache, an L2 similarity hit (≥ 0.85 cosine over 1,000-dim hashed bag-of-words) is promoted into L1 **under the query's key**: a borderline fuzzy match becomes a permanent exact hit with no similarity annotation (CODE-08). `contains()` ignores TTL expiry; caller-supplied metadata dicts are mutated and shared across levels (CODE-17). The `--environment` flag is decorative — no environment file is ever loaded, and the singleton ignores the argument after first construction (CODE-09). Token counting and pricing assume OpenAI models; on a watsonx/Bob deployment every budget and savings figure is computed against the wrong tokenizer and 2024 GPT-4 prices, with silent chars/4 degradation (CODE-10). By contrast, the truncation subsystem enforces its budget invariant rigorously, including BPE boundary drift — it is the subsystem to model the others on.

### 4.2 D2 — Memory & retrieval architecture

Three independent defects compound into one architectural fact: **the memory layer's validated retrieval stack is unreachable.**

- The persistent index's query path drops every candidate: chunk doc_ids are built as `file.md#slug`, then checked with `(kb_path / doc_id).exists()` — always false — and the silent full-scan fallback masks the bug, including in the test that claims to cover the path (CODE-01, verified by execution).
- No production caller passes `index=` or `graph=` to `KnowledgeBaseQuery`: not the `kb-search` CLI, not `ResearchAgent`, not the module CLI. The A/B-validated `embedding_weight=0.7` (p@3 0.88 vs 0.64) lives only in an uncalled method and in tests (CODE-02, MEM-01).
- Even if wired, the blending algebra is inert: recency normalizes mtimes as `epoch/max_epoch` (≈ 0.97–1.0 for any plausible corpus — a 2020 vs 2026 document differs by ~0.03), and PageRank×15 ≈ 0.2 against keyword scores up to 15+, so `graph_weight` is a no-op until ~0.95, then dominates (CODE-05, CODE-06).

The index lifecycle degrades monotonically: edited or renamed sections and deleted files leave stale vectors that keep matching with old content (rows are never deleted, CODE-04); a backend switch (hashing 1000-d ↔ MiniLM 384-d) crashes `search()` instead of the documented auto-rebuild (CODE-15); nothing on the query path checks staleness (CODE-11). Two divergent indexes coexist — `.bob/kb-index` (hashing, 1,459 chunks, rebuilt by the ritual) and `.bob/kb-index-st` (MiniLM, 1,049 chunks, orphaned) — and the live graph's 4,234 semantic edges derive from the backend the project's own validation rejected, violating the repo's own RAG-hygiene rule (MEM-06).

Cold-start economics also cut against the design goal: `.bob/settings.json` auto-loads ~50 KB (~12–13k tokens) of `AGENTS.md` + index every session, and the index lists every document twice with an unpruned "Recent Additions" section (MEM-08) — the system built to save tokens spends five figures of tokens per session on its own map.

### 4.3 D3 — Knowledge-base integrity & maintenance

The maintenance ritual genuinely runs — timestamps, graph metadata, and substantively filled lesson scaffolds prove it — but **it cannot detect the corruption it is accumulating**:

- `validate-kb.sh` increments its broken-link counter inside a `find | while` pipeline subshell; the count never propagates, so the script prints "✅ No broken links found" immediately after listing ~80 failures and never exits non-zero (MEM-04).
- A repo-wide kebab-case rename left ~35–40 genuinely broken references — in the KB, in `AGENTS.md` (the schema layer itself), and in `STATUS.md` (both cited basis documents 404 on a case-sensitive filesystem) (MEM-03, CLM-04). This is precisely the failure mode the KB's own lessons document warns about: a broken pointer silently converts the claimed 51% re-derivation saving into negative savings (failed fetch + full raw read).
- The session auto-load pointer is case-broken (`INDEX.md` vs `index.md`): on Linux — the CI runner the repo targets — the KB map silently never enters context (MEM-02).
- Graph "broken edge" detection only covers intra-KB targets; links leaving the KB are silently dropped, so `graph-health` reports zero broken edges while dozens exist (MEM-05).
- Semantic edge density is noise-level and worsening: ~39 edges/node at median cosine 0.41, celebrated in the automated lessons as "retrieval quality compounds" when it is a precision-decay signal (MEM-07).
- The update path auto-commits agent-written KB content with no review gate — unreviewed agent output becomes durable team memory, the single largest trust liability in the design (MEM-09) — and documents carry no provenance of who or what wrote them (MEM-14).

Compounding is real but narrow: the cache thread-safety saga demonstrably distilled into a reusable checklist, and honest small-N measurement exists (51% saving, CI [38%, 64%], N=10 compact-summary pairs — published alongside the unflattering 2% all-pairs figure). But 65 of 110 documents are process snapshots or marketing artifacts filed as knowledge, the corpus is largely the memory system documenting itself, and the shipped usage surfaces (`Recipes/`, `LABs/`) contain **zero** references to the KB or its retrieval commands (MEM-12, MEM-13).

### 4.4 D4 — Claims, provenance & epistemic governance

Seventeen claims were registered and verified (Appendix B). The pattern: **the smallest public number is protected by the strongest provenance, while the largest public numbers sit in surfaces no gate scans.**

- **Verified:** the ~20% compression claim (manifest-complete, null test passing, N=183, honest per-document data; one caveat — `git_dirty: true` on the flagship run, CLM-07); the G-1–G-4 gap closures; ADR-017/018/019 code existence; the KM savings figures with disclosed small N; the retraction discipline (no living reassertion of withdrawn numbers).
- **Partially verified:** coverage (claimed 89.82%; committed artifact 89.19%; independently measured 89.68% — honest within noise, but the exact headline number has no supporting artifact, CLM-03); test counts (order-of-magnitude right, exact figures drifted, CLM-09).
- **Contradicted:** "all gates green" — the tree fails `check_savings_claims.py` (12 surfaces including README), `check_value_homes.py` (version 1.0.0 vs 1.1.0 drift; `SECURITY.md` stale), API-doc freshness, and two genuine tests (CLM-01). STATUS's own basis links are case-broken (A13).
- **Unverifiable / self-asserted:** the A+ (4.30/4.30) grade. The only independent verdict on file — the Phase-8 adversarial sign-off the STATUS row cites as its basis — is an explicit **NO-GO at 3.46/4.3** ("no dimension reached A+"). Four subsequent grade increments to a perfect score were produced by the same agentic process that performed the remediation, with no post-2026-07-14 audit artifact (CLM-02). Marketing surfaces project 40–75% Bobcoin reductions from a directory the savings-claims gate deliberately exempts, and cite a CLI command (`index-kb`) that does not exist (CLM-05, CLM-08). The p@3=0.88 figure has per-query documentation but no committed golden set or scoring script, and its baseline drifts between documents (0.64 vs 0.44) (CLM-06).

The epistemic machinery itself is decaying quietly: the status-consistency validator prints `SKIP … not found` for a renamed surface and exits 0 — a guard that no longer guards (CLM-04).

### 4.5 D5 — Engineering platform

Empirically the strongest dimension. Collection: 1,203 tests, zero errors. Functional run (excluding slow markers): **1,164 passed / 8 failed / 25 skipped in 103 s** — of the 8 failures, 5 are environment artifacts and 3 are real (research template missing its own tested `## Methodology` section; documentation-existence test expecting lowercase filenames that fail on Linux; a hard failure rather than skip without sentence-transformers). Coverage measured at **89.68%** against the enforced ≥80% gate, with all five per-package floors satisfied. The CLI works out of the box (15 subcommands; clean backend fallback warnings); the validation harness runs end-to-end and correctly refuses to emit results without complete git provenance.

Security posture is sound: no eval/exec/pickle/unsafe YAML anywhere in `src/` or `scripts/`; the only subprocess is static-argv git with timeout; path traversal properly mitigated; numpy persistence pickle-free both directions. Residuals are minor: a lab credential in a disabled MCP server config (SEC-01), stale `SECURITY.md` version table (SEC-02), environment-fragile latency tests (SEC-06). Governance artifacts (SECURITY/GOVERNANCE/SUPPORT, CODEOWNERS, dependabot, community-health gate) are complete and honest about the single-maintainer model. Reproducibility: a stranger validates the measurement claims in well under 30 minutes — but will conclude "the suite doesn't pass on Linux," which is the platform's biggest blemish.

---

## 5. Verdict Against Declared Status

| Repository declaration | Counter-audit verdict |
|---|---|
| "Beta — Not Production Ready" | **Confirmed.** Accurate; arguably the most honest headline in the repo |
| "A+ (4.30/4.30) weighted grade" | **Not confirmed.** Self-conferred; contradicted by the only independent artifact (NO-GO, 3.46/4.3); counter-audit score 2.9/5 |
| "~20% mean savings, CI [19%, 21%], N=183" | **Confirmed** (with dirty-tree provenance caveat) |
| "89.82% global coverage" | **Approximately confirmed** (89.19% artifact / 89.68% measured; headline figure unsupported) |
| "CI enforces the quality gates" | **Mechanism confirmed; state contradicted** — the current tree fails 3 of its own gates |
| "p@3=0.88 retrieval, full stack active" | **Contradicted as shipped** — the measured configuration is unreachable from any production path |
| "51% re-derivation saving (N=10)" | **Confirmed as measured**, with honest disclosure of the 2% all-pairs figure; undermined operationally by broken pointers (MEM-03) |

---

## 6. Recommendations

Prioritized by impact × effort within three horizons. Finding references map to Appendix A.

### 6.1 Horizon 1 — Reconnect & Repair (target: one sprint, ≈ 3–5 engineer-days)

| # | Action | Resolves | Impact | Effort |
|---|---|---|---|---|
| R1 | Fix the `#slug` existence check (strip fragment before path test; dedupe per file); add an integration test asserting the index path was *used* (full scan not invoked) | CODE-01 | Critical | Hours |
| R2 | Wire `index=`, `graph=`, `embedding_weight=0.7` (validated) into `kb-search`, `KBIndexer.query`, `ResearchAgent`; make `kb-status` report the *wired* configuration only | CODE-02, MEM-01 | Critical — p@3 0.64→0.88 for ~20 lines | Hours |
| R3 | Make the optimizer structure-preserving and never-empty: line-aware redundancy removal; exempt YAML frontmatter and fenced code; post-condition falling back to token-accurate truncation | CODE-03, CODE-07 | Critical | 1–2 days |
| R4 | Rewrite `validate-kb.sh` link check (process substitution, anchor/mailto/dir exclusions, non-zero exit); wire into CI as blocking | MEM-04 | High | Hours |
| R5 | One-shot casing/link repair sweep: `INDEX.md`→`index.md` in settings and skills; ~40 renamed-reference fixes across KB, `AGENTS.md`, `STATUS.md`; update gate-script hardcoded paths and exclusion regexes; add a CI check that every configured pointer resolves on a case-sensitive FS | MEM-02, MEM-03, CLM-04, A13 | High | 1 day |
| R6 | Align versions (`src/__init__.py`, `src/delegation/__init__.py`, `CHANGELOG.md` 1.1.0 entry, `SECURITY.md` table); fix the two genuinely failing tests; regenerate stale API doc | CLM-01, SEC-02 | High | Hours |
| R7 | Downgrade every published "p@3=0.88" statement to the wired configuration's figure until R2 lands; remove the hardcoded claim from `kb-status` output | MEM-01, CLM-06 | High (credibility) | Hours |

### 6.2 Horizon 2 — Lifecycle & Trust (target: 2–4 weeks)

| # | Action | Resolves |
|---|---|---|
| R8 | Index lifecycle: delete rows on file change/removal; record `embedding_dim` + backend in manifest and rebuild on mismatch; staleness spot-check (or auto-`sync()`) on query construction; single canonical index directory — delete or promote `.bob/kb-index-st` | CODE-04, CODE-11, CODE-15, MEM-06 |
| R9 | Normalize the ranking algebra once, in one place: min-max normalize keyword, embedding, PageRank and recency signals to [0,1] within the result set before blending; re-run the A/B validation; apply top-k cut *after* blending and date filtering | CODE-05, CODE-06, CODE-14 |
| R10 | Replace KB auto-commit with a review gate: stage-only by default (or a `mnemox/` branch), `--commit` opt-in; add `source:` (human/agent/pipeline + session id) and `review_by:` frontmatter; teach `validate-kb.sh` the new fields | MEM-09, MEM-14 |
| R11 | Write-time consolidation: before filing, query the index for near-duplicates (cosine > ~0.6) and force merge / supersede / link; add an `archive/` tier and retrieval-time filtering on `status`; move one-off phase reports and marketing briefs out of the retrieval set | MEM-12, near-duplicate concepts |
| R12 | Compact auto-generated index from frontmatter (one line per doc, Recent Additions capped at 10, no double listing) targeting < 3k tokens cold start; track cold-start tokens as a regression metric | MEM-08 |
| R13 | Commit the p@3 golden set and scoring script; make retrieval precision a manifest-backed, re-runnable number like the savings figure; reconcile the 0.64/0.44 baseline drift | CLM-06 |
| R14 | Commission a genuinely independent re-grade (human third party or an external agentic process with no remediation involvement); until then, replace "A+ (4.30/4.30)" with the last independent verdict plus a dated remediation log | CLM-02 |
| R15 | Extend the savings-claims gate to the marketing surfaces (`research/` briefs, challenge submission, `Recipes/`, `LABs/`, `evaluation/`); require a "projection, not measured" tag with a link to measured baselines on every 40–75% figure; fix the nonexistent `index-kb` command reference | CLM-05, CLM-08 |
| R16 | Cache semantics: promote L2 hits under the matched key with similarity annotation; TTL check in `contains()`; copy metadata dicts per level; re-run a rerun of the validation harness from a clean tree to clear `git_dirty` | CODE-08, CODE-17, CLM-07 |

### 6.3 Horizon 3 — Compound & Prove (target: 1–3 months)

| # | Action | Resolves |
|---|---|---|
| R17 | End-to-end Recipe/LAB running the full write→retrieve→compound loop on a **foreign** repository — the missing proof that compounding generalizes beyond self-documentation | MEM-13 |
| R18 | Tokenizer/pricing correctness for the actual deployment target: explicit tokenizer resolution, loud fallback signaling, watsonx/Claude price tables; retire the 2024 OpenAI table as default | CODE-10 |
| R19 | Real environment configuration (map environment→file and load it) or remove the `-e` flag and singleton parameter | CODE-09 |
| R20 | Graph health as regression discipline: edges/node and median-cosine tracked as health regressions, top-k mutual-NN edge capping, out-of-KB broken-edge reporting | MEM-05, MEM-07 |
| R21 | Performance at scale: vectorize the L2 scan (matrix cosine, as L3 already does); lazy percentile computation; PageRank dangling-node optimization — required before any 10x KB-size claim | CODE-13, CODE-16 |
| R22 | Multi-user trust: conflict arbitration beyond git (review requirements per category, poisoning surface review of the delegation write channel) | MEM-09 residual |

---

## 7. Target-State Design (Memory Layer)

The target architecture keeps what is differentiated — git-versioned markdown as the store, the schema layer, the honesty machinery — and completes the loop that is currently severed:

1. **One retrieval plane.** A single `KnowledgeBaseQuery` construction site (factory) that always receives the canonical index, graph, and validated weights from configuration; keyword-only mode becomes an explicit degradation with a logged reason, never a silent default. Every retrieval claim in docs derives from the factory's actual defaults, mechanically checked.
2. **A real index lifecycle.** The index is a managed artifact with schema: backend, dimension, chunk inventory with deletion semantics, staleness contract on the query path, and a single home on disk. Rebuilds are idempotent and dimension-safe.
3. **Normalized ranking algebra.** All signals — lexical, dense, graph centrality, recency — normalized to [0,1] within the candidate set, blended with weights that live in one config dataclass, validated by a committed golden set that CI can re-score.
4. **Write-side governance as the differentiator.** Provenance frontmatter (`source`, `session`, `review_by`), staged-branch commits with human review, write-time near-duplicate consolidation, and lifecycle states (`active`/`superseded`/`archived`) that the retrieval plane respects. This converts the current biggest liability — unreviewed agent-written memory — into the product's defensible moat: *auditable, git-native memory provenance*, which neither RAG stores nor MCP memory servers offer.
5. **Context budget as an SLO.** Cold-start tokens (< 3k target), edges/node, stale-doc count, and broken-pointer count tracked as regression metrics in CI, alongside the existing coverage and savings gates.
6. **Provenance symmetry.** Every published number — savings, precision, coverage, grade — carries the same manifest discipline the 20% figure already has. What cannot be re-measured from committed artifacts is not published.

---

## 8. Implementation Plan

| Phase | Duration | Workstreams | Exit criteria |
|---|---|---|---|
| P0 — Baseline freeze | 0.5 day | Tag the snapshot; record current gate failures; open findings register as issues | All 46 findings triaged into issues with owners |
| P1 — Reconnect & Repair (R1–R7) | 3–5 days | Retrieval wiring; optimizer structure preservation; integrity gates; casing sweep; version alignment | Suite green on Linux; all repo gates pass; `kb-search` demonstrably uses the index (integration test); no unreachable-claim published |
| P2 — Lifecycle & Trust (R8–R16) | 2–4 weeks | Index lifecycle; ranking algebra; write governance; compact index; golden set; independent re-grade commissioned | p@3 re-measured from committed golden set; cold start < 3k tokens; review gate active; clean-tree validation manifest |
| P3 — Compound & Prove (R17–R22) | 1–3 months | Foreign-repo demonstration; tokenizer correctness; scale hardening; multi-user trust | One external repo shows measured re-derivation savings; watsonx tokenizer default; graph health SLOs in CI |
| P4 — Re-audit & status update | 1 week | Independent re-audit against this report's findings register | Every Critical/High closed or accepted with rationale; STATUS.md grade replaced by independent verdict |

Sequencing rationale: P1 items are independent of each other and parallelizable; P2's R9 (algebra) depends on R2 (wiring) to be measurable; R13 (golden set) must precede R14 (re-grade) so the re-grade scores the wired system; P3's foreign-repo proof depends on P2's write governance to be credible.

---

## 9. Validation Plan

### 9.1 Per-fix acceptance criteria (samples; full mapping in the findings register)

| Fix | Acceptance test |
|---|---|
| CODE-01/02 | Integration test: index a KB, edit nothing, run `kb-search`; assert the full-scan path was **not** invoked and results carry index provenance. Mutation check: re-break the `#slug` join and confirm the test fails |
| CODE-03 | Property-based test (Hypothesis): for all inputs and all `max_tokens ≥ 1`, output is non-empty when input is non-empty, and line structure of surviving content is preserved; regression test at 3,756 tokens / cap 100 |
| CODE-07 | Round-trip test: `analyze` output parses as valid frontmatter + markdown; `date:` filter and graph builder consume it successfully |
| MEM-04 | `validate-kb.sh` exits non-zero on a planted broken link; CI job goes red; anchor/mailto/dir links produce no false positives |
| MEM-02/03 | CI job on ubuntu-latest resolves every pointer in `settings.json`, `AGENTS.md`, `STATUS.md`, and skills; zero broken references reported by the (fixed) validator |
| CODE-05/06 | Unit tests on synthetic corpora: a strictly newer document outranks an older equal-score document at `recency_weight=0.5`; a high-PageRank document measurably moves rank at `graph_weight=0.3`; blend weights sum-to-one property holds |
| CLM-01 | All gate scripts exit 0 in CI on the release SHA; release blocked otherwise |
| CLM-02/R14 | Independent re-grade artifact committed with grader identity, method, and per-dimension scores; STATUS.md cites it |

### 9.2 Program-level validation

1. **Gate integrity:** every integrity gate must be demonstrated *capable of failing* (planted-defect tests in CI for the link validator, status validator, savings guard, value-homes) — a gate that cannot fail is not a gate.
2. **Provenance-complete metrics:** re-run the validation harness from a clean tree (`git_dirty: false`); commit the p@3 golden set and re-measure; regenerate coverage headline from the committed artifact only.
3. **Cold-start budget:** measured token count of auto-loaded context < 3,000; tracked in CI as a regression metric.
4. **Compounding evidence:** one foreign-repository case study with before/after measured token spend across ≥ 5 sessions, manifest-backed, published with the same discipline as the 20% figure.
5. **Re-audit protocol:** independent re-audit (no remediation involvement) scoring the same five MECE dimensions; target ≥ 4.0/5 weighted with zero open Critical/High findings before any production-readiness claim.

---

## Appendix A — Consolidated Findings Register

### Critical

| ID | Dim | Summary | Evidence |
|---|---|---|---|
| CODE-01 | D2 | Persistent-index query path never returns results: `file.md#slug` doc_ids fail the existence check; silent full-scan fallback masks the bug (also in its own test) | `src/embeddings/index.py:187`, `src/tools/kb_query.py:252-254`, `:284-285` |
| CODE-02 | D2 | Embedding index and graph re-ranking wired into no production path; `kb-search`, `ResearchAgent`, module CLI all keyword-only | `src/cli.py:349-352`, `src/delegation/research_agent.py:34`, `src/embeddings/indexer.py:89-97` |
| CODE-03 | D1 | `optimize()` can return empty string (structure-flattening + line-truncation of one giant line); default 4,096-token cap makes this the default behavior for long prompts | `src/optimizer/prompt_optimizer.py:329-349`, `:441-453`, `src/config/schema.py:48`, `src/facade.py:135-141` |

### High

| ID | Dim | Summary | Evidence |
|---|---|---|---|
| CODE-04 | D2 | Index rows never deleted: stale vectors from edits/renames/deletions match forever; `flush()` refuses to persist an emptied index | `src/embeddings/index.py:186-197`, `:261-262` |
| CODE-05 | D2 | Recency weighting numerically inert (`epoch/max_epoch` ≈ 0.97–1.0) | `src/tools/kb_query.py:399-405` |
| CODE-06 | D2 | PageRank blend scale-mismatched (×15 ≈ 0.2 vs keyword ≤ 15+); `graph_weight` no-op until ≈0.95 | `src/graph/ranker.py:20-23`, `:89` |
| CODE-07 | D1 | `analyze_and_ingest` corrupts written KB docs (frontmatter flattened); compression ratio always 1.0 (absent key); cache-hit path raises TypeError | `src/delegation/pipeline.py:210-228`, `:260-278` |
| CODE-08 | D1 | L2→L1 promotion caches fuzzy match as exact under the query key; metadata dropped | `src/cache/multi_level_cache.py:180-184` |
| CODE-09 | D1 | `--environment` decorative: no env file loaded; singleton ignores argument | `src/config/manager.py:51-80` |
| MEM-01 | D2 | Validated retrieval (p@3=0.88, w=0.7) unreachable; `kb-status` falsely announces "Full stack active — p@3=0.88" | `src/cli.py:349`, `:490` |
| MEM-02 | D3 | Session auto-load pointer case-broken (`INDEX.md` vs `index.md`); silent cold-start failure on case-sensitive FS | `.bob/settings.json`, `.bob/skills/knowledge-manager/SKILL.md` |
| MEM-03 | D3 | ~35–40 broken cross-references from kebab-case rename, incl. `AGENTS.md` and `STATUS.md` basis links | `validate-kb.sh` output; `AGENTS.md:35,101,371-385,445` |
| MEM-04 | D3 | `validate-kb.sh` always reports success (subshell counter loss), never exits non-zero | `scripts/validate-kb.sh:31-51` |
| CLM-01 | D4 | Tree fails its own CI gates: savings-claims (12 surfaces incl. README), value-homes (1.0.0 vs 1.1.0), API-doc freshness, 2 genuine test failures | `scripts/check_savings_claims.py`, `scripts/check_value_homes.py`, `tests/test_templates.py`, `tests/test_workflows.py` |
| CLM-02 | D4 | A+ (4.30/4.30) self-conferred; only independent artifact says NO-GO 3.46/4.3; no post-07-14 audit exists | `docs/knowledge-base/research/audit-2026-07-14-signoff.md`; `STATUS.md:11` |

### Medium

| ID | Dim | Summary |
|---|---|---|
| CODE-10 | D1 | OpenAI-only tokenizer/pricing; silent chars/4 degradation; wrong economics on watsonx deployments |
| CODE-11 | D2 | No staleness check on the query path; `is_stale()` only used by status display |
| CODE-12 | D1 | Pervasive silent `except Exception: continue/pass` across the KB layer |
| CODE-13 | D5 | L2 lookup O(n·dim) Python-loop cosine; percentile sort inside metrics lock on every hit |
| CODE-14 | D1 | Multi-level `size()` double-counts without version support; CLI text path KeyError on error dicts; top-k cut before blend/date-filter |
| CODE-15 | D2 | Backend/dimension switch crashes `search()` instead of documented auto-rebuild |
| MEM-05 | D3 | Graph broken-edge detection blind to out-of-KB targets; false clean bill |
| MEM-06 | D2 | Two divergent indexes; live graph built from the validation-rejected backend |
| MEM-07 | D3 | Semantic edge density noise-level (~39/node, median cosine 0.41) and celebrated as improvement |
| MEM-08 | D2 | ~12–13k-token cold start, monotonically growing; index double-lists every doc |
| MEM-09 | D3 | Auto-commit of agent-written KB content without review; poisoning propagation vector |
| CLM-03 | D4 | Coverage headline (89.82%) contradicts committed artifact (89.19%); number not guarded by value-homes |
| CLM-04 | D4 | Guard rot from casing rename: consistency validator silently skips a surface; savings-gate exclusion regex dead |
| CLM-05 | D4 | 40–75% marketing projections in gate-exempt directories; exceed every measured figure |

### Low / Informational

| ID | Dim | Summary |
|---|---|---|
| CODE-16 | D5 | Coordinator retry stats skipped; sequential timeout accounting; hubs double-weighting; PageRank O(d·n) dangling loop |
| CODE-17 | D1 | `contains()` ignores TTL; metadata dicts mutated and shared across levels; logger level ignored when cached; hardcoded p@3 string in CLI |
| MEM-10 | D3 | Lessons "new docs" detection uses mtimes → false deltas |
| MEM-11 | D3 | Documented pointer fix introduced two new broken pointers; correction loop lacks verification |
| MEM-12 | D3 | Marketing/process artifacts filed as knowledge (65/110 docs in research tier) |
| MEM-13 | D2 | `Recipes/`/`LABs/` contain zero KB references; adoption pattern undemonstrated |
| MEM-14 | D3 | No per-doc provenance (author/session/model) or review/expiry semantics |
| CLM-06 | D4 | p@3 golden set/scoring script not committed; baseline drift 0.64 vs 0.44 |
| CLM-07 | D4 | Flagship validation run from dirty tree (`git_dirty: true`) |
| CLM-08 | D4 | Marketing cites nonexistent `bob-optimize index-kb` command |
| CLM-09 | D4 | Minor count drifts (24 vs 23 skips; 60 vs "23" performance tests) |
| SEC-01 | D5 | Lab credential in disabled MCP config (`.bob/mcp.json:109`) |
| SEC-02 | D5 | `SECURITY.md` supported-versions table stale vs 1.1.0 |
| SEC-06 | D5 | Latency SLO tests environment-fragile on shared hardware |
| SEC-03/04/05 | D5 | Positive: path containment, pickle-free persistence, static-argv subprocess, clean shell scripts |

## Appendix B — Claims Register (abridged)

| Claim | Verdict |
|---|---|
| "Beta — Not Production Ready" canonical | VERIFIED |
| ~20% savings, CI [19,21], N=183, null pass | VERIFIED (dirty-tree caveat) |
| Coverage 89.82% global / 84% delegation | PARTIALLY VERIFIED (89.19% artifact / 89.68% measured; delegation exact) |
| "1112 passed / 23 skipped" | PARTIALLY VERIFIED (1164/25/8-failed measured; 2 real failures) |
| CI gate inventory as described | VERIFIED as mechanism; current tree fails 3 gates |
| G-1–G-4 closed | VERIFIED |
| ADR-017/018/019 code exists | VERIFIED (p@3 reproducibility: UNVERIFIABLE — no golden set) |
| A+ (4.30/4.30) | UNVERIFIABLE / SELF-ASSERTED; contradicted by NO-GO 3.46/4.3 |
| Fabrication withdrawn, no reassertion | VERIFIED |
| STATUS basis links resolve | CONTRADICTED (case-broken) |
| KM savings 51% (N=10) / 2% all-pairs | VERIFIED as measured, honestly disclosed |
| Platform claims (Bobcoin, save_memory, mode UX) | UNVERIFIABLE FROM REPO (proprietary runtime) |
| SLA v1.0 targets | VERIFIED as targets, explicitly not guarantees |

## Appendix C — Method Notes

Empirical environment: Python 3.11.15 venv; `pip install -e '.[monitoring]'` + test tooling; sentence-transformers deliberately omitted (2 skips + 1 failure attributable, identified). Full functional suite: 103 s. Coverage run: 89.68% (5,156 statements, 532 missed). Gate scripts executed verbatim from `scripts/`. Validation harness executed end-to-end (`--corpus repo --no-write`): pipeline healthy, exit 1 on missing git provenance — correct strict behavior in a snapshot without `.git`. All file:line citations refer to the 2026-07-19 snapshot.

*This document was produced by an independent multi-agent counter-audit and is intended to be filed under `docs/knowledge-base/research/` as a dated, frozen record. Per the repository's own convention, `STATUS.md` remains the single source of truth for current maturity; this record supersedes no prior document but should inform the next STATUS revision.*
