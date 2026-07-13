"""Property-based test for the cache round-trip invariant: ``get(set(k, v)) == v``.

Scoped to the two caches whose contract is *exact* key -> value retrieval:

* ``ExactCache`` — hash-keyed exact store.
* ``MultiLevelCache`` via its L1 exact path — ``set`` writes both L1 and L2, and
  ``get`` consults the exact L1 hash before the L2 similarity layer, so the
  round-trip is exact and independent of L2.

``SemanticCache`` is deliberately excluded: it resolves by embedding similarity,
and a known dense-HashingVectorizer collision (bug D, deferred to Phase 4) breaks
*exact* retrieval there by design — the round-trip invariant does not hold for it.

The deterministic hypothesis profile is registered in ``tests/conftest.py``.
"""

from hypothesis import given
from hypothesis import strategies as st

from src.cache.exact_cache import ExactCache
from src.cache.multi_level_cache import MultiLevelCache

# Only utf-8-encodable text: lone surrogates (Unicode category "Cs") cannot be
# utf-8 encoded, so hashing such a key would raise — an edge unrelated to the
# round-trip contract. Non-surrogate unicode round-trips are already proven by
# tests/cache/test_exact_cache.py::test_unicode_key_handling; we just avoid the
# invalid-text edge here.
_text = st.text(st.characters(codec="utf-8"))


@given(key=_text, value=_text)
def test_exact_cache_roundtrip(key, value):
    """ExactCache: whatever is set under a key comes back verbatim.

    A fresh cache per example (defaults ``ttl_seconds=None``, ``max_size=1000``)
    guarantees no time-based expiry or LRU eviction can occur between set and get.
    """
    cache = ExactCache()
    cache.set(key, value)
    assert cache.get(key) == value


@given(key=_text, value=_text)
def test_multi_level_cache_l1_roundtrip(key, value):
    """MultiLevelCache: the exact L1 hit precedes the L2 similarity layer, so the
    round-trip is exact and bypasses the known L2 collision (bug D)."""
    cache = MultiLevelCache()
    cache.set(key, value)
    assert cache.get(key) == value
