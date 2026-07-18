---
title: Repo Hygiene — Lessons Learned
category: research
tags: [git, gitignore, absolute-paths, secrets, plan-files, repo-hygiene, portability, security]
created: 2026-07-18
updated: 2026-07-18
status: active
priority: P2
branch: fix-multilevel-cache-race
---

# Repo Hygiene — Lessons Learned

## Objective

Document the repo hygiene issues found and fixed on `fix-multilevel-cache-race`,
and the rules derived from them. These issues are independent of the cache thread-
safety work — they accumulated over multiple sessions and were invisible until a
deliberate hygiene pass was run.

---

## Background

A hygiene audit before the final push found five distinct classes of issue across
the repository:

| ID | Class | Severity | What was found |
|---|---|---|---|
| H-1 | Unrelated directories tracked | Low | `LABs/` and `Recipes/` — Bob IDE artefacts, unrelated to this project |
| H-2 | Plan files at repo root | Low | 4 session-scaffolding `.md` files accumulating at root |
| H-3 | Absolute machine-specific paths | Medium | `/Users/david.leconte/…` in 3 committed documents |
| H-4 | Absolute paths from another user's machine | High | `/Users/coredump/Desktop/EXEC2/…` in `.bob/mcp.json` |
| H-5 | Exposed API secret in committed file | **Critical** | Real OpenAI API key in `.bob/mcp.json` |

---

## Findings

### H-1 — Unrelated directories (`LABs/`, `Recipes/`)

**What happened:** `LABs/` and `Recipes/` are Bob IDE workspace artefacts — demo
labs and recipe collections that belong to the IDE, not to this Python package.
They were present in the working tree but not relevant to the project's topic.

**Fix:** Added to `.gitignore`:
```gitignore
# Bob IDE Labs and Recipes — unrelated to this project's topic
LABs/
Recipes/
```

**Rule:** Any directory that exists because of the IDE or development environment,
not because of the project, belongs in `.gitignore` from its first appearance.
Letting it accumulate even one commit makes it harder to remove cleanly.

---

### H-2 — Plan/scratch files accumulating at the repo root

**What happened:** Four planning documents were created at the repo root during
fix sessions (`gap-fix-plan.md`, `km-savings-test-plan.md`, `minilm-docs-plan.md`,
`cache-remediation-plan.md`). By the time the branch was ready to merge, each was
fully superseded: the CHANGELOG entries describe every fix, the KB research docs
summarise every finding, and the test files are the ground truth. Yet they remained
at root, appearing in `git diff --stat`, `ls`, and every file-picker in every editor.

**Fix — two-step:**
1. Move files to `docs/project-management/plans/` (their permanent home).
2. Gitignore the root-level filenames **with a leading `/`** so the pattern is
   anchored to the repo root only and does not accidentally ignore the files
   in their new location under `docs/`.

```gitignore
# Root-level plan/scratch files — transient session artefacts
/gap-fix-plan.md
/km-savings-test-plan.md
/minilm-docs-plan.md
/cache-remediation-plan.md
```

**Why the leading `/` matters:**  
Without it, a gitignore pattern like `gap-fix-plan.md` matches *anywhere* in the
tree — including `docs/project-management/plans/gap-fix-plan.md`. The file
becomes invisible to git at its permanent location. Leading `/` anchors the pattern
to the root.

**Rule (from `iterative-audit-lessons-2026-07.md`, Finding 6, reinforced):**
Plan/scratch files belong in one of three places:
1. `docs/adr/` — if the decision is architectural and needs a permanent record
2. `docs/project-management/plans/` — if the plan is a project artefact worth keeping
3. Deleted on branch merge — if it is pure session scaffolding

They do not belong at the repo root. Their presence at root is a signal that the
session that created them did not have a designated destination.

---

### H-3 — Absolute machine-specific paths in committed documents

**What happened:** Three committed files contained `/Users/david.leconte/…` paths:
- `docs/project-management/reviews/HANDOFF_PROMPT.md` — 5 occurrences (cd command,
  location references, file listing examples)
- `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md` — 1 occurrence (template path)
- `evaluation/TEST_REPOSITORIES.md` — 1 occurrence (CLI example)

These paths are valid only on one person's machine. Anyone else cloning the repo
and following the instructions would either get an error or silently use the wrong path.

**Fix:** Replaced all instances with `<project-root>` placeholder:
```bash
sed -i '' 's|/Users/david.leconte/Projects/bob-llmwiki-knowledge-manager|<project-root>|g' \
  docs/project-management/reviews/HANDOFF_PROMPT.md \
  evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md \
  evaluation/TEST_REPOSITORIES.md
```

**Rule:** All paths in committed documentation must be relative or use a
clearly-labelled placeholder (`<project-root>`, `$(pwd)`, `./`). The test:
```bash
git ls-files | xargs grep -l "/Users/$USER" 2>/dev/null
```
should return empty on any machine after any commit.

---

### H-4 — Another user's absolute paths in `.bob/mcp.json`

**What happened:** `.bob/mcp.json` contained:
```json
"command": "/Users/coredump/Desktop/EXEC2/.venv/bin/python",
"args": ["/Users/coredump/Desktop/EXEC2/external-llm-mcp-server-bob/external_llm_mcp_server.py"]
```

These are absolute paths from a different developer's machine (`coredump`). The
`external-llm` server was already `"disabled": true`, but the paths were committed
and caused log errors for every other user opening the workspace (confirmed in
`.bob/.bob-errors/` logs: `spawn /Users/coredump/… ENOENT`).

**Fix:** Replaced with portable invocation:
```json
"command": "python",
"args": ["external_llm_mcp_server.py"]
```

**Rule:** MCP server configurations in `.bob/mcp.json` must never contain absolute
paths referencing any specific machine. Use:
- `python` / `uv` / `npx` for commands (resolved from `$PATH`)
- Relative paths or `--directory` flags for script locations
- Environment variables for configurable roots

---

### H-5 — Exposed API key in committed file (Critical)

**What happened:** `.bob/mcp.json` contained a live OpenAI API key in plain text:
```json
"OPENAI_API_KEY": "sk-proj-cqDP…"
```

This key was committed to the repo and pushed to GitHub. The key should be
considered **compromised** from the moment it was committed — any clone, fork,
or CI run with read access to the repo could extract it.

**Immediate fix:** Redacted to placeholder:
```json
"OPENAI_API_KEY": "YOUR-OPENAI-API-KEY-HERE"
```

**What should have happened:** The key should never have been placed in a tracked
file. The correct pattern is:
```json
"OPENAI_API_KEY": "${OPENAI_API_KEY}"
```
read from the environment, or from a `.env` file that is gitignored.

**Rule (from `platform-secrets-config.md` workspace rule):**
> All config and secrets come from the environment / a secret manager — never
> hardcoded, never committed. Provide a `.env.example` with no real values.

**Detection command:**
```bash
git log --all -p | grep -E "sk-proj-|sk-live-|AKIA|ghp_"
```
Run this before every push. A pre-commit hook is the structural enforcement.

**Note on git history:** Redacting the value in a new commit does not remove it
from git history. If this key was active at the time of commit, it should be
rotated immediately regardless of the redaction.

---

## Hygiene Audit Protocol

The following commands detect all five issue classes. Run before every push on a
branch that has touched `.bob/`, `docs/`, or `evaluation/`:

```bash
# H-1: Unrelated directories not gitignored
ls -d */ | grep -vE "^(src|tests|docs|scripts|config|examples|evaluation|\.git|\.bob|\.venv)/"

# H-2: Plan/scratch files at root
ls *.md | grep -vE "^(README|CHANGELOG|AGENTS|CONTRIBUTING|GOVERNANCE|INTEGRATIONS|SECURITY|STATUS|SUPPORT|CODE_OF_CONDUCT)\.md$"

# H-3: Machine-specific absolute paths in committed files
git ls-files | xargs grep -l "/Users/$USER\|/home/$USER" 2>/dev/null

# H-4: Any user's absolute paths in committed files
git ls-files | xargs grep -rn "/Users/[a-z]\|/home/[a-z]" 2>/dev/null | grep -v ".md:#\|example\|placeholder"

# H-5: Secret patterns in committed files (extend the pattern list as needed)
git ls-files | xargs grep -lE "sk-proj-|sk-live-|AKIA[A-Z]{16}|ghp_[a-zA-Z0-9]{36}" 2>/dev/null
```

All five commands should produce empty output on a clean repo.

---

## `.gitignore` Design Rules

Derived from the H-2 leading-`/` mistake:

| Scenario | Pattern | Behaviour |
|---|---|---|
| Ignore a file only at root | `/filename.md` | Root only — safe to use `filename.md` in subdirs |
| Ignore a file anywhere in tree | `filename.md` | Matches everywhere — use only if truly global |
| Ignore a directory anywhere | `dirname/` | Matches everywhere including subdirs |
| Ignore a directory only at root | `/dirname/` | Root only — rarely needed |

When gitignoring a file that has a legitimate permanent home elsewhere in the repo,
**always use leading `/`** so the ignore applies only at root.

---

## Conclusions

### Summary of Fixes

| ID | Action taken | Files changed |
|---|---|---|
| H-1 | Added `LABs/`, `Recipes/` to `.gitignore` | `.gitignore` |
| H-2 | Moved 4 plan files to `docs/project-management/plans/`; gitignored at root with `/` | `.gitignore`, 4 file moves |
| H-3 | Replaced `/Users/david.leconte/…` with `<project-root>` | 3 files |
| H-4 | Replaced `/Users/coredump/…` paths with portable invocation | `.bob/mcp.json` |
| H-5 | Redacted live API key to placeholder | `.bob/mcp.json` |

### Verification gate (all five checks must pass before merge)

```bash
git ls-files | xargs grep -l "david\.leconte\|/Users/david\|/Users/coredump" 2>/dev/null || echo "H-3/H-4 clean"
git ls-files | xargs grep -lE "sk-proj-|sk-live-|AKIA[A-Z]" 2>/dev/null             || echo "H-5 clean"
ls *.md | grep -vE "^(README|CHANGELOG|AGENTS|CONTRIBUTING|GOVERNANCE|INTEGRATIONS|SECURITY|STATUS|SUPPORT|CODE_OF_CONDUCT)\.md$" || echo "H-2 clean"
```

---

## Sources

- [`.gitignore`](../../../.gitignore) — updated with `LABs/`, `Recipes/`, anchored plan patterns
- [`.bob/mcp.json`](../../../.bob/mcp.json) — redacted API key, portable paths
- [`docs/project-management/reviews/HANDOFF_PROMPT.md`](../../project-management/reviews/HANDOFF_PROMPT.md) — absolute paths replaced
- [`evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md`](../../../evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md) — absolute paths replaced
- [`evaluation/TEST_REPOSITORIES.md`](../../../evaluation/TEST_REPOSITORIES.md) — absolute paths replaced

## Related Documents

- [Iterative Audit Methodology — Lessons Learned](./iterative-audit-lessons-2026-07.md) — Finding 6: plan-file hygiene
- [Cache Thread-Safety Audit — Round 5](./cache-race-fix-round5-2026-07.md)
- [Cache Thread-Safety Audit — Rounds 1–4](./cache-race-fix-lessons-2026-07.md)

---
*Last Updated: 2026-07-18*
*Category: Research*
