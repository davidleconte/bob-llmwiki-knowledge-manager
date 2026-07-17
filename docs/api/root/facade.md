# facade

TokenOptimizer: the unified facade over the token-optimization system.

Composes the cache, optimizer and truncator from a single
:class:`~src.config.schema.ConfigSchema` and registers the monitoring health
checks, so callers (and the CLI) have one entry point instead of wiring each
component by hand. Build it from the config singleton with
:meth:`TokenOptimizer.from_config`, or pass an explicit ``ConfigSchema``.

``config.cache`` fields applied by the facade:

- ``config.cache.l1*`` (``l1_max_size``, ``l1_ttl_seconds``, ``l1_enabled``): govern
  **both** the :attr:`cache` (L1 level) *and* the ``optimize()`` path, because the
  facade shares the same :class:`~src.cache.exact_cache.ExactCache` instance between
  both surfaces. Changing ``l1_max_size`` affects how many optimizations are memoised.
- ``config.cache.l2*`` (``l2_max_size``, ``l2_similarity_threshold``, ``l2_ttl_seconds``,
  ``l2_enabled``): govern **only** the :attr:`cache` surface (``cache.get()``,
  ``cache_stats()``). They have **no effect** on ``optimize()`` by design — an L2
  semantic hit could return a *different* prompt's optimized text, which would be
  wrong. The optimizer uses exact (L1) matching only.

``config.monitoring`` fields applied by the facade:

- ``log_level``: passed to the facade's :class:`~src.monitoring.logger.LoggerFactory`
  logger so all facade-level log events respect the configured severity floor.
- ``metrics_enabled``: gates the facade's own :attr:`_metrics` usage (``True`` by
  default; set ``False`` to suppress facade-level metric recording).

``config.monitoring.health_check_interval`` is *not yet applied* — health checks
are on-demand (called by :meth:`health`); a background timer scheduler is a future
enhancement and would require a daemon thread (out of scope for Beta).

The facade holds no business logic of its own: every operation delegates to an
already-tested component method. It is the first place cache + optimizer +
truncation + monitoring are actually composed together (Phase 4).

## Classes

### `TokenOptimizer`

Unified facade composing the optimizer, caches, truncator and monitoring.

Attributes:
    config: The ``ConfigSchema`` the components were built from.
    cache: A ``MultiLevelCache`` built from ``config.cache``. Governs the
        ``cache.get()`` / ``cache_stats()`` / ``query_l3()`` surfaces.
        Its L1 (:class:`~src.cache.exact_cache.ExactCache`) is *shared*
        with :attr:`optimizer`, so ``config.cache.l1*`` settings apply to
        both. Its L2 (:class:`~src.cache.semantic_cache.SemanticCache`) is
        **not** used by ``optimize()`` — see the module docstring for the
        design rationale. ``config.cache.l2*`` settings affect only this
        attribute, not the optimizer memoisation path.
    optimizer: A ``PromptOptimizer`` built from ``config.optimizer``, sharing
        this facade's L1 cache. Its memoisation is L1-only (exact matching).
    truncator: A ``Truncator``.

#### Methods

##### `__init__(config: Optional['ConfigSchema'])`

Compose the system from a ``ConfigSchema``.

Args:
    config: Explicit configuration. When ``None``, the current
        ``ConfigManager`` singleton's schema is used.
    model: Model name for token counting / pricing.
    track_costs: Whether the optimizer records costs with CostTracker.


##### `from_config(cls, environment: str) -> 'TokenOptimizer'`

Build a facade from the ``ConfigManager`` singleton for ``environment``.


##### `optimize(prompt: str, max_tokens: Optional[int]) -> Dict[str, Any]`

Optimize a prompt end to end.

With ``max_tokens=None`` the optimizer's config-driven default cap applies
(``config.optimizer.max_tokens``); a per-call value overrides it.


##### `truncate(text: str, max_tokens: int, strategy: Optional[str]) -> Dict[str, Any]`

Truncate text to a token budget (delegates to ``Truncator``).


##### `count(text: str) -> int`

Count tokens in ``text`` (delegates to the optimizer's ``TokenCounter``).


##### `cache_stats() -> Dict[str, Any]`

Return multi-level cache statistics.


##### `metrics() -> Dict[str, Any]`

Return the current metrics summary.


##### `cost_report(include_breakdown: bool) -> Dict[str, Any]`

Return a cost report computed over the shared ``CostTracker``.


##### `health() -> Dict[str, Any]`

Run the registered health checks and return the system-health dict.


