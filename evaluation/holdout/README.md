# Held-out validation corpus (corpus B)

This directory freezes a **hold-out slice** of the real repo prose corpus, used
only to verify that a savings headline measured on the primary corpus (corpus A —
`docs/**` and `examples/*/docs/knowledge-base/**`, minus this slice) **reproduces**
on prose the number was not measured against (C4 / ATK-GATE-01).

## Why an i.i.d. slice, not hand-written prose

Optimizer compression is strongly composition-dependent: real documents range from
near-0% to ~40%, so two *independently sourced* corpora differ by 10–15 percentage
points just from genre variation — a tight reproduction band would false-positive
on an honest number. A hold-out drawn as an **i.i.d. subset of the same corpus**
removes that confound: under an honest full corpus, A and B are samples of one
distribution and their means agree within sampling error (measured **0.02pp** at a
15% split). A **cherry-picked** A (the most compressible documents) diverges from
the representative B — measured **8.84pp** — and a fabrication-scale figure diverges
by tens of points. The gate (`src.validation.holdout_ok`,
`MAX_HOLDOUT_DIVERGENCE_PP = 5.0`) sits an order of magnitude above the honest noise
and well below the cherry-pick signal.

## What is here

- `holdout-manifest.json` — the **frozen** list of hold-out relative paths, selected
  once by `sha256(path) % 100 < 15` against the corpus at `frozen_at` and then fixed.

`src.validation.load_repo_prose` excludes exactly these paths (so A and B are
disjoint); `src.validation.load_holdout` loads exactly these paths.

## Freeze discipline

- The manifest is **frozen**: do not add or remove paths to move a number. A
  cherry-picked A cannot pre-arrange B only because B was fixed independently, in
  advance. New documents added to the repo enter corpus A, never this frozen B.
- If the slice must be refreshed (e.g. too many of its paths were renamed away),
  regenerate it in **its own PR** with a rationale — never in the same PR as a
  published number (the gate-integrity check enforces that separation).
