"""Composition helpers: build live runtime components from config dataclasses.

This is the single home for the config-field -> constructor-kwarg mapping. Every
consumer that needs a component built from config (the :class:`~src.facade.TokenOptimizer`
facade, the CLI, tests) goes through these builders instead of re-reading config or
hard-coding literals, so the mapping cannot drift. The field-name reconciliation
Phase 4 performed (``CacheConfig``/``OptimizerConfig`` names -> component kwargs)
lives here, once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.cache.multi_level_cache import MultiLevelCache
from src.optimizer.prompt_optimizer import PromptOptimizer
from src.pricing import DEFAULT_MODEL
from src.truncation.truncator import Truncator

if TYPE_CHECKING:
    from src.cache.exact_cache import ExactCache
    from src.config.schema import CacheConfig, OptimizerConfig


def build_cache(config: "CacheConfig") -> MultiLevelCache:
    """Build a :class:`MultiLevelCache` from a :class:`CacheConfig`.

    Maps every ``CacheConfig`` field onto the cache constructor: sizes, TTLs, the
    L2 similarity threshold, the L1/L2 enabled flags, and version-support
    settings (``version_support_enabled``, ``max_versions``) all take effect.
    """
    return MultiLevelCache(
        l1_max_size=config.l1_max_size,
        l2_max_size=config.l2_max_size,
        similarity_threshold=config.l2_similarity_threshold,
        l1_ttl_seconds=config.l1_ttl_seconds,
        l2_ttl_seconds=config.l2_ttl_seconds,
        l1_enabled=config.l1_enabled,
        l2_enabled=config.l2_enabled,
        version_support_enabled=config.version_support_enabled,
        max_versions=config.max_versions,
    )


def build_optimizer(
    config: "OptimizerConfig",
    *,
    model: str = DEFAULT_MODEL,
    use_cache: bool = True,
    track_costs: bool = False,
    cache: "ExactCache | None" = None,
) -> PromptOptimizer:
    """Build a :class:`PromptOptimizer` from an :class:`OptimizerConfig`.

    ``model``/``use_cache``/``track_costs``/``cache`` are not part of
    ``OptimizerConfig`` and are passed separately; the config's ``max_tokens``/
    ``target_reduction``/``min_quality_score``/``strategies`` map 1:1 via
    :meth:`PromptOptimizer.from_config`. ``cache`` lets the facade share its
    config-built L1 so ``config.cache.l1`` governs the optimize() cache.

    Note: L2 (semantic) cache is intentionally *not* shared with the optimizer —
    an L2 hit could return a different prompt's optimized text (wrong content).
    The optimizer uses L1 exact matching only; see the ``TokenOptimizer`` facade
    module docstring for the full ``config.cache.l2*`` scoping explanation.
    """
    return PromptOptimizer.from_config(
        config, model=model, use_cache=use_cache, track_costs=track_costs, cache=cache
    )


def build_truncator(*, model: str = DEFAULT_MODEL, default_strategy: str = "semantic") -> Truncator:
    """Build a :class:`Truncator`.

    Truncation has no config section yet (no config contract requires one), so
    this takes plain arguments; it lives here so the facade has one composition
    entry point per component.
    """
    return Truncator(model=model, default_strategy=default_strategy)
