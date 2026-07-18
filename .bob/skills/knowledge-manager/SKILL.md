---
name: knowledge-manager
description: >
  Full workflow instructions for the Mnemox Knowledge Builder mode -- document
  templates, naming conventions, cross-reference protocol, INDEX.md maintenance,
  and the mnemox workspace command.
  Use when creating or updating knowledge base content in Bob IDE or Bob Shell CLI.
triggers:
  - "create a concept document"
  - "create a guide"
  - "create a reference document"
  - "write a research note"
  - "update the knowledge base"
  - "update INDEX.md"
  - "add to the knowledge base"
  - "document this in the KB"
  - "knowledge base template"
  - "mnemox your workspace"
  - "mnemox this workspace"
  - "mnemox this project"
  - "mnemox"
  - "initialise mnemox"
---

# Knowledge Manager Skill

This skill provides the full template corpus and workflow protocol for the
`knowledge-manager` Bob IDE mode. Activate it when creating or updating any
knowledge base document.

---

## Document Templates

### Concept (`docs/knowledge-base/concepts/concept-name.md`)

````markdown
---
title: "[Concept Name]"
category: concept
tags: [tag1, tag2, compact-summary]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# [Concept Name]

## Overview
Brief description of the concept (2-3 sentences).

## Key Points
- Main idea 1
- Main idea 2
- Main idea 3

## Details

### Subsection 1
Detailed explanation...

### Subsection 2
More details...

## Examples

### Example 1: [Scenario]
```
Code or command example
```

Explanation of the example.

## Related Documents
- [Related Concept 1](./related-concept-1.md)
- [Related Guide](../guides/related-guide.md)

## References
- [External Source 1](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Concept*
````

---

### Guide (`docs/knowledge-base/guides/task-name-guide.md`)

````markdown
---
title: "[Task Name] Guide"
category: guide
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# [Task Name] Guide

## Overview
Brief description of what this guide covers and who it's for.

## Prerequisites
- Prerequisite 1
- Prerequisite 2

## Steps

### Step 1: [Action]
Detailed instructions.

```bash
# Example command
command --option value
```

### Step 2: [Action]
Detailed instructions.

## Verification
How to verify the task completed successfully:

```bash
verify-command
```

Expected output:
```
Expected result
```

## Troubleshooting

### Issue 1: [Problem Description]
**Symptoms**: What you see.
**Cause**: Why this happens.
**Solution**: How to fix it.

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](./related-guide.md)

## References
- [Official Documentation](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Guide*
````

---

### Reference (`docs/knowledge-base/references/api-name-reference.md`)

````markdown
---
title: "[API/Component Name] Reference"
category: reference
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# [API/Component Name] Reference

## Overview
Brief description of what this reference covers.

## API Endpoints / Components

### Endpoint/Component 1
**Description**: What it does.

**Parameters**:
- `param1` (type): Description
- `param2` (type): Description

**Returns**: Description of return value.

**Example**:
```
Example usage
```

### Endpoint/Component 2
**Description**: What it does.

**Parameters**:
- `param1` (type): Description

**Returns**: Description of return value.

**Example**:
```
Example usage
```

## Common Patterns

### Pattern 1: [Use Case]
```
Example code
```

### Pattern 2: [Use Case]
```
Example code
```

## Error Handling

### Error 1: [Error Code/Name]
**Cause**: Why this error occurs.
**Solution**: How to handle it.

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](../guides/related-guide.md)

## References
- [Official API Documentation](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Reference*
````

---

### Research (`docs/knowledge-base/research/topic-YYYY-MM.md`)

````markdown
---
title: "[Topic] Research - [Month YYYY]"
category: research
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# [Topic] Research - [Month YYYY]

## Objective
What we're researching and why.

## Background
Context and motivation.

## Findings

### Finding 1: [Title]
Description.

**Evidence**:
- Data point 1

## Analysis

### Interpretation
What the findings mean.

### Implications
How this affects our work.

## Conclusions

### Recommendations
1. Recommendation 1

### Next Steps
- Action item 1

## Sources
- [Source 1](https://example.com)

## Related Documents
- [Related Concept](../concepts/related-concept.md)

---
*Last Updated: YYYY-MM-DD*
*Category: Research*
````

---

## Cross-Reference Protocol

Every document must link **bidirectionally**:

1. When you add a link from document A to document B, open document B and add the
   reciprocal link back to A under its **Related Documents** section.
2. Use relative paths from the document's own directory:
   - `../concepts/name.md` from guides/
   - `../guides/name.md` from concepts/
   - `./sibling.md` within the same folder

---

## INDEX.md Maintenance

After creating or updating any document, add or refresh its entry in
`docs/knowledge-base/INDEX.md` under the correct category heading:

````markdown
## Concepts
- [Concept Name](concepts/concept-name.md) - One-line description

## Guides
- [Task Name Guide](guides/task-name-guide.md) - One-line description

## References
- [API Name Reference](references/api-name-reference.md) - One-line description

## Research
- [Topic YYYY-MM](research/topic-YYYY-MM.md) - One-line description
````

---

## Knowledge Graph Rebuild (mandatory after every KB write)

After updating INDEX.md, always rebuild the knowledge graph so the new document
is discoverable via semantic search and PageRank re-ranking:

```bash
uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
```

This is not optional — a document written to disk but not indexed is invisible to
`bob-optimize kb-search` and to any mode querying the graph. The rebuild takes
~5 seconds and is idempotent.

---

## Naming Conventions (quick reference)

| Category  | File name pattern          | Example                     |
|-----------|----------------------------|-----------------------------|
| Concept   | `concept-name.md`          | `token-caching.md`          |
| Guide     | `task-name-guide.md`       | `setup-kb-guide.md`         |
| Reference | `api-name-reference.md`    | `cache-api-reference.md`    |
| Research  | `topic-YYYY-MM.md`         | `delegation-2026-07.md`     |

---

## Persistence note (Bob IDE)

Bob IDE has no `save_memory` tool. All knowledge persistence is achieved by
writing markdown files to `docs/knowledge-base/`. Commit those files to git so they
survive across sessions and team members can benefit from them.

---

## Mnemox Command Protocol

When the user types `mnemox`, `mnemox your workspace`, `mnemox this workspace`,
`mnemox this project`, or `initialise mnemox`, follow this protocol:

### Step 1 — Detect mode

Check whether `docs/knowledge-base/INDEX.md` exists in the project root (or in
`$MNEMOX_HOME` if set).

- **File absent** → **Init path** (first-time setup)
- **File present** → **Update path** (ongoing refresh)

### Step 2a — Init path (fresh workspace)

1. Tell the user: *"No KB found — initialising Mnemox for this workspace."*
2. Call `scripts/init-project.sh` via `execute_command`.
3. Call `scripts/run-full-analysis.sh` via `execute_command`.
4. Call `scripts/validate-kb.sh` via `execute_command`.
5. Confirm: *"Workspace Mnemoxed. docs/knowledge-base/ is scaffolded and the
   7-phase analysis has been filed. Start a new 🧠 Mnemox Knowledge Builder
   session to query results."*
6. **Do not** auto-commit on the init path.

### Step 2b — Update path (existing KB)

The update path has two sub-modes — choose based on what the user typed:

| Trigger | Sub-mode | What runs |
|---|---|---|
| `mnemox` / `mnemox your workspace` / `--update` | **full** (default) | analysis + lessons + graph + commit |
| `mnemox --quick` / "quick" / "no analysis" | **quick** | lessons + graph + commit only |
| `mnemox --full` / "full" | **full** (explicit) | analysis + lessons + graph + commit |

**Full update steps:**
1. Tell the user: *"KB found — running full Mnemox update (analysis + lessons + graph + commit)."*
2. Call `bash scripts/mnemox.sh --full` via `execute_command`. This runs all 4 steps.
3. Parse `MNEMOX_LESSONS_NOTE=<path>` from the last matching stdout line.
4. **Synthesise lessons in this session**: read `<path>`, present top 3–5 findings immediately.

**Quick update steps:**
1. Tell the user: *"KB found — running quick Mnemox update (lessons + graph + commit, no analysis)."*
2. Call `bash scripts/mnemox.sh --quick` via `execute_command`. This runs Steps 2–4 only.
3. Parse `MNEMOX_LESSONS_NOTE=<path>` from the last matching stdout line.
4. **Synthesise lessons in this session**: read `<path>`, present top 3–5 findings immediately.

### MNEMOX_HOME resolution order

1. Environment variable `MNEMOX_HOME` if set.
2. Flag `--km-home <path>` if the user included it.
3. Current working directory (auto-detect).

### Idempotency guarantee

Every step is idempotent. Running `mnemox` twice on the same workspace is safe:
the init path creates structure only if absent; the update path only files
new dated snapshots (never overwrites prior KB work).
