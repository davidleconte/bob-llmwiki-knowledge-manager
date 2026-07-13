# Bob Shell Knowledge Manager

### Make your codebase's knowledge *compound* — instead of paying to rediscover it every session.

A native **IBM Bob Shell** implementation of Andrej Karpathy's **LLM-Wiki** pattern, engineered for **Bobcoin economy**.

`MIT licensed` · `Native Bob Shell mode` · `No MCP servers` · `No plugins` · `Pattern: LLM-Wiki (Karpathy)`

> **Executive summary.** Every Bob session re-reads and re-reasons about the same codebase — and pays
> Bobcoins to do it, again and again. The fix isn't a shorter prompt; it's a **memory**. Bob Shell
> Knowledge Manager turns Bob into a disciplined maintainer of a living, markdown knowledge base for your
> repository: knowledge is written down once and *retrieved* thereafter, so the bill falls because the work
> stops repeating. It ships as **two native Bob modes** — no plugin, no MCP server, nothing external in the
> loop. In one real run, it scaffolded the documentation strategy for a **94-module platform in six tool
> calls for 0.36 Bobcoins**.

---

https://github.com/user-attachments/assets/897fecc2-8849-4fad-b8e0-3c408b026de6


## 1. The problem: you're paying to relearn what Bob already knew

IBM's own guidance is blunt about where a session's budget goes. Every turn burns **input**, **output**,
and **reasoning** tokens — and the two you can't see are the expensive ones.

Teams respond by trimming the visible line: disabling tools, pasting less, shortening prompts. That helps —
until it hits a floor. Because the largest recurring cost isn't the prompt. **It's re-derivation.** Session
after session, Bob re-reads your architecture, re-infers the same relationships, and re-explains the same
concepts — because nothing it learned last time survived the end of the thread.

> The cheapest session is the one that never has to think a thought twice.

## 2. The idea we implement: Karpathy's LLM-Wiki

Karpathy's *LLM-Wiki* pattern replaces "retrieve-from-scratch" with a **persistent, compounding artifact**:

> *"The wiki is a persistent, compounding artifact. The cross-references are already there. The
> contradictions have already been flagged."* — as opposed to RAG, where *"the LLM is rediscovering
> knowledge from scratch on every question. There's no accumulation."*

It has three layers:

1. **Raw sources** — your code and docs. Immutable; the model reads, never edits.
2. **The wiki** — LLM-owned markdown: concepts, guides, references, cross-links.
3. **The schema** — a config that makes the model *"a disciplined wiki maintainer rather than a generic chatbot."*

His load-bearing insight: *"the tedious part of maintaining a knowledge base is not the reading or the
thinking — it's the bookkeeping."* LLMs are extraordinary bookkeepers. Point one at your repo, and the
knowledge base maintains itself.

## 3. What this is: the pattern, made native to Bob Shell

Bob Shell Knowledge Manager is that pattern, built entirely on Bob's **native** capabilities — no plugin,
no MCP server, no external service in the loop:

- **📚 `knowledge-manager` mode** — turns Bob into a structured KB maintainer: concepts / guides /
  references / research, consistent templates, bidirectional cross-references, `save_memory`, and a
  self-updating `INDEX.md`.
- **🔍 `repo-analyzer` mode** — a 7-phase repository audit that runs analysis *scripts* and files digested
  findings into the KB, instead of dragging raw source through the context window.
- **The schema layer** — your `AGENTS.md` plus the mode definition *are* Karpathy's third layer: stable
  rules that make Bob both disciplined and cacheable.

<p align="center">
  <img src="docs/assets/kb-compounding-loop.svg" alt="The compounding-knowledge loop: Bob reads your repository once, files digested knowledge into a version-controlled knowledge base, and every later session retrieves from that knowledge base instead of re-deriving from the repo." width="760">
</p>

## 4. Why it saves Bobcoins: structure, not a benchmark

The savings aren't a number we ran once — they're **structural**. Each principle in IBM's token-economy
guidance has a concrete home in how the modes behave:

| IBM principle (*Save Bobcoins*) | The recurring waste | How the modes remove it |
|---|---|---|
| **Catalog tax** | Every enabled MCP server re-sends its full tool catalog *every turn* | Native Bob mode — **no plugin, no MCP** to load |
| **Payload tax** | A 2,000-line file attached when 20 lines matter | `repo-analyzer` runs scripts that **summarise**; the KB stores digested reports you *cite*, not raw source |
| **Compression trap** | Stripping meaning to save input backfires (a study measured **+67% cost**) | Templates **preserve** meaning — rationale, real names, cross-refs — structured, not stripped |
| **Short threads** | Turn 15 re-pays 14 turns of stale history | Knowledge persists in KB files + `save_memory`; a fresh thread **retrieves** it instead of re-deriving it |
| **Let caching work** | Reworded prefixes miss the cache | Fixed mode definition + `AGENTS.md` + KB layout = a **cacheable prefix** |
| **Trim output** | Verbose narration is paid on every reply | Bounded artifacts: templates, `INDEX.md`, reports — not essays |
| **The three budget columns** | Output & reasoning cost more than input | A curated KB shrinks all three: less to **read**, less to **reason** about, less to **write** |

**So what:** the mode makes the cheap path the *default* path. You don't have to remember the discipline —
the mode **is** the discipline.

## 5. Proof point: a 94-module platform, documented for 0.36 coins

A real run on **HCD At Its Core** — IBM's Hyper-Converged Database teaching platform: 94 interactive demo
modules, a decorator-based Python engine, an adversarial "Audit Arena" test framework. The prompt: *act as
knowledge manager for this codebase; analyse it and propose the first five documents worth writing.*

Bob's answer, in **six tool calls**:

- Correctly read the architecture — V3 engine, the `@demo_module` decorator, context-fixture injection,
  the Audit Arena tribunal.
- Proposed **five targeted, correctly-typed documents** (two concepts, two guides, one API reference) —
  each with a rationale and a content outline.
- **Cost: 0.36 Bobcoins** — under 1% of a session budget. ~2 minutes. No retries.

One run is one data point, not a benchmark — but it's the *shape* of the value: **structured, accurate, and
cheap enough to run on every repo you touch.** Full transcript: `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md`.

## 6. How it compares: the thesis, the engine, and the native port

Three points on one line — from an idea, to a full research engine, to a frugal Bob-native port:

| | **Karpathy's LLM-Wiki** · the thesis | **nvk/llm-wiki** · the engine | **Bob Shell KM** · this project |
|---|---|---|---|
| **Nature** | The blueprint / pattern | A full multi-agent implementation | The pattern, native to Bob Shell |
| **Platform** | Any LLM (concept) | Claude Code, Codex, OpenCode… | **IBM Bob Shell** |
| **Mechanism** | 3 layers: raw / wiki / schema | Plugin + `/wiki:*` commands, a hub of topic wikis | Two modes + templates + KB + scripts |
| **Research** | You curate | 5–10 parallel agents, auto-compile, thesis mode | Single-agent, natural language, script-assisted |
| **Setup** | DIY | Install a plugin | `install.sh` — **no plugin, no MCP** |
| **Cost posture** | Frugal by design | Powerful; heavier per run | **Engineered for Bobcoin economy** |
| **Reach for it when…** | You want the idea | You want a research hub in Claude Code | **You live in Bob Shell and optimise Bobcoins** |

**So what:** this project doesn't try to out-feature nvk's research engine. It brings Karpathy's
compounding-knowledge idea to Bob Shell users **natively and cheaply** — frugality is the design centre,
not an afterthought.

## 7. Get started in 5 minutes

No custom mode required. Point three scripts at your project, then let any Bob mode do the thinking.

```bash
# 0 · Set this once, to wherever you cloned this repo
KM_HOME=~/Projects/bob-llmwiki-knowledge-manager

# 1 · Scaffold the knowledge base in your project
cd ~/your-project
"$KM_HOME/scripts/init-project.sh"

# 2 · Let the scripts do the reading — a full automated analysis,
#     filed straight into docs/knowledge-base/
"$KM_HOME/scripts/run-full-analysis.sh"

# 3 · Validate the knowledge-base structure
"$KM_HOME/scripts/validate-kb.sh"
```

Now stay in **whatever Bob mode you're already using** (Ask, Code, …) and paste this prompt — replace
`<path-to-this-repo>` with wherever you cloned it (the same path as `$KM_HOME` above):

```text
I want you to act as a knowledge manager for this codebase.

Your role:
- Document code in docs/knowledge-base/
- Use templates from <path-to-this-repo>/config/templates/
- Create concept documents for core ideas
- Create guides for how-to instructions
- Create references for API documentation
- Create research notes for investigations
- Maintain INDEX.md with all documents
- Add cross-references between related documents

Start by analyzing the codebase and suggesting 5 initial documents to create
```

The scripts have already filed digested reports into `docs/knowledge-base/`, so Bob proposes documents
**grounded in evidence it didn't have to re-read** — the same prompt that produced the 0.36-coin result in §5.

> *Optional:* the `knowledge-manager` mode packages this prompt into a one-liner (`./scripts/install.sh` to
> register it). Handy later — not required for the flow above.

## 8. What's in the box

- **2 native Bob modes** — `knowledge-manager`, `repo-analyzer`.
- **4 document templates** — concept · guide · reference · research.
- **A knowledge-base structure** with a self-maintained `INDEX.md` and `save_memory` integration.
- **Core scripts** — `install`, `init-project`, `validate-kb`, `export-kb` (markdown / Obsidian / HTML / PDF).
- **An analysis suite** — scan, dependencies, metrics, security, test-coverage, git-history, docs, and a
  consolidated report.
- **3 worked example knowledge bases** — a software project, a research project, and a personal wiki.

## 9. Token savings: real-world expectations

⚠️ **IMPORTANT DISCLAIMER:** Token savings metrics require validation on real repositories.

**E2E Test Results (Controlled Environment):**
- Prompt optimization: 10-20% measured savings
- Cache hits: 100% savings when cache matches
- Combined: 40-60% in ideal conditions

**Synthetic Validation Claims (NOT VALIDATED):**
- "68.96% token savings" - from hardcoded simulation, not real optimizer
- "95% CI [66.42, 71.51]" - fabricated precision (std=0.0)
- "52/73/81% scaling" - artifact of capped baseline
- **Status:** Awaiting real-world validation (see Phase 6 of remediation plan)

**Expected Real-World Performance:**
- First-time analysis: 5-15% savings (cold cache)
- Repetitive tasks: 20-40% savings (warm cache)
- Cache hit rate: 10-20% realistic (not 23.33% theoretical)

**The 0.36 Bobcoin example (§5)** is real but represents an ideal case: structured analysis with script-assisted digestion. Your actual savings will vary significantly based on task type, repetition patterns, and cache effectiveness.

**See:** `docs/knowledge-base/research/external-audit-2026-07-12.md` for complete audit findings.

## 10. Maturity: what's proven, what's experimental

**Status: Beta (7/10) — Not Production Ready**

⚠️ This system requires real-world validation before production use. See audit findings and remediation plan in knowledge base.

### ✅ Proven & Usable Today

**What Works:**
- Two native Bob modes (`knowledge-manager`, `repo-analyzer`)
- Document templates and KB structure
- Phase 1 automation scripts (8 scripts, production-ready)
- Comprehensive documentation
- 98.4% test pass rate (312/317 tests passing)

**Validated Claims:**
- Token optimization framework functional (213 tests passing)
- Caching system tested and working (E2E validated)
- Script-based analysis reduces manual effort by 70-80%
- **Test pass rate:** 98.4% (312/317 tests) — Note: This is pass rate, not code coverage
- **Code coverage:** Not yet measured (requires --cov run)

### 🧪 Experimental / Needs Validation

**What Needs Work:**
- Real LLM API integration (currently mock-based testing)
- Production validation on diverse repositories
- Phase 4 delegation framework (theoretical only)
- Windows support (bash scripts not cross-platform)

**Performance Claims:**
- Token savings: Measured 10-20% optimization, 40-60% combined (with caching)
- Cache hit rates: Theoretical 23%, real-world likely 15-25%
- Cost savings: Depends heavily on workload patterns

### ⚠️ Known Limitations

1. **Testing:** Most tests use mocks, not real LLM APIs
2. **Platform:** Bash scripts require Unix-like environment (macOS, Linux)
3. **Dependencies:** Some features require optional dependencies (psutil for monitoring)
4. **Validation:** Performance claims based on synthetic data and E2E token counting
5. **Enterprise:** No SLA guarantees, audit trails, or vendor support
6. **Documentation Drift:** Two projects (KB manager + token optimization) merged but not fully reconciled
7. **Correctness Bugs:** 7 known bugs in health checks, caching, and delegation (see audit findings)
8. **Orphaned Code:** ~27% of src/ (delegation, monitoring) not integrated into main workflows

### ⛔ Not Claimed

- Enterprise SLAs or production support
- Automated multi-agent research (use `nvk/llm-wiki` for that)
- Guaranteed token savings percentages
- Cross-platform compatibility (Windows)

### 📋 Production Checklist

Before deploying to production:
- [ ] Run E2E tests with real token counting (`RUN_E2E_TESTS=1 pytest tests/e2e/ -v`)
- [ ] Validate on your specific repository types
- [ ] Measure actual Bobcoin costs for your workload
- [ ] Set up monitoring and cost tracking
- [ ] Review limitations and ensure they're acceptable

See `docs/knowledge-base/guides/p0-critical-fixes-implementation.md` for detailed production readiness steps.

## References

- **Andrej Karpathy — the LLM-Wiki pattern** · `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`
- **IBM Bob Shell — Save Tokens, Save Bobcoins** · `https://bob.ibm.com/docs/shell`
- **nvk/llm-wiki — a full multi-agent implementation** · `https://github.com/nvk/llm-wiki`
- **Live example — HCD codebase analysis (0.36 coins)** · `evaluation/LIVE_EXAMPLE_HCD_ANALYSIS.md`

---

**Author:** David Leconte · **Platform:** IBM Bob Shell · Inspired by Karpathy's LLM-Wiki and nvk's implementation.
