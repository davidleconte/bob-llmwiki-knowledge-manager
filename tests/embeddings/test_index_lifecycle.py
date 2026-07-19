"""CODE-04/11/15 regression: index lifecycle (deletion, stale chunks, dim guard).

* CODE-04 — a file deleted from disk must have its chunk rows reclaimed on
  rebuild; the index must not "grow forever".
* CODE-11 — editing a file to remove a section must drop that section's stale
  ``#slug`` chunk rows (``index_document`` only appends/updates, never deletes).
* CODE-15 — loading an index whose stored embedding dimension differs from the
  active embedder must discard the stale index rather than crash in ``search()``.

RED on the pre-fix index (deleted rows persist; a dim swap raises in the matmul),
GREEN once ``rebuild()`` reconciles deletions and ``_ensure_loaded`` guards dim.

The chunker splits on ``##`` (H2) sections and drops sections shorter than
``MIN_CHUNK_CHARS`` (50), so fixtures use H2 headings with padded bodies.
"""
from pathlib import Path

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex


def _section(title: str, word: str) -> str:
    body = (word + " ") * 20  # ~120 chars, comfortably above MIN_CHUNK_CHARS
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


def test_deleted_file_rows_are_reclaimed(tmp_path):
    kb = _make_kb(tmp_path)
    idx_path = tmp_path / ".bob" / "kb-index"
    _write(kb, "concepts", "a.md", _section("Alpha Overview", "alpha"))
    b = _write(kb, "concepts", "b.md", _section("Beta Overview", "beta"))

    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    idx.rebuild(kb)
    before = idx.doc_count
    assert before >= 2
    assert any(d.startswith("concepts/b.md") for d in idx._doc_ids)

    # Delete b.md and rebuild in a fresh instance (simulates a new session).
    b.unlink()
    idx2 = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    total = idx2.rebuild(kb)
    assert not any(d.startswith("concepts/b.md") for d in idx2._doc_ids), idx2._doc_ids
    assert total < before
    assert idx2._matrix is not None
    assert idx2._matrix.shape[0] == len(idx2._doc_ids)  # row/manifest invariant


def test_removed_section_chunks_are_dropped(tmp_path):
    kb = _make_kb(tmp_path)
    idx_path = tmp_path / ".bob" / "kb-index"
    doc = _write(
        kb,
        "guides",
        "multi.md",
        _section("First", "first") + "\n" + _section("Second", "second"),
    )
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    idx.rebuild(kb)
    before = [d for d in idx._doc_ids if d.startswith("guides/multi.md")]
    assert len(before) >= 2

    # Edit the file to drop the Second section, rebuild fresh.
    doc.write_text(_section("First", "first"), encoding="utf-8")
    idx2 = PersistentEmbeddingIndex(EmbeddingGenerator(), idx_path)
    idx2.rebuild(kb)
    after = [d for d in idx2._doc_ids if d.startswith("guides/multi.md")]
    assert len(after) < len(before), (before, after)
    assert idx2._matrix.shape[0] == len(idx2._doc_ids)


def test_dimension_mismatch_discards_stale_index(tmp_path):
    kb = _make_kb(tmp_path)
    idx_path = tmp_path / ".bob" / "kb-index"
    _write(kb, "concepts", "a.md", _section("Alpha Overview", "alpha"))

    idx = PersistentEmbeddingIndex(EmbeddingGenerator(max_features=1000), idx_path)
    idx.rebuild(kb)
    assert idx.doc_count > 0

    # New session with a different embedding dimension (simulates a backend swap).
    idx2 = PersistentEmbeddingIndex(EmbeddingGenerator(max_features=384), idx_path)
    # Must NOT raise in the matmul; the stale-dim index is discarded → empty.
    assert idx2.search("alpha") == []
    assert idx2.doc_count == 0
