---
title: "Independent Re-Grade Verdict — TEMPLATE"
kit: evaluation/regrade/regrade-kit-2026-07.md
status: TEMPLATE — unfilled slot; copy to verdict-YYYY-MM-DD.md and fill
---

# Independent Re-Grade Verdict — TEMPLATE

> **This is the verdict slot, not a verdict.** Copy this file to
> `evaluation/regrade/verdict-YYYY-MM-DD.md`, fill every cell, and commit it. Do **not**
> edit this TEMPLATE in place and do **not** put a grade in the TEMPLATE. The rubric,
> dimensions, finding register, and evidence manifests live in
> [`regrade-kit-2026-07.md`](regrade-kit-2026-07.md) — this slot only records *who*
> graded, *how*, and *what they scored*.
>
> **Who may fill it (R14 / same-lineage rule).** A genuinely independent grader only: a
> human third party, **or** an external agentic process with a *distinct model/lineage*
> and **no remediation involvement**. A verdict produced by the session/lineage that did
> the Wave-1/2/3 remediation does **not** discharge R14, no matter how it scores.

## Provenance  (required — the C5 grade-provenance gate keys on `grader:` + this artifact)

```
grader:                  <name, panel, or external agent identity>
method:                  <e.g. dual-rubric, read the kit + re-ran the two manifests>
date:                    <YYYY-MM-DD>
commit:                  <the repo commit SHA that was graded>
remediation-involvement: none        # MUST be none; otherwise this does not discharge R14
model-lineage:           <if agentic: model + confirmation it is distinct from the
                          remediation lineage (this repo was remediated by Claude Opus 4.x)>
```

## Scores — Tier-1 vendor scorecard  (scale /5)

Reproduce the worksheet rows from **kit §4a** and fill the score + evidence cells. One
row per dimension; cite the `path:line` or manifest that justifies each score.

| Dimension | Score /5 | Evidence / rationale |
|-----------|:--------:|----------------------|
| …         |          |                      |

**Tier-1 vendor overall:** `<n.n>/5`

## Scores — watsonx-jury scorecard  (scale /5)

Reproduce the worksheet rows from **kit §4b** and fill the score + evidence cells.

| Dimension | Score /5 | Evidence / rationale |
|-----------|:--------:|----------------------|
| …         |          |                      |

**watsonx-jury overall:** `<n.n>/5`

## Overall verdict

- **Institutional-bar verdict:** `<GO | NO-GO | CONDITIONAL>` — one-line rationale.
- **Letter grade (optional, /4.30 scale):** `<letter> (<n.nn>/4.30)` — leave in prose,
  not bolded, unless you intend it to become the live grade cited by `STATUS.md`.
- **Finding-register check:** confirm every Critical/High in kit §2 is closed-or-accepted
  as claimed, or record dissent here.

## Dissent / caveats

<free text — anything the scores don't capture; disagreements with the register's dispositions>

---
*Filed verdicts must be named `verdict-YYYY-MM-DD.md`. Once one exists, update `STATUS.md`
to cite it — that is the only path by which a live grade may reappear (C5 / CLM-02).*
