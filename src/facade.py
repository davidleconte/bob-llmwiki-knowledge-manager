"""TokenOptimizer: the unified facade over the token-optimization system.

Composes cache + optimizer + truncation + monitoring from a single
:class:`~src.config.schema.ConfigSchema`, so callers (and the CLI) have one entry
point instead of wiring each component by hand. Build it from the config
singleton with :meth:`TokenOptimizer.from_config`, or pass an explicit
``ConfigSchema``.

The facade holds no business logic of its own: every operation delegates to an
already-tested component method. It is the first place cache + optimizer +
truncation + monitoring are actually composed together (Phase 4).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from src.config.manager import get_config
from src.factory import build_cache, build_optimizer, build_truncator
from src.monitoring import (
    get_logger,
    get_metrics_collector,
    register_cache_health_check,
    register_monitoring_health_check,
    register_system_health_check,
)
from src.pricing import DEFAULT_MODEL

if TYPE_CHECKING:
    from src.config.schema import ConfigSchema


class TokenOptimizer:
    """Unified facade composing the optimizer, caches, truncator and monitoring.

    Attributes:
        config: The ``ConfigSchema`` the components were built from.
        cache: A ``MultiLevelCache`` built from ``config.cache``.
        optimizer: A ``PromptOptimizer`` built from ``config.optimizer``.
        truncator: A ``Truncator``.
    """

    def __init__(
        self,
        config: Optional["ConfigSchema"] = None,
        *,
        model: str = DEFAULT_MODEL,
        track_costs: bool = False,
    ):
        """Compose the system from a ``ConfigSchema``.

        Args:
            config: Explicit configuration. When ``None``, the current
                ``ConfigManager`` singleton's schema is used.
            model: Model name for token counting / pricing.
            track_costs: Whether the optimizer records costs with CostTracker.
        """
        if config is None:
            config = get_config().get_schema()
        self.config = config
        self.model = model
        self.track_costs = track_costs

        self.cache = build_cache(config.cache)
        self.optimizer = build_optimizer(config.optimizer, model=model, track_costs=track_costs)
        self.truncator = build_truncator(model=model)

        self._logger = get_logger("facade.token_optimizer")
        self._metrics = get_metrics_collector()

        # Register health checks so health() reports on the live components
        # (closes the B4 "health checks defined but never wired" orphan).
        register_cache_health_check("multi_level", self.cache)
        register_monitoring_health_check()
        register_system_health_check()

        self._logger.info("token_optimizer_initialized", model=model, track_costs=track_costs)

    @classmethod
    def from_config(
        cls, environment: str = "dev", *, model: str = DEFAULT_MODEL, track_costs: bool = False
    ) -> "TokenOptimizer":
        """Build a facade from the ``ConfigManager`` singleton for ``environment``."""
        schema = get_config(environment).get_schema()
        return cls(schema, model=model, track_costs=track_costs)

    # --- high-level operations (each backs a CLI subcommand) ---

    def optimize(self, prompt: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Optimize a prompt end to end.

        With ``max_tokens=None`` the optimizer's config-driven default cap applies
        (``config.optimizer.max_tokens``); a per-call value overrides it.
        """
        return self.optimizer.optimize(prompt, max_tokens=max_tokens)

    def truncate(
        self, text: str, max_tokens: int, strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Truncate text to a token budget (delegates to ``Truncator``)."""
        return self.truncator.truncate(text, max_tokens, strategy=strategy)

    def count(self, text: str) -> int:
        """Count tokens in ``text`` (delegates to the optimizer's ``TokenCounter``)."""
        return self.optimizer.token_counter.count_tokens(text)

    def cache_stats(self) -> Dict[str, Any]:
        """Return multi-level cache statistics."""
        return self.cache.stats()

    def metrics(self) -> Dict[str, Any]:
        """Return the current metrics summary."""
        return self._metrics.get_summary()

    def cost_report(self, include_breakdown: bool = True) -> Dict[str, Any]:
        """Return a cost report computed over the shared ``CostTracker``."""
        from src.monitoring.cost_reporting import generate_cost_report

        return generate_cost_report(include_breakdown=include_breakdown)

    def health(self) -> Dict[str, Any]:
        """Run the registered health checks and return the system-health dict."""
        from src.monitoring import get_health_checker

        return get_health_checker().check().to_dict()
