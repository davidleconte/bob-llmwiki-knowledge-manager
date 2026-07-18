---
title: "Mnemox Update — 2026-07-18"
category: research
tags: [mnemox, update, lessons-learned]
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
- Last mnemox run: 2026-07-18T18:23:47Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
93eea94 fix(submission): apply jury-1 + jury-2 recommendations
0bdefe9 feat(validate-kb): orphan + frontmatter checks; README --full one-liner
cf70ffe docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 2)
4e80729 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 13 |
| Guides     | 26 |
| References | 4 |
| Research   | 59 |
| **Total**  | **103** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`

## Findings

### 1. Adversarial review closes more gaps than friendly review

Two jury passes over the same submission (`93eea94`) produced fundamentally different findings. The friendly jury identified framing improvements (+0.5 pts potential). The adversarial jury identified structural vulnerabilities — an opening sentence that admitted the best impact was unmeasurable, a stat buried in a parenthetical that looked like cherry-picking, a graph feature that read as a dead end, and a contradiction between "A+" and "Beta" labels. The adversarial pass raised the score from 3.88 to 4.50 post-fix — a 0.62 gain. The pattern: always run an adversarial pass on any deliverable before submission. The question is not "does this read well?" but "what is the strongest attack a hostile reader can make, and does the text pre-empt it?"

### 2. Pre-empting an attack is stronger than surviving it

Every adversarial finding was resolved not by adding defensive footnotes but by naming the vulnerability head-on in the primary text. "This is a single-IBMer proof of concept" is in paragraph 4 of Field 1 — not a disclaimer at the bottom. The N=10/19 split leads the 51% paragraph — not follows it. The graph layer "we built it, measured it, found neutral uplift, disabled it" is the main sentence — not a caveat. In each case, saying it first converts a potential attack into a transparency signal. The rule: if a hostile reader can find it, say it yourself first and frame it.

### 3. The "where is the AI?" objection must be answered in the opening field

An IBM AI challenge submission built on Bash scripts and Markdown files faces a structural credibility question: where is the AI? The answer — *the intelligence is IBM Bob's; Mnemox gives Bob the institutional memory it needs to apply that intelligence without repeating itself* — was present in the submission but appeared too late (Field 2 / paragraph 6 of Field 1). Moving it to Field 1 paragraph 4 means every judge who reads the submission in order gets the answer before they form the objection. Position determines whether a correct answer lands.

### 4. Separating labels that measure different things prevents compound confusion

"Beta — Not Production Ready" and "A+ (4.30/4.30)" coexist in the repo and, to an outside reader, they appear contradictory: how can something be both perfect and not ready? The fix — two labels, two independent measurement axes (API stability vs engineering-quality rubric) — required one sentence in Field 2. The principle: whenever two true statements about a system appear to contradict each other, write the sentence that explains they measure different things. Never assume a reader will infer the distinction themselves.

### 5. Jury score improvement is bounded by what cannot be fabricated

The adversarial score rose from 3.88 to 4.50 across all implemented fixes. The remaining 0.20-point gap is entirely the absence of a second independent adoption data point — a second IBMer, a second project, independently measured results. That cannot be manufactured and should not be. The right response to an unfillable gap is to name it honestly (done: "single-IBMer proof of concept") rather than to paper over it with vague language. The ceiling for an honest single-person proof of concept is approximately 4.5/5 — and that is a competitive score.

## Conclusions

### Recommendations

1. **Apply the adversarial-then-friendly review sequence to every future IBM submission or external deliverable** — run adversarial first (find all attacks), then friendly (confirm strengths), never only friendly.
2. **Add the "name your own vulnerabilities" pattern to the KB as a communication concept** — this session demonstrated it concretely across five independent examples.
3. **Index the 19 orphaned research snapshots from `run-full-analysis.sh`** — either add a bulk-index entry in `index.md` under a "Analysis Snapshots" heading or add a suppress-list to the orphan check for known bulk-generated files.

### Next Steps

- [ ] Add "Analysis Snapshots" section to `index.md` covering the 19 orphaned `run-full-analysis.sh` output files, or add a `# mnemox-orphan-exempt` frontmatter tag to suppress the warning for known bulk-generated docs
- [ ] Run `scripts/add-frontmatter.sh` to bulk-fix 43 docs with incomplete frontmatter (or triage: fix the 13 concepts + 4 references first, leave dated research notes for a batch pass)
- [ ] Write a KB concept document: "Adversarial Review Pattern" — the pre-emption rule, the two-jury sequence, the label-separation technique

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
