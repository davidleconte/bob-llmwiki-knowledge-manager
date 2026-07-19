---
title: "Delegation Analysis Pipeline"
category: concept
tags: [delegation, pipeline, agents, compact-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Delegation Analysis Pipeline

## Overview

The delegation analysis pipeline (`src/delegation/`) is a **parallel sub-agent framework**
that runs 6 specialised analysis agents concurrently against a target directory, compresses
each agent report through `TokenOptimizer`, and writes the results as KB research documents.
It is accessed via `bob-optimize analyze` and is layering-clean — it calls `TokenOptimizer`
as a client and does not modify the facade's `optimize()` path.

## Key Points

- **6 parallel agents:** Security · Performance · Quality · Architecture · Documentation · Research
- **Thin connector pattern:** `src/delegation/pipeline.py` (~175 lines) wires the delegation
  infrastructure to the Token Optimizer without coupling them
- **KB-aware by design:** `ResearchAgent` loads prior KB findings first (via
  `KnowledgeBaseQuery`) so duplicate analysis of known issues is avoided
- **Token-compressed output:** each agent report is compressed through `TokenOptimizer`
  before being written to `output_dir` — reducing KB document size and future retrieval cost
- **Coverage:** 84% measured, 70% floor; all 6 agents smoke-tested + containment-tested

## Details

### The 6 Agents

| Agent | Task type | What it analyses |
|-------|-----------|-----------------|
| `SecurityAgent` | `security` | Vulnerability patterns, unsafe API usage, path traversal risks |
| `PerformanceAgent` | `performance` | Bottlenecks, O(n²) patterns, memory allocation hot spots |
| `QualityAgent` | `quality` | Code complexity, test coverage, duplication, type safety |
| `ArchitectureAgent` | `architecture` | Layering, coupling, cohesion, dependency direction |
| `DocumentationAgent` | `documentation` | Docstring coverage, stale comments, missing README sections |
| `ResearchAgent` | `research` | Prior KB findings — runs first; all other agents depend on it |

### Execution Model

```
bob-optimize analyze <target>
         │
         ▼
  AnalysisPipeline.run()         ← src/delegation/pipeline.py
         │
         ├─► ResearchAgent       ← runs first; loads KB context via KnowledgeBaseQuery
         │         (completes)
         │
         ├─► SecurityAgent  ┐
         ├─► PerformanceAgent│   ← run in parallel (ThreadPoolExecutor)
         ├─► QualityAgent   │     after ResearchAgent completes
         ├─► ArchitectureAgent│
         └─► DocumentationAgent┘
                   │
                   ▼ (each result)
           TokenOptimizer.optimize()   ← ~20% compression (manifest-backed)
                   │
                   ▼
         output_dir/<agent>-<timestamp>.md   ← written as KB research doc
```

### Layering Boundary

The delegation module has a **one-way dependency** on the Token Optimization System:

```
pipeline.py → TokenOptimizer   (delegation calls TOS as a client)
pipeline.py → KnowledgeBaseQuery  (delegation reads the KB)
```

`TokenOptimizer` (and the facade) does **not** depend on `src/delegation/`. The two
subsystems remain independently testable and independently deployable. See
[ADR-019](../../adr/019-delegation-pipeline-activation.md).

### Path-Traversal Containment

All target paths are resolved through `src/tools/safe_paths.resolve_within` before being
passed to agents. Absolute paths and `../` escapes are rejected. The containment is
verified by `tests/delegation/test_agents_containment.py`.

## Benefits

| Benefit | Detail |
|---------|--------|
| **Parallel analysis in one command** | 6 agents run concurrently — a full repo audit that would take ~6 sequential invocations completes in the time of the slowest single agent |
| **No re-derivation** | `ResearchAgent` loads prior KB findings before other agents run — issues already documented are not re-analysed in new runs |
| **Compressed KB output** | Each report is token-optimized before storage — retrieval cost on subsequent KB queries is lower |
| **Structured KB integration** | Output is written as standard KB research documents (frontmatter, categories, cross-references) — immediately queryable via `bob-optimize kb-search` |
| **Incrementally extensible** | New agent types can be registered in `SubAgentRegistry` without changing `pipeline.py` or the facade |

## Examples

### Run a full repository analysis (CLI)

```bash
bob-optimize analyze src/ \
  --kb-path docs/knowledge-base \
  --output-dir /tmp/analysis \
  --workers 6 \
  --depth 3
```

### Skip compression (useful for debugging agent output)

```bash
bob-optimize analyze src/cache --no-compress --output-dir /tmp/debug
```

### Check integration health

```bash
bob-optimize kb-status   # shows embedding backend, index freshness, compression availability
```

### Python API

```python
from src.delegation.pipeline import AnalysisPipeline

pipeline = AnalysisPipeline(
    kb_path="docs/knowledge-base",
    output_dir="/tmp/analysis",
    compress=True,
    max_workers=6,
)
result = pipeline.run(target="src/")
print(f"Agents succeeded: {result.succeeded}")
print(f"Tokens saved by compression: {result.total_tokens_saved}")
```

## Related Documents

- [Knowledge Graph Layer](./knowledge-graph-layer.md)
- [KB-TOS Shared Embedding Layer](./kb-tos-embedding-layer.md)
- [ADR-019: Delegation Pipeline Activation](../../adr/019-delegation-pipeline-activation.md)
- [Delegation Integration Analysis 2026-07-13](../research/delegation-integration-analysis-2026-07-13.md)

## References

- [Architecture §2 — Delegation subsystem](../../architecture/ARCHITECTURE.md)
- [src/delegation/EXPERIMENTAL.md](../../../src/delegation/EXPERIMENTAL.md)

---
*Last Updated: 2026-07-18*
*Category: Concept*
