# API Reference

Complete API reference for the Token Optimization System.

> Generated from source docstrings by `scripts/generate_api_docs.py`.
> Do not edit by hand — run the generator and commit. CI (`docs-freshness`)
> fails if this tree drifts from `src/` via `generate_api_docs.py --check`.

## Cache

- [base](cache/base.md) - `cache/base.py`
- [embeddings](cache/embeddings.md) - `cache/embeddings.py`
- [exact_cache](cache/exact_cache.md) - `cache/exact_cache.py`
- [multi_level_cache](cache/multi_level_cache.md) - `cache/multi_level_cache.py`
- [semantic_cache](cache/semantic_cache.md) - `cache/semantic_cache.py`

## Config

- [manager](config/manager.md) - `config/manager.py`
- [schema](config/schema.md) - `config/schema.py`
- [validator](config/validator.md) - `config/validator.py`

## Delegation

- [base](delegation/base.md) - `delegation/base.py`
- [coordinator](delegation/coordinator.md) - `delegation/coordinator.py`
- [pipeline](delegation/pipeline.md) - `delegation/pipeline.py`
- [registry](delegation/registry.md) - `delegation/registry.py`

## Delegation/Agents

- [architecture_agent](delegation/agents/architecture_agent.md) - `delegation/agents/architecture_agent.py`
- [documentation_agent](delegation/agents/documentation_agent.md) - `delegation/agents/documentation_agent.py`
- [performance_agent](delegation/agents/performance_agent.md) - `delegation/agents/performance_agent.py`
- [quality_agent](delegation/agents/quality_agent.md) - `delegation/agents/quality_agent.py`
- [research_agent](delegation/agents/research_agent.md) - `delegation/agents/research_agent.py`
- [security_agent](delegation/agents/security_agent.md) - `delegation/agents/security_agent.py`

## Embeddings

- [chunker](embeddings/chunker.md) - `embeddings/chunker.py`
- [index](embeddings/index.md) - `embeddings/index.py`
- [indexer](embeddings/indexer.md) - `embeddings/indexer.py`
- [store](embeddings/store.md) - `embeddings/store.py`

## Graph

- [builder](graph/builder.md) - `graph/builder.py`
- [graph](graph/graph.md) - `graph/graph.py`
- [ranker](graph/ranker.md) - `graph/ranker.py`
- [store](graph/store.md) - `graph/store.py`

## Monitoring

- [cost_reporting](monitoring/cost_reporting.md) - `monitoring/cost_reporting.py`
- [cost_tracker](monitoring/cost_tracker.md) - `monitoring/cost_tracker.py`
- [health](monitoring/health.md) - `monitoring/health.py`
- [logger](monitoring/logger.md) - `monitoring/logger.py`
- [metrics](monitoring/metrics.md) - `monitoring/metrics.py`

## Optimizer

- [prompt_optimizer](optimizer/prompt_optimizer.md) - `optimizer/prompt_optimizer.py`
- [token_counter](optimizer/token_counter.md) - `optimizer/token_counter.py`

## Root

- [__main__](root/__main__.md) - `__main__.py`
- [cli](root/cli.md) - `cli.py`
- [cold_start](root/cold_start.md) - `cold_start.py`
- [facade](root/facade.md) - `facade.py`
- [factory](root/factory.md) - `factory.py`
- [kb_paths](root/kb_paths.md) - `kb_paths.py`
- [limits](root/limits.md) - `limits.py`
- [pricing](root/pricing.md) - `pricing.py`
- [provenance](root/provenance.md) - `provenance.py`

## Tools

- [batch_file_reader](tools/batch_file_reader.md) - `tools/batch_file_reader.py`
- [component_analyzer](tools/component_analyzer.md) - `tools/component_analyzer.py`
- [kb_query](tools/kb_query.md) - `tools/kb_query.py`
- [safe_paths](tools/safe_paths.md) - `tools/safe_paths.py`

## Truncation

- [strategies](truncation/strategies.md) - `truncation/strategies.py`
- [truncator](truncation/truncator.md) - `truncation/truncator.py`

## Validation

- [__main__](validation/__main__.md) - `validation/__main__.py`
- [corpus](validation/corpus.md) - `validation/corpus.py`
- [manifest](validation/manifest.md) - `validation/manifest.py`
- [measure](validation/measure.md) - `validation/measure.py`
- [report](validation/report.md) - `validation/report.py`
