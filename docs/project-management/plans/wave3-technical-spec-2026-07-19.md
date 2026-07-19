# Wave 3 — Technical Specification: Compound, Prove & Govern-at-Scale

> **Provenance banner (planning doc).** This is a forward-looking implementation +
> validation spec, authored 2026-07-19 after PR #24 (Wave 2) merged to `main`
> (merge `3baed4f`). It references retracted/withdrawn figures **only to critique
> them**. Canonical maturity lives in `STATUS.md`; the only validated savings number
> is the manifest-backed optimizer compression at
> `evaluation/results/validation-2026-07-14/manifest.json`; the retrieval headline is
> the manifest-backed p@3 = 0.84 at `evaluation/results/retrieval-2026-07-19/report.json`.
> Every code citation is `path:line` against the tree at merge `3baed4f`.

---

## 0. Reading guide

Answer-first, MECE by five work-streams. Each **sub-task** carries a fixed shape:
**Problem → Current state (cited) → Spec (interface + approach) → Validation (RED→GREEN) → Acceptance → Effort·Priority.**
Discipline is unchanged and non-negotiable: *a finding is closed only when its adversarial
regression test is RED on the unfixed tree and GREEN on the fixed tree.*

| Work-stream | Theme | Sub-tasks |
|---|---|---|
| **WS-A** | Perf & DoS at scale | A1–A8 |
| **WS-B** | Tokenizer & pricing fidelity (CODE-10) | B1–B4 |
| **WS-C** | Governance close-out | C1–C5 |
| **WS-D** | Memory/KB compounding | D1–D3 |
| **WS-E** | Independent re-grade & exit | E1–E2 |

---

## 1. Governing thought (SCQA)

- **Situation.** Waves 0–2 reconnected the retrieval stack, committed the hardening
  layer, and landed lifecycle/trust fixes. `main` now carries the honest p@3 = 0.84
  (no lift over keyword) and a withdrawn A+.
- **Complication.** Three classes of debt remain, and one "closed" item is mis-marked.
  (i) The system cannot honestly claim to work *at 10× scale* — the flagship graph and
  index paths are quadratic, and **ATK-DOS-01's PageRank O(N²) dangling loop is still
  live** (`src/graph/graph.py:401-411`) despite being tracked as "fixed / verify-only".
  (ii) On a **watsonx** deployment every token/cost number is computed against the wrong
  tokenizer and 2024 GPT prices, silently (CODE-10). (iii) The credibility differentiator
  is still self-asserted — the independent re-grade (CLM-02/R14) is owed, the gates have a
  bus-factor of 1 (ATK-GATE-07), and two whole-file escape hatches let outward-facing
  overclaims ship unscanned.
- **Question.** What is the shortest spec that lets Mnemox *prove* it compounds value at
  scale, computes honest economics on its actual target, and is graded by someone other
  than itself?
- **Answer (governing thought).** *Wave 3 is three provable claims and one handoff:
  **(1)** the hot paths are linearised and bounded, with a CI gate that fails on
  super-linear regression; **(2)** token/cost fidelity is model-correct with a loud
  fallback; **(3)** the honesty machinery is independently enforceable and the corpus is
  curated; and **(4)** a genuinely third-party re-grade replaces the self-verdict. Items
  1–3 are code Mnemox can close itself under RED→GREEN discipline; item 4 is the one thing
  it structurally cannot self-serve, and the spec treats it as a packaged handoff, not a
  self-run pass.*

---

## 2. Scope reconciliation — what Waves 0–2 already closed

The original remediation plan's Wave-3 list is **stale**. Verified against `git log` and
live code, the true state is:

| Finding | Plan said | **Verified reality** |
|---|---|---|
| ATK-DOS-02 (edge explosion) | Wave 3 | **CLOSED** W1/W2 — caps `src/graph/builder.py:290-308,51-52` |
| ATK-DOS-03 (L2 O(n) miss) | Wave 3 | **CLOSED** W1 — BLAS matmul `src/cache/semantic_cache.py:211-226` |
| ATK-DOS-04 (index growth) | Wave 3 | **PARTIAL** — reclamation done W2 (`src/embeddings/index.py:206-215`); **O(N²) `np.vstack` append residual** at `:140` |
| ATK-GATE-04 (research exempt) | Wave 3 | **CLOSED** W2 (`4fe2a0b`) for *dated* files — **banner hatch residual** (see C1) |
| ATK-GATE-01 (magnitude) | Wave 3 | **ACCEPTED** — composition guard added W1 (`src/validation/__init__.py:147-181`); magnitude gate deliberately absent (design decision, §6) |
| CODE-13 (L2 loop + metrics) | Wave 3 | **HALF** — L2 loop closed W1; metrics half = ATK-DOS-05 open |
| CLM-02 (self-A+) | Wave 3 | **HALF** — A+ withdrawn W1 (`STATUS.md:11`); **re-grade owed** (E1) |
| **ATK-DOS-01 (PageRank)** | "fixed, verify-only" | **⚠️ OPEN** — nested dangling loop unchanged `src/graph/graph.py:401-411`; the passing test only exercises the all-dangling one-iteration case |

**Net: the real Wave-3 open set** is CODE-10, CODE-16, ATK-DOS-01, ATK-DOS-05, ATK-DOS-06,
the ATK-DOS-04 append residual, the `build_semantic`/`index.search` quadratics (perf-at-scale,
CODE-13/16), ATK-GATE-07, the banner + precision-claim gate gaps, MEM-08, MEM-10, MEM-11,
MEM-12, MEM-13, and CLM-02/R14.

---

## 3. Priority (Impact × Effort)

| | **Low effort** | **High effort** |
|---|---|---|
| **High impact** | A6 ReDoS · C1 banner hatch · C2 precision gate · C5 grade-independence gate · A8 perf-scale gate | **A1 PageRank** · **A2 build_semantic** · **B1/B2 tokenizer+pricing** · **E1 independent re-grade** · **D3 foreign-repo demo** |
| **Low impact** | A5 metrics lock · C3 CODEOWNERS ref · A3 renorm | A4 L2 BLAS · A7 input bounds · D1 cold-start · D2 curation tier |

**Recommended order:** C1+C2+C5 (protect the honesty brand — cheap, first) → A1+A2+A3+A4+A7+A8
(scale) → A5+A6 → B1–B4 (watsonx economics) → D1+D2+D3 (compound demo) → C3+C4 → **E1/E2 last**
(re-grade only has meaning once the Critical/High set is closed).

---

## WS-A — Performance & DoS at scale

**Exit theme:** no attacker-reachable super-linear path on node/query/input growth, and a CI
gate that *fails a PR* on super-linear regression (today the only perf gate is a 50%-median
compare on `main` only — `.github/workflows/ci.yml:257-261`).

### A1 — PageRank dangling-mass hoist (ATK-DOS-01 / CODE-16) — **HIGH**

- **Problem.** Dangling-node score is redistributed with a nested `for ti in range(n)` inside
  a `for si in range(n)` — **O(D·N) per iteration**, up to O(100·N²) at `max_iter=100`.
  Measured 0.11→7.37 s at 250→2 000 nodes; extrapolated ~184 s/call @10k. A handful of
  planted link-less docs wedge every graph op.
- **Current state.** `src/graph/graph.py:401-411` (the nested loop), `:361-362`
  (`max_iter=100, tol=1e-6`). Test `tests/performance/test_dos_hardening.py:19-34` passes
  **only** because an all-dangling graph is already the uniform fixed point (converges in one
  iteration) — it does not exercise the quadratic.
- **Spec.** Standard dangling-mass aggregation. Per iteration: compute
  `dangling_mass = damping * Σ scores[si] for si where out_totals[si]==0` **once** (O(N)),
  then add `dangling_mass / n` to every node in a single O(N) pass; keep the O(E) weighted
  edge pass for non-dangling nodes. Net **O(N + E) per iteration**. No API change; result
  vector must be numerically identical (uniform redistribution is associative).
- **Validation (RED→GREEN).**
  - New `test_pagerank_mixed_dangling_scales_linear`: build a graph of N ∈ {1k, 2k, 4k} nodes
    where ~50 % are dangling **and** the rest form a chain that needs many iterations to
    converge; assert wall-time grows sub-quadratically (ratio t(4k)/t(1k) < 6, not ~16) and
    each call < 1.0 s at 4k. RED on current loop (times ~16×), GREEN after hoist.
  - `test_pagerank_result_unchanged`: on a fixed seeded graph, assert the new scores equal the
    old scores within 1e-9 (correctness-preservation).
- **Acceptance.** Both tests green; existing `test_pagerank_2000_dangling_nodes_under_1s` still
  green; ranker outputs (`tests/graph/`) unchanged.
- **Effort·Priority.** ~0.5 day · **HIGH** (mis-marked-closed, measured DoS).

### A2 — `build_semantic` similarity-loop bound (perf-at-scale, CODE-13/16) — **HIGH**

- **Problem.** For every one of N docs, `build_semantic` re-reads the file and runs a full
  `index.search` over the whole matrix → **O(N²·dim)**. The edge *caps* bound edges stored,
  not the similarity *cost*. Dominant cold-build cost; blocks any "10× KB" claim.
- **Current state.** `src/graph/builder.py:331-362` (loop; `index.search(content[:4000],
  top_k=50)` at `:349`). Edge caps at `:290-308` bound only output.
- **Spec.** Replace the per-doc full re-search with a **single batched top-k similarity pass**
  over the persisted index: (a) gather the per-document representative vectors already in the
  index (one vector per file, mean-pooled from its chunk rows — the index has them), forming
  `M ∈ [D × dim]`; (b) compute `S = M @ Mᵀ` once via BLAS (O(D²·dim) but vectorised, ~100×
  faster constant and no Python loop / no re-read / no re-embed); (c) for each row keep
  `top_k` above `min_similarity`, then apply the existing edge caps. Add a hard guard: if
  `D > _SEMANTIC_BUILD_MAX_DOCS` (config, default 5 000) switch to blocked/ANN mode or refuse
  with a loud log rather than silently melting. Reuses cached doc vectors — no second embed
  pass (removes the `content[:4000]` re-read at `:349`).
- **Validation (RED→GREEN).**
  - `test_build_semantic_no_full_rescan`: monkeypatch `index.search` to raise; assert
    `build_semantic` still produces edges (proves it no longer calls per-doc search). RED now
    (it calls search N times), GREEN after batching.
  - `test_build_semantic_scales_subquadratic`: build at D ∈ {500, 1 000, 2 000}; assert
    wall-time ratio t(2k)/t(500) < 10 (vectorised) and edges still obey caps.
  - `test_build_semantic_edges_identical_small`: on a 30-doc fixture, assert the produced edge
    set equals the current implementation's edge set (parity).
- **Acceptance.** Parity on small fixture; sub-quadratic scaling; caps still enforced
  (`tests/security/test_graph_poisoning.py` green).
- **Effort·Priority.** ~1–1.5 days · **HIGH**.

### A3 — `index.search` precompute norms + batched append (ATK-DOS-04 residual) — **MED**

- **Problem.** (i) `search()` recomputes `np.linalg.norm(matrix, axis=1)` **every query**
  (O(N·dim) wasted). (ii) `index_document()` appends one row via `np.vstack` → O(N²·dim) on a
  cold/full rebuild of the whole corpus.
- **Current state.** `src/embeddings/index.py:107-109` (per-query renorm), `:140` (per-row
  vstack), `:245` (rebuild slice).
- **Spec.** (i) Maintain a cached `_row_norms` vector, invalidated on any matrix mutation
  (append/drop/reconcile); `search` divides by the cached norms. (ii) Add a
  `rebuild()`-internal **batch path**: accumulate new rows in a Python list and do a single
  `np.vstack`/`np.concatenate` at the end of the rebuild rather than per-document; keep the
  single-doc `index_document` for incremental updates but route `rebuild` through the batch
  builder. On-disk format (`store.py:22-24`) unchanged.
- **Validation (RED→GREEN).**
  - `test_search_norms_cached`: spy on `np.linalg.norm`; assert it is **not** called on the
    second consecutive `search`. RED now, GREEN after caching.
  - `test_cold_build_subquadratic`: rebuild a 2 000- vs 500-chunk KB; assert time ratio < 8.
  - `test_norm_cache_invalidated_on_mutation`: after `index_document`, a subsequent `search`
    returns correct top-1 for the new doc (guards a stale-norm bug).
- **Acceptance.** Cache-correctness tests green; existing `tests/embeddings/` green.
- **Effort·Priority.** ~0.5 day · **MED**.

### A4 — L2 semantic-cache BLAS + O(1) eviction (CODE-13 / ATK-DOS-03 residual) — **MED**

- **Problem.** The `find_similar`/`get_with_similarity` paths still use the **non-BLAS Python
  cosine loop**; each miss re-`np.stack`s the whole matrix; `_evict_lru` is O(N) `min(...)`.
- **Current state.** `src/cache/semantic_cache.py:224` (full `np.stack` per miss), `:435`
  (O(N) eviction), `:570,614` (Python cosine). Note the *hot* `find`/lookup path was already
  BLAS-ified at `:211-226` in W1 — this is the residual on the auxiliary similarity APIs.
- **Spec.** (i) Route `find_similar`/`get_with_similarity` through the same
  `matrix @ query` BLAS path used at `:211-226`; keep a persistent `_matrix` maintained on
  insert/evict instead of re-stacking per call. (ii) Replace the O(N) LRU with an
  `OrderedDict` + `move_to_end`/`popitem(last=False)` (the pattern L1 already uses at
  `src/cache/exact_cache.py:196,284,305`) for O(1) eviction.
- **Validation (RED→GREEN).**
  - `test_find_similar_uses_persistent_matrix`: spy on `np.stack`; assert it is **not** called
    per query on the similarity path.
  - `test_l2_eviction_o1`: fill to `l2_max_size`, then time 1 000 evicting inserts; assert
    near-constant per-insert (ratio at 2× size < 1.5×).
  - Parity: `test_find_similar_results_unchanged` on a fixed fixture.
- **Acceptance.** BLAS + O(1) evict proven; existing cache concurrency suite green under
  `-p no:randomly` repetition (guards the W2 race fix).
- **Effort·Priority.** ~0.75 day · **MED**.

### A5 — Metrics percentile out-of-lock (ATK-DOS-05) — **LOW**

- **Problem.** Every recorded hit does `sorted(self.recent)` **inside the stats lock** →
  throughput ceiling under load.
- **Current state.** `src/monitoring/metrics.py:38-40`.
- **Spec.** Record raw samples under the lock (O(1) append to a bounded ring buffer, e.g.
  `deque(maxlen=W)`); compute percentiles **lazily on read**, outside the write lock, from a
  snapshot copy. Percentiles become eventually-consistent (acceptable for a metrics view).
- **Validation.** `test_metrics_record_no_sort`: spy on `sorted`; assert not called on
  `record()`, only on `percentile()`/`snapshot()`. `test_metrics_percentiles_correct`: values
  match a reference computation. `test_metrics_throughput`: 100k records complete under a
  wall-time bound (informational).
- **Acceptance.** Sort off the write path; percentile values correct.
- **Effort·Priority.** ~0.25 day · **LOW**.

### A6 — ReDoS hardening (ATK-DOS-06) — **HIGH-value / LOW-effort**

- **Problem.** Frontmatter/link/heading regexes are "one refactor away from an exponential
  hang"; no input-size cap or timeout on regex application; whole files are read unbounded.
- **Current state.** `src/graph/builder.py:41` (`_FM_TAGS_INLINE_RE`), `:32-45`;
  `src/tools/kb_query.py:47-54,488`. Whole-file reads at `kb_query.py:265-266`,
  `builder.py:224`, `index.py:174`.
- **Spec.** (i) Cap the substring the frontmatter/inline regexes ever see (frontmatter block
  is already delimited — bound it to, e.g., the first 8 KB / first `---…---` block; reject
  documents whose frontmatter block exceeds a config ceiling with a loud parse warning).
  (ii) Add a shared `safe_search(pattern, text, *, max_len)` helper in a small
  `src/text_safety.py` that truncates `text` to `max_len` before matching and is used by all
  frontmatter/link parsers. (iii) Audit each pattern for nested quantifiers; where present,
  rewrite to a linear form (possessive/atomic or explicit character classes).
- **Validation (RED→GREEN).**
  - `test_redos_frontmatter_bounded` (mark `planted_defect`): feed a pathological
    `tags: [` + `a,`×10 000 (or a nested-quantifier trigger) and assert parse returns within a
    hard time budget (e.g. < 100 ms) via `pytest-timeout` / a wall-clock assert. RED if a
    naive refactor is introduced, GREEN with the size cap.
  - `test_oversize_frontmatter_rejected_loudly`: a 5 MB frontmatter block yields a logged
    warning and an empty/So-flagged parse, not an OOM.
- **Acceptance.** No unbounded regex input anywhere in the parse paths; time-bound tests green.
- **Effort·Priority.** ~0.5 day · **HIGH-value** (cheap insurance on the honesty/uptime story).

### A7 — Global input bounds (DoS surface hardening) — **MED**

- **Problem.** No cap on per-file size, chunks-per-document, node count, or query length; a
  single crafted large doc (or one with tens of thousands of `##` headings) inflates memory
  and feeds the O(N²) builds.
- **Current state.** Whole-file reads (`kb_query.py:265`, `builder.py:224`, `index.py:174`);
  chunker has a min-size floor but **no ceiling** (`src/embeddings/chunker.py:104-124,120`);
  no `MAX_NODES` in graph build.
- **Spec.** Central `config/limits.yaml` (or a `src/limits.py` single home) with:
  `MAX_FILE_BYTES` (e.g. 1 MB), `MAX_CHUNKS_PER_DOC` (e.g. 500), `MAX_QUERY_CHARS`
  (e.g. 4 096), `MAX_GRAPH_NODES` (e.g. 20 000). Enforce at ingest (skip+warn oversized files),
  in the chunker (cap emitted chunks + warn), and at query entry (truncate + warn). All limits
  single-homed and asserted by `check_value_homes.py`.
- **Validation (RED→GREEN).**
  - `test_oversized_file_skipped`: a > `MAX_FILE_BYTES` file is skipped with a warning, index
    build still completes.
  - `test_chunks_per_doc_capped`: a doc with 5 000 headings yields ≤ `MAX_CHUNKS_PER_DOC`.
  - `test_query_length_capped`: a 1 MB query string is truncated, not embedded whole.
- **Acceptance.** All three green; limits registered in value-homes.
- **Effort·Priority.** ~0.75 day · **MED**.

### A8 — Perf-regression gate that fails a PR (governance of WS-A) — **HIGH-value**

- **Problem.** The only automated perf gate is a 50 %-median-regression compare **on `main`
  only**; `test_dos_hardening.py` runs in the coverage job (hard asserts) but there is no
  *scaling* gate on PRs, so a re-introduced quadratic passes CI until it hits `main`.
- **Current state.** `.github/workflows/ci.yml:222-264` (benchmark job, `--benchmark-only`,
  compare-fail `median:50%` at `:257-261`, main-only at `:257`). `test_dos_hardening.py`
  asserts run in the `test` job (`ci.yml:57-59`).
- **Spec.** Add a `scale-guard` pytest module `tests/performance/test_scale_invariants.py`
  (runs in the normal `test` job, not `--benchmark-only`) that encodes the WS-A ratios as hard
  assertions: PageRank t(4k)/t(1k) < 6; `build_semantic` t(2k)/t(500) < 10; cold index build
  t(2k)/t(500) < 8; L2 evict ratio < 1.5. Ratios (not absolutes) so they survive shared-runner
  noise. Document the thresholds in `config/gates/gate-config.yaml` under a new `perf_scale`
  block so a weakening is conspicuous (ties into ATK-GATE-07 review routing).
- **Validation.** Meta-test `tests/gates/test_scale_gate_selftest.py`: temporarily monkeypatch
  a function to be quadratic and assert the scale-guard **fails** (gate really bites) — the
  same self-test discipline the honesty gates use.
- **Acceptance.** Scale gate green on fixed tree, RED on an injected quadratic; wired into CI
  `test` job.
- **Effort·Priority.** ~0.5 day · **HIGH-value** (makes WS-A durable).

---

## WS-B — Tokenizer & pricing fidelity (CODE-10)

**Exit theme:** token counts and costs are computed against the *actual* target model, and any
fallback is **loud**. Especially load-bearing because this is a **watsonx** submission —
today every economics figure is silently computed against GPT-4/tiktoken.

### B1 — Multi-backend tokenizer with loud fallback — **HIGH**

- **Problem.** `TokenCounter` hardcodes `tiktoken.encoding_for_model`; an unknown model id
  (any Claude/Granite/watsonx id) raises `KeyError`, is **silently** caught, and degrades to a
  `words + special/2` heuristic with no signal.
- **Current state.** `src/optimizer/token_counter.py:38-46` (silent `except (ImportError,
  KeyError)`), `:71` (`encode`), `:97-118` (approx), `:251-257` (truncation heuristic). The
  only existing "loud" precedent is the validation gate at `src/validation/__init__.py:203-204`.
- **Spec.** Introduce a backend-resolution layer, single-homed in `token_counter.py`:
  - `resolve_tokenizer(model) -> Tokenizer` dispatching on a model→family map:
    `gpt*/o1* → tiktoken`; `claude* → anthropic token counter` (use the Anthropic SDK
    `count_tokens` if available, else a documented, versioned BPE approximation table for
    Claude flagged `approx=True`); `granite*/watsonx* → a Granite/HF tokenizer if the optional
    dep is installed, else `approx=True`).
  - A `Tokenizer` protocol: `.count(text) -> int`, `.exact: bool`, `.name: str`.
  - **Loud fallback contract:** when resolution yields an approximation, emit **exactly one**
    `logging.warning` per (process, model) — "tokenizer for '<model>' unavailable; counts are
    a ±X% approximation, not exact" — and set a `TokenCounter.approximate: bool` flag that
    propagates into the validation manifest (`tiktoken_active` generalises to
    `tokenizer_exact`). Never raise on the hot path (availability is deployment-dependent), but
    make the degradation observable and manifest-visible so no *published* number rides on a
    silent approximation.
  - Optional deps declared as extras (`pip install mnemox[watsonx]`, `[anthropic]`); resolution
    degrades gracefully when absent (that's the whole point of the loud path).
- **Validation (RED→GREEN).**
  - `test_unknown_model_warns_once`: `caplog` asserts exactly one warning for a
    `granite-3-8b` id; second construction with same id does not re-warn. RED now (silent),
    GREEN after.
  - `test_tokenizer_exact_flag`: `gpt-4` → `exact=True`; `granite-*` without the extra →
    `approximate=True`.
  - `test_claude_backend_selected` / `test_granite_backend_selected` (skipped if extra absent):
    the right backend is chosen and counts differ from the tiktoken heuristic.
  - `test_manifest_carries_tokenizer_exact`: a validation run on a non-GPT model records
    `tokenizer_exact=False` and the gate blocks publication (extends
    `src/validation/__init__.py:203-204`).
- **Acceptance.** Loud, once-per-model warning; manifest-visible; validation gate blocks a
  published number computed on an approximation.
- **Effort·Priority.** ~1.5 days · **HIGH**.

### B2 — Real per-model price tables (input/output split) — **HIGH**

- **Problem.** `USD_PER_1K_TOKENS` has only 4 GPT models at a **flat** per-1K rate (no
  input/output split); an unknown model silently prices at the **gpt-4 rate**.
- **Current state.** `src/pricing.py:18,22-27,30,37-43` (`usd_cost` `.get(model,
  DEFAULT_USD_PER_1K)` at `:42`). Bobcoin is flat/model-independent at `:33-34`.
- **Spec.** Extend the single home `src/pricing.py`:
  - Replace the flat map with `PRICES: dict[str, ModelPrice]` where
    `ModelPrice = {input_per_1k, output_per_1k, currency, as_of_date, source_url}`. Add
    watsonx Granite and Claude entries alongside GPT (values cited to a dated source in the
    frontmatter/comment; treat as *list prices*, clearly dated).
  - `usd_cost(input_tokens, output_tokens, model)` — split-aware; **unknown model raises or
    returns a loud sentinel**, not a silent GPT-4 fallback (align with B1's contract:
    unknown-model pricing is a publish-blocking condition, not a guess).
  - Keep Bobcoin as the internal unit but document its USD anchor per model so the two aren't
    silently decoupled.
- **Validation (RED→GREEN).**
  - `test_unknown_model_price_is_loud`: `usd_cost(...,"granite-x")` warns/raises rather than
    returning the gpt-4 rate. RED now, GREEN after.
  - `test_price_table_has_dates`: every `ModelPrice` carries `as_of_date` + `source_url`
    (guards stale silent prices).
  - `test_input_output_split`: input vs output priced differently for a model that has a split.
  - `test_pricing_single_home`: `check_value_homes.py` still passes; no price literal outside
    `src/pricing.py`.
- **Acceptance.** Split-aware, dated, single-homed, loud on unknown model.
- **Effort·Priority.** ~0.75 day · **HIGH**.

### B3 — Unify the delegation `//4` counting home — **MED**

- **Problem.** Six delegation agents count tokens as `len(str(...)) // 4`, bypassing
  `TokenCounter` entirely — a parallel, model-blind counting home that feeds reported totals.
- **Current state.** `src/delegation/agents/*.py` (`architecture_agent.py:80`,
  `documentation_agent.py:119`, `performance_agent.py:83`, `quality_agent.py:87`,
  `research_agent.py:127`), `security_agent.py:190-195` (`_estimate_tokens`), summed at
  `src/delegation/base.py:43,190`.
- **Spec.** Inject the shared `TokenCounter` into `DelegationAgent` (constructor or a
  module-level accessor) and replace every `//4` with `self.token_counter.count_tokens(...)`.
  Where a fast approximation is genuinely wanted (large intermediate blobs), call
  `TokenCounter` in its explicit `approximate=True` mode so the flag propagates rather than a
  hidden `//4`.
- **Validation.** `test_delegation_uses_token_counter`: monkeypatch `TokenCounter.count_tokens`
  to a sentinel; assert each agent's reported `token_count` routes through it (no `//4`
  literal remains — add a `test_no_div4_literal` grep-style guard over `src/delegation/`).
- **Acceptance.** Single counting home; delegation totals are model-correct.
- **Effort·Priority.** ~0.5 day · **MED**.

### B4 — Docs & economics reconciliation — **LOW**

- **Spec.** Update `docs/` economics language to state which tokenizer/prices back each figure;
  where a number was computed on GPT-4/tiktoken but the deployment is watsonx, label it
  accordingly or recompute. No bare savings % without a manifest citation (gate rule).
- **Validation.** `check_savings_claims.py` + `check_value_homes.py` green after edits.
- **Effort·Priority.** ~0.25 day · **LOW**.

---

## WS-C — Governance close-out

**Exit theme:** the honesty machinery catches outward-facing overclaims (not just savings
lines), is enforceable by more than one person, and cannot bless a self-conferred grade.

### C1 — Close the banner escape hatch (research-exemption residual) — **HIGH-value / LOW-effort**

- **Problem.** The mnemox overclaim shipped unscanned not via the dated-filename exemption
  (ATK-GATE-04 narrowed that) but via the **banner exception**: a `HISTORICAL SNAPSHOT` line
  in the head makes `scan_text` short-circuit to `[]` for the **whole file**, regardless of
  content or the doc's `status`.
- **Current state.** `scripts/check_savings_claims.py:129-138` (`BANNER_MARKERS`),
  `:147-151` (`has_banner`), `:226-227` (`if has_banner(text): return []`), `:249-255`
  (`_is_excluded` dated-file predicate). The exempted file is
  `docs/knowledge-base/research/mnemox-challenge-submission-2026-07.md` (frontmatter
  `status: active`, audience `challenge-judges`).
- **Spec.** Two changes:
  1. **A banner suppresses per-line flags only when the file is genuinely frozen.** Gate the
     banner short-circuit on frontmatter `status` ∈ {`superseded`, `archived`, `historical`}
     **and** a dated filename. An `active`/outward-facing doc with a banner is **still scanned**
     — the banner stops being a universal mute.
  2. **Even a frozen doc must still carry per-figure backing or an explicit retraction token on
     the claim line** (downgrade the whole-file skip to a per-line "backed-or-retracted"
     requirement). This preserves audit-trail docs while forbidding a live outward claim from
     hiding behind "HISTORICAL".
- **Validation (RED→GREEN).**
  - `test_active_doc_with_banner_is_scanned`: a `status: active` file with a `HISTORICAL
    SNAPSHOT` banner **and** an unbacked `60% reduction` line is **flagged**. RED now (banner
    mutes it), GREEN after.
  - `test_frozen_snapshot_requires_per_line_backing`: a `status: superseded` dated file with an
    unbacked savings line is flagged unless the line carries a manifest citation or a retraction
    token.
  - `test_gate_selftest_c1` in `tests/gates/`: the meta-test proving the new predicate bites.
- **Acceptance.** No `status: active` surface can mute the savings gate with a banner; frozen
  docs still exempt at the *file* level but gated at the *line* level.
- **Effort·Priority.** ~0.5 day · **HIGH-value** (this is the exact hole the last defect used).

### C2 — Precision/accuracy claim gate (new predicate) — **HIGH-value**

- **Problem.** The savings gate only fires on lines with a `SAVINGS_KEYWORDS` token; a
  retrieval/precision overclaim (the withdrawn "p@3 88 %", accuracy, recall, uplift) contains
  no savings keyword and is **structurally invisible** to every current gate. That is exactly
  why the withdrawn 88 % rode along until hand-corrected.
- **Current state.** `scripts/check_savings_claims.py:75-83` (`SAVINGS_KEYWORDS`),
  `:198-212` (`line_is_unbacked_claim` requires a savings keyword). No metric-claim gate exists.
- **Spec.** Add a sibling gate `scripts/check_metric_claims.py` (or a second predicate in the
  savings gate) covering `METRIC_KEYWORDS = {precision, recall, p@, accuracy, f1, uplift, ndcg,
  hit-rate}` + a numeric/percentage. A metric claim on a **live** surface must co-locate a
  manifest/report citation (e.g. `evaluation/results/.../report.json`) or a retraction token,
  mirroring the savings-line contract. Register it in `config/gates/gate-config.yaml` and wire
  it into CI next to the savings gate.
- **Validation (RED→GREEN).**
  - `test_unbacked_precision_claim_flagged`: `p@3 uplift 44% → 88%` with no report citation is
    flagged. RED (no such gate today), GREEN after.
  - `test_backed_precision_claim_passes`: the same line with
    `evaluation/results/retrieval-2026-07-19/report.json` present passes.
  - Self-test in `tests/gates/`.
- **Acceptance.** Precision/accuracy overclaims are gated on live surfaces; the honesty
  machinery no longer has a metric-shaped blind spot.
- **Effort·Priority.** ~0.75 day · **HIGH-value**.

### C3 — Gate-reviewer independence + fix dangling ref (ATK-GATE-07) — **MED**

- **Problem.** `@davidleconte` authors code, authors the gates that check it, and is the sole
  required approver to weaken them — bus-factor 1. The `CODEOWNERS` comment promises a
  `SECURITY.md §Gate Independence` sink that **does not exist**.
- **Current state.** `.github/CODEOWNERS:6,9-13,16,21-24` (all `@davidleconte`; the self-aware
  gap note at `:21-24`); `SECURITY.md` has no `§Gate Independence`.
- **Spec.** Three moves, in ascending strength (pick per what the project can staff):
  1. **Structural CI check (staff-free, do this regardless):** a `gate-integrity` CI job that
     **fails any PR whose diff touches both a gate definition (`config/gates/**`,
     `scripts/check_*.py`, `src/validation/**`) and a claim surface (`STATUS.md`, `README.md`,
     `docs/**`) in the same PR** — mechanically forbids the "weaken the gate + plant the claim"
     single-PR attack ATK-GATE-07 names, without needing a second human.
  2. **Add the missing `SECURITY.md §Gate Independence`** section documenting the single-owner
     status, the structural check above, and the standing invitation for an external reviewer;
     repoint the `CODEOWNERS` comment to it.
  3. **(If staffable) a second `CODEOWNERS` entry** for `config/gates/**` +
     `scripts/check_*.py` naming an independent reviewer; until then the structural check is the
     honest substitute and is *disclosed as such*.
- **Validation (RED→GREEN).**
  - `test_gate_integrity_blocks_mixed_pr` (meta / CI-script unit test): a simulated diff
    touching both a gate and `STATUS.md` fails the check; a gate-only or claim-only diff passes.
  - `test_security_md_has_gate_independence_section`: `SECURITY.md` contains
    `## Gate Independence` and `CODEOWNERS` no longer dangles.
- **Acceptance.** The single-PR gate-and-claim attack is mechanically blocked and the residual
  single-owner risk is *disclosed*, not silently accepted.
- **Effort·Priority.** ~0.75 day · **MED**.

### C4 — Magnitude-gate decision (ATK-GATE-01) — **decision, then LOW**

- **Problem/state.** A magnitude gate is **deliberately absent** ("gating a measurement
  re-incentivises fabrication"), replaced by a composition guard
  (`src/validation/__init__.py:147-181`: `MIN_CORPUS_N=30`, `MAX_TOP_DOC_TOKEN_SHARE=0.5`,
  `MAX_MEAN_MEDIAN_DIVERGENCE_PP=15`). The counter-audit's cherry-pick attack inflated the
  headline while the null stayed clean.
- **Spec (recommended).** Do **not** add a magnitude ceiling. Instead add a **held-out corpus**
  check: publish the number on corpus A but require it to reproduce within a tolerance band on a
  frozen, independently-composed hold-out corpus B (`evaluation/holdout/`), so a cherry-picked A
  can't survive. This attacks the cherry-pick without penalising an honest high number. (See §6
  decision.)
- **Validation.** `test_holdout_divergence_blocks_publish`: a headline computed on a
  cherry-picked corpus that diverges > tolerance on the hold-out is blocked; an honest number
  that reproduces passes.
- **Effort·Priority.** ~1 day if adopted · **MED** (gated on the §6 decision).

### C5 — Grade-independence gate (CLM-02, mechanical half) — **HIGH-value / LOW-effort**

- **Problem.** `check_status_consistency.py` validates only the *arithmetic* of a grade token
  (letter matches number, ≤ 4.30). A syntactically valid **self-conferred** `A+ (4.30/4.30)`
  passes cleanly — the gate cannot tell a self-grade from an independent one.
- **Current state.** `scripts/check_status_consistency.py:74` (`_GRADE_RE`), `:141-176`
  (`_validate_grade`, arithmetic only), `:70,343-350` (canonical-string requirement). Prose
  discipline (`STATUS.md:11` withdrawal) is not gate-enforced.
- **Spec.** Extend the status gate: any live grade token in `LIVE_DOCS` must be accompanied on
  an adjacent line by a **provenance tag** — `grader:` (independent identity), `method:`, and a
  citation to a committed re-grade artifact under `evaluation/regrade/` — **or** be explicitly
  marked `self-assessed`/`withdrawn`. A bare `**A+ (4.30/4.30)**` with no provenance and no
  self-label **fails**. This makes the E1 re-grade the *only* way to state a live grade, and
  hard-blocks a future silent self-A+.
- **Validation (RED→GREEN).**
  - `test_unprovenanced_grade_fails`: a bare `**A+ (4.30/4.30)**` in a live doc fails. RED now
    (arithmetic-valid → passes), GREEN after.
  - `test_self_labeled_grade_passes`: `**A+ (4.30/4.30)** (self-assessed, withdrawn)` passes.
  - `test_independent_grade_passes`: a grade with `grader:/method:/evaluation/regrade/...`
    passes.
- **Acceptance.** No live, unprovenanced, un-self-labeled grade can exist; the E1 artifact is
  the sanctioned path.
- **Effort·Priority.** ~0.5 day · **HIGH-value**.

---

## WS-D — Memory/KB compounding

**Exit theme:** the system's own map is cheap, its corpus is curated, and the
write→retrieve→compound loop is *demonstrated* on a foreign repo — the headline Horizon-3 proof.

### D1 — Compact cold-start index (MEM-08) — **MED**

- **Problem.** Cold start auto-loads a large map; the read path does **not** auto-build a
  missing index and silently degrades to keyword-only; the index double-lists docs and never
  prunes "Recent Additions".
- **Current state.** `src/cli.py:373` (index wired only `if exists()`, else keyword-only);
  `_ensure_loaded` `src/embeddings/index.py:374-401`; `kb-search --refresh` `cli.py:380-393`
  (manual only). A committed compact snapshot analog already exists: `.bob/kb-index-st/`
  (1.7 MB, git-tracked) vs the live `.bob/kb-index/` (6.2 MB, gitignored).
- **Spec.** (i) **First-query auto-build**: when `resolve_index_path` is absent, `kb-search`
  builds a compact index once (bounded by A7 limits) instead of silently going keyword-only —
  with a one-line "building index (first run)…" notice. (ii) **Compact cold-start map**: cap
  "Recent Additions" at 10, remove the double-listing in the auto-index generator, and target a
  cold-start token budget (`< 3k` tokens for the auto-loaded map). (iii) **Regression metric**:
  add the cold-start token count to `kb-status` and gate it in CI (fail if it grows past the
  budget) — the "system built to save tokens shouldn't spend five figures mapping itself".
- **Validation (RED→GREEN).**
  - `test_missing_index_autobuilds`: with no `.bob/kb-index`, `kb-search` builds and returns
    index-backed results (not keyword fallback). RED now, GREEN after.
  - `test_cold_start_map_under_budget`: the generated auto-index map is < budget tokens and
    lists each doc once; "Recent Additions" ≤ 10.
  - `test_cold_start_budget_gate`: CI meta-test fails if the map exceeds budget.
- **Acceptance.** No silent keyword degradation on first run; bounded, single-listed cold map;
  budget gated.
- **Effort·Priority.** ~1 day · **MED**.

### D2 — Curation / archive tier (MEM-10/11/12) — **MED**

- **Problem.** The trust-tier spine works (`verified`/`quarantined`/`generated`) but there is
  **no `archived` tier, no `generated→verified` promotion path**, the `add_trust_tier.py`
  migration is effectively un-run (**1 of 116** files tagged), 70/116 docs are the research
  tier (the system documenting itself), lessons "new-doc" detection uses **mtimes** (false
  deltas, MEM-10), and the correction loop lacks verification (MEM-11).
- **Current state.** Enforcement: `src/tools/kb_query.py:70-72,268-269,361-362`;
  `src/graph/builder.py:56,271-288`; provenance `src/provenance.py:3,35`. Migration
  `scripts/add_trust_tier.py:34-60,80-99`. No `archive/` dir; `docs/knowledge-base/` has only
  concepts/guides/references/research.
- **Spec.**
  1. **Run the migration** (`add_trust_tier.py` over the whole KB) so every doc carries an
     explicit tier; commit the result.
  2. **Add an `archived` tier** (frontmatter `trust_tier: archived` and/or a `research/archive/`
     move) that is **excluded from the retrieval set** (extend the `kb_query` tier filter) but
     preserved on disk — so marketing/process artifacts (MEM-12) stop polluting retrieval
     without being deleted.
  3. **Promotion workflow**: a `bob-optimize kb-promote <doc> --to verified` command that
     re-signs provenance (`src/provenance.py`) and records the promoter — the `generated→verified`
     path that today doesn't exist.
  4. **MEM-10 fix**: replace mtime-based change detection in the lessons loop with the
     content-hash mechanism the index already uses (`store.py` manifest hashes) — no false
     deltas on touch.
  5. **MEM-11 fix**: the correction loop must run `validate-kb.sh` (now exit-1 on broken links)
     **after** any pointer rewrite and fail if it introduced a break — closing the
     "unverified correction" root cause.
- **Validation (RED→GREEN).**
  - `test_all_kb_docs_have_trust_tier`: 0 untagged docs after migration (RED: 115 untagged now).
  - `test_archived_tier_excluded_from_retrieval`: an `archived` doc never appears in
    `kb-search` results but stays on disk.
  - `test_promote_resigns_provenance`: promotion flips the tier and yields a valid HMAC
    signature naming the promoter.
  - `test_lessons_detection_hash_not_mtime`: touching a file (mtime bump, content identical)
    produces **no** delta.
  - `test_correction_loop_verifies`: a pointer rewrite that breaks a link is caught by the
    post-rewrite `validate-kb.sh` and blocks.
- **Acceptance.** Curated retrieval set, working promotion, hash-based deltas, verified
  correction loop.
- **Effort·Priority.** ~1.5 days · **MED**.

### D3 — Foreign-repo write→retrieve→compound demo (MEM-13) — **HIGH**

- **Problem.** The compounding loop is **wired** (ResearchAgent retrieves prior KB findings
  first, agents write signed `generated` docs) but (a) `resolve_within(cwd, …)` **structurally
  forbids** analyzing a repo outside cwd, and (b) there is **no reproducible two-session demo**
  showing session-2 retrieval surfacing session-1's findings — the one live example is
  **retracted**. This is the headline "prove it compounds" deliverable and it is currently
  un-evidenced.
- **Current state.** `analyze_and_ingest` `src/cli.py:572-587`→`src/delegation/pipeline.py:79-248`;
  cwd containment `pipeline.py:112-116` + `src/tools/safe_paths.py:24-39`; ResearchAgent
  retrieval `src/delegation/agents/research_agent.py:47-72`, runs first `pipeline.py:129-142`;
  retracted example `evaluation/live-example-hcd-analysis.md:5-7`.
- **Spec.**
  1. **Opt-in foreign-repo analysis (safe):** add `--allow-external <path>` to
     `bob-optimize analyze` that permits an explicitly-named absolute path outside cwd, still
     routed through `safe_paths` containment **relative to the named external root** (no `../`
     escape beyond it), reads-only, and refuses symlink escapes. Preserves the security posture
     while unblocking the genuine use case.
  2. **Reproducible two-session compound demo** as a committed, CI-exercised artifact
     (`examples/compound-demo/`): session 1 analyzes a small pinned foreign fixture repo (vendored
     under `examples/compound-demo/fixture-repo/` at a fixed commit) → writes `generated` KB docs;
     session 2 issues a query that **must** retrieve a session-1 finding; the demo asserts the
     retrieved doc id equals the session-1 output id. Manifest-backed (record chunk counts,
     ids), so the compounding claim is reproducible, not anecdotal.
  3. **Replace the retracted example** reference in docs with this reproducible demo; keep the
     retracted file frozen with its retraction banner.
- **Validation (RED→GREEN).**
  - `test_external_repo_opt_in_contained`: `--allow-external /tmp/foo` analyzes it;
    `../etc/passwd` and symlink escapes are refused. RED now (all external refused), GREEN after.
  - `test_compound_demo_session2_retrieves_session1` (the headline test): run the two-session
    fixture end-to-end; assert session-2 top-k contains the session-1 finding id. This is the
    reproducible proof MEM-13 asks for.
  - `test_compound_demo_manifest`: the demo emits a manifest (ids, counts, code SHA).
- **Acceptance.** Foreign repos analyzable under containment; a CI-run demo proves cross-session
  compounding with a manifest; retracted anecdote no longer the evidence.
- **Effort·Priority.** ~2 days · **HIGH** (the Horizon-3 headline).

---

## WS-E — Independent re-grade & exit (CLM-02 / R14)

### E1 — Independent re-grade (the one Mnemox cannot self-serve) — **HIGH**

- **Problem.** Every grade increment (D− → A+) was produced by the same agentic lineage doing
  the remediation. The A+ is withdrawn (`STATUS.md:11`) but no independent verdict has replaced
  it; the acceptance criterion is a committed re-grade artifact with grader identity, method,
  and per-dimension scores.
- **Current state.** Owed action documented at
  `docs/knowledge-base/research/counter-audit-2026-07-19-independent.md:219,276`; consulting
  review `docs/consulting/engineering-soundness-review-2026-07-19.md:84`. Precondition R13
  (committed p@3 golden set) **landed** in W2 — R14 is unblocked.
- **Spec (design a package, not a self-pass).** Produce
  `evaluation/regrade/regrade-kit-2026-07.md` containing: the rubric (the two scorecards +
  dimensions), the finding register with the closed/accepted status per Wave, the manifests
  (validation + retrieval), and a **grader worksheet** with empty per-dimension score cells and
  a provenance block (`grader:`, `method:`, `date:`, `commit:`). Then **hand it to a genuinely
  independent grader** — a human third party **or** an external agentic process with **no
  remediation involvement and a distinct model/lineage** — and commit their filled verdict as
  `evaluation/regrade/verdict-<date>.md`. **Explicitly: a re-grade run by this
  session/lineage does not discharge R14** (same-lineage objection); the spec's job is the kit
  + the handoff, and the C5 gate refuses to let any grade go live until a provenanced verdict
  exists.
- **Validation.** `test_regrade_kit_complete`: the kit contains rubric + register + manifests +
  worksheet with a provenance block. `test_status_cites_regrade_when_present`: once a
  `verdict-*.md` exists, `STATUS.md` cites it and the C5 grade-provenance gate passes.
- **Acceptance.** Kit committed; verdict slot defined and gate-enforced; **no self-run grade is
  presented as independent.**
- **Effort·Priority.** ~1 day to build the kit (+ external turnaround) · **HIGH**.

### E2 — Wave-3 exit gate — **governance**

- **Spec.** Wave 3 is closed when: (a) every WS-A/B/C/D sub-task's RED→GREEN tests are green in
  CI on 3.11 + 3.12; (b) the new scale gate (A8), C1/C2/C3/C5 gate self-tests, and the compound
  demo (D3) run in CI; (c) full suite green ex load/perf, coverage ≥ 80 % + per-package floors;
  (d) the E1 kit is committed and the grade-provenance gate is live; (e) every remaining
  Critical/High is closed or **explicitly accepted with a dated rationale** in a Wave-3 status
  doc. ATK-DOS-01 must be re-verified with the *mixed*-dangling test (A1), not the
  all-dangling one.
- **Acceptance.** A single `docs/project-management/plans/wave3-status.md` mapping every
  finding → closed/accepted with commit + test citation, mirroring the Wave-2 close-out.

---

## 5. Sequencing & dependencies

```
Phase 1 (honesty brand, cheap, first):   C1 → C2 → C5           [protect before proving]
Phase 2 (scale):                         A1 ∥ A2 ∥ A3 ∥ A4 → A7 → A5 → A6 → A8
Phase 3 (watsonx economics):             B1 → B2 → B3 → B4
Phase 4 (compound proof):                D1 → D2 → D3
Phase 5 (governance staffing + exit):    C3 → C4(if adopted) → E1 → E2
```

- **A8 depends on** A1–A4 (it encodes their ratios).
- **C5 depends on** E1's artifact schema (grade provenance points at `evaluation/regrade/`).
- **D3 depends on** A7 (input bounds) + D1 (auto-build) so the demo runs on a bounded, self-building index.
- **E1 must be last** — a re-grade before the Critical/High set is closed grades a moving target.

---

## 6. Open design decisions (resolve before Phase 2/5)

1. **Magnitude gate (C4 / ATK-GATE-01).** Keep the "no magnitude ceiling" stance (composition
   guard only), **or** add a held-out-corpus reproduction check.
   **Recommendation: add the hold-out (C4).** It defeats the cherry-pick attack the counter-audit
   demonstrated *without* re-incentivising fabrication — consistent with the honesty brand.
2. **Gate-reviewer staffing (C3 / ATK-GATE-07).** Structural CI check only (staff-free), **or**
   also onboard a second `CODEOWNERS` reviewer.
   **Recommendation: ship the structural `gate-integrity` check now regardless** (it blocks the
   single-PR attack mechanically); pursue a second human reviewer opportunistically and *disclose*
   the residual until then. Do not present single-owner gates as independently enforced.

---

## 7. Master validation plan & exit criteria

- **Per-finding:** RED-on-unfixed / GREEN-on-fixed recorded (which hunk reverted, which test
  flipped) — including the **mixed-dangling** PageRank test for the mis-marked ATK-DOS-01.
- **System gates (fixed, committed tree):** full `pytest` (ex load/perf) green on 3.11 + 3.12;
  `--cov=src` ≥ 80 % + per-package floors; ruff + mypy + bandit; `validate-kb.sh` exit 0 on
  ubuntu; `python -m src.validation` (null + manifest + tokenizer-exact) exit 0; `pip-audit`;
  savings + status + value-homes + **new metric-claim (C2)** + **grade-provenance (C5)** +
  **scale (A8)** gates and their `tests/gates/` self-tests.
- **Scale proof:** the A8 ratios hold; `build_semantic` and PageRank are sub-quadratic on the
  synthetic 4k-node fixture.
- **Economics proof:** a validation run on a non-GPT model records `tokenizer_exact=False` and
  is publish-blocked; GPT and (if extras present) Claude/Granite counts differ measurably.
- **Compound proof:** the D3 two-session demo retrieves session-1's finding in session 2, with a
  manifest.
- **Governance close:** E1 kit committed; every Critical/High closed or dated-accepted in
  `wave3-status.md`; **no self-run grade presented as independent.**

---

## 8. Gate-compliance appendix (for the authors of these changes)

- Never place a bare `X%` on the same line as a savings keyword without a manifest citation on
  that line; keep a retraction token adjacent to any `68.96%` / `88%` mention (both are
  retracted/withdrawn).
- Restate canonical values as "per STATUS.md" / "per the manifest", never as fresh declarations
  (`check_value_homes.py`).
- New limits/thresholds (A7, A8) get a single home + a value-homes registration.
- Keep all new cross-links kebab-case and resolving on a **case-sensitive** FS (the ubuntu CI is
  the arbiter — see the Wave-2 case-link defect).
- This spec is a planning doc, not a claim surface: it cites figures only to critique them.
