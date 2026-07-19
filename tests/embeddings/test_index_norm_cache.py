"""ATK-DOS-04 residual: per-row norms are cached on the hot search path.

``search()`` used to recompute ``np.linalg.norm(matrix, axis=1)`` — and allocate a
full normalised copy of the matrix — on *every* query, O(N*dim) of wasted work per
search on the hot retrieval path. The row norms are matrix-invariant, so they are
cached and recomputed only after a mutation of ``_matrix``.

RED->GREEN: ``test_matrix_norm_computed_once_across_queries`` counts 2-D
``np.linalg.norm`` calls; the pre-fix code recomputes it on every query (fails the
"<= 1 across two searches" assertion), the cached version computes it once.
"""

import numpy as np

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex


def _section(title: str, word: str) -> str:
    body = (word + " ") * 20
    return f"## {title}\n\n{body.strip()}\n"


def _make_kb(root):
    kb = root / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    return kb


def _build_index(tmp_path):
    kb = _make_kb(tmp_path)
    for name, word in [("alpha", "alpha"), ("beta", "beta"), ("gamma", "gamma")]:
        (kb / "concepts" / f"{name}.md").write_text(
            _section(f"{name.title()} Overview", word), encoding="utf-8"
        )
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / ".bob" / "kb-index")
    idx.rebuild(kb)
    assert idx.doc_count >= 3
    return idx


def test_search_scores_match_naive_cosine(tmp_path):
    """Cached-norm cosine must equal the explicit per-row-normalised formula."""
    idx = _build_index(tmp_path)
    query = "alpha overview"

    got = dict(idx.search(query, top_k=idx.doc_count))

    # Naive reference: normalise each row and the query, then dot.
    q = idx._embedder.generate(query, use_cache=True)
    q_norm = q / (np.linalg.norm(q) + 1e-9)
    m_norms = np.linalg.norm(idx._matrix, axis=1, keepdims=True) + 1e-9
    ref_sims = (idx._matrix / m_norms) @ q_norm
    ref = dict(zip(idx._doc_ids, ref_sims.tolist()))

    assert got.keys() == ref.keys()
    for k in got:
        assert abs(got[k] - ref[k]) < 1e-5, f"{k}: cached {got[k]!r} != naive {ref[k]!r}"


def test_matrix_norm_computed_once_across_queries(tmp_path, monkeypatch):
    """RED->GREEN: the O(N*dim) matrix norm is computed once, then cached.

    Pre-fix code recomputes it on every ``search()`` (2 across two queries);
    the cache computes it once (1). q_vec's own 1-D norm is not counted.
    """
    idx = _build_index(tmp_path)

    counters = {"matrix_norm": 0}
    orig_norm = np.linalg.norm

    def counting_norm(a, *args, **kwargs):
        arr = np.asarray(a)
        if arr.ndim == 2:  # the [N x dim] matrix, not the 1-D query vector
            counters["matrix_norm"] += 1
        return orig_norm(a, *args, **kwargs)

    monkeypatch.setattr(np.linalg, "norm", counting_norm)

    idx.search("alpha overview", top_k=3)
    idx.search("beta overview", top_k=3)

    assert counters["matrix_norm"] <= 1, (
        f"matrix row-norms recomputed per query ({counters['matrix_norm']}x across 2 "
        "searches) — the ATK-DOS-04 residual cache has regressed."
    )


def test_norm_cache_invalidated_on_index_document(tmp_path):
    """Adding a row must invalidate the cache so later searches see the new vector."""
    idx = _build_index(tmp_path)

    idx.search("alpha overview", top_k=3)  # populate the cache
    assert idx._row_norms is not None

    before_rows = idx._matrix.shape[0]
    idx.index_document("concepts/delta.md", _section("Delta Overview", "delta"))
    assert idx._row_norms is None, "index_document must invalidate the row-norm cache"
    assert idx._matrix.shape[0] == before_rows + 1

    # The new row must be searchable and correctly normalised (cache repopulated).
    results = dict(idx.search("delta overview", top_k=idx.doc_count))
    assert "concepts/delta.md" in results
    assert idx._row_norms is not None
    assert idx._row_norms.shape[0] == idx._matrix.shape[0]
