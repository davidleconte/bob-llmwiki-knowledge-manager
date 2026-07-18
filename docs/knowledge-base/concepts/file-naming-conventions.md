# File Naming Conventions

## Overview
All Markdown files in this repository use **kebab-case** (lowercase, words separated by hyphens). This is the single enforced convention for every `.md` file outside of GitHub-convention root files and system directories.

## Key Points
- All `.md` files use kebab-case: `my-document-name.md`
- GitHub-convention root files are exempt: `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `STATUS.md`, `SUPPORT.md`, `INTEGRATIONS.md`, `CODE_OF_CONDUCT.md`
- `SKILL.md` files inside `.bob/skills/` are exempt (system-managed)
- Directories `.bob/`, `.claude/`, `.venv/`, `.github/` are hard exclusion zones — never rename files inside them
- The KB index file is `docs/knowledge-base/index.md` (lowercase)

## Details

### The Kebab-Case Rule
Applied to 107 files in 2026-07, converting all `SCREAMING_SNAKE_CASE` and `Mixed-Case` filenames:

```
docs/ARCHITECTURE.md        → docs/architecture/architecture.md
docs/QUICK_START.md         → docs/quick-start.md
docs/knowledge-base/INDEX.md → docs/knowledge-base/index.md
src/cache/CONCURRENCY.md    → src/cache/concurrency.md
```

Conversion formula: lowercase the stem, replace `_` with `-`.

### Why `index.md` Has the Widest Blast Radius
The KB index filename is referenced in more places than any other renamed file:
- `scripts/validate-kb.sh` — checks existence on disk
- `scripts/init-project.sh` — creates the file at init time
- `config/settings.json` — `fileName` array (auto-loaded by Bob IDE)
- `.bob/settings.json` — same
- `tests/test_workflows.py` — existence assertions
- `README.md` prose — 7 occurrences
- `AGENTS.md` KB-first protocol — multiple references
- `config/custom_modes.yaml` — inline instructions

**Rule:** Pair any rename of `index.md` with `grep -r "INDEX\.md"` (or the new name) across all non-excluded directories before committing.

### Exclusion Zones
References to `ARCHITECTURE.md` inside `.bob/custom_modes.yaml` are *content instructions to agents* telling them what file to generate in a client project — they are not file paths into this repository. They must never be rewritten by a rename sweep.

| Excluded path | Reason |
|---|---|
| `.bob/` | Bob IDE system config; `SKILL.md` naming is system-enforced |
| `.claude/` | Git worktrees; internal tooling |
| `.venv/` | Python virtual environment |
| `.github/` | GitHub Actions / PR templates — GitHub platform convention |

### Detecting Drift
```bash
# Find any .md files with uppercase letters outside exempted bases and dirs
find . -name "*.md" \
  -not -path "./.git/*" -not -path "./.claude/*" \
  -not -path "./.bob/*"  -not -path "./.venv/*" \
  -not -path "./.github/*" \
  | while read f; do
    base=$(basename "$f")
    echo "$base" | grep -qE '[A-Z]' && echo "UPPERCASE: $f"
  done
```

### Emoji in Mode Display Names
Mode emoji live in `.bob/custom_modes.yaml` under `customModes[slug].name`. Every prose reference in `README.md`, `AGENTS.md`, and every test assertion must match this single source. When the emoji changes, grep for the old character across those files.

The `knowledge-manager` mode uses `🧠` (not `📚`).

## Examples

```
# Correct
docs/quick-start.md
docs/knowledge-base/index.md
docs/architecture/architecture.md
src/cache/concurrency.md

# Incorrect
docs/QUICK_START.md
docs/knowledge-base/INDEX.md
docs/architecture/ARCHITECTURE.md
src/cache/CONCURRENCY.md
```

## Related Documents
- [Repo Hygiene Rules](./repo-hygiene-rules.md)
- [KB Document Types](./kb-document-types.md)
- [Knowledge Base Index](../index.md)

## References
- `mnemox-update-2026-07-18.md` — lessons from the 107-file kebab rename session
- `repo-hygiene-lessons-2026-07.md` — `.gitignore` leading-`/` rule and related hygiene

---
*Last Updated: 2026-07-18*
*Category: Concept*
