---
title: Integrated McKinsey Engagement — Mnemox Re-Audit After Remediation
category: research
tags: [re-audit, mece, remediation-verification, security, retrieval, governance, master-engagement]
created: 2026-07-20
updated: 2026-07-20
provenance: Independent re-audit (Claude Cowork) of the current tree on branch remediation/wave3-wse-e1-regrade-kit (v1.0-136-g07ad245); prior-finding remediation re-verified by re-running the original exploits against the current code in an isolated sandbox; supersedes nothing — STATUS.md remains canonical
---

# Integrated Engagement — Mnemox, Re-Audited After Remediation

**Engagement type (full scope, single deliverable):** Analysis · Audit · Recommendations · Target Design · Implementation Plan · Validation Plan · Documentation
**Posture:** Independent re-audit. The prior audits' conclusions were treated as *claims to re-test against the current code*, not as settled fact; every "fixed" verdict here was reproduced by re-running the original exploit or check against the present tree.
**Snapshot:** working tree at `v1.0-136-g07ad245`, branch `remediation/wave3-wse-e1-regrade-kit`, ~16,199 LOC (was ~14,550 on 2026-07-19 AM).
**Method note:** this is the second pass of the same engagement. Because the repository changed materially between passes, replaying the first pass would have been inaccurate; instead the first pass's findings became the test plan for this one.

---

## 0. Executive Summary

### 0.1 Governing thought

**The project that was audited this morning no longer exists.** In the interval, the team executed a large, disciplined remediation — and it is real, not cosmetic. Re-running the original exploits against the current code confirms that the three Critical wiring/optimizer defects, the arbitrary-file-read exploit, the retrieval-gaming exploit, both denial-of-service vectors, and the entire integrity-gate perimeter are **genuinely fixed and independently reproduced**. The self-assessed "A+" has been **withdrawn** — the single most important governance act available — and the honesty gates now have planted-defect tests proving they *can* fail. The independent counter-audit score moves from **2.9/5 to a verified ≈3.8/5**. What blocks a higher score, and a GO verdict, is a single coherent pattern: **three of the security fixes were applied to the layer where the defect was *demonstrated* (L1 cache, the signing module) rather than the layer where the attack actually *lands* (the L2 semantic cache, the retrieval trust decision).** Closing that pattern is a days-scale, well-bounded task — and the team's own remediation discipline is exactly the instrument to do it.

### 0.2 Situation — Complication — Question — Answer

**Situation.** Following the 2026-07-19 counter-audit (2.9/5) and adversarial audit (19 confirmed exploits), the team produced an adversarially self-critiqued remediation plan and executed it across several merged waves, adopting a strict "not closed until the regression test is red on the unfixed tree and green on the fixed tree" discipline. The instruction was to re-run the full-scope McKinsey engagement.

**Complication.** A faithful re-run cannot replay the earlier findings — most are now fixed. The honest engagement is a *verification re-audit*: does the remediation actually hold under the original attacks, and what remains?

**Question.** What is the true, current maturity of Mnemox, and what precisely stands between it and a defensible production-readiness verdict?

**Answer.** Maturity has risen substantially and verifiably (≈3.8/5). The remaining gap is narrow and specific: (i) **provenance is not enforced at the retrieval boundary** — a hand-forged `trust_tier: verified` document is still served as trusted because the HMAC signature the team built is never checked on the read path (residual HIGH); (ii) the **L2 semantic cache** still serves a colliding attacker payload, still ignores TTL in `contains()`, and still aliases the caller's metadata dict (three residual MEDIUMs, all fixed correctly in L1 but not L2); and (iii) the remediation introduced **three new minor defects**, chiefly an optimizer cache that ignores the per-call `max_tokens`, so a caller can silently receive an over-budget result. None requires re-architecture; all are addressable within the existing test discipline.

### 0.3 Verified scorecard — morning vs. now

| Dimension (MECE) | 2026-07-19 AM | 2026-07-20 (verified) | Basis for the change |
|---|---|---|---|
| D1 Product correctness (optimizer, cache, truncation) | 2.5 | **3.5** | Optimizer never-empty + structure-preserving (reproduced); truncation sound; residual L2-cache + new optimizer-cache bug hold it below 4 |
| D2 Retrieval & memory architecture | 2.0 | **3.5** | Retrieval genuinely wired (index path used, `#slug` fixed, graph blended); ranking normalized (gaming 18×→1.48×); held below 4 by provenance-not-enforced-on-read |
| D3 KB integrity & maintenance | 2.5 | **3.5** | `validate-kb.sh` fail-closed; 15 broken refs repaired; cold-start bounded; trust tier + quarantine + `kb-promote` added |
| D4 Claims, provenance & governance | 3.5 | **4.5** | A+ withdrawn; magnitude/corpus gate added; savings/status gates hardened; **gate-integrity tests prove gates can fail** |
| D5 Engineering platform | 4.0 | **4.5** | 1,441 passing tests; 90.0% coverage; new security/gates/retrieval/DoS suites; all 8 CI gates green; red/green remediation discipline |
| **Weighted overall** | **2.9** | **≈3.8** | **"Beta — Not Production Ready" still correct; trajectory strongly positive; GO gated on 3 residuals** |

### 0.4 The five things that matter most

1. **The remediation is real and was verified adversarially, not accepted on faith.** Retrieval wiring (CODE-01/02), never-empty optimizer (CODE-03), symlink file-read (ATK-FS-01), ranking gaming (ATK-MEM-03), both DoS vectors (ATK-DOS-01/02), and all integrity gates (MEM-04, ATK-GATE-01/02/03/06, CLM-01) were each re-tested by re-running the original exploit against current code and confirmed fixed.
2. **The governance turnaround is the standout.** Withdrawing the self-assessed A+, adopting the independent audits as STATUS basis, and adding *planted-defect* tests to the honesty gates (a gate that cannot fail is not a gate — now they demonstrably can) is best-in-class integrity behavior.
3. **One residual is HIGH and must gate any trust claim.** The provenance/trust machinery exists and correctly detects forgery *in isolation*, but the retrieval path makes its trust decision on the **plaintext** `trust_tier:` field and never calls `verify_document()`. The signature is decorative at the consumption boundary; a forged `verified` tier is served as trusted.
4. **A single root-cause pattern explains the residuals:** *fix-the-demonstrated-layer, not the vulnerable-layer.* L1 cache received the TTL guard and metadata copy; L2 did not — and L2 is where the collision attack lands. Signing was built; the read path that decides trust does not verify it. Naming the pattern makes the remaining work obvious.
5. **The remediation introduced three new, minor defects** — most notably an optimizer L1 cache keyed on the prompt alone, so a second call with a stricter `max_tokens` returns the earlier uncapped result. Honest re-audits report the regressions the fixes create, not only the defects they close.

---

## 1. Phase 1 — Analysis (current state of the asset)

### 1.1 What changed since the first pass

The tree advanced from `v1.0`+gap-closure to `v1.0-136-g07ad245` across several remediation waves (Wave 0/R/1 engineering-soundness; Waves 2–3 curation, cold-start, external-analysis, re-grade kit). LOC grew ~14,550 → ~16,199, adding four modules that map directly onto the prior recommendations: `src/provenance.py` (HMAC signing, quarantine, attestation), `src/cold_start.py` (bounded, budget-gated KB map), `src/pricing.py` (tokenizer/price separation), and `src/kb_paths.py` (canonical path handling). Five new test packages were added — `tests/security/`, `tests/gates/`, `tests/retrieval/`, `tests/optimizer/test_optimizer_integrity.py`, `tests/performance/test_dos_hardening.py` — that encode the prior findings as regression tests.

### 1.2 Remediation discipline (a first-class finding)

The remediation was governed by an *adversarially self-critiqued* plan (`adversarial-remediation-plan.md`, v2): before implementing, the team audited its own v1 plan against the codebase and caught real errors — including that the v1 plan proposed re-implementing a PageRank fix that *already existed*, and that it had missed the two Critical wiring defects entirely. The operating rule — "a finding is not closed until its adversarial regression test goes red on the unfixed tree and green on the fixed tree" — is precisely the discipline the original audits argued for. This is the behavior that makes the improvement credible rather than asserted.

### 1.3 Current status honesty

`STATUS.md` now reads: overall "Beta — Not Production Ready"; the A+ grade "**withdrawn** — self-grading is not a substitute for independent verification"; on-file independent verdicts cited as counter-audit 2.9/5 and last graded NO-GO 3.46/4.3; an independent re-grade "pending closure of the remaining Critical/High findings." This is accurate and admirably candid. The present re-audit is an input to that pending re-grade.

---

## 2. Phase 2 — Audit (verified findings against current code)

### 2.1 Verified fixed (exploit re-run against current code)

| ID | Prior severity | Verdict | Reproduced evidence |
|---|---|---|---|
| CODE-01 | Critical | **FIXED** | Index path returns chunk-id results; `_query_full_scan` invoked 0×; `#slug` stripped before existence check |
| CODE-02 | Critical | **FIXED** | `kb-search` returns index-sourced chunk IDs and blends graph (`graph_weight=0.3`) |
| CODE-03 / ATK-FS-03 | High | **FIXED** | 5,353-tok doc → non-empty 3,580 tok, headings/fences preserved; `max_tokens=1` → non-empty via truncation |
| ATK-FS-01 | Critical | **FIXED** | Symlink `concepts/*.md → /etc/passwd` skipped; no `root:`/`/bin` content in any result |
| ATK-MEM-01 | High | **FIXED (mitigated)** | Retrieved content wrapped in `<<<KB_REFERENCE_START/END>>>` + exfil `security_flags` + trust withholding (soft boundary) |
| ATK-MEM-03 | High | **FIXED** | Gaming ratio 18× → **1.48×**; BM25 TF saturation (400 occ → 2.49, cap 2.5); heading bonus capped |
| ATK-DOS-01 | High | **FIXED** | PageRank ~1.8×/doubling (linear), dangling mass aggregated O(N) |
| ATK-DOS-02 | High | **FIXED** | 120 mutually-similar docs (7,140 uncapped pairs) → 4,625 ≤ 5,000 cap; explicit `max_total_edges=20` honored |
| MEM-04 | High | **FIXED** | `validate-kb.sh`: clean → exit 0; planted broken link → **exit 1** (subshell counter fixed) |
| MEM-02 / MEM-03 | High | **FIXED** | Casing pointer corrected; 15 broken KB refs repaired |
| ATK-GATE-03 | Med | **FIXED** | `line_is_unbacked_claim("68.96% token savings (see manifest)")` → **True** (bare "manifest" no longer backs a claim) |
| ATK-GATE-01 | Med | **FIXED** | `corpus.py` adds `hash_corpus`/`make_null_corpus`/magnitude constants; `test_corpus_integrity` passes |
| ATK-GATE-02 | Med | **FIXED** | Case-mismatched live doc → **fail-closed exit 1** ("rename must be reflected") |
| ATK-GATE-06 | Med | **FIXED** | Fabricated grade `A+ (5.00/4.30)` flagged; unprovenanced live grade flagged |
| CLM-01 | High | **FIXED** | All 8 `scripts/check_*.py` exit 0; tree coverage **90.01%** |

### 2.2 Residuals (partial fixes — the "wrong-layer" pattern)

| ID | Severity | Verdict | What still fails |
|---|---|---|---|
| ATK-MEM-02 | **High** | **PARTIAL** | HMAC signing/quarantine/`kb-promote` exist and detect forgery, but the **retrieval trust decision reads plaintext `trust_tier:` and never calls `verify_document()`**; a hand-forged `trust_tier: verified` is served as trusted. Attestation is decorative at the consumption boundary. |
| ATK-FS-02 | Medium | **PARTIAL** | L2→L1 promotion poisoning **blocked** (no permanent exact hit), but the 1000-dim hashing collision still lets **L2 serve the attacker payload** for a distinct victim query at cosine 1.0 |
| ATK-FS-04 | Medium | **PARTIAL** | `ExactCache.contains()` now honors TTL; **`SemanticCache`/`MultiLevelCache.contains()` still ignore TTL** (contains=True while get=None after expiry) |
| ATK-FS-05 | Medium | **PARTIAL** | L1 deep-copies metadata; **`SemanticCache.set()` still stores and mutates the caller's dict by reference** |

### 2.3 New defects introduced by the remediation

| ID | Severity | Summary | Location |
|---|---|---|---|
| NEW-1 | **Medium** | `optimize()` L1 cache is keyed on the prompt only; a later call with a stricter `max_tokens` returns the earlier uncapped result (`truncated=None`) — a caller fitting a context window can silently get an over-budget result | `src/optimizer/prompt_optimizer.py` (cache key) |
| NEW-2 | Low | `--date-filter` is inert on the index path: `_query_via_index` sets `file` to `file.md#slug`, so `_doc_date_matches` reads a non-existent path and fails open | `src/tools/kb_query.py` (`_query_via_index`) |
| NEW-3 | Low | Per-node semantic edge cap counts only originated edges; reverse edges added elsewhere are uncounted (node reached 59 vs cap 50) — global cap still bounds totals, so no DoS hole | `src/graph/builder.py` (`build_semantic`) |
| NEW-4 | Cosmetic | `kb-search` on the shipped 115-doc KB reports every doc stale on a clean checkout (mtime-drift sentinels), though retrieval still works | `src/embeddings` staleness check |

### 2.4 Test and gate reality

Full suite (`pytest -m "not slow"`): **1,441 passed / 5 failed / 26 skipped**; all 5 failures are environmental (no `sentence-transformers`, no `.git`, one shared-CPU latency threshold), not remediation regressions. Coverage **90.01%** against the ≥80% gate; per-package floors satisfied. New suites all green: security 40, gates 81, retrieval 14, optimizer-integrity 8, DoS 9. All 8 `check_*.py` gates exit 0, and their `--selftest` modes confirm the gates flag planted violations.

---

## 3. Phase 3 — Recommendations

Prioritized by residual severity × effort. All are days-scale within the existing discipline.

### 3.1 Immediate — close the HIGH residual (1–2 days)

**R1. Enforce provenance at the retrieval boundary (ATK-MEM-02).** Make the trust decision depend on `verify_document()` (HMAC), not on the plaintext `trust_tier:` field: in `KnowledgeBaseQuery`, a document may be treated as `verified` only if its signature validates against the out-of-tree key; an unsigned or signature-mismatched doc is demoted to `generated`/quarantined regardless of what its frontmatter claims. Apply the same check on any cache-promotion path. Adversarial regression: a hand-forged `trust_tier: verified` with no valid signature must be withheld (red on current tree, green after).

### 3.2 Immediate — unify cache semantics across layers (1–2 days)

**R2. Push the L1 fixes down into L2 (ATK-FS-02/04/05).** `SemanticCache.contains()` must apply the TTL check `ExactCache` already has; `SemanticCache.set()` must `dict(metadata)`-copy like `ExactCache`; and the semantic lookup must either verify an exact-prompt hash before serving a similarity hit or raise the hashing dimensionality / switch the default backend so a cosine-1.0 collision between distinct prompts cannot serve one query's answer to another. Regressions: the three L1 tests, re-parameterized against L2.

### 3.3 Near-term — the new defects (0.5–1 day)

**R3. Key the optimizer cache on `(prompt, max_tokens, strategies)` (NEW-1)**, so a stricter budget cannot return a looser cached result; add a post-condition test that a cached result never exceeds the requested cap. **R4.** Carry the real file path (not the chunk id) on the index path so `--date-filter` applies (NEW-2). **R5.** Count reverse edges against the per-node cap or document it as a global-only bound (NEW-3). **R6.** Suppress the clean-checkout staleness warning or ship refreshed sentinels (NEW-4).

### 3.4 Structural — institutionalize the root-cause lesson

**R7. Add a "vulnerable-layer" checklist to the remediation discipline.** For every security fix, require an explicit statement of *the layer the attack lands on* and a regression test at that layer, not merely at the layer where the PoC was first written. This single procedural addition would have caught all four residuals, since each has a passing L1/isolated test masking an unfixed L2/consumption path.

---

## 4. Phase 4 — Target Design

The to-be state is a small delta on the current architecture, not a redesign.

1. **One trust authority at the read boundary.** Retrieval consumes a single `trust(doc)` function whose only trusted input is the verified HMAC signature; `trust_tier:` frontmatter becomes an *unauthenticated hint*, never the decision. Quarantine and promotion consult the same function. This makes the provenance investment load-bearing instead of decorative.
2. **Uniform cache contract.** L1 and L2 implement one `CacheLayer` contract with identical TTL, metadata-ownership, and key-identity semantics, verified by one shared test suite parameterized over both layers — eliminating the class of "fixed in L1, open in L2" residuals by construction.
3. **Collision-resistant semantic keys.** The semantic cache either (a) gates a similarity hit on an exact-content hash match, or (b) uses a higher-dimensional / learned embedding so that distinct prompts cannot collide at threshold — closing ATK-FS-02 at the mechanism level.
4. **Budget-honest optimizer.** Optimizer results are cache-keyed by their full request (prompt + budget + strategies) and carry a truthful `truncated`/`meets_target` contract, so no consumer can receive a silently over-budget result.

---

## 5. Phase 5 — Implementation Plan

| Wave | Scope | Items | Exit criteria |
|---|---|---|---|
| W-A (1–2 days) | Close HIGH | R1 provenance-at-read | Forged-tier test red→green; retrieval trust depends on signature; no plaintext-only trust path remains |
| W-B (1–2 days) | Unify cache | R2 (TTL, metadata copy, collision guard in L2) | L1 cache tests pass when re-run against L2; collision test no longer serves attacker payload |
| W-C (0.5–1 day) | New defects | R3–R6 | Optimizer cache honors budget; date-filter applies on index path; edge-cap semantics documented/enforced; staleness warning corrected |
| W-D (0.5 day) | Discipline | R7 | Remediation template requires a named vulnerable-layer + a test at that layer |
| W-E (in flight) | Independent re-grade | team's E1 kit | Re-grade scores the tree *after* W-A/W-B; target ≥4.0/5 with zero open High |

Sequencing: W-A and W-B are independent and parallelizable; the re-grade (W-E) should run only after both land, so it scores a tree with no open High residual.

---

## 6. Phase 6 — Validation Plan

The team's own rule — red on the unfixed tree, green on the fixed tree — is the validation standard; this plan extends it to the residuals.

1. **Provenance (R1).** Planted forged-`verified` doc (no valid signature) must be withheld from retrieval and from promotion; a correctly-signed doc must pass. Add a "signature stripped" mutation test that must fail if verification is removed.
2. **Cache (R2).** Re-parameterize the three passing L1 tests (`test_cache_integrity`) against L2/`MultiLevelCache`; add a collision test asserting a distinct victim query never receives an attacker-stored value; add a TTL-expiry `contains()==get()` invariant test.
3. **Optimizer budget (R3).** Property test (Hypothesis): for all prompts and all `max_tokens≥1`, a cached-or-fresh result never exceeds the requested cap and reports `truncated` truthfully.
4. **Gate integrity (regression guard).** Keep the planted-defect tests for every honesty gate; add one for the provenance-at-read control so a future refactor cannot silently make trust plaintext-only again.
5. **Independent re-grade.** Run the E1 re-grade kit after W-A/W-B; publish the verdict with the same manifest discipline as the savings figure. This present re-audit's ≈3.8/5 is offered as one independent input, explicitly conditioned on the residuals.

**GO condition:** zero open Critical/High (i.e., ATK-MEM-02 closed), the L2 cache residuals closed or formally risk-accepted with rationale, and an independent re-grade ≥4.0/5 on the post-W-B tree.

---

## 7. Documentation

The documentation set is now strong and mostly self-consistent. Recommended updates: (i) fold the four residuals (ATK-MEM-02, ATK-FS-02/04/05) and the four new defects (NEW-1..4) into `adversarial-remediation-plan.md` as an explicitly-tracked "post-verification residuals" wave, so they are not lost between waves; (ii) adopt the proposed `README.proposed.md` as `README.md` once R1 lands, updating its §9 security-posture note to reflect that provenance is now verified at the read boundary; (iii) record this re-audit as the dated basis alongside the existing 2026-07-19 audits in `STATUS.md`; (iv) when the E1 re-grade completes, replace the "pending" grade line with the independent verdict. The provenance-and-honesty discipline that governs the savings numbers should be extended verbatim to the forthcoming re-grade.

---

## Appendix A — Consolidated verified register (this pass)

**Fixed (15):** CODE-01, CODE-02, CODE-03/ATK-FS-03, ATK-FS-01, ATK-MEM-01 (mitigated), ATK-MEM-03, ATK-DOS-01, ATK-DOS-02, MEM-02, MEM-03, MEM-04, ATK-GATE-01, ATK-GATE-02, ATK-GATE-03, ATK-GATE-06, CLM-01.
**Partial / residual (4):** ATK-MEM-02 (High — provenance not verified at read boundary), ATK-FS-02 (Med — L2 collision serves payload), ATK-FS-04 (Med — L2 `contains()` ignores TTL), ATK-FS-05 (Med — L2 metadata aliasing).
**New defects (4):** NEW-1 (Med — optimizer cache ignores `max_tokens`), NEW-2 (Low — date filter inert on index path), NEW-3 (Low — per-node edge cap counts only originated edges), NEW-4 (Cosmetic — clean-checkout staleness warning).
**Prior finding revised by remediation-plan self-audit:** the morning ATK-DOS-01 "~184s@10k" extrapolation reflected a code path that the team's own plan review found already partly hoisted; current measurement confirms linear scaling — recorded here as fixed, with the original figure noted as superseded.

## Appendix B — Method

Current tree re-staged from the device (branch `remediation/wave3-wse-e1-regrade-kit`) into an isolated sandbox; `pip install -e .[monitoring]` + test tooling; `sentence-transformers`/`torch` deliberately omitted (26 skips + 1 fallback failure attributable, identified). Each prior finding was re-tested by re-running its original exploit or check against the current code; "fixed" is asserted only where the exploit no longer reproduces. Full suite, coverage, all gate scripts, and the five new test packages were executed. Five test failures were confirmed environmental and excluded from findings. Severity reflects impact against a "can write a repo file" access bar.

## Appendix C — Scorecard rationale

D1 3.5: optimizer never-empty verified; truncation sound; held down by NEW-1 and the L2 cache residuals. D2 3.5: retrieval genuinely wired and ranking normalized (large gains); held below 4 by provenance-not-enforced-on-read (a retrieval-trust gap). D3 3.5: integrity gate and cold-start fixes strong; trust tier present but not enforced at consumption. D4 4.5: A+ withdrawal + magnitude/corpus gate + planted-defect gate tests are best-in-class; short of 5 only pending the independent re-grade. D5 4.5: 1,441 tests, 90% coverage, new adversarial suites, disciplined red/green process. Simple mean 3.9; reported as **≈3.8** to weight the open HIGH residual, which a strict institutional bar would treat as capping the security-relevant dimensions until closed.

*Independent re-audit produced by Claude (Cowork). Companion to the 2026-07-19 counter-audit, innovation portfolio, and adversarial audit. STATUS.md remains the single source of truth; this record is an input to the pending independent re-grade.*
