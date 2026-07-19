---
title: "bob-optimize CLI Reference"
category: reference
tags: [reference, cli, token-optimization]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# bob-optimize CLI Reference

## Overview

`bob-optimize` is the Token Optimization System (TOS) CLI. It exposes the cache,
optimizer, truncation, monitoring, knowledge graph, and delegation subsystems as
composable subcommands. Install with `pip install -e ".[dev]"`.

## Synopsis

```bash
uv run bob-optimize [GLOBAL_OPTIONS] <subcommand> [SUBCOMMAND_OPTIONS]
```

## Global Options

| Option | Description |
|---|---|
| `-e / --environment ENV` | Config environment (default: `dev`). Loads `config/<ENV>.yaml`. |
| `--json` | Emit raw JSON output (machine-readable). |
| `--verbose` | Restore INFO-level component logging (suppressed by default). |
| `-h / --help` | Print usage and exit. |

## Subcommands

### `optimize` — Optimize a prompt for token efficiency

```bash
uv run bob-optimize optimize <text>
uv run bob-optimize optimize - < prompt.txt    # read stdin
uv run bob-optimize optimize "Your prompt here" --max-tokens 2000
```

| Option | Description |
|---|---|
| `text` | Prompt text, or `-` to read stdin |
| `--max-tokens N` | Cap on optimized tokens (overrides config) |

Applies whitespace normalisation, redundancy removal, and structural compression.
Reports original tokens, optimized tokens, and compression ratio.

---

### `truncate` — Truncate text to a token budget

```bash
uv run bob-optimize truncate "Long text..." --max-tokens 500
uv run bob-optimize truncate - --max-tokens 1000 --strategy end < file.txt
```

| Option | Description |
|---|---|
| `text` | Text, or `-` to read stdin |
| `--max-tokens N` | Token budget |
| `--strategy NAME` | Truncation strategy (default from config). Options: `end`, `middle`, `smart` |

---

### `count` — Count tokens in text

```bash
uv run bob-optimize count "Some text"
echo "pipeline text" | uv run bob-optimize count -
```

Returns the raw token count using the configured tokeniser (tiktoken `cl100k_base`).

---

### `cache-stats` — Show multi-level cache statistics

```bash
uv run bob-optimize cache-stats
uv run bob-optimize cache-stats --json
```

Displays L1 (ExactCache) and L2 (SemanticCache) hit rates, entry counts, evictions,
and overall multi-level stats for the current session.

---

### `cost-report` — Show a cost report

```bash
uv run bob-optimize cost-report
uv run bob-optimize cost-report --json
```

Summarises token costs in Bobcoins (1 Bobcoin = $0.000015 / token at gpt-4 rates),
broken down by operation type.

---

### `metrics` — Show the metrics summary

```bash
uv run bob-optimize metrics
uv run bob-optimize metrics --json
```

Reports RED metrics (Rate, Errors, Duration) for each TOS component: optimizer,
cache, truncation. Includes p50/p95 latencies.

---

### `health` — Run health checks

```bash
uv run bob-optimize health
uv run bob-optimize health --json
```

Runs the registered health check suite (cache capacity, embedding backend, disk
space, dependency availability). Exit code `0` = all healthy; `1` = degraded.

---

### `config` — Show the effective configuration

```bash
uv run bob-optimize config
uv run bob-optimize config --json
```

Prints the merged configuration (defaults + environment overrides). Useful for
confirming which `cache.l1_max_size`, `optimizer.max_tokens`, etc. are active.

---

### `graph-build` — Build KB knowledge graph

```bash
uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
uv run bob-optimize graph-build \
    --kb-path docs/knowledge-base \
    --graph-path .bob/kb-graph.json \
    --semantic-threshold 0.3 \
    --with-semantic
```

| Option | Default | Description |
|---|---|---|
| `--kb-path PATH` | `docs/knowledge-base` | KB root directory |
| `--graph-path PATH` | `.bob/kb-graph.json` | Output graph file |
| `--semantic-threshold F` | `0.3` | Min cosine similarity for a semantic edge |
| `--with-semantic` | off | Derive semantic edges from the embedding index (requires `.bob/kb-index/`) |

Outputs: nodes count, edges count, graph path, semantic threshold used.

---

### `graph-query` — Show neighbourhood context for a KB document

```bash
uv run bob-optimize graph-query concepts/token-optimization.md
uv run bob-optimize graph-query concepts/caching.md --depth 2
uv run bob-optimize graph-query guides/setup-token-optimization.md \
    --edge-types explicit semantic
```

| Option | Default | Description |
|---|---|---|
| `doc_id` | _(required)_ | KB-relative path (e.g. `concepts/caching.md`) |
| `--depth N` | `1` | BFS traversal depth |
| `--graph-path PATH` | `.bob/kb-graph.json` | Graph file to read |
| `--edge-types TYPE…` | all | Edge types to traverse: `explicit` `semantic` `broken` |

---

### `graph-health` — Show KB graph health

```bash
uv run bob-optimize graph-health
uv run bob-optimize graph-health --top-k 10
```

| Option | Default | Description |
|---|---|---|
| `--graph-path PATH` | `.bob/kb-graph.json` | Graph file |
| `--top-k N` | `5` | Number of hub docs to show |

Reports: total nodes/edges, orphan count, top hub documents by degree, broken link count.

---

### `kb-status` — Show KB integration health

```bash
uv run bob-optimize kb-status
uv run bob-optimize kb-status --kb-path docs/knowledge-base --json
```

| Option | Default | Description |
|---|---|---|
| `--kb-path PATH` | `docs/knowledge-base` | KB root |
| `--index-path PATH` | `.bob/kb-index` | Embedding index directory |
| `--graph-path PATH` | `.bob/kb-graph.json` | Graph file |

Checks: embedding backend (MiniLM vs TF-IDF fallback), index freshness (stale if
any KB doc is newer than the index), compression availability, graph file presence.

---

### `analyze` — Run parallel delegation analysis

```bash
uv run bob-optimize analyze src/cache
uv run bob-optimize analyze src/ --workers 8 --depth deep
uv run bob-optimize analyze src/optimizer --no-compress \
    --output-dir docs/knowledge-base/research
```

| Option | Default | Description |
|---|---|---|
| `target` | _(required)_ | Directory or file to analyse |
| `--kb-path PATH` | `docs/knowledge-base` | KB root for ResearchAgent context |
| `--output-dir PATH` | `docs/knowledge-base/research` | Where to write generated research docs |
| `--workers N` | `5` | Max parallel workers |
| `--depth shallow\|deep` | `shallow` | Analysis depth per agent |
| `--no-compress` | off | Skip TokenOptimizer compression before KB write |

Dispatches 6 parallel agents: security, performance, quality, architecture,
documentation, research. Each agent writes a research doc to `--output-dir`.

---

### `kb-search` — Semantic search across the knowledge base

```bash
uv run bob-optimize kb-search "multi-level cache thread safety"
uv run bob-optimize kb-search "graph build" --categories concepts guides
uv run bob-optimize kb-search "coverage floor" --max-results 5 --date-filter 2026-07
```

| Option | Default | Description |
|---|---|---|
| `query` | _(required)_ | Free-text search query |
| `--kb-path PATH` | `docs/knowledge-base` | KB root |
| `--max-results N` | `10` | Maximum results to return |
| `--recency-weight F` | `0.0` | Blend weight for recency tiebreaker (0.0 = off) |
| `--date-filter PREFIX` | — | ISO date prefix filter (e.g. `2026-07`) |
| `--categories CAT…` | all | Restrict search: `concepts` `guides` `references` `research` |

## Related Documents

- [Mnemox CLI Reference](./mnemox-cli-reference.md)
- [Obsidian Integration Guide](../guides/obsidian-integration-guide.md)
- [Token Optimization Concepts](../concepts/token-optimization.md)
- [Multi-Level Caching Architecture](../concepts/multi-level-caching-architecture-patterns.md)
- [Knowledge Graph Layer](../concepts/knowledge-graph-layer.md)
- [Cache API Reference](./cache-api.md)
- [Setup Token Optimization Guide](../guides/setup-token-optimization.md)
