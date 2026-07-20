# Pitch File — Slide-by-Slide Outline
**Team BobjectifLune** — *Objectif Lune*: aim at the impossible. Bob as the craft; the KB as the flight log.

> **Required for judging submissions (optional for non-judged).**
> Target: ~8 slides / ~2.5 minutes. Lead with the outcome, demo the zero-install path, close on honesty.
> Tone: outcome-first, honest, no inflated claims.
> **Copyright:** use the *name* and an original moon/rocket motif — **no Tintin/Hergé artwork or text**.

> **✅ The judged artifact is already built:** [`08-pitch-deck.pdf`](./08-pitch-deck.pdf) (3 pages, ≈0.46 MB)
> condenses this outline into the required PDF. Upload that. Keep this 8-slide outline as the source for
> (a) recording the optional ≤3-min **MP4** instead, or (b) expanding into a longer live-presented deck.
> The PDF's 3 pages map to: **Page 1** = Slides 1–2 (problem + insight), **Page 2** = Slides 3–5 (how it
> works + numbers), **Page 3** = Slides 6–8 (adopt + trust + frontier).

---

## Narrative through-line: *Objectif Lune*

Bookend the deck with the team story so it lands as one arc, not eight facts. **BobjectifLune** = Bob +
*Objectif Lune* (Destination Moon): aim at the impossible, reach it through curiosity, involvement,
fail-fast, and resiliency — with Bob as the craft. The KB is the **flight log** that makes the next mission
launch from altitude, not the ground. Map each value to something *real* in the project:

| Value | Where it actually shows in this project |
|---|---|
| **Curiosity** | Asked "why do we re-pay for what Bob already knew?" — reframed cost as a *memory* problem |
| **Fail-fast** | Shipped a wrong 68.96% figure, *caught it fast*, retracted it publicly |
| **Resiliency** | Rebuilt a manifest-backed validation harness + CI that blocks any unprovenanced number |
| **Involvement** | Team-shared KB — one member's knowledge becomes everyone's; value compounds |

---

## Slide 1 — The hook · open the arc (Practicality)

**Headline:** On the way to the impossible, you cannot afford to forget what you already learned.

> "Team BobjectifLune — Bob, plus *Objectif Lune*: aim at the impossible. Here's ours. Every Bob session
> starts amnesiac. It re-reads your repo and re-answers last week's question — you pay Bobcoins and your
> own time to relearn what Bob already knew."

Show the compounding-knowledge loop graphic (`docs/assets/kb-compounding-loop.svg`). One original moon/rocket motif, no Tintin art.

**Visual idea:** Simple before/after — "Session 1: Bob reads 2,000 lines. Session 10: Bob reads 2,000 lines again." → "With KB: Session 10 reads 200 lines."

---

## Slide 2 — The insight (Creativity)

**Headline:** Knowledge should compound — not restart.

> "The fix isn't a shorter prompt. It's a *memory*." One line: we implement Karpathy's LLM-Wiki pattern —
> but **native to Bob**, as two modes, no plugin, no MCP. *Our* originality: Bob-native modes + Bobcoin-economy
> framing + a cacheable schema layer.

- Andrej Karpathy's LLM-Wiki pattern: persistent, version-controlled KB the LLM maintains itself
- *"The wiki is a compounding artifact. The cross-references are already there."* vs. RAG: *"the LLM is rediscovering knowledge from scratch on every question. There's no accumulation."*
- Three layers: Raw sources → Wiki (KB) → Schema (mode + AGENTS.md)
- **The distinction from RAG in one line:** RAG retrieves from a snapshot. Mnemox accumulates and compounds. One note on the slide is enough — Slide 7 closes it fully.

**Visual idea:** Three-layer diagram — Raw sources → Wiki (KB) → Schema

---

## Slide 3 — Live demo, zero install (Design & usability)

**Headline:** Mnemox — two native Bob modes, zero plugins. The memory IBM Bob was missing.

Open Bob IDE → mode picker → **🧠 Mnemox Knowledge Builder**. First message:
> "What did we document most recently? Summarise the KB and suggest what to work on next."

Show Bob answering from the KB, grounded, *without re-reading raw source.* Emphasise: **5 seconds, zero setup.**

- **🧠 Mnemox Knowledge Builder mode** — living KB: concepts, guides, references, research — templates, cross-references, self-updating index
- **🔍 Repo Analyzer mode** — 7 automated scripts → ~200-line digests, filed into the KB
- Works in **Bob IDE** (mode picker, zero install) and **Bob Shell CLI**

**Visual:** Screenshot of Bob IDE mode picker showing "🧠 Mnemox Knowledge Builder" selected *(Take this screenshot from your own Bob IDE — 2 minutes)*

---

## Slide 4 — Under the hood (Effectiveness)

**Headline:** Six token-economy taxes. Each one has a concrete Bash-KB fix.

The 6 token-economy taxes and how the **Bash KB Manager** removes them — no Python required:

| Waste | How the Bash KB Manager removes it |
|---|---|
| **Catalog tax** (MCP re-sends tool list every turn) | Native Bob mode — no plugin, no MCP |
| **Payload tax** (2,000-line file for 20 relevant lines) | 7 analysis scripts summarise; KB stores digests you *cite* |
| **Compression trap** (stripping meaning raises cost) | Templates preserve rationale, real names, cross-refs |
| **Short-thread tax** (turn 15 re-pays 14 turns of history) | Knowledge persists in KB + `save_memory`; fresh thread retrieves |
| **Cache misses** (reworded prefixes) | Fixed mode + `AGENTS.md` + stable KB layout = cacheable prefix |
| **Verbose output** | Bounded artefacts — templates, `INDEX.md`, reports — not essays |

> The optional Python Token Optimization System goes further (20% compression, semantic cache) — see the appendix slide. The Bash KB Manager requires nothing beyond Bob.

---

## Slide 5 — The numbers, honestly (Effectiveness + trust)

**Headline:** ~60% fewer Bobcoins per iteration cycle — reinvested into 94 richer demos.

- **51% re-derivation saving** — when Bob retrieves from a compact KB summary instead of re-reading raw source (N=10 compact-summary pairs; CI [38%, 64%]). Compact summaries are the right unit: architecture decisions, concept digests, reference sheets — intentionally smaller than source.
- **On hcd-at-its-core** — 94 interactive demos, 15 masterclasses on real clusters — the KB Manager cut Bobcoin spend per iteration cycle by **~60%** (session cost readout, single-project observation by the author). Every Bobcoin recovered was reinvested into deeper failure modes, richer topologies, and more entropic scenarios that would otherwise have been unaffordable.
- The KB is version-controlled: every session compounds into one shared institutional asset.

**Visual idea:** Simple ROI chart — X axis: queries, Y axis: Bobcoin cost — two lines: "without KB" (flat high) vs "with KB" (low after breakeven at query 1)

---

## Slide 6 — The South EMEA / watsonx.data proof (Practicality + Impact)

**Headline:** Any IBMer can adopt it in under 5 minutes — and the Tiger Team already has.

The real Tiger-Team workflow you accelerated (see [`05-emea-watsonxdata-case-study.md`](./05-emea-watsonxdata-case-study.md)) — a lakehouse/real-time engagement pattern that now starts from accumulated KB expertise instead of zero. *Grounds the tool in real IBM revenue work.*

- **Bob IDE:** mode picker → 🧠 Mnemox Knowledge Builder — zero installation, zero CLI, zero scripts
- **Bob Shell CLI:** one alias, one command
- Plain Markdown files in Git — no proprietary format, no lock-in, adoptable by any IBM team

**Visual idea:** Two-step activation — (1) Open workspace (2) Select mode → done

---

## Slide 7 — Why it wins on trust (Creativity + quality)

**Headline:** Not RAG. Not a plugin. Not a benchmark. A compounding memory — that won't overclaim its own savings.

> "We caught our *own* fabricated 68.96% figure, retracted it, and built CI that blocks any unprovenanced
> number. A productivity tool that won't overclaim its own productivity."

| | RAG | MCP Server | Mnemox (Bob Shell KM) |
|---|---|---|---|
| Rediscovers from scratch every query | ✅ Yes | ✅ Yes | ❌ No — retrieves |
| Catalog tax | No | ✅ Yes | ❌ No |
| Knowledge accumulates over time | ❌ No | ❌ No | ✅ Yes |
| Works natively in Bob IDE | Depends | Depends | ✅ Yes |

STRIDE threat model · bandit SAST · null tests · manifest-backed validation · formal retraction on file.

---

## Slide 8 — The ask / the frontier · close the arc

**Headline:** **BobjectifLune** — curiosity, resilience, and IBM Bob on the road to the impossible.

> "When re-derivation cost approaches zero, the budget freed from repetition funds depth, breadth, and
> deeper agent teams — it moves the frontier of what's affordable to attempt with Bob. That's *Objectif
> Lune*: Bob got us off the ground, the knowledge base is the flight log that keeps us climbing. The
> impossible, made repeatable."

- **BobjectifLune** — inspired by Tintin's *Objectif Lune*: what seems impossible becomes achievable through curiosity, a fail-fast mindset, and resilience. **Mnemox** is the craft.
- This submission was drafted using the tool it describes. The knowledge base at `docs/knowledge-base/` — 110+ documents — was created and maintained by the Knowledge Manager mode. The GitHub repository is the proof of concept.
- Open-sourced under MIT license — any IBM team can clone, init, and start compounding immediately
- **Next:** a domain-specific starter KB for watsonx.data Tiger Teams so every South EMEA engagement starts from accumulated expertise, not zero

---

## Appendix A — Optional Python Token Optimization System (backup slide / Q&A)

> **Do not include in the main 8-slide deck.** Use only if a judge asks "how does the 20% compression work?" or "what is the optional system?"

**Headline:** Optional Python layer — goes further, requires nothing for the core product.

- **~20% mean compression** (N=183, null-tested, manifest-backed; CI [18.9%, 21.2%]) — whitespace + redundant-phrase removal, quality ≈ 0.80
- **Cache: 20% → 92%** depending on repetition rate — we show the model, not one flattering number
- **Graph layer** — built, measured, retrieval uplift neutral; ships disabled; used for KB structural health (orphan detection, hub analysis)
- Independently operable: if Python is absent, the Bash KB Manager is completely unaffected
- **Beta — Not Production Ready**: API stability not guaranteed; do not depend on it in production pipelines

> "The Bash KB Manager is the product. The Python system is the accelerator. You do not need it to start compounding."

---

## Deck Production Notes

- Keep each slide to **one idea, one headline, one visual**
- **Show, don't tell** — the zero-install IDE demo (Slide 3) is your strongest 30 seconds; rehearse it cold
- The personal hcd example on Slide 5 is the most important moment in the pitch — pause on it
- Close on the honesty slide (Slide 7) — it's what no other team will have
- Slides 1–8 are the main deck; Appendix A is backup for judge Q&A only
- **Do not** show the Beta Python install path on camera; lead with the mode picker
- **Do not** surface any non-Bob build tooling in the recording
- **Do not** show STATUS.md on camera, and do not cite any grade. The prior A+ self-grade was **withdrawn** (self-grading isn't verification — which is exactly our brand). If maturity comes up: "Bash KB Manager is stable v1.0; the Python layer is Beta; every number is measured and labelled."
