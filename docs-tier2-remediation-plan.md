# Docs Tier-2 Remediation Plan
# All remaining documentation gaps to institutional vendor standard

**Goal:** Bring every remaining document in the repository to A-grade against the
institutional Tier-1 Software Vendor standard (arc42, Diátaxis, MECE).

**Scope:** 26 files across 4 groups. The core docs (root, docs/, docs/adr/,
docs/architecture/, docs/security/, docs/api/, docs/knowledge-base/) already grade A/A−.
This plan covers the residual non-A surfaces.

**Gates must stay green after every sub-task.**

---

## Sub-task 1 — Fix live claim inconsistencies (two files with wrong facts)

**Intent:**
Two live (non-frozen, non-banner-covered) files contain claims that contradict
STATUS.md. Unlike the project-management frozen docs, these are guides on the
primary navigation path.

File 1: `docs/knowledge-base/guides/token-optimizer-quick-install.md:179`
- Claims "C+ (2.5/4.0 GPA), 60% production readiness"
- STATUS.md says: A (3.89/4.30), Beta — Not Production Ready
- This contradicts the grade and misrepresents "60% production ready" when STATUS.md
  says Beta maturity (not a % figure)

File 2: `docs/REPOSITORY_ANALYSIS_WORKFLOW.md`
- No retraction banner, no frontmatter
- Created 2026-07-12; references "Token Optimization System (caching & optimization)"
  alongside KB Manager as two integrated tools — implies they are integrated (they are not)
- Inconsistent with the dual-system separation maintained throughout all other docs

**Expected Outcomes:**
- `token-optimizer-quick-install.md:177-185` — stale status block updated to cite
  STATUS.md correctly (A, 3.89/4.30, Beta) or redirected to STATUS.md
- `REPOSITORY_ANALYSIS_WORKFLOW.md` — frontmatter added; retraction banner added to
  the "Important Caveats" section; dual-system integration claim qualified

**Todo List:**
1. Read `docs/knowledge-base/guides/token-optimizer-quick-install.md:170-200` fully.
2. Update lines 177-185 to replace the stale C+ grade with: link to STATUS.md for
   current grade; remove "60% production readiness" (not a metric STATUS.md uses).
3. Read `docs/REPOSITORY_ANALYSIS_WORKFLOW.md` fully.
4. Add YAML frontmatter (title, date: 2026-07-12, status: reference, category: guide).
5. Add a "**Note:**" callout near line 12 clarifying the two systems are NOT integrated
   (they work together but remain independent), consistent with docs/README.md.
6. Run `python3 scripts/check_status_consistency.py` — must pass.
7. Run `ruff check src/ scripts/ tests/` — must pass (no Python changes, but confirm).

**Relevant Context:**
- `docs/knowledge-base/guides/token-optimizer-quick-install.md:170-185` — stale status
- `docs/REPOSITORY_ANALYSIS_WORKFLOW.md:1-20` — missing frontmatter + integration claim
- `STATUS.md` — authoritative grade
- `docs/README.md` — canonical dual-system framing

**Status:** [ ] pending

---

## Sub-task 2 — Fix docs/project-management/README.md metrics (banner-covered but asserts fabricated numbers)

**Intent:**
`docs/project-management/README.md` carries a retraction banner on line 3
(correctly naming "68.96%, 89.3%, 91.80%" as fabricated). The banner satisfies
`check_savings_claims.py` via the banner-exception rule. However, the body
(lines 57-70) still contains an active "Key Project Metrics" table asserting:
- "A+ Quality Standards: 100%" — contradicts STATUS.md (A, not A+)
- "Production Readiness: 100%" — contradicts STATUS.md (Beta, not production-ready)
- "Overall Grade: A+ WITH HONORS" — contradicts STATUS.md (A, 3.89/4.30)
- "Token Savings: 89.3%" — fabricated, retracted

The banner makes these claims legally pass the gate but they remain misleading to
any reader who glances at the table.

The right fix: replace the metrics table body with a redirect to STATUS.md.
The historical narrative (weeks 17-20, timeline, what was built) stays as-is —
only the claims table rows are updated.

**Expected Outcomes:**
- Lines 57-70: The four misleading rows are replaced with accurate current values
  or a single redirect to STATUS.md.
- All other content in the file (timeline, directory structure, links) stays intact.
- `check_savings_claims.py` continues to pass (it already passes; nothing should break).
- `check_status_consistency.py` passes.

**Todo List:**
1. Read `docs/project-management/README.md:50-75` to confirm exact current content.
2. Replace the four rows in "Quality Achievements" (lines 58-62) with accurate values
   sourced from STATUS.md: grade = A (3.89/4.30), production readiness = Beta,
   overall = A.
3. Replace lines 64-70 "System Performance" table rows for Token Savings (89.3%) and
   Quality Score (91.80%) with references to `evaluation/results/validation-2026-07-14/`
   and the manifest-backed ~20% figure. Latency and coverage can stay as-is.
4. Run `python3 scripts/check_status_consistency.py && python3 scripts/check_savings_claims.py`.

**Relevant Context:**
- `docs/project-management/README.md:1-75` — the file to fix
- `STATUS.md` — source of truth for all metric replacements

**Status:** [ ] pending

---

## Sub-task 3 — Add frontmatter to docs/ root orphan docs and project-management tree

**Intent:**
24 files under `docs/` and `docs/project-management/` lack YAML frontmatter.
All Tier-1 research/planning documents in this repo carry frontmatter with
`title`, `date`, `status`, and `category`. The absence of frontmatter makes
documents harder to navigate and inconsistent with the knowledge-base/ standard.

Files that need frontmatter added:

**docs/ root (3 files):**
- `docs/TOKEN_SAVINGS_TEST_PLAN.md` — historical, needs `status: superseded`
- `docs/WORKFLOW_AUTOMATION_PLAN.md` — historical, needs `status: historical`
- `docs/REPOSITORY_ANALYSIS_WORKFLOW.md` — reference guide (handled in ST-1 if
  not already done there)

**docs/project-management/phases/ (5 files):**
- `PHASED_IMPLEMENTATION_WITH_MOCK_TESTING.md`
- `PHASE_1_IMPLEMENTATION_SUMMARY.md`
- `PHASE_2_IMPLEMENTATION_PLAN.md`
- `PHASE_3_EXECUTIVE_SUMMARY.md`
- `PHASE_3_IMPLEMENTATION_PLAN.md`

**docs/project-management/planning/ (9 files):**
- `BEST_PRACTICES_IMPLEMENTATION_PLAN.md`
- `DOCUMENTATION_GAP_ANALYSIS.md`
- `DOCUMENTATION_REORGANIZATION_PLAN.md`
- `LLM_OPTIMIZATION_COMPLETE_SUMMARY.md`
- `MOCK_DATA_AUTOMATION.md`
- `MOCK_DATA_QUALITY_ANALYSIS.md`
- `TOKEN_OPTIMIZATION_IMPLEMENTATION_PLAN.md`
- `WEEK_19_COMPLETION_SUMMARY.md`
- `WEEK_20_IMPLEMENTATION_PLAN.md`

**docs/project-management/reviews/ (8 files):**
- `ADVERSARIAL_REVIEW_NEXT_STEPS.md`
- `ARCHITECTURE_AUDIT_FINAL.md`
- `ARCHITECTURE_AUDIT_REPORT.md`
- `ARCHITECTURE_AUDIT_REPORT_REVISED.md`
- `HANDOFF_PROMPT.md`
- `PROJECT_AUDIT_REPORT.md`
- `WEEK18_FINAL_VALIDATION_REPORT.md`
- `WEEK2_DAILY_CHECKLIST.md`

**Expected Outcomes:**
- Every file has a YAML frontmatter block with at minimum:
  `title`, `date` (from existing Last Updated or creation context), `status`,
  `category`.
- `status` values: `superseded` / `historical` / `aspirational` / `reference`
  as appropriate per file content.
- No existing content is changed — frontmatter is inserted at the top.
- All banners already present stay in place below the frontmatter.

**Todo List:**
1. For each file: read lines 1-5 to determine if frontmatter already present and
   what existing header line is.
2. Insert frontmatter block before line 1. Do not remove or reorder existing content.
3. For `docs/TOKEN_SAVINGS_TEST_PLAN.md`: add `status: superseded`,
   `superseded_by: evaluation/results/validation-2026-07-14/`
4. For all `project-management/phases/*`: add `status: historical`,
   `superseded_by: docs/knowledge-base/research/audit-2026-07-14-signoff.md`
5. For all `project-management/planning/*`: add `status: aspirational`,
   `note: Proposed implementation plan; actual status in Phase-8 sign-off audit`
6. For all `project-management/reviews/*`: add `status: historical`,
   `superseded_by: docs/knowledge-base/research/audit-2026-07-14-signoff.md`
7. Run `python3 scripts/check_savings_claims.py` — must pass (banners still present).
8. Run `python3 scripts/check_status_consistency.py` — must pass.

**Relevant Context:**
- `docs/knowledge-base/research/adversarial-review-round1-2026-07-13.md:1-10` —
  example of correct frontmatter format
- `docs/knowledge-base/guides/token-optimizer-quick-install.md:1-10` —
  another example of correct frontmatter

**Status:** [ ] pending

---

## Sub-task 4 — Delete README4.md and commit all changes

**Intent:**
`README4.md` is a byte-for-byte duplicate of `README.md`. It has no incoming
references, violates the "one home per value" principle, and was kept as a source
copy when README.md was replaced. It should be removed.

**Expected Outcomes:**
- `README4.md` is deleted.
- All changes from ST-1, ST-2, ST-3 are committed with logical commit messages.
- All gate scripts pass.

**Todo List:**
1. Confirm `README4.md` is still identical to `README.md` (no drift since last check).
2. Delete `README4.md`.
3. Run all gate scripts one final time.
4. Commit: `git add -A && git commit -m "docs(tier2): ..."` with appropriate message.

**Relevant Context:**
- `README4.md` — the duplicate to delete
- All gate scripts in `scripts/`

**Status:** [ ] pending
