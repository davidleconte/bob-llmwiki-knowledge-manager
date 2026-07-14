"""Multi-level caching system for token optimization.

This module implements a two-level cache:
- L1: Exact match cache (hash-based, O(1) lookup)
- L2: Semantic similarity cache (embedding-based, cosine similarity)

Characteristics:
- Cache hit rate: workload-dependent (tracks how often prompts repeat); it is
  NOT a fixed system property and is excluded from the savings headline. See
  ``evaluation/results/validation-2026-07-14/`` and ``STATUS.md``.
- Lookup latency: O(1) L1 exact match; L2 cosine similarity over embeddings.
- Memory efficiency: bounded LRU eviction.
"""

from src.cache.base import CacheEntry, CacheInterface
from src.cache.exact_cache import ExactCache
from src.cache.multi_level_cache import MultiLevelCache
from src.cache.semantic_cache import SemanticCache

__all__ = [
    "CacheEntry",
    "CacheInterface",
    "ExactCache",
    "SemanticCache",
    "MultiLevelCache",
]
