"""D3 / MEM-13: the reproducible two-session write→retrieve→compound demo.

Session 1 analyzes the pinned fixture repo and writes ``generated`` KB docs;
session 2 queries the KB and must retrieve a session-1 finding. This is the
reproducible "prove it compounds" proof that replaces the retracted anecdote.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_DEMO_FILE = _REPO / "examples" / "compound-demo" / "compound_demo.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("compound_demo", _DEMO_FILE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def demo(monkeypatch):
    # The fixture repo is analyzed via a cwd-relative path (containment), so the
    # demo must run with cwd at the repo root.
    monkeypatch.chdir(_REPO)
    return _load_demo()


def test_compound_demo_session2_retrieves_session1(demo, tmp_path):
    """The headline: session 2 retrieves a doc session 1 wrote, manifest-backed."""
    manifest = demo.run_compound_demo(tmp_path / "kb")

    assert manifest["session1_docs_written"] >= 1, "session 1 wrote no docs"
    assert manifest["compounded"] is True, f"no compounding demonstrated: {manifest}"
    assert manifest["matched_ids"], "session 2 retrieved no session-1 finding"
    # Every matched id is one session 1 actually produced (no phantom match).
    assert set(manifest["matched_ids"]) <= set(manifest["session1_output_ids"])
    # Every retrieved id (fragments stripped) is file-level, not a chunk slug.
    assert all("#" not in rid for rid in manifest["session2_retrieved_ids"])


def test_compound_demo_manifest_is_reproducible(demo, tmp_path):
    """The demo emits a manifest with ids, counts, and a code SHA (reproducible)."""
    manifest = demo.run_compound_demo(tmp_path / "kb", code_sha="testsha123")

    for key in (
        "code_sha",
        "fixture",
        "session1_output_ids",
        "index_chunk_count",
        "session2_query",
        "session2_retrieved_ids",
        "matched_ids",
        "compounded",
    ):
        assert key in manifest, f"manifest missing {key}"
    assert manifest["code_sha"] == "testsha123"
    assert manifest["index_chunk_count"] >= 1
    assert manifest["fixture"].endswith("fixture-repo")
