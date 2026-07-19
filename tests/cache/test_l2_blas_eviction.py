"""A4: L2 SemanticCache — BLAS similarity APIs + O(1) LRU eviction.

``find_similar`` / ``get_with_similarity`` used a per-entry Python cosine loop
(``cosine_similarity_vectors`` over every cached embedding); they now build one
locked snapshot matrix and do a single ``matrix @ query`` BLAS matmul — the same
path ``get()`` already used. ``_evict_lru`` scanned every entry with ``min(...)``
(O(N)); ``entries`` is now an access-ordered ``OrderedDict`` so eviction is a
front ``popitem`` (O(1)).

Design note: this keeps the *per-call locked snapshot* rather than a persistent
matrix — a persistent matrix would be a concurrency hazard against the W1/W2
snapshot race fix and is invalidated on every vocabulary change. The win here is
Python-loop → BLAS, not avoiding the (bounded, ≤max_size) stack.
"""

from __future__ import annotations

import numpy as np

import src.cache.semantic_cache as sc_mod
from src.cache.semantic_cache import SemanticCache


def _fill(cache: SemanticCache, n: int) -> None:
    for i in range(n):
        cache.set(f"key_{i} alpha beta gamma token{i}", f"resp_{i}")


def _stack_spy(monkeypatch):
    calls = {"n": 0}
    real = np.stack

    def counting_stack(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(sc_mod.np, "stack", counting_stack)
    return calls


def test_find_similar_uses_batched_stack(monkeypatch):
    """RED->GREEN: find_similar builds one np.stack matrix (not a Python loop).

    The old per-entry cosine loop never called np.stack; the batched path does.
    """
    cache = SemanticCache(max_size=50, similarity_threshold=0.0)
    _fill(cache, 20)
    calls = _stack_spy(monkeypatch)

    results = cache.find_similar("alpha beta gamma token3", top_k=5)

    assert results, "find_similar returned nothing"
    assert calls["n"] >= 1, "find_similar did not use the batched np.stack BLAS path"


def test_get_with_similarity_uses_batched_stack(monkeypatch):
    """RED->GREEN: get_with_similarity uses the np.stack BLAS path."""
    cache = SemanticCache(max_size=50, similarity_threshold=0.0)
    _fill(cache, 20)
    calls = _stack_spy(monkeypatch)

    out = cache.get_with_similarity("alpha beta gamma token3")

    assert out is not None
    assert calls["n"] >= 1, "get_with_similarity did not use the batched BLAS path"


def _explicit_cosine_ranking(cache, query, top_k):
    """Reference ranking via explicit normalised cosine over each embedding."""
    qe = cache.embedding_generator.generate(query)
    qn = np.linalg.norm(qe) or 1.0
    ref = []
    for vk, emb in cache.embeddings.items():
        en = np.linalg.norm(emb) or 1.0
        cos = float(np.dot(qe, emb) / (qn * en))
        ref.append((cache._extract_base_key(vk), max(0.0, min(1.0, cos))))
    ref.sort(key=lambda x: x[1], reverse=True)
    return ref[:top_k]


def test_find_similar_parity_with_explicit_cosine():
    """Batched find_similar must match an explicit per-entry cosine ranking."""
    cache = SemanticCache(max_size=50, similarity_threshold=0.0)
    _fill(cache, 15)
    query = "alpha beta gamma token7"

    got = cache.find_similar(query, top_k=15)
    ref = _explicit_cosine_ranking(cache, query, top_k=15)

    assert [g[0] for g in got] == [r[0] for r in ref], "ranking diverged"
    for (_, g_score, _), (_, r_score) in zip(got, ref):
        assert abs(g_score - r_score) < 1e-5, f"{g_score} != {r_score}"


def test_get_with_similarity_parity_with_get():
    """get_with_similarity's best match must equal get()'s hit on the same query."""
    cache = SemanticCache(max_size=50, similarity_threshold=0.0)
    _fill(cache, 15)
    query = "alpha beta gamma token4"

    via_get = cache.get(query)
    via_sim = cache.get_with_similarity(query)

    assert via_sim is not None
    assert via_sim[0] == via_get, "get_with_similarity returned a different response"
    assert 0.0 <= via_sim[1] <= 1.0


def test_lru_eviction_removes_least_recently_used():
    """O(1) eviction must still remove the genuinely least-recently-used entry."""
    cache = SemanticCache(max_size=3, similarity_threshold=0.99)
    cache.set("aaa alpha unique", "ra")
    cache.set("bbb beta unique", "rb")
    cache.set("ccc gamma unique", "rc")

    # Touch aaa and bbb (exact-key hits) so ccc is the least recently used.
    assert cache.get("aaa alpha unique") == "ra"
    assert cache.get("bbb beta unique") == "rb"

    cache.set("ddd delta unique", "rd")  # full -> must evict ccc

    assert cache.size() == 3
    assert not cache.contains("ccc gamma unique"), "LRU entry ccc was not evicted"
    assert cache.contains("aaa alpha unique")
    assert cache.contains("bbb beta unique")
    assert cache.contains("ddd delta unique")


def test_lru_reinsert_refreshes_recency():
    """Re-setting an existing key moves it to MRU (not evicted next)."""
    cache = SemanticCache(max_size=3, similarity_threshold=0.99)
    cache.set("aaa alpha unique", "ra")
    cache.set("bbb beta unique", "rb")
    cache.set("ccc gamma unique", "rc")

    cache.set("aaa alpha unique", "ra2")  # refresh aaa -> MRU; bbb now LRU

    cache.set("ddd delta unique", "rd")  # evicts bbb, not aaa

    assert not cache.contains("bbb beta unique")
    assert cache.contains("aaa alpha unique")
    assert cache.get("aaa alpha unique") == "ra2"
