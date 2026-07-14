"""Tests for corpus loading, hashing, and the null corpus."""

from __future__ import annotations

import json
from pathlib import Path

from src.validation.corpus import (
    Document,
    hash_corpus,
    load_repo_prose,
    load_session_transcripts,
    make_null_corpus,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

PROSE = (
    "The knowledge base stores durable technical prose so that an agent need "
    "not re-derive the same reasoning every session. Retrieval beats "
    "re-derivation on cost and on consistency across runs."
)


def test_load_repo_prose_returns_sorted_markdown():
    docs = load_repo_prose(REPO_ROOT)
    assert docs, "expected a non-empty real-prose corpus"
    sources = [d.source for d in docs]
    assert sources == sorted(sources), "corpus must be deterministically ordered"
    assert all(s.endswith(".md") for s in sources)


def test_load_repo_prose_excludes_synthetic_data():
    docs = load_repo_prose(REPO_ROOT)
    assert all("evaluation/data" not in d.source for d in docs)


def test_hash_corpus_is_order_independent_and_content_sensitive():
    a = Document("a.md", "alpha")
    b = Document("b.md", "beta")
    assert hash_corpus([a, b]) == hash_corpus([b, a])
    assert hash_corpus([a, b]) != hash_corpus([a, Document("b.md", "changed")])


def test_make_null_corpus_is_seeded_and_preserves_words():
    docs = [Document("d.md", PROSE)]
    null_a = make_null_corpus(docs, seed=0)
    null_b = make_null_corpus(docs, seed=0)
    assert [d.text for d in null_a] == [d.text for d in null_b], "same seed -> same shuffle"
    # Word multiset preserved; only order destroyed.
    assert sorted(null_a[0].text.split()) == sorted(PROSE.split())
    assert null_a[0].source == "null:d.md"
    # Single-spaced (no compressible whitespace left).
    assert "  " not in null_a[0].text


def test_make_null_corpus_different_seed_differs():
    docs = [Document("d.md", PROSE)]
    assert make_null_corpus(docs, 0)[0].text != make_null_corpus(docs, 12345)[0].text


def test_load_session_transcripts_absent_dir_is_empty():
    assert load_session_transcripts(Path("/no/such/dir")) == []


def test_load_session_transcripts_parses_json_and_skips_mocks(tmp_path):
    (tmp_path / "real.json").write_text(json.dumps({"prompt": PROSE}), encoding="utf-8")
    (tmp_path / "test_mock.json").write_text(json.dumps({"prompt": PROSE}), encoding="utf-8")
    (tmp_path / "note.md").write_text(PROSE, encoding="utf-8")
    docs = load_session_transcripts(tmp_path)
    sources = {d.source for d in docs}
    assert "session:real.json" in sources
    assert "session:note.md" in sources
    assert not any("test_mock" in s for s in sources), "mock test_* files must be skipped"
