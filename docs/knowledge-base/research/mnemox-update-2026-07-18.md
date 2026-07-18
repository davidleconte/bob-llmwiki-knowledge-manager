# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 7 days ago
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
9611585 docs(kb): add quality-gate-status-2026-07-18 + INDEX update
2bcd828 docs(kb): add Round 5 and repo hygiene lessons learned
36b1dbf fix: repo hygiene, cache race Rounds 3-5, portable paths
3676bcb fix: close Round-2 cache thread-safety gaps (N-1 through N-4)
a9ca3ba feat(km): add graph-rebuild step 7 + KM savings measurement suite
73eb8ff feat(p4-final): delegation pipeline, knowledge graph, SLA, gap fixes, KB docs
25cd5d6 docs+fix(p4-st5): ADR-018, architecture, CHANGELOG, STATUS — P4 sign-off
dae3197 feat(p4-st4): recency_weight + date_filter + kb-search CLI (query quality)
d347e79 feat(p4-st3): NodeProps enrichment — mtime_epoch, content_length, description, related_refs
bc966fd test(p4-st2): add TestMiniLMBackend — sentence-transformers fallback wiring (ADR-017 follow-up)
63e9714 fix(p4-st1): AF-3 remove redundant findall guard in _extract_tables, use finditer only
0882653 feat(p3): knowledge graph layer + MiniLM dual-backend + embeddings fixes + docs
949de33 docs: MiniLM backend documentation across README, architecture, ADR-014, security
e5e8fea feat(embed): structure-aware MarkdownChunker + chunk-level doc_ids (step 4)
a3a90d9 feat(embed): optional MiniLM-L6-v2 backend via mlx-embeddings (step 3)
403cf21 perf(embed): raise truncation ceiling 2000→6000 chars (steps 1+2)
a4119ea feat(perf): add production-confidence test suite for M3 Pro / x86 developer hardware
1711000 fix(benchmarks): remove hardcoded timing assertions, raise CI compare threshold to 50%
18618c2 fix(ci): prefix all post-uv-sync commands with `uv run`
83b212a chore(arch-review): Tier-1 architecture review — all 8 sub-tasks closed
0349f95 docs(readme): clarify bob-optimize usage in Bob Shell CLI vs Bob IDE
eac6cfd docs(readme): add §8 TOS examples + renumber downstream sections
994131e docs: README improvements + SVG fix + INTEGRATIONS.md §5 update
d76ee3b fix(claims-gate): add retraction banner to docs-tier2-remediation-plan.md
314b12e chore(root): clean up root — move plan files under docs/, fix .gitignore
297f9e4 chore: add .bob/kb-index/ to .gitignore; remove accidental empty Enter file
833ea2c chore: update pending notes
51bb266 chore(.bob): add Bob workspace config, skills, labs, recipes
e046864 chore: update AGENTS.md, CHANGELOG, README, mode config, test rename
fdcc6f3 docs(p2+a-plus): ADRs 014/015, integration docs, plan closure, STATUS update
46927d8 feat(p2): KB Manager ↔ TOS integration — embeddings package + L3 type-contract fix
5926c25 chore(trivial): D1 slow markers, E1 pip-audit --strict, C1 quality scenarios
91957ca docs(readme): update grade to A (4.09) and add §6 session-activation guide
646269f security(tools): narrow TOCTOU window from 3-step to 2-step in all three tools
c447cec docs(api): regenerate API docs after B1/B2/G1 changes
5e36593 feat(facade): wire MonitoringConfig.log_level and metrics_enabled
7d2070c feat(cache): wire version_support_enabled/max_versions to ExactCache and MultiLevelCache
19c93f5 docs(tier2): full documentation audit — all 170+ files elevated to institutional vendor standard
a585c39 chore(delegation): keep as clean side sub-project
5338150 chore: gitignore .claude/worktrees/ (Bob subagent workspace dirs)
99dfd3a docs: architecture remediation, README replacement, session activation tooling, KB guides
75d05cf docs(audit): correct arch-audit frozen note — ARCHITECTURE.md:74 src/tools/ claim was already fixed
8a901ba docs(security): name TOCTOU check-then-use window as residual 4 in THREAT_MODEL.md
f01aa0f feat(optimizer): wire OptimizerConfig.strategies through from_config() and build_optimizer()
dcb2f5c Fix MultiLevelCache thread-safety race (dict changed size during iteration)
809f8c0 Phase 8: fix M-3 (truncation budget overshoot) + M-2 (gate selftest hygiene)
8cf342b Phase 8: close HIGH-1 (path-traversal leaf leak) + HIGH-2 (live fabrications)
c84b33d Phase 8: remediate sign-off audit blockers (fabrication, coverage, correctness)
f777433 Phase 7: ruff format the two new Phase-7 files
5a8a0bb Phase 7 (F): reconcile live docs to Phases 0-7
6d738d5 Phase 7 (E): security CI gates + governance completeness gate
93169c5 Phase 7 (B): STRIDE threat model; retract fabricated ADR-012
d60f4aa Phase 7 (D): add the community-health set
c21dd76 Phase 7 (C): add SECURITY.md disclosure policy; fix repo URLs
3be8198 Phase 7 (A): contain path traversal in src/tools/ read helpers
9bc3316 docs(AGENTS): mark Phases 0-6 done; Next = Phase 7
cd67b9a Phase 6 (U): README targeted-correctness pass
6bce2b0 Phase 6 (T): Diátaxis navigation spine + the missing Tutorials entry
df8024f Phase 6 (S): one authoritative architecture doc; deprecate the competitors
bba1887 Phase 6 (R): bring the CHANGELOG under Keep-a-Changelog discipline
d99fbdf Phase 6 (Q): regenerate + drift-lock the API reference
dfc914d Phase 6 (P): generic 'one home per value' validator + reconcile drifts
2787f50 Phase 5 (L): run the harness; reconcile live docs to the measured figure
7d0ab11 Phase 5 (M): CI validation job + manifest-backed-savings guard
d0e858b Phase 5 (K): retire the fabricated validator to a thin shim
a2be3eb Phase 5 (J): src/validation/ manifest-backed validation harness
c0f4d05 Phase 4: reconcile live status docs (Phase 4 done)
e5b1b9b Phase 4 (G): unified CLI over the facade (stdlib argparse)
72c29eb Phase 4 (I): wire health checks into the facade; retire the inert drift monitor
ec97e48 Phase 4 (F): composition layer -- factory + TokenOptimizer facade
51ad063 Phase 4 (E): wire config->runtime; flip the 9 config xfails
f64b24f Phase 4 (H): kill src->scripts layering violation (B3) + reconcile delegation docs
56a3c57 Correct coverage snapshot to 82.4% after Phase-3 code changes
7cd248b Phase 3 CI: Python matrix + lint/typecheck/SBOM gates
a8ff72d style: apply ruff format across the codebase
28fdc14 Phase 3 lint: adopt ruff, apply autofixes, fix 2 bugs it surfaced
31a830d Phase 3: single-home deps, 3.11+ matrix, ruff/mypy config + typing baseline
0478cb5 Reconcile status drift + add one-home-per-value CI validator
b917d36 Fix SemanticCache C-5 collision: exact-key fast-path in get()
ee4c1ed CI fixes: declare PyYAML (test dep) + fix stale PromptOptimizer(TokenCounter()) e2e call
4cf4cd3 Phase 2 hardening: property tests, CI, coverage 73→80, + 2 bug fixes
153b0b1 Phase 2 triage: green the test suite (68 failed + 5 errors → 0)
72cbcd3 Phase 2 (config): consolidate split-brain pytest config + coverage gate + timeout (#4)
f81407f Phase 1 (C-9): keep priority truncation in original document order
342b0ab Phase 1 (C-7): make delegation coordinator honor per-task timeouts
8480add Phase 1 (C-5): make semantic-cache embeddings deterministic
7e3839a Phase 1 (C-6): enforce cache TTL on read (was configured but inert)
3ad0478 Phase 1 (C-8): fix always-zero monitoring health check
da6dff1 Phase 1 (C-8b): fix MetricsCollector.get_metrics() self-deadlock
3d2bb6e Phase 1 (C-4): make runtime config.update() atomic
d8bc709 Phase 1 (C-3): enforce truncation token-budget invariant
f496ccc Phase 1 (C-2): single source of truth for pricing
ad02e6f Phase 1 (C-1): fix write-only exact cache in PromptOptimizer
84b98ef Phase 0: institutional audit deliverable + integrity freeze
8027adc Update KB index with institutional evaluation
39f7d97 Add institutional software vendor evaluation
0ec03b4 Add Phase 3 monitoring lessons learned
7e3bc02 Document Phase 3 real-time monitoring implementation
f153b65 Add real-time monitoring and quality validation tools
1fae6a1 Phase 3: Add lessons learned from additional work
44c0173 Phase 3: Add validation testing and Day 7-8 preparation
75cde43 Phase 3: Add comprehensive validation user guide
19f041a Phase 3 Day 3-4: Update KB with parallel work documentation
2698d65 Phase 3 Day 3-4: Add session analysis automation script
4baf128 Phase 3 Day 3-4: Add analysis and reporting tools
5f011cf Phase 3 Day 1-2: Update KB with validation framework docs
30bfff9 Phase 3 Day 1-2: Create validation framework
2f804fa Phase 3: Create real-world validation plan
06a7e0f Phase 2: Update KB index and add lessons learned
239dd34 Phase 2 Complete: Add vocabulary drift monitoring (H-1)
de0e175 docs: Add Phase 1 lessons learned and update KB index
df78ce0 feat: Phase 1 H3-H4 - Configuration Management & Integration Tests
637c4d7 test(delegation): Add comprehensive test suite for delegation module (C-2)
3af589a feat(cache): Add version support to all cache implementations (C-1)
67a15b2 Complete adversarial review and remediation planning
90ac304 Add Phase 6 lessons learned and update knowledge base
8e8177c Complete Phase 6 self-validation with strong results
8fb6429 Implement Phase 6 validation script and run initial test
1c9d66a Add Phase 6 Bob Shell validation approach
0823579 Implement SavingsEstimator class (estimation mode)
9cad04d Add Real-Time Savings Measurement Guide
f009ee8 Add cost tracking comparison analysis
d837ced Update knowledge base INDEX with Phase 5 and Phase 6 documentation
0ac01f9 Add Phase 6: Real-World Validation execution plan
bcde6ee Phase 5: Documentation reconciliation complete
cd2f7a0 docs: Add comprehensive audit remediation status report
28b260a feat: Integrate monitoring (logging + metrics) into all core components
1ced8a0 docs: Document delegation module as experimental and not integrated
3490c82 fix: Skip 6 hanging tests in test_metrics.py for Python 3.14 compatibility
492781f fix: Phase 3 remediation - fix 7 critical bugs
b8788b6 feat: Phase 2 remediation - test & build hygiene
b689cc2 fix: Phase 1 remediation - correct production readiness claims
246052b docs: Add comprehensive audit remediation action plan
f6dad32 docs: Add external audit (2026-07-12) to knowledge base
606e44d docs: Add cost tracking lessons learned to knowledge base
5d88dc1 feat: Complete cost tracking system with KB savings estimation
93cd42b docs: make README quick-start portable across participant machines
a6264cd Update README.md
c998271 docs: credit author and platform explicitly in README
02bb3fa docs: rewrite README as a contextual LLM-Wiki/Bobcoin narrative
9313413 Add complete book on Bob Shell Knowledge Manager
fb80b28 docs: add Knowledge Base Framework design addendum
6c4b7a2 docs: add comprehensive MECE framework and design documentation
093417a docs: add references section with key resource links
3ec0f37 docs: add live example of HCD codebase analysis
4caae36 docs: comprehensive test validation and honest assessment
80015a3 Documentation Reorganization Complete - Logical Directory Structure
4f1c775 Week 18 Days 6-7 Complete - Final Review & Validation
2da3290 Add Week 2 data collection tools and comprehensive guide
380cb14 Update EXECUTION_GUIDE with conda/uv setup instructions
f3ca612 Add comprehensive adversarial review framework
e766bb2 Phase 6: Polish documentation and prepare for release
f376a7b Phase 5: Add comprehensive test suite (45 tests, all passing)
deb519d Complete Phase 4: Example Knowledge Bases
d2ed8e9 Complete Phase 3: Documentation
3c3d143 Complete Phase 2: Automation Scripts
3c88ade Initial commit: Core project structure
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 7 |
| Guides     | 26 |
| References | 2 |
| Research   | 58 |
| **Total**  | **94** |

## New Analysis Reports Filed



## Findings

<!-- MNEMOX_SYNTHESISE: Bob — review the git changes and new analysis reports
above and write 3–5 concrete, specific lessons learned directly into this
section now. Replace this comment with the synthesised content.
Focus on: what changed in the codebase, what patterns emerged, what should
be remembered for the next session. Then update INDEX.md with this note's entry. -->

## Conclusions

### Recommendations
<!-- Bob: add 1–3 actionable next steps based on the findings above -->

### Next Steps
<!-- Bob: add specific tasks for the next session -->

## Related Documents
- [Knowledge Base Index](../INDEX.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
