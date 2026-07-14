# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

This repository contains **TWO DISTINCT SYSTEMS**:

### 1. Bob Shell Knowledge Manager (Original Project)

A lightweight knowledge management framework for Bob Shell that provides structured documentation templates and workflows.

**Purpose:** Organize and maintain knowledge bases using Bob Shell's native capabilities  
**Technology:** Bash scripts, YAML configuration, Markdown templates  
**Complexity:** ~500 lines of configuration and scripts  

**Key Components:**
- Custom Bob Shell mode (`knowledge-manager`)
- 4 document templates (concept, guide, reference, research)
- 4 bash automation scripts
- Example knowledge bases

### 2. Token Optimization System (Week 19-20 Implementation)

A Python-based framework that reduces token usage for LLM operations through caching, optimization, and truncation.

**Purpose:** Reduce LLM token costs while preserving quality  
**Technology:** Python 3.11+, tiktoken, scikit-learn, numpy, pytest  
**Complexity:** ~3,500 lines of Python code (core system)  

**Key Components:**
- Multi-level caching (L1: exact, L2: semantic)
- Prompt optimization and token counting
- Text truncation strategies
- Monitoring and observability

### 3. Delegation Module (Experimental - Not Integrated)

A parallel sub-agent framework for repository analysis. **This is a separate system, not integrated with the token optimizer.**

**Purpose:** Parallel code repository analysis  
**Technology:** Python 3.11+, ThreadPoolExecutor  
**Complexity:** ~1,588 lines of Python code  
**Status:** Experimental, orphaned (not wired into runtime), demo-only. Held at a ~54% per-package coverage floor (`scripts/check_coverage_by_package.py`). Per the Phase-4 decision it stays a **separate, layering-clean subsystem** (not facade-wired — it solves a different problem domain); its only Phase-4 change was the B3 layering fix (shared utilities moved to `src/tools/`).  

**Key Components:**
- DelegationCoordinator (parallel execution)
- 6 specialized agents (security, performance, quality, architecture, documentation, research)
- Task queue with priority scheduling
- Result aggregation and reporting

**Note:** See `src/delegation/EXPERIMENTAL.md` and `docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md` for details.

---

## Building and Running

### Bob Shell Knowledge Manager

#### Installation

```bash
# Install the knowledge-manager mode to Bob Shell
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/install.sh
```

#### Initialize in Your Project

```bash
# Create knowledge base structure in your project
cd ~/Projects/your-project
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
```

#### Usage

```bash
# Start Bob Shell in knowledge-manager mode
bob --chat-mode=knowledge-manager

# Common tasks:
# - "Research [topic] and create a concept document"
# - "Create a guide for [task]"
# - "What do we know about [topic]?"
# - "Update [document] with [new information]"
```

#### Validate Knowledge Base

```bash
# Validate KB structure and cross-references
./scripts/validate-kb.sh
```

### Token Optimization System

#### Installation

```bash
# Install the package with dev + monitoring extras (single home: pyproject.toml)
pip install -e ".[dev,monitoring]"
```

#### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test suite
python3 -m pytest tests/cache/ -v
python3 -m pytest tests/optimizer/ -v
python3 -m pytest tests/monitoring/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

#### Using the System

```python
from src.optimizer import PromptOptimizer
from src.cache import MultiLevelCache
from src.monitoring import get_logger, get_metrics_collector

# Initialize components
optimizer = PromptOptimizer()
cache = MultiLevelCache()
logger = get_logger("main")
metrics = get_metrics_collector()

# Optimize a prompt
result = optimizer.optimize("Your prompt here")
logger.info("optimization_complete", savings=result["savings"])
```

#### Generating API Documentation

```bash
# Auto-generate API docs from source code
python3 scripts/generate_api_docs.py
```

---

## Development Conventions

### Bob Shell Knowledge Manager

#### Directory Structure

```
config/
├── custom_modes.yaml      # Bob Shell mode definition
├── settings.json          # Recommended settings
└── templates/             # Document templates
    ├── concept.md
    ├── guide.md
    ├── reference.md
    └── research.md

scripts/
├── install.sh            # Install mode to Bob Shell
├── init-project.sh       # Initialize KB in project
├── validate-kb.sh        # Validate KB structure
└── export-kb.sh          # Export to various formats

examples/
├── personal-wiki/        # Personal KB example
├── research-project/     # Research KB example
└── software-project/     # Software KB example
```

#### Knowledge Base Structure

When initialized in a project, creates:

```
docs/knowledge-base/
├── INDEX.md              # Master index
├── concepts/             # Core concepts and definitions
├── guides/               # How-to guides and tutorials
├── references/           # API docs and specifications
└── research/             # Research notes and findings
```

#### Document Naming Conventions

- **Concepts:** `concept-name.md`
- **Guides:** `task-name-guide.md`
- **References:** `api-name-reference.md`
- **Research:** `topic-YYYY-MM.md`

#### Template Standards

All templates include:
- Frontmatter with metadata
- Standard sections (Overview, Details, Examples, etc.)
- Cross-reference placeholders
- Related documents section

### Token Optimization System

#### Code Organization

```
src/
├── cache/          # Caching implementations (L1, L2, multi-level)
├── optimizer/      # Token counting and prompt optimization
├── truncation/     # Text truncation strategies
└── monitoring/     # Logging, metrics, health checks
```

#### Testing Strategy

- **Mock-based testing** - No external dependencies required
- **Test-to-code ratio:** 1.14:1 (higher is better)
- **Coverage gate:** >=80%, enforced by `fail_under` in `pyproject.toml` (the single home for the number; see [`STATUS.md`](STATUS.md) for the current measured snapshot)
- **Test categories:** Unit, integration, performance

#### Code Quality Standards

1. **Type Hints:** All functions must have complete type annotations
2. **Docstrings:** Google-style docstrings for all public APIs
3. **Error Handling:** Comprehensive with graceful degradation
4. **Performance:** L1 cache <1ms, L2 cache <100ms, optimization <10ms
5. **Logging:** Use structured logging (JSON format) via `src.monitoring`

#### Key Design Patterns

- **Strategy Pattern:** Truncation strategies, cache implementations
- **Factory Pattern:** Logger factory, metrics collector
- **Template Method:** Base cache class with concrete implementations
- **Singleton:** Global metrics collector, health checker

#### Monitoring Integration

Always integrate monitoring when adding new features:

```python
from src.monitoring import get_logger, get_metrics_collector

logger = get_logger("component_name")
metrics = get_metrics_collector()

# Log events
logger.info("event_name", key="value", latency_ms=5.0)

# Record metrics
metrics.record_cache_hit("L1", 0.5)
metrics.record_optimization(1000, 800, 10.0)
```

#### Performance Requirements

- **L1 Cache Lookup:** <1ms (O(1) hash table)
- **L2 Cache Lookup:** <100ms (O(n) similarity search)
- **Token Counting:** <10ms per 1000 tokens
- **Optimization:** <50ms per prompt
- **Overall Latency (p95):** <100ms

---

## Documentation

### Bob Shell Knowledge Manager Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 5-minute getting started guide
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Detailed installation
- **[docs/USAGE.md](docs/USAGE.md)** - Usage guide with examples
- **[docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md)** - Customization options
- **[docs/WORKFLOWS.md](docs/WORKFLOWS.md)** - Common workflows
- **[docs/COMPARISON.md](docs/COMPARISON.md)** - Comparison with LLM-Wiki

### Token Optimization System Documentation

- **[docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md](docs/architecture/ACTUAL_SYSTEM_ARCHITECTURE.md)** - Current implementation
- **[docs/MONITORING.md](docs/MONITORING.md)** - Monitoring and observability
- **[docs/api/README.md](docs/api/README.md)** - Auto-generated API reference
- **[docs/adr/](docs/adr/)** - Architecture Decision Records (12 ADRs)
- **[docs/INDEX.md](docs/INDEX.md)** - Complete documentation index

### Important Notes

1. **Deprecated Docs:** Files in `docs/architecture/deprecated/` describe the original planned architecture (not implemented) - ignore them
2. **Current Architecture:** Always refer to `ACTUAL_SYSTEM_ARCHITECTURE.md` for Token Optimization System implementation
3. **Dual Nature:** This repository contains both the simple KB framework AND the Python optimization system
4. **Optional Dependencies:** psutil is optional for Token Optimization System; gracefully degrades without it

---

## Common Tasks

### Bob Shell Knowledge Manager Tasks

**Add a new document template:**
1. Create template in `config/templates/`
2. Follow existing template structure
3. Include frontmatter and standard sections
4. Update mode instructions if needed
5. Add example to `examples/`

**Modify the knowledge-manager mode:**
1. Edit `config/custom_modes.yaml`
2. Update `roleDefinition`, `whenToUse`, or `customInstructions`
3. Test with `bob --chat-mode=knowledge-manager`
4. Update documentation

**Add a new script:**
1. Create in `scripts/` directory
2. Make executable: `chmod +x scripts/new-script.sh`
3. Follow bash best practices
4. Add error handling with `set -e`
5. Document in README

### Token Optimization System Tasks

**Add a new cache strategy:**
1. Extend `BaseCache` in `src/cache/base.py`
2. Implement required methods (`get`, `set`, `clear`, `get_stats`)
3. Add tests in `tests/cache/`
4. Update `MultiLevelCache` if needed
5. Document in API reference

**Add a new truncation strategy:**
1. Add strategy to `TruncationStrategies` in `src/truncation/strategies.py`
2. Implement strategy method
3. Add tests in `tests/truncation/`
4. Update `Truncator` auto-selection logic if needed

**Add monitoring metrics:**
1. Add metric recording to `MetricsCollector` in `src/monitoring/metrics.py`
2. Add corresponding dataclass if needed
3. Update `get_metrics()` output
4. Add tests in `tests/monitoring/`

---

## Project Status

⚠️ **Overall Status: Beta (7/10) — Not Production Ready**

See: `docs/knowledge-base/research/external-audit-2026-07-12.md` for complete audit findings and `docs/knowledge-base/guides/audit-remediation-action-plan.md` for remediation plan.

### Bob Shell Knowledge Manager
- **Status:** Functional, needs validation
- **Tests:** 45 tests passing
- **Version:** 1.0
- **Note:** Original project, well-documented

### Token Optimization System
- **Implementation:** Core library in place; unified facade/CLI + config wiring are Phase 4
- **Tests / Coverage:** see [`STATUS.md`](STATUS.md) (gate >=80%, enforced by `pyproject.toml`)
- **Maturity:** Beta — Not Production Ready (≈D- vs the institutional bar; [`STATUS.md`](STATUS.md) is authoritative)
- **Known Issues:** Phase-1 correctness bugs fixed (incl. the C-5 semantic-cache collision); Phase-4 integration gaps and residual documentation drift remain
- **Next:** Phase 3 supply-chain hardening, then Phase 4 integration and Phase 5 real validation

### Delegation Module (Experimental)
- **Status:** Functional but not integrated with core system
- **Coverage:** 0% (demo-only, no integration tests)
- **Purpose:** Parallel repository analysis (separate use case)
- **Note:** See `src/delegation/EXPERIMENTAL.md` for details

---

## Next Steps for Agents

When working on this codebase:

### For Bob Shell Knowledge Manager:
1. **Understand the simplicity** - It's just templates and scripts, not complex code
2. **Test with Bob Shell** - Always test mode changes with actual Bob Shell
3. **Follow conventions** - Use established naming and structure patterns
4. **Document examples** - Add examples for new features

### For Token Optimization System:
1. **Read architecture first** - Check `ACTUAL_SYSTEM_ARCHITECTURE.md`
2. **Test always** - Write tests before implementation (TDD)
3. **Monitor everything** - Add logging and metrics for new features
4. **Document APIs** - Use comprehensive docstrings; they auto-generate docs
5. **Follow patterns** - Use existing design patterns (Strategy, Factory, etc.)
6. **Performance matters** - Profile and optimize; meet latency targets
7. **Graceful degradation** - Handle missing dependencies

---

## Contact & Support

- **Documentation:** See `docs/INDEX.md` for complete documentation index
- **Issues:** Track in project management system
- **Architecture Questions:** Refer to ADRs in `docs/adr/`