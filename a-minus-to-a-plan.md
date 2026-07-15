# Plan: A− → A (Gap Closure)

**Branch:** `fix-multilevel-cache-race`  
**Basis:** Post-remediation scorecard (2026-07-14) · Grounded by direct file reads  
**Goal:** Close the three remaining scoreboard gaps that prevent A-grade on any dimension

## Scope correction (important)

The scorecard listed "Enforce TTL in caches" as finding #2. Direct file inspection shows **TTL is already fully implemented**:
- `src/cache/exact_cache.py:162-176` — `get()` checks `age_seconds` against `ttl_seconds`, evicts expired entries
- `src/cache/semantic_cache.py:264-279` — `_finalize_hit()` does the same for L2
- `src/cache/multi_level_cache.py:73-78` — TTL forwarded to sub-caches from config
- `tests/cache/test_exact_cache.py` — `TestExactCacheTTL` (4 tests); `tests/cache/test_semantic_cache.py` — `TestSemanticCacheTTL` (2 tests); `tests/cache/test_multi_level_cache.py` — `TestMultiLevelCacheTTL` (2 tests)

That audit finding was stale. **The three real items are:**

1. **#2 → CI install-from-lock** — 5 jobs install from floating `>=` floors; replace with `uv sync --frozen`
2. **#3 → Delete README2.md and README3.md** — orphaned root duplicates (deletion was blocked earlier)
3. **#4 → Curate `docs/` root** — 22 non-spine files cluttering the Diátaxis root; move to `docs/archive/`

---

## Sub-Task 1 — Wire CI to install from `uv.lock`

**Status:** `[ ] pending`

**Intent**  
Five jobs in `.github/workflows/ci.yml` install dependencies with `pip install -e ".[dev,monitoring]"`, which resolves `>=` floor constraints at runtime — meaning CI builds are not reproducible and could silently pick up a breaking upstream update. The `sbom` job already exports the locked closure for the CVE audit (`uv export --frozen`). The fix extends that discipline to the test jobs: replace the `pip install` step with `uv sync --frozen --extra dev --extra monitoring` so every job installs the exact pinned versions from `uv.lock`.

**Affected jobs and lines:**

| Job | Lines | Current command |
|-----|-------|----------------|
| `test` (matrix) | 42–45 | `pip install -e ".[dev,monitoring]"` |
| `typecheck` | 112–116 | `pip install -e ".[dev,monitoring]"` |
| `e2e` | 129–132 | `pip install -e ".[dev,monitoring]"` |
| `validation` | 151–154 | `pip install -e ".[dev,monitoring]"` |
| `benchmarks` | 180–183 | `pip install -e ".[dev,monitoring]"` |

The `sbom` job (lines 215–237) already installs `uv` separately for lock operations — no change needed there.

**Expected Outcomes**
- Every test-running CI job installs the exact versions pinned in `uv.lock`
- CI fails deterministically if `uv.lock` is out of sync (already enforced by `uv lock --check` in the `sbom` job)
- No test regressions — the locked closure is already in sync (`uv lock --check` passes)

**Todo List**
1. Read `.github/workflows/ci.yml` lines 28–50 (the `test` job's install step) to confirm exact current content
2. For each of the 5 jobs, replace:
   ```yaml
   - name: Install (editable + dev/monitoring extras)
     run: |
       python -m pip install --upgrade pip
       pip install -e ".[dev,monitoring]"
   ```
   with:
   ```yaml
   - name: Install uv
     uses: astral-sh/setup-uv@v4
     with:
       version: "latest"
   - name: Install (locked from uv.lock)
     run: uv sync --frozen --extra dev --extra monitoring
   ```
3. The `sbom` job manually installs uv via pip (`pip install ... uv`). Leave it unchanged — it has its own install chain for the SBOM/audit tools.
4. After editing, run `python3 scripts/check_value_homes.py` and `python3 scripts/check_status_consistency.py` to confirm no drift introduced

**Relevant Context**
- `uv.lock` is in sync (verified: `uv lock --check` passes in current session)
- `astral-sh/setup-uv` is the official GitHub Action for uv; the `sbom` job already uses it implicitly via `pip install uv`
- `uv sync --frozen` is equivalent to `pip install -e . --constraint <lock>` but uses the lock file directly
- The `cache: pip` line in `actions/setup-python` can be removed or kept (it will be a no-op when pip is not the installer)

---

## Sub-Task 2 — Delete README2.md and README3.md

**Status:** `[ ] pending`

**Intent**  
`README2.md` and `README3.md` at the repo root are orphaned duplicates. `README2.md` is an alternative "dual-system" framing; `README3.md` is a near-copy of `README.md`. Neither is referenced from any live index (the `docs/knowledge-base/INDEX.md` link was removed in a prior session). `README.md` is the declared authoritative file per `pyproject.toml:9`, `AGENTS.md`, and `check_status_consistency.py`. These files should not exist.

**Expected Outcomes**
- `ls *.md` at repo root shows only `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `LICENSE` (and `STATUS.md`, `remediation-plan.md`, `a-minus-to-a-plan.md`)
- `grep -r "README2\|README3" --include="*.md" . --exclude-dir=.claude` finds no live references

**Todo List**
1. Confirm no remaining live references: `grep -r "README2\|README3" --include="*.md" . --exclude-dir=.claude | grep -v "knowledge-base/research/"`
2. Delete both files
3. Run `python3 scripts/check_status_consistency.py` to confirm still passing

**Relevant Context**
- Both files were untracked in the original git status snapshot (not committed; safe to delete)
- `docs/knowledge-base/INDEX.md` link to `README3.md` was already removed in a prior session
- `docs/knowledge-base/research/full-codebase-review-2026-07-14.md:182` mentions the broken clone URL in `README2`/`README3` as a historical audit note — this is a frozen research doc, not a live link

---

## Sub-Task 3 — Curate `docs/` root: move archive content to `docs/archive/`

**Status:** `[ ] pending`

**Intent**  
The `docs/` root currently contains 35 files. Only 7 are the live Diátaxis spine (`QUICK_START.md`, `INSTALLATION.md`, `USAGE.md`, `CUSTOMIZATION.md`, `WORKFLOWS.md`, `MONITORING.md`, `README.md`). The remaining 28 are BOOK series chapters/appendices, phase completion reports, planning documents, design documents, and the legacy exhaustive index — none of which belong in the navigation root of a Diátaxis-structured documentation set. Moving them to `docs/archive/` cleans the root and fixes the F-dimension gap without deleting any content.

**Files to move (22 files):**

| Files | Current location | Target |
|-------|-----------------|--------|
| `BOOK_CHAPTER_01.md` … `BOOK_CHAPTER_09.md` (9 files) | `docs/` | `docs/archive/` |
| `BOOK_APPENDIX_A.md`, `BOOK_APPENDIX_B.md`, `BOOK_APPENDIX_C.md` (3 files) | `docs/` | `docs/archive/` |
| `BOOK_SUMMARY.md`, `BOOK_TABLE_OF_CONTENTS.md` (2 files) | `docs/` | `docs/archive/` |
| `PHASE1_IMPLEMENTATION_COMPLETE.md` … `PHASE4_IMPLEMENTATION_COMPLETE.md` (4 files) | `docs/` | `docs/archive/` |
| `DESIGN_DOCUMENT.md`, `DESIGN_DOCUMENT_KB_ADDENDUM.md` (2 files) | `docs/` | `docs/archive/` |
| `MECE_FRAMEWORK.md`, `COMPARISON.md` (2 files) | `docs/` | `docs/archive/` |

**Files to keep in `docs/` root (13 files — live, not archived):**

| File | Category | Keep reason |
|------|----------|-------------|
| `README.md` | Diátaxis nav hub | Authoritative entry point |
| `QUICK_START.md` | Tutorial | Live Diátaxis spine |
| `INSTALLATION.md` | How-to | Live Diátaxis spine |
| `USAGE.md` | How-to | Live Diátaxis spine |
| `CUSTOMIZATION.md` | How-to | Live Diátaxis spine |
| `WORKFLOWS.md` | How-to | Live Diátaxis spine |
| `MONITORING.md` | Reference | Live Diátaxis spine |
| `ARCHITECTURE.md` | Reference | Authoritative architecture doc |
| `INDEX.md` | Legacy index | Keep; README points to it as fallback |
| `REPOSITORY_ANALYSIS_WORKFLOW.md` | How-to | Live workflow doc |
| `WORKFLOW_AUTOMATION_PLAN.md` | How-to | Live planning doc |
| `TOKEN_SAVINGS_TEST_PLAN.md` | Reference | Live methodology doc |

**Links that break and must be updated:**

| File | Line | Link to update |
|------|------|----------------|
| `docs/README.md` | 68 | `DESIGN_DOCUMENT.md` → `archive/DESIGN_DOCUMENT.md` |
| `docs/README.md` | 68 | `MECE_FRAMEWORK.md` → `archive/MECE_FRAMEWORK.md` |
| `docs/README.md` | 68 | `COMPARISON.md` → `archive/COMPARISON.md` |
| `docs/README.md` | 70 | `BOOK_TABLE_OF_CONTENTS.md` → `archive/BOOK_TABLE_OF_CONTENTS.md` |
| `docs/INDEX.md` | 46–49 | `PHASE1/2/3/4_IMPLEMENTATION_COMPLETE.md` → `archive/PHASE*.md` |
| `docs/knowledge-base/concepts/token-optimization.md` | 293 | `../../DESIGN_DOCUMENT.md` → `../../archive/DESIGN_DOCUMENT.md` |

**Expected Outcomes**
- `ls docs/*.md` shows only the 13 live files listed above
- `docs/archive/` exists and contains 22 archived files
- All 4 links in `docs/README.md` and 4 links in `docs/INDEX.md` and 1 link in `token-optimization.md` are updated
- `python3 scripts/generate_api_docs.py --check` still passes (API docs are in `docs/api/`, unaffected)
- `python3 scripts/check_savings_claims.py` still passes (all archived files already have banners)
- `python3 scripts/check_status_consistency.py` still passes

**Todo List**
1. Create `docs/archive/` directory by writing a `docs/archive/README.md` marker file (explains what archive contains)
2. Move the 22 files (use shell `mv` or write_file equivalent — agent mode has shell access)
3. Update the 4 links in `docs/README.md` (lines 68, 70)
4. Update the 4 links in `docs/INDEX.md` (lines 46–49)
5. Update the 1 link in `docs/knowledge-base/concepts/token-optimization.md` (line 293)
6. Run `python3 scripts/check_savings_claims.py`, `python3 scripts/check_status_consistency.py`, and `python3 scripts/generate_api_docs.py --check`

**Relevant Context**
- `docs/archive/` does not yet exist — create it
- All BOOK_* and PHASE* files already carry retraction/deprecation banners; they are point-in-time records
- `docs/project-management/` already exists for older planning docs; `docs/archive/` is the right home for the BOOK series and phase milestones since they are historical, not ongoing planning
- The `check_savings_claims.py` gate correctly handles archived files via banner exception — no change to the gate needed
- `docs/ARCHITECTURE.md` stays in root — it is the authoritative current architecture doc (not part of BOOK series)

---

## Sub-Task 4 — Run full gate suite and confirm clean

**Status:** `[ ] pending`

**Intent**  
After all three prior sub-tasks, verify the repository is in a clean, fully consistent state.

**Todo List**
1. `python3 scripts/check_status_consistency.py`
2. `python3 scripts/check_savings_claims.py`
3. `python3 scripts/check_value_homes.py`
4. `python3 scripts/check_community_health.py`
5. `python3 scripts/check_layering.py src`
6. `.venv/bin/python scripts/generate_api_docs.py --check`
7. `.venv/bin/ruff check src/ scripts/ tests/`
8. `.venv/bin/python -m pytest tests/ -x -q --no-header --tb=short` (fast smoke pass)
9. Report any failures and fix them before marking complete
