"""ATK-GATE-01 regression: the corpus-composition guard.

The validation harness deliberately does NOT gate the savings *magnitude* (gating a
measurement re-incentivises fabrication). It DOES gate corpus *composition*: a number
is only publishable if its corpus is representative. These tests pin the three
cherry-pick signatures the guard rejects and confirm a representative corpus passes.
"""

from __future__ import annotations

import pytest

from src.validation import (
    MAX_MEAN_MEDIAN_DIVERGENCE_PP,
    MAX_TOP_DOC_TOKEN_SHARE,
    MIN_CORPUS_N,
    composition_ok,
    validation_ok,
)
from src.validation.manifest import REQUIRED_FIELDS
from src.validation.measure import _corpus_composition


def _good_comp(**over):
    base = {
        "n_docs": 100,
        "top_doc_token_share": 0.10,
        "mean_savings_pct": 20.0,
        "median_savings_pct": 19.0,
        "mean_median_divergence_pp": 1.0,
        "trimmed_mean_savings_pct": 19.5,
    }
    base.update(over)
    return base


def _report(comp):
    return {"optimizer_compression": {"corpus_composition": comp}}


def _full_report(comp):
    """A report that passes null/manifest/tiktoken so only composition varies."""
    manifest = {f: "x" for f in REQUIRED_FIELDS}
    manifest["config"] = {"env": "test"}
    manifest["library_versions"] = {"pytest": "9"}
    manifest["tiktoken_active"] = True
    return {
        "null_test": {"passed": True, "mean_savings_pct": 0.5, "threshold_pct": 5.0},
        "manifest": manifest,
        "optimizer_compression": {"corpus_composition": comp},
    }


# ── composition_ok ───────────────────────────────────────────────────────────


def test_representative_corpus_passes():
    ok, reasons = composition_ok(_report(_good_comp()))
    assert ok, reasons
    assert reasons == []


def test_too_few_docs_is_rejected():
    ok, reasons = composition_ok(_report(_good_comp(n_docs=MIN_CORPUS_N - 1)))
    assert not ok
    assert any("too small" in r for r in reasons)


def test_single_document_dominating_tokens_is_rejected():
    share = MAX_TOP_DOC_TOKEN_SHARE + 0.3
    ok, reasons = composition_ok(_report(_good_comp(top_doc_token_share=share)))
    assert not ok
    assert any("dominates" in r for r in reasons)


def test_mean_far_from_median_is_rejected():
    div = MAX_MEAN_MEDIAN_DIVERGENCE_PP + 10.0
    ok, reasons = composition_ok(_report(_good_comp(mean_median_divergence_pp=div)))
    assert not ok
    assert any("outliers" in r for r in reasons)


# ── _corpus_composition metric computation ───────────────────────────────────


def test_composition_metrics_expose_concentration_and_skew():
    scored = [
        {"savings_percentage": 10.0, "original_tokens": 100},
        {"savings_percentage": 10.0, "original_tokens": 100},
        {"savings_percentage": 90.0, "original_tokens": 800},  # one huge, high-savings doc
    ]
    comp = _corpus_composition(scored, total_original=1000)
    assert comp["n_docs"] == 3
    assert comp["top_doc_token_share"] == pytest.approx(0.8)
    assert comp["median_savings_pct"] == pytest.approx(10.0)
    assert comp["mean_savings_pct"] == pytest.approx(36.6667, abs=1e-3)
    assert comp["mean_median_divergence_pp"] == pytest.approx(26.6667, abs=1e-3)


# ── wiring: validation_ok incorporates the composition guard ─────────────────


def test_validation_ok_flags_a_cherry_picked_corpus():
    ok, reasons = validation_ok(_full_report(_good_comp(n_docs=3, top_doc_token_share=0.9)))
    assert not ok
    assert any("too small" in r for r in reasons)
    assert any("dominates" in r for r in reasons)


def test_validation_ok_passes_a_representative_corpus():
    ok, reasons = validation_ok(_full_report(_good_comp()))
    assert ok, reasons
