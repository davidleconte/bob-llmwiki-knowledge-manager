# A/B Velocity Measurement Protocol — one honest before/after

> **Why this exists.** Every independent assessment of the submission — a same-lineage self-score **and** a
> 3-juror clean-room panel — named the *same* single gap: no **controlled developer-velocity** number. The
> only reproducible figure is 20% token compression; the ≈60% hcd figure has no repo artifact and is a
> token→time extrapolation. This protocol produces **one** defensible before/after with the *same rigor as
> the 20% harness*, so Field 3 (and the pitch) can cite a measured velocity number instead of an estimate.
>
> **Cost to run:** ~4–8 hours for 8 tasks. Feasible before **July 22, 10:00 ET**.

Design in one line: **paired, counterbalanced, pre-registered, report-everything.** N = 8 tasks (5 minimum).

---

## 1 — Pre-register the tasks (BEFORE any timing)
Write a fixed list of **8 "Bob iteration cycle" tasks** — each a bounded piece of work on a complex module
that *requires re-establishing foundational context* first (e.g. "implement/answer `<specific question>`
about `<module>` to `<explicit done-criterion>`"). Commit the list + done-criteria to git and do **not**
change them afterward. Freezing the task set is what stops post-hoc cherry-picking.

## 2 — Two conditions, same task (paired)
Run **every** task under both:
- **A — cold / no KB:** fresh Bob session, KB **not** loaded; Bob re-derives context from source.
- **B — with KB:** Bob session with the Mnemox mode loaded; Bob retrieves context from the KB.

## 3 — The honesty guards (this is what makes the number defensible)
- **No leakage (the look-ahead analog).** The KB must be built from **prior/general** sessions, not seeded
  with the test tasks' answers. If a task's specific answer was written into the KB *for* this test, that
  task is invalid. Verify each digest B relies on is independent of the test question.
- **Counterbalance order.** Pre-record a random A-first/B-first order per task (coin flip). Prevents the
  second run winning just from learning effects.
- **Fixed done-criterion.** Decide "done" upfront per task so you cannot stop early on the favourable run.
- **Quality gate.** Verify B's answer is **at least as correct/complete** as A. *A faster-but-worse result
  is not a win* — record quality; flag/discard any B answer that is worse.
- **Report everything.** Log all 8 tasks, including ties and any where the KB didn't help (or hurt). No
  dropping unfavourable trials.

## 4 — Metrics (record per task × condition)
| Metric | How |
|---|---|
| **Wall-clock** min to done-criterion | stopwatch, Bob-in-the-loop time |
| **Bobcoin / token spend** | session cost readout |
| **Quality** | pass/fail vs done-criterion (+ note if B < A) |

## 5 — Analysis
- Per task: `Δtime = (A − B) / A`, `ΔBobcoin = (A − B) / A`.
- Report the **median + full distribution** (not just the mean), **N**, and a **bootstrap 95% CI** — the
  same method the 20% harness uses.
- Headline = the median % reduction with CI and N, e.g. *"median X% wall-clock and Y% Bobcoin reduction
  per iteration cycle (N=8 paired tasks, 95% CI […]), single-project."*

## 6 — Manifest (so it is citeable like the 20%)
Record task-list hash, KB commit SHA, date, Bob version/config, per-task order, and all raw numbers under
`evaluation/results/velocity-ab-<date>/`. Without the manifest it is an anecdote, not a measurement.

## 7 — What you may then claim (and not)
- **Claim:** the measured median reduction, with **N + CI + "single-project, paired A/B."**
- **Do not:** annualize, generalize across teams, or blend it with the 20%/cache numbers.
- **Then:** replace the extrapolated ≈60% in Field 3's hours and on pitch page 2 with the measured number,
  and cite the manifest. That single artifact is what moves Effectiveness 2→4 and the overall to finalist range.
