# Delegation Module — Analysis Pipeline

**Status:** Integrated — Analysis Pipeline (see ADR-019)
**Coverage:** coordinator + base unit-tested; pipeline integration-tested; held at a **70% per-package floor** in `scripts/check_coverage_by_package.py`.
**Last Updated:** 2026-07-17

## Overview

This module implements a **parallel sub-agent delegation framework** for repository analysis. It is integrated with the Token Optimization System via `src/delegation/pipeline.py` — see ADR-019 for the design rationale.

## Purpose

The delegation module enables parallel execution of specialized analysis agents:
- **SecurityAgent** - Security vulnerability scanning
- **PerformanceAgent** - Performance bottleneck detection
- **QualityAgent** - Code quality assessment
- **ArchitectureAgent** - Architecture analysis
- **DocumentationAgent** - Documentation coverage
- **ResearchAgent** - Knowledge base search

## Architecture

```
DelegationCoordinator
├── ThreadPoolExecutor (parallel execution)
├── SubAgentRegistry (agent management)
└── Task Queue (priority-based scheduling)
    ├── SubAgentTask (task definition)
    └── SubAgentResult (result aggregation)
```

## Usage

See `examples/delegation_example.py` for a complete working example:

```python
from src.delegation import DelegationCoordinator, SubAgentTask
from src.delegation.agents import SecurityAgent, PerformanceAgent

# Create coordinator
coordinator = DelegationCoordinator(max_workers=5)

# Register agents
coordinator.register_agent(SecurityAgent("security-1"))
coordinator.register_agent(PerformanceAgent("performance-1"))

# Create tasks
tasks = [
    SubAgentTask(task_type="security", target="src/cache"),
    SubAgentTask(task_type="performance", target="src/cache"),
]

# Execute in parallel
results = coordinator.execute_parallel()
```

## Integration with Token Optimization System

The delegation module solves a **different but complementary problem** to the token optimizer:

| Aspect | Delegation Module | Token Optimizer |
|--------|------------------|-----------------|
| **Purpose** | Repository analysis | Prompt optimization |
| **Input** | Code directories | Text prompts |
| **Output** | Analysis reports (compressed) | Optimized prompts |
| **Execution** | Parallel (ThreadPool) | Sequential |
| **Latency** | Seconds to minutes | Milliseconds |
| **Use Case** | KB ingestion / repo audit | LLM cost reduction |

The **integration surface** is `src/delegation/pipeline.py`: each agent's output is compressed by `TokenOptimizer` before being written as a KB research document. The two systems remain **layering-clean** and independently testable. See ADR-019 for the rationale.

## Current Status

- ✅ **Functional:** All agents work correctly
- ✅ **Documented:** Clear examples and API docs
- ✅ **Tested:** `tests/delegation/` — 55 tests covering coordinator, base types, pipeline, and all 6 agent classes (containment + success path); **84% coverage** vs 70% floor
- ✅ **Layering-clean (Phase 4):** shared utilities live in `src/tools/` (`from src.tools.…`); the `src/ → scripts/` import gap (audit finding B3) is gone
- ✅ **Production pipeline:** `src/delegation/pipeline.py` — parallel analysis → TokenOptimizer compression → KB ingestion
- ✅ **CLI entry point:** `bob-optimize analyze <target> [--kb-path] [--output-dir] [--workers] [--depth] [--no-compress]`

## Future Possibilities

### Scenario 1: Batch Prompt Optimization
If you need to optimize 1000s of prompts in parallel, the delegation framework could be adapted.

**Effort:** 2-3 weeks  
**Benefit:** Marginal (current optimizer is already fast: <50ms)

### Scenario 2: Repository Analysis with Token Optimization
Use delegation agents to analyze repos, then optimize the analysis prompts before LLM calls.

**Effort:** 1-2 weeks  
**Benefit:** Moderate (reduces cost of repository analysis)

### Scenario 3: CI/CD Integration
Run delegation agents in CI/CD pipeline to analyze PRs and generate reports.

**Effort:** 1 week  
**Benefit:** High (automated code review)

## Development Guidelines

If you want to work on this module:

1. **Run the demo:**
   ```bash
   python3 examples/delegation_example.py
   # Output written to reports/delegation_report.txt (gitignored)
   ```

2. **Run existing tests:**
    ```bash
    python3 -m pytest tests/delegation/ -v
    # Covers: coordinator, base types, pipeline, and all 6 agent classes
    # Current coverage: 84% — floor: 70% (scripts/check_coverage_by_package.py)
    ```

3. **Add agent tests (if raising the floor):**
   ```bash
   # tests/delegation/ already exists
   # Add integration tests for individual agents
   # Raise floor in scripts/check_coverage_by_package.py after measuring
   ```

4. **Document integration points (if wiring to a service):**
   ```bash
   # Re-read docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md
   # Document the integration pattern in a new ADR
   # Add integration tests before raising coverage floor
   ```

## Maintenance

This module is **maintained and integrated** as an optional analysis pipeline. The core `src/delegation/pipeline.py` connector and the `bob-optimize analyze` CLI are the primary entry points.

**Contact:** See project maintainers

---

**Pipeline entry point:** `bob-optimize analyze <target>` — runs 6 agents in parallel, compresses each report, writes KB research docs.
**ADR:** [ADR-019: Delegation Pipeline Activation](../../docs/adr/019-delegation-pipeline-activation.md)
