---
title: Engineering-Soundness Audit — Mnemox (frozen evidence snapshot)
category: research
tags: [engineering-soundness, audit, mece, remediation, scorecard, finding-register, mckinsey]
created: 2026-07-19
updated: 2026-07-19
status: active
trust_tier: verified
provenance: Senior engineering-soundness review (McKinsey-style, MECE) synthesising the 2026-07-19 counter-audit (2.9/5) and red-team, cross-checked against the live working tree with file:line verification. This is the FROZEN evidence home for docs/consulting/engineering-soundness-review-2026-07-19.md — it is the single home for the numbers that the living report cites. Quotes RETRACTED figures verbatim for critique only.
---

> **FROZEN SNAPSHOT — quotes RETRACTED / FABRICATED figures for critique.** The "68.96%" and "89.3%" figures named below are WITHDRAWN and are reproduced only to analyse them. Canonical maturity lives in `STATUS.md`; validated savings live in `evaluation/results/validation-2026-07-14/manifest.json`. This directory (`docs/knowledge-base/research/`) is exempt from the savings/status CI gates by design; the head banner is belt-and-suspenders.

# Engineering-Soundness Audit of Mnemox — Evidence Snapshot (2026-07-19)

**Engagement:** Senior engineering-soundness review, McKinsey method (SCQA · MECE · Pyramid · 2×2 · Three-Horizons · value-driver tree · scorecard reconciliation).
**Object:** the live working tree of `bob-llmwiki-knowledge-manager` ("Mnemox") as of 2026-07-19, *including uncommitted changes* — this is what distinguishes it from the 2026-07-19 audit snapshots, which read a committed extract.
**Verdict (one line):** the declared **status** ("Beta — Not Production Ready") is honest; the declared **grade** (self-assessed **A+ 4.30/4.30**) is not yet earned — but the gap is *wiring, integrity repair, and proof*, not new invention. Reconciled engineering-soundness score **~2.9/5 today → ~4.2/5** after Horizons 1–2.

---

## 1. Method & evidence base

Three inputs were triangulated and then **re-verified against the live tree** (citations are current-tree `file:line` unless marked "(audit)"):
- `counter-audit-2026-07-19-independent.md` — independent MECE counter-audit, **2.9/5**, 46 findings (3 Critical, 12 High).
- `docs/knowledge-base/research/adversarial-audit-2026-07-19.md` — red-team, 15+ CONFIRMED live exploits (ATK-* IDs).
- `adversarial-remediation-plan.md` — the v2 technical remediation spec (finding→root-cause→fix→test→gate).

De-duplicated across the three, the register holds **~55 distinct findings**. The load-bearing correction to the audit snapshots: **fixes for the three headline Criticals already exist in the working tree, uncommitted and unproven in CI** (see §4). The audits graded a committed extract that predates this hardening layer.

---

## 2. Reconciled scorecard (single home for the scores)

**Reconciliation thesis:** the self-A+ and the audit-2.9/5 are *both internally coherent because they grade different objects* — the A+ grades **documentation/artifact completeness** (are the SLA, ADRs, CODEOWNERS, mypy scope present?); the 2.9/5 grades **functional integration end-to-end** (does the shipped path do what the artifacts claim?). Mnemox scores high on the first, low on the second. An *engineering-soundness* rubric must weight functional integration, so the defensible grade is the audit's, re-expressed.

All /5 and /4.3 numbers here are **independent engineering-soundness scores, distinct from the STATUS.md institutional grade.**

| Dimension (MECE branch) | Reconciled today | Basis | Post H1+H2 target |
|---|---|---|---|
| A Product correctness | 2.5 / 5 | `optimize()` could return `""` (now fixed-uncommitted); cache mislabel | 4.0 |
| B Memory & retrieval | 2.0 / 5 | flagship stack was unwired; ranking algebra inert; index has no lifecycle | 4.5 |
| C KB integrity & maintenance | 2.5 / 5 | gates could not fail; ~35–40 broken refs; auto-commit of unreviewed writes | 4.0 |
| D Claims, provenance & governance | 3.5 / 5 | best-in-class retraction discipline; but grade self-conferred, gates gameable | 4.5 |
| E Engineering platform | 4.0 / 5 | 11-job CI, SBOM, ~89% coverage; but 2 real failures + uncommitted hardening | 4.5 |
| **Weighted overall** | **~2.9 / 5** | — | **~4.2 / 5** |

**Grade genealogy (for the record):** self-assessed **A+ (4.30/4.30)**; counter-audit **2.9/5**; last independent verdict on file **NO-GO 3.46/4.3 (2026-07-14)**. No independent verdict has been issued *after* the uncommitted hardening — commissioning one is finding CLM-02/R14.

**Mapping to the four watsonx judging axes** (for the pitch adaptation only):

| watsonx axis | Reconciled read | Lever |
|---|---|---|
| Practicality & Coherence | Strong — real SDLC pain, Bob-native | Keep the narrative Bob-centric |
| Effectiveness & Efficiency | Medium — 20% optimizer is real; retrieval value unrealized until wired | Land H1 wiring → realise the memory branch |
| Design & Usability | Medium-strong — two surfaces; lead one demo path | Single golden-path demo |
| Creativity & Innovation | **Strongest** — LLM-Wiki-native memory + honesty brand | Re-grade in public = brand proof |

---

## 3. Validated metrics (single home — cite these, do not re-declare)

**Savings are two independent numbers on two token streams — never one blended figure** (blending is exactly the error that produced the withdrawn 68.96%).

| Metric | Value | Provenance |
|---|---|---|
| Optimizer compression (in-flight prompt) | **20.0% mean**, 95% CI [18.9%, 21.2%]; token-weighted **22.8%**; null test **0.73%** | N=183 real in-repo docs; tiktoken; bootstrap CIs; `evaluation/results/validation-2026-07-14/{report.json,manifest.json}` (manifest-backed) |
| KM re-derivation saving (compact-summary pairs) | **51% mean**, CI [38%, 64%] | N=10 well-formed compact-summary pairs; `tests/validation/test_km_savings.py` |
| KM saving across *all* pairs | **~2%**, CI [−32%, +30%] | reported for honesty — only compact-summaries save; comprehensive docs ≥ source ⇒ zero/negative |
| Compression fidelity | quality **≈ 0.80** | high-fidelity, not lossless |
| Retrieval precision | **p@3 = 0.88** (lab-measured, ADR-017) | **not** re-verified here; no golden set committed (finding CLM-06) — session runs ~0.64 keyword-only until wiring lands |
| Test suite | **1,284 tests collected** (live tree) | up from STATUS.md's 1,112; +~170 from the uncommitted security/gates/retrieval/optimizer/perf suites |
| Coverage | **89.19%** (live `coverage.json`) | STATUS.md cites 89.82% ⇒ drift finding CLM-03; gate floor is ≥80% (`pyproject.toml`) |

**Withdrawn figures (critique only):** "68.96% token savings" and "89.3% / std 0.0" were produced by a simulation that instantiated `PromptOptimizer()` but never invoked it, treated a zero-variance constant as 90 independent samples, used a strawman baseline, and hid a −13093.9% time result. They are retracted and must not reappear un-bannered — yet `docs/knowledge-base/guides/phase6-real-world-validation-plan.md:53` still publishes "Token savings: 68.96%" without a banner (finding CLM-05, a live Wave-0 gate failure).

---

## 4. The three headline Criticals — verified state in the live tree

| Audit claim (committed extract) | Live-tree state | Evidence (verified) |
|---|---|---|
| Retrieval stack never wired; `kb-search` keyword-only (CODE-01/02, MEM-01) | **FIXED — uncommitted** | `#slug` fragment stripped before path-join `src/tools/kb_query.py:327-335`; symlink + `resolve_within` guard `:336-342`; quarantine skip `:349-352`; `kb-search` builds `PersistentEmbeddingIndex`+`GraphStore`, passes `embedding_weight=0.7`/`graph_weight=0.3` `src/cli.py:344-388`; `kb-status` honesty-gated — claims p@3 only when the stack is confirmed active and labels it "per ADR-017, lab-measured, not re-verified" `src/cli.py:512-527`. Test: `tests/retrieval/test_wiring.py`. |
| `optimize()` returns empty string for >4096-token input (CODE-03/07) | **FIXED — uncommitted** | Never-empty post-condition falls back to `Truncator` `src/optimizer/prompt_optimizer.py:242-255`; `truncated` flag `:235-240`. Test: `tests/optimizer/test_optimizer_integrity.py`. |
| `validate-kb.sh` can never fail (subshell counter loss) (MEM-04) | **FIXED — uncommitted** | Process-substitution rewrite; exits 1 on broken links `scripts/validate-kb.sh:162-164`. Test: `tests/gates/test_validate_kb.py`. |

**The dominant near-term risk is therefore not "write the fixes" — it is "commit, wire to CI, and prove RED-on-unfixed / GREEN-on-fixed."** The entire hardening layer (`tests/{security,gates,retrieval,optimizer,performance}/`, `config/gates/`, `scripts/add_trust_tier.py`, the CI wiring in `.github/workflows/ci.yml`) is git-untracked. STATUS.md itself flags this ("untracked and not yet counted").

---

## 5. MECE finding register (~55 findings, single home)

Overlap rule: each defect counted once, at its root cause. **Status:** FIXED-UNC = fix + regression test in working tree, uncommitted · PARTIAL = fix present but incomplete/by-design-limited · OPEN = nothing in tree · ACCEPTED = documented residual.

### Branch A — Product correctness

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| CODE-03/07 | `optimize()` empty output + frontmatter flattening + missing `truncated` flag | Critical | FIXED-UNC | `prompt_optimizer.py:242-255,341-416` | `tests/optimizer/test_optimizer_integrity.py` |
| CODE-08/ATK-FS-02 | L2→L1 promotion caches fuzzy match as forged exact hit | High | FIXED-UNC | `multi_level_cache.py:180-189` | `tests/security/test_cache_integrity.py` |
| ATK-FS-04 | `contains()` ignores TTL (disagrees with `get()`) | Low | FIXED-UNC | `exact_cache.py` | `test_cache_integrity.py` |
| ATK-FS-05 | Shared mutable metadata dict across levels/caller | Low | FIXED-UNC | `exact_cache.py` | `test_cache_integrity.py` |
| CODE-10 | OpenAI-only tokenizer/pricing; silent `chars/4` on watsonx/Claude | Med | OPEN | `src/pricing.py`, `optimizer/token_counter.py` | — |
| CODE-12 | Pervasive silent `except Exception: continue` in KB layer | Med | OPEN | `kb_query.py` (multiple) | ruff rule |

### Branch B — Memory & retrieval architecture

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| CODE-01 | `#slug` doc_ids fail existence check → silent full-scan | Critical | FIXED-UNC | `kb_query.py:327-335` | `tests/retrieval/test_wiring.py` |
| CODE-02/MEM-01 | Index+graph wired into no production path; false p@3 claim | Critical | FIXED-UNC | `cli.py:344-388,512-527` | `test_wiring.py` |
| CODE-05 | Recency weighting numerically inert | High | FIXED-UNC | `kb_query.py` recency | `tests/retrieval/test_ranking_normalization.py` |
| CODE-06 | PageRank blend scale-mismatch (×15 no-op) | High | FIXED-UNC | `graph/ranker.py` | `test_ranking_normalization.py` |
| CODE-04/ATK-DOS-04 | Index rows never deleted; stale vectors match forever; unbounded growth | High | **OPEN** | `embeddings/index.py` (`is_stale` exists `:205`, no reclamation) | new `test_index_lifecycle.py` |
| CODE-11 | No staleness check on the query path | Med | OPEN | `kb_query._query_via_index` | new |
| CODE-15 | Backend/dim switch (1000-d↔384-d) crashes `search()` | Med | OPEN | `embeddings/index.py` matmul | new |
| MEM-06 | Two divergent indexes; graph built from validation-rejected backend | Med | OPEN | `.bob/kb-index` vs `.bob/kb-index-st` | manifest assertion |
| ATK-MEM-03 | Retrieval ranking trivially gamed (keyword-stuffing) | High | PARTIAL | trust-tier + graph mitigate; keyword score still stuffable | extend `test_trust_tier.py` |

### Branch C — KB integrity & maintenance

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| MEM-04 | `validate-kb.sh` never exits non-zero | High | FIXED-UNC | `validate-kb.sh:162-164` | `tests/gates/test_validate_kb.py` |
| MEM-02 | Session auto-load pointer case-broken (`INDEX.md` vs `index.md`) — silent cold-start fail on Linux/CI | High | PARTIAL | `.bob/settings.json`, `.bob/skills/knowledge-manager/SKILL.md` | new pointer test |
| MEM-03/CLM-04 | ~35–40 broken kebab-case refs incl. AGENTS.md, STATUS.md basis links | High | PARTIAL | tracked docs | validate-kb on ubuntu |
| ATK-MEM-04 | Auto-commit propagates unreviewed KB writes team-wide | High | FIXED-UNC | `scripts/mnemox.sh` stage+PR gate | shell/manual |
| ATK-MEM-05 | Graph/index poisoning persists (forged status/edges) | Med | OPEN | `graph/builder.py` | new |
| MEM-05 | Graph broken-edge detection blind to out-of-KB targets | Med | OPEN | `graph/builder.py` | new |
| MEM-07 | Semantic edge density noise-level celebrated as improvement | Med | OPEN | builder threshold | graph-health regression |
| MEM-08 | ~12–13k-token cold start; index double-lists every doc | Med | OPEN | auto-index generator | cold-start metric |
| MEM-10/11/12 | Lessons mtime false deltas; correction loop unverified; marketing filed as knowledge (~65/110) | Low | OPEN | KB curation | — |

### Branch D — Claims, provenance & governance

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| CLM-01 | Tree fails 3 of its own CI gates + 2 test failures | Critical (gov) | **PARTIAL** (live: savings + validate-kb still red) | version aligned `1.1.0`; savings gate red on 5 surfaces; validate-kb red on root hygiene | `tests/gates/test_ci_gate_baseline.py` |
| CLM-02 | A+ self-conferred; only independent artifacts are NO-GO 3.46/4.3 + counter-audit 2.9/5 | Critical (cred) | PARTIAL (disclosed; re-grade OPEN) | `STATUS.md:11` now discloses both | `test_status_gate.py` |
| ATK-GATE-02 | Status validator SKIPs renamed live doc, fails open | High | FIXED-UNC | `check_status_consistency.py` fail-closed | `tests/gates/test_status_gate.py` |
| ATK-GATE-03 | Bare word "manifest" backs a claim ("68.96% (see manifest)") | High | FIXED-UNC | `check_savings_claims.py:81-92` (bare token removed) | `tests/gates/test_savings_gate.py::test_bare_manifest_is_unbacked` |
| ATK-GATE-05 | Gate RED on honest tree (wrapped-citation false positive) | Med | FIXED-UNC | `check_savings_claims.py:199-230` paragraph look-ahead | `test_savings_gate.py` |
| ATK-GATE-06 | Fabricated weighted grade ("A+ 5.00/4.30") unguarded | Med | FIXED-UNC | `check_status_consistency.py::_validate_grade` | `test_status_gate.py` |
| ATK-GATE-01 | No **magnitude / corpus-composition** guard; cherry-pick inflates headline | High | **OPEN by design** | `src/validation/__init__.py:149-151` deliberately does not gate magnitude ("gating a measurement re-incentivises fabrication") | new `test_corpus_integrity.py` |
| ATK-GATE-04 | Blanket-exempt `research/**` + broad banner exception | Med | PARTIAL | `check_savings_claims.py` | savings self-test |
| ATK-GATE-07 | Self-referential gates; single self-owner edits gate + claim in one PR | Med (systemic) | PARTIAL/ACCEPTED | thresholds externalised to `config/gates/gate-config.yaml`; CODEOWNERS routes them — but owner is still solely one person | `tests/gates/test_gate_config.py` |
| ATK-GATE-08 | `coverage.json` trusted standalone; package floor set incomplete | Low | OPEN | `check_coverage_by_package.py` | new |
| CLM-03 | Coverage headline 89.82% vs artifact 89.19% | Med | OPEN | STATUS.md:23 | value-homes |
| CLM-05/08 | 40–75% marketing projections in gate-exempt dirs; nonexistent command refs | Med | OPEN | Recipes/LABs/challenge docs | savings scope-extension |
| CLM-06 | p@3 golden set + scoring script not committed; baseline drift 0.64 vs 0.44 | Med | OPEN | no committed golden set | new `test_p_at_3.py` |
| CLM-07 | Flagship validation run from dirty tree (`git_dirty: true`) | Low | OPEN | manifest provenance | manifest check |
| D4 | Retraction discipline (retract → re-measure → gate) | — | **STRENGTH — keep** | `evaluation/validation-disclaimer.md`, `check_savings_claims.py` | — |

### Branch E — Engineering platform (mostly strengths; enumerated for completeness)

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| CLM-01a | 2 genuine test failures (`tests/test_templates.py`, `tests/test_workflows.py`) | High | OPEN (live) | see Wave 0 | those files |
| SEC-02 | `SECURITY.md` supported-versions table stale vs 1.1.0 | Med | PARTIAL | `SECURITY.md` | value-homes |
| E1–E3 | 11-job CI, SBOM + `pip-audit --strict`, bandit, AST layering gate, per-package coverage floors, path containment, atomic persistence | — | **STRENGTH** | `.github/workflows/ci.yml`, `pyproject.toml`, `src/tools/safe_paths.py` | existing suites |

### Cross-cutting: Security / DoS / Supply-chain

| ID | Title | Sev | Status | Root cause | Test |
|---|---|---|---|---|---|
| ATK-FS-01 | `resolve_within` bypassed on read path; symlink → arbitrary file read | High | FIXED-UNC | guards on every read path `kb_query.py:336-342` (+ list/scan/stats paths) | `tests/security/test_path_containment.py` |
| ATK-MEM-01 | KB content reaches agent context unsanitised (indirect prompt injection) | Critical | FIXED-UNC | boundary markers + exfil flags `kb_query.py:36-64` | `tests/security/test_prompt_injection_boundary.py` |
| ATK-MEM-02 | No trust-tier/provenance; frontmatter forgeable | Critical | FIXED-UNC | trust-tier parser + quarantine `kb_query.py:70-82,349-352`; `scripts/add_trust_tier.py` | `tests/security/test_trust_tier.py` |
| ATK-DOS-01 | PageRank O(n²) dangling loop (~184s @10k) | High | FIXED (verify) | `graph/graph.py` | `tests/performance/test_dos_hardening.py` |
| ATK-DOS-02 | Semantic-graph edge explosion + O(N²) build | High | FIXED-UNC | edge caps `graph/builder.py` | `test_dos_hardening.py` |
| ATK-DOS-03 | L2 O(n) per-miss scan breaks <100ms SLA | Med | FIXED-UNC | BLAS matmul `semantic_cache.py` | `test_dos_hardening.py` |
| ATK-DOS-05/06 | Metrics re-sort under global lock; catastrophic-backtracking regex | Low | OPEN | `metrics.py`, `graph/builder.py` | new/fuzz |
| ATK-SUP-09/SEC-01 | Committed lab credential `MQ_PASSWORD`; enabled preview MCP endpoints | Low (+ops) | FIXED-UNC (+ROTATION owed) | `.bob/mcp.json` placeholder | ci.yml secret-scan |

**Severity rollup:** 3 Critical (CODE-01, CODE-02/MEM-01, CODE-03/07) + 3 governance/cred/security Criticals (ATK-MEM-01, ATK-MEM-02, CLM-01/02) · 12 High · ~20 Med · ~12 Low · plus strengths (D4 retraction discipline, E1–E3 platform).

---

## 6. Value-driver tree — where the savings come from

**Root:** total token/cost reduction per developer session. **Not one multiplied number.** Two independent branches on two token streams:

- **Branch A — In-flight prompt optimisation (TOS), real today.** Driver: compression **20.0% mean** (CI [18.9,21.2], N=183, manifest-backed); sub-drivers whitespace + redundancy + filler; guardrail quality ≈ 0.80; length-weighted 22.8%; null floor 0.73%. **Leak (now fixed-uncommitted):** the `""` bug nullified savings on any >4096-token prompt. Truncation savings reported *separately* (lossy) — never folded in.
- **Branch B — Cross-session re-derivation avoidance (KM), ~0 realised today, high ceiling.** Driver: **51% on N=10 compact-summary pairs**; **~2% across all pairs**. **Key lever = eligibility ratio** (share of retrievals hitting a compact summary): it converts 51%-on-eligible into ~2% overall. **Gating leak:** Branch B was entirely blocked by the unwired stack — keyword-only retrieval at ~0.64 fetched the wrong/no summary, so realised Branch B ≈ 0 until the (now-uncommitted) wiring lands and is proven.
- **Compounding logic:** A and B are **additive on different streams** within a session; **B compounds across sessions** as the corpus and eligibility ratio grow. Honest headline = "A: 20% now; B: 0 now → up to (51% × eligibility) as wiring + corpus mature" — never a single blended percentage.

---

## 7. The one genuinely two-sided design question (ATK-GATE-01)

The red-team calls the absence of a savings-magnitude gate a defect (cherry-picking the corpus can inflate the headline). The code makes the *opposite* argument, in a comment: gating a measurement magnitude "re-incentivises fabrication" (`src/validation/__init__.py:149-151`). **Both are right about different things.** The honest resolution is not to gate the *magnitude* (the code is correct that a magnitude threshold pressures the number) but to gate **corpus composition / representativeness** — a hold-out corpus, per-doc outlier clipping, and a documented corpus-selection rule — so the *denominator* cannot be cherry-picked while the *measurement* stays ungated. This distinction is the recommended Wave-2 decision.

---

## 8. Provenance & limits of this snapshot

- Verified live-tree anchors were read directly (optimizer, cli wiring, kb_query guards, validate-kb, gate internals, magnitude stance). Items marked OPEN/PARTIAL were assessed from the audits plus targeted reads; the full RED→GREEN mutation proof for the FIXED-UNC set is a Wave-1 execution step, not yet discharged here.
- This is a **frozen** artifact dated 2026-07-19. Post-remediation state is recorded separately (remediation log / updated STATUS.md), not by editing this file.
- Scores are engineering-soundness judgements, explicitly distinct from the STATUS.md institutional grade.
