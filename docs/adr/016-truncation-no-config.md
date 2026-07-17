# ADR-016: No `TruncationConfig` — Truncation Defaults Hard-Wired in Factory

**Status:** Accepted  
**Date:** 2026-07-16  
**Deciders:** Architecture Team  
**Context:** Token Optimization System — Tier-1 architecture review gap closure

---

## Context

The token optimization system exposes three mechanisms: **optimizer compression**
(near-lossless), **cache recompute-avoidance**, and **truncation** (lossy
budget-fit). The first two have corresponding config sections in `ConfigSchema`
(`OptimizerConfig` with `min_quality_score`, `CacheConfig` with
`l1/l2_max_size`). Truncation does not.

`build_truncator()` in `src/factory.py` is hard-wired with two defaults:

```python
def build_truncator(*, model: str = DEFAULT_MODEL, default_strategy: str = "semantic") -> Truncator:
    return Truncator(model=model, default_strategy=default_strategy)
```

This was a deliberate choice, not an oversight or an incomplete migration.

---

## Decision

**No `TruncationConfig` section will be added to `ConfigSchema`.** Truncation
defaults remain wired in `src/factory.py:build_truncator()`.

---

## Rationale

### 1. Truncation is lossy — misconfiguration has asymmetric consequences

`PromptOptimizer` has a `min_quality_score` safety gate that rejects
over-aggressive compression. `Truncator` has no equivalent gate: it always
truncates to the requested budget, unconditionally. An operator who sets
`truncation.strategy = "random"` or `truncation.budget = 100` in a config file
risks silently destroying prompt fidelity with no warning.

Adding a `TruncationConfig` section that callers can tune per-environment
without any acceptance criterion would recreate the same risk that `min_quality_score`
was introduced to prevent — but in the lossy domain where the consequences are
worse (information loss, not just a failed optimization attempt).

### 2. Callers who need per-call truncation control already have it

The `truncate()` facade method accepts `max_tokens` and `strategy` as arguments
at the call site. Callers who need different truncation behaviour per request can
pass those arguments directly — they do not need a config section to get control.
A config section would add indirection without adding capability.

### 3. Truncation strategy selection is workload-specific

The best truncation strategy (`semantic`, `lexical`, `random`) depends on the
shape of the content being truncated, not on the deployment environment. A config
file is the wrong level of abstraction for this choice. The `TokenOptimizer.truncate()`
signature already exposes `strategy` as an override; document it rather than
config-ify it.

### 4. Keeping the factory simple preserves the "one home" discipline

`build_truncator()` is deliberately minimal: it is the single home for
building a `Truncator`. Adding a `TruncationConfig` section would require:
- A new `TruncationConfig` dataclass in `src/config/schema.py`
- Validation rules in `src/config/validator.py`
- Wiring in `build_truncator()`
- New tests at every layer

...to expose two arguments (`strategy`, `model`) that callers can already pass
directly. The complexity cost exceeds the benefit.

---

## Alternatives Considered

### Alternative A: Add `TruncationConfig` with strategy and budget fields

**Rejected.** Exposes a lossy operation with no acceptance gate to
per-environment misconfiguration. Requires enforcing a quality floor that
truncation cannot provide (it is inherently content-lossy).

### Alternative B: Add `TruncationConfig` but gate it with an explicit opt-in

**Rejected.** The opt-in gate would add complexity for a feature that callers can
already achieve at the call site. Adds ADR surface area without adding safety.

### Alternative C: Expose only strategy in config, not budget

**Rejected** for the same reason as Alternative A — a `random` strategy selected
in config is just as harmful as any other misconfigured truncation parameter.

---

## Consequences

### Positive
- `build_truncator()` remains a one-liner — the simplest possible factory.
- No risk of per-environment misconfiguration of a lossy operation.
- Callers who need control use the call-site API (explicit is better than implicit).
- `ConfigSchema` stays focused on the optimizer and cache, both of which have
  measurable acceptance criteria.

### Negative
- A caller who wants to set a default truncation strategy for all calls
  made through the `TokenOptimizer` facade must either subclass or construct
  `Truncator` directly.
- Changing the factory default requires a code change rather than a config file
  change. This is intentional: the factory default is an architectural decision,
  not an operational tunable.

### Neutral
- `ARCHITECTURE.md §4` (config table) notes: "`build_truncator` takes plain
  arguments (truncation has no config section yet)" — this ADR explains the
  "yet" is intentional and not a backlog item.

---

## Related Decisions

- **ADR-013** (Facade and Factory Pattern) — `build_truncator` lives in
  `src/factory.py` as the single composition entry point for `Truncator`.
- **ADR-009** (Error Handling) — truncation never raises on over-budget input;
  it truncates silently, which is why accepting a misconfigured budget without a
  gate would be dangerous.
