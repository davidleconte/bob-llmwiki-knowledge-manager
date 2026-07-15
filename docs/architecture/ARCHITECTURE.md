# Architecture

**Status:** Current (authoritative) · **Last updated:** 2026-07-14 · **Maturity:** see [`STATUS.md`](../../STATUS.md)

This is the **single authoritative architecture document** for the Python
token-optimization system in this repository. It supersedes
[`ACTUAL_SYSTEM_ARCHITECTURE.md`](ACTUAL_SYSTEM_ARCHITECTURE.md) (v1.0, deprecated)
and [`UNIFIED_ARCHITECTURE.md`](UNIFIED_ARCHITECTURE.md) (v2.0, superseded); both
predate the Phase-4 facade and no longer describe the running system. Decision
records live in [`../adr/`](../adr/); the generated API reference in
[`../api/`](../api/README.md).

> The repository also ships a separate Bash product, the **Bob Shell Knowledge
> Manager** (~500 lines), whose architecture is documented in
> [`../ARCHITECTURE.md`](../ARCHITECTURE.md). The two share a repo but are not one
> system. This document is about the Python token-optimization system (`src/`).

---

## 1. Context and goals

The token-optimization system reduces the tokens an LLM prompt costs, three ways,
each measured **separately** (never blended — blending is how the retracted
"68.96%" was manufactured):

- **Optimizer compression** — near-lossless removal of redundancy. The only
  "savings" headline: **~20% mean** on real in-repo prose (95% CI ≈ [19%, 21%],
  N=183), manifest-backed at `evaluation/results/validation-2026-07-14/`.
- **Cache recompute-avoidance** — a hit returns a prior result for 0 tokens;
  workload-dependent (a property of the request stream's repeat rate).
- **Truncation** — lossy budget-fit; reported, but excluded from savings.

Quality attributes that shape the design: determinism (reproducible cache and
validation), honesty (every published number cites a manifest), and a clean
layering boundary (`src/` never imports from `scripts/`).

## 2. Component overview

```mermaid
flowchart TD
    subgraph entry [Entry points]
        CLI["bob-optimize / python -m src<br/>src/cli.py"]
    end
    subgraph compose [Composition]
        FAC["TokenOptimizer facade<br/>src/facade.py"]
        FACT["factory builders<br/>src/factory.py"]
        CFG["ConfigManager + ConfigSchema<br/>src/config/"]
    end
    subgraph runtime [Runtime components]
        CACHE["MultiLevelCache<br/>L1 exact + L2 semantic<br/>src/cache/"]
        OPT["PromptOptimizer + TokenCounter<br/>src/optimizer/"]
        TRUNC["Truncator<br/>src/truncation/"]
        MON["metrics / logger / health / cost<br/>src/monitoring/"]
    end
    PRICE["pricing (single home)<br/>src/pricing.py"]

    CLI --> FAC
    CFG --> FAC
    FAC --> FACT
    FACT --> CACHE & OPT & TRUNC
    FAC --> MON
    OPT --> PRICE
    MON --> PRICE
```

Not shown, deliberately separate:

- **`src/validation/`** — the manifest-backed measurement harness (`python -m
  src.validation`). It *invokes* the runtime components to measure them; it is
  not on the request path. See §6.
- **`src/tools/`** — operational CLI utilities (batch file reader, component
  analyzer, KB query) relocated out of `scripts/` in Phase 4 to keep the
  `src → scripts` layering clean. Included in the coverage and type gates with a
  per-package floor of 85% (`scripts/check_coverage_by_package.py`).
- **`src/delegation/`** — an **experimental**, layering-clean subsystem that is
  *not* wired into the facade (see [`../../src/delegation/EXPERIMENTAL.md`](../../src/delegation/EXPERIMENTAL.md)).

## 3. Runtime dataflow

The facade holds no business logic — every operation delegates to an
already-tested component method (`src/facade.py:9`).

```mermaid
sequenceDiagram
    participant U as Caller / CLI
    participant F as TokenOptimizer
    participant Fa as factory
    participant O as PromptOptimizer
    participant C as MultiLevelCache
    participant M as monitoring

    U->>F: from_config(environment)
    F->>Fa: build_cache / build_optimizer / build_truncator
    Fa-->>F: live components (from ConfigSchema)
    F->>M: register cache / monitoring / system health checks
    U->>F: optimize(prompt, max_tokens?)
    F->>O: optimizer.optimize(...)
    O->>C: (optional) cache lookup / store
    O-->>F: {original_tokens, optimized_tokens, savings_percentage, quality_score}
    F-->>U: result dict
```

The facade's public surface — each method backs a CLI subcommand
(`src/facade.py:87`): `optimize`, `truncate`, `count`, `cache_stats`, `metrics`,
`cost_report`, `health`.

## 4. Configuration → runtime

Configuration has **one home** (`src/config/schema.py`) and reaches the runtime
through the factory, so the config-field → constructor-kwarg mapping cannot drift
(`src/factory.py:3`).

```mermaid
flowchart LR
    ENV["environment<br/>(dev / …)"] --> MGR["ConfigManager singleton<br/>src/config/manager.py"]
    MGR --> SCH["ConfigSchema<br/>cache · optimizer · monitoring"]
    SCH --> BC["build_cache"]
    SCH --> BO["build_optimizer"]
    BC --> MLC[MultiLevelCache]
    BO --> PO[PromptOptimizer]
```

`ConfigSchema` (`src/config/schema.py`) bundles three dataclasses; the defaults
that matter to the architecture:

| Section | Field | Default | Effect |
|---|---|---|---|
| `CacheConfig` | `l1_max_size` / `l2_max_size` | 1000 / 10000 | L1/L2 capacity |
| `CacheConfig` | `l2_similarity_threshold` | 0.85 | L2 semantic-hit floor |
| `OptimizerConfig` | `max_tokens` | 4096 | output cap (a truncation lever) |
| `OptimizerConfig` | `target_reduction` | 0.3 | compression target ratio |
| `OptimizerConfig` | `min_quality_score` | 0.8 | reject over-aggressive optimization |
| `MonitoringConfig` | `health_check_interval` | 60 | health cadence (seconds) |

`build_cache` maps every `CacheConfig` field onto the cache constructor;
`build_optimizer` maps `OptimizerConfig` via `PromptOptimizer.from_config`;
`build_truncator` takes plain arguments (truncation has no config section yet).

## 5. Components

- **Cache (`src/cache/`).** `MultiLevelCache` orchestrates **L1** `ExactCache`
  (exact-key fast path) and **L2** `SemanticCache` (TF-IDF similarity, hit floor
  0.85). A hit returns a stored result for 0 tokens. Deterministic (stateless
  `HashingVectorizer`); the C-5 colliding-key correctness bug is fixed.
- **Optimizer (`src/optimizer/`).** `PromptOptimizer` applies whitespace
  normalization and redundancy removal to `target_reduction`, gated by
  `min_quality_score`. `TokenCounter` counts real tokens via tiktoken, with a
  `chars/4` fallback (the `tiktoken_active` honesty flag distinguishes them).
- **Truncation (`src/truncation/`).** `Truncator` fits text to a token budget by
  a chosen strategy (default `semantic`). Lossy; no fidelity gate — reported
  separately, never counted as savings.
- **Monitoring (`src/monitoring/`).** Structured `logger`, `metrics` collector,
  `health` checker (wired to the live cache/monitoring/system by the facade), and
  `cost_tracker`/`cost_reporting` for Bobcoin cost accounting.
- **Pricing (`src/pricing.py`).** The **single home** for model rates
  (USD-per-1K) and Bobcoin conversion; the optimizer's cost estimate and the cost
  tracker both read it, so the two cannot drift.

## 6. Validation harness (`src/validation/`)

The harness is off the request path: it measures the real product and writes a
reproducibility manifest per run.

```mermaid
flowchart LR
    CORP["corpus<br/>real in-repo prose"] --> MEAS
    CFG2[ConfigSchema] --> MEAS["measure<br/>optimizer · cache · truncation · null"]
    MEAS --> REP["report.json"]
    MEAS --> MAN["manifest.json<br/>data hash · code SHA · seed ·<br/>library versions · tiktoken_active"]
```

The three mechanisms are measured and reported separately; a **null test**
(optimizer over shuffled/high-entropy text) must collapse to ≈0% or the
measurement is an artefact. CI gates on the null test + manifest completeness +
`tiktoken_active`, **not** on savings magnitude (gating a measurement would
re-incentivise fabrication). See [`../../src/validation/README.md`](../../src/validation/README.md).

## 7. Cross-cutting invariants (enforced in CI)

- **Layering.** `src/` never imports from `scripts/` (`check_layering.py`, AST-based).
- **One home per value.** Version, Python floor, pricing, coverage gate, and
  maturity status each have one canonical source, machine-checked
  (`check_value_homes.py`, `check_status_consistency.py`).
- **Manifest-backed numbers.** Every published savings/cost percentage cites a
  reproducible manifest (`check_savings_claims.py`).
- **Doc freshness.** `docs/api/` is regenerated from source docstrings and
  CI-checked (`generate_api_docs.py --check`).

## 8. Where to go next

- Decisions and their rationale: [`../adr/`](../adr/README.md) (ADR 001–013).
- Per-module API: [`../api/`](../api/README.md) (generated, drift-checked).
- Maturity, coverage, and the measured savings snapshot: [`STATUS.md`](../../STATUS.md).

---

## 9. Deployment

**Runtime context:** Local Python library and CLI. No server, no daemon, no container
required. Single-user, single-process.

| Constraint | Value | Source |
|---|---|---|
| **Python** | ≥ 3.11 (3.11 and 3.12 tested in CI) | `pyproject.toml:requires-python` · `.github/workflows/ci.yml` matrix |
| **OS** | macOS, Linux | CI matrix (ubuntu-latest, macOS available); Bash scripts are macOS/Linux only |
| **Core deps** | `numpy ≥ 1.24`, `scikit-learn ≥ 1.3`, `tiktoken ≥ 0.5` | `pyproject.toml:dependencies` |
| **Optional deps** | `psutil` (system metrics in health checks); gracefully absent if not installed | `pyproject.toml:[optional-dependencies].monitoring` |
| **Concurrency** | Single-process, synchronous. `ThreadPoolExecutor` used only in `src/delegation/` (experimental, not on the optimise path) | `src/facade.py` — all operations sync |
| **Persistence** | In-memory only. No disk cache, no database, no external state store | `src/cache/exact_cache.py`, `src/cache/semantic_cache.py` |
| **Network** | None required at runtime. `tiktoken` downloads its BPE vocabulary on first use (one-time, cacheable offline) | `src/optimizer/token_counter.py` |
| **Install** | `pip install -e ".[dev,monitoring]"` or `uv sync` | `pyproject.toml` |
| **CLI** | `python -m src <subcommand>` or `bob-optimize <subcommand>` | `src/__main__.py` |

---

## 10. Glossary

| Term | Definition | Source |
|---|---|---|
| **Bobcoin** | Internal unit for estimated LLM cost: `token_count × price_per_token × 1000`. Enables a model-agnostic cost metric. | `src/pricing.py` |
| **tiktoken_active** | Boolean flag in the validation manifest: `True` when tiktoken's BPE encoder is available and used for token counting; `False` when the character-count fallback is active. A `False` value means token counts are approximate. | `src/optimizer/token_counter.py`, `src/validation/manifest.py` |
| **manifest-backed** | A savings or cost figure is "manifest-backed" when it is accompanied by a `manifest.json` that records the data hash, code SHA, config, random seed, library versions, and `tiktoken_active`. This makes the measurement reproducible and auditable. | `src/validation/manifest.py:45-58` |
| **L1 cache** | The exact-match cache layer (`ExactCache`). Uses SHA-256 hashing for O(1) lookup. Governed by `CacheConfig.l1_max_size` and `CacheConfig.l1_ttl_seconds`. | `src/cache/exact_cache.py` |
| **L2 cache** | The semantic-match cache layer (`SemanticCache`). Uses TF-IDF + cosine similarity for approximate matching. Governed by `CacheConfig.l2_similarity_threshold`. Not used in the `optimize()` path (exact matching only there). | `src/cache/semantic_cache.py` |
| **Facade** | `TokenOptimizer` (`src/facade.py`). The single public composition point: accepts a `ConfigSchema`, builds all components via the factory, and exposes five high-level operations. Holds no business logic. | `src/facade.py:37` |
| **Factory** | `src/factory.py`. Three builder functions (`build_cache`, `build_optimizer`, `build_truncator`) that are the single home for the config-field → constructor-kwarg mapping. | `src/factory.py:25-70` |
| **Null test** | A validation run of the optimizer over shuffled, high-entropy text. A legitimate optimizer should produce ≈0% compression on random input. A failing null test indicates the measurement is an artefact of the test fixture, not the optimizer. | `src/validation/` |
| **target_reduction** | `OptimizerConfig` field: the optimizer's compression target as a ratio (0.0–1.0). Default 0.3 (30% token reduction). The optimizer uses this as a soft target, not a hard cap. | `src/config/schema.py:49` |
| **quality_score** | A float (0.0–1.0) returned by `PromptOptimizer.optimize()` representing estimated semantic preservation of the optimized output. Must meet or exceed `OptimizerConfig.min_quality_score` (default 0.8) for the optimization to be accepted. | `src/optimizer/prompt_optimizer.py` |
| **MECE** | Mutually Exclusive, Collectively Exhaustive. A framework (from McKinsey) for structuring analysis so that categories neither overlap nor have gaps. Used in this project's architecture audit framework. | `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` |
