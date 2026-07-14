"""End-to-end tests for the TokenOptimizer facade (Phase 4 composition layer).

Exercises the single composed entry point: config -> factory -> facade -> the
component operations that back the CLI.
"""

import pytest

from src import TokenOptimizer
from src.config import ConfigManager
from src.config.schema import CacheConfig, ConfigSchema, MonitoringConfig, OptimizerConfig


@pytest.fixture
def fresh_config():
    """Isolate the two ConfigManager singletons (class ``_instance`` and the
    module-level ``_global_config`` that ``get_config()`` uses) between tests."""
    import src.config.manager as manager_mod

    ConfigManager._instance = None
    manager_mod._global_config = None
    cm = ConfigManager(environment="test")
    yield cm
    ConfigManager._instance = None
    manager_mod._global_config = None


class TestTokenOptimizerFacade:
    """The facade composes cache + optimizer + truncation + monitoring."""

    def test_from_config_builds_config_driven_components(self, fresh_config):
        """from_config() builds every component from the config singleton."""
        import src.config.manager as manager_mod

        manager_mod._global_config = fresh_config  # get_config() -> our manager

        facade = TokenOptimizer.from_config("test")

        opt_cfg = fresh_config.get_optimizer_config()
        cache_cfg = fresh_config.get_cache_config()
        assert facade.optimizer.max_tokens == opt_cfg.max_tokens
        assert facade.optimizer.target_reduction == opt_cfg.target_reduction
        assert facade.cache.l1_cache.max_size == cache_cfg.l1_max_size
        assert facade.cache.l2_cache.max_size == cache_cfg.l2_max_size

    def test_optimize_roundtrip(self, fresh_config):
        """optimize() returns a result carrying both output-text keys."""
        facade = TokenOptimizer(config=fresh_config.get_schema())
        result = facade.optimize("This is   a    test prompt with   extra spaces.")

        assert result["optimized_text"] == result["optimized"]
        assert result["original_tokens"] > 0
        assert result["optimized_tokens"] <= result["original_tokens"]

    def test_optimize_honors_config_max_tokens(self, fresh_config):
        """A config max_tokens cap is applied even without a per-call arg."""
        fresh_config.update({"optimizer.max_tokens": 50})
        facade = TokenOptimizer(config=fresh_config.get_schema())

        result = facade.optimize(" ".join(["word"] * 200))
        assert facade.count(result["optimized_text"]) <= 50

    def test_runtime_config_update_rebuilds(self, fresh_config):
        """Rebuilding the facade after a config update reflects the new value."""
        facade1 = TokenOptimizer(config=fresh_config.get_schema())
        assert facade1.optimizer.max_tokens == 4096  # OptimizerConfig default

        fresh_config.update({"optimizer.max_tokens": 16384})
        facade2 = TokenOptimizer(config=fresh_config.get_schema())

        assert facade2.optimizer.max_tokens == 16384
        assert facade1.optimizer.max_tokens == 4096  # old instance unchanged

    def test_truncate(self, fresh_config):
        """truncate() delegates to the Truncator and respects the budget."""
        facade = TokenOptimizer(config=fresh_config.get_schema())
        text = " ".join(f"sentence number {i}." for i in range(200))

        result = facade.truncate(text, max_tokens=20)
        assert result["truncated_tokens"] <= 20

    def test_count(self, fresh_config):
        facade = TokenOptimizer(config=fresh_config.get_schema())
        assert facade.count("hello world") > 0

    def test_cache_stats_and_metrics_are_dicts(self, fresh_config):
        facade = TokenOptimizer(config=fresh_config.get_schema())
        assert isinstance(facade.cache_stats(), dict)
        assert isinstance(facade.metrics(), dict)

    def test_cost_report_and_health_are_dicts(self, fresh_config):
        """cost_report() and health() return serializable dicts."""
        facade = TokenOptimizer(config=fresh_config.get_schema())
        assert isinstance(facade.cost_report(), dict)
        assert isinstance(facade.health(), dict)

    def test_explicit_schema(self):
        """An explicit ConfigSchema drives the composed components."""
        schema = ConfigSchema(
            cache=CacheConfig(l1_max_size=123, l2_max_size=4567),
            optimizer=OptimizerConfig(max_tokens=2048, target_reduction=0.25),
            monitoring=MonitoringConfig(),
        )
        facade = TokenOptimizer(config=schema)

        assert facade.cache.l1_cache.max_size == 123
        assert facade.cache.l2_cache.max_size == 4567
        assert facade.optimizer.max_tokens == 2048
        assert facade.optimizer.target_reduction == 0.25
