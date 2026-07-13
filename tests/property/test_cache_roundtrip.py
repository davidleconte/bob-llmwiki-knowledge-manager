"""Property-based test for the cache round-trip invariant: ``get(set(k, v)) == v``.

Scoped to the caches whose contract includes *exact* key -> value retrieval:

* ``ExactCache`` — hash-keyed exact store.
* ``MultiLevelCache`` via its L1 exact path — ``set`` writes both L1 and L2, and
  ``get`` consults the exact L1 hash before the L2 similarity layer, so the
  round-trip is exact and independent of L2.
* ``SemanticCache`` — via its exact-key fast-path (C-5 cache-quality fix). ``get``
  checks the exact versioned key before the embedding-similarity search, so an
  exactly-stored key returns its own value even when dense-HashingVectorizer
  buckets collide. (Previously excluded: the collision broke exact retrieval
  before the fast-path was added.)

The deterministic hypothesis profile is registered in ``tests/conftest.py``.
"""

from hypothesis import given
from hypothesis import strategies as st

from src.cache.exact_cache import ExactCache
from src.cache.multi_level_cache import MultiLevelCache
from src.cache.semantic_cache import SemanticCache

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


@given(key=_text, value=_text)
def test_semantic_cache_roundtrip(key, value):
    """SemanticCache: the exact-key fast-path returns a stored key's own value.

    A fresh cache per example (defaults ``ttl_seconds=None``, ``max_size=500``)
    guarantees no expiry or LRU eviction between set and get, so ``get`` resolves
    via the exact versioned-key hit rather than the embedding-similarity search —
    holding even when HashingVectorizer buckets collide for distinct short keys.
    """
    cache = SemanticCache()
    cache.set(key, value)
    assert cache.get(key) == value
