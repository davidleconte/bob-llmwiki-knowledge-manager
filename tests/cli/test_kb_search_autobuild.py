"""D1/MEM-08: kb-search auto-builds a missing index (no silent keyword degradation).

The read path used to wire the embedding index only ``if index_path.exists()`` and
otherwise fell through to keyword-only retrieval with no signal — so a fresh
checkout silently ran the weaker path. kb-search now builds the index once on the
first query, with a notice, and uses the validated retrieval stack.
"""

from __future__ import annotations

from pathlib import Path

from src.cache.embeddings import EmbeddingGenerator
from src.cli import main
from src.embeddings.index import PersistentEmbeddingIndex
from src.kb_paths import resolve_index_path


def _make_repo(tmp_path: Path) -> Path:
    # A self-contained tmp repo: the .git marker pins repo_root_for() here so the
    # index is built inside tmp, never in the real repo.
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    concepts = root / "docs" / "knowledge-base" / "concepts"
    concepts.mkdir(parents=True)
    (concepts / "caching.md").write_text(
        "# Caching\n\nCache eviction and TTL strategies for retrieval and lookups.\n",
        encoding="utf-8",
    )
    (concepts / "graph.md").write_text(
        "# Graph\n\nKnowledge graph edges, pagerank, and traversal for ranking.\n",
        encoding="utf-8",
    )
    return root / "docs" / "knowledge-base"


def test_missing_index_autobuilds(tmp_path, capsys):
    """RED->GREEN: a missing index is built on first query, not skipped."""
    kb = _make_repo(tmp_path)
    idx_path = resolve_index_path(kb)
    assert not idx_path.exists(), "precondition: no index yet"

    rc = main(["kb-search", "cache eviction strategies", "--kb-path", str(kb)])
    assert rc == 0

    # GREEN: the index was auto-built rather than silently degrading to keyword-only.
    assert idx_path.exists(), "kb-search did not auto-build the missing index"
    built = PersistentEmbeddingIndex(EmbeddingGenerator(), index_path=idx_path)
    assert built.doc_count > 0, "auto-built index has no vectors"

    # The degradation is observable, not silent.
    assert "building embedding index (first run)" in capsys.readouterr().err


def test_existing_index_not_rebuilt_without_refresh(tmp_path, capsys):
    """A second query reuses the built index — no rebuild notice, still index-backed."""
    kb = _make_repo(tmp_path)
    assert main(["kb-search", "caching", "--kb-path", str(kb)]) == 0
    capsys.readouterr()  # drain the first-run notice

    assert main(["kb-search", "graph ranking", "--kb-path", str(kb)]) == 0
    err = capsys.readouterr().err
    assert "building embedding index (first run)" not in err
    assert resolve_index_path(kb).exists()
