# Bob Shell Knowledge Manager

### Make your codebase's knowledge *compound* — instead of paying to rediscover it every session.

A native **IBM Bob Shell** implementation of Andrej Karpathy's **LLM-Wiki** pattern, engineered for **Bobcoin economy**.

`MIT licensed` · `Native Bob modes` · `No MCP servers` · `No plugins` · `Pattern: LLM-Wiki (Karpathy)` · `Bob Shell CLI` · `Bob IDE`

> **What this is.** Every Bob session re-reads and re-reasons about the same codebase — and pays
> Bobcoins to do it, again and again. The fix isn't a shorter prompt; it's a **memory**. This project turns
> Bob into a disciplined maintainer of a living, markdown knowledge base: knowledge is written down once
> and *retrieved* thereafter, so the bill falls because the work stops repeating. It ships as **two native
> Bob modes** — no plugin, no MCP server, nothing external in the loop.

---

## ℹ️ This repository contains two independently-operable systems

| System | Technology | Status |
|--------|-----------|--------|
| **Bob Shell Knowledge Manager** | Bash scripts, YAML, Markdown | Stable v1.0 |
| **Token Optimization System** (`src/`) | Python 3.11+, tiktoken, scikit-learn | Beta — Not Production Ready |

Each system works without the other. Three **opt-in** integration points connect them (all fallback-safe — if the Python system is absent, the KB Manager is unaffected): the KB query engine can use the TOS embedding scorer; the `knowledge-manager` mode can compress retrieved context via `bob-optimize`; and a persistent embedding index bridges KB document search with TOS cache infrastructure. See [`INTEGRATIONS.md`](INTEGRATIONS.md).

Architecture: [KB Manager — `docs/kb-manager/ARCHITECTURE.md`](docs/kb-manager/ARCHITECTURE.md) · [Python system — `docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md).

### Supported targets

| Target | Activation | Install step | Skill lazy-load | `save_memory` | **Best for** | **Key trade-off** |
|--------|-----------|--------------|-----------------|---------------|------------|-----------------|
| **Bob Shell CLI** | `bob --chat-mode=knowledge-manager` | `scripts/install.sh` | not supported | ✅ available | Daily CLI users; full `save_memory` | One-time install + `~/.zshrc` alias |
| **Bob IDE** | Mode picker → 📚 Knowledge Manager | none — zero steps | ✅ auto-loaded | ❌ file persistence only | IDE users; zero install | No cross-session `save_memory` facts |

> **Bob IDE users:** see [`docs/BOB-IDE-GUIDE.md`](docs/BOB-IDE-GUIDE.md) for the full IDE workflow.

---

## 1. The problem: you're paying to relearn what Bob already knew

IBM's own guidance is blunt about where a session's budget goes. Every turn burns **input**, **output**,
and **reasoning** tokens — and the two you can't see are the expensive ones.

Teams respond by trimming the visible line: disabling tools, pasting less, shortening prompts. That helps —
until it hits a floor. Because the largest recurring cost isn't the prompt. **It's re-derivation.** Session
after session, Bob re-reads your architecture, re-infers the same relationships, and re-explains the same
concepts — because nothing it learned last time survived the end of the thread.

> The cheapest session is the one that never has to think a thought twice.

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

## 3. This implementation: native to Bob Shell

Bob Shell Knowledge Manager is that pattern, built entirely on Bob's **native** capabilities:

- **📚 `knowledge-manager` mode** — structured KB maintainer: concepts / guides / references / research,
  consistent templates, bidirectional cross-references, `save_memory` *(Bob Shell CLI only — Bob IDE uses
  file persistence)*, self-updating `INDEX.md`.
- **🔍 `repo-analyzer` mode** — 7-phase repository audit that runs analysis *scripts* and files digested
  findings into the KB, instead of dragging raw source through the context window.
- **The schema layer** — your `AGENTS.md` plus the mode definition *are* Karpathy's third layer: stable
  rules that make Bob both disciplined and cacheable.

<p align="center">
  <img src="docs/assets/kb-compounding-loop.svg" alt="The compounding-knowledge loop: Bob reads your repository once, files digested knowledge into a version-controlled knowledge base, and every later session retrieves from that knowledge base instead of re-deriving from the repo." width="760">
</p>

## 4. Why it saves Bobcoins: structure, not a benchmark

The savings are **structural** — each IBM token-economy principle has a concrete home in how the modes behave:

| IBM principle | The recurring waste | How the modes remove it |
|---|---|---|
| **Catalog tax** | Every MCP server re-sends its full tool catalog every turn | Native Bob mode — **no plugin, no MCP** |
| **Payload tax** | A 2,000-line file attached when 20 lines matter | `repo-analyzer` runs scripts that **summarise**; the KB stores digested reports you *cite*, not raw source |
| **Compression trap** | Stripping meaning can backfire and *raise* effective cost | Templates **preserve** meaning — rationale, real names, cross-refs |
| **Short threads** | Turn 15 re-pays 14 turns of stale history | Knowledge persists in KB files + `save_memory` *(Bob Shell CLI)* / file persistence *(Bob IDE)*; a fresh thread **retrieves** |
| **Let caching work** | Reworded prefixes miss the cache | Fixed mode definition + `AGENTS.md` + KB layout = a **cacheable prefix** |
| **Trim output** | Verbose narration is paid on every reply | Bounded artifacts: templates, `INDEX.md`, reports — not essays |

## 5. Get started in 5 minutes (one-time setup)

No custom mode required. Point three scripts at your project, then let any Bob mode do the thinking.

> **Full-stack setup (recommended):** Run `./scripts/setup.sh` once from the repo
> root. It installs the Token Optimization System, builds the KB embedding index,
> and prints an integration health report (`bob-optimize kb-status`). The KB Manager
> works without it — setup.sh only activates the optional Python integrations.

```bash
# 0 · Set once, to wherever you cloned this repo
KM_HOME=~/Projects/bob-llmwiki-knowledge-manager

# 1 · Scaffold the knowledge base in your project
cd ~/your-project
"$KM_HOME/scripts/init-project.sh"

# 2 · Full automated analysis, filed into docs/knowledge-base/
"$KM_HOME/scripts/run-full-analysis.sh"

# 3 · Validate KB structure
"$KM_HOME/scripts/validate-kb.sh"
```

> **What `run-full-analysis.sh` produces:** 7 Bash scripts run against your repo and file 7 dated
> Markdown snapshots into `docs/knowledge-base/research/` (scan, dependencies, metrics, security,
> test coverage, git history, docs coverage). Bob reads these ~200-line digested reports instead of
> raw source — that is why the KB session immediately produces grounded suggestions. Start the KB
> session *after* this step. Re-run it any time to refresh dated snapshots without overwriting prior
> KB work. Full details: [`docs/knowledge-base/guides/complete-repository-analysis.md`](docs/knowledge-base/guides/complete-repository-analysis.md).

Then, in any Bob mode (Ask, Code, …):

```text
I want you to act as a knowledge manager for this codebase.

Your role:
- Document code in docs/knowledge-base/
- Use templates from <KM_HOME>/config/templates/
- Create concept documents for core ideas, guides for how-to instructions,
  references for API documentation, research notes for investigations
- Maintain INDEX.md with all documents and add bidirectional cross-references

Start by analyzing the codebase and suggesting 5 initial documents to create.
```

The scripts have already filed 7 dated research snapshots into `docs/knowledge-base/research/`, so Bob
proposes documents **grounded in evidence it didn't have to re-read from raw source**.

> *Optional:* the `knowledge-manager` mode packages this as a one-liner (`./scripts/install.sh`) for Bob Shell CLI,
> or is available immediately via the mode picker in Bob IDE. Not required.

## 6. Starting a new session (daily use)

Bob Shell sessions start fresh — the mode does not persist between restarts. After the one-time setup above, every new session takes one step.

### Path E — Bob IDE mode picker

No installation or CLI required. The Knowledge Manager mode is bundled in `.bob/custom_modes.yaml`.

1. Open the workspace in Bob IDE (VS Code / Cursor with the Bob extension).
2. Click the mode picker in the bottom-left status bar (shows the current mode name).
3. Scroll to **📚 Knowledge Manager** and select it.
4. Bob IDE loads `.bob/skills/knowledge-manager/SKILL.md` automatically via the `skill` group.

> **Full reference:** [`docs/BOB-IDE-GUIDE.md`](docs/BOB-IDE-GUIDE.md)

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
KB location: docs/knowledge-base/  (INDEX.md is loaded in context)
Resume: summarise what exists in the KB, what was most recently documented,
and suggest what to work on next.
Workflow: follow the 7-step process (determine category → select template →
apply naming convention → write content → add cross-references → save to
memory → update INDEX.md).
```

### Standard resume prompt (first message of every session)

Once activated, open with:

```text
What did we document most recently? Summarise the KB and suggest what to work on next.
```

Bob will scan `INDEX.md` (auto-loaded via `.bob/settings.json`), recall any `save_memory` facts from prior sessions *(Bob Shell CLI only — Bob IDE uses file persistence in `docs/knowledge-base/`)*, and propose the next logical documents or updates.

> **Full reference:** [`docs/USAGE.md §0`](docs/USAGE.md#0-starting-a-session) · [`docs/knowledge-base/guides/activating-knowledge-manager-in-new-session.md`](docs/knowledge-base/guides/activating-knowledge-manager-in-new-session.md)

### Mode switching and the KB

Switching mode mid-session (e.g. `/mode agent` to write code) does **not** delete or hide KB files — they
remain on disk exactly as written. What stops is the **maintenance discipline**: templates, bidirectional
cross-references, and `INDEX.md` updates are enforced by the `knowledge-manager` mode's instructions, not
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
- Knowledge-base structure with self-maintained `INDEX.md` and `save_memory` integration *(Bob Shell CLI; Bob IDE uses file persistence)*
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

The optimizer savings below are **measured** over a real corpus and carry a reproducibility manifest.
Reproduce with `python -m src.validation`; CI re-runs it on every push.

- **Optimizer compression:** ~20% mean savings (95% CI ≈ [19%, 21%], N=183 real in-repo docs, token-weighted ~23%) — manifest: [`evaluation/results/validation-2026-07-14/manifest.json`](evaluation/results/validation-2026-07-14/manifest.json). Near-lossless (whitespace + redundant-phrase removal).
- **Cache recompute-avoidance:** workload-dependent — a cache hit avoids full recompute. The harness
  discloses the workload's repeat rate separately; it is not blended into the compression figure.
- **Truncation:** lossy budget-fit — deletes content to hit a token target with no fidelity guarantee.
  Reported separately, excluded from the savings headline.
- **Null test:** on shuffled input the optimizer's reduction collapses to near zero — confirming the
  headline is genuine compression, not a measurement artifact.


## 11. Maturity and current status

**Current grade: A+ (4.30 / 4.30) against institutional Tier-1 vendor standard.**
Trajectory: D− (0.9) → B+/A− (3.46) → A− (3.70) → A (3.89) → A (4.09) → **A+ (4.30)** across Phases 0–8 + all 4 structural gaps closed (2026-07-18).
Authoritative status: [`STATUS.md`](STATUS.md).

**What "Beta — Not Production Ready" means here:**

| Dimension | Grade | Notes |
|-----------|:-----:|-------|
| Product Integrity & Claims | **A+** | All fabricated metrics retracted and permanently recorded; every published number manifest-backed; machine-validated by CI |
| Architecture & Design | **A+** | Facade holds no logic; factory is single config→constructor home; all config fields wired; SLA v1.0 + load tests + `sentence-transformers` in dev extras (G-1/G-3 closed) |
| Code Correctness | **A+** | C1–C8 + RLock fixed; behavioral regression tests for each; zero `# type: ignore` in `src/`; full mypy scope including `src/delegation/` + `src/tools/` (G-2 closed) |
| Testing & Verification | **A+** | 1053+ passed · ≥80% coverage gate · per-package floors · delegation floor 70%, measured 84% (ADR-019); load/soak suite (8 tests) |
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
- **Threat model:** [`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md) — STRIDE analysis;
  supersedes retracted ADR-012.
- **In CI:** bandit SAST (medium+, blocking) · CycloneDX SBOM · `pip-audit` (blocking, 0 CVEs) ·
  Dependabot · path-traversal containment in `src/tools/` verified end-to-end.

## 13. Documentation

- **[docs/README.md](docs/README.md)** — Diátaxis navigation hub (tutorials, how-to, reference, explanation)
- **[docs/BOB-IDE-GUIDE.md](docs/BOB-IDE-GUIDE.md)** — Bob IDE complete reference (activation, tool groups, skill, validation, troubleshooting)
- **[docs/QUICK_START.md](docs/QUICK_START.md)** — 5-minute getting started — Bob Shell CLI and Bob IDE (arc42 Tier-1)
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** — detailed installation — Bob Shell CLI and Bob IDE (arc42 Tier-1)
- **[docs/USAGE.md](docs/USAGE.md)** — usage guide with workflow diagrams (arc42 Tier-1)
- **[docs/kb-manager/ARCHITECTURE.md](docs/kb-manager/ARCHITECTURE.md)** — KB Manager architecture (arc42 v2.1, 13 sections, 8+ diagrams)
- **[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)** — Python token-optimizer architecture (arc42 v3.0, 11 sections, 5 diagrams)
- **[docs/MONITORING.md](docs/MONITORING.md)** — monitoring & observability (arc42 Tier-1)
- **[docs/SLA.md](docs/SLA.md)** — SLA v1.0: latency, throughput, quality, concurrency targets
- **[docs/security/THREAT_MODEL.md](docs/security/THREAT_MODEL.md)** — STRIDE threat model
- **[docs/adr/](docs/adr/)** — 19 Architecture Decision Records (ADR-012 superseded)
- **[STATUS.md](STATUS.md)** — canonical maturity status (single source of truth)

## References

- **Andrej Karpathy — LLM-Wiki pattern** · https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **nvk/llm-wiki — full multi-agent implementation** · https://github.com/nvk/llm-wiki
- **IBM Bob Shell** · https://bob.ibm.com/docs/shell

---

**Author:** David Leconte · **Platform:** IBM Bob Shell · Inspired by Karpathy's LLM-Wiki and nvk's implementation.
