# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T17:37:15Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
441cb1f feat: sync-skill-templates + 2 new reference docs
42d3506 mnemox: synthesise lessons 2026-07-18
a95ece7 mnemox: update KB 2026-07-18
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

### Finding 1: `sync-skill-templates.sh` works but is not truly idempotent on re-runs
On the second consecutive run the script re-wrote all 4 SKILL.md blocks even though content was identical, producing a non-empty `git diff`. Root cause: Python's `re.sub` always writes the file even when the replacement is unchanged. The script needs a pre/post hash check (`md5` or `sha256`) before writing, so it only touches the file when content actually changes. For now it is safe but noisy — commits will contain cosmetic-only SKILL.md changes if `config/templates/` are not modified.

### Finding 2: `add-frontmatter.sh` caught a genuine new doc (lessons note scaffold)
Step 2/6 added frontmatter to `research/mnemox-update-2026-07-18.md` because the lessons note was created by `mnemox-lessons.sh` *after* the previous frontmatter pass in commit `a95ece7`. This confirms the ordering in mnemox.sh is correct: frontmatter step must run *before* lessons capture so the note always gets frontmatter on the *next* run. The one-run lag is acceptable — the note gains frontmatter the moment it enters the next `--quick` pass.

### Finding 3: References category grew from 2 → 4 in one session — CLI docs pay off immediately
Both `mnemox-cli-reference.md` and `bob-optimize-cli-reference.md` were immediately indexed and graph-connected (115 nodes, 4162 edges, +120 from prior run). CLI reference docs are high-ROI KB entries: they are queried repeatedly by agents, cover ground that is otherwise scattered across `--help` output, and have no equivalent in the concept/guide tiers.

### Finding 4: mnemox.sh step count is now 6 — keep `--help` text in sync
The `--help` output still says `--quick: lessons + graph + commit only` which understates the current 6-step pipeline. When the step count changes, `--help`, banner messages, and this docs must all be updated together. Consider deriving the step count from a single constant at the top of `mnemox.sh`.

## Conclusions

### Recommendations
1. **Fix `sync-skill-templates.sh` idempotency** — add a SHA256 comparison before writing: read current block, compare to template content, skip write if identical. This eliminates spurious SKILL.md commits.
2. **Update `mnemox.sh --help` text** — `--quick` description should say "Steps 2–6 (frontmatter + template sync + lessons + validate + graph)".
3. **Add `--include-bob` flag to mnemox.sh auto-commit** — currently only `docs/knowledge-base/` is staged. An opt-in flag would also stage `.bob/skills/` changes (e.g., SKILL.md syncs).

### Next Steps
- Fix idempotency in `sync-skill-templates.sh` (SHA256 guard before write)
- Update `mnemox.sh --help` step descriptions to reflect 6-step pipeline

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
