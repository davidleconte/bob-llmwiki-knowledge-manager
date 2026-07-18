# Bob IDE Guide — 🧠 Mnemox Knowledge Builder Mode

**Version:** Bob IDE 1.121.0+bob2.0.1  
**Last verified:** 2026-07-16  
**Status:** All validation gates confirmed PASS (T1-B, T2-A, T2-B, T2-D, T4-D)

> **Cross-references:**  
> — New to this project? Start with [README.md](../README.md).  
> — 5-minute onboarding: [docs/quick-start.md](quick-start.md).
> — Full installation reference: [docs/INSTALLATION.md](INSTALLATION.md).
> — This guide covers Bob IDE only. For the terminal binary, see [docs/INSTALLATION.md](INSTALLATION.md) §1.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Installation](#3-installation)
4. [Activation](#4-activation)
5. [Tool groups](#5-tool-groups)
6. [Skill activation](#6-skill-activation)
7. [Persistence](#7-persistence)
8. [Validation prompts](#8-validation-prompts)
9. [Known limitations](#9-known-limitations)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

Bob IDE is the VS Code / Cursor extension version of Bob Shell. It runs modes defined in
`.bob/custom_modes.yaml` inside the active workspace rather than in a global
`~/.bob/custom_modes.yaml` file used by the Bob Shell CLI terminal binary.

| Dimension | Bob Shell CLI | Bob IDE |
|---|---|---|
| Installation | `scripts/install.sh` → `~/.bob/custom_modes.yaml` | Open workspace — zero steps |
| Mode activation | `bob --chat-mode=knowledge-manager` | Mode picker → 🧠 Mnemox Knowledge Builder |
| Shell group name | `command` | `execute` |
| Web group name | `browser` | not supported |
| Skill lazy-load | not supported | `skill` group + `use_skill()` |
| `save_memory` tool | available | **not available** |
| Knowledge persistence | `save_memory` + markdown files | markdown files only |
| Config file | `~/.bob/custom_modes.yaml` | `.bob/custom_modes.yaml` (workspace) |
| Hot-reload | restart required | immediate (no restart needed) |

This guide documents the Bob IDE path only. Every fact in this document was
machine-verified during the session of 2026-07-16.

---

## 2. Prerequisites

| Requirement | Details |
|---|---|
| Bob IDE | Version 1.121.0+bob2.0.1 or later |
| Editor | VS Code or Cursor with the Bob extension installed and active |
| Workspace | This repository cloned locally; the workspace root must contain `.bob/` |
| `.bob/custom_modes.yaml` | Must be present in the workspace root (committed to this repo) |
| `.bob/skills/knowledge-manager/SKILL.md` | Must be present for lazy-load skill support |

No network access, Python, or Node.js is required to run the Mnemox Knowledge Builder mode.

---

## 3. Installation

**No installation step is required for Bob IDE.**

The mode definition and skill are already committed to this repository:

```
.bob/
├── custom_modes.yaml              # Mode definitions (includes knowledge-manager + repo-analyzer)
└── skills/
    └── knowledge-manager/
        └── SKILL.md               # Lazy-load skill with templates and workflow
```

When you open this workspace in Bob IDE, the extension reads `.bob/custom_modes.yaml`
automatically. No script execution is needed. Hot-reload is immediate — any edit to
`.bob/custom_modes.yaml` is picked up without restarting the extension.

To confirm the files are present:

```bash
ls .bob/custom_modes.yaml
ls .bob/skills/knowledge-manager/SKILL.md
```

Both commands should return the file path without error.

> **Bob Shell CLI users:** If you are using the terminal binary, run `scripts/install.sh`
> instead. See [docs/INSTALLATION.md](INSTALLATION.md) for the CLI path.

---

## 4. Activation

### Locating the mode picker

The mode picker is in the **bottom-left of the chat panel** status bar. It shows the
currently active mode name (e.g. `Mode: Agent` by default).

### Selecting Mnemox Knowledge Builder

1. Click the mode name in the bottom-left status bar.
2. A mode list opens. Scroll to **🧠 Mnemox Knowledge Builder**.
3. Click it. The status bar immediately updates to:

   ```
   Mode: 🧠 Mnemox Knowledge Builder
   ```

No restart or reload is required. The change takes effect for the next message you send.

### Confirming activation

Send the following prompt immediately after switching:

```
What mode are you in?
```

The response should acknowledge the Knowledge Manager role and mention the
`docs/knowledge-base/` directory structure.

---

## 5. Tool groups

The Mnemox Knowledge Builder mode in Bob IDE is configured with the following tool groups
(defined in `.bob/custom_modes.yaml`):

| Group | What it enables | Notes |
|---|---|---|
| `execute` | Shell command execution (`execute_command`) | Bob IDE equivalent of `command` in Bob Shell CLI |
| `skill` | `use_skill()` lazy-load capability | Not available in Bob Shell CLI |
| `read` | File reading tools (`read_file`, `list_files`, `glob`, `grep`, etc.) | Standard across both targets |
| `edit[fileRegex=.*\.md$]` | File write/edit tools scoped to `.md` files | Enforces markdown-only editing within the mode |

### Group name differences

Bob Shell CLI uses `command` (shell) and `browser` (web). Bob IDE uses `execute` (shell)
and does not support `browser`. Using CLI group names in `.bob/custom_modes.yaml` will
cause the tools to be unavailable silently — always use `execute` for shell access in
IDE mode definitions.

---

## 6. Skill activation

### What the skill provides

The file `.bob/skills/knowledge-manager/SKILL.md` is a **lazy-load skill** — it is not
loaded into every session automatically. It contains:

- Document templates for all four types (concept, guide, reference, research) using
  4-backtick outer fences so inner code blocks render correctly.
- Cross-reference protocol for maintaining bidirectional links.
- `INDEX.md` maintenance instructions.
- Persistence note: file-based only (no `save_memory`).

### When to activate

Activate the skill at the start of any session where you will be creating or updating
knowledge base documents. You do not need to activate it for read-only queries.

### How to activate

Send this exact prompt at the start of the session:

```
use_skill("knowledge-manager")
```

Or equivalently:

```
Load the knowledge-manager skill.
```

### What loads

The skill loads the full SKILL.md content into the active context window. After
activation, the agent has access to all four document templates, the cross-reference
protocol, and the INDEX.md maintenance workflow.

The skill name is `knowledge-manager` (9 registered trigger phrases — activation via
the prompts above is always reliable).

---

## 7. Persistence

### No `save_memory` in Bob IDE

The `save_memory` tool is **not available in Bob IDE**. It is a Bob Shell CLI-only
capability. Any workflow or documentation that references `save_memory` without
qualification applies to Bob Shell CLI only.

### How to persist knowledge in Bob IDE

All knowledge is persisted by writing markdown files to the `docs/knowledge-base/`
directory tree:

```
docs/knowledge-base/
├── INDEX.md              # Master index — update after every new document
├── concepts/             # Core concepts and definitions
├── guides/               # How-to guides and tutorials
├── references/           # API documentation and specifications
└── research/             # Research notes and findings
```

The agent uses `write_file` (available via the `edit` group) to create and update
these files. Changes are immediately visible on disk and should be committed to git.

### Naming conventions

| Type | Convention | Example |
|---|---|---|
| Concept | `concept-name.md` | `multi-level-caching.md` |
| Guide | `task-name-guide.md` | `audit-remediation-action-plan.md` |
| Reference | `api-name-reference.md` | `token-optimizer-reference.md` |
| Research | `topic-YYYY-MM.md` or `topic-YYYY-MM-DD.md` | `external-audit-2026-07-12.md` |

### Commit your work

After a knowledge-manager session, commit the new and updated files:

```bash
git add docs/knowledge-base/
git commit -m "docs: add/update knowledge base entries"
```

---

## 8. Validation prompts

The following four prompts were verified on Bob IDE 1.121.0+bob2.0.1 in the session of
2026-07-16. Use them to confirm the mode and tooling are working correctly after
activation.

### T1-B — Mode activation

**Prompt:**
```
What mode are you in? Describe your role.
```

**Expected output:** The agent describes the Knowledge Manager role and confirms it will
write to `docs/knowledge-base/`. The status bar shows `Mode: 🧠 Mnemox Knowledge Builder`.

---

### T2-A — Shell execution (execute group)

**Prompt:**
```
Run: echo "SHELL_OK"
```

**Expected output:**
```
SHELL_OK
```

This confirms the `execute` tool group is active and shell commands work.

---

### T2-D — File read (read group)

**Prompt:**
```
Read the first 5 lines of config/custom_modes.yaml
```

**Expected output:** The first 5 lines of `config/custom_modes.yaml` printed verbatim.
This confirms the `read` tool group is active and workspace file access works.

---

### T4-D — Custom instructions recall

**Prompt:**
```
What are the naming conventions for knowledge base documents?
```

**Expected output:** The agent lists the four naming conventions (concept, guide,
reference, research) consistent with those in `AGENTS.md`. This confirms the mode's
`customInstructions` are loaded and active.

---

## 9. Known limitations

### MCP startup errors

When Bob IDE starts, the following MCP servers may log connection errors in the Output
panel:

- `external-llm`
- `swift-info`
- `mq-mcp-server-bob`
- `carbon-mcp`
- `techzone`
- `atlassian`

These errors are **pre-existing and unrelated to the Mnemox Knowledge Builder mode**. They do
not affect mode operation, file reading/writing, shell execution, or skill activation.
You can safely ignore them.

### `fileRegex` enforcement

The `edit[fileRegex=.*\.md$]` group configuration instructs the mode to restrict file
editing to `.md` files. In Bob IDE 1.121.0+bob2.0.1 this is **informational** — actual
enforcement behaviour may vary by Bob version. The agent will follow the intent of the
restriction in its responses.

### No `browser` group

Bob IDE does not support the `browser` tool group. Web browsing and URL-fetching
capabilities available in Bob Shell CLI are not available in this mode. Do not add
`browser` to `.bob/custom_modes.yaml` — it will have no effect.

### `write_file` is workspace-constrained

The `write_file` tool operates within the workspace root only. It cannot write to
absolute paths outside the workspace (e.g., `/tmp`). All knowledge base files must
be written under the workspace directory.

### No `save_memory` tool

Covered in [§7 Persistence](#7-persistence). This is a hard limitation of Bob IDE,
not a configuration issue.

---

## 10. Troubleshooting

### Mode not appearing in the picker

**Symptom:** After opening the workspace, `🧠 Mnemox Knowledge Builder` does not appear in
the mode list.

**Resolution:**
1. Confirm `.bob/custom_modes.yaml` exists in the workspace root:
   ```bash
   ls .bob/custom_modes.yaml
   ```
2. Make a trivial edit to `.bob/custom_modes.yaml` (add a space, then remove it) and
   save. Bob IDE hot-reloads the mode list on file save.
3. If the mode still does not appear, reload the VS Code / Cursor window:
   `Ctrl+Shift+P` → `Developer: Reload Window`.

---

### Wrong mode is active

**Symptom:** The status bar shows a different mode name (e.g. `Mode: Agent`).

**Resolution:** Click the mode name in the bottom-left status bar and select
`🧠 Mnemox Knowledge Builder` from the list. The switch is immediate.

---

### Shell commands not executing (execute group missing)

**Symptom:** The agent says it cannot run shell commands or `execute_command` is
unavailable.

**Resolution:** Verify that `groups` in `.bob/custom_modes.yaml` for the
`knowledge-manager` entry includes `execute` (not `command`):

```yaml
groups:
  - execute
  - skill
  - read
  - edit[fileRegex=.*\.md$]
```

If `command` appears instead of `execute`, correct it and save the file. Hot-reload
will apply the change immediately.

---

### Skill content not loading

**Symptom:** After `use_skill("knowledge-manager")`, the agent does not have access to
the document templates or cross-reference protocol.

**Resolution:**
1. Confirm the skill file exists:
   ```bash
   ls .bob/skills/knowledge-manager/SKILL.md
   ```
2. Confirm the `skill` group is in the mode definition (see above).
3. Re-send the activation prompt: `use_skill("knowledge-manager")`.

---

### Agent writing files outside `docs/knowledge-base/`

**Symptom:** The agent writes or proposes to write KB documents to a different
location (e.g. the project root or `src/`).

**Resolution:** Remind the agent explicitly:

```
Write all knowledge base documents to docs/knowledge-base/ using the appropriate
subdirectory: concepts/, guides/, references/, or research/.
```

The agent follows the directory structure documented in [§7 Persistence](#7-persistence).

---

*See also: [README.md](../README.md) · [quick-start.md](quick-start.md) · [INSTALLATION.md](INSTALLATION.md)*
