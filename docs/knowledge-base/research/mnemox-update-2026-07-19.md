---
title: "Mnemox Update — 2026-07-19"
category: research
tags: [mnemox, lessons-learned]
created: 2026-07-19
updated: 2026-07-19
status: active
---

# Mnemox Update — 2026-07-19

## Objective
Automated KB update run by `mnemox` on 2026-07-19.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T21:23:39Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
8977491 challenge: add 'why not RAG' answer to fields 2, 3, and pitch outline
0c8a5c1 fix(graph): rescue all 44 orphans — zero orphans on 108-node corpus
52435ef docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 7)
d5cf441 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 14 |
| Guides     | 26 |
| References | 4 |
| Research   | 64 |
| **Total**  | **109** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md`
- `docs/knowledge-base/research/audit-2026-07-13-institutional.md`
- `docs/knowledge-base/research/audit-2026-07-14-post-remediation.md`
- `docs/knowledge-base/research/cache-race-fix-round5-2026-07.md`
- `docs/knowledge-base/research/code-metrics-2026-07-12.md`
- `docs/knowledge-base/research/code-metrics-2026-07-13.md`
- `docs/knowledge-base/research/code-metrics-2026-07-18.md`
- `docs/knowledge-base/research/codebase-analysis-2026-07-14.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-12.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-13.md`
- `docs/knowledge-base/research/full-technical-design-retro-2026-07.md`
- `docs/knowledge-base/research/git-analysis-2026-07-12.md`
- `docs/knowledge-base/research/git-analysis-2026-07-13.md`
- `docs/knowledge-base/research/institutional-vendor-evaluation.md`
- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`
- `docs/knowledge-base/research/mnemox-update-2026-07-19.md`
- `docs/knowledge-base/research/phase1-lessons-learned-2026-07-13.md`
- `docs/knowledge-base/research/phase2-concurrency-test-results.md`
- `docs/knowledge-base/research/phase2-lessons-learned-2026-07-13.md`
- `docs/knowledge-base/research/phase2-performance-baseline-analysis.md`
- `docs/knowledge-base/research/phase2-performance-baseline-results.md`
- `docs/knowledge-base/research/phase2-vocabulary-drift-implementation.md`
- `docs/knowledge-base/research/phase3-additional-work-lessons-learned.md`
- `docs/knowledge-base/research/phase3-day1-2-validation-framework.md`
- `docs/knowledge-base/research/phase3-day3-4-parallel-work.md`
- `docs/knowledge-base/research/phase3-monitoring-lessons-learned.md`
- `docs/knowledge-base/research/phase3-real-time-monitoring-implementation.md`
- `docs/knowledge-base/research/quality-gate-status-2026-07-18.md`
- `docs/knowledge-base/research/repo-scan-2026-07-12.md`
- `docs/knowledge-base/research/repo-scan-2026-07-13.md`
- `docs/knowledge-base/research/repo-scan-2026-07-18.md`
- `docs/knowledge-base/research/repository-improvement-plan.md`
- `docs/knowledge-base/research/security-scan-2026-07-12.md`
- `docs/knowledge-base/research/security-scan-2026-07-13.md`
- `docs/knowledge-base/research/test-coverage-2026-07-12.md`
- `docs/knowledge-base/research/test-coverage-2026-07-13.md`

## Findings

### L-1 — Challenge submission pack is text-complete; pitch deck is the sole open blocker

The four commits since the last run closed the last content gap in the `2026_IBMer_Watsonx_Challenge/` pack. All three text fields (`01`, `02`, `03`) and the pitch outline (`04`) are submission-ready. The "why not RAG?" argument was inserted in three targeted places (Field 2 after the three-layer pattern, Field 3 after §4, and Slide 2 speaker notes in the pitch outline). The submission cannot be judged without the pitch deck — that is the single remaining deliverable before the July 22, 10:00 ET deadline.

### L-2 — Zero orphans achieved on the 108-node KB corpus

Commit `0c8a5c1` rescued all 44 remaining orphan documents. The graph now has 109 nodes and 4,589 edges (up from 2,876 on the 80-node snapshot of 2026-07-17). The semantic threshold of 0.30 continues to hold. The orphan-rescue pattern (semantic edges connecting isolated nodes to authority hubs) is the primary driver — structural cross-reference edges alone were insufficient for documents in niche sub-topics.

### L-3 — The "why not RAG?" objection must be answered at the point of formation, not preemptively

The positioning brief (`mnemox-positioning-brief-2026-07.md`) has a complete RAG comparison, but a jury reads the three submission fields, not the KB. The lesson: supporting material in the KB is invisible to judges unless its key argument is surfaced in the judged artefacts. The insertion pattern used here — blockquote immediately after the line that triggers the objection — is more effective than a dedicated comparison section further down the document.

### L-4 — Graph scale grows non-linearly with corpus size

80 docs → 2,876 edges (35.9 edges/node). 109 docs → 4,589 edges (42.1 edges/node). The semantic edge density increases super-linearly as the corpus grows, which means retrieval quality compounds: each new document creates more cross-links than the previous one. This validates the compounding thesis structurally — the graph becomes denser and more navigable with each session.

### L-5 — `mnemox --quick` is the right close-of-session ritual for content-only sessions

Full mnemox (with repo analysis) takes ~3–5 minutes and is appropriate after code changes. Quick mnemox (lessons + graph + commit) takes ~15 seconds and is appropriate after documentation or KB-only sessions. The current session was documentation-only (challenge pack edits + jury assessment). `--quick` was the correct choice.

## Conclusions

### Recommendations

1. **Build the pitch deck before July 22, 10:00 ET.** Every word is written in `04-pitch-file-outline.md`. The remaining work is layout, the Slide 3 mode picker screenshot (2 min), and the Slide 7 RAG comparison table (already written verbatim). This is the single action that determines judging eligibility.
2. **Do not rebuild the graph until the next KB write.** The graph is current at 109 nodes / 4,589 edges. Rebuilding without new documents adds no value and costs Bobcoins.
3. **On the next KB session, check index.md staleness.** The three challenge pack files (`02`, `03`, `04`) are not KB documents and are correctly absent from the index. No index update needed for this session.

### Next Steps

- [ ] Take the Slide 3 screenshot (Bob IDE mode picker → 🧠 Mnemox Knowledge Builder)
- [ ] Build the 8-slide pitch deck from `04-pitch-file-outline.md`
- [ ] Confirm eligibility gates: team registration + Bob education (~40 min) completed by July 22, 10:00 ET
- [ ] Decide on demo format (check submission form for whether video upload is required or optional)
- [ ] Submit before the deadline — only the last submission counts

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-19 — Mnemox Knowledge Builder*
*Category: Research*
