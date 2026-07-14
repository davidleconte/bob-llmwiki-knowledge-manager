"""Tests for report assembly, serialization, and the human summary."""

from __future__ import annotations

import json
from pathlib import Path

from src.validation.report import build_report, human_summary, write_report

REPO_ROOT = Path(__file__).resolve().parents[2]


def _fixture_report() -> dict:
    manifest = {
        "code_sha": "0" * 40,
        "git_dirty": False,
        "data_hash": "deadbeef" * 8,
        "config": {"optimizer": {"max_tokens": 4096}},
        "seed": 0,
        "library_versions": {"tiktoken": "0.13.0"},
        "tiktoken_active": True,
        "model": "gpt-4",
        "python_version": "3.12.10",
        "platform": "test",
        "timestamp": "2026-07-14T00:00:00+00:00",
    }
    optimizer = {
        "n": 3,
        "mean_savings_pct": 20.0,
        "median_savings_pct": 19.0,
        "std_savings_pct": 5.0,
        "ci95_savings_pct": [18.0, 22.0],
        "mean_quality_score": 0.8,
        "quality_note": "lexical heuristic (_estimate_quality), not semantic fidelity",
        "total_original_tokens": 300,
        "total_optimized_tokens": 240,
        "aggregate_savings_pct": 20.0,
        "mean_latency_ms": 3.0,
        "p95_latency_ms": 6.0,
        "tiktoken_active": True,
        "per_document": [],
    }
    cache = {
        "requested_repeat_rate": 0.3,
        "actual_repeat_fraction": 0.3,
        "requests": 10,
        "hits": 3,
        "hit_rate_pct": 30.0,
        "note": "workload-dependent; NOT a system property; excluded from the savings headline",
    }
    truncation = {
        "budget_tokens": 256,
        "documents": 3,
        "documents_truncated": 2,
        "mean_removal_pct_when_truncated": 80.0,
        "lossy": True,
        "note": "lossy deletion, no fidelity guarantee; NOT counted as savings",
        "per_document": [],
    }
    null_test = {
        "n": 3,
        "mean_savings_pct": 0.5,
        "aggregate_savings_pct": 0.4,
        "threshold_pct": 5.0,
        "passed": True,
        "rationale": "shuffled input has no compressible redundancy",
    }
    return build_report(manifest, optimizer, cache, truncation, null_test)


def test_build_report_keeps_mechanisms_separate():
    report = _fixture_report()
    assert report["schema"] == "bob-validation/v1"
    for section in (
        "optimizer_compression",
        "cache_recompute_avoidance",
        "truncation_budget_fit",
        "null_test",
    ):
        assert section in report
    assert report["headline"]["metric"] == "optimizer_compression_mean_savings_pct"
    assert report["headline"]["value"] == 20.0


def test_human_summary_leads_with_n_and_avoids_verdict():
    summary = human_summary(_fixture_report())
    assert "corpus documents (N):" in summary
    assert "HEADLINE" in summary and "NULL TEST" in summary
    # The report must not print a "VALIDATED" verdict -- only measured numbers.
    assert "VALIDATED" not in summary
    assert "PASS" in summary


def test_write_report_writes_both_files(tmp_path):
    report = _fixture_report()
    report_path, manifest_path = write_report(tmp_path / "out", report, report["manifest"])
    assert report_path.exists() and manifest_path.exists()
    assert json.loads(report_path.read_text())["headline"]["value"] == 20.0
    assert json.loads(manifest_path.read_text())["model"] == "gpt-4"
