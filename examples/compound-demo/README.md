# Compound demo — write → retrieve → compound (D3 / MEM-13)

The reproducible "prove it compounds" proof: what one analysis session learns is
retrievable in the next, instead of being re-derived. This **replaces the retracted
anecdote** (`evaluation/live-example-hcd-analysis.md`, kept frozen with its
retraction banner) with a manifest-backed, CI-exercised demo.

## What it does

```
python examples/compound-demo/compound_demo.py      # run from the repo root
```

1. **Session 1 (write).** Analyzes the pinned fixture repo under
   [`fixture-repo/`](fixture-repo/) with `bob-optimize analyze`'s delegation
   pipeline, writing signed `generated` KB docs (one per agent) into a fresh KB.
2. **Session 2 (retrieve).** Builds an index over that KB and issues a query about
   the fixture's subject matter; the query **must** retrieve one of session 1's
   findings.
3. Emits a **manifest** — session-1 output ids, index chunk count, session-2
   retrieved ids, the matched intersection, and the code SHA — and exits non-zero if
   session 2 surfaces no session-1 finding.

The fixture is vendored **inside the repo**, so path containment holds without
`--allow-external`; the general "analyze a repo outside the working directory" case
is tracked separately (D3 part 1). The fixture is **frozen** — do not edit it to
change a demo result.

## Why it is honest

The demo KB contains only session-1's output, so the round-trip (session 1 wrote it,
session 2 retrieved it) is what is being proven — not retrieval precision, which is
measured separately and manifest-backed (`evaluation/results/retrieval-2026-07-19/`,
CLM-06, p@3 = 0.84, no net lift over keyword). The compounding claim here is the
round-trip itself, demonstrated reproducibly rather than asserted.

## Test

`tests/e2e/test_compound_demo.py` runs the two-session loop end to end and asserts
session 2 retrieves a session-1 finding (RED→GREEN: if session 2 reads a different KB
than session 1 wrote to, the round-trip breaks and the test fails).
