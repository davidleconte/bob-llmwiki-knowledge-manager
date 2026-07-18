# Field 2 — Technical Statement
*Paste this text directly into the submission form. Remove this line first.*

---

**Mnemox** — built by **Team BobjectifLune** — is implemented as **two native IBM Bob modes** — no plugins, no MCP servers, no external dependencies — using Bob's own YAML mode configuration and skill system. Deploying to any project workspace requires a single command — `scripts/init-project.sh` — which scaffolds the KB directory structure and registers the mode in Bob IDE in under 30 seconds. After that one-time step, activation is permanent: mode picker → 🧠 Mnemox Knowledge Builder.

## Design pattern

An implementation of Andrej Karpathy's **LLM-Wiki** three-layer pattern, made native to IBM Bob:

1. **Knowledge layer** — version-controlled Markdown under `docs/knowledge-base/` (concepts, guides, references, research), cross-referenced and indexed.
2. **Retrieval layer** — `INDEX.md` (auto-loaded via `.bob/settings.json`) + `save_memory` facts; a session *retrieves* prior knowledge instead of re-reading source.
3. **Schema layer** — the Bob **mode definition** + `AGENTS.md`: stable rules that make Bob both disciplined *and* cacheable (a fixed prefix hits the cache instead of missing it).

> **Why not RAG?** RAG retrieves passages from a snapshot corpus — it does not accumulate the *reasoning* Bob already did. As Karpathy puts it: *"the LLM is rediscovering knowledge from scratch on every question. There's no accumulation."* Mnemox is the accumulator: knowledge is written once and retrieved as a structured, cross-referenced finding — not re-derived from raw chunks on every query. No infrastructure required beyond Git.

## How Bob is used (native, no external moving parts)

- **Two custom Bob modes** — `knowledge-manager` and `repo-analyzer`.
  - Bob Shell CLI: `config/custom_modes.yaml` → installed to `~/.bob/custom_modes.yaml` via `scripts/install.sh`.
  - Bob IDE: `.bob/custom_modes.yaml` (workspace-level) — **zero install**, selected from the mode picker; the skill (`.bob/skills/knowledge-manager/SKILL.md`) auto-loads.
- **IBM Bob skills wired in** for real IBM workflows: `ibm-watsonx.ai`, `ibm-watsonx-data`, `ibm-docling` / `docling-serve`, `carbon-mcp`, `techzone`, `draw-io`, plus Bob **rules** for AI/RAG hygiene, agent safety, containers, and secrets.
- **`repo-analyzer`** runs 7 Bash scripts (`scripts/run-full-analysis.sh`) that produce dated snapshots — scan, dependencies, metrics, security, test coverage, git history, docs coverage — that Bob consumes as digests rather than raw source.

## Why it structurally saves Bobcoins

Each IBM token-economy principle has a concrete home in how the modes behave:

| Waste | How the design removes it |
|---|---|
| **Catalog tax** (MCP re-sends its tool catalog every turn) | Native Bob mode — no plugin, no MCP |
| **Payload tax** (2,000-line file for 20 relevant lines) | Scripts summarise; the KB stores digests you *cite* |
| **Compression trap** (stripping meaning raises effective cost) | Templates preserve rationale, real names, cross-refs |
| **Short-thread tax** (turn 15 re-pays 14 turns of history) | Knowledge persists in KB + `save_memory`; a fresh thread retrieves |
| **Cache misses** (reworded prefixes) | Fixed mode + `AGENTS.md` + stable KB layout = a cacheable prefix |
| **Verbose output** | Bounded artifacts — templates, `INDEX.md`, reports — not essays |

## Optional Python Token Optimization System (`src/`, Python 3.11+)

For teams that want to push cost further, an *independently-operable* library, exposed via a `TokenOptimizer` facade and a `bob-optimize` CLI (`python -m src`):

- **L1 cache** — exact-match, O(1); **L2 cache** — semantic-similarity (cosine).
- **Optimizer** — high-fidelity compression (whitespace + redundant-phrase removal); measured quality score ≈ 0.80 on the validation corpus, i.e. meaning largely preserved (not a lossless guarantee).
- **Knowledge-graph layer** (`src/graph/`) — pure-Python property graph with PageRank re-ranking. We built it, measured it, and found retrieval uplift was neutral — so we disabled the score-blending component (`graph_weight = 0.0`) and repurposed the graph for what the data said it was good for: KB structural health analysis (orphan detection, hub identification, broken-link mapping). That is the engineering decision; we report it rather than omit it.
- Three **opt-in, fallback-safe** integration points bridge the two systems; if Python is absent, the Bash KB Manager is unaffected.

## Engineering quality (a differentiator, not a footnote)

- **CI gates**: code-coverage floor (≥80%), per-package floors, `ruff` lint/format, `mypy`, a 3.11/3.12 matrix, an SBOM, `bandit` security scan, a `src→scripts` layering gate, and benchmark-regression trending.
- **Security-by-design**: a STRIDE `THREAT_MODEL.md`, a path-traversal fix guarded by regression tests.
- **Provenance discipline**: every published savings number must cite a reproducible run with a manifest (data hash, code SHA, config, seed, library versions, `git_dirty`). Numbers without provenance are not published — and earlier fabricated numbers were formally **retracted** (see the Impact statement).

## What is deliberately *not* claimed

Enterprise SLAs, production support, guaranteed savings percentages, or Windows compatibility. Two labels apply to different things: **Beta — Not Production Ready** refers to the Python Token Optimization System's API stability (not safe to depend on in production pipelines); **A+** is an internal engineering-quality grade against defined rubric gates (coverage floors, lint, type-safety, CI matrix) — it measures code discipline, not production-readiness. They are independent assessments of independent things. The Bash KB Manager carries no Beta qualifier — it is stable v1.0 and requires nothing beyond Bob.
