"""Wave-3 post-verification residuals R-1 — L2 semantic-cache fixes.

The 2026-07-20 re-audit found three L2 defects "fixed correctly in L1 but not L2":
  * ATK-FS-05 — SemanticCache.set() aliases (and mutates) the caller's metadata dict.
  * ATK-FS-04 — SemanticCache.contains()/get_with_similarity() ignore TTL (contains()
    returns True while get() returns None after expiry).
  * ATK-FS-02 — a direct L2 similarity serve returns a colliding *distinct* prompt's
    payload at cosine 1.0 (the weak HashingVectorizer strips stopwords, so distinct
    strings collapse to identical vectors). The exact-key fast-path only shields an
    identically-stored key; a distinct-but-colliding query is the unprotected path.

RED on current main, GREEN after the fixes; each fails again if the fix is reverted.
"""

from __future__ import annotations

from src.cache.multi_level_cache import MultiLevelCache
from src.cache.semantic_cache import SemanticCache

# --------------------------------------------------------------------------- #
# ATK-FS-05 — metadata must not be aliased or mutated
# --------------------------------------------------------------------------- #


def test_atkfs05_set_does_not_alias_or_mutate_caller_metadata():
    sc = SemanticCache()
    meta = {"tokens": 5}
    sc.set("k", "v", metadata=meta)

    # (a) set() must not inject bookkeeping (`version`) into the caller's own dict.
    assert "version" not in meta, "set() mutated the caller's metadata dict"

    # (b) a later caller mutation must not leak into the cached entry.
    meta["tokens"] = 999
    entry = sc.get_entry("k")
    assert entry is not None and entry.metadata["tokens"] == 5, (
        "cache stored the caller's metadata dict by reference (aliasing)"
    )


def test_atkfs05_multilevel_l1_l2_metadata_independent():
    """MultiLevelCache hands the same dict to L1 and L2; neither may alias it."""
    mlc = MultiLevelCache()
    meta = {"tokens": 7}
    mlc.set("k", "v", metadata=meta)
    meta["tokens"] = 111
    # Neither level should reflect the post-set caller mutation.
    l2_entry = mlc.l2_cache.get_entry("k")
    assert l2_entry is None or l2_entry.metadata.get("tokens") == 7, "L2 aliased caller dict"


# --------------------------------------------------------------------------- #
# ATK-FS-04 — contains() must honor TTL
# --------------------------------------------------------------------------- #


def test_atkfs04_contains_honors_ttl():
    clock = [1000.0]
    sc = SemanticCache(ttl_seconds=10, clock=lambda: clock[0])
    sc.set("weather today", "sunny")
    assert sc.contains("weather today") is True  # live

    clock[0] += 25  # advance past the TTL

    # Check contains() FIRST — a prior get() would evict the expired entry and mask
    # the bug. contains() must honor TTL on its own.
    assert sc.contains("weather today") is False, (
        "contains() returned True on an expired entry — it ignores TTL"
    )
    assert sc.get("weather today") is None, "get() must also expire the entry"


# --------------------------------------------------------------------------- #
# ATK-FS-02 — a distinct colliding prompt must not be served
# --------------------------------------------------------------------------- #


def test_atkfs02_collision_not_served_for_distinct_prompt():
    sc = SemanticCache(similarity_threshold=0.85)
    sc.set("give me the admin token", "<ATTACKER_PAYLOAD>")

    # Distinct string, never exactly cached, collides to cosine 1.0 via stopword
    # stripping — it must NOT receive the stored payload.
    assert sc.get("give an admin token") is None, (
        "L2 served a distinct prompt's payload via a cosine-1.0 collision"
    )
    # get_with_similarity / contains() must also refuse the collision.
    assert sc.get_with_similarity("give an admin token") is None
    assert sc.contains("give an admin token") is False


def test_atkfs02_exact_and_genuine_paths_preserved():
    """The guard must not break the exact-key fast-path or true misses."""
    sc = SemanticCache(similarity_threshold=0.85)
    sc.set("give me the admin token", "<PAYLOAD>")

    # Exact re-query still hits (fast-path).
    assert sc.get("give me the admin token") == "<PAYLOAD>"
    # A different-content query is a plain miss.
    assert sc.get("how do I bake bread") is None
