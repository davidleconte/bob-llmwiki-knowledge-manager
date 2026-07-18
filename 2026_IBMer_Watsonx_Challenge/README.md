# 2026 IBMer watsonx Challenge — Submission Pack

> **Team: BobjectifLune** · Business area: **Software** (SDLC / developer productivity).
> Author: David Leconte, WW watsonx.data Tiger Team (South EMEA). Deadline: **July 22, 2026, 10:00 ET**.

---

## Team narrative (the spine of the pitch)

**BobjectifLune** = **Bob** + *Objectif Lune* (Tintin's *Destination Moon*). The name is the thesis:
*aim at what looks impossible, and reach it through curiosity, involvement, a fail-fast mindset, and
resiliency* — with **IBM Bob as the game-changing craft** for the journey.

The metaphor is not decoration — it *is* the product:
- **The moon = the impossible goal.** Bob is the rocket that makes the ascent affordable.
- **The knowledge base = the flight log.** Tintin's crew doesn't re-derive the route on the return trip; each mission builds on the last. The KB is that log — knowledge is written once and retrieved thereafter, so every session launches from accumulated altitude instead of the ground.
- **The values are true to the artifact's own history.** This project shipped a fabricated 68.96% savings figure, *caught it, retracted it, and re-measured honestly at 20%* — curiosity, fail-fast, and resiliency, demonstrated on itself. The team's ethos and the code's story are the same story.

> **Tagline candidates** (pick one for the deck): · "The impossible, made repeatable." ·
> "Aim for the moon — keep the flight log." · "Bob got us to the moon; the KB gets us back."

> **Copyright caution:** *Tintin* / Hergé artwork is protected. Do **not** put Tintin images or book
> excerpts in an official IBM submission — use the *name* and an original moon/rocket motif only.

The repo is the evidence; **these files are what get scored.** Every quantitative claim was fact-checked
against the repo (2026-07-18) and corrected where it overstated.

---

## Documents in This Pack

| # | File | Challenge field | Status |
|---|------|-----------------|--------|
| 1 | [`01_SOLUTION_STATEMENT.md`](./01_SOLUTION_STATEMENT.md) | Solution statement — *what it does* | ✅ Ready — paste into form field 1 |
| 2 | [`02_TECHNICAL_STATEMENT.md`](./02_TECHNICAL_STATEMENT.md) | Technical statement — *how it works* | ✅ Ready — paste into form field 2 |
| 3 | [`03_SOLUTION_IMPACT.md`](./03_SOLUTION_IMPACT.md) | Solution impact | ✅ Ready — paste into form field 3 |
| 4 | [`04_PITCH_FILE_OUTLINE.md`](./04_PITCH_FILE_OUTLINE.md) | Pitch file (required for judging) | ✅ Ready — build deck/video from this |
| 5 | [`05_MEA_WATSONXDATA_CASE_STUDY.md`](./05_MEA_WATSONXDATA_CASE_STUDY.md) | Impact evidence (feeds fields 3 + 4) | ✅ Ready — hcd-at-its-core ~60% proof |
| 6 | [`06_DEMO_SCRIPT.md`](./06_DEMO_SCRIPT.md) | Live demo (drives the pitch) | ✅ Ready — rehearse cold |
| 7 | [`07_SUBMISSION_CHECKLIST.md`](./07_SUBMISSION_CHECKLIST.md) | Pre-submit gate check | ✅ Use before every submit |

---

## Judging Criteria (keep visible while writing)

| Criterion | Weight signal | Current position |
|---|---|---|
| **Practicality & Coherence** | Is the need for Bob clear? Is it feasible? | Strong — Tiger Team persona, South EMEA geography, two working modes |
| **Effectiveness & Efficiency** | Significant, repeatable impact on daily work? | Good — 20% manifest-backed + hcd ~60% personal proof |
| **Design & Usability** | Easy to adopt into everyday work? | Strong — mode picker, zero install, no CLI required |
| **Creativity & Innovation** | Unique approach, differentiated? | Strongest — LLM-Wiki native to Bob is novel; honesty brand is unique |

---

## Integrity rule for this pack

Every number is either (a) traceable to a manifest-backed run, or (b) labelled at its exact confidence level (e.g. "single-project observation"). **Do not ship a vague claim as a fact.** The differentiator is that this project withdrew a fabricated savings figure and re-measured honestly — one inflated number throws that away.

---

## Honest self-scorecard (know where you're exposed)

| Criterion | Self-grade | Strength to lean on | Exposure to close |
|---|---|---|---|
| **Practicality & coherence** | Strong | Real SDLC pain; Bob-native, not a bolt-on | Keep the narrative Bob-centric |
| **Effectiveness & efficiency** | Good | 20% measured + hcd ~60% personal proof | Lean hard on the reinvestment story, not just the percentage |
| **Design & usability** | Strong | Zero-install Bob IDE mode | Two-system surface; lead with one path (demo #6) |
| **Creativity & innovation** | Undersold | Bob-native modes + Bobcoin-economy framing + honesty brand | Name the novelty on Slide 2; close on the retraction story on Slide 7 |

---

## Fact-check changelog (2026-07-18)

- **Corrected:** p@3 = 0.88 is the MiniLM embedding-only baseline; the graph re-ranking is neutral (no uplift/regression) and ships disabled (`graph_weight = 0.0`). Stated honestly in `02`.
- **Softened:** "near-lossless" → "high-fidelity (quality ≈ 0.80)"; measured quality is just under the 0.8 threshold, so zero-loss is not claimed.
- **Tightened:** headline numbers now exact — 20.0% mean, CI [18.9%, 21.2%], weighted 22.8%, null 0.73%.
- **Expanded:** 51% re-derivation saving now explicitly cites "N=10 well-formed pairs of 19 total measured" — the 9 mismatched pairs are disclosed.
- **Updated:** KB document count corrected from "60+" to "90+" (actual KB has 90+ documents).
- **Updated:** test count corrected from "1102" to "1 112 passed"; coverage from "89.6%" to "89.82%".
- **Verified SUPPORTED:** two Bob modes, IBM skills ecosystem, all CI gates, STRIDE threat model, path-traversal regression test, the 68.96% retraction, Beta/Stable statuses, L1/L2 cache, `bob-optimize` CLI.

---

## Project Repository

[`../README.md`](../README.md) — full project documentation
[`../STATUS.md`](../STATUS.md) — canonical maturity status *(do not show on camera — self-assessed grade)*
[`../docs/knowledge-base/INDEX.md`](../docs/knowledge-base/INDEX.md) — KB master index
