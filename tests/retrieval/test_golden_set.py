"""CLM-06: the retrieval p@3 golden set + its manifest-backed report.

Guards the golden set's integrity (every expected doc still resolves) and that
the committed measurement is manifest-backed (code_sha/git_dirty/data_hash/seed/
library_versions), so the headline retrieval number can never again be an
un-provenanced literal.
"""
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KB = REPO_ROOT / "docs" / "knowledge-base"
GOLDEN = REPO_ROOT / "evaluation" / "data" / "retrieval_golden_set.json"
REPORT = REPO_ROOT / "evaluation" / "results" / "retrieval-2026-07-19" / "report.json"

_MANIFEST_FIELDS = ("code_sha", "git_dirty", "data_hash", "seed", "library_versions")


def test_golden_set_integrity():
    """All 25 expected docs must resolve to a real KB file (no rot)."""
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    queries = data["queries"]
    assert len(queries) == 25
    for q in queries:
        assert q["query"] and q["expected_doc_id"], q
        assert (KB / q["expected_doc_id"]).exists(), f"golden doc missing: {q['expected_doc_id']}"


def test_committed_report_is_manifest_backed():
    """The committed p@3 report must carry a full reproducibility manifest."""
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert 0.0 <= report["p_at_3_wired"] <= 1.0
    assert report["n_queries"] == 25
    manifest = report["manifest"]
    for field in _MANIFEST_FIELDS:
        assert field in manifest, f"manifest missing {field}"


def test_top_distinct_docs_dedupes_and_strips_slug():
    from evaluation.scripts.score_retrieval import _top_distinct_docs

    results = [
        {"file": "concepts/a.md#intro"},
        {"file": "concepts/a.md#body"},  # same doc, different chunk → dedup
        {"file": "guides/b.md"},
        {"file": "references/c.md#x"},
    ]
    assert _top_distinct_docs(results, 3) == ["concepts/a.md", "guides/b.md", "references/c.md"]
