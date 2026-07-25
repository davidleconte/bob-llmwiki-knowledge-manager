"""C2 regression: the retrieval/accuracy metric-claim gate.

The savings gate only fires on *savings* keywords, so a retrieval-precision / p@N
overclaim (the withdrawn "p@3 44% -> 88%") was structurally invisible to every gate.
This gate closes that blind spot: a retrieval-metric keyword + percentage on a live
surface must cite a report or be retracted. It is deliberately scoped to named
retrieval metrics — bare English "accuracy"/"recall" are out of scope — and it
inherits the savings gate's banner/frozen logic (C1): frozen records stay exempt,
outward-facing live docs are scanned regardless of any banner.
"""

import subprocess
import sys
from pathlib import Path

from scripts.check_metric_claims import line_is_unbacked_metric, scan_text_metrics

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATE = _REPO_ROOT / "scripts" / "check_metric_claims.py"

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


def test_decimal_metric_is_a_claim_and_needs_backing():
    """Audit 2026-07-25 (G-3) — this test previously asserted the OPPOSITE, on the
    premise that "a decimal p@3 is a measured value, not a percentage overclaim".

    That premise did not survive the audit. Requiring a literal ``%`` made the gate
    blind to *every* retrieval figure the repo actually publishes, because the
    authoritative numbers are ratios (``p_at_3_wired = 0.84``) and every claim is
    written that way. The concrete casualty: ``docs/architecture/ARCHITECTURE.md:255``
    asserted a bare, unscoped ``p@3=0.88`` — an overclaim in decimal clothing — and no
    gate could see it. The blind spot was not an oversight; it was pinned here by a
    passing test.

    A ratio next to a metric keyword is now a claim, and must cite a report.
    """
    assert line_is_unbacked_metric("p@3 = 0.84 (21/25), matched by keyword-only.")


def test_decimal_metric_with_a_report_citation_passes():
    """The honest form still passes — backing is what matters, not the notation."""
    assert not line_is_unbacked_metric(
        "p@3 = 0.84 (21/25) — manifest: evaluation/results/retrieval-2026-07-19/report.json"
    )


def test_ratio_without_a_metric_keyword_is_ignored():
    """The keyword requirement is what keeps the ratio rule from firing on prose."""
    assert not line_is_unbacked_metric("target_reduction defaults to 0.3 in the schema.")


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


# ---------------------------------------------------------------------------
# CI-invocation regression: the gate must run as a direct script with only
# scripts/ on sys.path (no editable install, no repo root on the path) — exactly
# how CI's ruff/lint job invokes `python scripts/check_metric_claims.py`.
#
# The original C2 gate used `from scripts.check_savings_claims import ...`, which
# resolves under pytest / an editable install but raised
# `ModuleNotFoundError: No module named 'scripts'` on CI, where the lint job never
# runs `pip install -e .`. `-S` disables site-packages so the editable install is
# invisible, reproducing that condition; the sibling-import fallback keeps it green.
# ---------------------------------------------------------------------------


def test_gate_runs_as_direct_script_without_repo_on_path(tmp_path):
    """`python -S scripts/check_metric_claims.py --selftest` from a foreign cwd exits 0.

    Under ``-S`` the editable install is not on the path, so ``scripts`` is not an
    importable package — precisely the CI lint-job condition. Without the
    ModuleNotFoundError fallback this crashes at import time (RED); with it, the
    sibling import resolves and the selftest passes (GREEN).
    """
    result = subprocess.run(
        [sys.executable, "-S", str(_GATE), "--selftest"],
        capture_output=True,
        text=True,
        cwd=tmp_path,  # not the repo root: only scripts/ ends up on sys.path[0]
    )
    assert "No module named 'scripts'" not in result.stderr, (
        f"gate crashed on the sibling package import under CI conditions:\n{result.stderr}"
    )
    assert result.returncode == 0, (
        f"gate must run as a direct script without the repo on sys.path:\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
