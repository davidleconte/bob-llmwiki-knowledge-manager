---
title: Mnemox Engineering-Soundness — Deck Outline
category: consulting
tags: [engineering-soundness, deck, pitch, board-readout]
created: 2026-07-19
updated: 2026-07-19
status: active
trust_tier: verified
provenance: Slide-by-slide source for the engineering-soundness deck (PPTX generated from this outline). Action-title style, one governing message per slide. Numbers cited to their single home. Dual-use — internal board read-out and watsonx pitch adaptation.
---

# Deck outline — action titles, one message per slide

Design rules: assertion titles (the title states the takeaway); one governing message per slide; Pyramid structure (governing thought → key line of five → support); **original moon/rocket motif only — no Tintin/Hergé artwork** (challenge-pack copyright caution). Numbers cite their single home; the withdrawn figure appears only with a "retracted" label.

| # | Action title (the takeaway) | Body / support | Visual |
|---|---|---|---|
| 1 | **Mnemox's status is honest; its A+ grade isn't earned — yet.** | SCQA in four lines; the answer bolded. | SCQA block; moon-mission motif |
| 2 | **One question governs this review.** | "Is Mnemox engineering-sound, and what will make it so?" → five MECE branches. | 5-branch issue tree |
| 3 | **The A+ and the 2.9/5 are both right — they grade different things.** | Artifact completeness vs functional integration; the reconciled scorecard. | Scorecard table (2.9 → 4.2) |
| 4 | **The flagship retrieval stack was built, validated — and never called.** | The core defect; now fixed in-tree but uncommitted. | Dataflow: validated stack greyed vs keyword-only live path |
| 5 | **~20 lines of wiring move retrieval precision from 0.64 to 0.88.** | Highest-ROI fix; already in `src/cli.py:344-388`, needs commit + proof. | Before/after path + effort tag |
| 6 | **The optimiser could silently return nothing.** | Empty output on >4096-token prompts; never-empty post-condition now in `prompt_optimizer.py:242-255`. | Input → empty example, deterministic |
| 7 | **The gates that should catch corruption couldn't fail.** | `validate-kb.sh` false-green (fixed); bare-"manifest" backing (fixed); case-broken pointer. | False-green → red diff |
| 8 | **The savings that survive audit are the ones we measured honestly.** | The manifest-backed ~20% compression (source: `evaluation/results/validation-2026-07-14/manifest.json`); the withdrawn 68.96% is retracted. | Value-driver tree, Branch A |
| 9 | **Memory savings are real but unrealised — because retrieval was unwired.** | Branch B eligibility lever; realised ≈ 0 until wiring lands and is proven. | Value-driver tree, Branch B |
| 10 | **Fifty-five findings; six that block.** | Register headline: 6 Critical / 12 High / ~20 Med / ~12 Low; dominant status = fixed-uncommitted. | Severity bar |
| 11 | **Fix what's certain and cheap first.** | Commit + prove the hardening layer; then lifecycle, corpus guard, re-grade. | Impact × Effort 2×2 with findings plotted |
| 12 | **Two risks fire on every session.** | Unwired retrieval + empty-optimise (both fixed-uncommitted → must prove); credibility risk of the grade. | Severity × Likelihood 2×2 |
| 13 | **Days, then weeks, then months.** | H1 Reconnect & Repair → H2 Harden & Prove → H3 Scale & Differentiate, each with an exit gate. | Three-Horizons swimlane |
| 14 | **A fix isn't done until a test proves it was broken.** | Red-on-unfixed / green-on-fixed discipline; commit the p@3 golden set. | RED→GREEN loop |
| 15 | **Re-grading in public is the brand, not a retreat.** | Retraction discipline is the moat; commission a genuinely independent re-grade. | Retraction-discipline timeline |
| 16 | **Reconnect, prove, differentiate — 2.9 → 4.2.** | The ask + the top-5 recommendations. | Trajectory arrow + top-5 list |

## watsonx pitch adaptation (swap-in notes)

For the challenge pitch (not the board read-out): front-load slides 4, 8, 15, 16 and map each to a judging axis — Effectiveness ← 8/9, Creativity ← 15, Practicality ← 4/5, Design ← 5. Keep the STATUS.md self-grade off-camera (challenge-pack caution). Close on the mission tagline ("Bob got us to the moon; the knowledge base gets us back — from accumulated altitude, not the ground"). Original artwork only.
