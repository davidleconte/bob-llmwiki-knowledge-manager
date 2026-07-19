"""W2-2(d)/(b): canonical index/graph path resolution + staleness reporting.

* W2-2(d) — writers (indexer/graph-build/kb-status) and readers (kb-search,
  research agent) must resolve the index/graph to the SAME location. The old
  reader anchored at ``kb_path.parent/.bob/kb-index`` (``docs/.bob/kb-index``),
  while the index is written to the repo-root ``.bob/kb-index`` — so the wired
  retrieval stack silently found no index in the default layout.
* W2-2(b) — the index must report staleness (changed/deleted docs) so the read
  path can warn instead of silently serving stale vectors.
"""
from pathlib import Path

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex
from src.kb_paths import repo_root_for, resolve_graph_path, resolve_index_path


def _section(title: str, word: str) -> str:
    body = (word + " ") * 20
    return f"## {title}\n\n{body.strip()}\n"


def _make_kb(root: Path) -> Path:
    kb = root / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    return kb


def _write(kb: Path, cat: str, name: str, body: str) -> Path:
    p = kb / cat / name
    p.write_text(body, encoding="utf-8")
    return p


def test_resolver_anchors_at_repo_root_not_kb_parent(tmp_path):
    root = tmp_path / "repo"
    (root / ".bob").mkdir(parents=True)
    kb = root / "docs" / "knowledge-base"
    kb.mkdir(parents=True)

    assert repo_root_for(kb) == root
    assert resolve_index_path(kb) == root / ".bob" / "kb-index"
    assert resolve_graph_path(kb) == root / ".bob" / "kb-graph.json"
    # The old reader bug: docs-anchored path is NOT where the index lives.
    assert resolve_index_path(kb) != kb.parent / ".bob" / "kb-index"


def test_writer_and_reader_agree_on_index_location(tmp_path):
    root = tmp_path / "repo"
    (root / ".bob").mkdir(parents=True)
    kb = root / "docs" / "knowledge-base"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    (kb / "concepts" / "a.md").write_text(_section("Alpha Overview", "alpha"), encoding="utf-8")

    # Writer builds at the canonical path.
    write_path = resolve_index_path(kb)
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), index_path=write_path)
    idx.rebuild(kb)

    # Reader resolves to the same populated directory (old reader path is empty).
    read_path = resolve_index_path(kb)
    assert (read_path / "manifest.json").exists()
    assert read_path == write_path
    assert not (kb.parent / ".bob" / "kb-index").exists()


def test_stale_files_detects_changed_and_deleted(tmp_path):
    kb = _make_kb(tmp_path)
    idx_path = tmp_path / ".bob" / "kb-index"
    a = _write(kb, "concepts", "a.md", _section("Alpha", "alpha"))
    _write(kb, "concepts", "b.md", _section("Beta", "beta"))

    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    idx.rebuild(kb)
    assert idx.stale_files(kb) == {"changed": [], "deleted": []}

    # Change a.md, delete b.md — a fresh reader must see both as stale.
    a.write_text(_section("Alpha", "alpha") + _section("Extra", "extra"), encoding="utf-8")
    (kb / "concepts" / "b.md").unlink()

    idx2 = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    stale = idx2.stale_files(kb)
    assert "concepts/a.md" in stale["changed"], stale
    assert "concepts/b.md" in stale["deleted"], stale
