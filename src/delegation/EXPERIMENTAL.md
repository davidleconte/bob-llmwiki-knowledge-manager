# ⚠️ EXPERIMENTAL: Delegation Module

**Status:** Experimental / Not Integrated (intentionally — see below)
**Coverage:** unit-tested (coordinator + base); held at a **52% per-package floor** in `scripts/check_coverage_by_package.py`. Agents are intentionally not integration-tested. Not integrated with the optimizer, by design.
**Last Updated:** 2026-07-14

## Overview

This module implements a **parallel sub-agent delegation framework** for repository analysis. It is **NOT integrated** with the core token optimization system and serves a completely different purpose.

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
    SubAgentTask(task_type="performance", target="src/cache")
]

# Execute in parallel
results = coordinator.execute_parallel()
```

## Why Not Integrated?

The delegation module and token optimizer solve **different problems**:

| Aspect | Delegation Module | Token Optimizer |
|--------|------------------|-----------------|
| **Purpose** | Repository analysis | Prompt optimization |
| **Input** | Code directories | Text prompts |
| **Output** | Analysis reports | Optimized prompts |
| **Execution** | Parallel (ThreadPool) | Sequential |
| **Latency** | Seconds to minutes | Milliseconds |
| **Use Case** | CI/CD analysis | LLM cost reduction |

**Integration would add complexity without benefit.**

See: `docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md`

## Current Status

- ✅ **Functional:** All agents work correctly
- ✅ **Documented:** Clear examples and API docs
- ✅ **Unit-tested:** `tests/delegation/` covers the coordinator + base types (~54% floor); the `agents/*` subpackage is intentionally not integration-tested
- ✅ **Layering-clean (Phase 4):** the shared analysis utilities the agents use now live in `src/tools/` (imported as `from src.tools.…`); the old `src/ -> scripts/` import (audit finding B3) is gone
- ❌ **Not Used:** Only in demo script
- ❌ **Not Integrated:** Separate from core system, **by design** (Phase-4 decision — not facade-wired)

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
   uv run pytest tests/delegation/ -v
   # Covers: coordinator, base types, documentation-agent containment
   # Target floor: 52% (scripts/check_coverage_by_package.py)
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

This module is **maintained but not actively developed**. It works correctly but is not part of the core system.

**Contact:** See project maintainers

---

**Remember:** This is a separate system. Do not assume it's integrated with the token optimizer.
