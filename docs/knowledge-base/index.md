# Knowledge Base Index

> ⚠️ **Metrics correction (2026-07-14).** Earlier drafts cited fabricated figures — "68.96%", "89.3%", "91.80%". **Those are retracted.** The honest, measured figure is **~20% mean optimizer compression** on real prose (manifest-backed: `evaluation/results/validation-2026-07-14/`; see `STATUS.md`).
>
> ⚠️ **Grade correction (2026-07-19).** The self-assessed A+ (4.30/4.30) grade is not independently confirmed. The independent counter-audit (2026-07-19) scored **2.9/5**; the last graded independent verdict is NO-GO at 3.46/4.3 (2026-07-14). `STATUS.md` is the authoritative source.

Last Updated: 2026-07-19 · **115 documents** (14 concepts · 27 guides · 4 references · 69 research · 1 architectural overview)

## Quick Navigation
- [Concepts](./concepts/) - Core concepts and definitions
- [Guides](./guides/) - How-to guides and tutorials
- [References](./references/) - API documentation and specifications
- [Research](./research/) - Research notes and findings

## Recent Additions
- 2026-07-19: [Adversarial Remediation Plan (root)](../../adversarial-remediation-plan.md) - Planning ⭐ NEW — v2 detailed technical specification (14 sub-tasks) for closing all Critical/High audit findings; adversarially audited before implementation; gating independent re-grade
- 2026-07-19: [Obsidian Integration Guide](./guides/obsidian-integration-guide.md) - Guide ⭐ NEW — Semantic graph export to Obsidian Canvas + Dataview, and Obsidian MCP activation in Bob IDE
- 2026-07-19: [Adversarial Audit 2026-07-19](./research/adversarial-audit-2026-07-19.md) - Research ⭐ NEW — Red-team audit: 19 CONFIRMED exploits across file-read, cache-poisoning, prompt-injection, and honesty-gate surfaces
- 2026-07-19: [Independent Counter-Audit](./research/counter-audit-2026-07-19-independent.md) - Research ⭐ NEW — MECE independent counter-audit: 46 findings, scored 2.9/5; retrieval stack unwired, optimizer can return empty, 3 CI gates failing
- 2026-07-19: [Innovation Portfolio](./research/innovation-portfolio-2026-07-19.md) - Research ⭐ NEW — 24-candidate portfolio in 3 horizons: MCP server, cold-start index, Docling bridge, memory-lifecycle intelligence, trust-tiered memory
- 2026-07-19: [Mnemox Update — 2026-07-19 (documentation sync)](./research/mnemox-update-2026-07-19b.md) - Research ⭐ NEW — `mnemox --quick` session lessons: STATUS.md grade qualification, CHANGELOG [Unreleased], INDEX.md case fix, .docx hygiene, remediation-plan root placement
- 2026-07-19: [Mnemox Update — 2026-07-19](./research/mnemox-update-2026-07-19.md) - Research — automated KB update: git log, doc counts, lessons learned scaffold
- 2026-07-18: [Mnemox Challenge Submission](./research/mnemox-challenge-submission-2026-07.md) - Research ⭐ NEW — 2026 IBMer watsonx Challenge submission narrative (Team BobjectifLune)
- 2026-07-18: [Mnemox Executive Brief](./research/mnemox-executive-brief-2026-07.md) - Research ⭐ NEW — 4-minute CTO/challenge-judge decision summary; ROI table; quality gates; pilot design
- 2026-07-18: [Mnemox Competitive Positioning Brief](./research/mnemox-positioning-brief-2026-07.md) - Research ⭐ NEW — Mnemox vs. RAG / vector DB / LangChain / fine-tuning; positioning matrix; data residency
- 2026-07-18: [Mnemox CLI Reference](./references/mnemox-cli-reference.md) - Reference ⭐ NEW — all flags, modes, env vars, auto-detection logic, exit codes, examples
- 2026-07-18: [bob-optimize CLI Reference](./references/bob-optimize-cli-reference.md) - Reference ⭐ NEW — all 13 subcommands with options, defaults, and examples
- 2026-07-18: [Mnemox Update — 2026-07-18](./research/mnemox-update-2026-07-18.md) - Research — automated KB update: git log, doc counts, lessons learned scaffold
- 2026-07-18: [File Naming Conventions](./concepts/file-naming-conventions.md) - Concept ⭐ NEW — kebab-case rule, exclusion zones, `index.md` blast radius, emoji SSoT, drift detection
- 2026-07-18: [Repo Hygiene Rules](./concepts/repo-hygiene-rules.md) - Concept ⭐ NEW — 5 hygiene classes (H-1–H-5), pre-push verification gate, `.gitignore` leading-`/` rule
- 2026-07-18: [Cache Thread-Safety Patterns](./concepts/cache-thread-safety-patterns.md) - Concept ⭐ NEW — 4-tier audit, lock map, GIL limits, snapshot pattern, cross-class accessor pattern
- 2026-07-18: [KB Document Types](./concepts/kb-document-types.md) - Concept ⭐ NEW — compact summary vs comprehensive document, re-derivation saving applicability, compact-summary tag
- 2026-07-18: [Iterative Audit Methodology](./concepts/iterative-audit-methodology.md) - Concept ⭐ NEW — T1–T4 audit tiers, alternative-path anti-pattern, stats() canary, regression test discipline
- 2026-07-18: [Thread-Safe Cost Tracking](./concepts/thread-safe-cost-tracking.md) - Concept ⭐ NEW — opt-in design, RLock pattern, three confidence levels, Bobcoin pricing constant
- 2026-07-18: [Mnemox Update — 2026-07-18](./research/mnemox-update-2026-07-18.md) - Research — kebab rename lessons, emoji SSoT, index.md sweep, test brittleness
- 2026-07-18: [Quality Gate Status — 2026-07-18](./research/quality-gate-status-2026-07-18.md) - Research ⭐ NEW — Status-only audit snapshot: 1112 tests / 0 failures, 89.82% global coverage, all 5 per-package floors met, ruff + mypy clean; script-output hygiene warning; merge checklist
- 2026-07-18: [Repo Hygiene — Lessons Learned](./research/repo-hygiene-lessons-2026-07.md) - Research — 5 hygiene classes (unrelated dirs, root plan files, machine-specific paths, another user's paths, exposed API key); gitignore leading-`/` rule; hygiene audit protocol; portability verification commands
- 2026-07-18: [Cache Thread-Safety Audit — Round 5 Lessons Learned](./research/cache-race-fix-round5-2026-07.md) - Research — 3 new bugs fixed (l3_hits missing from stats, contains() flag-gating, CacheStatsSnapshot); structural enforcement via frozen dataclass; new counter checklist; 1109→1112 tests
- 2026-07-18: [Iterative Audit Methodology — Lessons Learned](./research/iterative-audit-lessons-2026-07.md) - Research — 6 findings on how to audit concurrency code across sessions; 4-tier audit checklist (T1 structural, T2 snapshot, T3 cross-class, T4 alternative paths); race taxonomy table; KB-first compounding; plan-file hygiene
- 2026-07-18: [Cache Thread-Safety Audit — Rounds 1–4 Lessons Learned](./research/cache-race-fix-lessons-2026-07.md) - Research — 14 races total (R-1–R-6, N-1–N-4, O-1–O-2, S-1–S-2); cross-class threshold read; unique_entries stale snapshot; 1109 tests passing
- 2026-07-18: [KB Leveraging Across Mode Switches — Lessons Learned](./research/kb-mode-switch-lessons-2026-07.md) - Research — session analysis: what was leveraged vs missed, 5 findings, AGENTS.md gap root cause, 19-pair corpus anti-pattern, two distinct KB doc roles, 5 recommendations
- 2026-07-18: [KM Bobcoin Savings Measurement Guide](./guides/km-bobcoin-savings-measurement-guide.md) - Guide ⭐ NEW — 7-section practical protocol: baseline session logging, shadow comparison, direct token-diff (bob-optimize / tiktoken), amortised ROI formula, reporting standards, stale-KB diagnosis, automation scripts
- 2026-07-18: [Knowledge Graph Layer](./concepts/knowledge-graph-layer.md) - Concept ⭐ NEW — property graph architecture, 4 modules, NodeProps model, edge types, benefits table (orphan detection, hubs, broken links, PageRank re-ranking)
- 2026-07-18: [Delegation Analysis Pipeline](./concepts/delegation-analysis-pipeline.md) - Concept ⭐ NEW — 6 parallel agents, thin connector pattern, KB-aware execution, token-compressed output, CLI usage
- 2026-07-18: [Knowledge Graph Usage Guide](./guides/knowledge-graph-usage-guide.md) - Guide ⭐ NEW — 5-step workflow: build index → build graph → health report → fix orphans → query; troubleshooting; best practices
- 2026-07-17: [Delegation Pipeline Activation](../adr/019-delegation-pipeline-activation.md) - ADR-019 — delegation module activated as analysis pipeline; `bob-optimize analyze`; coverage floor 52% → 70%; 84% measured
- 2026-07-17: [Knowledge Graph Layer — Live Validation](./research/graph-validation-2026-07-17.md) - Research — P3 graph live validation: 80 nodes, 2876 edges, threshold=0.30 confirmed, graph_weight=0.0 default confirmed, 27/40 orphans rescued by semantic edges
- 2026-07-17: [Adversarial Audit — Embeddings Chunker Integration](./research/adversarial-audit-embeddings-chunker-2026-07-17.md) - Research ⭐ NEW — 2 Critical bugs found and fixed: AF-1 (flush/reload shape mismatch) + AF-2 (is_stale always True); 2 Medium, 2 Low
- 2026-07-16: [KB Query Scorer A/B Validation](./research/kb-query-ab-validation-2026-07.md) - Research ⭐ NEW — embedding-only p@3=0.88 vs keyword p@3=0.64; recommends w=0.7 for KBIndexer
- 2026-07-16: [Multi-Level Caching Architecture Patterns](./concepts/multi-level-caching-architecture-patterns.md) - Concept ⭐ NEW
- 2026-07-14: [KB-TOS Integration Roadmap (P0/P1/P2)](./guides/kb-tos-integration-roadmap.md) - Guide ⭐ NEW
- 2026-07-14: [KB Manager ↔ TOS Integration Feasibility Study](./research/kb-tos-integration-feasibility-2026-07-14.md) - Research ⭐ NEW
- 2026-07-14: [KB-TOS Shared Embedding Layer](./concepts/kb-tos-embedding-layer.md) - Concept ⭐ NEW
- 2026-07-14: [Post-Remediation Full Audit](./research/audit-2026-07-14-post-remediation.md) - Research ⭐ NEW
- 2026-07-14: [Full Codebase & Documentation Review](./research/full-codebase-review-2026-07-14.md) - Research
- 2026-07-14: [Dual System Use Case Example](./guides/dual-system-use-case-example.md) - Guide ⭐ NEW
- 2026-07-14: [Using Both Systems Together](./guides/using-both-systems-together.md) - Guide ⭐ NEW
- 2026-07-14: [Token Optimizer Quick Install](./guides/token-optimizer-quick-install.md) - Guide ⭐ NEW
- 2026-07-14: [Bobcoin Savings Analysis](./research/bobcoin-savings-analysis-2026-07-14.md) - Research ⭐ NEW
- 2026-07-14: [README Critical Analysis](./research/readme-critical-analysis-2026-07-14.md) - Research ⭐ NEW
- 2026-07-14: [Senior Expert Institutional Audit](./research/senior-expert-institutional-audit-2026-07-14.md) - Research ⭐ NEW
- 2026-07-14: [Comprehensive Codebase Analysis](./research/codebase-analysis-2026-07-14.md) - Research ⭐ NEW
- 2026-07-13: [Institutional Software Vendor Evaluation](./research/institutional-vendor-evaluation.md) - Research
- 2026-07-13: [Phase 3 Monitoring Lessons Learned](./research/phase3-monitoring-lessons-learned.md) - Research
- 2026-07-13: [Phase 3 Real-Time Monitoring Implementation](./research/phase3-real-time-monitoring-implementation.md) - Research
- 2026-07-13: [Phase 3 Day 3-4 Parallel Work](./research/phase3-day3-4-parallel-work.md) - Research
- 2026-07-13: [Phase 3 Day 1-2 Validation Framework](./research/phase3-day1-2-validation-framework.md) - Research
- 2026-07-13: [Phase 2 Vocabulary Drift Implementation](./research/phase2-vocabulary-drift-implementation.md) - Research
- 2026-07-13: [Phase 2 Completion Summary](./research/phase2-completion-summary.md) - Research ⭐ NEW
- 2026-07-13: [Phase 2 Health Checks Complete](./research/phase2-health-checks-complete.md) - Research ⭐ NEW
- 2026-07-13: [Phase 2 Thread Safety Fixes Complete](./research/phase2-thread-safety-fixes-complete.md) - Research ⭐ NEW
- 2026-07-13: [Phase 2 Concurrency Test Results](./research/phase2-concurrency-test-results.md) - Research ⭐ NEW
- 2026-07-13: [Phase 2 Performance Baseline Results](./research/phase2-performance-baseline-results.md) - Research
- 2026-07-13: [Phase 2 Performance Baseline Analysis](./research/phase2-performance-baseline-analysis.md) - Research
- 2026-07-13: [Phase 2 Performance Optimization Plan](./guides/phase2-performance-optimization-plan.md) - Guide
- 2026-07-13: [Phase 1 Lessons Learned](./research/phase1-lessons-learned-2026-07-13.md) - Research
- 2026-07-13: [Phase 6 Real-World Validation Plan](./guides/phase6-real-world-validation-plan.md) - Guide ⭐ NEW
- 2026-07-13: [Phase 5 Documentation Reconciliation Complete](./guides/phase5-documentation-reconciliation-complete.md) - Guide ⭐ NEW
- 2026-07-13: [Audit Remediation Status](./guides/audit-remediation-status.md) - Guide ⭐ NEW
- 2026-07-13: [Delegation Integration Analysis](./research/delegation-integration-analysis-2026-07-13.md) - Research ⭐ NEW
- 2026-07-13: [Coverage Measurement 2026-07-13](./research/coverage-measurement-2026-07-13.md) - Research
- 2026-07-13: [External Audit 2026-07-12](./research/external-audit-2026-07-12.md) - Research
- 2026-07-13: [Cost Tracking Lessons Learned](./research/cost-tracking-lessons-learned.md) - Research
- 2026-07-13: [Bob Shell UI Integration](./guides/bob-shell-ui-integration.md) - Guide
- 2026-07-13: [Cost Tracking Guide](./guides/cost-tracking-guide.md) - Guide
- 2026-07-13: [E2E Testing Setup Guide](./guides/e2e-testing-setup-guide.md) - Guide
- 2026-07-13: [Repository Improvement Plan](./research/repository-improvement-plan.md) - Research
- 2026-07-13: [Multi-Level Caching](./concepts/multi-level-caching.md) - Concept
- 2026-07-13: [Token Optimization](./concepts/token-optimization.md) - Concept
- 2026-07-13: [Setting Up Token Optimization System](./guides/setup-token-optimization.md) - Guide
- 2026-07-13: [Cache API Reference](./references/cache-api.md) - Reference
- 2026-07-13: [Performance Benchmarks](./research/performance-benchmarks.md) - Research

## All Documents

### 🏛️ Architectural Overviews
- [Full Technical Design Retro-Engineering — 2026-07](./research/full-technical-design-retro-2026-07.md) - MECE issue tree architecture: §1 Why (4 pain points) → §2 What (6 UCs mapped to pains) → §3 How built (sub-system boundaries) → §4 How each component works → §5 SLA + quality gates → §6 Economic model with causal chain → §7 Open gaps. Adversarial-audited × 2 (13 factual/structural corrections). Load first for any architectural question. ⭐ UPDATED
- [Business Case — 2026-07](./research/business-case-2026-07.md) - For Business Owners, CTOs, and Enterprise Architects: §1 The Problem → §2 The Proposition → §3 The Investment → §4 The Return (ROI model) → §5 The Strategy (compounding thesis) → §6 The Fit (IBM architecture integration) → §7 The Risks → §8 The Decision (pilot design, decision owners, timeline). ⭐ NEW

### Recently Filed (not yet in Recent Additions)
- [Adversarial Review Pattern](./concepts/adversarial-review-pattern.md) - Two-pass hostile + friendly review technique; pre-emption rule; label separation; fabrication ceiling ⭐ NEW

### Planning Artefacts (root-level, outside KB tree)
- [Adversarial Remediation Plan](../../adversarial-remediation-plan.md) — v2 detailed technical specification for closing all Critical/High findings from the 2026-07-19 audits; 14 sub-tasks; adversarially audited before implementation. **The gate document for independent re-grade.** ⭐ NEW

### Concepts
- [File Naming Conventions](./concepts/file-naming-conventions.md) - Kebab-case rule for all `.md` files, exclusion zones, `index.md` blast radius, emoji single source of truth, drift detection command ⭐ NEW
- [Repo Hygiene Rules](./concepts/repo-hygiene-rules.md) - 5 hygiene failure classes (H-1–H-5): unrelated dirs, root plan files, machine-specific paths, cross-user paths, committed secrets; pre-push gate ⭐ NEW
- [Cache Thread-Safety Patterns](./concepts/cache-thread-safety-patterns.md) - 4-tier audit (structural, snapshot, cross-class, alternative paths), lock map for `src/cache/`, GIL limits, snapshot-before-compute pattern ⭐ NEW
- [KB Document Types](./concepts/kb-document-types.md) - Compact summary vs comprehensive document; re-derivation saving applies only to compact summaries; `compact-summary` tag; stale-pair detection ⭐ NEW
- [Iterative Audit Methodology](./concepts/iterative-audit-methodology.md) - T1–T4 audit tiers, `stats()` as canary, alternative-path anti-pattern, regression test discipline, KB compounding within a branch ⭐ NEW
- [Thread-Safe Cost Tracking](./concepts/thread-safe-cost-tracking.md) - Opt-in design, `RLock` pattern, tracking/reporting separation, three confidence levels, Bobcoin pricing constant ⭐ NEW
- [Knowledge Graph Layer](./concepts/knowledge-graph-layer.md) - P3 property graph over KB documents: 4 modules (graph · builder · ranker · store), NodeProps model, explicit + semantic + broken edge types, orphan/hub/broken-link detection, PageRank re-ranking, benefits table
- [Delegation Analysis Pipeline](./concepts/delegation-analysis-pipeline.md) - 6 parallel analysis agents (Security · Performance · Quality · Architecture · Documentation · Research), thin connector pattern, KB-aware execution order, token-compressed output, `bob-optimize analyze` CLI
- [Multi-Level Caching Architecture Patterns](./concepts/multi-level-caching-architecture-patterns.md) - Comprehensive guide to cache hierarchy patterns: L1/L2/L3 organization, eviction policies, distributed caching, with examples from CPU caches to CDN to application caches
- [KB-TOS Shared Embedding Layer](./concepts/kb-tos-embedding-layer.md) - P2 shared infrastructure (`src/embeddings/`): `PersistentEmbeddingIndex`, `FileBackedVectorStore`, `KBIndexer`, persistent disk-backed semantic search for KB Manager and Token Optimizer
- [Multi-Level Caching](./concepts/multi-level-caching.md) - Hierarchical caching strategy combining L1 (exact match) and L2 (semantic similarity) caches with automatic promotion
- [Token Optimization](./concepts/token-optimization.md) - Systematic approach to reducing LLM token consumption through caching, optimization, and truncation
- [Dependency Analysis](./concepts/dependency-analysis.md) - Python dependency inventory with security audit and recommendations for dependency management

### Guides
- [Obsidian Integration Guide](./guides/obsidian-integration-guide.md) - Semantic graph export to Obsidian Canvas + Dataview annotation, and Obsidian MCP activation in Bob IDE ⭐ NEW
- [KM Bobcoin Savings Measurement Guide](./guides/km-bobcoin-savings-measurement-guide.md) - 7-section protocol: baseline sessions, shadow comparison, direct token diff, amortised ROI formula, reporting standards, stale-KB diagnosis, automation ⭐ NEW
- [Knowledge Graph Usage Guide](./guides/knowledge-graph-usage-guide.md) - 5-step workflow: build embedding index → build graph → run health report → fix orphans → query; CLI and Python API; troubleshooting (T1–T4); best practices ⭐ NEW
- [KB-TOS Integration Roadmap (P0/P1/P2)](./guides/kb-tos-integration-roadmap.md) - Grounded P0/P1/P2 integration roadmap; P0 fully closed; P1 and P2 scope intact
- [Dual System Use Case Example](./guides/dual-system-use-case-example.md) - Real-world example: Enterprise AI Assistant Platform for 200-person engineering team, 12-month implementation, 90.3% cost savings (468,000 BC/year), 2,340% ROI, detailed month-by-month breakdown showing KB Manager (78% savings) + Token Optimizer (12% savings) working together
- [Using Both Systems Together](./guides/using-both-systems-together.md) - Comprehensive guide for using Token Optimizer and Knowledge Manager simultaneously: integration patterns, use case analysis, workflow examples, cost-benefit analysis, decision matrix, technical limitations, expected combined savings (60-75% in ideal conditions)
- [Token Optimizer Quick Install](./guides/token-optimizer-quick-install.md) - Fast 5-minute installation and verification guide for Token Optimization System: 3-step install, CLI usage, quick example, troubleshooting, system requirements
- [Real-Time Monitoring Guide](./guides/real-time-monitoring-guide.md) - Complete guide for real-time session monitoring and quality validation during data collection ⭐ NEW
- [Phase 3 Validation User Guide](./guides/phase3-validation-user-guide.md) - Comprehensive guide for collecting baseline and optimized measurements: best practices, query examples, troubleshooting, FAQ, and analysis instructions
- [Phase 3 Validation Testing Plan](./guides/phase3-validation-testing-plan.md) - Comprehensive testing strategy for validation tools: unit tests, integration tests, data validation, performance tests, and quality assurance
- [Phase 3 Day 7-8 Final Validation Template](./guides/phase3-day7-8-final-validation-template.md) - Complete template for final validation report: executive summary, results analysis, statistical significance, production readiness assessment
- [Phase 3 Real-World Validation Plan](./guides/phase3-real-world-validation-plan.md) - Comprehensive 2-3 week plan for real-world validation using Bob Shell, measuring actual token savings and preparing for production deployment
- [Phase 2 Performance Optimization Plan](./guides/phase2-performance-optimization-plan.md) - Complete Phase 2 implementation plan with performance targets, thread-safety, health checks, and vocabulary drift monitoring
- [Audit Remediation Action Plan](./guides/audit-remediation-action-plan.md) - Comprehensive 6-phase plan to address external audit findings with timeline and success criteria
- [Audit Remediation Status](./guides/audit-remediation-status.md) - Current status of audit remediation with Phases 1-4 complete, monitoring integrated, all critical bugs fixed
- [Phase 5 Documentation Reconciliation Complete](./guides/phase5-documentation-reconciliation-complete.md) - Complete report on Phase 5: moved deprecated docs, created UNIFIED_ARCHITECTURE.md, fixed all cross-references
- [Phase 6 Real-World Validation Plan](./guides/phase6-real-world-validation-plan.md) - Comprehensive 10-14 day execution plan for real-world validation with LLM APIs, replacing fabricated metrics with real measurements
- [Phase 6 Bob Shell Validation Approach](./guides/phase6-bob-shell-validation-approach.md) - Updated Phase 6 approach using Bob Shell itself as LLM API, eliminating need for external APIs, 100-200 BC budget, self-validation strategy
- [Phase 6 Lessons Learned](./research/phase6-lessons-learned-2026-07-13.md) - Critical insights from Phase 6 self-validation: 39.3% savings achieved, 76% confidence, self-validation superior to external APIs, budget estimation lessons, optimization patterns discovered
- [Adversarial Review Round 1](./research/adversarial-review-round1-2026-07-13.md) - Hostile critic analysis identifying 47 issues (12 Critical, 18 High, 17 Medium) across security, architecture, performance, testing, and documentation
- [Adversarial Review Round 2](./research/adversarial-review-round2-2026-07-13.md) - Defensive verification challenging Round 1 findings: 31 verified issues, 16 false positives, 12 new issues discovered, revised severity assessments
- [Comprehensive Issue List](./research/comprehensive-issue-list-2026-07-13.md) - Synthesis of both review rounds: 43 verified issues (2 Critical, 19 High, 14 Medium, 8 Low), prioritization matrix, remediation roadmap
- [Detailed Remediation Plan](./guides/remediation-plan-detailed-2026-07-13.md) - Complete technical plan with design, implementation, and validation phases for all 43 issues, 6-9 week timeline, success criteria
- [Real-Time Savings Measurement Guide](./guides/real-time-savings-measurement-guide.md) - Complete guide for measuring actual token savings in real-time, bridging Bob Shell's native tracking with optimization tools using estimation, shadow, and integration modes
- [Bob Shell UI Integration](./guides/bob-shell-ui-integration.md) - UI integration specification for real-time cost tracking indicator in Bob Shell chat interface
- [Cost Tracking Guide](./guides/cost-tracking-guide.md) - Comprehensive guide for Bobcoin cost tracking, budget management, and ROI monitoring
- [E2E Testing Setup Guide](./guides/e2e-testing-setup-guide.md) - Complete guide for setting up and running E2E tests, including common API compatibility issues and troubleshooting
- [Setting Up Token Optimization System](./guides/setup-token-optimization.md) - Complete installation and configuration guide for the Token Optimization System

### References
- [Mnemox CLI Reference](./references/mnemox-cli-reference.md) - All flags, modes, env vars, auto-detection logic, exit codes, examples ⭐ NEW
- [bob-optimize CLI Reference](./references/bob-optimize-cli-reference.md) - All 13 subcommands with options, defaults, and examples ⭐ NEW
- [KB Savings Estimation Methodology](./references/kb-savings-estimation-methodology.md) - Robust methodology for estimating token savings from knowledge base usage with confidence levels
- [Cache API Reference](./references/cache-api.md) - Complete API documentation for all cache classes, methods, and usage examples

### Research
- [Mnemox Update — 2026-07-19 (documentation sync)](./research/mnemox-update-2026-07-19b.md) - `mnemox --quick` session: STATUS.md grade qualification, CHANGELOG [Unreleased], index.md case fix, .docx hygiene, remediation-plan root placement ⭐ NEW
- [Quality Gate Status — 2026-07-18](./research/quality-gate-status-2026-07-18.md) - Status-only audit snapshot: 1112 tests / 0 failures, 89.82% global coverage, all 5 per-package floors met (delegation 84%, embeddings 88.8%, monitoring 97.1%, tools 92%, validation 90.8%), ruff + mypy clean; script-output hygiene warning; merge checklist ⭐ NEW
- [Repo Hygiene — Lessons Learned](./research/repo-hygiene-lessons-2026-07.md) - H-1–H-5 issue taxonomy; gitignore `/`-anchoring rule; hygiene audit protocol (5 shell commands); `.gitignore` design table; verification gate
- [Cache Thread-Safety Audit — Round 5 Lessons Learned](./research/cache-race-fix-round5-2026-07.md) - Round 5 findings: l3_hits missing (5A), contains() flag bug (5B), CONCURRENCY.md (5C), max_size comment (5D), CacheStatsSnapshot structural enforcement (5E); new counter checklist; 1112 tests ⭐ NEW
- [Iterative Audit Methodology — Lessons Learned](./research/iterative-audit-lessons-2026-07.md) - 4-tier audit checklist; 6 process findings; race taxonomy; KB compounding pattern; plan-file hygiene rule; `stats()` as concurrency canary ⭐ NEW
- [Cache Thread-Safety Audit — Rounds 1–4 Lessons Learned](./research/cache-race-fix-lessons-2026-07.md) - 14 races total (R-1–R-6, N-1–N-4, O-1–O-2, S-1–S-2); GIL misconception; lock-order rule; snapshot-before-compute; cross-class lock read; alternative-path stats bypass; 1109 tests
- [KB Leveraging Across Mode Switches — Lessons Learned](./research/kb-mode-switch-lessons-2026-07.md) - Session analysis: KB retrieval vs guidance vs compounding, 5 findings (broken AGENTS.md pointer, cost-tracking miss, mode-reset gap, 19-pair anti-pattern, two KB doc roles), 5 actionable recommendations
- [Knowledge Graph Layer — Live Validation](./research/graph-validation-2026-07-17.md) - P3 graph build on 80-doc corpus: structural metrics, semantic threshold calibration (0.30 confirmed), golden-set p@3 comparison, ADR-017 validation gate results ⭐ NEW
- [KB Manager ↔ TOS Integration Feasibility Study](./research/kb-tos-integration-feasibility-2026-07-14.md) - Architecture study of integrating the KB Manager with the Token Optimization System. Identifies 3 real overlap points, 8 challenges (C1–C8), evaluates 4 integration patterns, applies SOLID principles, and produces a verdict: integrate the embedding layer (P1) now; persistent index (P2) after TOS reaches v1.0.
- [Bobcoin Savings Analysis 2026-07-14](./research/bobcoin-savings-analysis-2026-07-14.md) - Comprehensive analysis of expected Bobcoin savings from both sub-projects: Token Optimizer (~20% measured compression), KB Manager (40-80% structural savings, workload-dependent), combined savings (60-75% in ideal conditions), honest variance reporting, applicability boundaries, and institutional recommendations
- [README Critical Analysis 2026-07-14](./research/readme-critical-analysis-2026-07-14.md) - Institutional perspective on root README.md: 70% alignment with audit findings, identifies 4 critical misalignments (prominent unverified anecdote, inflated maturity grade, outdated bug count, missing production blockers), provides detailed recommendations for institutional adoption
- [Senior Expert Institutional Audit 2026-07-14](./research/senior-expert-institutional-audit-2026-07-14.md) - Expert assessment by Senior Master Principal (LLM-Wiki & Token Management) against Tier 1 institutional standards: C+ grade (2.5/4.0 GPA), 60% production readiness, comprehensive dimension-by-dimension analysis with remediation roadmap
- [Comprehensive Codebase Analysis 2026-07-14](./research/codebase-analysis-2026-07-14.md) - Complete repository analysis: dual system architecture, code quality metrics, testing analysis, documentation assessment, known issues, and production readiness evaluation
- [Institutional Codebase & Documentation Audit 2026-07-13](./research/audit-2026-07-13-institutional.md) - MECE 7-dimension audit against institutional standards: product integrity, architecture, correctness, testing, supply-chain, documentation, governance with weighted D- grade and remediation roadmap
- [Phase 3 Additional Work Lessons Learned](./research/phase3-additional-work-lessons-learned.md) - Lessons from additional work: user guide creation, pragmatic testing approach, template-driven reporting, 6 hours investment, 2,800+ lines delivered
- [Phase 3 Day 3-4 Parallel Work](./research/phase3-day3-4-parallel-work.md) - Analysis & reporting tools: statistical analysis (600+ lines), visualization (530+ lines), automated testing (330+ lines), workflow automation (300+ lines), ready for real-world data
- [Phase 3 Day 1-2 Validation Framework](./research/phase3-day1-2-validation-framework.md) - Complete validation framework implementation: session tracker (18KB), savings measurement demo (14KB), automated scripts, ready for baseline measurements
- [Phase 2 Lessons Learned 2026-07-13](./research/phase2-lessons-learned-2026-07-13.md) - Key lessons from Phase 2 implementation: performance validation, thread-safety, health checks, vocabulary drift, TDD effectiveness, and recommendations for Phase 3
- [Phase 2 Vocabulary Drift Implementation](./research/phase2-vocabulary-drift-implementation.md) - Complete implementation of vocabulary drift monitoring with 22 tests, detecting concept drift in semantic cache
- [Phase 2 Completion Summary](./research/phase2-completion-summary.md) - Phase 2 completion report: 85/85 tests passing, 19-79x performance targets exceeded, all optional items complete
- [Phase 2 Health Checks Complete](./research/phase2-health-checks-complete.md) - Health check system implementation with 29 tests, component and system-level monitoring
- [Phase 2 Thread Safety Fixes Complete](./research/phase2-thread-safety-fixes-complete.md) - Thread-safety implementation fixing 3 critical bugs with RLock, 19 concurrency tests passing
- [Phase 2 Concurrency Test Results](./research/phase2-concurrency-test-results.md) - Comprehensive concurrency testing results revealing and fixing thread-safety issues
- [Phase 2 Performance Baseline Results](./research/phase2-performance-baseline-results.md) - Performance baseline measurements showing 19-79x faster than targets
- [Phase 1 Lessons Learned 2026-07-13](./research/phase1-lessons-learned-2026-07-13.md) - Key lessons from Phase 1 implementation: TDD effectiveness, configuration validation, integration testing, thread safety, versioning complexity, and recommendations for Phase 2
- [Delegation Integration Analysis 2026-07-13](./research/delegation-integration-analysis-2026-07-13.md) - ⚠️ **Superseded by ADR-019** — original analysis concluded "keep as separate system"; delegation module is now integrated as analysis pipeline (see `src/delegation/pipeline.py`, `bob-optimize analyze`)
- [Coverage Measurement 2026-07-13](./research/coverage-measurement-2026-07-13.md) - Real code coverage measurement revealing 49% actual coverage vs claimed 98.4% pass rate, with 28% orphaned code identified
- [External Audit 2026-07-12](./research/external-audit-2026-07-12.md) - Independent external audit identifying critical findings, fabricated metrics, and documentation drift with recommended remediation
- [Cost Tracking Lessons Learned](./research/cost-tracking-lessons-learned.md) - Key lessons learned from implementing the comprehensive Bobcoin cost tracking system with KB savings estimation
- [Performance Benchmarks](./research/performance-benchmarks.md) - Comprehensive performance analysis including latency, throughput, memory usage, and token savings measurements
- [Architecture Audit MECE Framework 2026-07-14](./research/architecture-audit-mece-2026-07-14.md) - MECE framework audit of architecture documentation
- [Phase 8 Audit Sign-off 2026-07-14](./research/audit-2026-07-14-signoff.md) - Final sign-off audit after Phase 8 remediation

### Analysis Snapshots
> Dated snapshots generated automatically by `scripts/run-full-analysis.sh`. Each file represents one analysis run; the most recent supersedes earlier ones. Listed here for completeness — use the latest dated file for current state.

**Repository Scans**
- [Repo Scan 2026-07-18](./research/repo-scan-2026-07-18.md) · [2026-07-13](./research/repo-scan-2026-07-13.md) · [2026-07-12](./research/repo-scan-2026-07-12.md)

**Code Metrics**
- [Code Metrics 2026-07-18](./research/code-metrics-2026-07-18.md) · [2026-07-13](./research/code-metrics-2026-07-13.md) · [2026-07-12](./research/code-metrics-2026-07-12.md)

**Security Scans**
- [Security Scan 2026-07-13](./research/security-scan-2026-07-13.md) · [2026-07-12](./research/security-scan-2026-07-12.md)

**Test Coverage**
- [Test Coverage 2026-07-13](./research/test-coverage-2026-07-13.md) · [2026-07-12](./research/test-coverage-2026-07-12.md)

**Documentation Coverage**
- [Doc Coverage 2026-07-13](./research/doc-coverage-2026-07-13.md) · [2026-07-12](./research/doc-coverage-2026-07-12.md)

**Git Analysis**
- [Git Analysis 2026-07-13](./research/git-analysis-2026-07-13.md) · [2026-07-12](./research/git-analysis-2026-07-12.md)

### Guides (orphan resolution)
- [Activating the Knowledge Manager in a New Session](./guides/activating-knowledge-manager-in-new-session.md) - Workflow for starting a KB session from scratch; CONTEXT.md; start-kb.sh
- [Complete Repository Analysis](./guides/complete-repository-analysis.md) - Full 7-phase analysis guide; what each script produces; how to interpret results
- [P0 Critical Fixes Implementation Guide](./guides/p0-critical-fixes-implementation.md) - Implementation guide for P0 critical fixes

---

## Usage

This knowledge base is managed by Bob Shell in `knowledge-manager` mode.

### Getting Started
```bash
# Start Bob Shell in knowledge-manager mode
bob --chat-mode=knowledge-manager
```

### Common Tasks
- **Research a topic**: "Research [topic] and create a concept document"
- **Create a guide**: "Create a guide for [task]"
- **Find information**: "What do we know about [topic]?"
- **Update document**: "Update [document] with [new information]"
- **Organize**: "Review and organize all [category] documents"

---

*Managed by [Bob Shell Knowledge Manager](https://github.com/davidleconte/bob-llmwiki-knowledge-manager)*
