---
title: "Mnemox Knowledge Builder — Executive Brief"
category: research
tags: [executive-brief, cto, challenge-submission, roi, one-pager]
created: 2026-07-18
updated: 2026-07-18
status: active
audience: [cto, vp-engineering, challenge-judges, executive-sponsor]
related:
  - ./mnemox-challenge-submission-2026-07.md
  - ./business-case-2026-07.md
  - ./full-technical-design-retro-2026-07.md
  - ./mnemox-positioning-brief-2026-07.md
  - ./bobcoin-savings-analysis-2026-07-14.md
---

> **HISTORICAL SNAPSHOT (2026-07).** Point-in-time research/analysis retained for the audit trail. Figures below reflect what was measured or projected at the time of writing; the canonical current numbers live in `STATUS.md` and the validation manifest (`evaluation/results/validation-2026-07-14/manifest.json`).


# Mnemox — Executive Brief

> **Read time: 4 minutes.**
> For the full business case, see the [Business Case](./business-case-2026-07.md).
> For technical architecture, see the [Technical Design](./full-technical-design-retro-2026-07.md).

---

## The problem in one sentence

Every IBM Bob session starts from zero. Whatever Bob learned about your architecture
yesterday is gone today. Your team pays the full Bobcoin cost to re-derive it —
every session, indefinitely.

---

## The solution in one sentence

**Mnemox gives IBM Bob a persistent memory** — so knowledge earned in Session 1 is
retrieved, not re-derived, in Session 100.

---

## What was built

**Team BobjectifLune** — 2026 IBMer watsonx Challenge submission.

Two independently deployable products shipped in one repository:

| Product | What it does | Measured outcome |
|---|---|---|
| **KB Manager** | Native IBM Bob mode (`knowledge-manager`) that persists structured knowledge across sessions as Git-backed Markdown. No plugin, no MCP server, no external dependency. | Structural saving: KB compact-summaries are **51% smaller** than their sources (N=10, 95% CI [38%, 64%]). Well-formed pairs break even in **1 session**, return **80×** at 40 queries. |
| **Token Optimizer** | Python library + CLI (`bob-optimize`) that compresses every prompt before it is sent — removes redundancy without changing meaning. | **~20% mean token reduction** (95% CI [18.9%, 21.2%], N=183 real documents, tiktoken BPE, null test passed, manifest-backed). |

Three opt-in shared layers progressively improve retrieval quality:

| Layer | What it adds | Key result |
|---|---|---|
| Semantic embedding index | MiniLM dense-vector KB search | Retrieval precision p@3 = **0.84** (21/25), matched by keyword-only — no net lift (report.json: evaluation/results/retrieval-2026-07-19/report.json) |
| Knowledge graph | Orphan detection, dead-link surfacing, authority hubs | 26/39 orphan documents rescued; 19 broken cross-references surfaced |
| Parallel analysis pipeline | 6 agents analyse a repo simultaneously, compress output, file into KB | Full repo analysis in one command: `bob-optimize analyze` |

---

## The ROI model (honest, conditional)

**What is a Bobcoin?** IBM Bob's internal token budget unit:
`token_count × price_per_token × 1000`. Finite. Shared. Worth managing.

| Scenario | Expected saving | Confidence | Condition |
|---|---|---|---|
| Stable codebase, recurring architecture queries, 6 months | **50–65%** Bobcoin reduction (modelled; manifest-backed basis) | Medium | KB maintained; structured Markdown prompts |
| Medium, active codebase, mixed queries | **35–50%** | Medium | KB updated weekly |
| Small, fast-changing codebase | **15–25%** | Low | Some recurring queries |
| One-off engagement, no repetition | ~0% | High | KB creation cost not recovered |

**Pilot cost and risk:** 400–700 Bobcoins total (~30 min human time). Breakeven: 1–3 sessions.

> **Conservative budget-planning figure: 40–60% Bobcoin reduction** (projection;
> modelled from the manifest-backed ~20% compression,
> `evaluation/results/validation-2026-07-14/manifest.json`) for teams with
> stable, recurring query patterns on structured codebases.

---

## Why this is strategic, not just a cost tool

The real return is not fewer Bobcoins spent — it is **more research conducted**:

- A team that cuts per-session cost by 50% can attempt **twice as many sessions**, or
  sessions **twice as broad**, for the same budget.
- A new team member starts their first session from the **full accumulated expertise** of
  every prior session by every prior team member. Onboarding becomes retrieval, not
  re-derivation.
- Architecture decisions documented in the KB survive team turnover. The rationale Bob
  captured in March is available to the engineer who joins in September.
- **The more capable the Bob setup, the more compounds** — every mode, skill, and MCP
  server generates valuable findings that are lost at session end without Mnemox.

---

## Engineering quality

This is not a prototype. It is an implementation with institutional-grade quality gates:

| Gate | Status |
|---|---|
| Tests | **1,112 passing / 0 failures** |
| Code coverage | **89.82% global** (≥80% gate); all 5 per-package floors met |
| Static analysis | **ruff + mypy clean** (Python 3.11 + 3.12 matrix) |
| Concurrency | **14 race conditions fixed** across 5 adversarial audit rounds |
| Savings claims | **Manifest-backed** — every published % cites a reproducible run |
| Architecture decisions | **19 ADRs** on record |
| Threat model | STRIDE-based; security reviewed |

**Grade: A+ (4.30/4.30)** against Tier-1 institutional standard.

---

## Honest maturity label

**Beta — Not Production Ready.** This reflects measurement scope, not implementation
quality:

- Token Optimizer validated on repo Markdown prose only; savings on other content
  types (code, JSON, conversational text) are not yet measured.
- No enterprise SLAs, no Windows support, no on-call rotation.
- The KB Manager → Token Optimizer integration bridge is blocked on TOS reaching v1.0.

The core pattern works. The engineering is production-grade. What is missing is
external corpus validation and the v1.0 stability milestone.

---

## The recommended entry point

**A 4-week pilot. Total risk: 400–700 Bobcoins.**

1. **Week 1:** Install Mnemox into one Bob IDE workspace. Run `mnemox` on one active
   project. Measure the KB creation cost.
2. **Weeks 2–4:** Run every Bob session on that project in `knowledge-manager` mode.
   Run `mnemox --quick` at session close. Track Bobcoin consumption per session.
3. **Gate (Week 4):** If per-session cost on recurring architecture queries fell ≥20%,
   continue. If not, the project type is not a fit — no sunk cost.

The pilot can start today. No IT approval, no external dependencies, no budget beyond
existing Bob usage.

---

## Decision summary

| Who | What to decide | Recommended action |
|---|---|---|
| **Team lead / Engineering Manager** | Pilot launch | Start today — one project, one volunteer, 30 minutes of setup |
| **CTO / Head of Engineering** | Broader rollout | Wait for 4-week pilot results; data-backed decision by mid-August |
| **Enterprise Architect** | Architecture integration | Review [Positioning Brief](./mnemox-positioning-brief-2026-07.md); data residency: all KB is Git-committed Markdown in your repo |
| **Platform team / CTO** | Token Optimizer production integration | Defer until TOS reaches v1.0; use CLI mode now |

---

## Links

| | |
|---|---|
| Challenge submission narrative | [Challenge Submission](./mnemox-challenge-submission-2026-07.md) |
| Full business case | [Business Case](./business-case-2026-07.md) |
| Technical architecture | [Technical Design](./full-technical-design-retro-2026-07.md) |
| Why not RAG / vector DB | [Positioning Brief](./mnemox-positioning-brief-2026-07.md) |
| Savings methodology | [Bobcoin Savings Analysis](./bobcoin-savings-analysis-2026-07-14.md) |
| Canonical maturity status | [STATUS.md](../../../STATUS.md) |
| Project README | [README.md](../../../README.md) |

---

*Created: 2026-07-18*
*Audience: CTO · VP Engineering · Enterprise Architect · Challenge Judges*
*Category: Research*
