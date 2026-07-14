"""Multi-level caching system for token optimization.

This module implements a two-level cache:
- L1: Exact match cache (hash-based, O(1) lookup)
- L2: Semantic similarity cache (embedding-based, cosine similarity)

Target metrics:
- Cache hit rate: 23.33%+
- Lookup latency: <100ms (p95)
- Memory efficiency: LRU eviction
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
