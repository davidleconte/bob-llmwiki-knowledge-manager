# Mnemox

### *Give IBM Bob a memory. Make your knowledge compound.*

> **Mnemox** — from *Mnemosyne* (Μνημοσύνη), the Greek Titaness of memory.
> In Greek mythology, Mnemosyne was not merely the goddess of remembrance —
> she was the *mother of the nine Muses*, the source from which all knowledge,
> art, and discovery flow. Before you can create, you must remember. Before you
> can go deeper, you must not re-pay for what you already know. Mnemosyne held
> the river of memory (*Lethe*'s opposite) in Hades — the water that let souls
> *retain* what they had learned rather than forget it at the threshold.
>
> **Mnemox is that river, built into IBM Bob.** It is the persistent memory layer
> IBM Bob was missing — the layer that lets every session start from everything
> the team already learned, so the budget previously consumed by forgetting is
> freed for the work that actually matters: going deeper, thinking broader,
> attempting the problems that were previously too expensive to try.
>
> *Mnemox your workspace. The impossible gets closer with every session.*

A native **IBM Bob** implementation of Andrej Karpathy's **LLM-Wiki** pattern, engineered for **Bobcoin economy**. Built by **Team BobjectifLune** as their 2026 IBMer watsonx Challenge submission. Works in **Bob IDE** and **Bob Shell CLI**.

> 💡 **What is a Bobcoin?** IBM Bob runs on a token-based budget called **Bobcoins** — the internal unit that measures how much AI computation each session consumes. Every question you ask, every file Bob reads, every answer it generates costs Bobcoins. The budget is finite and shared. Spending it on re-derivation — re-reading files Bob already processed, re-reasoning about decisions it already made — is waste. Mnemox eliminates that waste structurally, so your Bobcoin budget goes to work that actually moves things forward.

`MIT licensed` · `Native Bob modes` · `No MCP servers` · `No plugins` · `Pattern: LLM-Wiki (Karpathy)` · `Bob Shell CLI` · `Bob IDE`

> **What this is.** The most powerful thing you can do with Bob is give it a research scope that
> compounds. Not just one codebase — a living, growing body of knowledge that spans architectures,
> decisions, experiment findings, and accumulated expertise. Mnemox builds that memory: knowledge
> is written down once and *retrieved* thereafter, so the cost of re-derivation drops toward zero —
> and the budget it frees up becomes available for depth, breadth, and agentic ambition. It ships as
> **two native Bob modes** — no plugin, no MCP server, nothing external in the loop.

---

## 1. The problem: re-derivation is consuming the budget that should go to depth

IBM's own guidance is blunt about where a session's budget goes. Every turn burns **input**, **output**,
and **reasoning** tokens — and the two you can't see are the expensive ones.

Teams respond by trimming the visible line: disabling tools, pasting less, shortening prompts. That helps —
until it hits a floor. Because the largest recurring cost isn't the prompt. **It's re-derivation.** Session
after session, Bob re-reads the same architecture, re-infers the same relationships, and re-explains the
same concepts — because nothing it learned last time survived the end of the thread.

The consequence is invisible but compounding: every Bobcoin spent re-deriving what the team already knows is a Bobcoin not available for going deeper, exploring a new research direction, or deploying a broader agentic scope. The budget shrinks — not because Bob is doing more, but because it keeps relearning the same things.
The question teams eventually cannot ask is not *"can Bob do this?"* — it's *"can we afford to let Bob try?"*

> The cheapest session is the one that never has to think a thought twice. But the real prize is what
> you can do with the budget you recover.

## 2. The pattern: Karpathy's LLM-Wiki

Karpathy's *LLM-Wiki* pattern replaces "retrieve-from-scratch" with a **persistent, compounding artifact**:

> *"The wiki is a persistent, compounding artifact. The cross-references are already there. The
> contradictions have already been flagged."* — as opposed to RAG, where *"the LLM is rediscovering
> knowledge from scratch on every question. There's no accumulation."*

Three layers:

1. **Raw sources** — your code and docs. Immutable; the model reads, never edits.
2. **The wiki** — LLM-owned markdown: concepts, guides, references, cross-links.
3. **The schema** — a config that makes the model *"a disciplined wiki maintainer rather than a generic chatbot."*

His load-bearing insight: *"the tedious part of maintaining a knowledge base is not the reading or the
thinking — it's the bookkeeping."* LLMs are extraordinary bookkeepers. Point one at your repo, and the
knowledge base maintains itself.

## 3. This implementation: native to Bob — IDE and CLI

Bob Knowledge Manager is that pattern, built entirely on Bob's **native** capabilities. It works identically in **Bob IDE** and **Bob Shell CLI** — same modes, same KB structure, same compounding benefit.

### 3a. How it works — the three components

- **🧠 `knowledge-manager` mode** — structured KB maintainer: concepts / guides / references / research, consistent templates, bidirectional cross-references, self-updating `index.md`. Every document filed becomes a permanent asset, retrieved on demand by any future session.
- **🔍 `repo-analyzer` mode** — 7-phase repository audit that runs analysis scripts and files digested findings into the KB, instead of dragging raw source through the context window.
- **The schema layer** — your `AGENTS.md` plus the mode definition *are* Karpathy's third layer: stable rules that make Bob disciplined, consistent, and cacheable across every session.

> **Works with the full Bob ecosystem.** The Knowledge Manager is a native Bob mode — it composes naturally with every mode, skill, rule, and MCP server in the [Bob Marketplace](https://marketplace.bob.ibm.com). Use it alongside `ibm-watsonx-data`, `ibm-docling`, `carbon-mcp`, or `techzone` as examples — but it pairs equally with any current or future Bob capability. The KB becomes the persistent memory layer that runs underneath your entire Bob toolkit, not just one workflow.

<p align="center">
  <img src="docs/assets/kb-compounding-loop.svg" alt="The compounding-knowledge loop: Bob reads your repository once, files digested knowledge into a version-controlled knowledge base, and every later session retrieves from that knowledge base instead of re-deriving from the repo." width="760">
</p>

### 3b. Two activation paths — choose yours

| | **Bob IDE** *(recommended for teams)* | **Bob Shell CLI** |
|---|---|---|
| **Activate** | Mode picker → 🧠 Mnemox Knowledge Builder | `bob --chat-mode=knowledge-manager` *(slug — same mode)* |
| **First-time setup** | `scripts/init-project.sh` once per project (30 seconds) | `scripts/install.sh` once |
| **Persistence model** | **Git-backed markdown** — shared, versioned, visible to the whole team. Knowledge auto-loads at every session start via `.bob/settings.json`. | **`save_memory`** + markdown files — in-session fact injection, ideal for solo CLI use. |
| **Skill lazy-load** | ✅ `use_skill("knowledge-manager")` | not supported |
| **Best for** | Teams, shared knowledge, any workspace | Solo power users, terminal-native workflows |

> **Bob IDE is the recommended path for team use.** Knowledge persists as Git-committed Markdown — every team member reads and builds on the same growing KB. There is no private fact store: everything is shared, auditable, and compounds across the whole team.
>
> **Bob Shell CLI** adds `save_memory` on top of the same KB — an in-session fact store that injects recalled facts into each turn automatically. Fast and seamless for solo work; facts are private to the session owner.
>
> Both paths produce the same KB artefacts and the same compounding benefit. Choose based on your workflow, not on capability.

## 3c. Who this is for

The pattern works wherever accumulated knowledge has value — across roles, domains, and disciplines.

| Role | The problem | What the KB makes possible |
|---|---|---|
| **Product Specialist / Tiger Team** | Client scenarios re-answered from scratch each engagement; expertise lives in Slack and individual sessions | A living KB of patterns, decisions, and findings — every new engagement starts from the team's full accumulated expertise, not zero |
| **Software team (SDLC)** | Sprint knowledge decays between sessions; design rationale and architectural decisions are re-derived on every onboarding | Architecture decisions, design rationale, and test findings compound across sprints — new members get a KB tour, not an archaeology project |
| **Researcher** | Experiment context, negative results, and methodology notes don't survive session boundaries | A persistent research KB where each experiment builds on the last; literature, hypotheses, and findings are cross-referenced, not re-derived |
| **Agentic team lead** | Real-time multi-agent deployments on complex business scopes are Bobcoin-prohibitive when every agent pays the full re-derivation cost | Pre-loaded KB context reduces per-agent input cost, making it economically rational to deploy deeper agent teams on broader research scopes |

> **The economic thesis:** Bobcoin economy is not just about spending less — it is about *spending on
> what matters*. When re-derivation cost approaches zero, the budget previously consumed by repetition
> becomes available for depth, breadth, and agentic ambition. The KB is not a cost-cutting tool.
> It is a lever that moves the frontier of what is affordable.
>
> **The compounding advantage scales with your Bob stack.** Every mode, skill, rule, and MCP server you add to your Bob workspace produces knowledge worth keeping. The KB Manager captures it — so the more powerful your Bob setup, the more value compounds.

---

## ℹ️ This repository contains two independently-operable systems

| System | Technology | Status |
|--------|-----------|--------|
| **Bob Knowledge Manager** | Bash scripts, YAML, Markdown | Stable v1.0 |
| **Token Optimization System** (`src/`) | Python 3.11+, tiktoken, scikit-learn | Beta — Not Production Ready |

Each system works without the other. Three **opt-in** integration points connect them (all fallback-safe — if the Python system is absent, the KB Manager is unaffected): the KB query engine can use the TOS embedding scorer; the `knowledge-manager` mode can compress retrieved context via `bob-optimize`; and a persistent embedding index bridges KB document search with TOS cache infrastructure. See [`INTEGRATIONS.md`](INTEGRATIONS.md).

Architecture: [KB Manager — `docs/kb-manager/architecture.md`](docs/kb-manager/architecture.md) · [Python system — `docs/architecture/architecture.md`](docs/architecture/architecture.md).

### Supported targets

| Target | Activation | Install step | Skill lazy-load | **Persistence model** | **Best for** |
|--------|-----------|--------------|-----------------|----------------------|------------|
| **Bob Shell CLI** | `bob --chat-mode=knowledge-manager` | `scripts/install.sh` | not supported | `save_memory` (in-session, single-user) + markdown files | CLI power users; solo workflows |
| **Bob IDE (this repo)** | Mode picker → 🧠 Mnemox Knowledge Builder | none — zero steps | ✅ `use_skill("knowledge-manager")` — lazy, explicit | Git-backed markdown — shared, versioned, team-visible | Teams; any workspace; recommended |
| **Bob IDE (other project)** | Mode picker → 🧠 Mnemox Knowledge Builder | `scripts/init-project.sh` — once per project | ✅ `use_skill("knowledge-manager")` — lazy, explicit | Git-backed markdown — shared, versioned, team-visible | Teams; any workspace; recommended |

> **Two persistence models — both are complete, neither is a fallback:**
>
> **Bob Shell CLI** uses `save_memory` — an in-session fact store that injects recalled facts into each turn automatically. Fast and seamless for solo use; facts are private to the session owner and not visible to teammates.
>
> **Bob IDE** uses Git-backed markdown — knowledge is written to `docs/knowledge-base/`, committed to the repository, and auto-loaded at the start of every session via `.bob/settings.json`. Every team member reads and builds on the same growing KB. This is the recommended model for team use: knowledge is shared, auditable, and compounds across the entire team, not just one person's sessions.
>
> See [`docs/bob-ide-guide.md`](docs/bob-ide-guide.md) for the full Bob IDE workflow.

---

## 4. Why it saves Bobcoins: structure, not a benchmark

The savings are **structural** — each IBM token-economy principle has a concrete home in how the modes behave:

| IBM principle | The recurring waste | How the modes remove it |
|---|---|---|
| **Catalog tax** | Every MCP server re-sends its full tool catalog every turn | Native Bob mode — **no plugin, no MCP** |
| **Payload tax** | A 2,000-line file attached when 20 lines matter | `repo-analyzer` runs scripts that **summarise**; the KB stores digested reports you *cite*, not raw source |
| **Compression trap** | Stripping meaning can backfire and *raise* effective cost | Templates **preserve** meaning — rationale, real names, cross-refs |
| **Short threads** | Turn 15 re-pays 14 turns of stale history | Knowledge persists in Git-backed KB files (both targets); `save_memory` additionally injects facts per-turn *(Bob Shell CLI)*; a fresh thread always **retrieves** |
| **Let caching work** | Reworded prefixes miss the cache | Fixed mode definition + `AGENTS.md` + KB layout = a **cacheable prefix** |
| **Trim output** | Verbose narration is paid on every reply | Bounded artifacts: templates, `index.md`, reports — not essays |

## 5. Get started — `mnemox your workspace`

> **One word. That is the entire command.**
>
> Type `mnemox your workspace` (or just `mnemox`) in any **🧠 Mnemox Knowledge Builder** session —
> Bob IDE or Bob Shell CLI — and Mnemox does the right thing automatically:
>
> - **Fresh workspace** (no KB yet) → scaffolds `docs/knowledge-base/`, runs the 7-phase analysis
>   suite, validates structure. Your workspace is Mnemoxed.
> - **Already Mnemoxed** → refreshes the 7-phase analysis, captures lessons learned from `git log`
>   and KB diff into a dated research note, rebuilds the knowledge graph, and auto-commits
>   `docs/knowledge-base/` to git. Bob synthesises the lessons learned **in the same session**,
>   immediately after the script completes.
>
> The `mnemox` command is installed as a shell function by `scripts/install.sh` (Bob Shell CLI) and
> is wired as a trigger phrase in the mode skill (Bob IDE). Set `MNEMOX_HOME` to the path of this
> repo to use it from any project.

**Install once (Bob Shell CLI):**

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/install.sh          # writes ~/.bob/mnemox.sh, adds shell function
source ~/.bashrc              # or ~/.zshrc
```

**Already Mnemoxed?** Re-run `mnemox` at any time. Two speeds:

| Flag | What runs | When to use |
|------|-----------|-------------|
| `mnemox` / `mnemox --full` | 7-phase analysis + lessons + graph + commit | New source files, schema changes, architectural decisions |
| `mnemox --quick` | lessons + graph + commit only | Code housekeeping, doc edits, daily refresh — finishes in seconds |

<details>
<summary><strong>What happens under the hood (three scripts, ~5 minutes)</strong></summary>

```bash
# What mnemox calls internally:
scripts/init-project.sh        # (init path only) scaffold docs/knowledge-base/
scripts/run-full-analysis.sh   # 7-phase analysis → dated research snapshots
scripts/validate-kb.sh         # (init path only) structure check
scripts/mnemox-lessons.sh      # (update path only) lessons-learned note
uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
git add docs/knowledge-base/ && git commit -m "mnemox: update KB $(date +%Y-%m-%d)"
```

> **What `run-full-analysis.sh` produces:** 7 Bash scripts run against your repo and file 7 dated
> Markdown snapshots into `docs/knowledge-base/research/` (scan, dependencies, metrics, security,
> test coverage, git history, docs coverage). Bob reads these ~200-line digested reports instead of
> raw source — that is why the KB session immediately produces grounded suggestions.
> Re-run at any time to refresh dated snapshots without overwriting prior KB work.
> Full details: [`docs/knowledge-base/guides/complete-repository-analysis.md`](docs/knowledge-base/guides/complete-repository-analysis.md).

> **Full-stack setup (recommended):** Run `./scripts/setup.sh` once from the repo
> root. It installs the Token Optimization System, builds the KB embedding index,
> and prints an integration health report (`bob-optimize kb-status`). The KB Manager
> works without it — setup.sh only activates the optional Python integrations.

</details>

## 6. Starting a new session (daily use)

Bob Shell sessions start fresh — the mode does not persist between restarts. After the one-time setup above, every new session takes one step.

### Path E — Bob IDE mode picker

No installation or CLI required. The Knowledge Manager mode is bundled in `.bob/custom_modes.yaml`.

1. Open the workspace in Bob IDE (VS Code / Cursor with the Bob extension).
2. Click the mode picker in the bottom-left status bar (shows the current mode name).
3. Scroll to **🧠 Mnemox Knowledge Builder** and select it.
4. Bob IDE loads `.bob/skills/knowledge-manager/SKILL.md` automatically via the `skill` group.

> **Full reference:** [`docs/bob-ide-guide.md`](docs/bob-ide-guide.md)

### Path A — Wrapper script (Bob Shell CLI, recommended)

```bash
alias kb='~/Projects/bob-llmwiki-knowledge-manager/scripts/start-kb.sh'

kb                          # start KB session in current directory
kb ~/Projects/other-project # start in a different project
```

`start-kb.sh` verifies the KB exists, prints the document count, and launches `bob --chat-mode=knowledge-manager`. Add the alias to `~/.zshrc` for one-word daily activation.

### Path B — Direct CLI flag (Bob Shell CLI)

```bash
cd ~/your-project
bob --chat-mode=knowledge-manager
```

### Path C — Switch mode inside an existing Bob Shell session

```text
/mode knowledge-manager
```

### Path D — No mode installed (prompt injection)

If the mode is not installed globally, paste this at the start of any Bob mode:

```text
You are acting as the knowledge manager for this project.
KB location: docs/knowledge-base/  (index.md is loaded in context)
Resume: summarise what exists in the KB, what was most recently documented,
and suggest what to work on next.
Workflow: follow the 7-step process (determine category → select template →
apply naming convention → write content → add cross-references → save to
memory → update index.md).
```

### Standard resume prompt (first message of every session)

Once activated, open with:

```text
What did we document most recently? Summarise the KB and suggest what to work on next.
```

Bob will scan `index.md` (auto-loaded via `.bob/settings.json`), recall any `save_memory` facts from prior sessions *(Bob Shell CLI only — Bob IDE uses file persistence in `docs/knowledge-base/`)*, and propose the next logical documents or updates.

> **Full reference:** [`docs/usage.md §0`](docs/usage.md#0-starting-a-session) · [`docs/knowledge-base/guides/activating-knowledge-manager-in-new-session.md`](docs/knowledge-base/guides/activating-knowledge-manager-in-new-session.md)

### Mode switching and the KB

Switching mode mid-session (e.g. `/mode agent` to write code) does **not** delete or hide KB files — they
remain on disk exactly as written. What stops is the **maintenance discipline**: templates, bidirectional
cross-references, and `index.md` updates are enforced by the `knowledge-manager` mode's instructions, not
by the file system.

**Recommended pattern:** work in `agent` or `plan` mode for code changes, then `/mode knowledge-manager`
to file what you learned. Findings generated in another mode should be pasted into a new KB document
rather than assumed to be auto-captured.

`save_memory` facts set in `knowledge-manager` mode *(Bob Shell CLI only)* survive the mode switch and
remain available when you switch back.

## 7. What's in the box

**Bob Shell Knowledge Manager (the Bash system):**
- 2 native Bob modes — `knowledge-manager`, `repo-analyzer`
  - Bob Shell CLI config: `config/custom_modes.yaml` → installed to `~/.bob/custom_modes.yaml`
  - Bob IDE config: `.bob/custom_modes.yaml` (workspace-level, zero install)
- 4 document templates — concept · guide · reference · research
- Knowledge-base structure with self-maintained `index.md` and `save_memory` integration *(Bob Shell CLI; Bob IDE uses file persistence)*
- Bob IDE lazy-load skill: `.bob/skills/knowledge-manager/SKILL.md` — full templates + cross-reference protocol
- Core scripts — `install`, `init-project`, `validate-kb`, `export-kb` (Markdown / Obsidian / HTML / PDF)
- Analysis suite — scan, dependencies, metrics, security, test-coverage, git-history, docs, consolidated report
- 3 worked example knowledge bases — software project, research project, personal wiki

**Token Optimization System (the Python system, `src/`):**
- `TokenOptimizer` facade + `bob-optimize` CLI — composes all components behind one interface
- Multi-level cache — L1 exact match (<1 ms), L2 semantic similarity (<100 ms), with TTL enforcement
- Prompt optimizer — ~20% mean compression, near-lossless, tiktoken-counted (manifest: `evaluation/results/validation-2026-07-14/manifest.json`)
- Truncation — smart budget-fit strategies (lossy; reported separately from compression)
- Structured monitoring — JSON logging, metrics, health checks, cost tracking
- **Knowledge graph** (`src/graph/`) — property graph over KB documents; orphan/hub detection, multi-hop BFS traversal, PageRank re-ranking; CLI: `bob-optimize graph-build / graph-query / graph-health`

## 8. Using the Token Optimization System

The Python system (`src/`) is **independent** — it works without a KB, and the KB works without it.
Install once with `pip install -e ".[dev,monitoring]"`, then use whichever mode fits your workflow.

### Optional: MiniLM semantic embedding backend

The KB embedding pipeline supports an optional high-quality semantic backend powered by
`sentence-transformers/all-MiniLM-L6-v2` (384-dim, ~2–4 ms/doc warm on Apple Silicon).

`EmbeddingGenerator(backend="minilm")` resolves via a **priority fallback chain**:

1. **`mlx-embeddings`** — Apple MLX, Apple Silicon only, fastest (~2–4 ms warm)
   `pip install -e ".[mlx]"`
2. **`sentence-transformers`** — cross-platform CPU/GPU (~5–20 ms warm)
   `pip install sentence-transformers`
3. **`"hashing"` fallback** — always available, no deps, 1000-dim bag-of-ngrams

```python
from src.cache.embeddings import EmbeddingGenerator

embedder = EmbeddingGenerator(backend="minilm")
# Resolves: mlx-embeddings first, then sentence-transformers, then hashing
vec = embedder.generate("your KB document text")  # 384-dim if MiniLM loaded, else 1000-dim
```

> **No HuggingFace API key required.** `all-MiniLM-L6-v2` is a public model. On first use,
> it downloads once (~22 MB) to `~/.cache/huggingface/` and is cached persistently.

| Platform | MiniLM path | Install |
|----------|:-----------:|---------|
| macOS + Apple Silicon (M1/M2/M3+) | ✅ `mlx-embeddings` (fastest) | `pip install -e ".[mlx]"` |
| macOS + Intel, Linux, any | ✅ `sentence-transformers` | `pip install sentence-transformers` |
| No optional deps installed | ⚠️ Falls back to `"hashing"` | nothing to install |

**Fallback guarantee:** if neither optional package is installed, `EmbeddingGenerator`
emits a `UserWarning` and silently uses `HashingVectorizer` (1000-dim, <1 ms, no deps).
KB retrieval is **never blocked** by a missing MiniLM installation.

> **Why it matters:** `HashingVectorizer` p@3=0.60 vs MiniLM-L6-v2 p@3=0.88 on the
> 25-query KB golden set (live validation, 80-doc corpus). Use MiniLM for best retrieval
> quality. See ADR-014 and the [graph validation report](docs/knowledge-base/research/graph-validation-2026-07-17.md).

---

### Knowledge Graph (P3)

The graph layer (`src/graph/`) builds a property graph over the KB document corpus for
structural health analysis, multi-hop traversal, and PageRank-based re-ranking of search
results. It is **opt-in** and fully backward-compatible.

#### Implementation

Four modules, each independently usable:

| Module | Class | Responsibility |
|--------|-------|----------------|
| `src/graph/graph.py` | `KnowledgeGraph` | Adjacency dict, BFS traversal, PageRank (power method, damping=0.85), `orphans()`, `hubs()` |
| `src/graph/builder.py` | `KnowledgeGraphBuilder` | Parses frontmatter `related:` + inline `[text](path)` links for **explicit** edges; queries `PersistentEmbeddingIndex` to derive **semantic** edges at cosine ≥ 0.30 |
| `src/graph/ranker.py` | `GraphRanker` | Lazy PageRank cache; `rerank()` blend: `final = (1-w)·similarity + w·pagerank·15.0` |
| `src/graph/store.py` | `GraphStore` | Atomic `os.replace`-based JSON persistence to `.bob/kb-graph.json` |

Each KB document becomes a **node** with 10 properties (`NodeProps`): title, category, tags, date, type, status, mtime, content length, description, and raw related-refs. Edges carry a type (`explicit` or `semantic`), a weight (1.0 or cosine score), and an optional label.

#### Benefits

| Benefit | What it solves | Measured result |
|---------|----------------|-----------------|
| **Orphan detection** | Documents with no inbound links are invisible to retrieval — they can never be surfaced by a KB query | 80-doc corpus: 39 orphans identified; semantic edges rescued 26 of them (reduced to 13 explicit orphans) |
| **Hub identification** | High-pagerank documents are the conceptual anchors of the KB — surfacing them improves query relevance | `graph.hubs(top_k=5)` returns the 5 documents most-cited by others |
| **Broken-link detection** | Cross-references to deleted or renamed files silently rot | Builder stores type `"broken"` edges (weight 0.0, excluded from PageRank); `graph-health` reports them |
| **Multi-hop traversal** | Related documents two or more hops away are invisible to keyword + embedding search | `graph.neighbours(doc_id, depth=2)` returns all documents within N hops with their distance |
| **PageRank re-ranking** | Embedding similarity alone treats every document as equally authoritative | `GraphRanker.rerank()` blends cosine similarity with PageRank score; default `graph_weight=0.0` (safe — no regression observed on the current corpus; raise only after re-running the golden set) |
| **Structural health CLI** | No visibility into KB connectivity without querying every file manually | `bob-optimize graph-health` prints orphan count, hub list, broken links, and PageRank top-10 in one command |

> **`graph_weight=0.0` is the validated default.** Live validation on an 80-doc corpus with MiniLM
> showed no uplift and no regression from graph re-ranking at any tested weight (0.1–0.5): p@3
> remained 0.88 with or without graph. The graph adds value through structural analysis (orphan/hub
> detection), not through score blending, on the current corpus size. See
> [ADR-017](docs/adr/017-knowledge-graph-layer.md).

```python
from pathlib import Path
from src.cache.embeddings import EmbeddingGenerator
from src.embeddings.index import PersistentEmbeddingIndex
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.store import GraphStore, DEFAULT_GRAPH_PATH
from src.tools.kb_query import KnowledgeBaseQuery

KB_PATH = Path("docs/knowledge-base")

# Build embedding index + graph
embedder = EmbeddingGenerator(backend="minilm")
index = PersistentEmbeddingIndex(embedder=embedder)
index.rebuild(KB_PATH)

graph = KnowledgeGraphBuilder(kb_path=KB_PATH, index=index).build()
GraphStore().save(DEFAULT_GRAPH_PATH, graph)

# Graph-aware KB query
kb = KnowledgeBaseQuery(KB_PATH, embedder=embedder, embedding_weight=1.0,
                        graph=graph, graph_weight=0.0)  # graph_weight=0.0 validated safe default
results = kb.query("caching L1 L2", max_results=10)

# KB health report
print(f"Orphans: {len(graph.orphans())}")
for doc, count in graph.hubs(top_k=3):
    print(f"  {count} inbound: {doc}")
```

**CLI commands (P3):**

```bash
bob-optimize graph-build   --kb-path docs/knowledge-base   # build + persist graph
bob-optimize graph-query   "caching strategy"              # graph-aware search
bob-optimize graph-health  --kb-path docs/knowledge-base   # orphans, hubs, broken links
```

**Live validation (80-doc corpus, MiniLM):** 2 836 edges, 39→13 orphans rescued,
p@3=0.88 — identical with or without graph re-ranking at the validated
`graph_weight=0.0` default. See [ADR-017](docs/adr/017-knowledge-graph-layer.md) and
the [validation report](docs/knowledge-base/research/graph-validation-2026-07-17.md).

### How `bob-optimize` works inside Bob Shell and Bob IDE

`bob-optimize` is a **pre-processing step** — it compresses text before it reaches the LLM, saving
input tokens. It is not a chat interface; it does not send anything to an LLM. Both Bob Shell CLI and
Bob IDE can call it, but the experience differs:

| Interface | Integration | What you do |
|-----------|------------|------------|
| **Bob Shell CLI** | ✅ **Transparent — automatic** | Nothing. The `knowledge-manager` mode runs `bob-optimize` as a background subprocess when assembling KB context. You ask a question; Bob answers; compression happened invisibly. |
| **Bob Shell CLI** | ✅ On demand in the chat | Type *"Compress this text: …"* — Bob calls `bob-optimize optimize -` via its `command` tool and returns the compressed text. |
| **Bob IDE chat** | ✅ Via Python library | Type *"Use TokenOptimizer to compress: …"* — Bob runs `from src.facade import TokenOptimizer` in the workspace Python environment. More reliable than the CLI path in IDE. |
| **Bob IDE chat** | ⚠️ Via CLI | Works only if the `.venv/` is activated in the IDE's shell context. Falls back silently if unavailable — KB retrieval is never blocked. |

**In Bob Shell CLI you never need to type a `bob-optimize` command.** If it is in `PATH`, the mode
applies it automatically. If it is absent, the mode skips it silently and KB retrieval continues
unchanged.

---

### Example A — Compress a prompt before sending to an LLM (CLI, zero code)

```bash
# Shorten a long prompt by ~20%, near-losslessly, directly from the shell
echo "Your verbose system prompt here..." | bob-optimize optimize -

# Machine-readable output — get compressed text and token counts as JSON
echo "Your verbose system prompt here..." | bob-optimize optimize - --json
# → {"optimized_text": "...", "compression_ratio": 0.80,
#    "token_count_before": 450, "token_count_after": 360}

# Compress a file in-place (preview — prints to stdout, does not overwrite)
bob-optimize optimize path/to/my-prompt.txt
```

**Benefit:** ~20% fewer tokens on every LLM call that uses this prompt, at no quality cost
(whitespace and redundant-phrase removal only). Manifest-backed at
[`evaluation/results/validation-2026-07-14/`](evaluation/results/validation-2026-07-14/).

---

### Example B — Reuse results across sessions with the cache (Python library)

```python
from src.facade import TokenOptimizer

optimizer = TokenOptimizer()           # L1 exact cache + L2 semantic cache wired automatically

# First call: optimizer runs, result is cached in L1
r1 = optimizer.optimize("Summarise the authentication module architecture.")
print(r1["optimized_text"])            # compressed text
print(r1["compression_ratio"])         # e.g. 0.80 → ~20% smaller (manifest: evaluation/results/validation-2026-07-14/)
print(r1["token_count_before"])        # tokens in original
print(r1["token_count_after"])         # tokens after compression

# Second call with the same prompt: L1 cache hit — optimizer does NOT run
r2 = optimizer.optimize("Summarise the authentication module architecture.")
# r2["optimized_text"] == r1["optimized_text"], returned in <1 ms

# Semantically similar prompt: L2 semantic cache hit — still no recompute
r3 = optimizer.optimize("Give me the architecture summary for the auth module.")
# L2 hit if cosine similarity ≥ 0.85 against the cached prompt embedding
```

**Benefit:** Identical or near-identical prompts across a long session are served from cache at
<1 ms (L1) or <100 ms (L2) — the optimizer runs once, not on every repeated question.

> **Bob IDE tip:** ask Bob directly — *"Use TokenOptimizer to compress this text: …"* — and Bob
> will execute this code in the workspace Python environment and return the compressed result.

---

### Example C — KB context compression: automatic in Bob Shell CLI, on-demand in Bob IDE

**Bob Shell CLI — nothing to do.** The `knowledge-manager` mode already runs this pattern as a
background subprocess whenever it assembles KB context for injection. Install `bob-optimize` once;
the mode handles the rest transparently.

**Bob IDE — ask Bob directly in the chat:**

```text
Compress this KB context before I use it in a prompt:
<paste the text you retrieved from the knowledge base>
```

Bob IDE will execute `TokenOptimizer().optimize(...)` in the workspace and return the compressed
text, ready to paste.

**When scripting it yourself** (e.g. in a pipeline or pre-commit hook):

```bash
KB_CONTEXT=$(cat docs/knowledge-base/concepts/multi-level-caching.md)

compressed=$(echo "$KB_CONTEXT" | bob-optimize optimize - --json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['optimized_text'])" \
  2>/dev/null)

# Fallback: if bob-optimize is unavailable, use original context unchanged
CONTEXT_TO_INJECT="${compressed:-$KB_CONTEXT}"
```

**Benefit:** ~20% token reduction on retrieved context (manifest-backed). KB retrieval is never
blocked — the `${compressed:-$KB_CONTEXT}` fallback ensures silence on failure.
(Full contract: [INTEGRATIONS.md §4](INTEGRATIONS.md#4-kb-manager--opt-in-context-compression-p1-3))

---

> Full API reference, CLI flags, and integration patterns: **[INTEGRATIONS.md](INTEGRATIONS.md)**

---

## 9. How it compares

| | **Karpathy's LLM-Wiki** | **nvk/llm-wiki** | **Bob Shell KM** |
|---|---|---|---|
| **Nature** | The blueprint / pattern | Full multi-agent implementation | The pattern, native to Bob Shell |
| **Platform** | Any LLM (concept) | Claude Code, Codex, OpenCode… | **IBM Bob Shell** |
| **Mechanism** | 3 layers: raw / wiki / schema | Plugin + `/wiki:*` commands | Two modes + templates + KB + scripts |
| **Research** | You curate | 5–10 parallel agents, auto-compile | Single-agent, natural language, script-assisted |
| **Setup** | DIY | Install a plugin | `install.sh` — **no plugin, no MCP** |
| **Cost posture** | Frugal by design | Powerful; heavier per run | **Engineered for Bobcoin economy** |
| **Production** | Concept | Production | **Beta** |
| **Reach for it when…** | You want the idea | You want a research hub in Claude Code | **You live in Bob Shell and optimise Bobcoins** |

## 10. Token savings — measured, manifest-backed

The three savings mechanisms in this repository are measured and reported **separately**.
Blending them into a single headline would reproduce the fabricated 68.96% figure that was
retracted after the Phase 5 audit.

### Token Optimization System (Python library)

Reproduce with `python -m src.validation`; CI re-runs it on every push.

- **Optimizer compression:** ~20% mean (95% CI ≈ [19%, 21%], N=183 real in-repo docs,
  token-weighted ~23%) — manifest:
  [`evaluation/results/validation-2026-07-14/manifest.json`](evaluation/results/validation-2026-07-14/manifest.json).
  Near-lossless (whitespace + redundant-phrase removal).
- **Cache recompute-avoidance:** workload-dependent — a cache hit avoids full recompute.
  The harness discloses the workload's repeat rate; not blended into the compression figure.
- **Truncation:** lossy budget-fit — deletes content to hit a token target with no fidelity
  guarantee. Reported separately, excluded from the savings headline.
- **Null test:** on shuffled input the optimizer's reduction collapses to near zero —
  confirming the headline is genuine compression, not a measurement artifact.

### Knowledge Manager (Bob Shell mode)

Re-derivation saving: KB doc replaces full source read. Measured via shadow comparison
(`measure_optimizer`, cache=off, tiktoken/gpt-4) on 19 real source→KB file pairs from
this repo. Test suite: [`tests/validation/test_km_savings.py`](tests/validation/test_km_savings.py).

| Corpus | N pairs | Mean savings | 95% CI | What it means |
|--------|--------:|-------------:|-------:|---------------|
| All 19 pairs | 19 | 2% | [−32%, +30%] | No reliable claim — mixed pairing quality |
| Well-formed KB summaries | 10 | **51%** | **[38%, 64%]** | KB doc is genuinely more compact than its source |
| Mismatched pairs (KB ≥ source) | 9 | −52% | — | KB doc is a guide/report, not a summary — overhead, not saving |

**What "well-formed KB summary" means:** the KB document is a compact distillation of a
larger source file. 10 of 19 pairs in this repo meet that bar. The other 9 are legitimate
KB artefacts (guides, research reports, plans) that serve a different purpose and produce
no re-derivation saving.

**ROI on well-formed pairs:** mean 2.22 BC saved per query; breakeven in 1 query against a
0.80 BC creation + 0.30 BC maintenance cost; 80× return at 40 queries.

**Applicability boundary:** recurring architecture/configuration queries on a stable
codebase where the KB doc fully answers the query. Does not apply to first-time
exploratory tasks, debugging sessions, or queries that still require reading the raw source.

**These figures are not additive** with the TOS optimizer's ~20% compression — the two
mechanisms operate at different levels of the stack and have different applicability
conditions.

> To measure your own workload: see
> [`docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md`](docs/knowledge-base/guides/km-bobcoin-savings-measurement-guide.md).


## 11. Maturity and current status

**Current grade: A+ (4.30 / 4.30) against institutional Tier-1 vendor standard.**
Trajectory: D− (0.9) → B+/A− (3.46) → A− (3.70) → A (3.89) → A (4.09) → **A+ (4.30)** across Phases 0–8 + all 4 structural gaps closed (2026-07-18).
Authoritative status: [`STATUS.md`](STATUS.md).

**What "Beta — Not Production Ready" means here:**

| Dimension | Grade | Notes |
|-----------|:-----:|-------|
| Product Integrity & Claims | **A+** | All fabricated metrics retracted and permanently recorded; every published number manifest-backed; machine-validated by CI |
| Architecture & Design | **A+** | Facade holds no logic; factory is single config→constructor home; all config fields wired; SLA v1.0 + load tests + `sentence-transformers` in dev extras (G-1/G-3 closed) |
| Code Correctness | **A+** | C1–C8 + RLock fixed; **N-1–N-4** cache race conditions eliminated (unsynchronised `_similarity_scores` reads, threshold write, promotion-flag write, double `size()` snapshot); behavioral regression tests for each fix; zero `# type: ignore` in `src/`; full mypy scope |
| Testing & Verification | **A+** | **1 112 passed** · ≥80% coverage gate (89.82%) · per-package floors · **14+ race-detector tests** (concurrent eviction, `reset_stats()`, `update_threshold()`, promotion-flag, size-snapshot consistency under thread pressure) · load/soak suite (8 tests) |
| Build, Release & Supply-Chain | **A+** | `uv sync --frozen` in CI · `pip-audit --strict` · 0 CVEs · bandit SAST blocking · CycloneDX SBOM · 3.11+3.12 matrix |
| Documentation | **A+** | Two authoritative arc42 documents · 19 ADRs (ADR-012 superseded) · 41 API docs CI-drift-checked · STRIDE threat model grounded in `path:line` citations · formal SLA |
| Governance & Compliance | **A+** | 12-artifact community health · CODEOWNERS covers all packages (G-4 closed) · STRIDE TOCTOU narrowed · all governance validators in CI |

**Suitable for:**
- ✅ Development, testing, and research environments
- ✅ Internal tools with low risk tolerance
- ✅ Proof-of-concept and experimental deployments

**Not yet suitable for:**
- ❌ Production institutional deployment requiring SLAs
- ❌ Systems requiring compliance certifications or security audit
- ❌ Windows (Bash scripts require macOS/Linux)

**Known limitations:**
- Most tests use tiktoken for token counting, not real LLM APIs
- Sub-agent delegation (`src/delegation/`) is an analysis pipeline (not on the `optimize()` request path); activated via `bob-optimize analyze`
- TTL-based cache eviction is lazy (on-read), not proactive
- `psutil` is optional; some monitoring features degrade without it

**Not claimed:** Enterprise SLAs, production support, guaranteed savings percentages,
automated multi-agent research, or Windows compatibility.

## 12. Security

Local library and CLI — no network service, no stored credentials, no outbound traffic
except two optional first-use downloads:

- **tiktoken BPE vocabulary** (`src/optimizer/token_counter.py:38-46`) — fetched on first
  token-count if the local cache is absent; never triggered in tests.
- **`sentence-transformers/all-MiniLM-L6-v2` model** via `mlx-embeddings`
  (`src/cache/embeddings.py:49`) — fetched once (~22 MB) to `~/.cache/huggingface/` when
  `EmbeddingGenerator(backend="minilm")` is called for the first time. **Only triggered if
  `[mlx]` is installed and `backend="minilm"` is used explicitly. Never triggered by default
  configuration or on CI.**

- **Report a vulnerability:** [`SECURITY.md`](SECURITY.md) — GitHub Private Vulnerability Reporting.
- **Threat model:** [`docs/security/threat-model.md`](docs/security/threat-model.md) — STRIDE analysis;
  supersedes retracted ADR-012.
- **In CI:** bandit SAST (medium+, blocking) · CycloneDX SBOM · `pip-audit` (blocking, 0 CVEs) ·
  Dependabot · path-traversal containment in `src/tools/` verified end-to-end.

## 13. Documentation

- **[docs/README.md](docs/README.md)** — Diátaxis navigation hub (tutorials, how-to, reference, explanation)
- **[docs/bob-ide-guide.md](docs/bob-ide-guide.md)** — Bob IDE complete reference (activation, tool groups, skill, validation, troubleshooting)
- **[docs/quick-start.md](docs/quick-start.md)** — 5-minute getting started — Bob Shell CLI and Bob IDE (arc42 Tier-1)
- **[docs/installation.md](docs/installation.md)** — detailed installation — Bob Shell CLI and Bob IDE (arc42 Tier-1)
- **[docs/usage.md](docs/usage.md)** — usage guide with workflow diagrams (arc42 Tier-1)
- **[docs/kb-manager/architecture.md](docs/kb-manager/architecture.md)** — KB Manager architecture (arc42 v2.1, 13 sections, 8+ diagrams)
- **[docs/architecture/architecture.md](docs/architecture/architecture.md)** — Python token-optimizer architecture (arc42 v3.0, 11 sections, 5 diagrams)
- **[docs/monitoring.md](docs/monitoring.md)** — monitoring & observability (arc42 Tier-1)
- **[docs/sla.md](docs/sla.md)** — SLA v1.0: latency, throughput, quality, concurrency targets
- **[docs/security/threat-model.md](docs/security/threat-model.md)** — STRIDE threat model
- **[docs/adr/](docs/adr/)** — 19 Architecture Decision Records (ADR-012 superseded)
- **[STATUS.md](STATUS.md)** — canonical maturity status (single source of truth)

## References

- **Andrej Karpathy — LLM-Wiki pattern** · https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **nvk/llm-wiki — full multi-agent implementation** · https://github.com/nvk/llm-wiki
- **IBM Bob Shell** · https://bob.ibm.com/docs/shell

---

**Author:** David Leconte · **Platform:** IBM Bob Shell · Inspired by Karpathy's LLM-Wiki and nvk's implementation.
