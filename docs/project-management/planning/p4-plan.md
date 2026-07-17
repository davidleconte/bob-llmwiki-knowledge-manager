# P4 Plan — Query Quality, MiniLM Wiring, Graph Enrichment, Audit Cleanup

## Status: [x] complete — 2026-07-17

---

## Overview

P4 closes the four open threads that P3 deliberately deferred:

1. **Query quality** — fix the 3 known golden-set misses (recency tiebreaker, date-aware
   filtering, doc-length normalisation) so `KnowledgeBaseQuery` reaches p@3 > 0.88 on the
   validated golden set.
2. **MiniLM backend wiring** — `EmbeddingGenerator(backend="minilm")` must activate when
   either `mlx-embeddings` OR `sentence-transformers` is installed. Currently only the former
   activates it (ADR-017 follow-up; tracked in `docs/adr/017-knowledge-graph-layer.md`
   Validation section).
3. **NodeProps enrichment** — extend `NodeProps` and `KnowledgeGraphBuilder` to capture
   `mtime_epoch`, `content_length`, `description`, and `related_refs`. These fields power the
   recency tiebreaker (sub-task 2) and make the graph API richer for callers.
4. **Audit cleanup** — close the three open findings from the adversarial embeddings audit
   (AF-3: `findall` → `finditer`; AF-5: `doc_count` docstring/rename; AF-6: rebuild
   round-trip regression test).

A zero-th sub-task (pre-flight gate) ensures the benchmark CI job — which had a pending
smoke-test+push step — is confirmed green before any P4 changes land.

**Scope boundary:**
- The delegation module (`src/delegation/`) floor stays at 52% (intentional). P4 does not
  touch it.
- No new external dependencies. `sentence-transformers` is already installed; this sub-task
  wires it, not installs it.
- No schema-breaking changes to `.bob/kb-graph.json`. `NodeProps` gains optional fields with
  backward-compatible defaults so existing persisted graphs load without error.

**Authoritative test target:** `python3.11 -m pytest` (not `python3`).

---

## Sub-Task 0 — Pre-flight: close benchmark CI gate

**Intent:** Verify that the benchmark smoke-test step (`fix-benchmarks-ci-plan.md`
Sub-Task 4) is complete and all CI jobs are green. This is the entry gate for P4 — no
P4 code should be pushed while any CI job is red.

**Expected Outcomes:**
- `python3.11 -m pytest tests/performance/ --benchmark-only --benchmark-autosave` exits 0
- `uv run ruff check tests/performance/` exits 0
- Commit pushed to `fix-multilevel-cache-race` (or a new `p4-dev` branch)
- All 7 CI jobs green (lint, typecheck, tests 3.11, tests 3.12, e2e, validation, benchmarks)

**Todo List:**
1. Run `uv run ruff check tests/performance/` — confirm no errors
2. Run `uv run ruff format --check tests/performance/` — confirm no format drift
3. Run `python3.11 -m pytest tests/performance/ --benchmark-only --benchmark-autosave` — confirm exit 0
4. If not yet committed, `git add` the two test files + `.github/workflows/ci.yml` and commit with `"fix(benchmarks): remove hardcoded timing assertions, raise CI compare threshold to 50%"`
5. Push to branch; confirm CI passes

**Relevant Context:**
- `docs/project-management/planning/fix-benchmarks-ci-plan.md` — Sub-Task 4 (pending)
- `tests/performance/test_cache_performance.py` — timing assertions already replaced
- `tests/performance/test_optimizer_performance.py` — timing assertions already replaced
- `uv run` prefix required; do NOT use bare `python3` (defaults to 3.14)

**Status:** [ ] pending

---

## Sub-Task 1 — Audit cleanup: AF-3, AF-5, AF-6

**Intent:** Close the three open audit findings from
`docs/knowledge-base/research/adversarial-audit-embeddings-chunker-2026-07-17.md`.
These are correctness/hygiene fixes independent of all other P4 work.

**Expected Outcomes:**
- AF-3: `_TABLE_RE.findall(body)` in `src/embeddings/chunker.py` replaced with `finditer()`
  pattern; the affected method handles multi-row tables correctly
- AF-5: `PersistentEmbeddingIndex.doc_count` has an accurate docstring (or is renamed to
  `chunk_count` with a `doc_count` alias for backward-compat); no caller behaviour changes
- AF-6: New regression test in `tests/embeddings/` exercises the full
  `rebuild() → flush() → new_instance.search()` round-trip, confirming AF-1 fix is durable
- All existing tests still pass (`python3.11 -m pytest tests/embeddings/ -v`)

**Todo List:**
1. In `src/embeddings/chunker.py`: replace `_TABLE_RE.findall(body)` with
   `[m.group(0) for m in _TABLE_RE.finditer(body)]` (or equivalent iterator pattern) so
   multi-row table parsing returns complete table text, not just the last captured row
2. Update the affected method's docstring to document the corrected behaviour
3. In `src/embeddings/index.py`: update `doc_count` docstring to say "chunks indexed" (or
   rename the property to `chunk_count` and keep `doc_count` as a deprecated alias with a
   deprecation warning). Pick the minimal-churn option that doesn't break callers.
4. In `tests/embeddings/`: add a test `test_rebuild_flush_reload_roundtrip` that:
   - Creates a `PersistentEmbeddingIndex` with a temp KB path
   - Calls `rebuild()` to populate from filesystem
   - Calls `flush()` to persist
   - Instantiates a new `PersistentEmbeddingIndex` pointing at the same paths
   - Calls `search("cache")` and asserts at least one result is returned
   - Asserts the matrix shape after reload matches the shape after flush
5. Run `python3.11 -m pytest tests/embeddings/ -v` — all pass

**Relevant Context:**
- `src/embeddings/chunker.py` — `_TABLE_RE` and the `_extract_tables` method (AF-3)
- `src/embeddings/index.py:273–281` — `doc_count` property (AF-5)
- `tests/embeddings/test_embeddings.py` — existing test patterns to mirror (AF-6)
- `src/embeddings/store.py` — `STALENESS_FILE`, `save()`, `load()` 3-tuple (AF-1 fix, don't regress)
- AF-1 fixed in previous session: `manifest.json` (chunks) + `staleness.json` (file sentinels)

**Status:** [ ] pending

---

## Sub-Task 2 — MiniLM backend wiring: `sentence-transformers` fallback

**Intent:** Implement the ADR-017 follow-up action. `EmbeddingGenerator(backend="minilm")`
currently only activates when `mlx-embeddings` is installed. This sub-task wires
`sentence-transformers` as a second resolution path so `backend="minilm"` works on any
machine with either package installed.

**Expected Outcomes:**
- `EmbeddingGenerator(backend="minilm")` activates correctly when:
  - `mlx-embeddings` is installed → `_minilm_backend = "mlx"` (unchanged)
  - `sentence-transformers` is installed, `mlx-embeddings` is not → `_minilm_backend = "st"`
  - Neither installed → falls back to `"hashing"` (unchanged)
- `_embed_minilm()` dispatches via `_minilm_backend` (already exists; just needs the `"st"`
  branch to activate from `_try_load_minilm()`)
- New unit test `test_minilm_st_fallback` confirms the `"st"` branch activates and produces
  384-dim unit-norm vectors when `sentence-transformers` is importable
- `EmbeddingGenerator(backend="hashing")` behaviour is completely unchanged
- `python3.11 -m pytest tests/cache/ -v -k minilm` — all pass

**Todo List:**
1. In `src/cache/embeddings.py`, `_try_load_minilm()`: add a `try/except ImportError` block
   after the MLX attempt that imports `sentence_transformers` and sets `_minilm_backend = "st"`
   (the pattern already exists for the MLX path — mirror it)
2. Confirm `_embed_minilm()` already has a `_minilm_backend == "st"` dispatch branch (it
   should from the P3 dual-backend fix); if not, add it
3. Add a guard: if `_minilm_backend` is already `"mlx"`, skip the `sentence-transformers`
   attempt entirely (no double-loading)
4. In `tests/cache/`: add `test_minilm_st_fallback` — mock `mlx-embeddings` as unavailable
   (or test directly on this machine where it is not installed), call
   `EmbeddingGenerator(backend="minilm")`, assert `backend == "minilm"`,
   assert `embedding_dim == 384`, generate a vector and assert `shape == (384,)` and
   `abs(norm - 1.0) < 1e-5`
5. Update `docs/adr/017-knowledge-graph-layer.md` Validation section follow-up item:
   mark it as resolved, reference the sub-task and commit
6. Run `python3.11 -m pytest tests/cache/ -v` — all pass

**Relevant Context:**
- `src/cache/embeddings.py:42–78` — `_try_load_minilm()` and `_embed_minilm()`
- `src/cache/embeddings.py` global `_minilm_backend` — set by `_try_load_minilm()`
- `docs/adr/017-knowledge-graph-layer.md` — Validation section follow-up action item
- `docs/knowledge-base/research/graph-validation-2026-07-17.md:209–239` — the MiniLM
  pipeline described in the validation doc (reference implementation to match)
- Existing test in `tests/cache/` for `EmbeddingGenerator` backends — mirror the pattern

**Status:** [ ] pending

---

## Sub-Task 3 — NodeProps enrichment

**Intent:** Extend `NodeProps` with four new optional fields (`mtime_epoch`, `content_length`,
`description`, `related_refs`) and update `KnowledgeGraphBuilder` to populate them during
the filesystem walk. These fields are prerequisites for the recency tiebreaker (Sub-Task 4)
and make the graph API useful for caller display (description for previews, related_refs for
navigation).

All new fields have backward-compatible defaults so existing `.bob/kb-graph.json` files load
without error.

**Expected Outcomes:**
- `NodeProps` has four new fields with defaults: `mtime_epoch: float = 0.0`,
  `content_length: int = 0`, `description: str = ""`, `related_refs: List[str] = []`
- `NodeProps.to_dict()` / `from_dict()` round-trip all four fields correctly
- `KnowledgeGraphBuilder._build_explicit()` populates all four during its filesystem walk:
  - `mtime_epoch`: `Path.stat().st_mtime`
  - `content_length`: `len(content)` characters
  - `description`: first non-empty non-heading paragraph after the frontmatter block,
    truncated to 200 characters
  - `related_refs`: the raw `related:` list from frontmatter (strings, not resolved)
- Existing `GraphStore` round-trip still works: old JSON without these keys deserialises
  cleanly to default values (the `from_dict()` uses `.get(key, default)` already)
- `python3.11 -m pytest tests/graph/ -v` — all pass, including new tests covering:
  - `test_nodeprops_new_fields_defaults` — empty NodeProps, all four fields are default values
  - `test_nodeprops_roundtrip_with_new_fields` — `to_dict()` → `from_dict()` preserves all four
  - `test_builder_populates_mtime_epoch` — a tmp KB doc with known mtime
  - `test_builder_populates_content_length` — a tmp KB doc with known character count
  - `test_builder_populates_description` — a tmp KB doc with a first paragraph
  - `test_builder_populates_related_refs` — a tmp KB doc with `related:` frontmatter

**Todo List:**
1. In `src/graph/graph.py`, `NodeProps` dataclass: add the four fields in declaration order
   after `status`; update `to_dict()` to include them; update `from_dict()` to read them with
   `.get(key, default)` (safe for old JSON)
2. In `src/graph/builder.py`, `_build_explicit()` method: after loading content and parsing
   frontmatter, set the four new props on the `NodeProps` passed to `add_node()`:
   - `mtime_epoch = path.stat().st_mtime`
   - `content_length = len(content)`
   - `description = _extract_description(content)` (helper to extract first paragraph, ≤ 200 chars)
   - `related_refs = fm.get("related", [])` (raw strings, same list parsed by `_parse_frontmatter`)
3. Add helper `_extract_description(content: str) -> str` in `builder.py`: strips frontmatter
   block, skips blank lines and heading lines (`# ...`), returns first non-empty text line
   truncated to 200 chars; returns `""` if nothing found
4. In `tests/graph/test_graph.py`: add tests `test_nodeprops_new_fields_defaults` and
   `test_nodeprops_roundtrip_with_new_fields`
5. In `tests/graph/test_builder.py`: add four builder tests using `tmp_path` fixtures
   (mirror existing `_write_doc` / `_make_kb` helper pattern)
6. Run `python3.11 -m pytest tests/graph/ -v` — all pass

**Relevant Context:**
- `src/graph/graph.py:27–60` — `NodeProps` dataclass, `to_dict()`, `from_dict()`
- `src/graph/builder.py:47–85` — `_parse_frontmatter()` (already extracts `related`)
- `src/graph/builder.py` — `_build_explicit()` method (the filesystem walker that creates nodes)
- `src/graph/store.py` — `GraphStore.save()` / `load()` (JSON persistence; verify round-trip)
- `tests/graph/test_builder.py` — `_write_doc()` and `_make_kb()` helper pattern to mirror

**Status:** [ ] pending

---

## Sub-Task 4 — Query quality: recency tiebreaker and date filtering

**Intent:** Address 2 of the 3 known golden-set misses with targeted, backward-compatible
additions to `KnowledgeBaseQuery`. Miss #1 (length bias) is **not addressed in P4** —
MiniLM already achieves p@3=0.88 and `_keyword_score()` is left unchanged.

| Miss | Root cause | Fix |
|---|---|---|
| `"security vulnerability scan"` gets wrong version | No recency signal | `recency_weight` parameter: mtime-normalised blend |
| `"external audit july 2026"` | Date not in doc text | `date_filter` parameter: prefix-match on frontmatter `date:` field |
| `"dependency security audit packages"` beaten by long docs | Length bias | **Deferred** — MiniLM handles adequately; revisit if post-P4 audit shows regression |

All new parameters default to current behaviour (`recency_weight=0.0`, `date_filter=None`).

**Expected Outcomes:**
- `KnowledgeBaseQuery.__init__()` accepts `recency_weight: float = 0.0`; stored as
  `self._recency_weight`; validated in [0.0, 1.0]
- `KnowledgeBaseQuery.query()` accepts `date_filter: Optional[str] = None`
  (ISO date string prefix e.g. `"2026-07"`)
- When `recency_weight > 0`: after all scores are computed, a second pass normalises
  each doc's mtime to [0, 1] relative to the result set's max mtime, then blends:
  `score = (1-rw)*base_score + rw*(norm_mtime * 15.0)`; results re-sorted
- When `date_filter` is not None: results whose frontmatter `date:` field does not
  start with the filter string are dropped from the final list (after scoring, before
  truncating to `max_results`)
- `_keyword_score()` is **not modified** — no length normalisation in P4
- `src/cli.py` `graph-query` subcommand gains `--recency-weight FLOAT` flag (default `0.0`)
- Golden-set re-validation: p@3 ≥ 0.88 (no regression); Miss #3 resolved with
  `recency_weight=0.1` (newer `security-scan-2026-07-13.md` ranks above older one)
- All existing tests still pass; 5 new tests cover the new parameters

**Todo List:**
1. In `src/tools/kb_query.py`, `__init__()`: add `recency_weight: float = 0.0`; validate
   [0.0, 1.0]; store as `self._recency_weight`
2. In `_query_full_scan()` and `_query_via_index()`: after computing all scores, when
   `self._recency_weight > 0.0`, run a second pass over `all_results`:
   - Parse `result["last_modified"]` (ISO string already in dict) to float epoch via
     `datetime.fromisoformat(result["last_modified"]).timestamp()`
   - Find `mtime_max = max(epoche for all results)`
   - Normalise: `norm_mtime = epoch / mtime_max` (safe: mtime_max > 0 always)
   - Blend: `result["score"] = (1-rw)*result["score"] + rw*(norm_mtime * 15.0)`
   - Re-sort `all_results` by updated score before the final `[:max_results]` slice
3. In `query()`: add `date_filter: Optional[str] = None`; after the index/scan path returns
   `result["results"]`, filter in-place:
   `result["results"] = [r for r in result["results"] if _doc_date_matches(r, date_filter)]`
   where `_doc_date_matches()` is a small helper that reads `date:` from the raw file
   (regex `r"^date:\s*(\S+)"`) and checks `.startswith(date_filter)`
4. In `src/cli.py`, `graph-query` subcommand: add `--recency-weight` option (type `float`,
   default `0.0`); pass it through to `KnowledgeBaseQuery(recency_weight=...)`
5. In `tests/tools/`: add 5 tests:
   - `test_recency_weight_zero_is_unchanged` — `recency_weight=0.0` gives identical results
   - `test_recency_weight_promotes_newer_doc` — two tmp docs with identical content but
     different mtimes; `recency_weight=1.0` ranks newer first
   - `test_date_filter_excludes_non_matching` — doc with `date: 2026-06` excluded when
     `date_filter="2026-07"`
   - `test_date_filter_none_is_unchanged` — `date_filter=None` gives identical results
   - `test_golden_set_miss3_resolved` (**@pytest.mark.slow**) — query
     `"security vulnerability scan"` against live KB with MiniLM + `recency_weight=0.1`;
     assert `security-scan-2026-07-13.md` (newer) ranks above `security-scan-2026-07-12.md`
6. Run `python3.11 -m pytest tests/tools/ -v` — all pass

**Relevant Context:**
- `src/tools/kb_query.py:76–200` — `__init__()`, `query()`, `_query_full_scan()`,
  `_query_via_index()`; `_keyword_score()` is intentionally not modified
- `src/tools/kb_query.py:182–184` — `last_modified` already in every result dict
- `src/cli.py` — `graph-query` subcommand; add `--recency-weight` here
- `docs/knowledge-base/research/graph-validation-2026-07-17.md:177–183` — 3 miss root causes
- `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md` — 25-query golden set
- Sub-Task 3 must complete before this sub-task (provides `NodeProps.mtime_epoch` context,
  but recency tiebreaker uses `last_modified` from the result dict directly — so Sub-Task 3
  is a soft prereq for graph-wired callers, not a hard blocker)

**Status:** [ ] pending

---

## Sub-Task 5 — ADR-018, documentation update, STATUS.md

**Intent:** Write ADR-018, update the architecture doc to reflect all P4 changes, update
`CHANGELOG.md`, and update `STATUS.md`. This is the P4 sign-off sub-task.

**Expected Outcomes:**
- `docs/adr/018-p4-query-quality.md` exists and documents:
  - Decision 1: recency tiebreaker blend formula (why relative-normalised mtime, not absolute)
  - Decision 2: date filter design (prefix-match on `date:` field, not full-text date parsing)
  - Decision 3: length normalisation deferred (MiniLM sufficient at p@3=0.88; revisit if needed)
  - Validation results: p@3 before/after on golden set (values from Sub-Task 4 slow test)
- `docs/adr/README.md` has the ADR-018 entry
- `docs/architecture/ARCHITECTURE.md` reflects: (a) MiniLM dual-backend chain updated
  (mlx → sentence-transformers → hashing), (b) `NodeProps` table updated with 4 new fields,
  (c) query scoring section updated with recency and date-filter parameters
- `CHANGELOG.md` `[Unreleased]` section has P4 entries in Added/Changed/Fixed
- `STATUS.md` roadmap field updated with P4 note
- `docs/knowledge-base/INDEX.md` updated with any new research/guide docs created this phase

**Todo List:**
1. Write `docs/adr/018-p4-query-quality.md` (3 decisions + validation table; mirror ADR-017 structure)
2. Add ADR-018 row to `docs/adr/README.md`
3. Update `docs/architecture/ARCHITECTURE.md`:
   - §5 (Embedding backends): extend MiniLM resolution chain description
   - §3b (Graph layer): update `NodeProps` field table to include 4 new fields
   - §4 (Query scoring): add recency_weight and date_filter to parameter table
4. In `CHANGELOG.md` `[Unreleased]`:
   - Added: `NodeProps.mtime_epoch`, `content_length`, `description`, `related_refs`
   - Added: `KnowledgeBaseQuery.recency_weight` parameter
   - Added: `KnowledgeBaseQuery.query(date_filter=)` parameter
   - Changed: `EmbeddingGenerator(backend="minilm")` now activates via `sentence-transformers`
     when `mlx-embeddings` is not installed
   - Fixed: AF-3 `findall` → `finditer` in chunker; AF-5 `doc_count` docstring; AF-6 regression test
5. Update `STATUS.md` roadmap field with P4 completion note and validated p@3 figure
6. Update `docs/knowledge-base/INDEX.md` with new research entries if any were created

**Relevant Context:**
- `docs/adr/017-knowledge-graph-layer.md` — mirror this structure for ADR-018
- `docs/adr/README.md` — append new row in the ADR table
- `docs/architecture/ARCHITECTURE.md` — current architecture doc (updated in P3 doc session)
- `CHANGELOG.md` — `[Unreleased]` section
- `STATUS.md:12` — roadmap field (single home; do not update the maturity table without a
  completed re-audit)

**Status:** [ ] pending

---

## Ordering and dependencies

```
Sub-Task 0 (pre-flight CI gate)
    └── Sub-Task 1 (audit cleanup AF-3/5/6)     [independent]
    └── Sub-Task 2 (MiniLM backend wiring)      [independent]
    └── Sub-Task 3 (NodeProps enrichment)       [independent; prereq for Sub-Task 4]
            └── Sub-Task 4 (query quality)      [depends on Sub-Task 3 for mtime_epoch]
                    └── Sub-Task 5 (ADR + docs) [depends on Sub-Tasks 1–4]
```

Sub-Tasks 1, 2, 3 can be implemented in any order after Sub-Task 0 completes. Sub-Task 4
must wait for Sub-Task 3 (for `NodeProps.mtime_epoch`). Sub-Task 5 must be last.

---

## Validation gate

Before Sub-Task 5 is marked done, the following must all pass:

```bash
python3.11 -m pytest tests/ -v --ignore=tests/performance
python3.11 -m pytest tests/performance/ --benchmark-only --benchmark-autosave
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
python3.11 -m src.validation  # manifest-backed savings validation (no regression)
```

Golden-set regression requirement: p@3 ≥ 0.88 at baseline config; Miss #3
(`"security vulnerability scan"`) resolved with `recency_weight=0.1` + MiniLM.
Golden-set test is `@pytest.mark.slow` — run with `pytest -m slow`, not in default suite.

---

## Non-goals for P4

- Delegation module coverage improvement (floor stays at 52%)
- Sub-section/chunk-level graph nodes (rejected in ADR-017 Decision 2)
- Tag hierarchy or SPARQL-style queries
- Windows compatibility
- Automated multi-agent research pipeline
- Any new external package dependencies
- Keyword scorer length normalisation (deferred — MiniLM already handles Miss #1 at p@3=0.88)
