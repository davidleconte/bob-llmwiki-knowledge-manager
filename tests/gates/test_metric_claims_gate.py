"""C2 regression: the retrieval/accuracy metric-claim gate.

The savings gate only fires on *savings* keywords, so a retrieval-precision / p@N
overclaim (the withdrawn "p@3 44% -> 88%") was structurally invisible to every gate.
This gate closes that blind spot: a retrieval-metric keyword + percentage on a live
surface must cite a report or be retracted. It is deliberately scoped to named
retrieval metrics — bare English "accuracy"/"recall" are out of scope — and it
inherits the savings gate's banner/frozen logic (C1): frozen records stay exempt,
outward-facing live docs are scanned regardless of any banner.
"""

from scripts.check_metric_claims import line_is_unbacked_metric, scan_text_metrics

# ---------------------------------------------------------------------------
# The demonstrated hole: precision / p@N percentage overclaims must be flagged.
# ---------------------------------------------------------------------------


def test_precision_uplift_overclaim_flagged():
    assert line_is_unbacked_metric("Retrieval precision uplift: 44% -> 88%.")


def test_p_at_n_overclaim_flagged():
    assert line_is_unbacked_metric("Semantic index lifts p@3 to 88% correct in top 3.")


def test_ndcg_overclaim_flagged():
    assert line_is_unbacked_metric("nDCG jumps to 95% with the embedding index.")


# ---------------------------------------------------------------------------
# Backing: a report citation or a retraction token makes a metric line pass.
# ---------------------------------------------------------------------------


def test_report_citation_backs_metric():
    line = "p@3 = 84% (report.json: evaluation/results/retrieval-2026-07-19/report.json)."
    assert not line_is_unbacked_metric(line)


def test_retraction_backs_metric():
    assert not line_is_unbacked_metric('The "p@3 88%" claim was unverified and is retracted.')


def test_wrapped_report_citation_backs_metric():
    text = (
        "Retrieval precision p@3 = 88%\n"
        "(report.json: evaluation/results/retrieval-2026-07-19/report.json)."
    )
    assert not scan_text_metrics(text)


# ---------------------------------------------------------------------------
# Scope: non-retrieval "accuracy"/"recall" and decimal metrics are out of scope.
# ---------------------------------------------------------------------------


def test_bare_accuracy_out_of_scope():
    """Unrelated engineering accuracy (code-block detection, shell matching) must not trip."""
    assert not line_is_unbacked_metric("Code Block Detection: 98% accuracy.")


def test_bare_recall_verb_out_of_scope():
    assert not line_is_unbacked_metric("recall that 80% of teams adopt it.")


def test_decimal_metric_not_a_percentage_claim():
    """A decimal p@3 (no %) is a measured value, not a percentage overclaim."""
    assert not line_is_unbacked_metric("p@3 = 0.84 (21/25), matched by keyword-only.")


# ---------------------------------------------------------------------------
# C1 parity: banner logic is shared with the savings gate.
# ---------------------------------------------------------------------------


def test_outward_live_doc_metric_scanned_despite_banner():
    text = (
        "---\nstatus: active\naudience: [challenge-judges]\n---\n\n"
        "> **HISTORICAL SNAPSHOT.**\n\n- Retrieval precision uplift 44% -> 88%.\n"
    )
    assert scan_text_metrics(text), "outward-facing live doc must be scanned for metric overclaims"


def test_frozen_doc_metric_banner_suppressed():
    text = "---\nstatus: superseded\n---\n\n> **HISTORICAL SNAPSHOT.**\n\n- p@3 uplift to 88%.\n"
    assert not scan_text_metrics(text), "a frozen record's banner suppresses the metric scan"
