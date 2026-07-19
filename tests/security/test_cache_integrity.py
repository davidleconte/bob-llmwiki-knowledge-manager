"""ATK-FS-02/04/05 regression: cache poisoning, TTL bypass, metadata mutation."""
import time
import pytest
from src.cache.exact_cache import ExactCache
from src.cache.multi_level_cache import MultiLevelCache
from src.cache.semantic_cache import SemanticCache


# ---------------------------------------------------------------------------
# ATK-FS-02: L2 fuzzy match must not be promoted to L1 under victim's key
# ---------------------------------------------------------------------------

def test_fuzzy_l2_hit_not_promoted_to_l1_under_victim_key():
    """A cosine-similarity L2 hit must not be promoted as an exact L1 entry (ATK-FS-02)."""
    cache = MultiLevelCache(
        l1_max_size=100, l2_max_size=100, similarity_threshold=0.50,
    )
    # Store a value under attacker_key
    attacker_key = "how do I reset my admin password step by step"
    cache.set(attacker_key, "POISONED_PAYLOAD")

    # A semantically similar victim key that might score ≥ 0.50 under hashing
    victim_key = "steps to recover my admin password"
    # The victim key is NOT the attacker key — even if L2 returns a fuzzy hit,
    # it must NOT be stored in L1 under the victim's exact key
    _ = cache.get(victim_key)  # trigger any potential promotion

    # Directly check L1 — the victim key must not hold the attacker payload
    l1_result = cache.l1_cache.get(victim_key)
    assert l1_result != "POISONED_PAYLOAD", (
        "Fuzzy L2 hit was promoted to L1 under victim's exact key — ATK-FS-02 not fixed"
    )


def test_exact_l2_hit_is_promoted_to_l1():
    """An exact L2 hit SHOULD be promoted to L1 (promotion must still work for legit hits)."""
    cache = MultiLevelCache(
        l1_max_size=100, l2_max_size=100, similarity_threshold=0.85,
    )
    key = "what is the capital of France"
    cache.set(key, "Paris")

    # Evict from L1 to force an L2 path on next get
    cache.l1_cache.evict(key)

    result = cache.get(key)
    assert result == "Paris", "Exact L2 hit must still return the correct value"

    # After exact hit through L2, L1 should now hold it (promoted)
    l1_result = cache.l1_cache.get(key)
    assert l1_result == "Paris", (
        "Exact L2 hit was NOT promoted to L1 — legit promotion broken"
    )


# ---------------------------------------------------------------------------
# ATK-FS-04: contains() must respect TTL
# ---------------------------------------------------------------------------

def test_contains_respects_ttl():
    """contains() must return False for TTL-expired entries (ATK-FS-04)."""
    cache = ExactCache(max_size=100, ttl_seconds=0.05)  # 50 ms TTL
    cache.set("my-key", "my-value")
    assert cache.contains("my-key") is True, "Fresh entry should be present"
    time.sleep(0.1)  # exceed TTL
    assert cache.contains("my-key") is False, (
        "contains() returned True for TTL-expired entry — ATK-FS-04 not fixed"
    )


def test_contains_returns_true_before_ttl():
    """contains() must return True for a live (non-expired) entry."""
    cache = ExactCache(max_size=100, ttl_seconds=10.0)
    cache.set("alive-key", "alive-value")
    assert cache.contains("alive-key") is True


# ---------------------------------------------------------------------------
# ATK-FS-05: metadata dict must not be shared across caller / cache levels
# ---------------------------------------------------------------------------

def test_caller_mutation_does_not_corrupt_stored_metadata():
    """Mutating the dict passed to set() must not corrupt the stored entry (ATK-FS-05)."""
    cache = ExactCache(max_size=100)
    meta = {"source": "test", "tokens": 42}
    cache.set("key1", "value1", metadata=meta)

    # Mutate the original dict after the set
    meta["source"] = "MUTATED_BY_CALLER"
    meta["injected"] = "evil"

    # The cache should return the correct value unaffected
    assert cache.get("key1") == "value1"

    # Verify stored metadata was not mutated — get the raw entry
    versioned_key = cache._make_versioned_key("key1", None)
    hashed_key = cache._hash_key(versioned_key)
    stored_entry = cache.cache.get(hashed_key)
    assert stored_entry is not None
    assert stored_entry.metadata.get("source") == "test", (
        "Stored metadata was mutated by caller — ATK-FS-05 not fixed"
    )
    assert "injected" not in stored_entry.metadata, (
        "Caller dict mutation injected keys into stored metadata — ATK-FS-05 not fixed"
    )


def test_match_type_annotation_on_exact_l2_promotion():
    """L1 entries promoted from L2 via exact key should carry match_type='exact'."""
    cache = MultiLevelCache(
        l1_max_size=100, l2_max_size=100, similarity_threshold=0.85,
    )
    key = "annotated key test"
    cache.set(key, "annotated value")

    # Force evict from L1 to trigger L2 path
    cache.l1_cache.evict(key)

    result = cache.get(key)
    assert result == "annotated value"

    # Check that L1 entry (if promoted) carries match_type metadata
    versioned_key = cache.l1_cache._make_versioned_key(key, None)
    hashed_key = cache.l1_cache._hash_key(versioned_key)
    l1_entry = cache.l1_cache.cache.get(hashed_key)
    if l1_entry is not None:
        assert l1_entry.metadata.get("match_type") == "exact", (
            "Promoted exact L1 entry missing match_type='exact' annotation"
        )
