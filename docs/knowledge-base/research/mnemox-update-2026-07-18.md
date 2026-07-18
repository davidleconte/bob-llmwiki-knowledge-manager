---
title: "Mnemox Update — 2026-07-18"
category: research
tags: [mnemox, lessons-learned]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T19:27:59Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
550ad48 docs: institutional Tier-1 alignment — casing, stale metrics, broken hrefs
ea8084e docs: kebab-case link fixes + institutional audit corrections
d7fd046 ci: autosave benchmarks on PRs; enforce regression compare only on main
499f987 style: ruff format three test files
b8b35bb docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 5) + fix mnemox-lessons.sh frontmatter template
80ddbd1 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 14 |
| Guides     | 26 |
| References | 4 |
| Research   | 60 |
| **Total**  | **105** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/adversarial-audit-embeddings-chunker-2026-07-17.md`
- `docs/knowledge-base/research/adversarial-review-round1-2026-07-13.md`
- `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md`
- `docs/knowledge-base/research/audit-2026-07-13-institutional.md`
- `docs/knowledge-base/research/audit-2026-07-14-post-remediation.md`
- `docs/knowledge-base/research/audit-2026-07-14-signoff.md`
- `docs/knowledge-base/research/bobcoin-savings-analysis-2026-07-14.md`
- `docs/knowledge-base/research/cache-race-fix-lessons-2026-07.md`
- `docs/knowledge-base/research/cache-race-fix-round5-2026-07.md`
- `docs/knowledge-base/research/code-metrics-2026-07-12.md`
- `docs/knowledge-base/research/code-metrics-2026-07-13.md`
- `docs/knowledge-base/research/code-metrics-2026-07-18.md`
- `docs/knowledge-base/research/codebase-analysis-2026-07-14.md`
- `docs/knowledge-base/research/cost-tracking-lessons-learned.md`
- `docs/knowledge-base/research/coverage-measurement-2026-07-13.md`
- `docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-12.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-13.md`
- `docs/knowledge-base/research/external-audit-2026-07-12.md`
- `docs/knowledge-base/research/full-codebase-review-2026-07-14.md`
- `docs/knowledge-base/research/full-technical-design-retro-2026-07.md`
- `docs/knowledge-base/research/git-analysis-2026-07-12.md`
- `docs/knowledge-base/research/git-analysis-2026-07-13.md`
- `docs/knowledge-base/research/graph-validation-2026-07-17.md`
- `docs/knowledge-base/research/iterative-audit-lessons-2026-07.md`
- `docs/knowledge-base/research/kb-mode-switch-lessons-2026-07.md`
- `docs/knowledge-base/research/kb-query-ab-validation-2026-07.md`
- `docs/knowledge-base/research/kb-tos-integration-feasibility-2026-07-14.md`
- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`
- `docs/knowledge-base/research/performance-benchmarks.md`
- `docs/knowledge-base/research/phase1-lessons-learned-2026-07-13.md`
- `docs/knowledge-base/research/phase2-completion-summary.md`
- `docs/knowledge-base/research/phase2-concurrency-test-results.md`
- `docs/knowledge-base/research/phase2-health-checks-complete.md`
- `docs/knowledge-base/research/phase2-lessons-learned-2026-07-13.md`
- `docs/knowledge-base/research/phase2-performance-baseline-analysis.md`
- `docs/knowledge-base/research/phase2-performance-baseline-results.md`
- `docs/knowledge-base/research/phase2-thread-safety-fixes-complete.md`
- `docs/knowledge-base/research/phase2-vocabulary-drift-implementation.md`
- `docs/knowledge-base/research/phase3-additional-work-lessons-learned.md`
- `docs/knowledge-base/research/phase3-day1-2-validation-framework.md`
- `docs/knowledge-base/research/phase3-day3-4-parallel-work.md`
- `docs/knowledge-base/research/quality-gate-status-2026-07-18.md`
- `docs/knowledge-base/research/readme-critical-analysis-2026-07-14.md`
- `docs/knowledge-base/research/repo-hygiene-lessons-2026-07.md`
- `docs/knowledge-base/research/repo-scan-2026-07-12.md`
- `docs/knowledge-base/research/repo-scan-2026-07-13.md`
- `docs/knowledge-base/research/repo-scan-2026-07-18.md`
- `docs/knowledge-base/research/repository-improvement-plan.md`
- `docs/knowledge-base/research/security-scan-2026-07-12.md`
- `docs/knowledge-base/research/security-scan-2026-07-13.md`
- `docs/knowledge-base/research/senior-expert-institutional-audit-2026-07-14.md`
- `docs/knowledge-base/research/test-coverage-2026-07-12.md`
- `docs/knowledge-base/research/test-coverage-2026-07-13.md`

## Findings

### Finding 1 — Case-sensitive hrefs are a silent Linux CI failure vector

The `fix-multilevel-cache-race` → `main` merge and the subsequent Tier-1 alignment
pass (`550ad48`) together corrected **~40 broken hrefs** across 15 active docs. The
root pattern: macOS HFS+ resolves `QUICK_START.md`, `quick-start.md`, `SLA.md`,
`sla.md`, `architecture.md`, and `ARCHITECTURE.md` identically, masking link
hygiene errors that break on Linux runners.

**Lesson:** After any file rename, immediately grep all `.md` files for the old
name (both href target and display text). Do not rely on local link checkers — they
lie on macOS. The CI link-check job is the only ground truth.

**Key renames that created drift:**
| Old name | New on-disk name |
|---|---|
| `docs/ARCHITECTURE.md` | `docs/kb-manager/ARCHITECTURE.md` |
| `docs/QUICK_START.md` | `docs/quick-start.md` |
| `docs/SLA.md` → | `docs/sla.md` |

---

### Finding 2 — Stale snapshot numbers need a single-home enforcement pattern

`STATUS.md` § Terminology guardrail had `89.1% / 1053+ / 25 skipped / 2026-07-17`
while the authoritative quality-gate snapshot (`quality-gate-status-2026-07-18.md`)
recorded `89.82% / 1112 / 23 / 2026-07-18`. The two drifted because the Terminology
guardrail is prose, not a machine-readable value, so no CI check caught it.

**Lesson:** Point-in-time snapshot prose in `STATUS.md` must be updated atomically
with the quality-gate research doc that defines the numbers. The safest pattern is:
update both files in a single commit and include the old→new value in the commit
message (e.g. `"1053+ → 1112"`). `docs/knowledge-base/index.md` should always
defer to `STATUS.md` with a link rather than repeating the number.

---

### Finding 3 — `mnemox --quick` is the right post-merge ceremony

Full analysis (`scripts/run-full-analysis.sh`) takes ~90 s and re-derives facts
already known. For post-merge hygiene passes where the code is stable, `--quick`
(lessons + graph rebuild + commit) takes ~25 s and produces a dated KB snapshot
without redundant churn. The graph rebuild (`117 nodes / 4351 edges`) is mandatory
after any KB write — skipping it leaves new documents invisible to `bob-optimize
kb-search`.

**Pattern to follow:** `mnemox --quick` after every doc-alignment commit;
`mnemox --full` only after a substantive code change or at the start of a new
sprint.

---

### Finding 4 — Supersession banners on stale audit docs prevent grade confusion

Before `ea8084e`, three research docs
(`senior-expert-institutional-audit-2026-07-14.md`, `audit-2026-07-14-signoff.md`,
`readme-critical-analysis-2026-07-14.md`) showed C+/B+/A− grades contradicting
the current A+ (4.30/4.30). Any reader landing on those docs would conclude the
project is failing.

**Pattern:** A `> ⚠️ SUPERSEDED` callout block at the top of dated audit docs,
with an explicit forward pointer to `STATUS.md`, is the minimum required for
Tier-1 compliance. Frontmatter `status: superseded` alone is not enough — it is
not rendered visually in most Markdown renderers.

---

### Finding 5 — CI benchmark spurious failures need a structural fix, not a threshold tweak

Three benchmark tests (`test_l2_lookup_medium`, `test_count_large_text`,
`test_optimize_already_optimal`) exceeded the 50%-above-median threshold on GitHub
Actions ubuntu-latest 2-vCPU VMs — not because the code regressed, but because
shared CI runners introduce ±50% timing variance. The fix (`d7fd046`) was
architectural: **save benchmark results always, compare-and-fail only on `main`**.
PRs get the data trend without false-positive blocks.

**Lesson:** Benchmark CI gates must account for the execution environment. Flaky
time-based gates erode trust faster than they catch regressions. The correct gate
is trend-based (comparing median over N recent runs) rather than absolute-threshold.

---

## Conclusions

### Recommendations

1. **Add a `make link-check` target** (or equivalent `grep`-based CI step) that
   fails on any `QUICK_START.md`, `SLA.md`, or lowercase `architecture.md` href in
   active docs — prevents the Tier-1 casing drift from recurring silently.

2. **Establish a "metrics snapshot protocol"**: when a quality-gate research doc is
   filed, open `STATUS.md` in the same commit and update the Terminology guardrail
   numbers. Make this a checklist item in the PR template.

3. **Next KB gap to close**: `docs/INDEX.md` (at repo root, not KB index) is not
   tracked in the KB index (`docs/knowledge-base/index.md`). It shows as an orphan
   in validate-kb output. Either add it or exclude it from the orphan check.

### Next Steps

- [ ] Add a CI lint step: `grep -rn "QUICK_START\|SLA\.md\|/architecture\.md" docs/ README.md` → fail on match
- [ ] Update PR template to include: "STATUS.md Terminology guardrail updated if test count changed?"
- [ ] Resolve `docs/INDEX.md` orphan warning (add to KB index or add to validate-kb exclusion list)
- [ ] Confirm CI green on `main` at `550ad48` before declaring merge done

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
