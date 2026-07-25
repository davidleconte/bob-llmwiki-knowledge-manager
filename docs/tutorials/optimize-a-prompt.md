# Tutorial: optimize your first prompt

> ⚠️ **Metrics correction (2026-07-14).** Earlier drafts of this document cited fabricated token-savings/quality figures — "68.96%", "89.3%", "91.80%" — produced by a simulation that never invoked the optimizer. **Those figures are retracted.** The honest, measured figure is **~20% mean optimizer compression** on real prose (manifest-backed: `evaluation/results/validation-2026-07-14/`; see `STATUS.md` and `CHANGELOG.md`). Inline numbers below have been corrected where they appeared.


A hands-on, ~10-minute walk through the Python **token-optimization system** —
from install to optimizing a prompt on the command line and from Python. By the
end you will have counted tokens, compressed a prompt, read the result fields,
and know what the "savings" number does and does not mean.

This is a *learning* tutorial (safe to follow top to bottom). For task recipes
see the [how-to guides](../README.md#how-to-guides); for the full command and API
surface see the [reference](../README.md#reference).

## Prerequisites

- Python **3.11+** (see [`pyproject.toml`](../../pyproject.toml)).
- A clone of this repository, and a virtual environment you can install into.

## Step 1 — Install

From the repository root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,monitoring]"
```

Two equivalent ways to run the CLI:

```bash
python -m src --help      # always works from the repo
bob-optimize --help       # the installed console script (same thing)
```

This tutorial uses `python -m src`.

## Step 2 — Count tokens

Everything the system does is measured in real tokens (via tiktoken). Start by
counting some:

```bash
python -m src count "The quick brown fox jumps over the lazy dog."
```

```
tokens: 10
```

## Step 3 — Optimize a prompt

Now compress a wordy, repetitive prompt:

```bash
python -m src optimize "Please could you kindly explain, in detail,     what   caching is?     Please explain caching."
```

```
original: Please could you kindly explain, in detail,     what   caching is?     Please explain caching.
optimized: Please could you kindly explain, in detail, what caching is? Please explain caching.
original_tokens: 20
optimized_tokens: 17
tokens_saved: 3
savings_percentage: 15.0
quality_score: 1.0
meets_target: False
```

Read the fields:

| Field | Meaning |
|---|---|
| `original_tokens` / `optimized_tokens` | real token counts before and after |
| `tokens_saved` | `original_tokens - optimized_tokens` |
| `savings_percentage` | the compression for *this* prompt |
| `quality_score` | a **lexical heuristic** guardrail (not semantic fidelity) |
| `meets_target` | whether it hit `config.optimizer.target_reduction` (default 0.3) |

The optimizer normalizes whitespace and removes redundancy; it does **not** cap
length here unless you ask it to (Step 5).

## Step 4 — Machine-readable output

Add `--json` for scripting; component logs go to stderr, so stdout stays clean:

```bash
python -m src --json optimize "Please please explain    caching   now now now." 2>/dev/null
```

You get the same fields as a JSON object — pipe it into `jq` or another program.

## Step 5 — From Python

The CLI is a thin front end over the `TokenOptimizer` facade. The same result
from code:

```python
from src import TokenOptimizer

opt = TokenOptimizer.from_config("dev")          # build from config
result = opt.optimize("Please please explain    caching   now now now.")
print(result["original_tokens"], "->", result["optimized_tokens"],
      f"({result['savings_percentage']}%)")

opt.count("just count these tokens")             # -> int
opt.truncate("a very long text ...", max_tokens=8)  # lossy budget-fit
```

`from_config` reads the typed configuration (cache sizes, the optimizer's
`target_reduction` / `max_tokens`, monitoring) and composes the components for
you. See the [architecture doc](../architecture/ARCHITECTURE.md) for how that
wiring works.

## Step 6 — What "savings" means here

Per-prompt `savings_percentage` varies with how compressible the input is. The
project's **headline** figure is measured honestly, not asserted:

- Optimizer compression averages **~20% on real in-repo prose** (95% CI ≈
  [18.9%, 21.2%], N=183), manifest-backed at
  [`evaluation/results/validation-2026-07-14/`](../../evaluation/results/validation-2026-07-14/).
- Caching and truncation save tokens too, but they are reported **separately**:
  cache savings depend on your workload's repeat rate, and truncation is lossy.
  They are never blended into one number.

You can reproduce the measurement yourself:

```bash
python -m src.validation --corpus repo
```

## Where to go next

- **How-to** — [set up token optimization](../knowledge-base/guides/setup-token-optimization.md), [track costs](../knowledge-base/guides/cost-tracking-guide.md), [monitoring](../MONITORING.md).
- **Reference** — the [API reference](../api/README.md) and the [CLI](../../src/cli.py) subcommands (`optimize`, `truncate`, `count`, `cache-stats`, `cost-report`, `metrics`, `health`, `config`).
- **Explanation** — [how token optimization works](../knowledge-base/concepts/token-optimization.md) and the [architecture](../architecture/ARCHITECTURE.md).
