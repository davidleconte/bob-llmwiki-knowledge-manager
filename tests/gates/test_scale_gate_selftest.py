"""A8 self-test — prove the scale-regression gate actually bites.

The same self-test discipline the honesty gates use: a gate that never fails is
indistinguishable from no gate. Here we re-introduce the exact super-linear
implementations WS-A replaced and assert that
``tests/performance/test_scale_invariants`` raises — so a real regression in the
L2 eviction path (A4) or the PageRank dangling loop (A1) would fail CI, not pass
silently.

Both self-tests run cheaply: the eviction min()-scan is fast even when O(N); the
PageRank O(N^2) reference is driven at small sizes where its quadratic growth is
already unmistakable.
"""

from __future__ import annotations

import pytest

from tests.performance import test_scale_invariants as si
from tests.performance.test_dos_hardening import _naive_pagerank


def test_gate_bites_on_quadratic_eviction(monkeypatch):
    """Re-introduce the pre-A4 O(N) min()-scan eviction → the L2 invariant must fail."""
    import src.cache.semantic_cache as sc_mod

    def _on_min_scan(self):
        """The O(N) min()-over-timestamps scan that A4's O(1) popitem replaced."""
        if not self.entries:
            return
        lru_key = min(self.entries.items(), key=lambda kv: kv[1].timestamp)[0]
        self.entries.pop(lru_key, None)
        self.embeddings.pop(lru_key, None)
        self.responses.pop(lru_key, None)
        self.metadata_store.pop(lru_key, None)

    monkeypatch.setattr(sc_mod.SemanticCache, "_evict_lru", _on_min_scan)

    # The real invariant, run against the regressed implementation, must raise.
    with pytest.raises(AssertionError):
        si.test_l2_eviction_scale_ratio()


def test_gate_bites_on_quadratic_pagerank(monkeypatch):
    """Re-introduce the O(N^2) dangling redistribution → the PageRank invariant must fail."""
    import src.graph.graph as graph_mod

    monkeypatch.setattr(
        graph_mod.KnowledgeGraph, "pagerank", lambda self, **kw: _naive_pagerank(self)
    )

    ceiling = si._perf_scale()["pagerank_4k_over_1k"]
    # Small sizes keep the O(N^2) reference fast; on a 3x step its growth is ~9x,
    # already clear of the linear ceiling — enough to prove the gate bites.
    ratio = si._pagerank_ratio(80, 240)
    assert ratio >= ceiling, (
        f"self-test setup: expected the O(N^2) reference to exceed the ceiling "
        f"{ceiling}, but measured only {ratio:.2f}x — cannot prove the gate bites"
    )
    with pytest.raises(AssertionError):
        si._assert_ratio_under(ratio, ceiling, "self-test pagerank")
