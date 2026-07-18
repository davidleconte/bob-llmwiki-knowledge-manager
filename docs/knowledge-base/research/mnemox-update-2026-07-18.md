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
- Last mnemox run: 2026-07-18T20:17:14Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
63789a1 ci+docs: implement mnemox lessons-2026-07-18 action items
764a2e5 docs(kb): synthesise mnemox --quick lessons 2026-07-18 (run 6)
ba2ae9e mnemox: update KB 2026-07-18
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

- `docs/knowledge-base/research/business-case-2026-07.md`
- `docs/knowledge-base/research/full-technical-design-retro-2026-07.md`
- `docs/knowledge-base/research/mnemox-challenge-submission-2026-07.md`
- `docs/knowledge-base/research/mnemox-executive-brief-2026-07.md`
- `docs/knowledge-base/research/mnemox-positioning-brief-2026-07.md`
- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`

## Findings

### Finding 1 — Audience gap was the primary documentation risk

The project had A+ engineering quality and two well-structured documents (business case +
technical retro) but was under-served for its three most important audiences: challenge
judges, CTOs evaluating adoption, and Enterprise Architects doing competitive evaluation.
All three read *different* documents and ask *different* questions. Merging those audiences
into a single document — or routing them through a 700-line README — is a structural
documentation anti-pattern. The fix was to create dedicated, short-form, audience-specific
documents with a clear routing table between them.

**Lesson:** After any significant documentation sprint, audit by audience, not by content.
Ask: "If a judge has 5 minutes, what do they read? If an EA asks 'why not RAG?', where do
they land?" If the answer is "they have to find it themselves in a long doc", a gap exists.

### Finding 2 — The challenge submission narrative was buried four levels deep

The IBMer watsonx Challenge context (Team BobjectifLune, IBM Bob principles addressed,
what judges can evaluate, the "Why BobjectifLune" name origin) existed only in scattered
README sections. A judge arriving at the repo had no single document that said: *"This is
our submission. Here is what we built. Here is how to evaluate it."* The submission
narrative is arguably the most important document for the challenge — yet it was the last
to be written. For any future competition or external presentation, write the submission
narrative first, then use it to structure everything else.

### Finding 3 — Cross-reference chains must be verified mechanically, not assumed

After adding three new documents in one session, the cross-reference chain (README →
index.md → research docs → frontmatter `related:`) required four separate editing passes
to be fully consistent. Each pass found a reference that the prior pass had missed. The
skill protocol says cross-references are bidirectional — but "bidirectional" also means
every *new* document must be pointed to by all *existing* documents that are logically
related. The `mnemox --quick` graph rebuild (121 nodes, 4,381 edges) now captures these
relationships semantically, but the explicit `related:` frontmatter still requires manual
discipline. The `graph-health` command is the mechanical check.

**Action for next session:** Run `bob-optimize graph-health` to verify the 4 new research
documents have no structural orphans despite their cross-references being new.

### Finding 4 — The Mermaid diagram in the technical retro replaces a key architectural debt

The ASCII sub-system boundary diagram in §3 of the technical retro was the single biggest
readability gap in that document. An Enterprise Architect reading the component boundary
for the first time — shared embedding layer, one-way delegation dependency, blocked P1-3
bridge — needed a visual, not a box-drawing ASCII approximation. The Mermaid replacement
also surfaces the **multi-user vs. local** distinction (shared KB via Git; local-only
optimizer) which was architecturally critical but previously absent. Diagrams in KB
documents should default to Mermaid, not ASCII, unless the rendering environment is
known to not support it.

### Finding 5 — `graph_weight=0.0` is still unvalidated beyond the current corpus

The knowledge graph rebuilt to 121 nodes and 4,381 edges this session (up from 80 nodes
/ 2,876 edges in the July 17 snapshot). The semantic edge density is high. G-1 from the
technical retro still applies: `graph_weight=0.0` is confirmed correct for the current
tight-topic corpus, but the compounding PageRank effect is hypothetical until the corpus
diversifies across at least 3 distinct topic domains. At 121 nodes, all on the same
project, this is expected. The next meaningful corpus diversity check is at ~300 nodes.

## Conclusions

### Recommendations

1. **Run `bob-optimize graph-health`** immediately in the next session to verify the 4 new
   research documents have no structural orphans and that their semantic edges connected
   correctly into the graph.
2. **Add the challenge submission document to the README opener** (§1 or the project
   badge line) so it is the first thing a judge sees, not item 3 of 11 in §13 Documentation.
3. **Write the submission narrative first** in any future challenge or external presentation
   sprint — use it as the structural backbone for all supporting documents.

### Next Steps

- `bob-optimize graph-health --kb-path docs/knowledge-base` — verify 4 new docs not orphaned
- Consider promoting `mnemox-challenge-submission-2026-07.md` to a top-level link in the
  README header (alongside or replacing the current one-liner attribution on line 21)
- Validate P@3 on the expanded 121-node corpus using `bob-optimize kb-search` on the
  25-query golden set — confirm retrieval precision held at 0.88 after the corpus grew

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
