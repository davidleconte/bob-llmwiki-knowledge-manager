# factory

Composition helpers: build live runtime components from config dataclasses.

This is the single home for the config-field -> constructor-kwarg mapping. Every
consumer that needs a component built from config (the :class:`~src.facade.TokenOptimizer`
facade, the CLI, tests) goes through these builders instead of re-reading config or
hard-coding literals, so the mapping cannot drift. The field-name reconciliation
Phase 4 performed (``CacheConfig``/``OptimizerConfig`` names -> component kwargs)
lives here, once.

## Functions

### `build_cache(config: 'CacheConfig') -> MultiLevelCache`

Build a :class:`MultiLevelCache` from a :class:`CacheConfig`.

Maps every ``CacheConfig`` field onto the cache constructor: sizes, TTLs, the
L2 similarity threshold, the L1/L2 enabled flags, and version-support
settings (``version_support_enabled``, ``max_versions``) all take effect.


### `build_optimizer(config: 'OptimizerConfig') -> PromptOptimizer`

Build a :class:`PromptOptimizer` from an :class:`OptimizerConfig`.

``model``/``use_cache``/``track_costs``/``cache`` are not part of
``OptimizerConfig`` and are passed separately; the config's ``max_tokens``/
``target_reduction``/``min_quality_score``/``strategies`` map 1:1 via
:meth:`PromptOptimizer.from_config`. ``cache`` lets the facade share its
config-built L1 so ``config.cache.l1`` governs the optimize() cache.


### `build_truncator() -> Truncator`

Build a :class:`Truncator`.

Truncation has no config section yet (no config contract requires one), so
this takes plain arguments; it lives here so the facade has one composition
entry point per component.

