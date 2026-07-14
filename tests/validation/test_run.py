"""End-to-end tests for the orchestrator, the gate, and the CLI entry point."""

from __future__ import annotations

import json

from src.validation import run_validation, validation_ok
from src.validation.__main__ import main

PROSE = (
    "A durable knowledge base lets an agent retrieve prior reasoning instead of "
    "re-deriving it every session, which lowers token cost and improves "
    "consistency. Whitespace normalization and redundant-phrase removal shrink "
    "the prompt with little loss of meaning when structure is preserved."
)


def _make_temp_corpus(root):
    kb = root / "examples" / "demo" / "docs" / "knowledge-base" / "concepts"
    kb.mkdir(parents=True)
    (kb / "a.md").write_text(PROSE + "\n\n\n" + PROSE, encoding="utf-8")
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "b.md").write_text("# Title\n\n" + PROSE, encoding="utf-8")


def test_run_validation_on_temp_corpus(tmp_path):
    _make_temp_corpus(tmp_path)
    out = tmp_path / "out"
    report = run_validation(root=tmp_path, out_dir=out, corpus="repo", seed=0)

    assert report["headline"]["n"] == 2
    assert report["null_test"]["passed"] is True
    assert report["manifest"]["tiktoken_active"] is True
    # Files written with both report and manifest.
    assert (out / "report.json").exists()
    assert json.loads((out / "manifest.json").read_text())["extra"]["n_docs"] == 2


def test_validation_ok_flags_incomplete_provenance(tmp_path):
    # tmp_path is not a git repo, so code_sha is None -> the gate must catch it.
    _make_temp_corpus(tmp_path)
    report = run_validation(root=tmp_path, corpus="repo", seed=0, write=False)
    ok, reasons = validation_ok(report)
    assert ok is False
    assert any("manifest incomplete" in r for r in reasons)


def test_validation_ok_detects_null_failure():
    report = {
        "null_test": {"passed": False, "mean_savings_pct": 12.0, "threshold_pct": 5.0},
        "manifest": {
            "code_sha": "0" * 40,
            "git_dirty": False,
            "data_hash": "x",
            "config": {"a": 1},
            "seed": 0,
            "library_versions": {"tiktoken": "0.13.0"},
            "tiktoken_active": True,
            "model": "gpt-4",
            "python_version": "3.12",
            "platform": "t",
            "timestamp": "t",
        },
    }
    ok, reasons = validation_ok(report)
    assert ok is False
    assert any("null test FAILED" in r for r in reasons)


def test_empty_corpus_raises(tmp_path):
    # No markdown anywhere -> refuse to publish a number with no basis.
    from src.validation import EmptyCorpusError

    try:
        run_validation(root=tmp_path, corpus="repo", write=False)
    except EmptyCorpusError:
        return
    raise AssertionError("expected EmptyCorpusError on an empty corpus")


def test_main_happy_path_exits_zero(capsys):
    # Runs the real committed repo corpus (git provenance + tiktoken present).
    code = main(["--no-write", "--corpus", "repo", "--seed", "0"])
    captured = capsys.readouterr()
    assert code == 0
    assert "HEADLINE" in captured.out
