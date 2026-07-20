# Field 2 — Technical Statement
*Paste the text below the line into the form. Remove everything above the line first. Body ≈490 words (limit 500).*

---

**Mnemox** is implemented as **two native IBM Bob modes** — no plugins, no MCP servers, no external dependencies — using Bob's own YAML mode configuration and skill system. One command (`scripts/init-project.sh`) scaffolds the KB and registers the mode in Bob IDE in under 30 seconds; after that, activation is permanent: mode picker → 🧠 Mnemox Knowledge Builder.

**Design pattern — Karpathy's LLM-Wiki, made native to Bob (three layers):**
1. **Knowledge** — version-controlled Markdown under `docs/knowledge-base/` (concepts, guides, references, research), cross-referenced and indexed.
2. **Retrieval** — `INDEX.md` (auto-loaded via `.bob/settings.json`) + `save_memory` facts; a session retrieves prior knowledge instead of re-reading source.
3. **Schema** — the Bob mode definition + `AGENTS.md`: stable rules that make Bob both disciplined and *cacheable* (a fixed prefix hits the cache instead of missing it).

**Why not RAG?** RAG retrieves passages from a snapshot corpus; it doesn't accumulate the reasoning Bob already did. Mnemox stores the *answer* — structured, cross-referenced, curated — and retrieves it directly. No infrastructure beyond Git.

**How Bob was used (native, no external moving parts):**
- Two custom modes — `knowledge-manager` and `repo-analyzer` — defined in `config/custom_modes.yaml` (Bob Shell CLI) and `.bob/custom_modes.yaml` (Bob IDE, zero-install); the skill (`.bob/skills/knowledge-manager/SKILL.md`) auto-loads.
- IBM Bob skills wired in for real workflows: `ibm-watsonx.ai`, `ibm-watsonx-data`, `ibm-docling`, `carbon-mcp`, `techzone`, `draw-io`, plus Bob rules for RAG hygiene, agent safety, containers, and secrets.
- `repo-analyzer` runs 7 Bash scripts (`scripts/run-full-analysis.sh`) producing dated digests — scan, dependencies, metrics, security, coverage, git history, docs — that Bob consumes instead of raw source.
- **This submission was drafted in Bob using Mnemox**; the 110+ document KB was built and maintained by the Knowledge Manager mode itself.

**Why it structurally saves Bobcoins:** native mode (no catalog tax), digests you cite (no payload tax), templates that preserve rationale (no compression trap), persistent KB + `save_memory` (no short-thread tax), fixed schema (cacheable prefix), bounded artifacts (no verbose output).

**Optional Python Token Optimization System** (`src/`, independently operable, exposed via a `TokenOptimizer` facade + `bob-optimize` CLI): L1 exact cache + L2 semantic cache; ≈20% mean compression (whitespace + redundant-phrase removal) at a lexical-overlap quality heuristic of ≈0.80 — *not a semantic-fidelity guarantee*. A knowledge-graph layer was built, measured, showed neutral retrieval uplift, and now ships disabled (`graph_weight = 0.0`), repurposed for KB structural-health analysis. We report that decision rather than omit it. If Python is absent, the Bash KB Manager is unaffected.

**Engineering quality:** CI gates — coverage floor (≥80%), `ruff`, `mypy`, a 3.11/3.12 matrix, SBOM, `bandit`, a `src→scripts` layering gate, benchmark-regression trending; a STRIDE `THREAT_MODEL.md`; a path-traversal regression test.

**Provenance discipline:** every published savings number must cite a reproducible run with a manifest (data hash, code SHA, config, seed, versions, `git_dirty`). Numbers without provenance are not published — and the earlier fabricated figures were formally retracted. We don't self-award readiness grades: the system is labelled **Beta** and every claim is reported at its measured confidence.
