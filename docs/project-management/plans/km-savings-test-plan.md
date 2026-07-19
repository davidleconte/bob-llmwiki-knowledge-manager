> **HISTORICAL SNAPSHOT — RETRACTED METRICS.** The savings/cost percentages
> cited in this plan are from before the manifest-backed harness was in place.
> Preserved as an audit trail; see STATUS.md for validated results.


# KM Bobcoin Savings — Automated Test Plan

## Overview

Add `tests/validation/test_km_savings.py` — a self-contained, always-runnable
pytest module that mechanically executes the measurement protocol defined in
`docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md`.

**What it tests:**
1. **Context compression ratio** — KB docs are measurably smaller than the raw
   source files they summarise (direct token-diff, Section 3 of the guide).
2. **Re-derivation avoidance ceiling** — a "raw source" simulated session costs
   more tokens than a "KB-primary" simulated session answering the same query.
3. **Amortised ROI formula** — the accounting identity holds and breakeven is
   finite for realistic inputs.
4. **Reporting integrity** — a savings claim emitted by the harness contains all
   four required fields (method, N, confidence range, boundary).
5. **Null guard** — a degenerate KB doc that duplicates its source verbatim
   produces ≈0% compression and is correctly flagged, not silently included in
   the headline.

**What it does NOT test:**
- Real Bob Shell sessions (no live API calls; those belong in `tests/e2e/`).
- The TOS optimizer headline (already owned by `tests/validation/test_measure.py`).
- Wall-clock latency or concurrency (those belong in `tests/load/`).

**Grounding in existing patterns:**
- Uses `src.validation.corpus.Document` and `src.validation.measure.measure_optimizer`
  exactly as the existing validation suite does.
- Uses `src.pricing.tokens_to_bobcoins` and `src.monitoring.cost_tracker` for
  Bobcoin arithmetic.
- Fixtures follow `tests/conftest.py` conventions (tmp_path, autouse reset).
- No external deps, no env-var gates, runs in the standard `uv run pytest` pass.

---

## Sub-Task 1 — Fixtures: synthetic KB corpus

**Intent:** Create a minimal but realistic in-memory corpus that mimics a real
KB session: a long "raw source" doc and a shorter "KB summary" doc derived from it.
This gives every subsequent test a deterministic, dependency-free baseline.

**Expected Outcomes:**
- A `raw_source_doc` fixture returning a `Document` with ~500 words of technical prose.
- A `kb_summary_doc` fixture returning a `Document` with ~100 words summarising the
  same topic (realistic compression: ~75–85% reduction).
- A `verbatim_kb_doc` fixture returning a `Document` whose text is identical to the
  raw source (the degenerate null case: 0% compression).
- All fixtures are function-scoped and deterministic (no random seeds left unfixed).

**Todo List:**
1. Write `_PROSE_TEMPLATE` — a block of realistic technical markdown (~500 words)
   covering token caching architecture (use vocabulary consistent with the real KB docs
   so the optimizer has something genuine to compress).
2. Write `_KB_SUMMARY` — a manually compressed version of `_PROSE_TEMPLATE` (~100 words).
3. Define `raw_source_doc`, `kb_summary_doc`, and `verbatim_kb_doc` as module-level
   `@pytest.fixture` functions returning `Document` instances.

**Relevant Context:**
- `src/validation/corpus.py` — `Document(source, text)` dataclass.
- `tests/validation/test_measure.py::PARA` — existing prose fixture pattern to follow.

**Status:** [ ] pending

---

## Sub-Task 2 — Test: context compression ratio

**Intent:** Assert that a well-formed KB document is measurably smaller than its
raw source when token-counted with tiktoken — the direct mechanical proof of
Section 3 of the guide.

**Expected Outcomes:**
- `test_kb_doc_is_smaller_than_raw_source`: passes when kb_tokens < raw_tokens.
- `test_compression_ratio_is_within_expected_range`: compression is between 50%
  and 99% (i.e., KB is 1–50% the size of raw source); fails if KB is larger than
  source or completely empty.
- `test_compression_ratio_reported_with_correct_fields`: the helper function that
  computes and returns the ratio dict includes keys `raw_tokens`, `kb_tokens`,
  `savings_pct`, `mechanism`.

**Todo List:**
1. Import `src.optimizer.token_counter.TokenCounter`; instantiate with `model="gpt-4"`.
2. Write a `_measure_compression(raw_doc, kb_doc) -> dict` helper that token-counts
   both documents and returns the ratio dict (same shape as the guide's Section 3).
3. Write the three test functions, each calling `_measure_compression` on the
   `raw_source_doc` / `kb_summary_doc` pair.
4. For the verbatim case, assert `savings_pct` is < 2% (near-zero, not flagged as real savings).

**Relevant Context:**
- `src/optimizer/token_counter.py` — `TokenCounter.count_tokens(text) -> int`.
- `src/pricing.py` — `tokens_to_bobcoins` for the BC conversion step.
- Guide Section 3 for the exact formula: `savings_pct = (1 - kb_tokens/raw_tokens) * 100`.

**Status:** [ ] pending

---

## Sub-Task 3 — Test: re-derivation avoidance (shadow comparison)

**Intent:** Simulate the "raw session" vs "KB-primary session" comparison from
Section 2 of the guide, entirely in-process using `measure_optimizer` with different
corpora.

**Expected Outcomes:**
- `test_raw_session_costs_more_than_kb_session`: raw_bc > kb_bc for identical queries.
- `test_shadow_savings_pct_is_positive`: `(raw_bc - kb_bc) / raw_bc > 0`.
- `test_shadow_result_has_required_reporting_fields`: the result dict contains
  `raw_tokens`, `kb_tokens`, `savings_pct`, `n_queries`, `mechanism`,
  `applicability_boundary`.

**Todo List:**
1. Write a `_simulate_raw_session(docs) -> dict` helper: token-counts the full
   `raw_source_doc` text per query (simulates Bob reading the whole codebase).
2. Write a `_simulate_kb_session(docs) -> dict` helper: token-counts the
   `kb_summary_doc` text per query (simulates Bob reading the KB doc only).
3. Write the three test functions, asserting the ordering and field presence.
4. The `applicability_boundary` field must be a non-empty string (e.g., "recurring
   architecture queries on stable codebase") — assert `len(...) > 0`.

**Relevant Context:**
- `src/validation/measure.py::measure_optimizer` — shows how to run the optimizer
  over a `Sequence[Document]` without blending cache savings in.
- Guide Section 2: "shadow comparison" protocol with the `raw | kb-primary` tagging.

**Status:** [ ] pending

---

## Sub-Task 4 — Test: amortised ROI formula

**Intent:** Test the accounting identity from Section 4 of the guide:
`net_savings = (queries × savings_per_query) − creation_bc − maintenance_bc`.

**Expected Outcomes:**
- `test_roi_is_positive_after_breakeven`: with 40 queries × 0.38 BC saved, minus
  0.80 BC creation and 0.30 BC maintenance, net > 0 and ROI > 1.0.
- `test_roi_is_negative_before_breakeven`: with 1 query × 0.38 BC, minus the same
  creation/maintenance costs, net < 0.
- `test_breakeven_query_count_is_finite`: the function `breakeven_queries(creation,
  maintenance, savings_per_query)` returns a finite positive integer.
- `test_degenerate_zero_savings_per_query_raises`: calling the breakeven function
  with `savings_per_query=0` raises `ValueError` (not ZeroDivisionError).

**Todo List:**
1. Write a pure `_amortised_roi(queries, savings_per_query, creation_bc,
   maintenance_bc) -> dict` function returning `net_savings_bc`, `roi_multiplier`,
   `breakeven_queries`.
2. Write `breakeven_queries(creation_bc, maintenance_bc, savings_per_query) -> int`
   as a top-level helper; guard against `savings_per_query <= 0`.
3. Write the four test functions using the worked example from the guide (40 queries,
   0.38 BC saved each, 0.80 BC creation, 0.30 BC maintenance).

**Relevant Context:**
- `src/pricing.py::tokens_to_bobcoins` — use for BC ↔ token conversions in helpers.
- Guide Section 4 for the exact worked example and formula.

**Status:** [x] done

---

## Sub-Task 5 — Test: reporting integrity guard

**Intent:** Assert that any savings claim produced by the harness is compliant with
the four-field standard from Section 5 of the guide. This is the mechanism that
prevents the "single unsourced percentage" anti-pattern from re-emerging.

**Expected Outcomes:**
- `test_compliant_claim_passes_guard`: a dict with all four required keys and
  non-empty values passes `assert_compliant_claim(claim)` without raising.
- `test_missing_method_field_fails_guard`: a claim without `method` raises `AssertionError`.
- `test_missing_sample_size_fails_guard`: a claim without `n` raises `AssertionError`.
- `test_missing_confidence_range_fails_guard`: a claim without `confidence_range`
  (a two-element list) raises `AssertionError`.
- `test_missing_applicability_boundary_fails_guard`: a claim without
  `applicability_boundary` raises `AssertionError`.
- `test_additive_fallacy_is_rejected`: a claim that sets `method="additive_total"`
  is rejected by a dedicated check in the guard.

**Todo List:**
1. Write `assert_compliant_claim(claim: dict) -> None` — raises `AssertionError`
   with a descriptive message for each missing/invalid field.
2. Write the six test functions, each passing a minimally-valid or specifically
   broken claim dict.

**Relevant Context:**
- Guide Section 5 "Required elements" and "Non-compliant claims to avoid".
- `src/validation/manifest.py::missing_fields` — analogous guard pattern already in the codebase.

**Status:** [ ] pending

---

## Sub-Task 6 — Test: null guard for verbatim KB docs

**Intent:** Verify that a KB document that duplicates its source verbatim is correctly
detected as providing ~0% compression and excluded from the headline savings figure —
the exact anti-pattern that produced the retracted 68.96% figure.

**Expected Outcomes:**
- `test_verbatim_kb_is_flagged_as_zero_compression`: compression ratio < 2% for the
  `verbatim_kb_doc` fixture.
- `test_verbatim_kb_excluded_from_headline`: when the `verbatim_kb_doc` is mixed into
  a corpus with a genuine KB doc, the mean savings headline stays ≥ the genuine doc's
  savings (verbatim doc doesn't inflate it; if anything it dilutes it).
- `test_null_guard_message_is_informative`: the flag dict returned by the null check
  helper contains a `reason` string explaining *why* the doc was flagged.

**Todo List:**
1. Write `check_for_verbatim_duplication(raw_doc, kb_doc, threshold_pct=2.0) -> dict`
   returning `{"flagged": bool, "savings_pct": float, "reason": str}`.
2. Write the three test functions using the `verbatim_kb_doc` and `kb_summary_doc` fixtures.

**Relevant Context:**
- Sub-task 2's `_measure_compression` helper — reuse it here.
- `src/validation/measure.py::NULL_MAX_SAVINGS_PCT` — analogous threshold constant pattern.

**Status:** [ ] pending

---

## Sub-Task 7 — Wire to CI and update INDEX

**Intent:** Ensure the new tests run in the standard pytest pass, update the coverage
floor check, add the test file to `CODEOWNERS`, and register the guide cross-reference
in `docs/knowledge-base/index.md`.

**Expected Outcomes:**
- `uv run pytest tests/validation/test_km_savings.py -v` exits 0 with all tests passing.
- `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance -q` exits 0
  (new tests don't break the existing suite).
- `scripts/check_coverage_by_package.py` reports delegation ≥ 70% and validation ≥ 80%.
- `docs/knowledge-base/index.md` references the new guide under **Guides** with a
  one-line description.
- `.github/CODEOWNERS` has an entry for `tests/validation/test_km_savings.py`.

**Todo List:**
1. Run `uv run pytest tests/validation/test_km_savings.py -v` and fix any failures.
2. Run the full suite (excluding load/perf) and confirm no regressions.
3. Run `scripts/check_coverage_by_package.py` and confirm floors are met.
4. Add `tests/validation/test_km_savings.py @davidleconte` to `.github/CODEOWNERS`.
5. INDEX.md entry is already present (added in the previous turn); verify it's accurate.

**Relevant Context:**
- `scripts/check_coverage_by_package.py` — coverage floor enforcement.
- `.github/CODEOWNERS` — existing ownership pattern.

**Status:** [ ] pending
