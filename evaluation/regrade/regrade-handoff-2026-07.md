---
title: "Independent Re-Grade — Grader Handoff"
kit: evaluation/regrade/regrade-kit-2026-07.md
slot: evaluation/regrade/verdict-TEMPLATE.md
status: handoff instructions — read before filling a verdict
note: This file is NOT a verdict and NOT named verdict-*.md by design; it is assembled by the remediation lineage and therefore cannot itself discharge R14.
---

# Independent Re-Grade — Grader Handoff (2026-07)

You have been handed Mnemox's re-grade **kit**
([`regrade-kit-2026-07.md`](regrade-kit-2026-07.md)). This document tells you *how*
to produce the verdict. The rubric, finding register, and evidence manifests live
in the kit; the slot you fill is [`verdict-TEMPLATE.md`](verdict-TEMPLATE.md) →
`verdict-<date>.md`.

> **This handoff was assembled by the remediation lineage. It is not a grade and it
> cannot grade.** Its only job is to point an independent grader at the right tree,
> the right evidence, and the right slot.

## 0. Are you eligible to grade? (R14 independence)

Fill the verdict **only** if you are:

- a **human third party**, or
- an **external agentic process with a distinct model/lineage and no remediation
  involvement**.

You are **not** eligible if you are the Claude Code session/lineage that performed
the Wave-0/1/2/3 remediation, or a sub-agent it spawned — a verdict from that
lineage does **not** discharge R14 no matter how it scores. (This is the same rule
stated in kit §0 and the template header.)

## 1. What to grade — the CURRENT HEAD, not the kit's baseline

The kit's finding register is pinned at `6d0711d`. **The tree has advanced since**;
grade the current `HEAD` and fold these into your reading:

| Commit | Change | Where verified |
|---|---|---|
| `37c1ebc` | A7 input-bound caps + A8 scale-regression gate | `wave3-status.md` §3 |
| `0e97f6e` | ATK-MEM-02 closed — forged `trust_tier: verified` no longer trusted on read | `wave3-status.md` §4 |
| `b33f4d1` | E2 exit map (`wave3-status.md`) | this repo |

Also read [`../../docs/project-management/plans/wave3-status.md`](../../docs/project-management/plans/wave3-status.md):
its §2 records **open post-verification residuals** (R-1 L2-cache MEDIUMs; R-2/R-3
NEW-1..4) that are *tracked, not closed*. A defensible score must account for them.

## 2. The grading brief (adversarial, refute-by-default)

1. Score **both** rubrics from the kit — Tier-1 vendor (§4a) and watsonx-jury (§4b),
   each `/5`. For every dimension, cite a `path:line` or a manifest that justifies
   the score. A score without evidence is not a score.
2. **Default to skeptical.** Treat every "closed" disposition in kit §2 /
   `wave3-status.md` §2 as a *claim to re-test*, not a fact. Prefer re-running the
   check (§3) over trusting the register.
3. Independently confirm the finding-register: is every Critical/High closed-or-
   accepted as claimed? Record dissent in the verdict's Dissent section.
4. Weigh the open residuals (§1) and the standing partials (ATK-MEM-03, MEM-02/03)
   against the institutional bar.
5. Produce a single institutional verdict (`GO | NO-GO | CONDITIONAL`) with a
   one-line rationale, plus the two `/5` overalls.

## 3. Re-run these — reproduce, don't trust

```bash
# suite (ex load/perf) + coverage floors
.venv/bin/python -m pytest --ignore=tests/load --ignore=tests/performance
.venv/bin/python scripts/check_coverage_by_package.py coverage.json   # after --cov run

# the two evidence manifests behind the headline numbers
.venv/bin/python -m src.validation                 # validation: ~20% mean, N=183, null PASS
.venv/bin/python -m pytest tests/retrieval/test_golden_set.py   # retrieval: p@3=0.84, no lift

# honesty + integrity gates (all must exit 0)
for g in check_savings_claims check_status_consistency check_value_homes check_metric_claims; do
  .venv/bin/python scripts/$g.py; done
bash scripts/validate-kb.sh

# the new WS-A scale gate (A8) and its self-test
.venv/bin/python -m pytest tests/performance/test_scale_invariants.py tests/gates/test_scale_gate_selftest.py

# ATK-MEM-02 is really enforced (mutation): revert the read-path guard, the forged
# test must go red
#   sed -i 's/self._tier_grants_trust(tier, content)/tier in TRUSTED_TIERS/' src/tools/kb_query.py
#   pytest tests/security/test_trust_tier.py::test_forged_verified_tier_is_not_trusted   # expect FAIL
```

## 4. Prior independent assessments — inputs to weigh, not verdicts

Record these in your reasoning; do **not** copy any as your score.

- **Counter-audit, 2026-07-19:** 2.9/5.
- **Last graded institutional verdict, 2026-07-14:** NO-GO, 3.46/4.30.
- **Cowork re-audit, 2026-07-20:** ≈3.8/5, offered by its author as *one input* to
  this re-grade. Caveat: it graded the **pre-A7/A8 tree** (`07ad245`) and its GO
  condition ("zero open Critical/High") is now partly met — ATK-MEM-02, which it
  raised, is closed at `0e97f6e`. Verify against current HEAD before leaning on it.

## 5. Where to write the verdict

Copy [`verdict-TEMPLATE.md`](verdict-TEMPLATE.md) → `verdict-<date>.md`, fill the
provenance block (`grader:` / `method:` / `date:` / `commit:` /
`remediation-involvement: none` / `model-lineage:`), the two score tables, and the
overall verdict. Commit it. **Only then** may `STATUS.md` cite it — the C5
grade-provenance gate blocks a live grade until a provenanced `verdict-<date>.md`
exists (`tests/gates/test_regrade_kit.py::test_status_cites_regrade_when_present`).

Until that file lands, Mnemox has **no current independent grade** — which is the
honest, gate-enforced state today.
