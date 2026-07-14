# `src/validation` — real, manifest-backed validation (Phase 5)

This package replaces the retracted, fabricated validator (which constructed a
`PromptOptimizer` but **never invoked it**) with a harness that measures the
**real** product through the Phase-4 `TokenOptimizer` facade and writes a
reproducibility manifest for every run.

## Run it

```bash
python -m src.validation                 # committed repo-prose corpus, writes a dated report
python -m src.validation --help          # all flags
python -m src.validation --json          # full machine-readable report to stdout
```

Output lands in `evaluation/results/validation-<date>/` as `report.json`
(machine) + `manifest.json` (provenance). The process exits non-zero if the
honest gates fail — see below. `python evaluation/scripts/run_token_validation.py`
is a thin shim over this and behaves identically.

## What it measures — three mechanisms, kept separate

Blending these into one headline is exactly how the retracted "68.96%" was
manufactured, so they are reported separately and labelled:

| Mechanism | What it is | Role |
|---|---|---|
| **Optimizer compression** | near-lossless whitespace + redundant-phrase removal, cap disabled so lossy truncation can't leak in | **the only "savings" headline** (mean ± bootstrap CI, N) |
| **Cache recompute-avoidance** | a hit avoids the full recompute — a property of the *workload's* repeat rate, not the system | reported separately, repeat rate disclosed |
| **Truncation** | *lossy* budget-fit: deletes content to hit a token budget, no fidelity gate | reported separately, **excluded** from savings |

## Honest gates (what CI enforces)

The exit code encodes three checks — none of them a savings *magnitude* (gating a
measurement would re-incentivise fabrication):

1. **Null test** — the optimizer over a shuffled/high-entropy corpus must show
   near-zero savings (`< NULL_MAX_SAVINGS_PCT`). Material savings on incompressible
   input would mean the measurement is an artefact.
2. **Manifest complete** — `code_sha`, `git_dirty`, `data_hash`, `config`, `seed`,
   `library_versions`, `tiktoken_active`, … all present.
3. **tiktoken active** — token counts are real, not the `chars/4` approximation.

The companion guard `scripts/check_savings_claims.py` (in the CI `lint` job) fails
if any live doc publishes a savings/cost/hit-rate percentage without citing a
manifest — enforcing the `STATUS.md` publishing rule going forward.

## Corpus tiers

Two tiers are selectable with `--corpus`:

- `repo` **(default, committed, CI-runnable)** — real technical markdown from
  `examples/*/docs/knowledge-base/**` and the repo's own `docs/**`. Synthetic /
  Lorem-ipsum data under `evaluation/data/**` and the repeated-word test fixtures
  are deliberately excluded — measuring there inflates optimizer savings and is
  the very artefact this phase undoes.
- `sessions` — the optional **higher-credibility** tier: real prompts captured
  from live sessions. `both` unions the two.

### Capturing live sessions for the `sessions` tier

The `repo`/`docs` corpus is real prose but is *documents used as prompts*. For
the strongest credibility, measure on **real captured prompts**:

```bash
# Collect real Bob Shell sessions into evaluation/data/sessions/
scripts/run_baseline_measurement.sh      # human-in-the-loop capture
scripts/run_optimized_measurement.sh

# Then validate against them (writes its own manifest-backed report)
python -m src.validation --corpus sessions --sessions-dir evaluation/data/sessions
```

`load_session_transcripts` reads `.json`/`.md`/`.txt` transcripts tolerantly
(pulling `prompt`/`query`/`content`/… out of JSON records) and **skips**
`test_*` files, which are the random mock records the analysis tools generate.
If the directory is absent the tier yields an empty corpus and the harness
refuses to publish a number (rather than inventing one).

## Reproducing a published number

Each `manifest.json` pins the exact corpus (`data_hash`), code (`code_sha` +
`git_dirty`), config, seed, and library versions. To reproduce: check out the
recorded SHA, install the pinned deps, and re-run with the same `--seed` and
`--corpus`; the `data_hash` will match if the corpus is unchanged.
