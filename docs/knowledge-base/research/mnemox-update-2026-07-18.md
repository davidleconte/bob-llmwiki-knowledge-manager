# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T17:28:07Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
82fe4aa refactor: kebab-case all .md filenames under docs/ and evaluation/
4496d60 feat: auto-add frontmatter via mnemox
2b40318 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 13 |
| Guides     | 26 |
| References | 2 |
| Research   | 59 |
| **Total**  | **101** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/code-metrics-2026-07-12.md`
- `docs/knowledge-base/research/code-metrics-2026-07-13.md`
- `docs/knowledge-base/research/code-metrics-2026-07-18.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-12.md`
- `docs/knowledge-base/research/doc-coverage-2026-07-13.md`
- `docs/knowledge-base/research/git-analysis-2026-07-12.md`
- `docs/knowledge-base/research/git-analysis-2026-07-13.md`
- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`
- `docs/knowledge-base/research/performance-benchmarks.md`
- `docs/knowledge-base/research/repo-scan-2026-07-12.md`
- `docs/knowledge-base/research/repo-scan-2026-07-13.md`
- `docs/knowledge-base/research/repo-scan-2026-07-18.md`
- `docs/knowledge-base/research/repository-improvement-plan.md`
- `docs/knowledge-base/research/security-scan-2026-07-12.md`
- `docs/knowledge-base/research/security-scan-2026-07-13.md`
- `docs/knowledge-base/research/test-coverage-2026-07-12.md`
- `docs/knowledge-base/research/test-coverage-2026-07-13.md`

## Findings

### Finding 1: Kebab-case rename blast radius is large but manageable via `git add -A`
107 `.md` files were renamed across `docs/`, `evaluation/`, `src/`, and `LABs/` in the previous sessions, plus 94 more in this session under `docs/` and `evaluation/`. Git's rename-detection (`R`) correctly tracks all of these when staged with `git add -A`, producing clean, reviewable commit diffs. The key operational lesson: always `git add -A` the whole affected subtree rather than staging individual files — it enables rename detection and produces far more readable history.

### Finding 2: `add-frontmatter.sh` is fully idempotent — safe to run in every mnemox pass
The script's `head -1 == "---"` guard works reliably across all 100 KB docs. On the first real run it backfilled 27 documents (guides, references, research) that lacked frontmatter; the Step 2/5 `mnemox --quick` run immediately after confirmed 0 added, 100 already present. The approach — detect by first line, derive title from `# H1`, use file mtime for dates — is robust and requires no external state.

### Finding 3: SKILL.md templates must be kept in sync with `config/templates/`
The `.bob/skills/knowledge-manager/SKILL.md` template blocks were still showing bare `# [Concept Name]`-style examples even after `config/templates/` gained full frontmatter. This created a documentation skew: agents loading the skill would produce docs without frontmatter. Fix: keep SKILL.md as a mirror of `config/templates/`, updated in the same commit. A future improvement would be to generate SKILL.md template blocks directly from `config/templates/` in `mnemox.sh`.

### Finding 4: Graph density grows with frontmatter coverage
After adding frontmatter to all 100 KB docs and graduating 6 concept nodes, the knowledge graph grew from ~3,697 edges to 4,042 edges — a ~9% increase at 113 nodes. This confirms that `tags`, `category`, and `related` frontmatter fields contribute directly to edge scoring in `src/graph/builder.py`. Richer frontmatter → denser, more queryable graph.

### Finding 5: `compact-summary` tag must be on concept docs for `test_km_savings.py` filtering to work
The `TestContextCompressionRatio` suite filters for docs with `compact-summary` in their frontmatter tags. If concept docs lack this tag, the test suite degrades silently (it may pick up no docs). The guard is now automatic: `add-frontmatter.sh` assigns `[concepts, compact-summary]` tags to every concept, and `config/templates/concept.md` + SKILL.md include it by default.

## Conclusions

### Recommendations
1. **Generate SKILL.md template blocks from `config/templates/`** — add a step to `mnemox.sh` (or a new `sync-skill-templates.sh`) that renders `config/templates/*.md` into the SKILL.md fenced code blocks, keeping them permanently in sync.
2. **Add `references` category docs** — only 2 reference docs exist (vs 13 concepts, 26 guides, 59 research). A Reference doc for the `bob-optimize` CLI and one for `mnemox.sh` flags would improve discoverability.
3. **Stage `.bob/` changes in the mnemox auto-commit** — currently `git add docs/knowledge-base/` only. A future option `--include-bob` could also stage `.bob/` skill and mode changes.

### Next Steps
- Create `docs/knowledge-base/references/mnemox-cli-reference.md` — flags, modes, exit codes
- Create `docs/knowledge-base/references/bob-optimize-cli-reference.md` — all subcommands
- Wire SKILL.md template-sync into `mnemox.sh` (or standalone `sync-skill-templates.sh`)

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
