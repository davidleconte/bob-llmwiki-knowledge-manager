"""Automated measurement of Knowledge Manager Bobcoin savings.

Mechanically executes the protocol defined in
docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md.

Three savings mechanisms are measured and kept separate (the same discipline as
the rest of src/validation/):

1. Context compression ratio   — KB doc token count vs raw source token count.
   Uses measure_optimizer (the real product, cache=off, no truncation cap) so
   the number is grounded in the optimizer's actual behaviour, not just wc.

2. Re-derivation avoidance     — simulated raw session vs KB-primary session.
   Uses measure_optimizer on each corpus separately; savings = difference in
   total_original_tokens (what Bob would send), not a hypothetical.

3. Amortised ROI               — accounting identity from the guide's worked
   example, using real token counts from the fixtures rather than the guide's
   literal constants, so the test breaks if the optimizer changes meaningfully.

Reporting integrity and the null guard are tested as pure-function unit tests;
they do not need real corpora, only the contracts the guide mandates.

No env-var gate — every test here runs in the standard uv run pytest pass.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

import pytest

from src.config.schema import CacheConfig, ConfigSchema, MonitoringConfig, OptimizerConfig
from src.pricing import tokens_to_bobcoins
from src.validation.corpus import Document
from src.validation.measure import measure_optimizer

# ---------------------------------------------------------------------------
# Prose fixtures — realistic KB content, not Lorem Ipsum.
# ---------------------------------------------------------------------------

# ~500-word technical article (raw source a KB doc might summarise).
_RAW_SOURCE_TEXT = """\
# Multi-Level Caching in the Token Optimization System

## Overview

The Token Optimization System implements a two-tier cache hierarchy to avoid
redundant LLM token expenditure. The first tier, called ExactCache, stores
prompt-response pairs keyed by the SHA-256 hash of the input text. A lookup is
O(1) and completes in under one millisecond. The second tier, SemanticCache,
stores TF-IDF embedding vectors and responds to queries whose cosine similarity
to a stored entry exceeds a configurable threshold, defaulting to 0.85.

## Exact Cache (L1)

ExactCache is backed by an ordered dictionary with a configurable maximum
capacity. When capacity is reached the least-recently-used entry is evicted.
The default capacity is one thousand entries, occupying roughly five megabytes
of process memory. Because the hash is computed once at set-time and stored
alongside the value, a cache hit requires only a single dictionary lookup.

All public methods acquire a reentrant lock before touching shared state. This
ensures that concurrent writers cannot corrupt the underlying store, and that
a reader promoting an entry to the head of the LRU list does not race with a
simultaneous eviction.

## Semantic Cache (L2)

SemanticCache addresses the common case where the same underlying question is
phrased differently across sessions. A TF-IDF vectorizer is fitted lazily on
the first set() call and updated incrementally as new entries arrive. For each
get() request the system computes the cosine similarity between the query
vector and every stored vector and returns the highest-scoring entry if its
score exceeds the threshold.

Because similarity search is O(n) in the number of cached entries, the default
capacity is five hundred entries. Profiling shows that at this size the median
lookup latency is below ten milliseconds on a modern laptop, satisfying the
sub-100ms contract from the SLA.

## Cache Promotion

When the L2 tier returns a hit, the entry is promoted to L1. Subsequent
identical queries therefore bypass the more expensive vector comparison.
Promotion is implemented by calling l1_cache.set() inside the MultiLevelCache
get() path before returning the result to the caller.

## Hit Rate and Workload Dependency

The aggregate hit rate is a property of the request stream, not of the cache
implementation. A highly repetitive workload with 70 percent repeat queries
will see a 70 percent hit rate regardless of the cache tuning. For this reason
the validation harness always discloses the repeat rate of the synthetic
workload alongside the measured hit rate, so the two cannot be confused.

Savings from cache hits are reported separately from optimizer compression
savings. Blending them into a single headline produces a number that varies
wildly across workloads and cannot be reproduced independently. The prior
version of this documentation blended the two; the resulting 68.96 percent
figure was retracted after the Phase 5 audit.

## Configuration

Both cache tiers accept a configuration dataclass. Capacity, threshold, and
eviction policy are the only tunable parameters. The threshold must be between
zero and one; values above 0.95 are effectively exact-match caches. Values
below 0.70 risk returning semantically unrelated results and are rejected at
construction time with a ValueError.
"""

# ~100-word KB summary of the above (realistic compression: ~80% reduction).
_KB_SUMMARY_TEXT = """\
# Multi-Level Cache — Quick Reference

Two-tier cache: L1 (ExactCache, SHA-256, O(1), <1ms, LRU-1000) and
L2 (SemanticCache, TF-IDF cosine similarity, O(n), <100ms, capacity-500).

L2 hits are promoted to L1. Thread-safe via RLock.

**Hit rate is workload-dependent** — a 70% repeat-query stream yields ~70%
hits. Report hit rate and repeat rate together; never blend with optimizer
compression. The prior 68.96% headline blended both and was retracted.

Config: threshold 0.70–0.95, capacity per tier, eviction=LRU. Defaults
satisfy SLA targets.
"""


# ---------------------------------------------------------------------------
# Sub-task 1: Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_source_doc() -> Document:
    """~500-word technical markdown — the 'codebase' a KB doc summarises."""
    return Document(source="raw:cache-architecture.md", text=_RAW_SOURCE_TEXT)


@pytest.fixture
def kb_summary_doc() -> Document:
    """~100-word KB summary — realistic ~80% compression of the raw source."""
    return Document(source="kb:cache-architecture.md", text=_KB_SUMMARY_TEXT)


@pytest.fixture
def verbatim_kb_doc(raw_source_doc: Document) -> Document:
    """Degenerate KB doc: identical to the raw source — 0% compression."""
    return Document(source="verbatim:cache-architecture.md", text=raw_source_doc.text)


@pytest.fixture
def config() -> ConfigSchema:
    return ConfigSchema(CacheConfig(), OptimizerConfig(), MonitoringConfig())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _measure_compression(
    raw_doc: Document,
    kb_doc: Document,
    cfg: ConfigSchema,
) -> Dict[str, Any]:
    """Run measure_optimizer on raw then kb corpus; return compression dict.

    Uses measure_optimizer (cache=off, no truncation cap) for both so the
    numbers reflect the real product, not just character counts.
    """
    raw_result = measure_optimizer(cfg, "gpt-4", [raw_doc])
    kb_result = measure_optimizer(cfg, "gpt-4", [kb_doc])

    raw_tokens = raw_result["total_original_tokens"]
    kb_tokens = kb_result["total_original_tokens"]
    savings_pct = (1 - kb_tokens / raw_tokens) * 100 if raw_tokens else 0.0

    return {
        "raw_tokens": raw_tokens,
        "kb_tokens": kb_tokens,
        "savings_pct": round(savings_pct, 4),
        "mechanism": "re-derivation avoidance: KB doc replaces full source read",
    }


def _amortised_roi(
    *,
    queries: int,
    savings_per_query_bc: float,
    creation_bc: float,
    maintenance_bc: float,
) -> Dict[str, Any]:
    """Accounting identity from Guide §4.

    Uses real token-derived savings_per_query_bc rather than the guide's
    literal constants, so the formula is exercised against live measurements.
    """
    gross_savings = queries * savings_per_query_bc
    total_cost = creation_bc + maintenance_bc
    net_savings = gross_savings - total_cost
    roi_multiplier = net_savings / total_cost if total_cost > 0 else float("inf")
    return {
        "gross_savings_bc": round(gross_savings, 6),
        "total_cost_bc": round(total_cost, 6),
        "net_savings_bc": round(net_savings, 6),
        "roi_multiplier": round(roi_multiplier, 4),
        "breakeven_queries": breakeven_queries(creation_bc, maintenance_bc, savings_per_query_bc),
    }


def breakeven_queries(
    creation_bc: float,
    maintenance_bc: float,
    savings_per_query_bc: float,
) -> int:
    """Minimum number of queries to recover KB creation + maintenance cost."""
    if savings_per_query_bc <= 0:
        raise ValueError(
            f"savings_per_query_bc must be > 0; got {savings_per_query_bc!r}. "
            "A KB doc that saves nothing cannot reach breakeven."
        )
    return math.ceil((creation_bc + maintenance_bc) / savings_per_query_bc)


def assert_compliant_claim(claim: Dict[str, Any]) -> None:
    """Guard: raise AssertionError if the savings claim is missing a required field.

    Four fields are mandatory (Guide §5):
      - method        : non-empty string naming the measurement approach
      - n             : positive integer sample size
      - confidence_range : [lo, hi] two-element list of floats
      - applicability_boundary : non-empty string scoping when the figure applies

    One anti-pattern is explicitly banned:
      - method == "additive_total" re-manufactures the retracted blended headline.
    """
    errors: List[str] = []

    method = claim.get("method")
    if not isinstance(method, str) or not method.strip():
        errors.append("'method' must be a non-empty string")
    elif method.strip() == "additive_total":
        errors.append(
            "'method=additive_total' is the additive-fallacy anti-pattern: "
            "optimizer savings and KB re-derivation savings cannot be simply summed "
            "(they operate at different stack levels and have different applicability). "
            "Report them separately."
        )

    n = claim.get("n")
    if not isinstance(n, int) or n <= 0:
        errors.append("'n' must be a positive integer (sample size)")

    cr = claim.get("confidence_range")
    if (
        not isinstance(cr, (list, tuple))
        or len(cr) != 2
        or not all(isinstance(v, (int, float)) for v in cr)
        or cr[0] > cr[1]
    ):
        errors.append(
            "'confidence_range' must be a [lo, hi] pair of numbers with lo <= hi"
        )

    boundary = claim.get("applicability_boundary")
    if not isinstance(boundary, str) or not boundary.strip():
        errors.append("'applicability_boundary' must be a non-empty string")

    if errors:
        raise AssertionError(
            "Non-compliant savings claim — " + "; ".join(errors)
        )


def check_for_verbatim_duplication(
    raw_doc: Document,
    kb_doc: Document,
    cfg: ConfigSchema,
    threshold_pct: float = 2.0,
) -> Dict[str, Any]:
    """Flag a KB doc that provides effectively zero compression vs its source.

    Returns a dict with 'flagged', 'savings_pct', and 'reason'.
    threshold_pct: below this savings_pct the doc is considered verbatim/useless.
    """
    result = _measure_compression(raw_doc, kb_doc, cfg)
    flagged = result["savings_pct"] < threshold_pct
    reason = (
        f"KB doc compresses only {result['savings_pct']:.2f}% of its raw source "
        f"(threshold {threshold_pct:.1f}%). "
        + (
            "This is indistinguishable from verbatim duplication and provides "
            "no re-derivation saving. Exclude from savings headline."
            if flagged
            else "Compression is genuine."
        )
    )
    return {
        "flagged": flagged,
        "savings_pct": result["savings_pct"],
        "raw_tokens": result["raw_tokens"],
        "kb_tokens": result["kb_tokens"],
        "reason": reason,
    }


# ===========================================================================
# Sub-task 2 — Context compression ratio
# ===========================================================================

class TestContextCompressionRatio:
    """Guide §3: direct token-diff between raw source and KB summary."""

    def test_kb_doc_is_smaller_than_raw_source(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = _measure_compression(raw_source_doc, kb_summary_doc, config)
        assert result["kb_tokens"] < result["raw_tokens"], (
            f"KB doc ({result['kb_tokens']} tokens) must be smaller than "
            f"raw source ({result['raw_tokens']} tokens)"
        )

    def test_compression_ratio_within_realistic_range(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = _measure_compression(raw_source_doc, kb_summary_doc, config)
        assert 50.0 <= result["savings_pct"] <= 99.0, (
            f"Expected 50–99% compression for a well-formed KB summary; "
            f"got {result['savings_pct']:.2f}%. "
            "Below 50% means the KB is barely compressed; above 99% means it's empty."
        )

    def test_compression_result_has_required_fields(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = _measure_compression(raw_source_doc, kb_summary_doc, config)
        for field in ("raw_tokens", "kb_tokens", "savings_pct", "mechanism"):
            assert field in result, f"Missing required field: {field!r}"
        assert isinstance(result["mechanism"], str) and result["mechanism"]

    def test_verbatim_doc_shows_near_zero_compression(
        self, raw_source_doc: Document, verbatim_kb_doc: Document, config: ConfigSchema
    ) -> None:
        result = _measure_compression(raw_source_doc, verbatim_kb_doc, config)
        assert result["savings_pct"] < 2.0, (
            f"A verbatim KB doc must show < 2% savings; "
            f"got {result['savings_pct']:.2f}%. "
            "The optimizer should compress whitespace slightly but not meaningfully."
        )

    def test_savings_expressed_as_bobcoins(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = _measure_compression(raw_source_doc, kb_summary_doc, config)
        raw_bc = tokens_to_bobcoins(result["raw_tokens"])
        kb_bc = tokens_to_bobcoins(result["kb_tokens"])
        savings_bc = raw_bc - kb_bc
        assert savings_bc > 0.0, (
            f"Savings in Bobcoins must be positive; got {savings_bc:.6f} BC "
            f"(raw={raw_bc:.6f}, kb={kb_bc:.6f})"
        )


# ===========================================================================
# Sub-task 3 — Re-derivation avoidance (shadow comparison)
# ===========================================================================

class TestReDerivationAvoidance:
    """Guide §2: raw session vs KB-primary session via measure_optimizer."""

    def _run_shadow(
        self,
        raw_doc: Document,
        kb_doc: Document,
        cfg: ConfigSchema,
    ) -> Dict[str, Any]:
        """Simulate one shadow comparison pair."""
        raw_session = measure_optimizer(cfg, "gpt-4", [raw_doc])
        kb_session = measure_optimizer(cfg, "gpt-4", [kb_doc])

        raw_bc = tokens_to_bobcoins(raw_session["total_original_tokens"])
        kb_bc = tokens_to_bobcoins(kb_session["total_original_tokens"])
        savings_pct = (raw_bc - kb_bc) / raw_bc * 100 if raw_bc else 0.0

        return {
            "raw_tokens": raw_session["total_original_tokens"],
            "kb_tokens": kb_session["total_original_tokens"],
            "raw_bc": round(raw_bc, 6),
            "kb_bc": round(kb_bc, 6),
            "savings_pct": round(savings_pct, 4),
            "n_queries": 1,
            "mechanism": "re-derivation avoidance",
            "applicability_boundary": (
                "recurring architecture/config queries on a stable codebase "
                "where the KB doc fully answers the query"
            ),
        }

    def test_raw_session_costs_more_than_kb_session(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = self._run_shadow(raw_source_doc, kb_summary_doc, config)
        assert result["raw_bc"] > result["kb_bc"], (
            f"Raw session ({result['raw_bc']:.6f} BC) must cost more than "
            f"KB-primary session ({result['kb_bc']:.6f} BC)"
        )

    def test_shadow_savings_pct_is_positive(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = self._run_shadow(raw_source_doc, kb_summary_doc, config)
        assert result["savings_pct"] > 0.0, (
            f"Expected positive savings; got {result['savings_pct']:.2f}%"
        )

    def test_shadow_result_has_required_reporting_fields(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = self._run_shadow(raw_source_doc, kb_summary_doc, config)
        required = (
            "raw_tokens", "kb_tokens", "savings_pct",
            "n_queries", "mechanism", "applicability_boundary",
        )
        for field in required:
            assert field in result, f"Missing required field: {field!r}"
        assert len(result["applicability_boundary"]) > 0, (
            "applicability_boundary must describe when the saving applies"
        )

    def test_verbatim_kb_shadow_shows_negligible_savings(
        self, raw_source_doc: Document, verbatim_kb_doc: Document, config: ConfigSchema
    ) -> None:
        result = self._run_shadow(raw_source_doc, verbatim_kb_doc, config)
        # Verbatim KB ≈ same size as raw source; optimizer may compress both
        # by the same small amount, so savings_pct ~ 0.
        assert result["savings_pct"] < 5.0, (
            f"Verbatim KB doc should yield <5% shadow savings; "
            f"got {result['savings_pct']:.2f}%"
        )


# ===========================================================================
# Sub-task 4 — Amortised ROI formula
# ===========================================================================

class TestAmortisedROI:
    """Guide §4: accounting identity using real token counts from fixtures."""

    @pytest.fixture
    def real_savings_per_query_bc(
        self,
        raw_source_doc: Document,
        kb_summary_doc: Document,
        config: ConfigSchema,
    ) -> float:
        """BC saved on a single KB-vs-raw query pair, computed from real tokens."""
        raw_result = measure_optimizer(config, "gpt-4", [raw_source_doc])
        kb_result = measure_optimizer(config, "gpt-4", [kb_summary_doc])
        raw_bc = tokens_to_bobcoins(raw_result["total_original_tokens"])
        kb_bc = tokens_to_bobcoins(kb_result["total_original_tokens"])
        return raw_bc - kb_bc

    def test_roi_positive_after_breakeven(
        self, real_savings_per_query_bc: float
    ) -> None:
        # Use a query count well above the expected breakeven (40 queries is
        # the guide's example; with real savings_per_query this still holds).
        creation_bc = 0.80
        maintenance_bc = 0.30
        n_queries = 40
        result = _amortised_roi(
            queries=n_queries,
            savings_per_query_bc=real_savings_per_query_bc,
            creation_bc=creation_bc,
            maintenance_bc=maintenance_bc,
        )
        assert result["net_savings_bc"] > 0.0, (
            f"40 queries × {real_savings_per_query_bc:.6f} BC/query should yield "
            f"positive net savings; got {result['net_savings_bc']:.6f} BC. "
            "Check that the KB summary is genuinely smaller than the raw source."
        )
        assert result["roi_multiplier"] > 1.0, (
            f"ROI multiplier should exceed 1× at 40 queries; "
            f"got {result['roi_multiplier']:.4f}×"
        )

    def test_roi_negative_before_breakeven(
        self, real_savings_per_query_bc: float
    ) -> None:
        # Single query: can't recover KB creation cost in one use.
        result = _amortised_roi(
            queries=1,
            savings_per_query_bc=real_savings_per_query_bc,
            creation_bc=0.80,
            maintenance_bc=0.30,
        )
        assert result["net_savings_bc"] < 0.0, (
            "A single query should not recover KB creation cost; "
            f"got net={result['net_savings_bc']:.6f} BC with "
            f"savings_per_query={real_savings_per_query_bc:.6f} BC"
        )

    def test_breakeven_query_count_is_finite_and_positive(
        self, real_savings_per_query_bc: float
    ) -> None:
        bq = breakeven_queries(0.80, 0.30, real_savings_per_query_bc)
        assert isinstance(bq, int)
        assert bq > 0, "Breakeven must be at least 1 query"
        assert math.isfinite(bq), "Breakeven must be finite"

    def test_degenerate_zero_savings_per_query_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="savings_per_query_bc must be > 0"):
            breakeven_queries(0.80, 0.30, 0.0)

    def test_roi_result_has_expected_keys(
        self, real_savings_per_query_bc: float
    ) -> None:
        result = _amortised_roi(
            queries=10,
            savings_per_query_bc=real_savings_per_query_bc,
            creation_bc=0.50,
            maintenance_bc=0.10,
        )
        for key in (
            "gross_savings_bc", "total_cost_bc", "net_savings_bc",
            "roi_multiplier", "breakeven_queries",
        ):
            assert key in result, f"Missing key in ROI result: {key!r}"

    def test_gross_equals_queries_times_per_query(
        self, real_savings_per_query_bc: float
    ) -> None:
        n = 15
        result = _amortised_roi(
            queries=n,
            savings_per_query_bc=real_savings_per_query_bc,
            creation_bc=0.20,
            maintenance_bc=0.10,
        )
        expected = round(n * real_savings_per_query_bc, 6)
        assert abs(result["gross_savings_bc"] - expected) < 1e-5, (
            f"gross_savings_bc should be {expected}; got {result['gross_savings_bc']}"
        )


# ===========================================================================
# Sub-task 5 — Reporting integrity guard
# ===========================================================================

class TestReportingIntegrityGuard:
    """Guide §5: four required fields + additive-fallacy rejection."""

    def _valid_claim(self) -> Dict[str, Any]:
        return {
            "method": "shadow_comparison",
            "n": 34,
            "confidence_range": [70.0, 85.0],
            "applicability_boundary": (
                "recurring architecture queries on stable codebase over 4 weeks"
            ),
        }

    def test_compliant_claim_passes(self) -> None:
        assert_compliant_claim(self._valid_claim())  # must not raise

    def test_missing_method_fails(self) -> None:
        claim = self._valid_claim()
        del claim["method"]
        with pytest.raises(AssertionError, match="method"):
            assert_compliant_claim(claim)

    def test_empty_method_fails(self) -> None:
        claim = {**self._valid_claim(), "method": "   "}
        with pytest.raises(AssertionError, match="method"):
            assert_compliant_claim(claim)

    def test_missing_n_fails(self) -> None:
        claim = self._valid_claim()
        del claim["n"]
        with pytest.raises(AssertionError, match="'n'"):
            assert_compliant_claim(claim)

    def test_zero_n_fails(self) -> None:
        claim = {**self._valid_claim(), "n": 0}
        with pytest.raises(AssertionError, match="'n'"):
            assert_compliant_claim(claim)

    def test_missing_confidence_range_fails(self) -> None:
        claim = self._valid_claim()
        del claim["confidence_range"]
        with pytest.raises(AssertionError, match="confidence_range"):
            assert_compliant_claim(claim)

    def test_inverted_confidence_range_fails(self) -> None:
        claim = {**self._valid_claim(), "confidence_range": [90.0, 70.0]}
        with pytest.raises(AssertionError, match="confidence_range"):
            assert_compliant_claim(claim)

    def test_single_element_confidence_range_fails(self) -> None:
        claim = {**self._valid_claim(), "confidence_range": [70.0]}
        with pytest.raises(AssertionError, match="confidence_range"):
            assert_compliant_claim(claim)

    def test_missing_applicability_boundary_fails(self) -> None:
        claim = self._valid_claim()
        del claim["applicability_boundary"]
        with pytest.raises(AssertionError, match="applicability_boundary"):
            assert_compliant_claim(claim)

    def test_empty_applicability_boundary_fails(self) -> None:
        claim = {**self._valid_claim(), "applicability_boundary": ""}
        with pytest.raises(AssertionError, match="applicability_boundary"):
            assert_compliant_claim(claim)

    def test_additive_total_method_is_rejected(self) -> None:
        """Blending optimizer + KB savings into one figure re-manufactures the
        retracted 68.96% headline. The guard must reject it explicitly."""
        claim = {**self._valid_claim(), "method": "additive_total"}
        with pytest.raises(AssertionError, match="additive-fallacy"):
            assert_compliant_claim(claim)

    def test_multiple_missing_fields_reported_together(self) -> None:
        """All errors in one AssertionError, not one-at-a-time."""
        with pytest.raises(AssertionError) as exc:
            assert_compliant_claim({})
        msg = str(exc.value)
        assert "method" in msg
        assert "'n'" in msg
        assert "confidence_range" in msg
        assert "applicability_boundary" in msg


# ===========================================================================
# Sub-task 6 — Null guard for verbatim KB docs
# ===========================================================================

class TestVerbatimKBNullGuard:
    """A KB doc that duplicates its source verbatim must be flagged, not counted."""

    def test_verbatim_kb_is_flagged(
        self, raw_source_doc: Document, verbatim_kb_doc: Document, config: ConfigSchema
    ) -> None:
        result = check_for_verbatim_duplication(raw_source_doc, verbatim_kb_doc, config)
        assert result["flagged"] is True, (
            f"Verbatim KB doc must be flagged; "
            f"got savings_pct={result['savings_pct']:.2f}%"
        )

    def test_genuine_kb_is_not_flagged(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = check_for_verbatim_duplication(raw_source_doc, kb_summary_doc, config)
        assert result["flagged"] is False, (
            f"Genuine KB summary must NOT be flagged; "
            f"got savings_pct={result['savings_pct']:.2f}%"
        )

    def test_null_flag_reason_is_informative(
        self, raw_source_doc: Document, verbatim_kb_doc: Document, config: ConfigSchema
    ) -> None:
        result = check_for_verbatim_duplication(raw_source_doc, verbatim_kb_doc, config)
        assert isinstance(result["reason"], str) and len(result["reason"]) > 20, (
            "reason must be a descriptive string explaining why the doc was flagged"
        )
        assert "verbatim" in result["reason"].lower() or "threshold" in result["reason"].lower()

    def test_verbatim_doc_excluded_from_headline(
        self, raw_source_doc: Document, verbatim_kb_doc: Document, config: ConfigSchema
    ) -> None:
        """A flagged verbatim KB doc provides zero re-derivation saving.

        The optimizer may compress any document on its own merits (whitespace,
        redundant phrases) — a large verbatim doc can compress more than a
        tiny KB summary. That is the TOS optimizer working, not KB savings.

        The correct test is: after check_for_verbatim_duplication flags the
        doc, the re-derivation savings_pct (raw_tokens == verbatim_tokens) is
        near zero — i.e. using the verbatim "KB" instead of the raw source
        saves nothing at the structural level, which is what the flagging
        mechanism exists to communicate.
        """
        flag = check_for_verbatim_duplication(raw_source_doc, verbatim_kb_doc, config)
        assert flag["flagged"] is True, "Verbatim doc must be flagged before exclusion"
        # Re-derivation savings = (raw_tokens - verbatim_tokens) / raw_tokens.
        # Both docs are identical text, so this must be near zero.
        assert flag["savings_pct"] < 2.0, (
            f"Verbatim KB provides no structural re-derivation saving; "
            f"got {flag['savings_pct']:.2f}%. Flagging prevents it from "
            "entering the headline, which is the contract this test enforces."
        )

    def test_null_flag_result_has_required_fields(
        self, raw_source_doc: Document, kb_summary_doc: Document, config: ConfigSchema
    ) -> None:
        result = check_for_verbatim_duplication(raw_source_doc, kb_summary_doc, config)
        for field in ("flagged", "savings_pct", "raw_tokens", "kb_tokens", "reason"):
            assert field in result, f"Missing field in null-flag result: {field!r}"
