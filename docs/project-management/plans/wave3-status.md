---
title: Wave 3 — Status & Exit Map
category: research
tags: [wave-3, exit, remediation, finding-map, governance]
created: 2026-07-20
updated: 2026-07-20
provenance: Authored from the re-grade kit's finding register (evaluation/regrade/regrade-kit-2026-07.md) plus verified git archaeology of the Wave-3 merges; every "closed" row cites a merge/commit and a test. STATUS.md remains the canonical maturity home — this doc confers no grade.
---

# Wave 3 — Status & Exit Map

> Companion to [`wave3-technical-spec-2026-07-19.md`](wave3-technical-spec-2026-07-19.md)
> §WS-E/E2. `STATUS.md` remains the single source of truth for maturity; this
> document maps each finding to its closing commit + test and records the
> exit-criteria state. **It does not confer or restate a grade** — the independent
> re-grade (R14 / CLM-02) is pending and is not self-served here.

## 0. One-paragraph state

Wave 3 closed the scale/DoS, watsonx-economics, governance-gate and compound-demo
work across PRs #25–#37, and this exit PR adds the two WS-A items that were scoped
but never built (A7 input-bound caps, A8 scale-regression gate) plus the one open
HIGH an independent 2026-07-20 re-audit surfaced (ATK-MEM-02, unsigned trust tier
honoured on read). **After ATK-MEM-02 there are zero open Critical/High.** Wave 3
therefore exits **CONDITIONALLY**, blocked only on: (i) the independent R14 verdict
(not dischargeable by this lineage), and (ii) the *post-verification residuals*
(§2): the four MEDIUM items (three L2-cache defects + NEW-1) are now closed in
`443ad77`; three LOW/cosmetic NEW defects remain tracked.

## 1. Exit-criteria checklist (spec §656)

| # | Criterion | State | Evidence |
|---|---|---|---|
| a | Every WS-A/B/C/D sub-task RED→GREEN in CI on 3.11 + 3.12 | **Met** (+ A7/A8 this PR) | PRs #25–#37 merged green; A7/A8 tests added this PR |
| b | Scale gate (A8) + C1/C2/C3/C5 self-tests + D3 demo run in CI | **Met this PR** | A8 wired as a dedicated CI step (was in *no* job); C-gate self-tests + D3 already in CI |
| c | Full suite green ex load/perf; coverage ≥ 80% + per-package floors | **Met** | 1386 passed, 23 skipped; coverage gate + `check_coverage_by_package.py` in CI |
| d | E1 kit committed + grade-provenance (C5) gate live | **Met** | PR #37 (`1051af7`) + #38 (`5ff3b5c`); C5 points at `evaluation/regrade/` |
| e | Every remaining Critical/High closed **or** dated-accepted | **Partial** | Zero open Critical/High after ATK-MEM-02 (this PR). MEDIUM/minor residuals open + dated below; MEM-02/03 & ATK-MEM-03 remain Partial |
| — | Independent re-grade (R14) | **Pending** | Not self-served; see §5 |

## 2. Finding → closure map

Dispositions carried from `evaluation/regrade/regrade-kit-2026-07.md` (the register
at `6d0711d`), with the closing merge/commit resolved by archaeology. `W1` = the
2026-07-19 Wave-0/R/1 remediation branch; Wave-3 items cite their PR.

### Critical

| ID | Finding | Disposition | Commit | Test |
|---|---|---|---|---|
| CODE-01 | `#slug` doc_ids fail existence check → silent keyword-only scan | Closed (W1) | W1 | `tests/retrieval/test_wiring.py` |
| CODE-02 / MEM-01 | Embedding index + graph wired into no production path | Closed (W1) | W1 | `src/cli.py:344-388`; retrieval tests |
| CODE-03 / 07 | `optimize()` returns "" > 4096 tok; frontmatter flattening | Closed (W1) | W1 | `tests/optimizer/test_optimizer_integrity.py` |
| CLM-01 | Tree failed ≥3 of its own gates | Closed | W1 | honesty gates + validate-kb green |
| CLM-02 | A+ self-conferred; no independent verdict on file | **Open — R14 pending** | — | see §5 |

### High

| ID | Finding | Disposition | Commit | Test |
|---|---|---|---|---|
| ATK-DOS-01 | PageRank dangling-node O(N²) | Closed (Wave-3 A1) | #27 `fc53018` | `tests/performance/test_dos_hardening.py` (mixed-dangling) |
| CODE-04 / ATK-DOS-04 | Index rows never reclaimed; O(N²) `np.vstack` rebuild | Closed (Wave-3 A3ii) | #27 `fc53018` | WS-A rebuild tests |
| CODE-05 | Recency weighting numerically inert | Closed (W1) | W1 | `test_ranking_normalization.py` |
| CODE-06 | PageRank blend scale-mismatch | Closed (W1) | W1 | `tests/retrieval/` |
| CODE-08 / ATK-FS-02 | L2→L1 promotion caches fuzzy match as forged exact hit | Closed — **promotion vector** (W1); **L2 direct-serve collision** closed (`443ad77`) | W1 + `443ad77` | `tests/security/test_cache_integrity.py`; `test_l2_cache_residuals.py` (§2) |
| CODE-10 | watsonx tokenizer/pricing dishonesty | Closed (Wave-3 B1–B4) | #27 `fc53018` | WS-B tests |
| MEM-04 | `validate-kb.sh` never exits non-zero | Closed (W1) | W1 | `test_validate_kb.py` |
| ATK-FS-01 | Arbitrary file read via symlink escape | Closed (W1 + Wave-3 D3) | #33 `9606fdc` | `tests/security/test_path_containment.py` |
| ATK-GATE-02 | Status validator SKIPs renamed live doc, fails open | Closed — fail-closed (W1) | W1 | `check_status_consistency.py:377-383` |
| ATK-GATE-03 | Bare word "manifest" backs a savings claim | Closed (W1) | W1 | `scripts/check_savings_claims.py` |
| ATK-MEM-04 | Auto-commit propagates unreviewed KB writes | Closed — stage+PR gate (W1) | W1 | `scripts/mnemox.sh` |
| **ATK-MEM-02** | **Forged `trust_tier: verified` served as trusted (unsigned) on read** | **Closed (Wave-3 exit)** | **`0e97f6e`** | **`tests/security/test_trust_tier.py` (forged→withheld; signed→served), mutation-verified** |
| **A7** | No global input bounds (file/chunks/query/nodes) | **Closed (Wave-3 exit)** | **`37c1ebc`** | **`tests/security/test_input_bounds.py` (4)** |
| **A8** | No scale-regression gate on PRs | **Closed (Wave-3 exit)** | **`37c1ebc`** | **`tests/performance/test_scale_invariants.py` + `tests/gates/test_scale_gate_selftest.py`** |

### Accepted-by-design / disclosed (dated 2026-07-20)

| ID | Finding | Disposition | Rationale |
|---|---|---|---|
| ATK-GATE-01 | No magnitude ceiling; cherry-pick inflates headline | Accepted-by-design + Wave-3 C4 | Held-out reproduction gate (PR #29 `2dceffc`) defeats the cherry-pick without re-incentivising fabrication; a magnitude ceiling is deliberately not imposed (composition guard only) |
| ATK-GATE-07 | Self-referential gates; one owner edits gate + claim in one PR | Accepted (disclosed) + Wave-3 C3 | Structural `gate-integrity` check (PR #28 `f28b317`) blocks the single-PR mechanical attack; a second human reviewer is pursued opportunistically. **Disclosed residual:** `check_gate_integrity.py` does not yet cover `.github/workflows/` (a `ci.yml` edit that stops invoking a gate + a planted claim would bypass it) — deferred, tracked |
| ATK-MEM-03 | Retrieval ranking gameable via keyword-stuffing | Partial | Trust-tier + graph mitigate; BM25 TF-saturation + heading cap bound it; raw keyword score still stuffable — accepted as MEDIUM |
| MEM-02 / MEM-03 | Pointer case + broken kebab-case refs | Partial | 15 repaired W1; `validate-kb` green at `6d0711d`; remaining are non-blocking link hygiene |
| ATK-SUP-09 / SEC-01 | Committed lab credential | Absent in code/config at `6d0711d` | grep-verified; docs-only mention at most |

### Post-verification residuals

Reported by the independent 2026-07-20 re-audit
(`docs/knowledge-base/research/master-engagement-reaudit-2026-07-20.md`), each
independently re-verified against the code before action. **The four MEDIUM items
(R-1's three L2-cache defects + NEW-1) are now closed** in `443ad77` (RED→GREEN +
mutation-verified); the three LOW/cosmetic NEW-2..4 remain tracked.

| ID | Sev | Finding | Status |
|---|---|---|---|
| ATK-FS-05 | MEDIUM | `SemanticCache.set()` stored the caller's metadata dict by reference **and** mutated it | **Closed** (`443ad77`) — `tests/security/test_l2_cache_residuals.py::test_atkfs05_*` |
| ATK-FS-04 | MEDIUM | `contains()`/`get_with_similarity()` ignored TTL (contains=True while get=None after expiry) | **Closed** (`443ad77`) — `_is_expired` on the similarity path; `test_atkfs04_contains_honors_ttl` |
| ATK-FS-02 | MEDIUM | direct L2 serve returned a *distinct* colliding prompt's payload at cosine 1.0 (stopword-stripped hashing collision) | **Closed** (`443ad77`) — collision guard (fail-safe miss); `test_atkfs02_*` (exact + fuzzy paths preserved) |
| NEW-1 | MEDIUM | optimizer cache keyed on the prompt only → a stricter `max_tokens` returned an earlier *uncapped* result (and the reverse) | **Closed** (`443ad77`) — budget folded into the key; `tests/optimizer/test_new1_cache_budget.py` |
| NEW-2 | Low | `--date-filter` inert on the index path (`file` carries `#slug`, `_doc_date_matches` fails open) | **Open — tracked** |
| NEW-3 | Low | per-node semantic edge cap counts one direction only (a node reached 59 vs cap 50; the global cap still bounds totals) | **Open — tracked** |
| NEW-4 | Cosmetic | clean checkout flags every shipped doc stale (mtime-sentinel drift; retrieval unaffected) | **Open — tracked** |

### 2026-07-20 re-audit — register disposition

The independent re-audit
(`docs/knowledge-base/research/master-engagement-reaudit-2026-07-20.md`) graded the
**pre-fix** tree (`v1.0-136-g07ad245`, before `0e97f6e` / `37c1ebc` / `443ad77`), so
both its ≈3.8/5 and its open-residual list predate the closures above. Its full
register is dispositioned in the tables above; this is the crosswalk and the standing
against the re-audit's own GO condition (its §6).

| Re-audit GO condition (§6) | Current standing |
|---|---|
| Zero open Critical/High (ATK-MEM-02 closed) | **Met on main** — `0e97f6e` (see High table) |
| L2 cache residuals closed **or** formally risk-accepted | **Met on #41 merge** — ATK-FS-02/04/05 closed (`443ad77`); NEW-2..4 risk-accepted (tracked above) |
| Independent re-grade ≥ 4.0/5 on the post-W-B tree | **Open** — R14 (§5); must score the post-`443ad77` tree, not the pre-fix tree the re-audit itself graded |

Recommendation crosswalk: **R1** (provenance-at-read) = ATK-MEM-02 `0e97f6e`; **R2**
(unify L2 cache semantics) = ATK-FS-02/04/05 `443ad77`; **R3** (fold budget into the
optimizer key) = NEW-1 `443ad77`; **R7** (vulnerable-layer discipline) institutionalized
in [`adversarial-remediation-plan.md`](../../../adversarial-remediation-plan.md)
(Status-discipline section); **R4–R6** (NEW-2..4) tracked-open above. The re-audit's
≈3.8/5 is a candidate *input* to R14, not the verdict — §5.

## 3. Scale hardening (A7 + A8) — this exit PR (`37c1ebc`)

- **A7** — `src/limits.py` is the single home for `MAX_FILE_BYTES` (1 MiB),
  `MAX_CHUNKS_PER_DOC` (500), `MAX_QUERY_CHARS` (8192), `MAX_GRAPH_NODES` (20000);
  enforced at embedding-index ingest, the chunker, query entry, and the graph
  builder. Restated in `config/gates/gate-config.yaml::input_bounds` and
  drift-guarded by `check_value_homes.py` (mutation-verified).
- **A8** — `tests/performance/test_scale_invariants.py` asserts the four WS-A
  ratios (PageRank, `build_semantic`, cold rebuild, L2 evict) against ceilings in
  `gate-config.yaml::perf_scale`; wired as a dedicated CI step because these ran in
  no existing job. `tests/gates/test_scale_gate_selftest.py` proves the gate bites
  by re-introducing the pre-A4 O(N) eviction and the O(N²) PageRank reference.
  The spec's `l2_evict` ceiling of 1.5 was corrected to 8.0 from measurement
  (O(1)+locality ≈ 4×; O(N) min-scan ≈ 46×).

## 4. ATK-MEM-02 — this exit PR (`0e97f6e`)

The retrieval read path honoured a raw `trust_tier: verified` frontmatter value
without checking the HMAC signature `src/provenance.py` already provides
(`verify_document` was wired only to *promote*, never *read*). `KnowledgeBaseQuery`
now confers trusted-content access only on a `verified` doc that carries an
authentic signature; a forged/tampered one is withheld like an unverified doc.
Fail-closed and consistent with the current corpus (zero signed docs — adopting
signing on the write path is a separate, tracked step).

## 5. Independent re-grade (R14 / CLM-02) — pending, not self-served

Every grade increment to date came from the same agentic lineage doing the
remediation; the self-assessed A+ is withdrawn (`STATUS.md:11`). The E1 kit
(`evaluation/regrade/`) and its provenanced verdict slot are built, and the C5 gate
refuses to let a grade go live until a provenanced `verdict-*.md` exists. **This
document does not fill that slot.**

An independent 2026-07-20 re-audit (Claude Cowork surface — a distinct lineage from
the Claude Code session that authored the remediation) scored the pre-A7/A8 tree at
**≈3.8/5** and explicitly offers that as *one input* to the pending re-grade. It is
recorded here as a candidate input; **whether it discharges R14 is a human decision,
not one this session may make** — it graded a tree that predates ATK-MEM-02's
closure and this exit PR, and independence-of-lineage is a judgement the project
owner must ratify.

## 6. Exit verdict

**Wave 3 — CONDITIONALLY CLOSED.** Exit criteria (a)–(d) met; (e) met for
Critical/High (zero open after ATK-MEM-02) with MEDIUM/minor residuals dated-tracked
above. Two gates remain before an unconditional close:

1. **R14 independent verdict** filled into `evaluation/regrade/verdict-<date>.md` by
   a human or a genuinely distinct process (§5).
2. **Post-verification residuals** (§2): the four MEDIUM items closed (`443ad77`); the
   three LOW/cosmetic NEW-2..4 closed or formally risk-accepted.

No self-run grade is presented as independent.
