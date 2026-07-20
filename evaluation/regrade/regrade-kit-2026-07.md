---
title: "Independent Re-Grade Kit — 2026-07 (Wave 3 / E1 / R14 / CLM-02)"
status: ACTIVE — kit for handoff to a genuinely independent grader
graded-commit: 6d0711d
verdict-slot: evaluation/regrade/verdict-TEMPLATE.md → verdict-YYYY-MM-DD.md
---

# Independent Re-Grade Kit — 2026-07

This kit exists to discharge **R14 / CLM-02**: every grade increment this project has
recorded (D− → the withdrawn A+) was produced by the *same agentic lineage* that did the
remediation. Self-grading is not independent verification. This kit packages everything a
genuinely independent grader needs — the rubric, the finding register, and the evidence
manifests — so the grade can be re-derived by someone with no stake in the outcome.

> **Built by the remediation lineage; NOT a grade.** Per
> [`wave3-technical-spec-2026-07-19.md`](../../docs/project-management/plans/wave3-technical-spec-2026-07-19.md)
> §E1, a re-grade produced by this session/lineage does **not** discharge R14 (same-lineage
> objection). This kit deliberately states **no grade of its own** — the worksheet cells in
> §4 are empty by design. The C5 grade-provenance gate
> ([`check_status_consistency.py`](../../scripts/check_status_consistency.py)) refuses to let
> any live grade appear in `STATUS.md` until a provenanced `verdict-*.md` exists here.

## 0. The independence rule (who may fill the verdict)

A verdict discharges R14 **only** if produced by one of:

1. a **human third party** with no remediation involvement; or
2. an **external agentic process** with a **distinct model/lineage** and **no remediation
   involvement** — i.e. not this session, not a subagent this session dispatched.

The grader copies [`verdict-TEMPLATE.md`](verdict-TEMPLATE.md) to `verdict-YYYY-MM-DD.md`,
fills every cell, records the `grader:/method:/date:/commit:` provenance block, and commits
it. Only then may `STATUS.md` cite a live grade.

---

## 1. Rubric — the two scorecards (the "dual rubric")

Two complementary lenses. Both scored **/5**. Seed values below are the **most recent
independent scores on file** — they are context for the grader, **not** a pre-filled verdict;
the grader re-scores from scratch in §4.

### 1a. Tier-1 vendor scorecard (/5) — "would a serious engineering org ship this?"

Dimensions are the counter-audit's 5-branch MECE decomposition — the most recent
*independent, numeric* scoring on file
([`counter-audit-2026-07-19-independent.md:48-55`](../../docs/knowledge-base/research/counter-audit-2026-07-19-independent.md)).

| # | Dimension | Last independent score (2026-07-19) |
|---|-----------|:-----------------------------------:|
| D1 | Product correctness (does the optimizer/retriever do what's claimed?) | 2.5 / 5 |
| D2 | Memory & retrieval (embedding+graph wiring, ranking, lift) | 2.0 / 5 |
| D3 | KB integrity (links, pointers, validate-kb, no orphans) | 2.5 / 5 |
| D4 | Claims & governance (honesty gates, provenance, no fabrication) | 3.5 / 5 |
| D5 | Engineering platform (tests, CI, security, structure) | 4.0 / 5 |
| — | **Overall (unweighted mean)** | **2.9 / 5** |

Calibration notes for the grader: the "weighted 2.9/5" label is arithmetically the *unweighted*
mean of the five dimensions ([`adversarial-audit-2026-07-19.md:180`](../../docs/knowledge-base/research/adversarial-audit-2026-07-19.md)).
A hostile re-review judged 2.9 "about right, if a tenth or two too harsh"; nudging D2 (2.0→~2.3)
lifts the overall to ~3.0 (`adversarial-audit-2026-07-19.md:182`).

### 1b. watsonx-jury scorecard (/5) — the four watsonx Challenge judging axes

On file these axes were assessed **qualitatively only** (never numeric —
[`engineering-soundness-audit-2026-07-19.md:52-57`](../../docs/knowledge-base/research/engineering-soundness-audit-2026-07-19.md)).
The grader converts each to /5.

| # | Judging axis | On-file qualitative assessment (2026-07-19) |
|---|--------------|---------------------------------------------|
| J1 | Practicality & Coherence | Strong |
| J2 | Effectiveness & Efficiency | Medium |
| J3 | Design & Usability | Medium-strong |
| J4 | Creativity & Innovation | Strongest |

### 1c. Prior full institutional verdict (context — do NOT copy as a score)

The last *complete* institutional grade was a 7-dimension weighted rubric, verdict
**NO-GO, 3.46/4.30** (2026-07-14,
[`audit-2026-07-14-signoff.md:37-50`](../../docs/knowledge-base/research/audit-2026-07-14-signoff.md)):
A Product Integrity 20% · B Architecture 15% · C Code Correctness 20% · D Testing 15% ·
E Build/Supply 12% · F Docs 10% · G Governance 8% (letters B / A− / A− / B / A− / A− / A−).
Recorded so this kit reconciles with both numbers `STATUS.md` cites (2.9/5 and NO-GO 3.46/4.30).
The self-assessed A+ is **withdrawn** and appears here only as retracted history.

---

## 2. Finding register (Critical / High + disposition)

**Disposition is as of graded commit `6d0711d`** (after all twelve Wave-3 PRs, #26–#36,
merged). The counter-audit filed **46 findings — 3 Critical, 12 High, 14 Medium, 12 Low,
5 Info** (`counter-audit-2026-07-19-independent.md:38`); the engineering-soundness pass
reconciled ~55 with 6 Critical / 12 High. The Critical + material High set:

### Critical

| ID | Finding | Disposition @ 6d0711d | Cite |
|----|---------|----------------------|------|
| CODE-01 | `#slug` doc_ids fail existence check → silent keyword-only full-scan | **Closed (W1)** | `src/tools/kb_query.py:327-335`; `tests/retrieval/test_wiring.py` |
| CODE-02 / MEM-01 | Embedding index + graph wired into no production path; false p@3=0.88 | **Closed (W1)** | `src/cli.py:344-388,512-527` |
| CODE-03 / 07 | `optimize()` returns "" for >4096 tok; frontmatter flattening | **Closed (W1)** | `src/optimizer/prompt_optimizer.py:242-255`; `test_optimizer_integrity.py` |
| CLM-01 | Tree fails ≥3 of its own CI gates (savings, validate-kb) | **Closed** — all honesty gates + validate-kb green @ 6d0711d (verified for this kit) | this kit §5; `scripts/check_*.py` |
| CLM-02 | A+ self-conferred; only independent artifacts are NO-GO 3.46/4.30 + 2.9/5 | **OPEN — this kit discharges it** | `STATUS.md:11`; E1/R14 |

### High (material subset, with disposition)

| ID | Finding | Disposition @ 6d0711d | Cite |
|----|---------|----------------------|------|
| ATK-DOS-01 | PageRank dangling-node O(n²) (~184s @10k) — was mis-marked "fixed" | **Closed (Wave-3 A1)** — O(N); mixed-dangling test | `src/graph/graph.py`; `tests/performance/test_dos_hardening.py` |
| CODE-04 / ATK-DOS-04 | Index rows never reclaimed; O(N²) `np.vstack` rebuild residual | **Closed (Wave-3 A3ii)** — batched rebuild | `src/**/index.py`; WS-A tests |
| CODE-05 | Recency weighting numerically inert | **Closed (W1)** | `test_ranking_normalization.py` |
| CODE-06 | PageRank blend scale-mismatch (×15 no-op) | **Closed (W1)** | `tests/retrieval/` |
| CODE-08 / ATK-FS-02 | L2→L1 promotion caches fuzzy match as forged exact hit | **Closed (W1)** | `src/cache/multi_level_cache.py:180-189`; `tests/security/test_cache_integrity.py` |
| CODE-10 | watsonx tokenizer/pricing dishonesty (economics) | **Closed (Wave-3 B1–B4)** | `src/optimizer/token_counter.py`; WS-B tests |
| MEM-04 | `validate-kb.sh` never exits non-zero (subshell counter loss) | **Closed (W1)** | `scripts/validate-kb.sh:161-164`; `test_validate_kb.py` |
| ATK-FS-01 | Arbitrary file read via symlink escape (`/etc/passwd`) | **Closed (W1 + Wave-3 D3)** — path containment, rebased not relaxed | `tests/security/`; PR #33 |
| ATK-GATE-02 | Status validator SKIPs renamed live doc, fails open | **Closed (W1)** — fail-closed | `check_status_consistency.py:377-383` |
| ATK-GATE-03 | Bare word "manifest" backs a savings claim | **Closed (W1)** | `scripts/check_savings_claims.py:81-92` |
| ATK-MEM-04 | Auto-commit propagates unreviewed KB writes team-wide | **Closed (W1)** — stage+PR gate | `scripts/mnemox.sh` |
| ATK-GATE-01 | No magnitude/composition ceiling; cherry-pick inflates headline +54% | **Accepted-by-design + Wave-3 C4** — held-out reproduction gate; no magnitude ceiling (composition guard only), by design | PR #29; `evaluation/holdout/` |
| ATK-GATE-07 | Self-referential gates; one owner edits gate + claim in one PR | **Accepted (residual, disclosed) + Wave-3 C3** — structural gate-integrity check | PR #28; `wave3-…-spec:693-697` |
| ATK-MEM-03 | Retrieval ranking gameable (~18× via keyword-stuffing) | **Partial** — trust-tier + graph mitigate; keyword score still stuffable | `tests/security/`; grader: verify |
| MEM-02 / MEM-03 | Pointer case (`INDEX.md`), ~35 broken kebab-case refs | **Partial** — 15 repaired W1; validate-kb green @ 6d0711d | `STATUS.md:12` |
| ATK-SUP-09 / SEC-01 | Committed lab credential (`MQ_PASSWORD=passw0rd`) | **Absent in code/config @ 6d0711d** (docs-only at most); grader: verify | grep @ 6d0711d |

**Honest summary for the grader.** As of `6d0711d`, every Critical/High above is **Closed** or
**explicitly Accepted-by-design (with dated rationale)** — *except* **CLM-02**, the same-lineage
grade objection, which this kit exists to discharge, plus two **Partials** (ATK-MEM-03 keyword
stuffing; MEM-02/03 residual refs) that are flagged for independent verification, not asserted
closed. This register is a **claim surface to be falsified**, not a certificate: re-verify the
"Closed" rows against the cited tests before accepting them. The full 46/55-finding lists live at
`counter-audit-2026-07-19-independent.md:95-152` and `engineering-soundness-audit-2026-07-19.md:95-152`.
The consolidated Wave-3 finding→commit map (E2, `wave3-status.md`) is the remaining exit
deliverable and is not yet built.

---

## 3. Evidence manifests (re-runnable — the grader should re-run these)

Both manifests carry `git_dirty: true` — they were generated on a working tree with
uncommitted changes. That is a provenance caveat the grader should weigh: the metrics are
reproducible from the cited `code_sha`, but the exact tree state was not clean at capture.

### 3a. Validation manifest — `evaluation/results/validation-2026-07-14/manifest.json`

- **Headline:** optimizer compression **mean savings 20.01 %** (95 % CI **[18.91, 21.16]**),
  **n = 183**, `tiktoken_active = true`. Token-weighted aggregate 22.78 %. Cache
  recompute-avoidance (32.18 %) is reported **separately, excluded from the headline**.
- **Null test:** shuffled-control aggregate **0.728 %** (threshold 5 %) → **PASS** — the 20 %
  is not an artifact of the measurement.
- **Provenance:** `code_sha 47961436f30e0b4d6cdeeded9ec130af6fc7f863` · `data_hash c4ae956b…981bf8`
  · `seed 0` · `git_dirty true` · `model gpt-4` · tiktoken 0.13.0 / numpy 2.5.1 / scikit-learn 1.9.0
  · py 3.12.10 · n_docs 183 · 2026-07-14T13:12:02Z.

### 3b. Retrieval manifest — `evaluation/results/retrieval-2026-07-19/manifest.json`

- **Headline (the honest one):** `p_at_3_wired = 0.84` **and** `p_at_3_keyword_baseline = 0.84`
  (hits 21/21, **n_queries = 25**, k = 3) → **p@3 = 0.84 with NO net lift over keyword-only**.
  The higher **0.88** figure is an *unreached* MiniLM/sentence-transformers config, not the shipped
  hashing backend (finding CLM-06; see [`docs/adr/017-knowledge-graph-layer.md:11-12`](../../docs/adr/017-knowledge-graph-layer.md)).
- **Provenance:** `code_sha 4fe2a0b1781eb3e15dee841da2a640749d7a97e9` · `data_hash a15e0b6d8fbd12b3`
  · `seed 0` · `git_dirty true` · config `embedding_weight=0.7, graph_weight=0.3, backend=hashing, k=3`
  · `tiktoken_active false` · `model hashing-embeddings` · corpus `docs/knowledge-base`, n_queries 25,
  n_docs 116 · 2026-07-19T16:10:17Z.

### 3c. Supporting evidence

- **Golden set:** [`evaluation/data/retrieval_golden_set.json`](../data/retrieval_golden_set.json)
  — 25 queries, k=3, `{query, expected, expected_doc_id}` (R13; committed in W2, unblocked R14).
- **Held-out slice:** [`evaluation/holdout/holdout-manifest.json`](../holdout/holdout-manifest.json)
  — frozen i.i.d. hold-out (rule `sha256(path) % 100 < 15`), **n = 35**, frozen 2026-07-19 for the
  C4 magnitude/composition defense. Discipline note in-manifest: "do not add/remove paths to move a number."

---

## 4. Grader worksheet (empty — the independent grader fills this)

Score each dimension **/5** with a one-line evidence citation. **These cells are intentionally
blank; do not treat §1's seed values as pre-filled.** When done, transcribe into
`verdict-YYYY-MM-DD.md`.

### 4a. Tier-1 vendor worksheet

| Dimension | Score /5 | Evidence / `path:line` or manifest |
|-----------|:--------:|------------------------------------|
| D1 Product correctness |  |  |
| D2 Memory & retrieval |  |  |
| D3 KB integrity |  |  |
| D4 Claims & governance |  |  |
| D5 Engineering platform |  |  |
| **Overall (mean)** |  |  |

### 4b. watsonx-jury worksheet

| Judging axis | Score /5 | Evidence / `path:line` or manifest |
|--------------|:--------:|------------------------------------|
| J1 Practicality & Coherence |  |  |
| J2 Effectiveness & Efficiency |  |  |
| J3 Design & Usability |  |  |
| J4 Creativity & Innovation |  |  |
| **Overall (mean)** |  |  |

### 4c. Provenance block (required — the C5 gate keys on `grader:` + this artifact path)

```
grader:                  <name / panel / external-agent identity>
method:                  <how scored — e.g. read kit + re-ran both manifests>
date:                    <YYYY-MM-DD>
commit:                  6d0711d      # or the commit actually graded
remediation-involvement: none         # MUST be none to discharge R14
model-lineage:           <if agentic: model + confirmation distinct from the remediation lineage>
```

---

## 5. How to submit the verdict

1. Confirm the live tree is gate-green at the graded commit. As of `6d0711d`, the honesty gates
   `check_status_consistency`, `check_savings_claims`, `check_value_homes` and `validate-kb`
   all pass (re-run them; they are the CLM-01 closure evidence).
2. Copy [`verdict-TEMPLATE.md`](verdict-TEMPLATE.md) → `evaluation/regrade/verdict-YYYY-MM-DD.md`.
3. Fill §4a/§4b scores + the §4c provenance block. Optionally record a `/4.30` letter grade in
   prose if you intend it to become the live grade.
4. Commit the verdict, then update `STATUS.md` to cite it. The C5 grade-provenance gate
   (`check_status_consistency.py`) then permits a live grade; `test_status_cites_regrade_when_present`
   ([`tests/gates/test_regrade_kit.py`](../../tests/gates/test_regrade_kit.py)) enforces the citation.

*Wave-3 exit (E2) closes when this verdict is filed and the consolidated `wave3-status.md`
finding→commit map is committed.*
