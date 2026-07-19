---
title: "Obsidian Integration Guide"
category: guide
tags: [obsidian, knowledge-graph, mcp, dataview, canvas, export]
created: 2026-07-19
updated: 2026-07-19
status: active
---

# Obsidian Integration Guide

## Overview

Two features bring the Mnemox knowledge graph into Obsidian:

1. **Semantic graph export** — generates an Obsidian vault from `docs/knowledge-base/` with a Canvas file visualising all 109 nodes and 4 589 edges, plus Dataview frontmatter on every document so semantic neighbours are queryable.
2. **Obsidian MCP in Bob IDE** — registers the `obsidian-mcp` server in `.bob/mcp.json` so Bob IDE can read, search, and write KB documents directly through Obsidian's Local REST API.

The live `docs/knowledge-base/` is **never modified** by the export. All export output lands in `kb-export/`.

---

## Feature 1 — Semantic Graph Export to Obsidian

### Prerequisites

- Python 3.11+
- [Obsidian](https://obsidian.md) 1.1+ (Canvas support requires 1.1+)
- Obsidian [Dataview](https://github.com/blacksmithgu/obsidian-dataview) community plugin (for querying `semantic_links`)

### One-command export

```bash
./scripts/export-kb.sh obsidian-graph
```

This runs three steps in sequence:
1. Copies `docs/knowledge-base/` → `kb-export/knowledge-base/` and creates `.obsidian/app.json`
2. Generates `kb-export/kb-semantic-graph.canvas` — the full semantic graph as an Obsidian Canvas file
3. Injects `semantic_links:` Dataview frontmatter into every document in `kb-export/knowledge-base/`

### What the export produces

| Artefact | Location | What it contains |
|---|---|---|
| KB vault copy | `kb-export/knowledge-base/` | Full copy of all 110 KB documents |
| Obsidian config | `kb-export/.obsidian/app.json` | Minimal vault settings |
| Canvas file | `kb-export/kb-semantic-graph.canvas` | 109 nodes · 4 589 edges |
| Dataview annotations | In every `.md` in `kb-export/` | `semantic_links:` YAML list |

**Canvas edge colours:**
- 🟢 Green (`"2"`) — explicit links (author-stated cross-references)
- 🔵 Blue (`"4"`) — semantic edges (MiniLM cosine similarity ≥ 0.30)
- 🔴 Red (`"1"`) — broken links (target document missing)

**Canvas layout:** nodes are sub-clustered by their first tag within four columns (concepts · guides · references · research).

### Opening the vault in Obsidian

1. In Obsidian: **File → Open Folder as Vault**
2. Navigate to and select the `kb-export/` directory
3. Obsidian opens the vault with Graph View, backlinks, and tags all working from the Markdown link structure

### Using the Canvas file

1. In the Obsidian file tree, open `kb-semantic-graph.canvas`
2. The full Mnemox knowledge graph renders visually — pan and zoom to explore
3. Semantic edges (blue) connect documents with MiniLM similarity ≥ 0.30; the edge label shows the cosine weight (e.g. `0.41`)

### Querying semantic neighbours with Dataview

Install the Dataview plugin, then create a note in the vault with:

```dataview
TABLE semantic_links FROM "knowledge-base/concepts"
WHERE length(semantic_links) > 0
SORT file.name ASC
```

Each document's `semantic_links:` frontmatter lists its semantic neighbours:

```yaml
semantic_links:
  - doc: "concepts/multi-level-caching.md"
    weight: 0.61
  - doc: "research/phase2-performance-baseline-results.md"
    weight: 0.52
```

### Advanced options

Control the Dataview annotation density:

```bash
# Cap at top 5 semantic neighbours per document
python3 scripts/export-kb-graph-dataview.py --top-n 5

# Raise the similarity threshold (only high-confidence links)
python3 scripts/export-kb-graph-dataview.py --min-weight 0.45
```

### Refreshing the export

The export is a snapshot. After KB changes, re-run:

```bash
./scripts/export-kb.sh obsidian-graph
```

The previous `kb-export/` is overwritten. `docs/knowledge-base/` is never touched.

---

## Feature 2 — Obsidian MCP in Bob IDE

### Prerequisites

- [Node.js](https://nodejs.org) 18+ (for `npx`)
- Obsidian installed with the **Local REST API** community plugin enabled
- The Obsidian vault open and the plugin server running on port 27123

### Step-by-step activation

**Step 1 — Install the Local REST API plugin in Obsidian**

1. Obsidian → Settings → Community Plugins → Browse
2. Search for **"Local REST API"**
3. Install and enable it
4. Open its settings; copy the **API Key** shown in the panel

**Step 2 — Configure the MCP entry**

Open `.bob/mcp.json` and replace the placeholder:

```json
"OBSIDIAN_API_KEY": "YOUR-OBSIDIAN-LOCAL-REST-API-KEY-HERE"
```

with the API key you copied. The entry is already `"disabled": false` — no other change needed for basic use.

> ⚠️ **Machine-specific path:** `OBSIDIAN_VAULT_PATH` is committed as `"docs/knowledge-base"` (relative). Some versions of `obsidian-mcp` require an absolute path. If so, expand it locally:
> ```json
> "OBSIDIAN_VAULT_PATH": "/absolute/path/to/docs/knowledge-base"
> ```
> **Do not commit an absolute path** — it is machine-specific. Keep the relative value in the repo.

**Step 3 — Open the vault in Obsidian**

Point Obsidian at `docs/knowledge-base/` as a vault (or a parent folder). The Local REST API plugin server must be running (check the plugin status bar icon).

**Step 4 — Use it in Bob IDE**

The MCP is now active. Bob IDE can call the following tools:

| Tool | What it does |
|---|---|
| `list-files` | List all files in the vault |
| `get-file` | Read a KB document by path |
| `search` | Full-text search across the vault |
| `create-file` | Write a new KB document |
| `update-file` | Overwrite an existing KB document |
| `append-to-file` | Append content to a KB document |
| `delete-file` | Delete a KB document |

### Example Bob IDE prompts

```
Search my Obsidian KB for documents about caching strategies.
```

```
Read the knowledge-manager concept document and summarise the key points.
```

```
Create a new research note in Obsidian called "findings-2026-07-19.md" with today's session summary.
```

### Known limitation

`obsidian-mcp` connects to Obsidian's Local REST API, which only runs when Obsidian is open. If Obsidian is closed, all MCP tool calls will fail silently or return errors. This is expected — Bob IDE degrades gracefully.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Canvas file does not open | Obsidian version < 1.1 | Update Obsidian |
| `semantic_links` not visible in Dataview | Dataview plugin not installed | Install it from Community Plugins |
| MCP tools fail with connection error | Obsidian not open / plugin server not running | Open Obsidian and check plugin status |
| MCP tools fail with auth error | Wrong API key | Re-copy from Local REST API plugin settings |
| Export produces 0 nodes | `.bob/kb-graph.json` missing | Run `uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic` first |

---

## Related Documents

- [Knowledge Graph Layer](../concepts/knowledge-graph-layer.md)
- [Mnemox CLI Reference](../references/mnemox-cli-reference.md)
- [bob-optimize CLI Reference](../references/bob-optimize-cli-reference.md)

---
*Last Updated: 2026-07-19*
*Category: Guide*
