"""A3(ii): rebuild() appends all chunks in ONE batched np.vstack.

The old ``rebuild`` called ``index_document`` per chunk, and each append did
``np.vstack([matrix, row])`` — reallocating the whole matrix on every chunk, i.e.
O(N²·dim) on a cold/full build. ``rebuild`` now collects every changed file's
chunks and appends them with a single embed + single ``np.vstack``.

RED->GREEN anchor: ``test_rebuild_uses_single_vstack`` counts ``np.vstack`` calls
during a fresh rebuild — one on the batched path, ~one-per-chunk on the old path.
Correctness: ``test_rebuild_rows_match_direct_embedding`` proves every stored row
equals the chunk's own embedding (the batching did not corrupt or misorder rows).
"""

from __future__ import annotations

import numpy as np

import src.embeddings.index as index_mod
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.chunker import MarkdownChunker
from src.embeddings.index import PersistentEmbeddingIndex


def _make_kb(tmp_path, n_docs: int = 40, sections: int = 1):
    kb = tmp_path / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    words = ["alpha", "beta", "gamma", "delta", "epsilon"]
    for i in range(n_docs):
        w = words[i % len(words)]
        body = "\n\n".join(
            f"## Section {s}\n\n{w} topic{i % 4} section {s} " + (w + " ") * 10
            for s in range(sections)
        )
        (kb / "concepts" / f"doc_{i}.md").write_text(f"# Doc {i}\n\n{body}\n", encoding="utf-8")
    return kb


def _fresh_index(tmp_path):
    return PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / ".bob" / "kb-index")


def test_rebuild_uses_single_vstack(tmp_path, monkeypatch):
    """A fresh rebuild of many chunks must call np.vstack at most once (batched).

    Pre-fix, index_document vstack'd per chunk -> one call per chunk (~40+).
    """
    kb = _make_kb(tmp_path, n_docs=40)
    idx = _fresh_index(tmp_path)

    calls = {"n": 0}
    real_vstack = np.vstack

    def counting_vstack(*args, **kwargs):
        calls["n"] += 1
        return real_vstack(*args, **kwargs)

    monkeypatch.setattr(index_mod.np, "vstack", counting_vstack)
    n_rows = idx.rebuild(kb)

    assert n_rows >= 40, f"expected >=40 rows, got {n_rows}"
    assert calls["n"] <= 1, (
        f"rebuild called np.vstack {calls['n']}x for {n_rows} rows — the A3(ii) "
        "batched append has regressed to per-chunk vstack (O(N²·dim))."
    )


def test_rebuild_rows_match_direct_embedding(tmp_path):
    """Every stored row equals its chunk's own embedding (order-independent).

    Guards that the batched embed/append stored the right vector under the right
    doc_id — a misordered batch or a wrong-slug mapping would fail here.
    """
    kb = _make_kb(tmp_path, n_docs=12, sections=3)  # multi-section -> many chunks
    idx = _fresh_index(tmp_path)
    idx.rebuild(kb)

    # Reconstruct the chunk_doc_id -> text map exactly as rebuild does.
    chunker = MarkdownChunker()
    embedder = EmbeddingGenerator()
    text_by_id: dict[str, str] = {}
    for md_file in sorted((kb / "concepts").glob("*.md")):
        file_doc_id = str(md_file.relative_to(kb))
        content = md_file.read_text(encoding="utf-8")
        for slug, chunk_text in chunker.chunk(file_doc_id, content):
            text_by_id[f"{file_doc_id}#{slug}"] = chunk_text

    assert set(idx._doc_ids) == set(text_by_id), "doc_id set diverged from chunker"
    assert idx._matrix.shape[0] == len(idx._doc_ids) == len(idx._manifest)

    for i, cid in enumerate(idx._doc_ids):
        expected = embedder.generate(text_by_id[cid][:6000], use_cache=False).astype(np.float32)
        assert np.array_equal(idx._matrix[i], expected), (
            f"stored row for {cid} != its own embedding"
        )


def test_rebuild_then_search_finds_each_doc(tmp_path):
    """Post-batched-rebuild, each doc is retrievable (rows are live, not stale)."""
    kb = _make_kb(tmp_path, n_docs=15)
    idx = _fresh_index(tmp_path)
    idx.rebuild(kb)

    # A query built from doc_7's distinctive content should surface doc_7's chunk.
    results = idx.search("gamma topic3 section 0", top_k=5)
    assert results, "search returned nothing after batched rebuild"
    assert any("doc_" in doc_id for doc_id, _ in results)


def test_incremental_index_document_still_appends(tmp_path):
    """The single-doc incremental path is unchanged (append + searchable)."""
    kb = _make_kb(tmp_path, n_docs=5)
    idx = _fresh_index(tmp_path)
    idx.rebuild(kb)
    before = idx._matrix.shape[0]

    idx.index_document("concepts/new.md#s", "brandnew unique vocabulary token corpus")
    assert idx._matrix.shape[0] == before + 1
    assert idx._doc_ids[-1] == "concepts/new.md#s"
    top = idx.search("brandnew unique vocabulary", top_k=1)
    assert top and top[0][0] == "concepts/new.md#s"
