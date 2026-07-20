# A/B developer-velocity measurement

The one honest before/after that every review asked for. Same rigour as the 20%
compression harness; produces a manifest-backed **median wall-clock and Bobcoin
reduction per iteration cycle**, single-project, paired A/B.

See [`AB-velocity-measurement-protocol.md`](../../2026_IBMer_Watsonx_Challenge/AB-velocity-measurement-protocol.md)
for the full protocol. This directory holds the frozen inputs; the analysis
instrument is [`src/velocity.py`](../../src/velocity.py).

## Files

| File | Role |
|---|---|
| `tasks.json` | **Frozen** pre-registered task set (freeze = committed). Do not edit after timing begins. |
| `measurements.example.json` | Schema template with **synthetic** values — proves the pipeline; never cite it. |
| `measurements.<date>.json` | *You create this* — the real recorded A/B readings. |

## How to run it (the human-in-the-loop step)

The harness does **not** invent timings. You run each of the 8 tasks on Bob
under both conditions and record the readings:

1. **Freeze** `tasks.json` (already committed). Do not change it afterward.
2. For each task, follow its pre-recorded `order` (counterbalance):
   - **A — cold / no KB:** fresh Bob session, KB not loaded. Time to the
     done-criterion; record the Bobcoin/token readout; mark quality pass/fail.
   - **B — with KB:** Bob session with the Mnemox mode loaded. Same task, same
     done-criterion. Record the same three numbers.
3. **No-leakage guard:** confirm the KB digest B used was written by prior/general
   sessions, not seeded with this task's answer. If it was seeded, the task is invalid.
4. **Quality gate:** if B's answer is worse/incomplete vs. A, mark `quality_pass: false`
   — a faster-but-worse result is not a win and is excluded from the headline.
5. Put the readings in `measurements.<date>.json` (see the example schema).
6. Compute the report + manifest:

```bash
.venv/bin/python -m src.velocity \
  --tasks evaluation/velocity/tasks.json \
  --measurements evaluation/velocity/measurements.<date>.json \
  --out evaluation/results/velocity-ab-<date>/
```

The harness **refuses to emit a headline below 5 valid paired tasks**, reports
every task (including ties and quality-gate exclusions), and writes a manifest —
so the number is citeable exactly like the 20%.

## What you may then claim (and not)

- **Claim:** the measured median reduction, with **N + CI + "single-project, paired A/B."**
- **Do not:** annualise, generalise across teams, or blend it with the 20%/cache numbers.
- **Then:** replace the extrapolated ≈60% in Field 3 and on pitch page 2 with the
  measured number and cite `evaluation/results/velocity-ab-<date>/manifest.json`.
