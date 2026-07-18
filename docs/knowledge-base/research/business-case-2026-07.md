---
title: "Mnemox Knowledge Builder — Business Case"
category: research
tags: [business-case, roi, strategy, cto, enterprise-architect, business-owner]
created: 2026-07-18
updated: 2026-07-18
status: active
audience: [business-owner, cto, enterprise-architect]
related:
  - ./mnemox-challenge-submission-2026-07.md
  - ./mnemox-executive-brief-2026-07.md
  - ./mnemox-positioning-brief-2026-07.md
  - ./full-technical-design-retro-2026-07.md
  - ./bobcoin-savings-analysis-2026-07-14.md
  - ../guides/km-bobcoin-savings-measurement-guide.md
  - ../guides/kb-tos-integration-roadmap.md
---

# Mnemox Knowledge Builder — Business Case

> **Who this document is for:** Business Owners, CTOs, and Enterprise Architects
> evaluating whether to adopt Mnemox for their IBM Bob-enabled teams.
>
> **What it answers:** Should we adopt this? What does it cost? What do we get
> back? How does it fit our architecture? What are the risks?
>
> **What it is not:** A technical design document. For component specifications,
> SLA figures, and implementation details, see the
> [Technical Design](./full-technical-design-retro-2026-07.md).
>
> **5-minute version:** See the [Executive Brief](./mnemox-executive-brief-2026-07.md)
> for a one-page decision-quality summary.

---

## How to Read This Document

```
§1  THE PROBLEM      — What is re-derivation costing your team today?
§2  THE PROPOSITION  — What Mnemox does about it, in plain language
§3  THE INVESTMENT   — What adoption costs (time, people, Bobcoins)
§4  THE RETURN       — Measured and structural savings, honestly scoped
§5  THE STRATEGY     — The compounding thesis and the long-term bet
§6  THE FIT          — How it integrates with your IBM architecture
§7  THE RISKS        — Honest maturity, known limits, mitigations
§8  THE DECISION     — What to decide, by whom, by when
```

---

## §1 — The Problem: Your Team Is Paying Twice for Everything It Already Knows

Every IBM Bob session starts from zero. Whatever Bob learned in the last
session — about your architecture, your design decisions, your codebase
patterns — is gone when the thread ends. The next session re-reads the
same files, re-infers the same relationships, and re-derives the same
answers. **Your team pays the full Bobcoin cost every time.**

This is not a failure of Bob. It is the default behaviour of any stateless
LLM system. But it has a compounding cost that most teams do not see:

```
Session 1:  Bob reads your architecture docs         →  800 Bobcoins
Session 2:  Bob reads your architecture docs again   →  800 Bobcoins
Session 3:  Bob reads your architecture docs again   →  800 Bobcoins
            ...
Session N:  Bob reads your architecture docs again   →  800 Bobcoins
```

The invisible cost is not the single session — it is the pattern across
all sessions. A team running 10 architecture-related Bob sessions per week
on a project that Bob could have learned once is spending **10× the minimum
necessary cost** on re-derivation alone.

> **What is a Bobcoin?** IBM Bob runs on a token-based budget called **Bobcoins** —
> the internal unit that measures how much AI computation each session consumes.
> Every question asked, every file Bob reads, every answer it generates costs Bobcoins.
> Mnemox reduces that cost structurally so the freed budget goes to depth, not repetition.

### The four cost drivers

| Cost Driver | What happens | Business impact |
|---|---|---|
| **Re-derivation** | Bob re-reads the same source files in every session | Direct Bobcoin waste — paying for work already done |
| **Prompt inflation** | Every prompt carries redundant context, filler, and noise | 20–30% of every Bobcoin budget goes to words that carry no information |
| **Context pollution** | Retrieval returns tangentially related documents | Bob spends reasoning tokens on content it doesn't need |
| **Context dislocation** | Retrieved chunks arrive in the wrong order | Bob re-reconstructs narrative coherence it could have retrieved intact |

### The question that becomes unanswerable

The consequence of this pattern is not just wasted budget. It is a ceiling
on ambition. When every session starts from zero, the Bobcoin cost of
attempting a broad, multi-session agentic research scope is prohibitive.
Teams stop asking "can Bob do this?" and start asking "can we afford to
let Bob try?" **That ceiling is what Mnemox removes.**

> **Why not just use a vector database (RAG)?** This is the right question to ask.
> See [§6 — The Fit](#§6----the-fit-integration-with-your-ibm-architecture) and the
> [Positioning Brief](./mnemox-positioning-brief-2026-07.md) for the direct comparison.
> The short answer: RAG retrieves from a snapshot; Mnemox accumulates and compounds.
> Karpathy's framing: *"the LLM is rediscovering knowledge from scratch on every
> question [in RAG]. There's no accumulation."* Mnemox is the accumulator.

---

## §2 — The Proposition: What Mnemox Does

Mnemox implements Andrej Karpathy's *LLM-Wiki* pattern natively inside
IBM Bob. In Karpathy's words, the alternative to re-derivation is
*"a persistent, compounding artifact — the cross-references are already
there, the contradictions have already been flagged"* — as opposed to RAG,
where *"the LLM is rediscovering knowledge from scratch on every question.
There's no accumulation."*

Mnemox makes Bob an accumulator. It does this through **two independently
deployable systems** and three shared infrastructure layers:

### System 1 — KB Manager: Eliminate re-derivation

**What it is:** A native IBM Bob mode (`knowledge-manager`) that persists
structured knowledge across sessions as Git-backed Markdown. No plugin,
no MCP server, no external dependency.

**What it does in plain language:**
- Bob analyses your repository once, files the findings into a structured
  knowledge base (`docs/knowledge-base/`), and commits it to Git.
- Every future session reads the KB instead of re-reading the source. A
  question Bob has answered before costs near-zero to answer again.
- Knowledge is shared across the whole team — every team member starts
  every session from the full accumulated expertise, not from their own
  prior sessions only.

**The one-word entry point:** Type `mnemox` in any KB session. Bob does
the right thing automatically — scaffolds the KB on first use, refreshes
it on subsequent runs.

### System 2 — Token Optimizer: Compress every prompt

**What it is:** A Python library and CLI (`bob-optimize`) that reduces the
token cost of every prompt before it is sent, regardless of whether a KB
exists.

**What it does in plain language:**
- Removes whitespace, redundant phrases, verbal hedges, and structural
  noise from prompts — automatically, without changing the meaning.
- Caches results so that repeated or similar prompts return instantly at
  zero token cost.
- Operates as a transparent layer: the same request costs fewer Bobcoins,
  the same answer comes back.

**Measured:** ~20% mean token reduction on structured prose (95% CI
[18.9%, 21.2%], N=183 real documents, reproducible manifest at
`evaluation/results/validation-2026-07-14/`).

### The three shared layers (infrastructure)

Three opt-in infrastructure layers connect the two systems and
progressively improve retrieval quality as they are activated:

| Layer | What it adds | How it is activated |
|---|---|---|
| **Semantic embedding index** | KB search uses MiniLM dense vectors instead of keyword matching. Retrieval precision: 44% → 88% correct in top 3 results. | `bob-optimize index-kb` |
| **Knowledge graph** | Surfaces orphaned documents, dead cross-references, and authority hubs. Turns a flat file collection into a navigable graph. | `bob-optimize graph-build` |
| **Parallel analysis pipeline** | Runs 6 analysis agents simultaneously on your repository, compresses their output, and files the findings into the KB in a single command. | `bob-optimize analyze` |

Each layer is **fallback-safe** — if it is absent, the system works without
it. KB retrieval degrades gracefully from graph + semantic to keyword-only.

---

## §3 — The Investment: What Adoption Costs

Honest cost accounting matters. The savings figures in §4 are only
meaningful against a realistic cost baseline.

### One-time setup cost

| Task | Who | Time | Bobcoin cost |
|---|---|---|---|
| Install Mnemox into a Bob IDE workspace | Any team member | 5 minutes | ~0 (no Bob calls required) |
| Run first `mnemox` analysis on a repository | Bob session | 10–20 minutes | 200–500 BC (depends on repo size) |
| Install optional Python optimizer (`bob-optimize`) | Engineer | 10 minutes | ~0 |
| Build initial embedding index and knowledge graph | `bob-optimize` CLI | 2–5 minutes | ~0 (local compute) |

**Total first-session investment: 200–500 Bobcoins + ~30 minutes of human
time.** This is the payback threshold — the KB must save more than this
before it becomes net-positive.

> **Breakeven:** At a measured mean saving of 2.22 Bobcoins per
> architecture query, the KB pays back its creation cost in roughly
> **1–3 sessions** for recurring query types. See §4 for the full
> ROI model.

### Ongoing maintenance cost

| Task | Frequency | Time | Bobcoin cost |
|---|---|---|---|
| `mnemox --quick` (lessons + graph refresh) | After every significant session | 30 seconds | ~50 BC |
| `mnemox` / `mnemox --full` (full 7-phase analysis) | When source files change materially | 5–10 minutes | 100–300 BC |
| Review and cross-reference new KB documents | Weekly | 15 minutes human | ~0 BC |

**Monthly maintenance cost estimate: 300–800 Bobcoins** for an active
project with weekly source changes. A project with a stable codebase
costs less; a rapidly-changing one costs more.

### What "free" does not mean

The KB Manager is free to install. The investment is **discipline**: someone
on the team must run `mnemox` after significant sessions, review the filed
documents, and retire stale ones when the source changes. A KB that is never
updated becomes a liability — Bob retrieves outdated answers at low token
cost, which is worse than re-deriving the correct answer at higher cost.

---

## §4 — The Return: Measured and Structural Savings

The savings from Mnemox come from two distinct mechanisms. They are
**not additive in a simple way** — each has its own applicability condition,
its own measurement basis, and its own confidence level. A honest ROI
model must keep them separate.

### Mechanism 1 — Re-derivation elimination (KB Manager)

**What is saved:** The difference between reading the raw source and reading
the KB digest. For a well-formed KB document (a compact summary of a larger
source), this is structural — the KB document is smaller than the source by
design.

**Measured on this repository:**

| Population | N pairs | Mean saving | 95% CI | Meaning |
|---|---|---|---|---|
| Well-formed KB summaries | 10 | **51%** | [38%, 64%] | KB doc is genuinely more compact than its source |
| Comprehensive guides/research | 9 | −52% | — | These are not summaries — they are larger than source by design |
| **All 19 pairs combined** | 19 | 2% | [−32%, +30%] | Mixed — the two populations must not be combined |

> **The right unit of measurement is the compact-summary population
> only.** The 9 comprehensive documents (guides, research notes, plans)
> are not designed to replace reading the source — they serve a different
> purpose. Including them in the savings headline would be dishonest.

**ROI on well-formed pairs:**
- Mean saving: 2.22 Bobcoins per query
- Creation cost: ~0.80 Bobcoins
- Maintenance cost: ~0.30 Bobcoins per update cycle
- **Breakeven: 1 query.** Return: ~80× at 40 queries on the same document.

**Scenarios by project type:**

| Project type | Typical saving (amortised over 6 months) | Confidence |
|---|---|---|
| Large, stable codebase (100K+ tokens); repetitive architecture queries | 60–75% | Medium |
| Medium, active codebase (30K tokens); mixed queries | 35–50% | Medium |
| Small, rapidly-changing codebase; mostly unique queries | 15–25% | Low |
| One-off engagement; no repetition | 0% (KB creation cost not recovered) | High |

### Mechanism 2 — Prompt compression (Token Optimizer)

**What is saved:** Redundant tokens in every prompt — before the prompt
is sent, regardless of whether a KB exists.

**Measured:** ~20% mean reduction (95% CI [18.9%, 21.2%], N=183 structured
Markdown documents, tiktoken BPE, null test passed).

- **Corpus scope:** Structured Markdown prose from this repository. Savings
  on conversational text, code-heavy inputs, or API responses are not yet
  measured — treat 20% as an upper bound for those content types.
- **Activation condition:** Every novel prompt. Workload-independent.
- **Additional cache saving:** If your request stream has repeated or
  near-duplicate prompts, cache hits return at 0 Bobcoins. Rate is
  workload-dependent (0% for fully unique streams; 30–90% for repetitive
  documentation or code-analysis workflows).

### Combined: what to tell a business owner

```
Scenario: Engineer using both systems on a stable codebase for 6 months

  Session 1 (KB creation):   net cost (investment)
  Sessions 2–10:             ~30–50% saving (KB immature + optimizer)
  Sessions 11+:              ~50–70% saving (mature KB + optimizer)
  Amortised over 6 months:   50–65% average Bobcoin reduction

Conservative single figure for budget planning: 40–60% reduction
Optimistic figure (ideal conditions): 60–75%
```

**What we are not claiming:** Guaranteed percentages. Additive savings.
Universal applicability. These figures require the right project type
(stable, recurring queries), the right adoption behaviour (KB maintained),
and the right content type (structured Markdown prose, not raw code).

---

## §5 — The Strategy: The Compounding Thesis and the Long-Term Bet

### Why this is a strategic investment, not just a cost tool

Karpathy's insight is that a knowledge base that compounds is
qualitatively different from one that does not. The immediate saving
(fewer Bobcoins) is real but secondary. The strategic value is what
the freed budget makes possible.

**The compounding loop:**

| Session | What happens | Cumulative effect |
|---|---|---|
| **Session 1** | Bob reads your repo → files KB documents | Investment session. Spend ~300 BC to save thousands. |
| **Sessions 2–10** | Bob reads KB only → saves 200–400 BC per session | Cost recovers within 1–3 sessions |
| **Sessions 11–50** | KB grows → graph surfaces cross-repo connections | Team asks broader, deeper questions that were previously too expensive |
| **Session 50+** | KB is the team's institutional memory | Questions previously unanswerable within budget become routine |

The ceiling on what Bob can attempt is set by Bobcoin budget divided by
session cost. Every percentage point of saving is a percentage point of
additional ambition. A team that reduces its per-session cost by 50% can
attempt twice as many sessions, or sessions twice as broad, for the same
budget. **The real return on Mnemox is not fewer Bobcoins spent — it is
more research conducted.**

### The team-level compounding effect

The KB is Git-backed and shared. This means:

- A new team member starts their first session from the full accumulated
  expertise of every prior session by every prior team member. Onboarding
  becomes retrieval, not re-derivation.
- Decisions documented in the KB survive team turnover. The architecture
  rationale Bob captured in March is available to the engineer who joins
  in September.
- Every IBM Bob mode, skill, rule, and MCP server your team uses produces
  knowledge worth keeping. The KB captures it — so the more capable your
  Bob setup, the more compounds.

### The strategic risk of not adopting

Teams that do not adopt a persistent knowledge pattern face a different
kind of compounding — compounding re-derivation cost. As projects grow,
the raw source that Bob must re-read to answer each question grows with
it. **The per-session Bobcoin cost rises proportionally with repository
size** — a 100K-token repo costs roughly 5× more per architecture session
than a 20K-token repo, and that gap widens with every sprint. The questions
that become too expensive to ask arrive earlier, and they arrive for every
team member simultaneously.

The IBM Bob ecosystem compounds this risk: every new mode, skill, and MCP
server your team activates adds capabilities — which generate more valuable
findings — which are lost at session end unless a persistent memory layer
exists. Mnemox is that layer; without it, the more capable your Bob setup
becomes, the more you lose per session.

---

## §6 — The Fit: Integration with Your IBM Architecture

### Deployment model

Mnemox is a **local tool, not a service.** There is no server, no database,
no cloud dependency, and no network call at runtime (beyond Bob itself).

| Constraint | Value |
|---|---|
| Deployment target | Local developer workstation or Bob IDE workspace |
| Network dependency | None at runtime |
| Data residency | All KB documents are Git-committed Markdown files in your repository |
| Authentication | IBM Bob authentication only — no additional credentials |
| Admin rights required | No |
| IT approval for install | No — zero external dependencies |

### Integration points

Three opt-in integration points connect Mnemox to the IBM Bob ecosystem.
All three are fallback-safe — removing any one leaves the others working.

| Integration | What it adds | Dependency |
|---|---|---|
| KB query + embedding index | Semantic search over KB documents | `sentence-transformers` or `mlx-embeddings` (optional Python packages) |
| Knowledge graph | Orphan/hub detection, multi-hop traversal | Pure Python; no external dependency |
| Context compression | Prompt compression before Bob call | `bob-optimize` CLI (Python 3.11+) |

### Compatibility with the IBM Bob ecosystem

Mnemox is a native Bob mode — it composes with every mode, skill, rule,
and MCP server in the Bob Marketplace. It is not a plugin and installs
no MCP server. It adds no catalog tax (the per-turn cost of MCP tool
catalogs). The KB becomes the persistent memory layer underneath your
entire Bob toolkit.

**Compatible with:** `ibm-watsonx-data`, `ibm-docling`, `carbon-mcp`,
`techzone`, `watsonx-orchestrate`, and any current or future Bob capability.

### What it touches in your repository

```
docs/knowledge-base/          ← all KB documents (Markdown, Git-committed)
  concepts/                   ← architectural concepts, system models
  guides/                     ← how-to guides, workflows
  references/                 ← API references, specifications
  research/                   ← findings, analyses, experiment notes
  INDEX.md                    ← auto-maintained catalogue
.bob/kb-index/                ← embedding vectors (local, gitignored)
.bob/kb-graph.json            ← knowledge graph (local, gitignored)
```

The KB documents are the only persistent artefact that requires governance
decisions. They are plain Markdown files — readable, diffable, and
auditable in any Git workflow. The embedding index and graph are local
cache files, regenerated on demand, and never committed.

---

## §7 — The Risks: Honest Maturity Statement and Mitigations

### Maturity

**Current status: Beta — Not Production Ready**

This is not a cautious label applied to a production-quality system.
It reflects a specific, documented state:

| What "Beta" means here | What it does NOT mean |
|---|---|
| The Token Optimizer has not been validated on diverse external corpora — only on structured Markdown prose from this repository | The core implementation is buggy or unstable |
| The KB Manager savings are workload-dependent and not benchmarked on external projects | The pattern does not work |
| No enterprise SLAs, no on-call rotation, no Windows support | The quality gates (1,112 tests, 89.82% coverage, ruff + mypy clean) are not real |

**Engineering quality grade: A+ (4.30/4.30) against Tier-1 institutional
standard** — all correctness bugs fixed, CI-enforced quality gates, STRIDE
threat model, 19 ADRs. The "Beta" label reflects measurement scope, not
implementation quality.

### Known limitations for enterprise evaluation

| Limitation | Impact | Mitigation |
|---|---|---|
| Optimizer validated on repo Markdown only | 20% saving may be lower on conversational text, code, or JSON | Run `bob-optimize validate` on a sample of your actual prompts before committing |
| KB savings are workload-dependent | ROI varies significantly by project type | Pilot on one stable, recurring-query project for 4–8 weeks before broader rollout |
| KB requires active maintenance | A stale KB returns wrong answers cheaply | Assign `mnemox --quick` as a session-close discipline; automate with a Git hook |
| Token Optimizer is Beta | Not suitable for systems requiring uptime SLAs | Use as a development-time tool, not an inline production service |
| No Windows support | Bash scripts are macOS/Linux only | Bob IDE (Windows-compatible) works; the analysis scripts require a POSIX shell |
| Knowledge graph P@3 uplift is corpus-dependent | Graph re-ranking adds 0 P@3 on the current tight-topic corpus | Graph primary value today is structural health (orphan/hub detection), not ranking |

### The honest ROI risk

The savings figures in §4 are honest but conditional. A deployment that
does not meet the applicability conditions will not achieve them:

- **Re-derivation saving requires stable, recurring queries.** A team
  that uses Bob primarily for one-off exploratory tasks will not recover
  the KB creation cost.
- **Compression saving requires structured prose.** Codebases that are
  primarily raw code or JSON will see lower savings than the measured 20%.
- **Both savings require adoption discipline.** A KB that is created once
  and never updated degrades toward zero value within weeks of the source
  changing.

---

## §8 — The Decision

### What needs to be decided

| Decision | Options | Recommended | Success metric |
|---|---|---|---|
| **Adopt Mnemox KB Manager?** | (A) Full adoption; (B) Pilot one project; (C) No adoption | B — 4–8 week pilot on a stable, recurring-query project | Per-session BC cost falls ≥20% on recurring architecture queries by week 4 |
| **Adopt Token Optimizer?** | (A) Integrate into workflow; (B) CLI use only; (C) Skip | B — CLI use for prompt compression during development; defer library integration until TOS reaches v1.0 | `bob-optimize validate` on your prompt sample shows ≥15% compression |
| **Activate semantic embedding index?** | (A) Yes; (B) No | A — low-cost, high-impact; requires only `pip install sentence-transformers` | P@3 on your KB queries ≥ 80% (vs. ~44% keyword baseline) |
| **Activate knowledge graph?** | (A) Yes; (B) Health-check only; (C) No | B — run `graph-health` monthly to find orphans and dead links; defer score-blending (`graph_weight > 0`) until corpus diversifies | Zero broken cross-references in monthly health report |

### Pilot design (recommended entry point)

A minimal 4-week pilot that validates the core value proposition with
negligible risk:

**Week 1:** Install Mnemox into one Bob IDE workspace. Run `mnemox` on one
active project. Measure the KB creation cost (Bobcoins consumed).

**Weeks 2–4:** Run every Bob session on that project in `knowledge-manager`
mode. Run `mnemox --quick` at the end of each session. Track Bobcoin
consumption per session.

**Gate:** At week 4, compare per-session Bobcoin cost before and after.
If the saving on recurring architecture/configuration queries covers the
creation cost plus 4 weeks of maintenance, continue. If not, the project
type is not a good fit — try a different project or don't adopt.

**No sunk cost:** If the pilot fails the gate, the only cost is the
initial KB creation Bobcoins (200–500 BC) and 4 weeks of `mnemox --quick`
runs (~200 BC total). Total pilot risk: **400–700 Bobcoins**.

### Who decides

| Decision | Decision-maker | Input needed from |
|---|---|---|
| Pilot launch | Team lead or engineering manager | One volunteer project; 30 minutes of setup time |
| Broader rollout | CTO or head of engineering | Pilot results; maintenance burden assessment |
| Enterprise architecture integration | Enterprise Architect | Integration review against existing IBM toolchain; data residency sign-off |
| Production deployment of Token Optimizer | CTO + Platform team | TOS stability milestone (currently Beta); SLA requirements |

### When

The pilot can start today. It requires no IT approval, no external
dependencies, and no budget beyond the Bobcoin cost of running Bob
sessions — which the team is already spending.

The broader rollout decision depends on pilot results. A 4-week pilot
started today produces a data-backed decision by mid-August.

---

## Related Documents

| Document | What it adds |
|---|---|
| [**Executive Brief**](./mnemox-executive-brief-2026-07.md) | One-page decision-quality summary for CTO / executive sponsor — read this first |
| [**Competitive Positioning Brief**](./mnemox-positioning-brief-2026-07.md) | Why Mnemox vs. RAG / vector DB / LangChain memory — for Enterprise Architects |
| [Technical Design Retro](./full-technical-design-retro-2026-07.md) | Full architecture: components, SLA, CI gates, open gaps — for engineers |
| [Bobcoin Savings Analysis](./bobcoin-savings-analysis-2026-07-14.md) | Detailed savings model with scenarios and variance reporting |
| [KB Savings Measurement Guide](../guides/km-bobcoin-savings-measurement-guide.md) | How to measure your own workload savings during the pilot |
| [KB-TOS Integration Roadmap](../guides/kb-tos-integration-roadmap.md) | P1/P2/P3 integration milestones and current status |
| [Architecture — KB Manager](../../../docs/kb-manager/ARCHITECTURE.md) | KB Manager arc42 architecture (arc42 v2.1) |
| [Architecture — Token Optimizer](../../../docs/architecture/architecture.md) | Python token-optimizer architecture (arc42 v3.0) |
| [STATUS.md](../../../STATUS.md) | Canonical maturity status — single source of truth |

---

*Created: 2026-07-18*
*Audience: Business Owner · CTO · Enterprise Architect*
*Category: Research*
