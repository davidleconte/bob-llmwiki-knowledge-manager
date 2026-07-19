"""A2: ``PersistentEmbeddingIndex.search_batch`` — batched top-k parity.

``search_batch`` folds the per-query matrix-vector products of ``search`` into a
single blocked BLAS matmul and selects top-k with ``argpartition`` instead of a
full Python sort. It is the batching primitive behind
``KnowledgeGraphBuilder.build_semantic`` (CODE-13/16 cold-build cost).

These tests pin its contract: it returns the SAME ranked results as calling
``search`` per query (up to BLAS reassociation at the tie boundary), handles the
empty index, and is unaffected by the query-block boundary.
"""

from __future__ import annotations

import numpy as np

from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex


def _section(title: str, word: str) -> str:
    body = (word + " ") * 20
    return f"## {title}\n\n{body.strip()}\n"


def _build_index(tmp_path, n_docs: int = 24):
    kb = tmp_path / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
    for i in range(n_docs):
        w = words[i % len(words)]
        (kb / "concepts" / f"doc_{i}.md").write_text(
            _section(f"Doc {i}", f"{w} topic{i % 4} shared corpus vocabulary"),
            encoding="utf-8",
        )
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / ".bob" / "kb-index")
    idx.rebuild(kb)
    assert idx.doc_count >= n_docs
    return idx


def _same_ranking(batched, per_query, tol=1e-4):
    """Both lists must agree on the (doc_id, score) sequence within tolerance."""
    assert len(batched) == len(per_query)
    for b, s in zip(batched, per_query):
        assert [d for d, _ in b] == [d for d, _ in s], f"doc order differs:\n{b}\n{s}"
        for (_, bs), (_, ss) in zip(b, s):
            assert abs(bs - ss) < tol, f"score {bs} != {ss}"


def test_search_batch_matches_per_query_search(tmp_path):
    """search_batch(qs) == [search(q) for q in qs] in ranking and score."""
    idx = _build_index(tmp_path)
    queries = [
        "alpha topic0 shared corpus",
        "gamma topic2 vocabulary",
        "delta shared corpus topic3",
        "zeta topic1 alpha beta",
    ]
    per_query = [idx.search(q, top_k=10) for q in queries]
    batched = idx.search_batch(queries, top_k=10)
    _same_ranking(batched, per_query)


def test_search_batch_scores_match_naive_cosine(tmp_path):
    """Batched scores equal the explicit per-row-normalised cosine formula."""
    idx = _build_index(tmp_path)
    query = "alpha topic0 shared corpus"

    got = dict(idx.search_batch([query], top_k=idx._matrix.shape[0])[0])

    q = idx._embedder.generate(query, use_cache=True)
    q_norm = q / (np.linalg.norm(q) + 1e-9)
    m_norms = np.linalg.norm(idx._matrix, axis=1, keepdims=True) + 1e-9
    ref_sims = (idx._matrix / m_norms) @ q_norm
    ref = dict(zip(idx._doc_ids, ref_sims.tolist()))

    assert got.keys() == ref.keys()
    for k in got:
        assert abs(got[k] - ref[k]) < 1e-5, f"{k}: {got[k]!r} != {ref[k]!r}"


def test_search_batch_respects_block_boundary(tmp_path):
    """A small query block must not change results vs a single-block run."""
    idx = _build_index(tmp_path)
    queries = [f"topic{i % 4} shared corpus vocabulary" for i in range(7)]
    one_block = idx.search_batch(queries, top_k=8, _block=512)
    many_blocks = idx.search_batch(queries, top_k=8, _block=2)
    # Ranking must be identical; scores may differ only by BLAS block-shape
    # reassociation (~1e-7).
    _same_ranking(many_blocks, one_block, tol=1e-5)


def test_search_batch_empty_index_returns_empty_lists(tmp_path):
    """Empty index yields one empty result list per query (never raises)."""
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), tmp_path / ".bob" / "empty")
    out = idx.search_batch(["anything", "else"], top_k=5)
    assert out == [[], []]


def test_search_batch_empty_query_list(tmp_path):
    """No queries -> no result rows."""
    idx = _build_index(tmp_path, n_docs=6)
    assert idx.search_batch([], top_k=5) == []


def test_search_batch_top_k_caps_results(tmp_path):
    """Each result row is capped at top_k."""
    idx = _build_index(tmp_path)
    out = idx.search_batch(["alpha shared corpus", "beta vocabulary"], top_k=3)
    assert all(len(row) <= 3 for row in out)
