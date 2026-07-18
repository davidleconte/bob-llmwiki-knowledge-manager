# Documentation Update Plan — Bob IDE Port & Validation Work

## Scope Decisions (confirmed 2026-07-16)

- **`docs/COMPARISON.md`** — included for completeness check (Sub-Task 8).
- **New document** — `docs/bob-ide-guide.md` to be created as the canonical Bob IDE
  reference. Sub-Task 1 (README.md) links to it; Sub-Tasks 3–5 cross-reference it
  rather than duplicating IDE content inline.

## Overview

This plan captures all documentation changes required to reflect the work completed in
the session of 2026-07-16. The work established:

1. **`config/custom_modes.yaml`** — Bob Shell CLI source-of-truth: group names corrected
   (`command`/`browser` restored; `execute` regression reverted; `save_memory` reference removed).
2. **`.bob/custom_modes.yaml`** — Two new entries appended: `knowledge-manager` and
   `repo-analyzer` with Bob IDE-correct groups (`execute`/`skill`).
3. **`.bob/skills/knowledge-manager/SKILL.md`** — New lazy-load skill: full document templates
   (4-backtick outer fences), cross-reference protocol, INDEX.md maintenance, persistence note.
4. **`scripts/install.sh`** — Rewritten to document Bob Shell CLI vs Bob IDE distinction,
   corrected exit-on-missing-bob message.
5. **`scripts/init-project.sh`** — Heredoc space bug fixed on lines 23 (`<<INDEXEOF`) and
   99 (`<<CTXEOF`); `<< WORD` (space before delimiter) caused heredoc body to execute as shell.
6. **Validation** — All manual gates passed on Bob Shell 1.0.6 (T2-A shell, T2-B write,
   T2-D read, T4-D customInstructions) and confirmed on Bob IDE (mode picker + T2-D + T4-D).

**Non-goal:** Do not change any Python/Token Optimization System code or tests. Do not
alter the KB content files under `docs/knowledge-base/research|concepts|guides|references`.
Do not touch `docs/adr/` ADRs.

**Standard:** IBM Top-Tier institutional documentation quality:
- Every factual claim grounded in the actual file state.
- No stale references (`save_memory` as Bob IDE tool, `--no-interactive` flag, CLI-only
  `bob --chat-mode=` for IDE users).
- Consistent terminology: "Bob Shell CLI" for the terminal binary; "Bob IDE" for the
  VS Code/Cursor extension.
- Every code block tested or machine-verified.
- Cross-references between documents are bidirectional.

---

## Sub-Task 1 — README.md: Add Bob IDE as a first-class supported target

**Status:** `[x] done`

**Intent:**
README.md currently presents the project as CLI-only. It references `save_memory` without
qualification, shows only `bob --chat-mode=knowledge-manager` for activation, and never
mentions Bob IDE. After the session's work, Bob IDE is a fully supported target with its
own installation path (zero-step) and skill. The README is the project's front door and
must reflect this.

**Relevant context:**
- File: `README.md`
- High-impact lines: L5-13 (intro), L62-69 (mode description), L125-147 (quick-start block)
- The two-system table at L19-26 is the right pattern to extend.
- `.bob/custom_modes.yaml` and `.bob/skills/knowledge-manager/SKILL.md` are the new artefacts.

**Expected outcomes:**
- README has a clear "Supported targets" section or table distinguishing Bob Shell CLI and Bob IDE.
- `save_memory` is either removed or annotated as Bob Shell CLI-only.
- Bob IDE activation (`mode picker → 🧠 Mnemox Knowledge Builder`) is documented alongside
  `bob --chat-mode=knowledge-manager`.
- `.bob/skills/knowledge-manager/SKILL.md` is mentioned as the lazy-load skill for IDE.
- No broken cross-references introduced.

**Todo list:**
- [ ] Add a "Supported targets" row or section after the two-system table showing:
      CLI path (`scripts/install.sh` → `bob --chat-mode=`) vs IDE path (open workspace → mode picker).
- [ ] Replace or annotate every `save_memory` mention: state it is Bob Shell CLI-only;
      Bob IDE persists via markdown files.
- [ ] Add the Bob IDE activation method alongside the existing CLI activation block.
- [ ] Add a bullet point for `.bob/skills/knowledge-manager/SKILL.md` in the feature list.
- [ ] Verify all internal links still resolve after edits.

---

## Sub-Task 2 — AGENTS.md: Split Bob Shell Knowledge Manager section into CLI and IDE subsections

**Status:** `[x] done`

**Intent:**
AGENTS.md is the authoritative developer reference read by every agent at session start.
Its "Building and Running → Bob Shell Knowledge Manager" section (lines 61-95) covers only
CLI installation. IDE developers reading this will follow the wrong path. Since AGENTS.md
is auto-loaded into every Bob session, correctness here directly affects every future
knowledge-manager session.

**Relevant context:**
- File: `AGENTS.md`
- Section: "Building and Running → Bob Shell Knowledge Manager" (~L58-94)
- The `scripts/install.sh` commentary block now already documents the two targets;
  AGENTS.md should mirror that distinction.
- `.bob/custom_modes.yaml` entries and `.bob/skills/knowledge-manager/SKILL.md` must be
  mentioned as the IDE artefacts.

**Expected outcomes:**
- Section has two clearly labelled sub-sections: "Bob Shell CLI" and "Bob IDE".
- CLI sub-section: `scripts/install.sh`, `bob --chat-mode=knowledge-manager`.
- IDE sub-section: open workspace → mode picker → `🧠 Mnemox Knowledge Builder`; no install step;
  reference to `.bob/custom_modes.yaml` and `.bob/skills/knowledge-manager/SKILL.md`.
- Any `save_memory` references are annotated CLI-only.
- The `scripts/init-project.sh` heredoc fix is not explicitly documented here (it is an
  implementation detail) but the script usage remains accurate.

**Todo list:**
- [ ] Split "Building and Running → Bob Shell Knowledge Manager" into two sub-sections:
      "#### Bob Shell CLI" and "#### Bob IDE".
- [ ] Under Bob IDE: document zero-install path, mode picker activation, skill activation
      (`use_skill("knowledge-manager")`), and reference `.bob/custom_modes.yaml`.
- [ ] Annotate or remove `save_memory` from any instructions under Bob IDE sub-section.
- [ ] Confirm AGENTS.md "Key Components" list mentions `.bob/skills/knowledge-manager/SKILL.md`.

---

## Sub-Task 3 — docs/quick-start.md: Add Bob IDE activation path

**Status:** `[x] done`

**Intent:**
QUICK_START.md is the 5-minute onboarding guide. It currently has a single linear flow
(install → init → first doc) that assumes Bob Shell CLI. Bob IDE users have a zero-step
installation and a different activation method. The flowchart and Step 1 section must
branch explicitly.

**Relevant context:**
- File: `docs/quick-start.md`
- Mermaid flowchart: lines ~30-51 (flowchart TD Start → Q1 → S1 …)
- §3 "Step 1: Install the mode (~2 min)": CLI-only
- §7 Troubleshooting: CLI-only
- Prerequisites table: L57-63

**Expected outcomes:**
- Prerequisites table gains a "Bob IDE" row (VS Code / Cursor / Bob IDE extension).
- Flowchart branches at start: "Using Bob Shell CLI?" vs "Using Bob IDE?".
- Step 1 has a "Bob IDE users" callout box: "No install needed. Open the workspace →
  mode picker → 🧠 Mnemox Knowledge Builder. Then skip to Step 3."
- Troubleshooting section adds a "Bob IDE" sub-section with the mode-picker-not-showing fix
  (reload config or trivial edit of `.bob/custom_modes.yaml`).
- No existing CLI content removed.

**Todo list:**
- [ ] Add "Bob IDE" prerequisite row to the prerequisites table.
- [ ] Add a branch at the top of the flowchart for IDE vs CLI.
- [ ] Add a callout box at the start of §3 for IDE users with the zero-step path.
- [ ] Add "Bob IDE" troubleshooting sub-section in §7.
- [ ] Verify mermaid syntax is valid (no double-quotes inside square brackets).

---

## Sub-Task 4 — docs/installation.md: Add Bob IDE installation section

**Status:** `[x] done`

**Intent:**
INSTALLATION.md is the complete lifecycle installation reference. It currently covers only
`scripts/install.sh` and `scripts/init-project.sh`. A Bob IDE user who reads this will
attempt to run CLI scripts that are irrelevant to their workflow. A dedicated Bob IDE
section is needed, including scope clarification at the top.

**Relevant context:**
- File: `docs/installation.md`
- §1 scope header: L1-6
- Main install procedure: L32-50
- Verification steps: L206-209
- The `scripts/init-project.sh` heredoc fix (lines 23, 99) is an internal correctness
  fix; INSTALLATION.md should ensure usage instructions remain accurate but need not
  document the fix itself.

**Expected outcomes:**
- Scope header explicitly states: "Bob Shell CLI installation. For Bob IDE, see §X."
- New section "Bob IDE Installation" documents: open workspace, mode picker, `use_skill`,
  reference to `.bob/custom_modes.yaml` and `.bob/skills/knowledge-manager/SKILL.md`.
- Verification steps section adds IDE verification (mode picker shows 🧠 Mnemox Knowledge Builder;
  four validation prompts from the validation plan).
- `scripts/init-project.sh` usage instructions remain accurate (no `<< WORD` space in any
  documentation examples — but there were none; the fix was in the script itself).

**Todo list:**
- [ ] Add scope qualifier to §1: "This section covers Bob Shell CLI. Bob IDE users: see §X."
- [ ] Add new section "Bob IDE Installation" with: zero-step install, mode picker, skill
      activation, and `.bob/` artefact references.
- [ ] Update verification section to include Bob IDE verification steps.
- [ ] Add cross-reference back from new IDE section to QUICK_START.md.

---

## Sub-Task 5 — docs/usage.md: Add Bob IDE activation path and fix save_memory references

**Status:** `[x] done`

**Intent:**
USAGE.md documents four activation paths (A–D), all CLI. It contains multiple `save_memory`
references without qualification. IDE users reading this guide will find no path for their
environment and will believe `save_memory` is available to them. This is the highest-traffic
practical guide; the gap is HIGH priority.

**Relevant context:**
- File: `docs/usage.md`
- Paths A–D: lines ~37-87
- `save_memory` mentions: L98, L140, and elsewhere
- "Tool bindings" paragraph: L113-114

**Expected outcomes:**
- New "Path E — Bob IDE mode picker" section added after existing paths.
- Every `save_memory` reference qualified: "Bob Shell CLI only — Bob IDE uses file
  persistence (`write_file`) instead."
- "Tool bindings" paragraph updated to reflect that `save_memory` is not available in
  Bob IDE.
- No existing CLI paths altered.

**Todo list:**
- [ ] Add Path E: "Bob IDE — mode picker activation" with step-by-step instructions.
- [ ] Search for every `save_memory` occurrence and add inline qualifier or footnote.
- [ ] Update "Tool bindings" paragraph to list Bob IDE tools separately from CLI tools.
- [ ] Verify all internal anchors still resolve.

---

## Sub-Task 6 — docs/workflows.md and docs/customization.md: Scope annotations

**Status:** `[x] done`

**Intent:**
These two medium-priority files contain `save_memory` references and CLI-assumed workflows
that need scope annotations. Neither requires structural changes — only targeted inline
clarifications and a scope note at the top of each.

**Relevant context:**
- `docs/workflows.md`: `save_memory` at L89, L199, L290, L382, L545; all workflows assume CLI.
- `docs/customization.md`: scope header assumes CLI; resolution chain diagram missing IDE level.

**Expected outcomes:**
- Each file has a scope note in its header: "These instructions apply to Bob Shell CLI.
  For Bob IDE, group names differ (`execute`/`skill` vs `command`/`browser`) and
  `save_memory` is not available."
- Every `save_memory` occurrence in both files is annotated CLI-only.
- CUSTOMIZATION.md resolution chain adds a note about Bob IDE workspace-level
  `.bob/custom_modes.yaml` being the IDE equivalent.

**Todo list:**
- [ ] Add scope note to top of `docs/workflows.md`.
- [ ] Annotate all `save_memory` references in `docs/workflows.md` as CLI-only.
- [ ] Add scope note to top of `docs/customization.md`.
- [ ] Add IDE note to resolution chain diagram in `docs/customization.md`.

---

## Sub-Task 7 — docs/ARCHITECTURE.md and docs/index.md: Low-priority cross-reference updates

**Status:** `[x] done`

**Intent:**
These files need minor additions only: a cross-reference to the new `.bob/skills/`
artefact in ARCHITECTURE.md, and a navigation note for IDE users in docs/index.md.

**Relevant context:**
- `docs/ARCHITECTURE.md`: L5-8 scope, L84 memory constraint.
- `docs/index.md`: L1-6 navigation header.

**Expected outcomes:**
- ARCHITECTURE.md scope section adds: "Bob IDE-compatible implementation:
  `.bob/skills/knowledge-manager/SKILL.md`."
- ARCHITECTURE.md memory constraint (L84) notes: "CLI: `save_memory` tool; IDE:
  file persistence only."
- docs/index.md navigation header adds a sentence: "Bob IDE users: the Knowledge Manager
  mode and skill are in `.bob/custom_modes.yaml` and `.bob/skills/knowledge-manager/SKILL.md`."

**Todo list:**
- [ ] Add IDE cross-reference to scope section in `docs/ARCHITECTURE.md`.
- [ ] Update memory constraint note in `docs/ARCHITECTURE.md`.
- [ ] Add IDE navigation sentence to `docs/index.md`.


## Sub-Task 8 — docs/COMPARISON.md: Completeness check and CLI vs IDE comparison

**Status:** `[x] done`

**Intent:**
The subagent found no critical gaps in COMPARISON.md, but it predates the Bob IDE port.
A completeness check is required and, if the file compares Bob Shell features against
LLM-Wiki or other tools, a row for "Bob IDE support" should be added. Additionally, this
is the natural home for the canonical CLI vs IDE comparison table that no other file
currently contains.

**Relevant context:**
- File: `docs/COMPARISON.md`
- Read the file first to establish its current structure before deciding what to add.
- Confirmed facts for the comparison table (all machine-verified this session):

| Dimension | Bob Shell CLI | Bob IDE |
|---|---|---|
| Installation | `scripts/install.sh` → `~/.bob/custom_modes.yaml` | Open workspace — zero steps |
| Mode activation | `bob --chat-mode=knowledge-manager` | Mode picker → 🧠 Mnemox Knowledge Builder |
| Shell group name | `command` | `execute` |
| Web group name | `browser` | not supported |
| Skill lazy-load | not supported | `skill` group + `use_skill()` |
| `save_memory` tool | available | not available |
| Knowledge persistence | `save_memory` + markdown files | markdown files only |
| Config file | `~/.bob/custom_modes.yaml` | `.bob/custom_modes.yaml` (workspace) |
| Hot-reload | restart required | immediate |
| Validation flag | `-p "prompt"` | N/A (mode picker) |

**Expected outcomes:**
- COMPARISON.md retains all existing content unchanged.
- A "Bob Shell CLI vs Bob IDE" section or table is added using the verified facts above.
- If the file already has a feature comparison table, a "Bob IDE" column is added.
- No claims made that are not machine-verified.

**Todo list:**
- [x] Read `docs/COMPARISON.md` in full before writing anything.
- [x] Determine whether to add a new section or extend an existing table.
- [x] Add CLI vs IDE comparison using only the verified facts from the table above.
- [x] Verify no broken internal links introduced.

**Completion note (2026-07-16):** New section "Bob Shell CLI vs Bob IDE" added to
`docs/archive/COMPARISON.md` (lines 84–101 in the patched file) with all 11 verified
dimensions from the session table and a machine-verification note. All existing content
preserved unchanged.

---

## Sub-Task 9 — docs/bob-ide-guide.md: Create canonical Bob IDE reference document

**Status:** `[x] done`

**Intent:**
No single document currently describes the Bob IDE experience end-to-end. Sub-Tasks 1–7
add cross-references to it; this sub-task creates the document they point to. It is the
IDE equivalent of QUICK_START.md + INSTALLATION.md combined, written specifically for
the Bob IDE context.

**Relevant context:**
- New file: `docs/bob-ide-guide.md`
- All facts below are machine-verified in this session on Bob IDE 1.121.0+bob2.0.1:
  - Workspace modes: `.bob/custom_modes.yaml` (appended — 68+2 modes, hot-reload)
  - Groups: `execute`, `skill` (not `command`/`browser`)
  - Skill: `.bob/skills/knowledge-manager/SKILL.md` (name=knowledge-manager, 9 triggers)
  - Mode picker: bottom-left status bar, shows 🧠 Mnemox Knowledge Builder
  - Validation: T2-A (shell), T2-D (read), T4-D (customInstructions) all confirmed pass
  - `save_memory` not available; file persistence via `write_file` only
  - MCP errors at startup (external-llm, swift-info, carbon-mcp, techzone, atlassian)
    are pre-existing and do not affect knowledge-manager mode operation

**Expected outcomes:**
- `docs/bob-ide-guide.md` exists with the following sections:
  1. Overview — what Bob IDE mode support provides vs Bob Shell CLI
  2. Prerequisites — Bob IDE version, workspace requirements
  3. Installation — zero-step; confirm `.bob/custom_modes.yaml` is present
  4. Activation — mode picker location, scrolling to 🧠 Mnemox Knowledge Builder
  5. Tool groups — `execute`, `skill`, `read`, `edit[\.md$]` and what each enables
  6. Skill activation — `use_skill("knowledge-manager")`, when to call it, what it loads
  7. Persistence — no `save_memory`; write to `docs/knowledge-base/`; commit to git
  8. Validation prompts — the four verified prompts with expected outputs
  9. Known limitations — MCP startup errors (pre-existing, harmless); fileRegex
     enforcement informational; no `browser` group
  10. Troubleshooting — mode not in picker (reload config); wrong mode active
- Document uses only verified facts; no speculative claims.
- Cross-references to README.md, QUICK_START.md, and INSTALLATION.md are included.

**Todo list:**
- [ ] Create `docs/bob-ide-guide.md` with all 10 sections above.
- [ ] Use only machine-verified facts (no claims about untested behaviour).
- [ ] Add cross-reference from this file back to QUICK_START.md and INSTALLATION.md.
- [ ] Ensure README.md Sub-Task 1 link target matches the filename created here.

---


---

## Consistency Rules (apply across all sub-tasks)

These rules must hold across every file touched. Check each before marking a sub-task done.

| Rule | Requirement |
|---|---|
| Terminology | "Bob Shell CLI" for the terminal binary; "Bob IDE" for VS Code/Cursor extension |
| Group names | CLI files: `command`/`browser`; IDE files: `execute`/`skill` |
| save_memory | Never presented as available in Bob IDE; always annotated CLI-only |
| Activation | CLI: `bob --chat-mode=knowledge-manager`; IDE: mode picker → 🧠 Mnemox Knowledge Builder |
| Skill reference | `.bob/skills/knowledge-manager/SKILL.md` referenced wherever IDE workflow is described |
| No broken links | Every internal `[text](path)` link verified to resolve after edits |
| Code blocks tested | No new code block added unless the command has been verified in the session |

---

## Validation Checklist (run after all sub-tasks complete)

```bash
# 1. No stale save_memory instructions in docs (negating prose is allowed)
grep -rn "save_memory" docs/ README.md AGENTS.md \
  | grep -v "CLI-only\|not available\|no save_memory\|Bob Shell CLI"

# 2. No --no-interactive flag referenced anywhere
grep -rn "\-\-no-interactive" docs/ README.md AGENTS.md scripts/

# 3. All internal markdown links resolve
python3 -c "
import re, os, sys
issues = []
for root, dirs, files in os.walk('docs'):
    dirs[:] = [d for d in dirs if d not in ['assets','deprecated']]
    for fname in files:
        if not fname.endswith('.md'): continue
        fpath = os.path.join(root, fname)
        with open(fpath) as f: content = f.read()
        for link in re.findall(r'\[.*?\]\(([^)]+)\)', content):
            if link.startswith('http') or link.startswith('#'): continue
            target = os.path.normpath(os.path.join(os.path.dirname(fpath), link))
            if not os.path.exists(target):
                issues.append(f'{fpath}: broken link -> {link}')
for i in issues: print(i)
print('OK' if not issues else f'{len(issues)} broken links')
"

# 4. .bob/skills/knowledge-manager/SKILL.md is referenced in at least README and AGENTS.md
grep -l "knowledge-manager/SKILL" README.md AGENTS.md docs/quick-start.md \
  docs/installation.md docs/usage.md
```
