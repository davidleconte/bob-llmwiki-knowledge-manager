# Plan — `mnemox` as a Smart Two-Mode Command

## Overview

Make the word **`mnemox`** — typed in any Bob Shell CLI or Bob IDE session, or run
at the terminal — a single self-aware entry point that does the right thing
automatically:

- **Fresh workspace** (no `docs/knowledge-base/index.md`) → **init mode**: scaffold
  the KB, run the 7-phase analysis suite, validate structure. The workspace is
  Mnemoxed for the first time.
- **Already-Mnemoxed workspace** (INDEX.md exists) → **update mode**: refresh the
  7-phase analysis, capture lessons learned (git log + KB diff → one research note
  filed into the KB), rebuild the knowledge graph, auto-commit all KB changes to git.

Both targets (Bob Shell CLI terminal command + Bob IDE / Bob Shell chat phrase) are
served by the same underlying script. The chat phrase is wired via SKILL.md triggers
and `customInstructions` in the mode definition.

Graph rebuild (`bob-optimize graph-build`) is always attempted; if `uv` or Python is
absent the script warns and continues — it never blocks.

## Confirmed Design Decisions

| # | Decision | Answer |
|---|---|---|
| 1 | When does Bob synthesise the lessons-learned note? | **In the same session** — after mnemox-lessons.sh files the scaffold, Bob reads it immediately and fills the `Lessons Learned` section before the session continues |
| 2 | How does Bob find mnemox.sh in other-project workspaces? | **`MNEMOX_HOME` environment variable** — set at install time in `~/.bob/mnemox.sh`; default value is the KM repo path resolved at install time; user can override by exporting `MNEMOX_HOME` before launching Bob |
| 3 | Does mnemox auto-commit to git? | **Yes, on update path only** — `git add docs/knowledge-base/ && git commit -m "mnemox: update KB $(date +%Y-%m-%d)"` runs at the end of the update path after graph rebuild; init path does not auto-commit (user reviews first KB before committing) |

---

## Sub-Task 1 — Create `scripts/mnemox.sh`

**Intent**
The single executable that implements both modes. Everything else (alias, chat trigger,
mode instruction) calls this script. All logic lives here so it is testable
independently of Bob.

**Expected Outcomes**
- Running `bash scripts/mnemox.sh` from any project root:
  - Detects fresh vs already-Mnemoxed via presence of `docs/knowledge-base/index.md`
  - Fresh → runs init-project.sh, run-full-analysis.sh, validate-kb.sh; prints
    "✅ Workspace Mnemoxed" with doc count and KB path
  - Already-Mnemoxed → runs run-full-analysis.sh, then a new lessons-learned
    capture script (see Sub-Task 2), then validate-kb.sh, then attempts
    graph-build; prints "✅ Mnemox updated" with what changed
- Accepts optional `--init` and `--update` flags to force a specific mode
- Resolves KM home via: `MNEMOX_HOME` env var → `--km-home` flag → auto-detect
  from script location. Default value of `MNEMOX_HOME` is set at install time in
  `~/.bob/mnemox.sh` pointing to the resolved KM repo path.
- Graph rebuild: attempt `uv run bob-optimize graph-build --kb-path
  docs/knowledge-base --with-semantic`; on failure print amber warning, set
  exit code 0 (never blocks)
- On update path: after graph rebuild, runs
  `git add docs/knowledge-base/ && git commit -m "mnemox: update KB $(date +%Y-%m-%d)"`
  — if git commit fails (nothing to commit, no git repo) warns and continues
- Prints a timestamped `.mnemox-last-run` file to the project root after every
  successful run (used by git-log window in Sub-Task 2)

**Todo List**
1. Create `scripts/mnemox.sh` with shebang, `set -e` on the init path only
   (update path uses explicit error capture to avoid blocking on graph rebuild or git)
2. Implement detection: `[ -f "docs/knowledge-base/index.md" ]`
3. Implement KM home resolution: MNEMOX_HOME env var → `--km-home` flag →
   auto-detect from script's own directory parent
4. Implement init path: call init-project.sh → run-full-analysis.sh →
   validate-kb.sh → write `.mnemox-last-run` → print summary (no git commit)
5. Implement update path: call run-full-analysis.sh → call
   `scripts/mnemox-lessons.sh` (Sub-Task 2) → call validate-kb.sh →
   attempt graph-build with graceful failure → git add + commit with graceful
   failure → write `.mnemox-last-run` → print summary
6. Add `--help` output documenting both modes, all flags, and MNEMOX_HOME
7. Make executable: `chmod +x scripts/mnemox.sh`

**Relevant Context**
- `scripts/init-project.sh` — scaffolds dirs, INDEX.md, CONTEXT.md, .bob/settings.json
- `scripts/run-full-analysis.sh` — 7-phase suite, already handles partial failures
  internally (FAILED counter, exits 1 if any fail — mnemox.sh should capture this
  but not propagate on update mode)
- `scripts/validate-kb.sh` — validates structure and prints stats
- `uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic`
  — confirmed in src/cli.py:234-274 and SKILL.md:266
- `.mnemox-last-run` — plain text file containing ISO timestamp of last run;
  created by this script, read by mnemox-lessons.sh

**Status** `[ ] pending`

---

## Sub-Task 2 — Create `scripts/mnemox-lessons.sh`

**Intent**
Capture what changed since the last `mnemox` run and emit a structured research note
into `docs/knowledge-base/research/` for Bob to read next session. Two inputs:
(a) `git log` since last run timestamp, (b) KB doc count before vs after the
fresh analysis. Bob does not write this note — the script writes it. The note is
a structured Markdown scaffold; the next Bob session enriches it if needed.

**Expected Outcomes**
- Reads `.mnemox-last-run` for the since-timestamp (falls back to 7 days if absent)
- Runs `git log --since="<timestamp>" --oneline --no-merges` to get commit list
- Counts KB docs before and after analysis by category
- Writes a dated research note to
  `docs/knowledge-base/research/mnemox-update-YYYY-MM-DD.md` using the
  existing research template schema:
  - Objective: KB update run on <date>
  - Git changes: commit list since last run (if any)
  - KB delta: doc counts before/after per category
  - New analysis reports filed: list from run-full-analysis.sh output
  - Lessons learned section: contains a structured Bob-readable prompt that
    instructs Bob to synthesise lessons learned **in the same session** immediately
    after mnemox completes:
    `<!-- MNEMOX_SYNTHESISE: Bob — read the git changes and new analysis reports
    above and write 3–5 concrete lessons learned directly into this section now.
    Replace this comment with the synthesised content. Then update INDEX.md. -->`
- Updates `docs/knowledge-base/index.md` Recent Additions entry for the new note
- Exits 0 always (non-blocking)
- Emits the path of the new research note to stdout on the last line, prefixed
  `MNEMOX_LESSONS_NOTE=` so mnemox.sh and the mode instruction can read it

**Todo List**
1. Create `scripts/mnemox-lessons.sh` with shebang, no `set -e`
2. Read `.mnemox-last-run`; default to `7 days ago` if absent
3. Capture `git log --since --oneline --no-merges` output; handle no-git gracefully
4. Count KB docs per category before analysis (direct find commands)
5. Write dated research note using heredoc with the research template schema,
   including the `MNEMOX_SYNTHESISE` comment for Bob to act on in-session
6. Append one-line entry to INDEX.md Recent Additions section (sed/awk after
   `## Recent Additions` line)
7. Emit `MNEMOX_LESSONS_NOTE=<path>` as final stdout line
8. Make executable: `chmod +x scripts/mnemox-lessons.sh`

**Relevant Context**
- Research template schema: `.bob/skills/knowledge-manager/SKILL.md:178-222`
- INDEX.md Recent Additions pattern: `docs/knowledge-base/index.md:13-30`
  (format: `- YYYY-MM-DD: [Title](path) - Category — one-line description`)
- Git utility pattern: `src/validation/manifest.py:45-76` (subprocess pattern
  to follow in bash equivalent)
- `.mnemox-last-run` written by Sub-Task 1

**Status** `[ ] pending`

---

## Sub-Task 3 — Register `mnemox` alias in `scripts/install.sh`

**Intent**
Make `mnemox` a real terminal command for Bob Shell CLI users — not just a chat
phrase. After `scripts/install.sh` runs, typing `mnemox` in any terminal from any
project directory invokes `scripts/mnemox.sh` with the correct `MNEMOX_HOME`.

**Expected Outcomes**
- `scripts/install.sh` writes `~/.bob/mnemox.sh` containing:
  - `export MNEMOX_HOME="<resolved-KM-path>"` (hardcoded at install time)
  - `mnemox() { bash "$MNEMOX_HOME/scripts/mnemox.sh" "$@"; }`
- User can override by exporting a different `MNEMOX_HOME` before launching Bob
  or terminal — the function always uses the current value of `$MNEMOX_HOME`
- Prints a one-time instruction to add `source ~/.bob/mnemox.sh` to `~/.zshrc`
  or `~/.bashrc`
- Install is idempotent: re-running install.sh overwrites `~/.bob/mnemox.sh`
  without duplicating the source line in the shell rc file

**Todo List**
1. Add a new section to `scripts/install.sh` after the existing CLI install block
2. Write `~/.bob/mnemox.sh` containing:
   - `export MNEMOX_HOME="<resolved-KM-path>"`
   - `mnemox() { bash "$MNEMOX_HOME/scripts/mnemox.sh" "$@"; }`
3. Check if `source ~/.bob/mnemox.sh` already exists in `~/.zshrc` / `~/.bashrc`;
   if not, print the one-time instruction (do not auto-modify rc files)
4. Print confirmation: "mnemox command installed — source ~/.bob/mnemox.sh to activate"

**Relevant Context**
- `scripts/install.sh` — existing install logic; add after line 78
- KM_HOME detection: use `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`
  then `KM_HOME="$(dirname "$SCRIPT_DIR")"` — same pattern as run-full-analysis.sh:18

**Status** `[ ] pending`

---

## Sub-Task 4 — Wire `mnemox` phrase into SKILL.md and mode customInstructions

**Intent**
Make `mnemox your workspace` (and natural variants) a recognised phrase in both
Bob IDE and Bob Shell CLI chat sessions. When Bob sees the phrase, it executes
`scripts/mnemox.sh` via `execute_command` / `execute` tool group — it does not
attempt to implement the logic itself.

**Expected Outcomes**
- Typing `mnemox your workspace`, `mnemox this project`, `mnemox`, or
  `initialise mnemox` in the knowledge-manager mode chat triggers Bob to run
  `bash scripts/mnemox.sh` (or `bash $KM_HOME/scripts/mnemox.sh` for other-project
  workspaces) via the execute tool
- Bob reports the script's stdout output verbatim, then summarises what happened
- If already Mnemoxed, Bob additionally invites the user to review the new
  lessons-learned research note that was just filed
- Triggers added to `.bob/skills/knowledge-manager/SKILL.md` frontmatter
- Protocol instruction added to the knowledge-manager mode's `customInstructions`
  in `.bob/custom_modes.yaml` (the workspace entry, not the global config entry)

**Todo List**
1. Add five trigger phrases to `.bob/skills/knowledge-manager/SKILL.md` triggers:
   - `"mnemox your workspace"`
   - `"mnemox this workspace"`
   - `"mnemox this project"`
   - `"mnemox"`
   - `"initialise mnemox"`
2. Add a `## Mnemox Command Protocol` section to SKILL.md body (after the
   Persistence note at the end) documenting:
   - The exact execute_command to run (MNEMOX_HOME resolution order)
   - The two-mode behaviour (init vs update)
   - **Same-session synthesis instruction**: after the script completes on update
     path, Bob MUST read the `MNEMOX_LESSONS_NOTE` path from script output, open
     that file, and immediately synthesise 3–5 lessons learned by replacing the
     `MNEMOX_SYNTHESISE` comment with real content, then update INDEX.md
3. Find the knowledge-manager entry in `.bob/custom_modes.yaml` and append a
   Mnemox protocol block to its `customInstructions` field explaining:
   - MNEMOX_HOME resolution: `$MNEMOX_HOME` env var → `--km-home` flag →
     workspace `scripts/mnemox.sh` if present → fail with clear message
   - Run via execute_command, capture stdout
   - Parse `MNEMOX_LESSONS_NOTE=<path>` from stdout
   - On update: immediately read that file and synthesise lessons in-session
   - Report the git commit hash that was made

**Relevant Context**
- `.bob/skills/knowledge-manager/SKILL.md:1-17` — frontmatter with existing triggers
- `.bob/skills/knowledge-manager/SKILL.md:286-291` — Persistence note (append after)
- `.bob/custom_modes.yaml` — 21401 lines; find knowledge-manager slug entry
- Bob IDE execute tool group: confirmed in BOB-IDE-GUIDE.md §5, custom_modes.yaml
- Bob Shell CLI command group: confirmed in scripts/install.sh comments line 12

**Status** `[ ] pending`

---

## Sub-Task 5 — Update README.md §5 and Supported Targets table

**Intent**
Make `mnemox` the canonical, one-word entry point shown in the README — replacing
the three-command bash block in §5 as the recommended path, while keeping the
individual scripts documented for advanced users. Update the Supported Targets table
to show `mnemox` as the install step for all three targets.

**Expected Outcomes**
- README §5 opens with: `mnemox` — one word, typed in the Bob chat or terminal
- The three-command bash block is demoted to "Advanced / individual scripts" below
- The Supported Targets table install-step column shows `mnemox` for all three rows
- A new "Already Mnemoxed?" callout explains the update behaviour
- The Mnemox mythology blockquote in the README opening gains one sentence:
  *"Type `mnemox` in any Bob session. That is the whole command."*

**Todo List**
1. Add one sentence to the Mnemox mythology blockquote (README line ~17)
2. Rewrite README §5 opening paragraph and code block to lead with `mnemox`
3. Add "Already Mnemoxed?" callout explaining auto-update + lessons-learned
4. Update the Supported Targets table install-step column (3 rows)
5. Keep the three-command block as a collapsible `<details>` or "Advanced" note

**Relevant Context**
- `README.md:117-148` — Supported Targets table
- `README.md:164-198` — §5 current content
- `README.md:15-18` — Mnemox mythology blockquote to gain one sentence

**Status** `[ ] pending`

---

## Sub-Task 6 — Add `.mnemox-last-run` to `.gitignore`

**Intent**
The `.mnemox-last-run` timestamp file is machine-local and should not be committed.
One line in `.gitignore`.

**Expected Outcomes**
- `.gitignore` contains `.mnemox-last-run`
- No other changes

**Todo List**
1. Append `.mnemox-last-run` to `.gitignore`

**Relevant Context**
- `.gitignore` — existing file in repo root

**Status** `[ ] pending`

---

## Implementation Order

1 → 2 → 3 → 4 → 5 → 6

Sub-Tasks 1 and 2 are the core; 3–6 are wiring and documentation.
Sub-Task 3 depends on Sub-Task 1 (needs the script path).
Sub-Task 4 depends on Sub-Tasks 1 and 2 (references the script and the lessons note).
Sub-Task 5 depends on Sub-Task 1 (shows the mnemox command).
Sub-Task 6 is independent — can be done any time.

---

## What is explicitly NOT in scope

- Any changes to the Python TOS system beyond the existing `bob-optimize graph-build` call
- Auto-committing the KB to git (user commits; mnemox only writes files)
- Any network calls, cloud sync, or external services
- Changing the Bob mode YAML schema or group permissions
- Windows compatibility (bash scripts, macOS/Linux only)
