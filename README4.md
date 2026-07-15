# Bob Shell Knowledge Manager

### Make your codebase's knowledge *compound* — instead of paying to rediscover it every session.

A native **IBM Bob Shell** implementation of Andrej Karpathy's **LLM-Wiki** pattern, engineered for **Bobcoin economy**.

`MIT licensed` · `Native Bob Shell mode` · `No MCP servers` · `No plugins` · `Pattern: LLM-Wiki (Karpathy)`

> **What this is.** Every Bob session re-reads and re-reasons about the same codebase — and pays
> Bobcoins to do it, again and again. The fix isn't a shorter prompt; it's a **memory**. This project turns
> Bob into a disciplined maintainer of a living, markdown knowledge base: knowledge is written down once
> and *retrieved* thereafter, so the bill falls because the work stops repeating. It ships as **two native
> Bob modes** — no plugin, no MCP server, nothing external in the loop.

---

## ⚠️ This repository contains two separate systems

| System | Technology | Status |
|--------|-----------|--------|
| **Bob Shell Knowledge Manager** | Bash scripts, YAML, Markdown | Stable v1.0 |
| **Token Optimization System** (`src/`) | Python 3.11+, tiktoken, scikit-learn | Beta — Not Production Ready |

They share a repository but are **not integrated**. The Python system is composed behind a single
`TokenOptimizer` facade and `bob-optimize` CLI (`python -m src`).
Architecture: [KB Manager — `docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [Python system — `docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md).

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
  consistent templates, bidirectional cross-references, `save_memory`, self-updating `INDEX.md`.
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
| **Short threads** | Turn 15 re-pays 14 turns of stale history | Knowledge persists in KB files + `save_memory`; a fresh thread **retrieves** |
| **Let caching work** | Reworded prefixes miss the cache | Fixed mode definition + `AGENTS.md` + KB layout = a **cacheable prefix** |
| **Trim output** | Verbose narration is paid on every reply | Bounded artifacts: templates, `INDEX.md`, reports — not essays |

## 5. Get started in 5 minutes

No custom mode required. Point three scripts at your project, then let any Bob mode do the thinking.

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

The scripts have already filed digested reports into `docs/knowledge-base/`, so Bob proposes documents
**grounded in evidence it didn't have to re-read**.

> *Optional:* the `knowledge-manager` mode packages this as a one-liner (`./scripts/install.sh`). Not required.

## 6. What's in the box

**Bob Shell Knowledge Manager (the Bash system):**
- 2 native Bob modes — `knowledge-manager`, `repo-analyzer`
- 4 document templates — concept · guide · reference · research
- Knowledge-base structure with self-maintained `INDEX.md` and `save_memory` integration
- Core scripts — `install`, `init-project`, `validate-kb`, `export-kb` (Markdown / Obsidian / HTML / PDF)
- Analysis suite — scan, dependencies, metrics, security, test-coverage, git-history, docs, consolidated report
- 3 worked example knowledge bases — software project, research project, personal wiki

**Token Optimization System (the Python system, `src/`):**
- `TokenOptimizer` facade + `bob-optimize` CLI — composes all components behind one interface
- Multi-level cache — L1 exact match (<1 ms), L2 semantic similarity (<100 ms), with TTL enforcement
- Prompt optimizer — ~20% mean compression, near-lossless, tiktoken-counted (manifest: `evaluation/results/validation-2026-07-14/manifest.json`)
- Truncation — smart budget-fit strategies (lossy; reported separately from compression)
- Structured monitoring — JSON logging, metrics, health checks, cost tracking

## 7. How it compares

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

## 8. Token savings — measured, manifest-backed

The optimizer savings below are **measured** over a real corpus and carry a reproducibility manifest.
Reproduce with `python -m src.validation`; CI re-runs it on every push.

- **Optimizer compression:** ~20% mean savings (95% CI ≈ [19%, 21%], N=183 real in-repo docs, token-weighted ~23%) — manifest: [`evaluation/results/validation-2026-07-14/manifest.json`](evaluation/results/validation-2026-07-14/manifest.json). Near-lossless (whitespace + redundant-phrase removal).
- **Cache recompute-avoidance:** workload-dependent — a cache hit avoids full recompute. The harness
  discloses the workload's repeat rate separately; it is not blended into the compression figure.
- **Truncation:** lossy budget-fit — deletes content to hit a token target with no fidelity guarantee.
  Reported separately, excluded from the savings headline.
- **Null test:** on shuffled input the optimizer's reduction collapses to near zero — confirming the
  headline is genuine compression, not a measurement artifact.

> ⚠️ **Retracted:** the earlier "68.96% / 95% CI [66.42, 71.51] / VALIDATED" figures were fabricated by
> a simulation that never invoked the optimizer. See
> [`evaluation/VALIDATION_DISCLAIMER.md`](evaluation/VALIDATION_DISCLAIMER.md).

**On the 0.36 Bobcoin HCD example:** one reported run on a 94-module platform allegedly cost 0.36 Bobcoins
in six tool calls. This figure has no token counts, tokenizer, model, or reproducibility manifest and
represents an ideal case (structured analysis, script-assisted digestion). **It cannot be independently
verified.** Do not base adoption decisions on it. The measured ~20% compression (manifest-backed, see §8) is the honest number.

## 9. Maturity and current status

**Current grade: A (3.89 / 4.30) against institutional vendor standard.**
Trajectory: D− (0.9) → B+/A− (3.46) → A− (3.70) → **A (3.89)** across Phases 0–8 + post-Phase-8 gap closure.
Authoritative status: [`STATUS.md`](STATUS.md). Authoritative audit: [`docs/knowledge-base/research/audit-2026-07-14-post-remediation.md`](docs/knowledge-base/research/audit-2026-07-14-post-remediation.md).

**What "Beta — Not Production Ready" means here:**

| Dimension | Grade | Notes |
|-----------|:-----:|-------|
| Product Integrity & Claims | **A** | All fabricated metrics retracted; README duplicates deleted |
| Architecture & Design | A− | Clean facade + layering; ADR-013 added; §9 Deployment + §10 Glossary added; architecture docs B− → A−; dead `strategies` config field remains |
| Code Correctness | **A** | C1–C7 + RLock + C8 singletons fixed; behavioral regression tests for each |
| Testing & Verification | A− | 899 passed · 87.1% coverage (gate ≥80%) · delegation floor frozen at 52% |
| Build, Release & Supply-Chain | **A** | CI locked to uv.lock · 0 CVEs · bandit SAST blocking · SBOM |
| Documentation | **A** | Diátaxis spine · docs/ root curated · two authoritative arch docs (one per system) · all docs/ Tier-1 arc42 · API docs in sync |
| Governance & Compliance | A− | 12-artifact community health · STRIDE threat model · TOCTOU unnamed |

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
- Sub-agent delegation (`src/delegation/`) is experimental and intentionally not wired into the facade
- TTL-based cache eviction is lazy (on-read), not proactive
- `psutil` is optional; some monitoring features degrade without it

**Not claimed:** Enterprise SLAs, production support, guaranteed savings percentages,
automated multi-agent research, or Windows compatibility.

## 10. Security

Local library and CLI — no network service, no stored credentials, no outbound traffic
(except optional tiktoken BPE vocab download on first use).

- **Report a vulnerability:** [`SECURITY.md`](SECURITY.md) — GitHub Private Vulnerability Reporting.
- **Threat model:** [`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md) — STRIDE analysis;
  supersedes retracted ADR-012.
- **In CI:** bandit SAST (medium+, blocking) · CycloneDX SBOM · `pip-audit` (blocking, 0 CVEs) ·
  Dependabot · path-traversal containment in `src/tools/` verified end-to-end.

## 11. Documentation

- **[docs/README.md](docs/README.md)** — Diátaxis navigation hub (tutorials, how-to, reference, explanation)
- **[docs/QUICK_START.md](docs/QUICK_START.md)** — 5-minute getting started (arc42 Tier-1)
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** — detailed installation (arc42 Tier-1)
- **[docs/USAGE.md](docs/USAGE.md)** — usage guide with workflow diagrams (arc42 Tier-1)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — KB Manager architecture (arc42 v2.0, 13 sections, 8+ diagrams)
- **[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)** — Python token-optimizer architecture (arc42 v3.0, 10 sections, 4 diagrams)
- **[docs/MONITORING.md](docs/MONITORING.md)** — monitoring & observability (arc42 Tier-1)
- **[docs/security/THREAT_MODEL.md](docs/security/THREAT_MODEL.md)** — STRIDE threat model
- **[docs/adr/](docs/adr/)** — 13 Architecture Decision Records
- **[STATUS.md](STATUS.md)** — canonical maturity status (single source of truth)

## References

- **Andrej Karpathy — LLM-Wiki pattern** · https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **nvk/llm-wiki — full multi-agent implementation** · https://github.com/nvk/llm-wiki
- **IBM Bob Shell** · https://bob.ibm.com/docs/shell

---

**Author:** David Leconte · **Platform:** IBM Bob Shell · Inspired by Karpathy's LLM-Wiki and nvk's implementation.
