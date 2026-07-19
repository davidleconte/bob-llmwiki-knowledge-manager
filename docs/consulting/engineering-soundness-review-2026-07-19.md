---
title: Mnemox Engineering-Soundness Review
category: consulting
tags: [engineering-soundness, mece, remediation, scorecard, review]
created: 2026-07-19
updated: 2026-07-19
status: active
trust_tier: verified
provenance: Senior engineering-soundness review (McKinsey method). Living narrative; the frozen evidence home is docs/knowledge-base/research/engineering-soundness-audit-2026-07-19.md. Canonical maturity is STATUS.md; validated savings are manifest-backed at evaluation/results/validation-2026-07-14/manifest.json.
---

# Mnemox — Engineering-Soundness Review

**Audience:** the maintainer and any independent reviewer. **Method:** McKinsey (SCQA · MECE · Pyramid Principle · 2×2 · Three-Horizons · value-driver tree · scorecard reconciliation). **Object:** the live working tree as of 2026-07-19, *including uncommitted changes*. **Numbers:** every figure below is cited to its single home — this report does not re-declare canonical values. Full finding register, scorecard math, and verbatim retracted figures live in the [frozen evidence snapshot](../knowledge-base/research/engineering-soundness-audit-2026-07-19.md).

> **Reading guide.** §1 is the whole answer in one page. §2 reconciles the grade dispute. §3–8 walk the five MECE branches. §9–13 are the plan: value drivers, prioritisation, roadmap, validation. §14 explains how this document stays honest under the repo's own CI gates.

> **Remediation status (updated 2026-07-19, branch `remediation/engineering-soundness-2026-07-19`).** **H1 (Reconnect & Repair) is done and committed:** the tree is gate-green (all honesty gates + ruff + mypy); the retrieval wiring, never-empty optimiser, and `validate-kb` fixes are landed — including three *real latent bugs* mypy caught that the paired tests missed (the embedding index was constructed without its `embedder`, so the `TypeError` was swallowed and retrieval silently fell back to keyword-only; the optimiser's never-empty fallback imported a non-existent symbol and would have crashed if triggered); 15 broken KB references repaired; RED→GREEN mutation proofs recorded. **Two governance decisions are implemented:** the self-assessed A+ is **withdrawn** from `STATUS.md` pending an independent re-grade, and a **corpus-composition guard** (ATK-GATE-01 — guards composition, not magnitude) is added to the validation harness with tests. **Still open (H2/H3, genuine multi-week work):** index lifecycle (CODE-04/11/15), graph provenance (ATK-MEM-05/06), a committed p@3 golden set (CLM-06), watsonx-correct tokenizer/pricing (CODE-10), perf-at-scale, gate-owner independence (ATK-GATE-07), and the **independent re-grade itself, which must be performed by a third party** — self-grading is the exact anti-pattern this project exists to avoid.

---

## 1. The answer, first (SCQA)

- **Situation.** Mnemox is a git-native memory layer + token optimiser for IBM Bob, pairing unusually strong epistemic governance — a fabricated headline savings figure that was caught, **retracted**, and re-measured honestly (see the manifest-backed number in §3) — with ~15K LOC of Python, a ~110-doc knowledge base, and a Bash Bob-modes manager. `STATUS.md` declares "Beta — Not Production Ready" with a self-assessed **A+ (4.30/4.30)**.
- **Complication.** Two independent 2026-07-19 audits find the A+ unearned: the validated embedding+graph retrieval stack was never wired into a production path, `optimize()` could silently return an empty string, and the "honesty gates" were gameable. The independent counter-audit scored the committed extract **2.9/5**; the last independent verdict on file is **NO-GO 3.46/4.3 (2026-07-14)**.
- **Question.** Is Mnemox engineering-sound, and what is the shortest credible path to make it so?
- **Answer.** **The status is honest; the grade is not earned yet — but the gap is wiring, integrity repair, and proof, not new invention.** In fact the fixes for all three headline Criticals *already exist in the working tree, uncommitted and unproven in CI.* A disciplined three-horizon programme lifts a defensible engineering-soundness score from **~2.9/5 to ~4.2/5**, and re-grading in public strengthens the honesty brand rather than spending it.

**The single most important fact:** the audits graded a *committed extract*; the live tree already contains the hardening. The near-term job is **commit + prove RED-on-unfixed / GREEN-on-fixed + wire to CI**, not authoring. Evidence: `src/optimizer/prompt_optimizer.py:242-255` (never-empty), `src/cli.py:344-388` (retrieval wired), `scripts/validate-kb.sh:162-164` (gate can now fail) — all git-untracked.

---

## 2. Why "A+" and "2.9/5" are both internally coherent

They grade **different objects**. The A+ grades **documentation/artifact completeness** — are the SLA, ADRs, CODEOWNERS, mypy scope, threat model present? They are. The 2.9/5 grades **functional integration** — does the shipped path do what the artifacts claim? Often, not yet. An engineering-soundness rubric must weight integration, so the defensible grade is the audit's, re-expressed:

| MECE branch | Reconciled today | Post H1+H2 target |
|---|---|---|
| A Product correctness | 2.5 / 5 | 4.0 |
| B Memory & retrieval | 2.0 / 5 | 4.5 |
| C KB integrity | 2.5 / 5 | 4.0 |
| D Claims & governance | 3.5 / 5 | 4.5 |
| E Platform (tests/CI/security) | 4.0 / 5 | 4.5 |
| **Weighted overall** | **~2.9 / 5** | **~4.2 / 5** |

These /5 numbers are **independent engineering-soundness scores, distinct from the STATUS.md institutional grade.** Scorecard math is in the frozen snapshot §2. Recommended governance move: demote the A+ to a dated, clearly-labelled *self-assessment* and let "Beta — Not Production Ready" remain the sole canonical maturity string (it is already pinned as `canonical_status_string` in `config/gates/gate-config.yaml`).

---

## 3. The MECE issue tree

Governing question: **"Is Mnemox engineering-sound, and what will make it so?"** Overlap rule: each defect is counted once, at its root cause.

- **A. Product correctness** — optimiser integrity, truncation invariant, cache correctness, token/pricing fidelity.
- **B. Memory & retrieval architecture** — tier wiring, read-path correctness, ranking algebra, index lifecycle.
- **C. KB integrity & maintenance** — broken pointers/casing, gate efficacy, write discipline, cold-start weight.
- **D. Claims, provenance & governance** — savings-claim integrity, grade genealogy, gate independence, retraction discipline.
- **E. Engineering platform** — tests/coverage, CI depth, security posture, independent verifiability.

**Validated metrics (cited to their single home — the [frozen snapshot §3](../knowledge-base/research/engineering-soundness-audit-2026-07-19.md) and the manifest):** optimiser compression is the **manifest-backed** ~20% figure (95% CI and N in the snapshot; source `evaluation/results/validation-2026-07-14/manifest.json`, null test manifest-backed); the KM re-derivation figures (compact-summary pairs vs all-pairs) are reported honestly in the snapshot with their N; retrieval p@3 is lab-measured per ADR-017 and **not yet manifest-backed** (finding CLM-06). The **retracted/withdrawn** "68.96%" figure is reproduced only in the gate-exempt snapshot, for critique.

---

## 4. Branch A — Product correctness

**Conclusion: was the weakest-per-line branch, now largely repaired in-tree; one open robustness item.** The headline defect — `optimize()` returning an empty string on large inputs — is fixed by a never-empty post-condition that falls back to token-accurate truncation (`src/optimizer/prompt_optimizer.py:242-255`), with a paired regression test (`tests/optimizer/test_optimizer_integrity.py`). The redundancy remover now exempts YAML frontmatter and fenced code so Markdown structure survives compression. The cache correctness defect — a fuzzy L2 hit being promoted to L1 under the caller's key (a forged exact hit) — is fixed by promoting only on an exact-key match (`src/cache/multi_level_cache.py:180-189`). **Open:** OpenAI-only tokenizer/pricing silently falls back to `chars/4` on watsonx/Claude (CODE-10) — a fidelity gap for the target platform, deferred to H3.

---

## 5. Branch B — Memory & retrieval architecture

**Conclusion: the flagship branch; its core defect (an unwired stack) is fixed in-tree, but the index has no lifecycle — the largest genuinely-open surface.** The validated embedding+graph stack is now constructed and injected on the `kb-search` path (`src/cli.py:344-388`, `embedding_weight=0.7`/`graph_weight=0.3`), the read-path `#slug` existence bug is fixed (`src/tools/kb_query.py:327-335`), and `kb-status` no longer over-claims precision — it states p@3 only when the stack is confirmed active and labels it "per ADR-017, lab-measured, not re-verified" (`src/cli.py:512-527`). Ranking algebra (recency and PageRank blend, previously numerically inert) is normalised within the result set (`tests/retrieval/test_ranking_normalization.py`). **Open (H2):** the persistent index never deletes rows on file change/removal, so stale vectors match forever and the store grows unbounded (CODE-04/ATK-DOS-04); no staleness check runs on the query path (CODE-11); a backend/dimension switch crashes `search()` (CODE-15); two divergent index directories coexist (MEM-06).

---

## 6. Branch C — KB integrity & maintenance

**Conclusion: the maintenance ritual runs, but the gate that should catch corruption was previously unable to fail — now fixed, with a residual casing/reference debt.** `validate-kb.sh` is repaired to exit non-zero on broken links (`scripts/validate-kb.sh:162-164`, paired test `tests/gates/test_validate_kb.py`). **Partial/open:** a session-load pointer is case-broken (`INDEX.md` vs the actual `index.md`) which silently fails cold-start on case-sensitive filesystems (Linux/CI) (MEM-02); ~35–40 broken kebab-case cross-references remain across tracked docs (MEM-03); agent-written KB documents were auto-committed without review — now staged behind a review branch + PR (ATK-MEM-04, `scripts/mnemox.sh`). Cold-start context is heavy (~12–13k tokens, every doc double-listed) and warrants a compact auto-index (MEM-08, H2).

---

## 7. Branch D — Claims, provenance & governance

**Conclusion: best-in-class retraction discipline; the remaining gaps are a self-conferred grade and gates that could be gamed — the grade gaps are now gate-enforced in-tree, the re-grade itself is still owed.** Strength to preserve: the retract → re-measure → gate loop (`evaluation/validation-disclaimer.md`, `scripts/check_savings_claims.py`). Fixed in-tree: the savings gate no longer accepts the bare word "manifest" as backing (`scripts/check_savings_claims.py:81-92`), the status gate fails closed on a missing live doc and rejects impossible grades (`scripts/check_status_consistency.py`), each with self-tests in `tests/gates/`. **Open / two-sided:** there is deliberately **no savings-magnitude gate** — the code argues that gating a measurement "re-incentivises fabrication" (`src/validation/__init__.py:149-151`). That is correct about *magnitude*; the honest fix is to guard **corpus composition/representativeness** (a hold-out corpus + outlier clipping + a documented selection rule) so the denominator cannot be cherry-picked while the measurement stays ungated (ATK-GATE-01 — see §12 decision). **Owed:** a genuinely independent re-grade by a third party with no remediation involvement (CLM-02/R14); the A+ vs NO-GO 3.46/4.3 tension is currently *disclosed* in `STATUS.md:11` but not *resolved*.

---

## 8. Branch E — Engineering platform

**Conclusion: the strongest branch; a mature platform undercut only by two live test failures and the fact that the hardening layer is uncommitted.** Strengths: an 11-job CI (ruff, mypy, bandit `-ll`, per-package coverage floors, an AST-based layering gate, a CycloneDX SBOM with a blocking `pip-audit --strict`, and the honesty gates with their own self-tests), atomic persistence, and a single `resolve_within` path-containment primitive reused across every untrusted-path handler. Coverage sits comfortably above the ≥80% gate floor. **Live gaps:** two genuine test failures (`tests/test_templates.py`, `tests/test_workflows.py`) and the fact that the security/gates/retrieval/optimizer/performance suites — and their CI wiring — are still git-untracked, so the newest hardening is not yet counted (this is the Wave-1 job).

---

## 9. Value-driver tree — where savings come from (and why never one number)

Two independent branches on two token streams; blending them is exactly the error that produced the withdrawn figure.

- **Branch A — in-flight prompt optimisation (real today):** the manifest-backed ~20% compression (CI + N in the snapshot), guard-railed at quality ≈ 0.80, reported separately from lossy truncation. Its leak — the `""` bug that nullified savings on large prompts — is now fixed in-tree.
- **Branch B — cross-session re-derivation avoidance (high ceiling, ~0 realised today):** the compact-summary re-derivation saving (see snapshot for the eligible-pair figure and the all-pairs honesty figure). Its lever is the **eligibility ratio** — the share of retrievals that hit a compact summary — and its leak was the unwired stack: keyword-only retrieval fetched the wrong summary, so realised Branch B ≈ 0 until the (now-uncommitted) wiring lands and is proven.
- **Compounding:** A and B are additive on different streams within a session; B compounds *across* sessions as the corpus and eligibility ratio grow. Honest headline: "A now; B → up to (eligible-saving × eligibility) as wiring and corpus mature" — never a single blended percentage.

---

## 10. Finding register (summary)

~55 de-duplicated findings: **6 Critical** (3 product/retrieval + 3 governance/security), **12 High**, ~20 Medium, ~12 Low, plus enumerated strengths. The dominant status is **FIXED-UNCOMMITTED** (fix + regression test present, not committed) for the Critical/High set, with a genuinely-open long tail in index lifecycle, corpus-composition gating, graph provenance, tokenizer fidelity, and gate-owner independence. The full table (ID · severity · status · root-cause `file:line` · test) is the [frozen snapshot §5](../knowledge-base/research/engineering-soundness-audit-2026-07-19.md).

---

## 11. Prioritisation — two 2×2s

**(a) Remediation — Impact × Effort.**
- **High impact / Low effort (do first, H1):** commit + prove the retrieval wiring; the never-empty optimiser; the `#slug` fix; repair `validate-kb.sh`; green the failing gates + version/casing.
- **High impact / High effort (plan, H2):** index lifecycle + dimension enforcement; ranking normalisation hardening; corpus-composition guard; commit the p@3 golden set; commission the independent re-grade.
- **Low impact / Low effort (fill-in):** kebab-case reference sweep; cache `match_type` label; compact cold-start index.
- **Low impact / High effort (defer, H3):** watsonx-correct tokenizer/pricing; multi-user conflict arbitration.

**(b) Risk — Severity × Likelihood.**
- **High / High (mitigate now):** unwired retrieval (fires every query — *fixed-uncommitted, must prove*); empty-optimize on large prompts (*fixed-uncommitted*); `validate-kb.sh` false-green (*fixed-uncommitted*); credibility risk of a reviewer re-deriving A+ vs NO-GO.
- **High / Low:** symlink/path escape (mitigated by `resolve_within`); frontmatter corruption on large `analyze` writes.
- **Low / High:** ~35–40 broken refs; ranking inertness; coverage headline drift.
- **Low / Low:** case-sensitive cold-start (low on macOS dev, higher on Linux CI/prod).

---

## 12. Three-Horizons roadmap

- **H1 — Reconnect & Repair.** Gate-green the tree (Wave 0), repair integrity/casing (Wave R), and **commit + prove** the Critical/High hardening layer with CI wiring (Wave 1). *Exit:* every H1 fix has an adversarial test that is red on the unfixed tree and green on the fixed tree; `kb-status`'s claim becomes true.
- **H2 — Harden & Prove.** Index lifecycle + dimension enforcement; ranking normalisation; **corpus-composition guard** (the ATK-GATE-01 decision); KB write-review gate + per-doc provenance; commit the p@3 golden set as a manifest-backed number; **commission an independent re-grade**.
- **H3 — Scale & Differentiate.** Full write→retrieve→compound loop demonstrated on a foreign repo; watsonx-correct tokenizer/pricing; perf-at-scale; gate-owner independence; KB curation/archive tier.

**Two decisions to make before H2:** (1) **magnitude gate** — recommend guarding corpus *composition*, not the measurement magnitude (§7); (2) **A+ row** — recommend demoting it to a dated self-assessment (§2).

---

## 13. Validation plan

- **Per finding:** record the RED-on-unfixed / GREEN-on-fixed proof (which hunk reverted, which test flipped). The FIXED-UNCOMMITTED set already has paired tests under `tests/{retrieval,optimizer,gates,security,performance}/`.
- **System gates (must pass on the fixed, committed tree):** full `pytest` (ex load/perf) on 3.11+3.12; `--cov=src` ≥ 80% + per-package floors; ruff + mypy + bandit `-ll`; `validate-kb.sh` exits 0 on ubuntu with zero broken non-research links; `python -m src.validation` (null test + manifest completeness + tiktoken active); `pip-audit --strict`; the three honesty gates + their `tests/gates/` self-tests.
- **Retrieval proof:** `bob-optimize kb-search` demonstrably uses the index (wiring test asserts the full-scan path is not taken); p@3 re-measured from a *committed* golden set as a manifest-backed number.
- **Governance close:** the independent re-grade citation replaces the self-A+; `STATUS.md` reconciled (coverage and test-count drift).

---

## 14. Appendix — how this document stays honest under the repo's own gates

This report lives in `docs/consulting/`, which the savings and status gates scan. It therefore follows the "one home per value" discipline: it **cites** canonical numbers rather than re-declaring them, keeps any mention of the withdrawn figure adjacent to a retraction word, references only the ≥80% coverage gate (not a competing coverage number as a live claim), and quotes the self-A+ only *attributed and critiqued*. The full numbers, with their confidence intervals and Ns, live once — in the manifest and the [frozen evidence snapshot](../knowledge-base/research/engineering-soundness-audit-2026-07-19.md). All internal links are kebab-case and resolve.
