---
title: "Adversarial Review Pattern"
category: concept
tags: [review, communication, submissions, quality, honesty-brand]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Adversarial Review Pattern

## Overview

A two-pass review technique where the first pass is explicitly hostile — searching for the strongest possible attacks on a deliverable — and the second pass is confirmatory. The adversarial pass consistently surfaces structural vulnerabilities that a friendly pass misses entirely, and the act of pre-empting each attack in the primary text converts vulnerabilities into transparency signals.

## Key Points

- Run adversarial *first*, friendly *second* — never only friendly
- Pre-empting an attack is stronger than surviving it
- Position determines whether a correct answer lands
- Score improvement is bounded by what cannot be fabricated — name unfillable gaps honestly
- Two true statements that appear to contradict each other require one sentence explaining they measure different things

## Details

### The Two-Pass Sequence

**Pass 1 — Adversarial (hostile examiner)**
The question is not *"does this read well?"* but *"what is the strongest attack a hostile reader can make, and does the text pre-empt it?"* Look for:
- Claims that admit unmeasurability in the same sentence that calls them most important
- Statistics buried in parentheticals that look like cherry-picking when extracted
- Features that appear to be dead ends (built but produce no measurable result)
- Labels or grades that appear to contradict each other
- Self-measurement on self-owned projects dressed as independent evidence
- Missing answers to the obvious objection ("where is the AI?")

**Pass 2 — Friendly (confirmatory)**
Confirm genuine strengths, framing opportunities, and positioning improvements. Do not use the friendly pass to find vulnerabilities — the adversarial pass already did that.

### The Pre-Emption Rule

For every attack found in Pass 1, resolve it by naming the vulnerability head-on *in the primary text*, not by adding a defensive footnote or disclaimer at the bottom. Placement matters:

| Approach | Effect |
|----------|--------|
| Name it in the opening paragraph | Converts attack into transparency signal before the reader forms the objection |
| Bury it in a footnote | Reader finds it themselves and wonders what else is hidden |
| Omit it | Attack lands cleanly; trust is lost when the reader finds it elsewhere |

### Label Separation

Whenever two true statements about a system appear to contradict each other, write the sentence that explains they measure different things. Examples:
- "Beta — Not Production Ready" (API stability) vs "A+" (engineering quality rubric): *"Two labels, two independent measurement axes."*
- "Single-project observation" vs "manifest-backed": *"Different provenance levels for different claims — each stated at its own confidence level."*

Never assume a reader will infer the distinction themselves.

### The Fabrication Ceiling

Score improvement under adversarial review is bounded by what cannot be fabricated. The correct response to an unfillable gap (e.g., absence of a second independent adopter) is to name it honestly, not to paper over it with vague language. An honest ceiling is more credible than an inflated claim.

## Examples

### Example 1: Submission Field 3 opening (2026-07-18)

**Before (attacked):**
> "…two independent, measured mechanisms — and one that cannot be measured but changes everything."

A hostile judge reads: *you are asking me to score you on a claim you admit you cannot substantiate.*

**After (pre-empted):**
> "…three measured, manifest-backed mechanisms — and the compounding value those savings make possible."

### Example 2: N=10/19 statistics (2026-07-18)

**Before (attacked):**
> "51% mean token saving (N=10 well-formed summary pairs out of 19 total measured…)"

A hostile judge reads: *you cherry-picked half your dataset.*

**After (pre-empted):**
> "KB artefacts fall into two structurally distinct categories: compact summaries (N=10)… and comprehensive guides and research reports (N=9)… Only the compact-summary category is the right unit of measurement… The N=9 comprehensive artefacts are not excluded to flatter the number — they are excluded because re-derivation saving is not what they are for."

## Related Documents

- [KB Document Types](./kb-document-types.md)
- [Iterative Audit Methodology](./iterative-audit-methodology.md)
- [Repo Hygiene Rules](./repo-hygiene-rules.md)

---
*Last Updated: 2026-07-18*
*Category: Concept*
