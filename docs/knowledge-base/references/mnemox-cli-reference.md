---
title: "Mnemox CLI Reference"
category: reference
tags: [reference, mnemox, cli]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Mnemox CLI Reference

## Overview

`mnemox` (alias for `bash scripts/mnemox.sh`) is the Knowledge Builder workspace
command. It runs in two modes — **init** (first-time scaffold) and **update**
(ongoing maintenance) — and always finishes with a graph rebuild and git commit.

## Synopsis

```bash
bash scripts/mnemox.sh [MODE_FLAG] [--km-home PATH]
mnemox [MODE_FLAG] [--km-home PATH]          # if installed via scripts/install.sh
```

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| _(none)_ | — | auto | Detect mode: **init** if KB missing, **update** if present |
| `--init` | mode | — | Force init: scaffold KB → 7-phase analysis → validate |
| `--update` | mode | — | Force update (same as `--full`) |
| `--quick` | mode | — | Update without repo analysis: Steps 2–5 only |
| `--full` | mode | — | Update with full repo analysis: all 5 steps |
| `--km-home PATH` | option | auto | Override the Mnemox repo path |
| `--help`, `-h` | — | — | Print usage and exit |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MNEMOX_HOME` | Parent dir of `scripts/mnemox.sh` | Path to the Mnemox repo root. Set once in your shell profile to use `mnemox` from any project directory. |

## Modes in Detail

### `--init`  (first-time setup)

Runs 3 steps:

1. **Scaffold** — `init-project.sh`: creates `docs/knowledge-base/{concepts,guides,references,research}/` and `index.md`
2. **7-phase analysis** — `run-full-analysis.sh`: repo scan, security, code metrics, docs, tests, git, performance
3. **Validate** — `validate-kb.sh`: checks directory structure and broken links

Does **not** auto-commit. Review the generated KB before committing:

```bash
git add docs/knowledge-base/ && git commit -m "mnemox: initial KB"
```

### `--update` / `--full`  (full update)

Runs 5 steps with `set +e` (non-fatal on graph/git errors):

1. **Refresh analysis** — re-runs `run-full-analysis.sh`
2. **Frontmatter backfill** — `add-frontmatter.sh docs/knowledge-base` (idempotent)
3. **Capture lessons** — `mnemox-lessons.sh`: appends a dated entry to `index.md`, creates a research note scaffold at `docs/knowledge-base/research/mnemox-update-YYYY-MM-DD.md`
4. **Validate** — `validate-kb.sh`
5. **Rebuild graph** — `uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic`; skipped gracefully if `uv` is absent

Then auto-commits `docs/knowledge-base/` with message `mnemox: update KB YYYY-MM-DD`.

### `--quick`  (quick update)

Same as `--full` but **skips Step 1** (repo analysis). Use at the end of a Bob
session to capture lessons and commit without re-running the full 7-phase analysis.

```bash
bash scripts/mnemox.sh --quick
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success (including graph-build warnings and git-commit skips) |
| `1` | Fatal: invalid `MNEMOX_HOME`, unknown flag, or `--update` without an existing KB |

## Auto-detection Logic

```
if KB_INDEX (docs/knowledge-base/index.md) exists → MODE=update
else                                               → MODE=init
```

Override with `--init` or `--update` to bypass auto-detection.

## Lessons Note Protocol

After each `--quick` or `--full` run, mnemox prints:

```
Bob: please read docs/knowledge-base/research/mnemox-update-YYYY-MM-DD.md
     and synthesise the lessons learned now.
```

The note contains a `<!-- MNEMOX_SYNTHESISE -->` scaffold. Replace the scaffold
with 3–5 concrete findings from the session's git log and analysis reports, then
commit the synthesised note.

## Examples

```bash
# First-time setup in a new project
bash ~/Projects/bob-llmwiki-knowledge-manager/scripts/mnemox.sh --init

# Quick session close (lessons + graph + commit, no analysis)
bash scripts/mnemox.sh --quick

# Full update from a different project directory
MNEMOX_HOME=~/Projects/bob-llmwiki-knowledge-manager bash scripts/mnemox.sh --full

# Use --km-home flag instead of env var
bash scripts/mnemox.sh --quick --km-home ~/Projects/bob-llmwiki-knowledge-manager
```

## Related Documents

- [Setup Token Optimization](../guides/setup-token-optimization.md)
- [Knowledge Graph Usage Guide](../guides/knowledge-graph-usage-guide.md)
- [Bob Optimize CLI Reference](./bob-optimize-cli-reference.md)
- [KB Document Types](../concepts/kb-document-types.md)
