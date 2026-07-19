"""C4 / ATK-GATE-01: held-out corpus reproduction gate.

The composition guard catches obvious cherry-pick signatures (tiny N, one doc
dominating, mean/median divergence). This gate closes the subtler one: a corpus A
composed to inflate the headline while every composition metric stays clean. The
defence is a FROZEN i.i.d. slice of the same corpus (corpus B) held out from A. An
honest headline reproduces on B within sampling error; a cherry-picked A diverges,
because B was frozen independently and cannot be pre-arranged.
"""

from __future__ import annotations

import json

from src.validation import (
    MAX_HOLDOUT_DIVERGENCE_PP,
    holdout_ok,
    load_holdout,
    repo_root,
    run_validation,
    validation_ok,
)
from src.validation.corpus import load_holdout_paths, load_repo_prose

PROSE = (
    "A durable knowledge base lets an agent retrieve prior reasoning instead of "
    "re-deriving it every session, which lowers token cost and improves "
    "consistency. Whitespace normalization and redundant-phrase removal shrink "
    "the prompt with little loss of meaning when structure is preserved."
)


# ---- frozen manifest + disjointness (real repo) ---- #


def test_holdout_manifest_is_frozen_and_nonempty():
    paths = load_holdout_paths(repo_root())
    assert paths, "the hold-out manifest must list frozen paths"
    docs = load_holdout(repo_root())
    assert docs, "hold-out corpus B must load at least one document"
    assert {d.source for d in docs} <= paths


def test_holdout_is_disjoint_from_corpus_a():
    """Corpus A (measured) and corpus B (hold-out) must not overlap."""
    a = {d.source for d in load_repo_prose(repo_root())}
    b = {d.source for d in load_holdout(repo_root())}
    assert a and b
    assert a.isdisjoint(b), f"A and B overlap: {sorted(a & b)[:5]}"


# ---- gate logic (synthetic reports): RED->GREEN ---- #


def _report(primary: float, holdout: float) -> dict:
    """Minimal report carrying only what the holdout/validation gates read."""
    return {
        "null_test": {"passed": True, "mean_savings_pct": 0.0, "threshold_pct": 5.0},
        "manifest": {"tiktoken_active": True},
        "optimizer_compression": {
            "corpus_composition": {
                "n_docs": 100,
                "top_doc_token_share": 0.1,
                "mean_median_divergence_pp": 2.0,
            }
        },
        "holdout": {
            "primary_mean_savings_pct": primary,
            "mean_savings_pct": holdout,
            "divergence_pp": round(abs(primary - holdout), 4),
        },
    }


def test_holdout_reproduction_passes():
    ok, reasons = holdout_ok(_report(primary=7.0, holdout=6.8))
    assert ok and reasons == []


def test_holdout_divergence_blocks_publish():
    """RED->GREEN: a headline that does not reproduce on B is blocked.

    Removing holdout_ok from validation_ok lets this cherry-pick-shaped report pass;
    with the gate wired in it fails with a hold-out reason.
    """
    report = _report(primary=16.0, holdout=7.0)  # 9pp — the measured cherry-pick signal
    ok, reasons = holdout_ok(report)
    assert not ok
    assert any("reproduce" in r and "hold-out" in r for r in reasons)

    # And it propagates through the top-level gate.
    vok, vreasons = validation_ok(report)
    assert not vok
    assert any("hold-out" in r for r in vreasons)


def test_holdout_at_tolerance_boundary():
    just_under = holdout_ok(_report(7.0, 7.0 + MAX_HOLDOUT_DIVERGENCE_PP - 0.1))
    just_over = holdout_ok(_report(7.0, 7.0 + MAX_HOLDOUT_DIVERGENCE_PP + 0.1))
    assert just_under[0] is True
    assert just_over[0] is False


def test_holdout_absent_is_not_applicable():
    """A report with no holdout block (synthetic test root) is not gated on it."""
    ok, reasons = holdout_ok({"manifest": {}})
    assert ok and reasons == []


# ---- integration: run_validation attaches + reproduces ---- #


def _make_temp_corpus(root, n=44):
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True)
    for i in range(n):
        # Distinct per doc so the shuffled null collapses (identical/doubled prose
        # stays compressible even shuffled and would fail the null test).
        body = (
            f"{PROSE} Document {i} discusses subsystem {i} and its behaviour under "
            f"condition {i % 7}, with configuration option {i % 5} enabled."
        )
        (docs_dir / f"doc_{i:02d}.md").write_text(f"# Doc {i}\n\n{body}\n", encoding="utf-8")


def test_run_validation_attaches_reproducing_holdout(tmp_path):
    """A run whose repo carries a frozen manifest attaches a holdout block.

    The hold-out is an i.i.d. slice of the same docs, so on an honest corpus it
    reproduces and validation passes.
    """
    _make_temp_corpus(tmp_path)
    holdout_paths = [f"docs/doc_{i:02d}.md" for i in range(0, 44, 6)]  # ~8 docs
    manifest_dir = tmp_path / "evaluation" / "holdout"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "holdout-manifest.json").write_text(
        json.dumps({"paths": holdout_paths}), encoding="utf-8"
    )

    report = run_validation(root=tmp_path, corpus="repo", seed=0, write=False)

    assert "holdout" in report, "run must attach a holdout block when the manifest exists"
    assert report["holdout"]["n"] == len(holdout_paths)
    # Same distribution -> the headline reproduces on B -> the holdout gate passes.
    # (Full validation_ok also needs git manifest fields, which a tmp repo lacks —
    # that constraint is exercised separately in test_run.py.)
    assert report["holdout"]["divergence_pp"] <= MAX_HOLDOUT_DIVERGENCE_PP
    ok, reasons = holdout_ok(report)
    assert ok, reasons
