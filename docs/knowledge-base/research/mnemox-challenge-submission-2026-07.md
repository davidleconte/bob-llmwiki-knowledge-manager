---
title: "Mnemox — 2026 IBMer watsonx Challenge Submission"
category: research
tags: [challenge-submission, watsonx-challenge, ibmer, team-bobjectiflune, executive-summary]
created: 2026-07-18
updated: 2026-07-18
status: active
audience: [challenge-judges, ibm-leadership, watsonx-program-team]
related:
  - ./mnemox-executive-brief-2026-07.md
  - ./mnemox-positioning-brief-2026-07.md
  - ./business-case-2026-07.md
  - ./full-technical-design-retro-2026-07.md
  - ../../../README.md
---

> **HISTORICAL SNAPSHOT (2026-07).** Point-in-time research/analysis retained for the audit trail. Figures below reflect what was measured or projected at the time of writing; the canonical current numbers live in `STATUS.md` and the validation manifest (`evaluation/results/validation-2026-07-14/manifest.json`).


# Mnemox — 2026 IBMer watsonx Challenge Submission

> **Team:** BobjectifLune
> **Challenge:** 2026 IBMer watsonx Challenge
> **Submission type:** Native IBM Bob implementation
> **Platforms:** Bob IDE · Bob Shell CLI
> **License:** MIT

---

## The one-line pitch

**Mnemox gives IBM Bob a persistent memory** — so every team's Bobcoin budget goes to
new work, not repeating work the team already paid for.

---

## The problem we solved

IBM Bob is stateless. Every session starts from zero. Whatever Bob learned about your
architecture, your design decisions, your codebase patterns — it is gone when the
thread ends. The next session re-reads the same files, re-infers the same relationships,
and re-derives the same answers. **Your team pays the full Bobcoin cost every time.**

This is not a failure of Bob. It is the default behaviour of any stateless LLM. But
it has a compounding cost most teams do not see:

```
Session 1:  "Explain our microservices boundary decisions"  →  800 Bobcoins
Session 2:  "Remind me — how are our services bounded?"     →  800 Bobcoins
Session 3:  "What was the rationale for our API gateway?"   →  800 Bobcoins
...
Session N:  Same questions. Same cost. Same Bob, starting from scratch.
```

The question teams eventually can no longer ask is not *"can Bob do this?"* —
it is *"can we afford to let Bob try?"*

**Mnemox removes that ceiling.** It makes Bob an accumulator: knowledge earned in
Session 1 is retrieved, not re-derived, in Session 100.

---

## What we built

Two independently deployable products in one repository, connected by three shared
infrastructure layers. Both work in **Bob IDE** and **Bob Shell CLI** — same modes,
same KB, same compounding benefit.

### Product 1 — KB Manager (the core pattern)

A native IBM Bob mode (`knowledge-manager`) that implements Andrej Karpathy's
**LLM-Wiki pattern** natively inside Bob.

**What it does:**
- Bob analyses your repository once and files the findings into a structured,
  Git-backed knowledge base (`docs/knowledge-base/`)
- Every future session reads the KB instead of re-reading the source
- Knowledge is shared across the whole team — every member starts every session
  from the team's full accumulated expertise, not from their own prior sessions
- The one-word entry point: type `mnemox`. Bob does the right thing automatically

**The pattern (Karpathy):**
> *"The wiki is a persistent, compounding artifact. The cross-references are
> already there. The contradictions have already been flagged."* — as opposed
> to RAG, where *"the LLM is rediscovering knowledge from scratch on every
> question. There's no accumulation."*

Mnemox is the accumulator. The KB becomes the team's institutional memory —
surviving team turnover, onboarding new members as retrieval not re-derivation,
and growing more valuable with every session.

**Technology:** Bash scripts + YAML + Markdown. ~500 lines. Zero external
dependencies. No plugin, no MCP server, no infrastructure.

### Product 2 — Token Optimizer (the engineering layer)

A Python library and CLI (`bob-optimize`) that reduces the token cost of every
prompt before it is sent — independently of whether a KB exists.

**What it does:**
- Removes whitespace, redundant phrases, and verbal hedges from prompts
  automatically, without changing meaning (~20% mean reduction)
- Caches results so repeated or similar prompts return instantly at zero
  token cost
- Operates as a transparent layer: same request, fewer Bobcoins, same answer

**Measured:** ~20% mean token reduction (95% CI [18.9%, 21.2%], N=183 real
documents, tiktoken BPE, null test passed, manifest-backed at
`evaluation/results/validation-2026-07-14/`).

**Technology:** Python 3.11+, ~3,500 lines, 1,124+ tests, self-assessed A+ engineering grade (D− → A+ across 8 remediation phases; independent counter-audit commissioned July 2026).

### Three shared infrastructure layers

| Layer | What it adds | Key result |
|---|---|---|
| **Semantic embedding index** | MiniLM dense-vector KB search instead of keyword matching | A/B-measured p@3 uplift: 44% → 88% (validated configuration; production retrieval wiring in progress) |
| **Knowledge graph** | Surfaces orphaned documents, dead cross-references, authority hubs | 26/39 orphan documents rescued; 19 broken links found |
| **Parallel analysis pipeline** | 6 agents analyse a repository simultaneously, compress output, file into KB | Full repo analysis in one command: `bob-optimize analyze` |

---

## Why this matters for the IBM Bob ecosystem

Mnemox is not a standalone tool. It is the **persistent memory layer that runs
underneath the entire IBM Bob ecosystem**.

Every mode, skill, rule, and MCP server in the Bob Marketplace generates knowledge
worth keeping — architecture insights, security findings, integration patterns,
experiment results. Without Mnemox, that knowledge evaporates at session end.
With Mnemox, it compounds.

**The strategic multiplier:** the more capable a team's Bob setup, the more Mnemox
returns. A team using `ibm-watsonx-data`, `ibm-docling`, `watsonx-orchestrate`, and
`carbon-mcp` together generates richer findings per session. Mnemox captures every
one of them, permanently, for every team member.

---

## The IBM Bob principles this submission addresses

| IBM Bob principle | How Mnemox addresses it |
|---|---|
| **Catalog tax** | Native Bob mode — no MCP server, no plugin. Zero per-turn catalog overhead. |
| **Payload tax** | `repo-analyzer` runs scripts that summarise; the KB stores digested reports cited by reference, not raw source injected in full |
| **Compression trap** | Templates preserve meaning — rationale, real names, cross-references — while reducing token volume |
| **Short threads** | Knowledge persists in Git-backed KB files across any number of threads and sessions. A fresh thread always retrieves from the KB |
| **Cache coherence** | Fixed mode definition + `AGENTS.md` + KB layout = a cacheable prefix that repeats across every session |
| **Bobcoin economy** | Re-derivation saving: 51% on well-formed KB summaries (N=10, breakeven in 1 session). Compression: ~20% on every novel prompt. |

---

## Measured results

All figures are manifest-backed and independently reproducible. No blended totals.

| Mechanism | Figure | Measured on | Condition |
|---|---|---|---|
| Re-derivation elimination | **51% saving** per query (95% CI [38%, 64%]) | 10 well-formed KB summary pairs from this repo | Prior answer captured in KB; compact-summary document |
| Prompt compression | **~20% mean** token reduction (95% CI [18.9%, 21.2%]) | N=183 real Markdown documents, tiktoken BPE | Every novel prompt; structured Markdown prose |
| Retrieval precision uplift | **44% → 88%** correct in top 3 results | 80-doc KB, 25-query golden set | A/B-measured; production retrieval wiring in progress |
| ROI breakeven | **1 session** for well-formed KB pair | 0.80 BC creation cost, 2.22 BC mean saving | Single recurring query on a compact-summary document |
| Return at 40 queries | **~80×** on well-formed pair | ROI model; amortised creation + maintenance | Stable document, recurring query type |

**Combined scenario** (stable codebase, 6-month horizon, both systems active):
conservative estimate **40–60% Bobcoin reduction**; optimistic (ideal conditions)
**60–75%**. These are not additive — they are scenario projections with explicit
applicability conditions.

---

## Engineering quality

This submission is engineered to institutional standard:

| Gate | Result |
|---|---|
| Tests | **1,124+ passing / 1 pre-existing failure** (research template missing `## Methodology` section — unrelated to KB Manager) |
| Code coverage | **89.82% global** (≥80% gate enforced by CI); all 5 per-package floors met |
| Static analysis | **ruff + mypy clean** (Python 3.11 + 3.12 matrix) |
| Concurrency | **14 race conditions fixed** across 5 adversarial audit rounds; all state protected by `RLock` |
| Savings integrity | **Manifest-backed** — `check_savings_claims.py` CI gate rejects any published % without a manifest file |
| Architecture decisions | **19 ADRs** on record; all decisions traceable |
| Security | STRIDE threat model; bandit SAST; CycloneDX SBOM; `pip-audit` (0 CVEs) |
| Grade | **D− (0.9) → self-assessed A+** across 8 remediation phases; independent counter-audit commissioned July 2026 (see `docs/knowledge-base/research/counter-audit-2026-07-19-independent.md`) |

**Trajectory:** D− (0.9) → self-assessed A+ across 8 adversarial remediation phases. An independent counter-audit (July 2026) confirmed the honesty machinery and retraction discipline while identifying specific retrieval-wiring and KB-integrity items. Remediation is in progress.

---

## Honest maturity statement

**Status: Beta — Not Production Ready.**

This reflects measurement scope, not implementation quality:
- Token Optimizer validated on repo Markdown prose only; savings on other content
  types (raw code, JSON, conversational text) are not yet benchmarked
- No enterprise SLAs, no Windows support, no on-call rotation
- The KB Manager → Token Optimizer integration bridge requires TOS to reach v1.0
  stability (currently blocked; see G-6 in the Technical Design)

The core pattern works. The engineering is production-grade. The honest gap is
external corpus validation and the v1.0 stability milestone.

---

## What judges can evaluate today

| What to evaluate | How |
|---|---|
| **Core KB pattern** | `bob --chat-mode=knowledge-manager` (Bob Shell CLI) or mode picker (Bob IDE) → type `mnemox` |
| **Token optimizer** | `pip install -e ".[dev]"` → `bob-optimize optimize --text "your prompt"` |
| **Measured savings** | `python -m src.validation` → reproduces the manifest-backed 20% figure |
| **KB retrieval quality** | `bob-optimize kb-search "your query"` → shows P@k results |
| **Knowledge graph health** | `bob-optimize graph-health` → orphan count, hub list, broken links |
| **Parallel repo analysis** | `bob-optimize analyze` → 6 agents, compressed output, KB documents filed |
| **Full test suite** | `uv run pytest tests/ --ignore=tests/load --ignore=tests/performance` → 1,124+ passing, 1 pre-existing failure |
| **Engineering grade** | [`counter-audit-2026-07-19-independent.md`](./counter-audit-2026-07-19-independent.md) — independent assessment on file |

---

## The team

**Team BobjectifLune** — 2026 IBMer watsonx Challenge.

> **Why BobjectifLune?** From *"Objectif Lune"* — the French title of Verne's
> *From the Earth to the Moon*. Before you can reach the moon, you need to
> stop wasting fuel re-discovering where it is. Mnemox is the navigation layer
> that makes the ambitious affordable.

---

## Key documents

| Document | Audience | What it contains |
|---|---|---|
| **[This document](./mnemox-challenge-submission-2026-07.md)** | Challenge judges | Full submission narrative |
| [Executive Brief](./mnemox-executive-brief-2026-07.md) | CTO / VP Engineering / judges | 4-minute ROI and decision summary |
| [Business Case](./business-case-2026-07.md) | Business Owner / CTO / EA | Full investment, ROI, pilot design, risks |
| [Technical Design](./full-technical-design-retro-2026-07.md) | Engineers / technical judges | Architecture, components, SLA, gaps |
| [Competitive Positioning](./mnemox-positioning-brief-2026-07.md) | Enterprise Architect / CTO | Mnemox vs. RAG / vector DB / LangChain |
| [README](../../../README.md) | All | Project overview, getting started, comparisons |
| [STATUS.md](../../../STATUS.md) | All | Canonical maturity — single source of truth |

---

*Created: 2026-07-18*
*Audience: Challenge Judges · IBM Leadership · watsonx Program Team*
*Category: Research*
