# Remediation Plan — Post Phase-8 Residuals

**Branch:** `fix-multilevel-cache-race`  
**Basis:** Full codebase and documentation review (2026-07-14), grounded by direct file reads against current branch state  
**Authoritative prior audit:** `docs/knowledge-base/research/audit-2026-07-14-signoff.md`

## Context

The Phase-8 adversarial sign-off audit (NO-GO verdict, grade B+/A−) identified several blockers. Direct inspection of the *current branch* confirms that the majority of those findings have already been remediated:

| Phase-8 finding | Current state |
|----------------|---------------|
| Fabricated metrics on ~12 live surfaces | ✅ All files carry retraction banners; `check_savings_claims.py` is tree-wide |
| `check_savings_claims.py` 5-file allowlist | ✅ Upgraded to tree-wide scan in Phase 8 |
| ExactCache versioned-key collision | ✅ `escape_version()` already applied |
| `ConfigManager.load_from_env()` skips validation | ✅ Compute-validate-commit already in place |
| Facade's disjoint cache | ✅ Optimizer shares L1 from `MultiLevelCache`; documented in docstring |
| `documentation_agent.py` raw `rglob()` | ✅ `resolve_within()` called before traversal |
| `pip-audit` non-blocking | ✅ Already blocking (Phase 8) |
| CI installs from floating `>=` | ✅ CVE gate audits against `uv.lock` locked closure |
| `THREAT_MODEL.md` over-claims delegation | ✅ Leaf-level containment documented + tested |
| `STATUS.md:18` stale assertion | ✅ Correctly states bugs fixed with regression tests |
| `AGENTS.md` delegation floor contradiction | ✅ Both locations correctly state 52% floor / ~53% measured |

**Remaining open work** (verified by direct file reads):

1. `yourusername` placeholder URLs survive in several live docs (not just `INSTALLATION.md`)
2. `README2.md` and `README3.md` are duplicate root files that should not exist
3. `STATUS.md` maturity table still shows `≈ D‑` grade, which is stale vs. the verified B+/A− re-grade
4. `docs/knowledge-base/index.md:136` contains a `yourusername` link
5. `docs/knowledge-base/guides/setup-token-optimization.md:24` contains a `yourusername` clone URL
6. `docs/BOOK_CHAPTER_08.md` lines 38, 426, 428 contain `yourusername` URLs
7. The 82-file grep list for `68.96|89.3%|91.80` reveals many files now carry banners or are frozen research — but it is worth verifying the gate works correctly against a sample

The correct real GitHub URL (from `pyproject.toml:54`) is:  
`https://github.com/davidleconte/bob-llmwiki-knowledge-manager`

---

## Sub-Tasks

---

### Sub-Task 1 — Replace all `yourusername` placeholder URLs

**Status:** `[ ] pending`

**Intent**  
The `pyproject.toml` was corrected in a prior phase to use `davidleconte` as the GitHub owner. Several documentation files still contain the old `yourusername` placeholder. These are the only live surfaces remaining with broken links.

**Affected files (verified by grep):**
- `docs/installation.md` — lines 18, 189
- `docs/BOOK_CHAPTER_08.md` — lines 38, 426, 428
- `docs/knowledge-base/guides/setup-token-optimization.md` — line 24 (clone URL)
- `docs/knowledge-base/guides/token-optimizer-quick-install.md` — line 27
- `docs/knowledge-base/index.md` — line 136 (footer link)

**Expected Outcomes**  
- `grep -r "yourusername" --include="*.md" .` (excluding `.claude/`) returns zero matches
- All clone URLs point to `https://github.com/davidleconte/bob-llmwiki-knowledge-manager`

**Todo List**
1. Read each affected file to confirm exact line content
2. Replace `yourusername` with `davidleconte` in each file using `search_and_replace`
3. Verify no `yourusername` occurrences remain in non-worktree markdown files

**Relevant Context**
- Correct URL: `https://github.com/davidleconte/bob-llmwiki-knowledge-manager` (from `pyproject.toml:54`)
- Worktrees under `.claude/` are CI scratch directories — skip them
- Audit snapshots under `docs/knowledge-base/research/` are frozen; their references to `yourusername` are citations of old bugs (do not edit)

---

### Sub-Task 2 — Delete duplicate root README files

**Status:** `[ ] pending`

**Intent**  
`README2.md` and `README3.md` at the repo root are redundant files. `README2.md` contains a separate "dual-system" framing; `README3.md` appears to be a near-copy of `README.md`. They are not referenced from any index, not linked from CI, and create confusion about which file is authoritative. `README.md` is the declared single source. These should be deleted.

**Expected Outcomes**  
- Only `README.md` exists at the root
- `ls *.md` at repo root shows no `README2.md` or `README3.md`
- No other file links to `README2.md` or `README3.md` (verify before deleting)

**Todo List**
1. Grep for any references to `README2.md` or `README3.md` across the repo
2. If no live references exist, delete both files
3. If any reference exists, update the referring file to point to `README.md` instead, then delete

**Relevant Context**
- Both files are listed as untracked in the git status snapshot at the start of this conversation
- `README.md` is the authoritative file (declared in `AGENTS.md`, `pyproject.toml:9`, and `check_status_consistency.py`)
- `docs/knowledge-base/index.md:20` links to `README3.md` — this must be updated before deletion

---

### Sub-Task 3 — Update `STATUS.md` maturity grade to reflect verified re-audit result

**Status:** `[ ] pending`

**Intent**  
`STATUS.md` is the declared single source of truth for maturity status. Its table currently shows `≈ D‑ (target: A+)` as the weighted grade — a value from the 2026-07-13 institutional audit. The 2026-07-14 adversarial Phase-8 re-audit verified the actual grade as **B+/A− (3.46 / 4.3)**, up from D−. The table should reflect the verified current state so the file is not self-contradictory.

The test count in the Terminology section also cites `771 passed` (a Phase-8 figure) — this is accurate as a point-in-time snapshot and carries the right provenance language.

**Expected Outcomes**  
- `STATUS.md` table row `Weighted grade vs institutional bar` shows the verified B+/A− grade with a reference to the Phase-8 sign-off audit
- `check_status_consistency.py` still passes (it checks maturity status and coverage gate, not the GPA figure)
- The NO-GO sign-off decision is noted (not elided)

**Todo List**
1. Read `STATUS.md` fully to see current table
2. Update the `Weighted grade vs institutional bar` row to: `≈ B+/A‑ (3.46/4.3) — Phase-8 re-audit; NO-GO vs A+ sign-off bar (see audit-2026-07-14-signoff.md)`
3. Update the `Basis` row to also reference `audit-2026-07-14-signoff.md`
4. Run `python scripts/check_status_consistency.py` to confirm it still passes

**Relevant Context**
- `STATUS.md` lines 5–12 — the table to update
- `docs/knowledge-base/research/audit-2026-07-14-signoff.md` — source of the B+/A− grade
- `scripts/check_status_consistency.py` — gate that must remain green
- Do not change `Overall status` ("Beta — Not Production Ready") — that is correct

---

### Sub-Task 4 — Verify `check_savings_claims.py` gate is effective tree-wide

**Status:** `[ ] pending`

**Intent**  
The Phase-8 sign-off audit's primary blocker (A1) was that `check_savings_claims.py` used a 5-file allowlist and could not see the fabricated figures on `docs/BOOK_*`, `docs/adr/*`, and guide files. The script was upgraded to tree-wide scanning in Phase 8. This sub-task verifies the upgrade is actually effective — that the gate correctly passes the current tree (all files bannered or frozen) and that it would correctly fail if an un-bannered fabricated claim were introduced.

**Expected Outcomes**  
- `python scripts/check_savings_claims.py` exits 0 on the current tree
- `python scripts/check_savings_claims.py --selftest` exits 0
- Adding a test line `"This saves 89.3% tokens."` to a non-bannered, non-excluded file causes the gate to exit non-zero (manual verification or a new test)

**Todo List**
1. Read `scripts/check_savings_claims.py` fully to confirm tree-wide scan logic
2. Run `python scripts/check_savings_claims.py` and confirm exit 0
3. Run `python scripts/check_savings_claims.py --selftest` and confirm exit 0
4. Spot-check: create a throwaway temp file with an un-backed claim, confirm the gate catches it, then delete the temp file

**Relevant Context**
- `scripts/check_savings_claims.py` lines 14–31 — the Phase-8 scope description
- `EXCLUDED_DIR_PARTS` and `BANNER_MARKERS` constants control what is exempt
- The gate runs in CI under the `lint` job in `.github/workflows/ci.yml`

---

### Sub-Task 5 — Fix `STATUS.md` stale phase roadmap reference

**Status:** `[ ] pending`

**Intent**  
`STATUS.md` line 12 says `Roadmap | Phases 0–8 (see the approved remediation plan)`. The Phase-8 adversarial audit is complete (NO-GO verdict filed). The roadmap row should reflect that Phase 8 produced a NO-GO with a documented gap list, and that the gap list is captured in `audit-2026-07-14-signoff.md` + `remediation-plan.md` (this file). This is a minor but precise accuracy fix on the canonical status document.

**Expected Outcomes**  
- `STATUS.md` roadmap row is updated to reflect Phase 8 complete (NO-GO) with a pointer to the gap list
- `check_status_consistency.py` still passes

**Todo List**
1. Update `STATUS.md` table row `Roadmap` to: `Phases 0–8 complete (Phase 8 = NO-GO; gap list in audit-2026-07-14-signoff.md + remediation-plan.md)`
2. Run `python scripts/check_status_consistency.py` to confirm it still passes

**Relevant Context**
- `STATUS.md` line 12 — row to update
- This is intentionally a separate sub-task from Sub-Task 3 to keep diffs reviewable

---

### Sub-Task 6 — Run full gate suite and confirm clean

**Status:** `[ ] pending`

**Intent**  
After all prior sub-tasks are complete, run the full local gate suite to confirm no regressions were introduced and the repository is in a clean, self-consistent state. This is the final checkpoint before the plan is considered done.

**Expected Outcomes**  
- All gates pass with exit 0
- `pytest` passes with no new failures
- `check_status_consistency.py` passes
- `check_savings_claims.py` passes
- `ruff check .` and `ruff format --check .` pass

**Todo List**
1. Run `ruff check .` — fix any new issues
2. Run `ruff format --check .` — fix any formatting issues
3. Run `python scripts/check_status_consistency.py`
4. Run `python scripts/check_savings_claims.py`
5. Run `python scripts/check_value_homes.py`
6. Run `python -m pytest tests/ -x -q` (fast smoke pass)
7. Report any failures and address them

**Relevant Context**
- Full gate list documented in `CONTRIBUTING.md`
- CI runs `.github/workflows/ci.yml` — this sub-task mirrors the `lint` + `test` jobs locally
- Do not run `pytest --cov=src` (slow); the quick smoke pass is sufficient for this cleanup work
