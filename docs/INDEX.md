# Token Optimization System — Documentation Index

> **Looking for the docs?** The primary entry point is the Diátaxis-organized
> **[documentation home](README.md)** (Tutorials · How-to · Reference · Explanation).
> This page is the exhaustive index, kept for completeness; canonical status is
> always [`STATUS.md`](../STATUS.md).

**Version:** 3.0
**Last Updated:** 2026-07-18
**Status:** Beta — Not Production Ready (A+; all structural gaps closed — see [`STATUS.md`](../STATUS.md))

---

## Quick Links

- [README](../README.md) - Project overview and getting started
- [CHANGELOG](../CHANGELOG.md) - Version history and changes
- [Architecture](architecture/ARCHITECTURE.md) - Authoritative system architecture
- [API Reference](api/README.md) - Complete API documentation
- [Monitoring Guide](MONITORING.md) - Observability and metrics
- [Security Policy](../SECURITY.md) - Vulnerability disclosure
- [Threat Model](security/THREAT_MODEL.md) - STRIDE analysis (supersedes ADR-012)

---

## Documentation Structure

### 1. Core Documentation

- **[README](../README.md)** - Project overview, installation, quick start
- **[CHANGELOG](../CHANGELOG.md)** - Version history and release notes
- **[MONITORING](MONITORING.md)** - Monitoring, logging, and health checks

### 2. Quick Start Guides

**Location:** `docs/`

- **[Quick Start Guide](quick-start.md)** — 5-minute getting started guide
- **[Installation Guide](INSTALLATION.md)** — Detailed installation instructions
- **[Usage Guide](USAGE.md)** — Comprehensive usage examples
- **[Customization Guide](CUSTOMIZATION.md)** — Customization options
- **[Workflows Guide](WORKFLOWS.md)** — Common workflows and patterns
- **[Repository Analysis Workflow](REPOSITORY_ANALYSIS_WORKFLOW.md)** — Token-efficient repo analysis

### 3. Testing & Validation

**Location:** `evaluation/`

- **[Honest Assessment](../evaluation/HONEST_ASSESSMENT.md)** - Critical analysis with real measurements
- **[Token Savings Test Plan](TOKEN_SAVINGS_TEST_PLAN.md)** - Validation methodology
- **[Validation Report (Phase 5, measured)](../evaluation/results/validation-2026-07-14/report.json)** — manifest-backed run (`report.json` + `manifest.json`); the earlier `validation_report.json` (68.96%) is retracted/fabricated

**Key Findings:**
- ✅ 1112 tests passing — see [STATUS.md](../STATUS.md) for the current live snapshot; gate is `pyproject.toml`
- ✅ Token savings **measured**: ~20% mean optimizer compression (95% CI [19%, 21%], N=183) — manifest-backed at `evaluation/results/validation-2026-07-14/`; the earlier 68.96% is retracted
- ✅ A+ (4.30/4.30) — all 4 structural gaps closed (SLA v1.0, sentence-transformers, full mypy scope, CODEOWNERS)
- ✅ Delegation pipeline wired: `bob-optimize analyze` (ADR-019)
- ⚠️ Mock-based testing (no real LLM API integration)

### 4. Architecture Documentation

**Location:** `docs/architecture/`  
**Overview:** [Architecture README](architecture/README.md)

#### Current Architecture

- **[Architecture](architecture/ARCHITECTURE.md)** ⭐ — the single authoritative
  architecture document (v3.0): components, runtime dataflow, config→runtime,
  KB subsystems (P2 embeddings, P3 graph, P4 query quality), delegation pipeline
  (ADR-019), validation harness, SLA, and glossary.
- **[Bob Shell KB Manager Architecture](kb-manager/ARCHITECTURE.md)** — arc42 v2.1
  for the Bash product: mode, templates, scripts, deployment.

#### Superseded / Deprecated

- **[Actual System Architecture](architecture/deprecated/ACTUAL_SYSTEM_ARCHITECTURE.md)** — v1.0, superseded by ARCHITECTURE.md
- **[Unified Architecture](architecture/deprecated/UNIFIED_ARCHITECTURE.md)** — v2.0, superseded (predates the Phase-4 facade)
- **[Master Architecture](architecture/deprecated/MASTER.md)** — Original design (deprecated)
- **[Quality Attributes](architecture/deprecated/QUALITY_ATTRIBUTES.md)** — Quality goals (deprecated; metrics retracted)
- **[Documentation Plan](architecture/deprecated/DOCUMENTATION_PLAN.md)** — Planning doc (deprecated)

**Note:** the deprecated documents describe an earlier or planned system. Refer to [ARCHITECTURE.md](architecture/ARCHITECTURE.md) for the current implementation.

### 5. API Reference

**Location:** `docs/api/`
**Overview:** [API Reference](api/README.md)

Auto-generated API documentation from source code (see [full API reference](api/README.md)):

#### Cache Module
- [base](api/cache/base.md) — Base cache interface
- [embeddings](api/cache/embeddings.md) — Embedding generation (`EmbeddingGenerator`, backend fallback chain)
- [exact_cache](api/cache/exact_cache.md) — L1 exact match caching
- [multi_level_cache](api/cache/multi_level_cache.md) — L1/L2 cache orchestration
- [semantic_cache](api/cache/semantic_cache.md) — L2 semantic similarity caching

#### Config Module
- [schema](api/config/schema.md) — `ConfigSchema` (single home for all defaults)
- [manager](api/config/manager.md) — `ConfigManager` singleton
- [validator](api/config/validator.md) — Config validation

#### Delegation Module
- [pipeline](api/delegation/pipeline.md) — `AnalysisPipeline` — 6-agent parallel analysis → KB ingestion
- [coordinator](api/delegation/coordinator.md) — `DelegationCoordinator` — parallel execution
- [base](api/delegation/base.md) — `SubAgentBase`, `SubAgentTask`, `SubAgentResult`
- [registry](api/delegation/registry.md) — `SubAgentRegistry` — agent management
- Agents: [security](api/delegation/agents/security_agent.md) · [performance](api/delegation/agents/performance_agent.md) · [quality](api/delegation/agents/quality_agent.md) · [architecture](api/delegation/agents/architecture_agent.md) · [documentation](api/delegation/agents/documentation_agent.md) · [research](api/delegation/agents/research_agent.md)

#### Embeddings Module (P2 KB Index)
- [chunker](api/embeddings/chunker.md) — `MarkdownChunker` — `##`-boundary splitting + GFM tables
- [index](api/embeddings/index.md) — `PersistentEmbeddingIndex` — disk-backed vector index
- [indexer](api/embeddings/indexer.md) — `KBIndexer` — sync + query interface
- [store](api/embeddings/store.md) — `FileBackedVectorStore` — atomic `.npy`/JSON I/O

#### Graph Module (P3 Knowledge Graph)
- [graph](api/graph/graph.md) — `KnowledgeGraph`, `NodeProps`, `Edge`
- [builder](api/graph/builder.md) — `KnowledgeGraphBuilder` — explicit + semantic edges
- [ranker](api/graph/ranker.md) — `GraphRanker` — PageRank re-ranking
- [store](api/graph/store.md) — `GraphStore` — atomic JSON persistence

#### Monitoring Module
- [health](api/monitoring/health.md) — Health checking system
- [logger](api/monitoring/logger.md) — Structured logging (`StructuredLogger`)
- [metrics](api/monitoring/metrics.md) — Metrics collection (`MetricsCollector`)
- [cost_tracker](api/monitoring/cost_tracker.md) — Bobcoin cost tracking
- [cost_reporting](api/monitoring/cost_reporting.md) — Cost reports

#### Optimizer Module
- [prompt_optimizer](api/optimizer/prompt_optimizer.md) — Prompt optimization
- [token_counter](api/optimizer/token_counter.md) — Token counting (tiktoken + fallback)

#### Truncation Module
- [strategies](api/truncation/strategies.md) — Truncation strategies
- [truncator](api/truncation/truncator.md) — Text truncation

#### Tools Module
- [kb_query](api/tools/kb_query.md) — `KnowledgeBaseQuery` — 3-tier hybrid search
- [component_analyzer](api/tools/component_analyzer.md) — Static component analysis
- [batch_file_reader](api/tools/batch_file_reader.md) — Batch file reading with path containment
- [safe_paths](api/tools/safe_paths.md) — Path-traversal containment (`resolve_within`)

#### Root / Facade
- [facade](api/root/facade.md) — `TokenOptimizer` facade
- [factory](api/root/factory.md) — Builder functions
- [cli](api/root/cli.md) — `bob-optimize` CLI subcommands
- [pricing](api/root/pricing.md) — Model rates + Bobcoin conversion

### 6. Architecture Decision Records (ADRs)

**Location:** `docs/adr/`
**Overview:** [ADR README](adr/README.md)

19 ADRs documenting key architectural decisions (ADR-012 superseded):

| Category | ADRs |
|---|---|
| Technology | 001 Python, 008 Token counting |
| Architecture | 002/006 Caching, 007 Sync vs async, 013 Facade/factory, 016 Truncation config, 017 Knowledge graph, 018 Query quality, 019 Delegation pipeline |
| Algorithms | 003 TF-IDF, 004 Semantic similarity, 005 Batch processing, 014 KB embedding scorer, 015 Persistent embedding index |
| Quality | 009 Error handling, 010 Testing, 011 Monitoring, ~~012~~ Security (superseded by THREAT_MODEL.md) |

### 7. User Guides

- **[Installation](INSTALLATION.md)** — Setup and installation
- **[Quick Start](quick-start.md)** — Getting started guide
- **[Usage](USAGE.md)** — Detailed usage instructions
- **[Workflows](WORKFLOWS.md)** — Common workflows
- **[Repository Analysis Workflow](REPOSITORY_ANALYSIS_WORKFLOW.md)** — Token-efficient repository audit workflow
- **[Customization](CUSTOMIZATION.md)** — Configuration and customization
- **[Bob IDE Guide](BOB-IDE-GUIDE.md)** — Bob IDE mode picker, skill activation, persistence
- **[SLA](sla.md)** — Latency/throughput targets and measurement methodology
- **[Comparison](archive/COMPARISON.md)** — Comparison with alternatives (archived)

### 8. Configuration

**Location:** `config/`

- **custom_modes.yaml** — Custom mode configurations
- **settings.json** — System settings
- **templates/** — Document templates (concept, guide, reference, research)

### 9. Examples

**Location:** `examples/`

- **personal-wiki/** — Personal knowledge base example
- **research-project/** — Research project example
- **software-project/** — Software project example

### 10. Evaluation

**Location:** `evaluation/`

- **`results/validation-2026-07-14/`** — Authoritative manifest-backed measurement run (`report.json` + `manifest.json`)
- **`VALIDATION_DISCLAIMER.md`** — Retraction notice for the fabricated 68.96% figure
- **`HONEST_ASSESSMENT.md`** — Critical analysis with real measurements

### 11. Scripts

**Location:** `scripts/`

- **setup.sh** — Full-stack setup: Python extras + embedding index build + stack validation
- **install.sh** — Install knowledge-manager mode into Bob Shell global config
- **init-project.sh** — Scaffold KB directory structure in a target project
- **validate-kb.sh** — Validate KB structure and broken links
- **export-kb.sh** — Export KB to multiple formats (markdown, Obsidian, HTML, PDF)
- **generate_api_docs.py** — Auto-generate `docs/api/` from source docstrings
- **check_coverage_by_package.py** — Per-package coverage floor enforcement

---

## Implementation Status

### Completed Components ✅

| Component | Package | CLI entry points | Documentation |
|---|---|---|---|
| **Token Counter** | `src/optimizer/` | `bob-optimize count` | [API](api/optimizer/token_counter.md) |
| **Prompt Optimizer** | `src/optimizer/` | `bob-optimize optimize` | [API](api/optimizer/prompt_optimizer.md) |
| **Truncation** | `src/truncation/` | `bob-optimize truncate` | [API](api/truncation/) |
| **Cache System** | `src/cache/` | `bob-optimize cache-stats` | [API](api/cache/) |
| **Config** | `src/config/` | `bob-optimize config` | [API](api/config/) |
| **Monitoring** | `src/monitoring/` | `bob-optimize health`, `metrics`, `cost-report` | [Guide](MONITORING.md) |
| **KB Embedding Index (P2)** | `src/embeddings/` | `bob-optimize kb-index` | [API](api/embeddings/) |
| **Knowledge Graph (P3)** | `src/graph/` | `bob-optimize graph-build/query/health` | [API](api/graph/) |
| **KB Search (P4)** | `src/tools/kb_query.py` | `bob-optimize kb-search`, `kb-status` | [API](api/tools/kb_query.md) |
| **Delegation Pipeline** | `src/delegation/` | `bob-optimize analyze` | [API](api/delegation/) · [ADR-019](adr/019-delegation-pipeline-activation.md) |
| **Validation Harness** | `src/validation/` | `python -m src.validation` | [API](api/validation/) |
| **API Docs** | `docs/api/` | `scripts/generate_api_docs.py` | [Index](api/README.md) |

> Current test counts and coverage: see [`STATUS.md`](../STATUS.md) (single source of truth).

---

## Key Features

### Token Optimization
- **Prompt compression** — ~20% mean on real prose (manifest-backed, null-test validated)
- **Multi-level cache** — L1 exact (SHA-256, O(1)) + L2 semantic (TF-IDF cosine)
- **Intelligent truncation** — lossy budget-fit (4 strategies), reported separately

### Knowledge Base Intelligence
- **Persistent embedding index (P2)** — `sentence-transformers` / `mlx-embeddings` / hashing fallback
- **Knowledge graph (P3)** — PageRank re-ranking, orphan detection, hub analysis
- **Query quality (P4)** — recency weighting, date filtering, hybrid keyword+embedding scoring

### Analysis Pipeline
- **Delegation pipeline** — 6 parallel agents (security, performance, quality, architecture, documentation, research) → TokenOptimizer → KB ingestion via `bob-optimize analyze`

### Monitoring & Observability
- **Structured Logging** — JSON-formatted logs with automatic enrichment
- **Metrics Collection** — Cache, optimization, and truncation metrics
- **Health Checking** — Component and system health monitoring
- **Cost Tracking** — Bobcoin budget + spend reporting

See [MONITORING.md](MONITORING.md) for details.

### API Documentation
- **Auto-generated** — Extracted from source code docstrings (CI-checked for drift)
- **Type-annotated** — Full type annotations, mypy-clean
- **Organized** — By module (14 packages)

See [API Reference](api/README.md) for details.

---

## Navigation by Role

### Developers
1. Start with [Quick Start](quick-start.md) (Bob Shell KB) or the [optimize-a-prompt tutorial](tutorials/optimize-a-prompt.md) (Python TOS)
2. Review [API Reference](api/README.md)
3. Check the [Architecture](architecture/ARCHITECTURE.md)
4. See [Usage Guide](USAGE.md) for examples

### DevOps / SRE
1. Review [Monitoring Guide](MONITORING.md)
2. Check [Installation](INSTALLATION.md)
3. See [Health Checking](api/monitoring/health.md)
4. Review [SLA](sla.md) for latency/throughput targets

### Architects
1. Read the [Architecture](architecture/ARCHITECTURE.md)
2. Review [ADRs](adr/README.md)
3. See [STRIDE Threat Model](security/THREAT_MODEL.md)
4. Check the [SLA](sla.md) for quality scenarios

### Contributors
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
2. Check [GOVERNANCE.md](../GOVERNANCE.md)
3. Review [STATUS.md](../STATUS.md) for the current maturity/coverage baseline

---

## Getting Started

**One-step full-stack setup (recommended):**

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/setup.sh
```

**Manual installation (Python extras only):**

```bash
pip install -e ".[dev,monitoring]"
```

**Optimize a prompt (CLI):**

```bash
echo "Your long prompt here" | bob-optimize optimize -
```

**Optimize a prompt (Python library):**

```python
from src.facade import TokenOptimizer

optimizer = TokenOptimizer()
result = optimizer.optimize("Your prompt here")
print(result["optimized_text"])        # compressed text
print(result["compression_ratio"])     # e.g. 0.80 means output is 0.8x the input size
```

**Run a repository analysis:**

```bash
bob-optimize analyze src/ --kb-path docs/knowledge-base --output-dir /tmp/analysis
```

See [Quick Start](quick-start.md) for the Bob Shell KB Manager onboarding.

---

## Documentation Standards

- **Format:** Markdown with Mermaid diagrams
- **Style:** Clear, concise, example-driven (arc42 / Tier-1)
- **Structure:** Diátaxis quadrants (Tutorials · How-to · Reference · Explanation)
- **Maintenance:** API docs auto-generated from source (CI-checked for drift)
- **Honesty:** All performance/savings figures must cite a reproducible manifest

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 3.0 | 2026-07-18 | Added embeddings/graph/delegation modules; fixed stale links; updated component table |
| 2.0 | 2026-07-12 | Added monitoring, API docs, reorganized structure |
| 1.0 | 2026-07-12 | Initial release with core implementation |

---

**Last Updated:** 2026-07-18
**Status:** Beta — Not Production Ready; A+ (4.30/4.30) — see [`STATUS.md`](../STATUS.md)