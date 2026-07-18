# Repo Hygiene Rules

## Overview
Five recurring hygiene failure classes and their structural fixes. Run the five detection commands before every push on any branch that touches `.bob/`, `docs/`, or `evaluation/`.

## Key Points
- Never commit absolute machine-specific paths (`/Users/username/…`) — use `<project-root>` or relative paths
- Never commit secrets or API keys — read them from environment variables
- Gitignore root-level plan/scratch files with a **leading `/`** to avoid hiding them in subdirectories
- Unrelated IDE directories (`LABs/`, `Recipes/`) belong in `.gitignore` from their first appearance
- MCP server configs in `.bob/mcp.json` must use portable commands (`python`, `uv`) not absolute paths

## Details

### H-1 — Unrelated IDE Directories
`LABs/` and `Recipes/` are Bob IDE workspace artefacts unrelated to this project's codebase. They must be gitignored:
```gitignore
LABs/
Recipes/
```
**Rule:** Any directory that exists because of the IDE/environment, not because of the project, belongs in `.gitignore` from its first appearance.

### H-2 — Plan Files at Repo Root
Session-scaffolding `.md` files accumulate at the repo root. After the work is done, they show up in `git diff --stat` and every file-picker.

**Fix:** Gitignore them with a **leading `/`** anchored to root only:
```gitignore
/gap-fix-plan.md
/cache-remediation-plan.md
```

**Why leading `/` is critical:** Without it, `gap-fix-plan.md` matches *anywhere* in the tree — including `docs/project-management/plans/gap-fix-plan.md` — silently hiding the permanent copy from git.

**Destination rules for plan files:**
| Type | Where it belongs |
|---|---|
| Architectural decision | `docs/adr/` |
| Project-management artefact | `docs/project-management/plans/` |
| Pure session scaffolding | Delete on branch merge |

### H-3 — Absolute Machine-Specific Paths in Documents
Any `/Users/username/…` path in a committed document breaks portability for every other developer.

**Fix:**
```bash
sed -i '' 's|/Users/david.leconte/Projects/bob-llmwiki-knowledge-manager|<project-root>|g' \
  affected-file.md
```

**Detection:**
```bash
git ls-files | xargs grep -l "/Users/$USER\|/home/$USER" 2>/dev/null
```

### H-4 — Another User's Absolute Paths in `.bob/mcp.json`
MCP configs must use portable invocations:
```json
// Wrong
"command": "/Users/coredump/Desktop/EXEC2/.venv/bin/python"

// Correct
"command": "python"
```
Use `python`/`uv`/`npx` resolved from `$PATH`; never hardcode any user's home directory.

### H-5 — API Keys Committed to Tracked Files (Critical)
A committed secret is a compromised secret from the moment of the commit, regardless of any later redaction. Git history retains it.

**Prevention:**
```json
// .bob/mcp.json — correct
"OPENAI_API_KEY": "${OPENAI_API_KEY}"
```
Provide `.env.example` with placeholder values; gitignore `.env`.

**Detection:**
```bash
git ls-files | xargs grep -lE "sk-proj-|sk-live-|AKIA[A-Z]{16}|ghp_[a-zA-Z0-9]{36}" 2>/dev/null
```

**If a key was committed:** rotate it immediately — the redaction commit does not remove it from history.

## Pre-Push Verification Gate
Run all five checks; all must produce empty output:

```bash
# H-1: unrelated directories not gitignored
ls -d */ | grep -vE "^(src|tests|docs|scripts|config|examples|evaluation|\.git|\.bob|\.venv)/"

# H-2: plan/scratch files at root
ls *.md | grep -vE "^(README|CHANGELOG|AGENTS|CONTRIBUTING|GOVERNANCE|INTEGRATIONS|SECURITY|STATUS|SUPPORT|CODE_OF_CONDUCT)\.md$"

# H-3: machine-specific absolute paths
git ls-files | xargs grep -l "/Users/$USER\|/home/$USER" 2>/dev/null

# H-4: any user's absolute paths
git ls-files | xargs grep -rn "/Users/[a-z]\|/home/[a-z]" 2>/dev/null | grep -v "#\|example\|placeholder"

# H-5: secret patterns
git ls-files | xargs grep -lE "sk-proj-|sk-live-|AKIA[A-Z]{16}|ghp_" 2>/dev/null
```

## Related Documents
- [File Naming Conventions](./file-naming-conventions.md)
- [Repo Hygiene — Lessons Learned](../research/repo-hygiene-lessons-2026-07.md)
- [Knowledge Base Index](../index.md)

## References
- `platform-secrets-config.md` workspace rule — secrets from environment, never committed
- `repo-hygiene-lessons-2026-07.md` — full audit findings with evidence

---
*Last Updated: 2026-07-18*
*Category: Concept*
