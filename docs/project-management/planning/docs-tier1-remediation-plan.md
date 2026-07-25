# docs/ Tier-1 Remediation Plan

> ✅ **EXECUTED — closed 2026-07-25.** All seven sub-tasks shipped. Verified
> structurally: every target document now carries mermaid diagrams, a glossary, and
> quality-scenario / risk sections (`docs/MONITORING.md` 5 diagrams,
> `docs/USAGE.md` 6, `docs/WORKFLOWS.md` 5, `docs/INSTALLATION.md` 3,
> `docs/CUSTOMIZATION.md` 2, `docs/quick-start.md` 1). Two caveats stated plainly:
> four of the six lack a *dedicated* `## Constraints` heading (the material appears
> inline), and `docs/quick-start.md` is intentionally lighter than the others because
> it is a 5-minute tutorial, not a reference. Prose quality was **not** re-graded —
> only the structural criteria this plan enumerates were checked.
>
> ⚠️ **This plan's own filename citations are stale** and were never corrected: it
> targets `docs/monitoring.md`, `docs/installation.md`, `docs/usage.md`,
> `docs/customization.md`, `docs/workflows.md` (lowercase) when the tracked files are
> `MONITORING.md`, `INSTALLATION.md`, `USAGE.md`, `CUSTOMIZATION.md`, `WORKFLOWS.md`.
> Its "Already Grade A" list cites `docs/ARCHITECTURE.md` and
> `docs/architecture/architecture.md`, **neither of which exists** — the real file is
> `docs/architecture/ARCHITECTURE.md`. Left as written: this is a frozen planning
> record, and the case bug it exhibits is exactly the tree-wide defect the 2026-07-25
> audit catalogued (~103 broken references), fixed at the source in Wave 2.

**Goal:** Every document in `docs/` at the same Tier-1 institutional level as
`docs/ARCHITECTURE.md` and `docs/architecture/architecture.md` (Grade A).

**Standard:** arc42 / ISO/IEC 42010 · Tier-1 Software Vendor bar.
Each document must have:
- Mermaid diagrams (context, component, sequence, or deployment — appropriate to type)
- Grounding in actual source code or scripts with `path:line` citations
- Constraints section
- Quality scenarios or success criteria
- Risks / known limitations
- Glossary (or pointer to canonical glossary)
- Correct document type framing (not an architecture doc pretending to be a guide)

**Scope:** 7 documents to upgrade. 2 already at grade A are left untouched.

**Already Grade A (no action):**
- `docs/ARCHITECTURE.md` (Bob Shell KB Manager) — A
- `docs/architecture/architecture.md` (Python token-optimizer) — A

**Already Grade A in its domain (no action):**
- `docs/security/threat-model.md` — A (narrow scope by design; exemplary)

**Gates that must stay green after every sub-task:**
- `scripts/check_status_consistency.py`
- `scripts/check_savings_claims.py`
- `scripts/check_value_homes.py`
- `scripts/check_layering.py`
- `scripts/generate_api_docs.py --check`
- `ruff check src/ scripts/ tests/`

---

## Sub-Task 1 — Rewrite `docs/monitoring.md` (B → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 305 lines. Excellent code examples grounded in `src/monitoring/`.
Missing: system context diagram, component diagram of monitoring subsystem,
deployment constraints, ADRs, quality scenarios, glossary, risk register.

**Intent:** Elevate from an operational code-example guide to a Tier-1 monitoring
architecture document that explains *why* the monitoring is designed the way it is,
not just *how* to use it.

**Expected Outcomes:**
- Mermaid component diagram showing the 4 monitoring pillars and their relationships
- Mermaid sequence diagram showing how a `optimize()` call emits metrics + logs
- Context section: what the monitoring system observes, what it does not observe
- Constraints section (no external APM, in-process only, optional psutil)
- ADR section: why structured JSON logging? why in-process metrics vs Prometheus?
- Quality scenarios: latency impact, what triggers a health check failure, log format contract
- Risks & known limitations
- Glossary of monitoring-specific terms

**Todo List:**
1. Read full `docs/monitoring.md` (already done in research)
2. Read `src/monitoring/` directory to understand all 4 components
3. Read `src/monitoring/metrics.py`, `src/monitoring/logger.py`, `src/monitoring/health.py`, `src/monitoring/cost_tracker.py` for accurate citations
4. Write context section: what the monitoring subsystem covers (logger, metrics, health, cost), what it does NOT cover (no APM, no distributed tracing, no alerting)
5. Write Mermaid component diagram of the 4 monitoring pillars + their producers (cache, optimizer, facade, truncator)
6. Write Mermaid sequence diagram: `optimize()` call → logger.info + metrics.record_*
7. Add constraints section: in-process only, psutil optional, no network, no disk persistence
8. Add ADR section: 3 embedded decisions (JSON vs plaintext, in-process vs Prometheus, CostTracker singleton)
9. Keep existing code examples (they are excellent) — do NOT remove them
10. Add quality scenarios: 5 measurable scenarios (log format contract, metrics accuracy, health check coverage, cost tracking precision, latency budget)
11. Add risks: singleton state between tests, no persistence, psutil optional degradation
12. Add glossary: Bobcoin, structured log event, health check, MetricsCollector, CostTracker

**Relevant Context:**
- Current file: `docs/monitoring.md`
- Source: `src/monitoring/` (logger.py, metrics.py, health.py, cost_tracker.py, cost_reporting.py)
- Reference: `docs/architecture/architecture.md §5` (monitoring component description)

---

## Sub-Task 2 — Rewrite `docs/installation.md` (C → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 195 lines. Procedural steps only. No diagrams, no constraints,
no grounding in script logic, no failure modes beyond 3 error messages.

**Intent:** Transform from a recipe guide to a Tier-1 installation document that
documents the installation architecture: what gets copied where, why, what the
pre/post states look like, what can go wrong at each step and why.

**Expected Outcomes:**
- Mermaid sequence diagram of the full `install.sh` execution (matches `scripts/install.sh` actual logic)
- Mermaid sequence diagram of `init-project.sh` execution
- Mermaid state diagram: system states before/after each installation step
- Pre/post conditions at every step (grounded in actual filesystem paths)
- Constraints section: Bob Shell version, Bash version, filesystem permissions
- Failure modes: every `exit 1` in `install.sh` documented with root cause + recovery
- Quality scenarios: 5 verifiable success criteria (file exists, mode activates, etc.)
- Risks: overwrite of existing config, stale backup, Bash 3.2 heredoc `$(date)` bug

**Todo List:**
1. Read `scripts/install.sh` in full (already done in research)
2. Read `scripts/init-project.sh` in full (already done in research)
3. Map every `exit 1` path in both scripts to a documented failure mode
4. Write Mermaid sequence diagram for `install.sh` (exact logic: detect config dir → backup → copy mode → copy settings)
5. Write Mermaid sequence diagram for `init-project.sh` (exact logic: check project → mkdir → write INDEX.md → write settings.json → update .gitignore)
6. Write Mermaid state diagram: 3 system states (Fresh install / Mode installed / KB initialised)
7. Add constraints section: OS, Bash ≥ 3.2, Bob Shell config directory must exist, disk space
8. Document every failure mode with `scripts/install.sh:line` citations
9. Add quality scenarios: 5 verifiable outcomes
10. Add risk register: 4 risks (config overwrite, Bash 3.2 `$(date)` bug, no uninstall script, template path hardcoded)
11. Add glossary: Bob Shell config home, custom mode, knowledge-manager slug, pandoc

**Relevant Context:**
- Current file: `docs/installation.md`
- Source: `scripts/install.sh:1-48`, `scripts/init-project.sh:1-120`
- Known bug: `init-project.sh` INDEX.md heredoc uses `$(date)` inside single quotes — does not expand

---

## Sub-Task 3 — Rewrite `docs/quick-start.md` (C → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 159 lines. Step-by-step recipe. No diagrams, stale reference to
`PHASE3_IMPLEMENTATION_COMPLETE.md` (archived), no grounding in actual script paths.

**Intent:** A Tier-1 quick-start is more than steps — it shows the user the system
in 3 minutes via diagrams, explains what each step achieves architecturally, and
provides verifiable success criteria at every stage.

**Expected Outcomes:**
- Mermaid flowchart: the 3-step onboarding path (install → init → first session) with decision branches
- Mermaid diagram showing what a "ready" state looks like (files in place, mode active)
- Remove stale reference to `PHASE3_IMPLEMENTATION_COMPLETE.md`
- Each step grounded with expected filesystem output or command verification
- Prerequisites section with specific version checks (Bob Shell, Bash)
- "What just happened?" explanation after each step (architectural context)
- 5-minute success criteria checklist (verifiable)
- Troubleshooting section grounded in actual failure modes from scripts

**Todo List:**
1. Remove reference to `PHASE3_IMPLEMENTATION_COMPLETE.md` (archived)
2. Write 3-step flowchart: Install → Init → First Document, with alt paths (already installed, already init'd)
3. Write "ready state" diagram: files that must exist after each step
4. Add "What just happened?" paragraph after each step — architectural context (what was copied where, what changed)
5. Ground all paths in actual script output (use output from `install.sh` and `init-project.sh`)
6. Add prerequisites: Bob Shell ≥ any version with customModes support, Bash ≥ 3.2, Git (optional)
7. Add verifiable 5-minute checklist: 5 assertions user can confirm (mode in mode list, KB dirs exist, INDEX.md present, validate-kb.sh passes, first document created)
8. Add troubleshooting: 5 failure modes grounded in actual script error messages
9. Add "Next steps" with correct links (no dead links)

**Relevant Context:**
- Current file: `docs/quick-start.md`
- Source: `scripts/install.sh`, `scripts/init-project.sh`, `scripts/validate-kb.sh`
- Stale link to remove: `PHASE3_IMPLEMENTATION_COMPLETE.md`

---

## Sub-Task 4 — Rewrite `docs/usage.md` (C → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 485 lines. Most comprehensive operational guide currently. Good
examples. Missing: all diagrams, system context, grounding in actual source, no
quality criteria, no risk register.

**Intent:** Elevate from a recipe guide to a Tier-1 usage reference that explains
the decision model behind every operation (why use concept vs guide, how search
actually works, what `save_memory` does under the hood) with diagrams for all
key workflows.

**Expected Outcomes:**
- Mermaid flowchart: document-type decision tree (concept vs guide vs reference vs research)
- Mermaid sequence diagram: full "create document" path (mode → template → write → memory → index)
- Mermaid sequence diagram: full "search/query" path (search_file_content → memory recall → synthesis)
- Mermaid flowchart: knowledge base maintenance cycle (daily/weekly/monthly)
- Each operation section has: what it does, when to use it, what the outcome is, verification step
- All script commands grounded with expected output
- Quality scenarios: 6 measurable success criteria
- Risk register: 5 operational risks (INDEX.md staleness, memory saturation, naming drift, etc.)
- Glossary of usage-specific terms

**Todo List:**
1. Read current `docs/usage.md` in full (already done in research)
2. Write document-type decision tree flowchart (when concept vs guide vs reference vs research)
3. Write "create document" sequence diagram (full 7-step mode workflow from `custom_modes.yaml:180-203`)
4. Write "query KB" sequence diagram (2-path: memory recall first, then search_file_content)
5. Write maintenance cycle flowchart (daily/weekly/monthly cadences)
6. Add "what it does architecturally" paragraph to each operation section (grounded in mode instructions and Bob Shell built-ins)
7. Add verification step to every operation (how user confirms success)
8. Add quality scenarios: 6 measurable outcomes
9. Add operational risks: INDEX.md staleness, naming convention drift, memory limit, search false-negatives, export format incompatibility
10. Add glossary: Bob mode, search_file_content, save_memory, INDEX.md, cross-reference, knowledge-manager workflow

**Relevant Context:**
- Current file: `docs/usage.md`
- Mode instructions: `config/custom_modes.yaml:180-203` (the 7-step workflow)
- Bob Shell built-ins: `save_memory`, `search_file_content`

---

## Sub-Task 5 — Rewrite `docs/customization.md` (C → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 63 lines. Almost entirely bullet points. No diagrams, no examples,
no grounding in actual YAML structure.

**Intent:** A Tier-1 customization guide shows the extension model: what can be
customized, how the override resolution works (project-level vs global), what
constraints exist, and what risks each customization introduces.

**Expected Outcomes:**
- Mermaid flowchart: configuration resolution chain (project .bob/ overrides ~/.bob/ overrides defaults)
- Annotated YAML example: a real custom mode YAML with every field explained (grounded in `config/custom_modes.yaml`)
- Mermaid flowchart: template customization extension points
- Full "add a new template" tutorial with verifiable steps
- Constraints section: what cannot be customized without breaking the KB contract
- Quality scenarios: 3 verifiable customization outcomes
- Risks: breaking naming conventions, mode collision, template drift from INDEX.md expectations

**Todo List:**
1. Read `config/custom_modes.yaml` in full (already done in research)
2. Write configuration resolution flowchart (project `.bob/custom_modes.yaml` → `~/.bob/custom_modes.yaml` → Bob Shell defaults)
3. Write annotated YAML snippet: every key in the `knowledge-manager` mode entry with inline explanation
4. Write template customization section: how to add a new document type (full tutorial with verifiable steps)
5. Write "add a custom category" section: how to extend beyond the 4 standard categories (mkdir + mode instructions update)
6. Add constraints: KB contract (INDEX.md, 4 dirs) — what scripts assume and will break if violated
7. Add quality scenarios: 3 verifiable outcomes (custom mode activates, new template used by Bob, custom category validated by validate-kb.sh)
8. Add risk register: naming convention drift, mode collision, template that breaks INDEX.md update, category that breaks validate-kb.sh

**Relevant Context:**
- Current file: `docs/customization.md`
- Config: `config/custom_modes.yaml:158-211` (knowledge-manager mode entry)
- Script assumptions: `scripts/validate-kb.sh:20-26` (hardcoded 4 category dirs)
- Templates: `config/templates/`

---

## Sub-Task 6 — Rewrite `docs/workflows.md` (D → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header)

**Current state:** 65 lines of bullet points. No diagrams, no grounding, no
decisions, no quality criteria. Effectively a stub.

**Intent:** A Tier-1 workflows document describes each workflow as a first-class
process: trigger, actors, steps, decision points, success criteria, and what happens
when it goes wrong. With Mermaid flowcharts for each major workflow.

**Expected Outcomes:**
- Mermaid flowchart: "Morning Research Session" workflow end-to-end
- Mermaid flowchart: "New Project Onboarding" workflow
- Mermaid flowchart: "KB Maintenance Cycle" (daily/weekly/monthly with decision gates)
- Mermaid flowchart: "Research Project Documentation" workflow
- Each workflow has: trigger, pre-conditions, steps with Bob commands, success criteria, failure paths
- Anti-patterns section: what NOT to do (e.g., creating documents outside KB Manager mode, skipping INDEX.md update)
- Quality scenarios: verifiable success criteria for each workflow
- Risk register: workflow-level risks (incomplete research session, INDEX.md drift, search false-negatives)

**Todo List:**
1. Read current `docs/workflows.md` in full (already done)
2. Define the 4 primary workflows: Morning Research, New Project Setup, KB Maintenance, Research Documentation
3. Write "Morning Research Session" flowchart (start Bob → research → create doc → save memory → update index → commit)
4. Write "New Project Onboarding" flowchart (init-project.sh → create architecture doc → create setup guide → create API reference → link all)
5. Write "KB Maintenance Cycle" flowchart (daily check → weekly review with link validation → monthly audit with outdated content check)
6. Write "Research Project Documentation" flowchart (define objective → gather sources → document findings → create concept docs → cross-reference → export)
7. Add trigger and pre-conditions to each workflow
8. Add success criteria (verifiable) to each workflow
9. Add failure paths and recovery steps to each workflow
10. Add anti-patterns section: 5 documented anti-patterns with root cause and correct alternative
11. Add risk register: 4 workflow-level risks

**Relevant Context:**
- Current file: `docs/workflows.md`
- Mode instructions: `config/custom_modes.yaml:180-203` (workflow steps)
- Scripts used in workflows: `validate-kb.sh`, `export-kb.sh`
- Examples: `examples/personal-wiki/`, `examples/research-project/`, `examples/software-project/`

---

## Sub-Task 7 — Elevate `docs/monitoring.md` context section to cover both systems (B → A)

**Status:** [x] closed — verified 2026-07-25 (structural criteria met; see header) — depends on Sub-Task 1

**Note:** Included in Sub-Task 1 above (combined).

---

## Post-Completion

After all 6 sub-tasks:
1. Run full gate suite
2. Update `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` with final status
3. Update `arch-doc-remediation-plan.md` with completion note
4. Consider updating overall project grade in `STATUS.md` if documentation dimension closes
