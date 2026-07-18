---
title: "Mnemox Update — 2026-07-18 (run 4)"
category: research
tags: [mnemox, lessons-learned, graph, retro-engineering]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox --quick` on 2026-07-18.
This note captures what changed since the last run and synthesises lessons learned.

## Background
- Last mnemox run: 2026-07-18T18:44:29Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
38f7098 feat(kb): orphan resolution, frontmatter bulk-fix, adversarial-review concept
2b8ac80 docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 3)
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 14 |
| Guides     | 26 |
| References | 4 |
| Research   | 59 |
| **Total**  | **104** |

## Graph State (this run)

| Metric | Value |
|--------|-------|
| Nodes  | 116 |
| Edges  | 4,269 |
| Prior nodes (July 17 validation) | 80 |
| Prior edges | 2,876 |
| Growth | +45% nodes, +48% edges |

## Findings

### Finding 1: Retro-engineering a system produces the most powerful KB document type

The session produced a full technical design document derived purely from reading the
live KB and code — not from memory or speculation. This is the single most valuable KB
input pattern: **the architectural retro-engineering research note**. It is comprehensive
(covers all layers), grounded (every claim traced to a source), and immediately reusable
as context for future sessions. The token cost of that derivation is now permanently
amortised across every subsequent session that reads the document instead of re-deriving it.

**Implication:** Whenever a significant exploration happens in a session, the closing act
should be a retro-engineering summary written to `research/`. This is the KB Manager's
primary value loop.

### Finding 2: The knowledge graph grew significantly (80 to 116 nodes) and is now stale

The `--quick` run revealed the graph had not been rebuilt since the corpus reached 116
documents. Edge count grew from 2,876 to 4,269 (+48%). This means the orphan rescue
rate, hub rankings, and broken-link counts in the July 17 validation are stale — they
were measured on an 80-doc corpus. New structural orphans may exist among the 36
documents added without a graph rebuild.

**Implication:** Every KB write session should end with a graph rebuild. The `--quick`
run is the safety net that catches missed rebuilds.

### Finding 3: The frontmatter gap in the lessons note itself is a self-referential reminder

The validator reported `Missing 'title:' in frontmatter: research/mnemox-update-2026-07-18.md`
for this document. The `mnemox.sh` script creates the lessons note from a template
that lacks a `title:` field. This is a known script hygiene issue — the template needs
to emit a `title:` line. Until fixed, every mnemox run produces one frontmatter
warning on its own output file.

**Implication:** The `scripts/mnemox.sh` lessons note template (around the
`cat > "$LESSONS_NOTE"` heredoc) needs `title: "Mnemox Update — YYYY-MM-DD"` added
to its frontmatter block. One-line fix.

### Finding 4: The two-session pattern (deep exploration → `mnemox --quick`) is working

The session sequence was: (1) deep retro-engineering exploration consuming the full KB,
then (2) `mnemox --quick` to commit, rebuild the graph, and file a lessons note. This
pattern produces exactly the right artefacts: the exploration output is in the chat, the
knowledge is persisted in the KB, the graph reflects the current corpus, and the commit
log is clean. No re-derivation tokens were spent — the KB was the primary source.

**Implication:** This two-step pattern (`explore deeply` then `mnemox --quick`) should be
documented as the standard workflow in the knowledge graph usage guide.

### Finding 5: The retro-engineering document is the highest-leverage KB investment this session

The document produced in this session covers: business objectives, functional requirements
(UC-1 through UC-6), all component technical specs, the embedding and graph value stack,
the economic model, all quality gates, and all open gaps. Any future session with a fresh
context window can load this single document instead of re-reading 12+ source files.
Estimated token saving per re-read: over 10,000 tokens replaced by one ~4,000-token document.

**Implication:** The retro-engineering document should be filed as a stable `research/`
document and linked from `INDEX.md` under a prominent `## Architectural Overviews` heading
so it is always the first hit on broad architectural queries.

## Conclusions

### Recommendations

1. **File the retro-engineering document** from this session as
   `docs/knowledge-base/research/full-technical-design-retro-2026-07.md` — it is currently
   only in the chat history and will be lost at context reset.
2. **Fix the `mnemox.sh` lessons note template** to include `title:` in frontmatter —
   one line eliminates a persistent validator warning on every run.
3. **Re-run `bob-optimize graph-health`** on the now-116-node corpus to get updated orphan
   counts, hub rankings, and broken-link status — the July 17 validation report is stale.

### Next Steps

- `write_file` the retro-engineering document to `research/full-technical-design-retro-2026-07.md`
- Add a `title:` line to the `mnemox.sh` heredoc template (single-line fix in `scripts/mnemox.sh`)
- Run `bob-optimize graph-health --kb-path docs/knowledge-base` for fresh structural metrics
- Add `## Architectural Overviews` heading to `INDEX.md` with the retro doc entry

## Related Documents
- [Knowledge Base Index](../index.md)
- [Knowledge Graph Usage Guide](../guides/knowledge-graph-usage-guide.md)
- [Graph Validation — July 2026](./graph-validation-2026-07-17.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder (run 4)*
*Category: Research*
