# ADR-013: Facade and Factory Pattern for System Composition

**Status:** Accepted  
**Date:** 2026-07-14  
**Deciders:** Architecture Team  
**Context:** Token Optimization System — Phase 4 composition refactor  

---

## Context

Before Phase 4, the token optimization system had four independently tested subsystems
(`src/cache/`, `src/optimizer/`, `src/truncation/`, `src/monitoring/`) but no single
composition point. Callers (including the CLI and tests) wired the components manually —
importing `MultiLevelCache`, `PromptOptimizer`, `Truncator`, and monitoring utilities
separately, constructing them with hard-coded literals, and connecting them by hand.

This created several problems:

1. **Config did not reach the runtime.** `ConfigSchema` (`src/config/schema.py`) existed
   with typed, default-carrying fields, but nothing read those fields when building live
   components. An operator setting `l1_max_size=500` in configuration saw no effect.

2. **Constructor drift.** Every caller repeated the config-field → constructor-kwarg
   mapping independently. When a field was renamed the mapping broke in multiple places.

3. **No shared resources.** The CLI's cache and the optimizer's internal cache were
   separate instances even when they should share state (e.g., `config.cache.l1` should
   govern both the multi-level surface and the optimizer's exact-match cache).

4. **No composition entry point for testing.** Integration tests could not build a
   realistic "full system" from a config without duplicating the manual wiring.

5. **Health checks orphaned.** Three monitoring health-check registration calls existed
   but were never invoked, so `health()` always returned an empty report.

The Phase 4 refactor introduced a facade/factory pattern to solve all five problems in
one architectural change.

---

## Decision

Introduce two new modules:

- **`src/facade.py` — `TokenOptimizer` class.** The single public composition point. It
  accepts a `ConfigSchema`, delegates construction to the factory, registers health checks,
  and exposes the five high-level operations (`optimize`, `truncate`, `count`,
  `cache_stats`, `metrics`, `cost_report`, `health`). It holds no business logic of its
  own — every operation is a one-line delegation to an already-tested component method.

- **`src/factory.py` — three builder functions.** `build_cache(CacheConfig)`,
  `build_optimizer(OptimizerConfig, …)`, `build_truncator(…)`. These are the **single
  home for the config-field → constructor-kwarg mapping**. Every consumer that needs a
  component built from config goes through these builders; the mapping cannot drift.

`ConfigSchema` (`src/config/schema.py`) remains the single home for configuration
defaults. The facade always reads from it (either the explicit argument or the
`ConfigManager` singleton).

---

## Rationale

**Why a facade (not callers composing directly)?**  
Callers should not know which components exist or how to wire them. A facade enforces
a single tested composition path, prevents partial-construction bugs, and gives
operators one object to configure.

**Why a separate factory module (not constructors in the facade)?**  
The config-field → constructor-kwarg mapping is the most likely place for drift as
fields evolve. A factory module makes the mapping explicit, testable in isolation, and
unrepeatable — if you want a live `MultiLevelCache` from config, there is exactly one
path. The facade stays thin (no mapping logic).

**Why not a dependency injection container?**  
The system has a small number of well-known components (4 subsystems). A DI container
would add a framework dependency and indirection with no benefit at this scale. Builder
functions are simpler, type-checked, and easier to read.

**Why not a service locator?**  
A service locator hides dependencies and makes testing harder. The facade constructor
takes a `ConfigSchema` explicitly; all dependencies are visible at call sites.

**Why share the L1 cache between `MultiLevelCache` and `PromptOptimizer`?**  
`config.cache.l1` (size, TTL, enabled flag) should govern the exact-match cache used by
`optimize()` and the L1 level of the multi-level surface. If they were separate
instances, two disjoint caches would exist with identical config but no shared state,
and operators could not reason about capacity. The facade (`facade.py:85`) passes
`self.cache.get_l1_cache()` to `build_optimizer()` so both share one `ExactCache`.

---

## Alternatives Considered

### Alternative A — Keep manual wiring at each call site

**Pros:** No new abstraction; each caller is explicit.  
**Cons:** Config-field drift, duplicated mapping code, orphaned health checks, no shared
L1 cache, impossible to build a realistic integration test without duplicating wiring.  
**Rejected:** The pre-Phase-4 state had all these problems simultaneously.

### Alternative B — Dependency injection container (e.g., `injector`, `dependency_injector`)

**Pros:** Handles complex graphs; provider registration is declarative.  
**Cons:** Adds a framework dependency; increases cognitive load for a 4-component graph;
no type-safety benefit over explicit builder functions at this scale.  
**Rejected:** Overkill for the complexity level.

### Alternative C — Service locator (global registry of live instances)

**Pros:** Zero constructor arguments; components accessible anywhere.  
**Cons:** Hidden dependencies; non-deterministic component lifetime; breaks test
isolation (tests would mutate shared global state).  
**Rejected:** Incompatible with the mock-based testing strategy (ADR-010).

### Alternative D — Abstract base class + concrete implementations per environment

**Pros:** Allows swapping implementations by environment (dev/prod).  
**Cons:** No concrete need for environment-specific implementations at this stage; adds
indirection with no benefit now.  
**Rejected:** Deferred; the `from_config(environment=...)` classmethod on
`TokenOptimizer` preserves the option without requiring it.

---

## Consequences

### Positive

- Config flows to the runtime: `config.cache.l1_max_size`, `config.cache.l2_similarity_threshold`,
  `config.optimizer.max_tokens`, etc. all take effect at construction time
  (`factory.py:31-39`, `factory.py:58-59`).
- The config-field → constructor-kwarg mapping lives in exactly one place (`src/factory.py`).
- Health checks are registered at construction time (`facade.py:94-96`); `health()` returns
  a live system report.
- L1 cache is shared between the multi-level surface and the optimizer (single `ExactCache`
  instance, `facade.py:85`).
- The facade is the composition entry point for the CLI (`python -m src`) and all
  integration tests.

### Negative

- **`MonitoringConfig` fields not yet read.** `config.monitoring.log_level`,
  `config.monitoring.metrics_enabled`, and `config.monitoring.health_check_interval` are
  declared in `ConfigSchema` and parsed from environment config, but the facade does not
  apply them to the monitoring subsystem (`facade.py:9-11`). This is a documented gap;
  monitoring is wired as health-check registration only.
- **`OptimizerConfig.strategies` is a dead field.** `ConfigSchema` declares
  `OptimizerConfig.strategies` (`schema.py:51`), but `build_optimizer` does not pass it
  to `PromptOptimizer`. The strategies are currently hard-coded inside the optimizer.
  This is a "declared but not read" field; it is harmless but misleading.
- Adding the facade layer means any bug in the factory is shared by all consumers. This
  is offset by the factory being the single, well-tested mapping source.

### Neutral

- The `from_config(environment)` classmethod (`facade.py:101-106`) provides a convenient
  shorthand for the CLI while leaving the constructor (`__init__`) the testable entry point.
- L2 semantic cache is not used in the `optimize()` path by design — a semantic hit could
  return a different prompt's optimization. L2 is only exercised through the `cache`
  surface directly. This trade-off is documented in `facade.py:76-78`.

---

## Implementation

```python
# src/facade.py — composition entry point
from src.factory import build_cache, build_optimizer, build_truncator

class TokenOptimizer:
    def __init__(self, config: Optional["ConfigSchema"] = None, ...):
        if config is None:
            config = get_config().get_schema()
        self.cache = build_cache(config.cache)
        self.optimizer = build_optimizer(
            config.optimizer,
            use_cache=config.cache.l1_enabled,
            cache=self.cache.get_l1_cache(),   # shared L1
        )
        self.truncator = build_truncator(model=model)
        # health checks wired here, not orphaned
        register_cache_health_check("multi_level", self.cache)
        register_monitoring_health_check()
        register_system_health_check()
```

```python
# src/factory.py — single home for config → constructor mapping
def build_cache(config: CacheConfig) -> MultiLevelCache:
    return MultiLevelCache(
        l1_max_size=config.l1_max_size,
        l2_max_size=config.l2_max_size,
        similarity_threshold=config.l2_similarity_threshold,
        l1_ttl_seconds=config.l1_ttl_seconds,
        l2_ttl_seconds=config.l2_ttl_seconds,
        l1_enabled=config.l1_enabled,
        l2_enabled=config.l2_enabled,
    )
```

**Source references:**
- Facade class: `src/facade.py:37-147`
- Factory builders: `src/factory.py:25-70`
- Config schema: `src/config/schema.py:11-95`
- Shared L1 wiring: `src/facade.py:73-86`
- Health check registration: `src/facade.py:94-96`
- Documented MonitoringConfig gap: `src/facade.py:9-11`

---

## Validation

- `pytest tests/test_facade.py` — end-to-end facade tests (configuration, delegation, health)
- `pytest tests/test_factory.py` — builder function unit tests
- `scripts/check_layering.py` — confirms `src/factory.py` is the only home for config mapping
- `scripts/check_value_homes.py` — confirms config defaults have single homes in `schema.py`
- `python -m src optimize "test prompt"` — CLI smoke test through facade

---

## References

- `src/facade.py` — TokenOptimizer implementation
- `src/factory.py` — builder functions
- `src/config/schema.py` — ConfigSchema, CacheConfig, OptimizerConfig, MonitoringConfig
- `docs/architecture/architecture.md §3` — sequence diagram showing optimize() path through facade
- ADR-002: Caching strategy (what the factory builds for the cache)
- ADR-011: Monitoring (health checks wired by the facade)
- `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` — audit finding that prompted this ADR
