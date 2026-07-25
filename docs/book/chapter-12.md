# Chapter 12: The Honesty Gates

> **Live document.** This chapter is part of [Mnemox — The Complete Guide](table-of-contents.md). Numbers here cite a manifest or say they do not; [`STATUS.md`](../../STATUS.md) is the single home for maturity, coverage and test counts. Chapters 1–9 were written mid-2026 — where a chapter predates a subsystem, chapters 10–12 cover it.

*Added 2026-07-25. This chapter exists because of what an audit found in the gates
described by chapters 7 and 9.*

This project's stated differentiator is not its compression ratio. It is that the
compression ratio is one you can check. Chapter 9 makes that claim; this chapter
describes the machinery behind it, and then describes where that machinery failed —
which is the more useful half.

## 12.1 Why mechanical honesty at all

The founding incident is on the record: a **fabricated, since-retracted** headline figure of **68.96% token savings**,
with a confidence interval and a "VALIDATED" label, produced by a simulation that never
invoked the optimizer. It was not caught by review. It was caught by someone reading the
script.

The response was structural rather than cultural. Culture — "we will be careful" — does
not survive a tired week. So:

- Every published savings or cost number must cite a **manifest**: data hash, code SHA,
  config, seed, library versions, `git_dirty` flag.
- Each mechanism is measured and reported **separately**. Compression, cache
  recompute-avoidance and truncation are never summed, because summing them is precisely
  how 68.96% was manufactured.
- The fabricated report is **still in the tree**, at
  `evaluation/results/validation_report.json`, carrying an in-band `_RETRACTED_` marker.
  Deleting it would have been tidier and less honest.

## 12.2 The gates

Ten checks run in CI. Each is a script that a human can read.

| Gate | What it enforces |
|---|---|
| `check_savings_claims.py` | a savings/cost number cites a manifest, or is marked retracted |
| `check_metric_claims.py` | a retrieval metric cites a report |
| `check_status_consistency.py` | live docs agree with the single homes; grades carry provenance |
| `check_value_homes.py` | a value declared in two places has one source |
| `check_gate_integrity.py` | one PR may not both weaken a gate and plant a claim |
| `check_md_links.py` | every relative link resolves against the **git index**, case-sensitively |
| `check_architecture_freshness.py` | every `src/` module is named by ARCHITECTURE.md or an ADR |
| `check_layering.py` | `src/` never imports from `scripts/` |
| `check_doc_freshness.py` | a doc asserting a date is not older than its own newest commit |
| `validate-kb.sh` | KB cross-references resolve |

Two design choices are worth naming:

**Every gate ships a self-test that proves it can fail.** A gate that has never been
demonstrated to go red is indistinguishable from a gate that cannot. The CI job runs
`--selftest` *before* the real scan.

**Gate integrity is a structural answer to bus-factor 1.** One person writing the code,
the gates that check the code, and the claims the gates guard is a closed loop. Absent a
second reviewer, `check_gate_integrity.py` mechanically forbids a single PR from touching
both a gate definition and a claim surface. It is disclosed in `SECURITY.md` as exactly
what it is: an honest substitute for a human, not an equal of one.

## 12.3 Where the gates failed

A full-project audit on 2026-07-25 found that the gates were passing while several live
overclaims shipped. Not because the gates were absent — because each had a **blind spot
shaped like the thing it was written to catch**.

- **The grade gate** matched only the bold `**<letter> (n.nn/4.30)**` form. So the
  README's `2.9 → 3.8 → 4.2/5` — a *projected* target republished as an achieved
  independent verdict — was invisible, as was an unbolded `A+ (4.30/4.30)` in the docs
  index. The gate could not see either of the two overclaims actually shipping.
- **The metric gate** required a literal `%`. Every retrieval figure in the repository is
  a ratio (`p@3 = 0.84`; manifest: evaluation/results/retrieval-2026-07-19/report.json),
  so the gate guarding retrieval overclaims had never seen a real
  one. Worse: a passing test *asserted* this was correct — "a decimal p@3 is a measured
  value, not a percentage overclaim". The blind spot was pinned in place by a green test.
- **Gate integrity** did not treat `.github/workflows/**` as a gate definition. A gate is
  only a gate if CI invokes it, so a PR could delete a check's CI step and plant a claim
  together and pass — the exact attack, through an unwatched path. It was not theoretical:
  nine DoS-hardening regression tests had been running in **no CI job at all**.
- **The link checker** covered `docs/knowledge-base/` — about 4% of the Markdown — and
  checked the filesystem rather than the git index. On a case-insensitive macOS
  filesystem that made ~110 broken references invisible locally while they 404'd on
  GitHub.
- **The savings gate** documented itself as "tree-wide" while never scanning
  `2026_IBMer_Watsonx_Challenge/` — the outward-facing pack written for external judges,
  the single most consequential surface in the repository.

## 12.4 The lesson, generalised

Each blind spot has the same shape: **the gate encoded the last incident rather than the
general class.**

The grade regex was written to catch the withdrawn A+, and it caught exactly that,
forever. The metric gate was written after a `88%` overclaim, so it required a `%`. The
integrity check was written about scripts, so it watched scripts.

A gate that matches the shape of the last failure is a gate you have to re-earn on every
new failure — and it will read green the whole time. The generalisation is uncomfortable
because narrow rules have fewer false positives, and false positives are what erode trust
in a gate. The resolution used here: widen the pattern, then require that provenance can
be satisfied *several honest ways* — cite a manifest, name the on-file verdict, mark it
self-assessed, or label it a projection — so that the widened rule has an easy correct
answer rather than only a hard one.

## 12.5 What still is not gated

Named, because an inventory of your own blind spots is the only defence against the next
one:

- **Prose quality.** The freshness gate checks that a module is *named* somewhere, not
  that the description is any good.
- **Whether a manifest's numbers are right.** The gate checks a citation exists and is
  within tolerance of the cited file; it cannot tell you the run was well-designed.
- **Prose currency beyond the date line.** `check_doc_freshness.py` now ties a declared
  date to the file's newest commit — but a doc can be touched without its content being
  re-checked, so a fresh date is evidence of an edit, not of accuracy.
- **Human review.** Gate integrity is a substitute for a second reviewer. It is a good
  substitute. It is still a substitute.

---

**Back to:** [Table of Contents](table-of-contents.md)
