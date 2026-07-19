---
title: Mnemox Engineering-Soundness — Executive One-Pager
category: consulting
tags: [engineering-soundness, executive-summary, scorecard, recommendations]
created: 2026-07-19
updated: 2026-07-19
status: active
trust_tier: verified
provenance: One-page executive summary of the engineering-soundness review. Numbers cited to their single home (STATUS.md for maturity; evaluation/results/validation-2026-07-14/manifest.json for savings; the frozen evidence snapshot for the finding register).
---

# Mnemox — Engineering-Soundness, in One Page

## The situation, in four sentences (SCQA)

- **Situation.** Mnemox gives IBM Bob a git-native memory and a token optimiser, and is unusually honest — it caught, **retracted**, and re-measured a fabricated headline savings number (the real, manifest-backed figure lives in `evaluation/results/validation-2026-07-14/manifest.json`). `STATUS.md` says "Beta — Not Production Ready" with a self-assessed **A+ (4.30/4.30)**.
- **Complication.** Two independent 2026-07-19 audits find the A+ unearned: the validated retrieval stack was never wired to production, `optimize()` could return an empty string, and the honesty gates were gameable (counter-audit **2.9/5**; last independent verdict **NO-GO 3.46/4.3**).
- **Question.** Is Mnemox engineering-sound, and what makes it so?
- **Answer.** **The status is honest; the grade is not earned yet — but the gap is wiring and proof, not new invention. The fixes for all three headline problems already exist in the working tree, uncommitted.** A three-horizon programme lifts a defensible engineering-soundness score from ~2.9/5 to ~4.2/5, and re-grading in public strengthens the honesty brand.

## Reconciled scorecard (the A+ and the 2.9/5 grade different things)

The A+ grades **artifact completeness**; the 2.9/5 grades **functional integration**. Engineering soundness weights integration:

| Branch | Today | Target (post H1+H2) |
|---|---|---|
| A Product correctness | 2.5 / 5 | 4.0 |
| B Memory & retrieval | 2.0 / 5 | 4.5 |
| C KB integrity | 2.5 / 5 | 4.0 |
| D Claims & governance | 3.5 / 5 | 4.5 |
| E Platform (tests/CI/security) | 4.0 / 5 | 4.5 |
| **Overall** | **~2.9 / 5** | **~4.2 / 5** |

*(Independent engineering-soundness scores, distinct from the STATUS.md institutional grade.)*

## Top-5 recommendations (ranked by impact × effort)

1. **R1 — Commit + prove the retrieval wiring.** The validated stack is injected on `kb-search` (`src/cli.py:344-388`) but uncommitted; prove it red-on-unfixed / green-on-fixed and land it. Highest ROI.
2. **R2 — Commit the never-empty optimiser** (`src/optimizer/prompt_optimizer.py:242-255`) with its regression test — closes the empty-output defect.
3. **R3 — Commit the `#slug` read-path fix** (`src/tools/kb_query.py:327-335`) so index candidates are not silently discarded.
4. **R4 — Green the tree against its own gates:** fix the 5 savings-gate surfaces (incl. an un-bannered "68.96%" — retracted — in `phase6-real-world-validation-plan.md`), the `validate-kb.sh` root-hygiene failure, the casing/reference debt, and the two failing tests.
5. **R5 — Make precision provable, then re-grade:** commit the p@3 golden set as a manifest-backed number and commission a genuinely independent re-grade; retire the self-A+ in favour of that verdict.

## The honesty framing

*The status was true; we are making the grade true too.* Re-grading in public — after the wiring lands and the gates bite — is the differentiator, not a retreat.

**Canonical pointers:** maturity → `STATUS.md`; validated savings → `evaluation/results/validation-2026-07-14/manifest.json`; full finding register → [`docs/knowledge-base/research/engineering-soundness-audit-2026-07-19.md`](../knowledge-base/research/engineering-soundness-audit-2026-07-19.md); full narrative → [`engineering-soundness-review-2026-07-19.md`](engineering-soundness-review-2026-07-19.md).
