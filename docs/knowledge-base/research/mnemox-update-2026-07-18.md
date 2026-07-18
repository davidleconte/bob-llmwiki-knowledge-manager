---
title: "Mnemox Update — 2026-07-18 (run 5)"
category: research
tags: [mnemox, lessons-learned, adversarial-audit, embeddings, retro-engineering]
created: 2026-07-18
updated: 2026-07-18
status: active
related:
  - ../index.md
  - ./full-technical-design-retro-2026-07.md
---

# Mnemox Update — 2026-07-18 (run 5)

## Objective
Automated KB update run by `mnemox --quick` on 2026-07-18.
Captures changes from the adversarial audit cycle: retro-doc corrections + code fix.

## Background
- Last mnemox run: 2026-07-18T19:08:03Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
49c2271 fix(doc+code): adversarial audit corrections on retro-engineering doc + EmbeddingGenerator warning message
833860a docs(kb): file full technical design retro-engineering 2026-07 + index architectural overviews heading
206bf61 docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 4)
23c01b2 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 14 |
| Guides     | 26 |
| References | 4 |
| Research   | 60 |
| **Total**  | **105** |

## Graph State

| Metric | Value |
|---|---|
| Nodes | 117 |
| Edges | 4,357 |
| Δ edges since run 4 | +88 (retro-doc + adversarial audit doc added as new nodes with semantic edges) |

## Validator Warnings to Track

| Warning | Root Cause | Fix |
|---|---|---|
| `INDEX.md` listed as orphan | Validator scans `research/` and flags `INDEX.md` because it has no entry pointing *to* it — expected false positive | Add validator exclusion for `INDEX.md` in `scripts/validate-kb.sh` |
| `Missing 'title:' in research/mnemox-update-*.md` | `mnemox.sh` lessons note heredoc lacks `title:` field | Add `title: "Mnemox Update — $(date +%Y-%m-%d)"` to heredoc (single-line fix in `scripts/mnemox.sh`) — both warnings disappear on next run |

## Findings

### Finding 1: The adversarial audit → code fix pipeline worked end-to-end

The session executed the full adversarial review loop: (1) hostile pass identified 8 structural attacks, (2) gap analysis cross-checked each attack against live code, (3) one gap (G-3) was found **factually wrong** — the code had already fixed it, (4) the documentation was corrected, and (5) a genuine code bug was found and fixed (`EmbeddingGenerator` warning message). This is the correct sequence: adversarial analysis surfaces real issues *and* exposes stale documentation about resolved issues.

**Implication:** Adversarial audit is not just a review technique — it is a staleness detector. Every "this is broken" claim in a KB document is an opportunity to discover that the code has moved on without updating the docs.

### Finding 2: G-3 being CLOSED means the §5.2 backend chain description was already accurate — the doc was behind the code, not the other way around

The retro-engineering document listed G-3 as an open gap (`sentence-transformers` not wired). The code at [`src/cache/embeddings.py:64-70`](../../../src/cache/embeddings.py) had wired it since P4. The document was written from memory/KB, not from the live code — it reproduced a stale finding from an older KB document. This is the re-derivation contamination problem: when a session reads a stale KB document about a gap, it propagates the stale claim into new documents without re-checking the source.

**Implication:** Any KB document that lists "open gaps" or "known issues" must cite the commit that introduced the gap. Without a commit reference, there is no way to know if the gap is still open without reading the code. Add `(open since: <commit>)` to each gap row in §10.

### Finding 3: One code change emerged from a documentation review — the correct direction

Normally code changes drive documentation updates. Here the inverse happened: adversarial review of a doc found a misleading warning message in the code. The fix was a 4-line string change with zero functional impact, but it means any user who encounters the warning on a machine without `mlx-embeddings` now gets correct remediation instructions (they're told to install `sentence-transformers` too, not just `mlx`).

**Implication:** Documentation adversarial audits are worth running even when you believe the code is correct — they surface the user-facing text that code review doesn't catch.

### Finding 4: The `mnemox.sh` template bug is a recurring false alarm — fix it once

Every single `mnemox --quick` run in this session has produced `Missing 'title:' in frontmatter: research/mnemox-update-*.md`. This is four consecutive runs. The fix is a single line in [`scripts/mnemox.sh`](../../../scripts/mnemox.sh). The cost of ignoring it is validator noise that trains the operator to ignore warnings — exactly the wrong habit when real frontmatter issues need to be caught.

**Implication:** Fix the heredoc template in `mnemox.sh` as the first action next session. It is the lowest-cost highest-signal fix available.

### Finding 5: The adversarial pattern itself should be KB-documented as a repeatable workflow

The full workflow executed this session — (a) hostile pass, (b) gap cross-check against code, (c) verdict table (reinforce/overlap/contradict), (d) design document of changes, (e) apply + validate + commit — is repeatable and valuable. It is currently documented only in the `adversarial-review-pattern.md` concept, which covers the two-pass technique but not the gap-analysis integration step. The gap-analysis step (checking whether a gap is still open in the live code before incorporating it into corrections) is the key addition this session discovered.

**Implication:** Update [`adversarial-review-pattern.md`](../concepts/adversarial-review-pattern.md) with a Step 3: "Gap code-check — for each gap cited in the document under review, verify against the live source before incorporating it into corrections."

## Conclusions

### Recommendations

1. **Fix `mnemox.sh` heredoc** — add `title: "Mnemox Update — $(date +%Y-%m-%d)"` to the lessons note template. Eliminates a recurring false-positive warning on every run.
2. **Add commit references to §10 gap rows** in `full-technical-design-retro-2026-07.md` — `(open since: <commit>)` makes staleness detectable without reading the code.
3. **Update `adversarial-review-pattern.md`** with the gap code-check step discovered this session.

### Next Steps

- Fix `scripts/mnemox.sh` heredoc template (1-line change)
- Add `(open since: commit)` references to each open gap in the retro doc §10
- Add Step 3 to `adversarial-review-pattern.md`: gap code-check protocol

## Related Documents
- [Knowledge Base Index](../index.md)
- [Full Technical Design Retro-Engineering](./full-technical-design-retro-2026-07.md)
- [Adversarial Review Pattern](../concepts/adversarial-review-pattern.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder (run 5)*
*Category: Research*
