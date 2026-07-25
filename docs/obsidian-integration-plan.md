# Obsidian Integration Plan

> ✅ **EXECUTED — closed 2026-07-25.** All six sub-tasks shipped; each `Status` line
> below cites the artifact that closes it. This document is retained as the design
> record, not as open work. Until 2026-07-25 every sub-task still read
> `[ ] pending` while the code had been in the tree for days — a tracking-doc
> staleness the full-project audit flagged.
>
> The live operator documentation is
> [`docs/knowledge-base/guides/obsidian-integration-guide.md`](knowledge-base/guides/obsidian-integration-guide.md).

## Top-Level Overview

Two independent features that together make the Mnemox knowledge graph visible and
writable inside Obsidian, both from the export surface (Feature 1) and from Bob IDE
via MCP (Feature 2).

**Feature 1 — Semantic Graph Export to Obsidian**
Generate an export of `docs/knowledge-base/` that surfaces the semantic edges stored
in `.bob/kb-graph.json` as two complementary Obsidian artefacts:
- A `.canvas` file (Obsidian Canvas JSON) for full visual graph exploration
- Dataview YAML frontmatter injected into the exported KB documents so edges are
  queryable via the Dataview plugin

The live `docs/knowledge-base/` is **never modified**. All changes land in `kb-export/`.

**Feature 2 — Obsidian MCP Server in Bob IDE**
Register the `obsidian-mcp` Node.js MCP server in `.bob/mcp.json` pointing at the
live `docs/knowledge-base/` vault. Bob IDE can then read, search, and write KB
documents directly through Obsidian's Local REST API. Entry added `disabled: false`
(opt-in by the workspace owner who must have the Local REST API plugin running).
Document prerequisites and setup in a new KB guide.

**Scope boundaries (non-goals):**
- No modification of `src/graph/` core logic
- No Windows compatibility work
- No modification of `.bob/skills/knowledge-manager/SKILL.md`
- No changes to the live KB documents in `docs/knowledge-base/`
- Feature 2 does not add MCP tool allowlists (left to the workspace owner)

---

## Sub-Tasks

---

### ST-1 — Obsidian Canvas exporter (`scripts/export-kb-graph-canvas.py`)

**Status:** [x] closed — verified 2026-07-25: `scripts/export-kb-graph-canvas.py` + `scripts/canvas_export.py`

**Intent**
Produce a `kb-export/kb-semantic-graph.canvas` file that renders the Mnemox
knowledge graph in Obsidian's native Canvas view. Nodes are positioned by
category cluster; edges are drawn for explicit, semantic, and broken edge types
with distinct colours. This gives a visual, interactive map of the full 109-node,
4 589-edge graph without touching any live KB document.

**Expected Outcomes**
- `kb-export/kb-semantic-graph.canvas` exists and opens correctly in Obsidian 1.1+
- Nodes are grouped spatially by category (concepts / guides / references / research)
- Edges carry colour metadata: green = explicit, blue = semantic, red = broken
- Semantic edges include their cosine weight as a label (e.g. `0.41`)
- Canvas file passes Obsidian's JSON schema (no parse errors on open)
- Script is runnable standalone: `python scripts/export-kb-graph-canvas.py`

**Todo List**
1. Create `scripts/export-kb-graph-canvas.py`
2. Load `.bob/kb-graph.json` via `json.load` (do not import `src/` — keep the
   script dependency-free)
3. Assign each node a (x, y) position using a deterministic sub-clustered grid layout:
   - Four category columns: concepts=0, guides=800, references=1600, research=2400
   - Within each column, group nodes by their first tag (alphabetically); each group
     is a vertical sub-cluster separated by a 120px gap from the next group
   - Within each sub-cluster, sort nodes alphabetically, space 140px apart vertically
   - Node size: width=320, height=60 (Obsidian Canvas default card dimensions)
   - Column width chosen so sub-cluster labels do not overlap between columns
4. Build the Canvas JSON structure:
   ```
   {
     "nodes": [
       {"id": <str>, "type": "file", "file": "knowledge-base/<doc_id>",
        "x": <int>, "y": <int>, "width": 260, "height": 60}
     ],
     "edges": [
       {"id": <str>, "fromNode": <str>, "toNode": <str>,
        "color": <"2"|"4"|"1">, "label": <str|null>}
     ]
   }
   ```
   - Node `id`: md5 hex of doc_id (deterministic, 8-char prefix)
   - Edge `id`: md5 hex of `source+target+type` (deterministic, 8-char prefix)
   - Canvas colour codes: `"2"` = green (explicit), `"4"` = blue (semantic),
     `"1"` = red (broken)
   - Semantic edge label: cosine weight rounded to 2 decimal places
   - Explicit edge label: the `label` field from the graph if non-null, else null
5. Write output to `kb-export/kb-semantic-graph.canvas` (create `kb-export/` if absent)
6. Print a summary: node count, edge count by type, output path
7. Add `obsidian-graph` target to `scripts/export-kb.sh` that calls this script

**Relevant Context**
- Graph source: `.bob/kb-graph.json` — schema in ST-1 evidence above
- Edge types: `"explicit"` (weight=1.0), `"semantic"` (weight=0.3–1.0), `"broken"` (weight=0.0)
- Obsidian Canvas JSON spec: `nodes[]` and `edges[]` arrays; node type `"file"` uses
  relative vault path in `"file"` field; edge colour is a string `"1"`–`"6"`
- The Canvas file must live inside the vault root (or a subfolder of it). Since we
  export to `kb-export/`, the vault root is `kb-export/` and KB docs are at
  `kb-export/knowledge-base/`. Canvas `"file"` paths must be relative to the vault
  root: `"knowledge-base/concepts/caching.md"` not `"docs/knowledge-base/..."`.
- `scripts/export-kb.sh` lines 37-55: existing obsidian export block to extend
- No `src/` imports — script must be runnable without `uv` or package install

---

### ST-2 — Dataview frontmatter injector (`scripts/export-kb-graph-dataview.py`)

**Status:** [x] closed — verified 2026-07-25: `scripts/export-kb-graph-dataview.py` + `scripts/dataview_export.py`

**Intent**
Produce an annotated copy of the KB in `kb-export/knowledge-base/` where each
document's YAML frontmatter is extended with a `semantic_links:` list. This makes
the semantic edges queryable via the Obsidian Dataview plugin without modifying
the live KB. Runs after ST-1 (or independently after `export-kb.sh obsidian`).

**Expected Outcomes**
- Every document in `kb-export/knowledge-base/` has a `semantic_links:` YAML list
  containing the top-N semantic neighbours (by cosine weight) with their doc_id and weight
- Documents with no semantic edges above threshold get `semantic_links: []`
- The live `docs/knowledge-base/` files are untouched (verified by `git diff --quiet`)
- Script is runnable standalone: `python scripts/export-kb-graph-dataview.py`
- A sample Dataview query is printed to stdout showing how to use the annotation

**Todo List**
1. Create `scripts/export-kb-graph-dataview.py`
2. Accept `--graph-path` (default `.bob/kb-graph.json`),
   `--export-path` (default `kb-export/knowledge-base`),
   `--top-n` (default 0 = all edges above threshold, any positive integer caps the list),
   `--min-weight` (default 0.30, matching the graph build threshold; user-adjustable)
3. Load the graph JSON; build a dict `semantic_neighbours[doc_id] = [(target, weight), ...]`
   sorted by weight descending, filtered by `--min-weight`, capped at `--top-n` if > 0
4. For each `.md` file in `kb-export/knowledge-base/`:
   - Read the file content
   - Locate the closing `---` of the frontmatter block (second `---` line)
   - If `semantic_links:` already present in frontmatter, replace it; otherwise insert it
     before the closing `---`
   - Write the `semantic_links:` block in YAML list format:
     ```yaml
     semantic_links:
       - doc: "concepts/caching.md"
         weight: 0.41
       - doc: "research/phase2-performance.md"
         weight: 0.38
     ```
5. Print a sample Dataview query to stdout:
   ```dataview
   TABLE semantic_links FROM "knowledge-base/concepts"
   WHERE length(semantic_links) > 0
   SORT file.name ASC
   ```
6. Print summary: files annotated, total semantic_link entries written
7. Add invocation to `scripts/export-kb.sh` `obsidian-graph` target (after ST-1)

**Relevant Context**
- Frontmatter regex: same pattern as `src/graph/builder.py` `_FRONTMATTER_RE`
  (`^---\s*\n(.*?)\n---\s*\n` with `re.DOTALL`)
- Must not modify files in `docs/knowledge-base/` — validate with assert on path
- Export path must exist before running (created by `export-kb.sh obsidian` or ST-1)
- No `src/` imports — script must run without `uv`

---

### ST-3 — Extend `scripts/export-kb.sh` with `obsidian-graph` target

**Status:** [x] closed — verified 2026-07-25: `scripts/export-kb.sh:63` (`obsidian-graph` target) — and its non-idempotent `cp -r` was fixed 2026-07-25

**Intent**
Wire ST-1 and ST-2 into the existing export script as a new `obsidian-graph`
format option that runs the full Obsidian export (existing `obsidian` case) then
adds Canvas generation and Dataview annotation on top of it. One command produces
the complete Obsidian vault with semantic graph support.

**Expected Outcomes**
- `./scripts/export-kb.sh obsidian-graph` runs all three steps:
  1. Existing Obsidian vault copy (`cp -r docs/knowledge-base/ kb-export/knowledge-base/`)
  2. Canvas generator (`python scripts/export-kb-graph-canvas.py`)
  3. Dataview injector (`python scripts/export-kb-graph-dataview.py`)
- `./scripts/export-kb.sh` with no args still shows updated usage including `obsidian-graph`
- Existing `obsidian` target is unchanged
- Exit codes propagate: if Canvas script fails, the shell command fails

**Todo List**
1. Open `scripts/export-kb.sh`
2. Add `obsidian-graph)` case block after the existing `obsidian)` block
3. The new block: run existing obsidian copy logic, then invoke the two Python scripts
4. Update the usage/help block to include `obsidian-graph`
5. Verify: `bash scripts/export-kb.sh obsidian-graph` runs end-to-end
   without errors on the current repo

**Relevant Context**
- `scripts/export-kb.sh` lines 36-53: existing obsidian case to duplicate and extend
- Python invocation: `python3 scripts/export-kb-graph-canvas.py` and
  `python3 scripts/export-kb-graph-dataview.py` (use `python3` for portability)
- No uv/venv required — scripts have no external dependencies

---

### ST-4 — Tests for ST-1 and ST-2

**Status:** [x] closed — verified 2026-07-25: `tests/graph/test_canvas_export.py` + `tests/graph/test_dataview_export.py`

**Intent**
Add unit tests for the two export scripts so that Canvas JSON validity and
Dataview frontmatter injection correctness are regression-tested. Follow the
existing test pattern in `tests/graph/`.

**Expected Outcomes**
- `scripts/canvas_export.py` — importable module with a `build_canvas(graph_dict, **opts)`
  function; `scripts/export-kb-graph-canvas.py` is a thin CLI wrapper around it
- `scripts/dataview_export.py` — importable module with an `inject_dataview(export_path, graph_dict, **opts)`
  function; `scripts/export-kb-graph-dataview.py` is a thin CLI wrapper around it
- `tests/graph/test_canvas_export.py` — 6+ tests covering:
  - Canvas JSON has `nodes` and `edges` arrays
  - Node count matches graph node count
  - Sub-cluster grouping: nodes sharing the same first tag are vertically adjacent
  - Edge colours correct for each type (`"2"` explicit, `"4"` semantic, `"1"` broken)
  - Semantic edge labels formatted as `"0.41"` (2 dp)
  - Output is valid JSON parseable by `json.loads`
- `tests/graph/test_dataview_export.py` — 6+ tests covering:
  - `semantic_links:` block injected into frontmatter
  - Live `docs/knowledge-base/` files untouched (path assertion in fixture)
  - `top_n=0` returns all edges above threshold
  - `top_n=3` caps at 3 neighbours
  - `min_weight` filter excludes edges below threshold
  - Files with no semantic edges get `semantic_links: []`
- All new tests pass under `uv run pytest tests/graph/ -v`
- Coverage gate still passes (`≥80%` global, `≥70%` delegation floor)

**Todo List**
1. Extract Canvas layout and JSON generation into `scripts/canvas_export.py`
   as an importable module (no `src/` imports, no argparse)
   - Public API: `build_canvas(graph_dict: dict, output_path: str | Path) -> dict`
2. Extract Dataview injection logic into `scripts/dataview_export.py`
   as an importable module
   - Public API: `inject_dataview(export_path: str | Path, graph_dict: dict, top_n: int = 0, min_weight: float = 0.30) -> dict`
   - Returns stats dict: `{"files_annotated": int, "total_links": int}`
3. Make `scripts/export-kb-graph-canvas.py` a thin CLI wrapper calling `canvas_export.build_canvas`
4. Make `scripts/export-kb-graph-dataview.py` a thin CLI wrapper calling `dataview_export.inject_dataview`
5. Write `tests/graph/test_canvas_export.py` using `tmp_path` + direct calls to `canvas_export.build_canvas`
6. Write `tests/graph/test_dataview_export.py` using `tmp_path` + direct calls to `dataview_export.inject_dataview`
7. Run `uv run pytest tests/graph/ -v` — all must pass
8. Run `uv run pytest tests/ --cov=src --cov-report=term-missing` — coverage gate must hold

**Relevant Context**
- `tests/graph/test_builder.py` and `test_store.py`: fixture patterns to follow
- `tmp_path` pytest fixture for all file I/O — no writes to live dirs in tests
- `scripts/` is not a Python package — tests must add `scripts/` to `sys.path` or
  use `importlib` to import the module; follow the pattern used in any existing
  `tests/` file that imports from outside `src/`

---

### ST-5 — Obsidian MCP registration in `.bob/mcp.json`

**Status:** [x] closed — verified 2026-07-25: `.bob/mcp.json.example` carries the Obsidian entry (`.bob/mcp.json` itself is gitignored as credential-bearing)

**Intent**
Register `obsidian-mcp` (MarkusPfundstein/obsidian-mcp) as an active MCP server
in Bob IDE, pointing at the live `docs/knowledge-base/` vault path. Entry is
`disabled: false`. Anyone opening the workspace in Bob IDE gets the MCP active;
if the Obsidian Local REST API plugin is not running, the server silently fails
to connect (Bob IDE degrades gracefully — no crash).

**Expected Outcomes**
- `.bob/mcp.json` contains an `"obsidian"` entry with:
  - `"command": "npx"`
  - `"args": ["-y", "obsidian-mcp"]`
  - `"env"` block with `OBSIDIAN_API_KEY` and `OBSIDIAN_HOST` (port 27123 default)
  - `"disabled": false`
  - A `"description"` field explaining what tools it exposes and the prerequisite
- The JSON is valid (no syntax errors)
- A prominent comment-style description documents what the workspace owner must do
  before the MCP is functional (install Local REST API plugin, set API key)

**Todo List**
1. Open `.bob/mcp.json`
2. Add the `"obsidian"` entry after the existing `"bob-marketplace"` entry:
   ```json
   "obsidian": {
     "command": "npx",
     "args": ["-y", "obsidian-mcp"],
     "env": {
       "OBSIDIAN_API_KEY": "YOUR-OBSIDIAN-LOCAL-REST-API-KEY-HERE",
       "OBSIDIAN_HOST": "https://127.0.0.1:27123",
       "OBSIDIAN_VAULT_PATH": "docs/knowledge-base"
     },
     "disabled": false,
     "description": "Obsidian MCP — read/write access to the live Mnemox KB vault via Obsidian Local REST API plugin. PREREQUISITES: (1) Obsidian installed with the 'Local REST API' community plugin enabled. (2) Replace OBSIDIAN_API_KEY with the key shown in the plugin settings. (3) Vault open in Obsidian, plugin server running on port 27123. (4) OBSIDIAN_VAULT_PATH is relative; expand to absolute path locally if required — do not commit an absolute path. Tools: list-files, get-file, search, create-file, update-file, append-to-file, delete-file."
   }
   ```
3. Verify JSON syntax: `python3 -c "import json; json.load(open('.bob/mcp.json'))"`

**Relevant Context**
- `.bob/mcp.json` current structure: 10 servers, mix of `streamable-http` and
  `command/args` transports
- `obsidian-mcp` uses `stdio` transport (command/args pattern), same as
  `terraform` and `external-llm` entries
- Default Obsidian Local REST API port: 27123 (HTTP) or 27124 (HTTPS with self-signed cert)
- `OBSIDIAN_VAULT_PATH` is committed as a relative path (`docs/knowledge-base`);
  if the MCP server requires an absolute path, expand it locally — never commit
  an absolute machine-specific path
- The `npx -y` invocation auto-installs the package on first run (no pre-install needed)

---

### ST-6 — KB guide: Obsidian integration setup

**Status:** [x] closed — verified 2026-07-25: `docs/knowledge-base/guides/obsidian-integration-guide.md`

**Intent**
Write a KB guide that documents both features end-to-end: how to run the semantic
graph export (Feature 1) and how to activate the Obsidian MCP in Bob IDE (Feature 2).
This is the only documentation artefact — no changes to SKILL.md.

**Expected Outcomes**
- `docs/knowledge-base/guides/obsidian-integration-guide.md` exists, follows the
  KB guide template, and passes `scripts/validate-kb.sh`
- Covers Feature 1: prerequisites (Python 3.11+, Obsidian 1.1+, Dataview plugin),
  step-by-step export command, how to open the vault, how to use the Canvas view,
  sample Dataview query
- Covers Feature 2: prerequisites (Node.js 18+, Obsidian Local REST API plugin),
     step-by-step activation (replace API key in `.bob/mcp.json`), list of available MCP
     tools, limitation that `OBSIDIAN_VAULT_PATH` must be expanded to an absolute path
     locally if required and must not be committed back
- Cross-references: links to `references/mnemox-cli-reference.md` and
  `concepts/knowledge-graph-layer.md`
- `docs/knowledge-base/index.md` updated with the new guide entry

**Todo List**
1. Write `docs/knowledge-base/guides/obsidian-integration-guide.md` using the
   guide template from `.bob/skills/knowledge-manager/SKILL.md`
2. Section 1: Feature 1 — Semantic graph export
   - Prerequisites list
   - Commands: `./scripts/export-kb.sh obsidian-graph`
   - What the export produces (vault structure, Canvas file, annotated frontmatter)
   - Opening the vault in Obsidian (File → Open Folder as Vault → select `kb-export/`)
   - Using Canvas (navigate to `kb-semantic-graph.canvas`)
   - Using Dataview (install plugin → sample query from ST-2 output)
3. Section 2: Feature 2 — Obsidian MCP in Bob IDE
   - Prerequisites: Node.js 18+, Obsidian Local REST API plugin
   - Step-by-step: install plugin, copy API key, edit `OBSIDIAN_API_KEY` in
     `.bob/mcp.json`, update `OBSIDIAN_VAULT_PATH` to local absolute path
   - Tools available (from obsidian-mcp README): list-files, get-file, search,
     create-file, update-file, append-to-file, delete-file
   - Limitation: `OBSIDIAN_VAULT_PATH` is machine-specific — each team member
     must set their own value; do not commit a real path to a shared repo
   - Example Bob IDE prompt: "Search my Obsidian KB for documents about caching"
4. Add Related Documents links (bidirectional)
5. Update `docs/knowledge-base/index.md` Guides section
6. Run `scripts/validate-kb.sh` — must pass with 0 errors

**Relevant Context**
- Guide template: `.bob/skills/knowledge-manager/SKILL.md` guide template block
- `references/mnemox-cli-reference.md`: CLI reference to cross-link
- `concepts/knowledge-graph-layer.md`: graph layer concept to cross-link
- `docs/knowledge-base/index.md`: current Guides section for insertion point

---

## Dependency Order

```
ST-1 (Canvas exporter) ──┐
                          ├──► ST-3 (export-kb.sh obsidian-graph target)
ST-2 (Dataview injector) ─┘
      │
      └──► ST-4 (tests for ST-1 + ST-2)  [can run in parallel with ST-3]

ST-5 (mcp.json entry) ──► ST-6 (KB guide)  [independent of ST-1–4]
```

ST-5 and ST-6 are fully independent of ST-1 through ST-4 and can be implemented
in parallel or in any order relative to them.

---

## Validation Gate (after all sub-tasks)

After all sub-tasks are marked done, run the following before final commit:

```bash
# 1. Full export smoke test
./scripts/export-kb.sh obsidian-graph
# Expected: kb-export/kb-semantic-graph.canvas exists, kb-export/knowledge-base/ annotated

# 2. Canvas JSON validity
python3 -c "import json; d=json.load(open('kb-export/kb-semantic-graph.canvas')); \
  print(f'nodes={len(d[\"nodes\"])} edges={len(d[\"edges\"])}')"

# 3. Live KB untouched
git diff --quiet docs/knowledge-base/ && echo "OK: live KB unchanged" || echo "FAIL: live KB modified"

# 4. Tests
uv run pytest tests/graph/ -v

# 5. MCP JSON validity
python3 -c "import json; json.load(open('.bob/mcp.json')); print('mcp.json valid')"

# 6. KB validation
bash scripts/validate-kb.sh
```

All six checks must pass before the implementation is considered complete.
