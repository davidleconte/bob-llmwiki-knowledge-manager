# facade

TokenOptimizer: the unified facade over the token-optimization system.

Composes the cache, optimizer and truncator from a single
:class:`~src.config.schema.ConfigSchema` and registers the monitoring health
checks, so callers (and the CLI) have one entry point instead of wiring each
component by hand. Build it from the config singleton with
:meth:`TokenOptimizer.from_config`, or pass an explicit ``ConfigSchema``.

Note: ``config.monitoring`` fields (``log_level``, ``metrics_enabled``,
``health_check_interval``) are not yet applied by the facade -- monitoring is
wired as health-check registration, not configured from ``MonitoringConfig``.

The facade holds no business logic of its own: every operation delegates to an
already-tested component method. It is the first place cache + optimizer +
truncation + monitoring are actually composed together (Phase 4).

## Classes

### `TokenOptimizer`

Unified facade composing the optimizer, caches, truncator and monitoring.

Attributes:
    config: The ``ConfigSchema`` the components were built from.
    cache: A ``MultiLevelCache`` built from ``config.cache``. Its L1 (exact)
        level is the *same* instance the optimizer uses for optimize()
        caching, so ``config.cache.l1`` governs both and they are not
        disjoint; L2 (semantic) is exercised only through this ``cache``
        surface directly (optimize() uses L1 only, by design).
    optimizer: A ``PromptOptimizer`` built from ``config.optimizer``, sharing
        this facade's L1 cache.
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


