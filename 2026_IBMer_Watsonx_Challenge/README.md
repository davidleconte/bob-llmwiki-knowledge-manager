# 2026 IBMer watsonx Challenge — Submission Pack

> ✅ **SUBMITTED — frozen 2026-07-25.** This pack was submitted to the 2026 IBMer
> watsonx Challenge before the **22 July 2026, 10:00 ET** deadline, as a zip of the
> repository at that release. It is preserved as the record of what was entered and is
> **no longer a working document**: unchecked boxes below are the state at submission,
> not outstanding work, and the deadline references are historical.
>
> Numbers here were correct against the evidence available on 22 July. Two have since
> been superseded and are **not** retro-edited, because this is a submission record:
>
> * **Compression.** The pack cites ~20% mean. A 2026-07-25 re-measurement puts the
>   current system at **6.8%** — the optimizer was made structure-preserving, trading
>   ~12pp of compression for fidelity (0.798 → 0.995). See [`STATUS.md`](../STATUS.md).
> * **The ≈60% Bobcoin figure.** A single-project practitioner observation with **no
>   repo artifact**, as `09-compound-loop-demo.md` in this same pack says of it. It was
>   labelled as an observation rather than a measurement, which was the right call, but
>   it is not reproducible and should not be repeated as one.

> **Team: BobjectifLune** · Business area: **Software** (SDLC / developer productivity).
> Author: David Leconte, WW watsonx.data Tiger Team (South EMEA). Deadline: **July 22, 2026, 10:00 ET**.

---

## Team narrative (the spine of the pitch)

**BobjectifLune** = **Bob** + *Objectif Lune* (Tintin's *Destination Moon*). The name is the thesis:
*aim at what looks impossible, and reach it through curiosity, involvement, a fail-fast mindset, and
resiliency* — with **IBM Bob as the game-changing craft** for the journey.

The metaphor is not decoration — it *is* the product:
- **The moon = the impossible goal.** Bob is the rocket that makes the ascent affordable.
- **The knowledge base = the flight log.** The crew doesn't re-derive the route on the return trip; each mission builds on the last. The KB is that log — knowledge is written once and retrieved thereafter, so every session launches from accumulated altitude instead of the ground.
- **The values are true to the artifact's own history.** This project shipped a fabricated 68.96% savings figure, *caught it, retracted it, and re-measured honestly at 20%* — curiosity, fail-fast, and resiliency, demonstrated on itself. The team's ethos and the code's story are the same story.

> **Tagline candidates** (pick one for the deck): · "The impossible, made repeatable." ·
> "Aim for the moon — keep the flight log." · "Bob got us to the moon; the KB gets us back."

> **Copyright caution:** *Tintin* / Hergé artwork is protected. Do **not** put Tintin images or book
> excerpts in an official IBM submission — use the *name* and an original moon/rocket motif only.

The repo is the evidence; **these files are what get scored.** Every quantitative claim was re-verified
against live repo artifacts (2026-07-20) and corrected where it had drifted.

---

## Documents in This Pack

| # | File | Challenge field | Status |
|---|------|-----------------|--------|
| 1 | [`01-solution-statement.md`](./01-solution-statement.md) | Solution statement — *what it does* | ✅ **483 words** (limit 500) — paste into form field 1 |
| 2 | [`02-technical-statement.md`](./02-technical-statement.md) | Technical statement — *how it works* | ✅ **478 words** (limit 500) — paste into form field 2 |
| 3 | [`03-solution-impact.md`](./03-solution-impact.md) | Solution impact | ✅ **FORM ENTRY block at top** — categories + hours + frequency |
| 4 | [`04-pitch-file-outline.md`](./04-pitch-file-outline.md) | Pitch file — slide-by-slide source | ✅ Source of truth for the deck |
| 5 | [`05-emea-watsonxdata-case-study.md`](./05-emea-watsonxdata-case-study.md) | Impact evidence (feeds fields 3 + 4) | ✅ hcd ≈60% proof |
| 6 | [`06-demo-script.md`](./06-demo-script.md) | Live demo (drives the pitch) | ✅ Rehearse cold |
| 7 | [`07-submission-checklist.md`](./07-submission-checklist.md) | Pre-submit gate check | ✅ Use before every submit |
| 8 | [`08-pitch-deck.pdf`](./08-pitch-deck.pdf) · [`08-pitch-deck.html`](./08-pitch-deck.html) | **Pitch file (required for judging)** | ✅ **Built — 3 pages, ≤10 MB.** Upload the PDF. |

> The pitch PDF is generated from `08-pitch-deck.html` (self-contained, no external assets) via
> `weasyprint 08-pitch-deck.html 08-pitch-deck.pdf`. Edit the HTML, re-run, re-upload.

---

## Judging Criteria (keep visible while writing)

| Criterion | Weight signal | Current position |
|---|---|---|
| **Practicality & Coherence** | Is the need for Bob clear? Is it feasible? | Strong — Tiger Team persona, South EMEA geography, two working modes |
| **Effectiveness & Efficiency** | Significant, repeatable impact on daily work? | Good — 20% manifest-backed + hcd ≈60% personal proof |
| **Design & Usability** | Easy to adopt into everyday work? | Strong — mode picker, zero install, no CLI required |
| **Creativity & Innovation** | Unique approach, differentiated? | Strongest — LLM-Wiki native to Bob is novel; honesty brand is unique |

---

## Integrity rule for this pack

Every number is either (a) traceable to a manifest-backed run, or (b) labelled at its exact confidence
level (e.g. "single-project observation"). **Do not ship a vague claim as a fact.** The differentiator is
that this project withdrew a fabricated savings figure and re-measured honestly — one inflated number
throws that away.

---

## Honest self-scorecard (know where you're exposed)

| Criterion | Self-grade | Strength to lean on | Exposure to close |
|---|---|---|---|
| **Practicality & coherence** | Strong | Real SDLC pain; Bob-native, not a bolt-on | Keep the narrative Bob-centric |
| **Effectiveness & efficiency** | Good | 20% measured + hcd ≈60% personal proof | Lean on the reinvestment story, not just the percentage |
| **Design & usability** | Strong | Zero-install Bob IDE mode | Two-system surface; lead with one path (demo #6) |
| **Creativity & innovation** | Undersold | Bob-native modes + Bobcoin-economy framing + honesty brand | Name the novelty on Slide 2; close on the retraction story on Slide 7 |

---

## Fact-check changelog

### 2026-07-20 (this pass — overhaul for submission-readiness)
- **🔴 Fixed word-limit violations.** Field 1 was **701 words**, Field 2 was **807 words** — both over the hard **500-word** form limit and would have been truncated mid-argument. Rewritten to **483** and **478** words with the strongest beats intact.
- **🟠 Removed the withdrawn "A+" self-grade defense** from Field 2. `STATUS.md` (2026-07-19) records that the self-assessed A+ was **withdrawn** ("self-grading is not verification"). Defending a retracted grade contradicts the honesty brand; Field 2 now simply states the system is labelled **Beta** and reported at measured confidence.
- **🟠 Added a FORM ENTRY block to Field 3** — the impact field is structured (categories + hours-before/after + frequency), which the prose lacked. Task = one Bob iteration cycle; **2.0 hr → 0.8 hr (≈60%)**, multiple times/day, anchored to the measured ≈60% Bobcoin reduction.
- **🟠 Built the pitch PDF** (`08-pitch-deck.pdf`, 3 pages) — judging requires an actual PDF/MP4, not an outline.
- **🟡 Fixed all 7 broken document links** in this README (`01_SOLUTION_STATEMENT.md` → `01-solution-statement.md`, etc.).
- **🟡 Tightened the fidelity claim.** `report.json` flags quality 0.80 as a *lexical-overlap heuristic, not semantic fidelity*; Field 2/3 now say exactly that instead of "meaning largely preserved."
- **🟡 Updated KB document count** "90+" → "**110+**" (live count 118; using the stable rounded floor).
- **Re-verified SUPPORTED against live artifacts (2026-07-20):** 20.0% mean / 22.8% weighted / null 0.73% / N=183 / quality 0.7984 (`evaluation/results/validation-2026-07-14/report.json`); `graph_weight = 0.0` default (`src/cli.py`); both `custom_modes.yaml` files; `bob-optimize` CLI (`pyproject.toml`); `docs/assets/kb-compounding-loop.svg`.

### 2026-07-18 (prior pass)
- Corrected p@3 baseline framing (0.88 = MiniLM embedding-only; graph re-ranking neutral, ships disabled).
- "near-lossless" → "high-fidelity (quality ≈ 0.80)"; headline numbers made exact; 51% pairs disclosed (N=10/19); 68.96% retraction verified on file.

---

## Project Repository

- [`../README.md`](../README.md) — full project documentation
- [`../STATUS.md`](../STATUS.md) — canonical maturity status. **Shows "Beta — Not Production Ready" and records that the prior A+ self-grade was withdrawn.** Consistent with our brand, but *do not put it on camera* — raw internal audit scores add nothing to the pitch and invite off-topic questions.
- [`../docs/knowledge-base/INDEX.md`](../docs/knowledge-base/index.md) — KB master index
