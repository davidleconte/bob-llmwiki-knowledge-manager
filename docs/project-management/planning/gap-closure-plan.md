# Gap Closure Plan — A (3.89) → A+ Trajectory

**Goal:** Close or document the four tracked open items to improve grade integrity and set up for PR.
**Scope:** Documentation corrections, one dead-field removal, one threat-model addendum, one PR.
**Gates must stay green throughout every sub-task.**

---

## Sub-task 1 — Wire `OptimizerConfig.strategies` through to the optimizer (Gap B)

**Intent:**
`OptimizerConfig.strategies` (`src/config/schema.py:51`) is declared, validated by
`ConfigValidator` (`src/config/validator.py:134-144`), and tested by ~12 tests — but is
never passed by `from_config()` (`prompt_optimizer.py:137-162`) to the constructor, which
has no `strategies` parameter. The optimizer always runs three hardcoded calls at lines
202–204 regardless of config. The field is not dead in the config/validator layer; the
only broken link is the last mile: config → constructor → runtime behaviour.

The fix is to wire, not remove: add a `strategies` parameter to `PromptOptimizer.__init__`,
pass it through `from_config()` and `build_optimizer()`, and make the three method calls
at lines 202–204 conditional on whether their name appears in the `strategies` list.
The mapping is: `"remove_whitespace"` → `_normalize_whitespace`, `"compress_repeated"` →
`_remove_redundancy`, `"remove_comments"` / `"shorten_names"` → `_compress_content`.

**Expected Outcomes:**
- `PromptOptimizer.__init__` accepts a `strategies: list[str]` parameter (default: all three,
  matching `OptimizerConfig.__post_init__`'s default list).
- `from_config()` passes `config.strategies` through.
- `build_optimizer()` in `src/factory.py` passes `config.strategies` through.
- The three strategy calls at lines 202–204 are conditional on the strategies list.
- The e2e test `test_optimizer_strategies_from_config` passes (currently it only asserts the
  config field is set; a follow-up assertion can verify the optimizer skips disabled strategies).
- All existing tests pass unchanged.
- `STATUS.md:12` roadmap note for Gap B updated to "Closed".

**Todo List:**
1. Read `src/optimizer/prompt_optimizer.py:44-56` (constructor signature) and lines 200–210
   (strategy calls) in full.
2. Add `strategies: Optional[List[str]] = None` parameter to `PromptOptimizer.__init__`;
   store as `self.strategies`; default to `["remove_whitespace", "compress_repeated"]` when
   `None` (matching the config default).
3. Wrap the three calls at lines 202–204 with guards:
   - `if "remove_whitespace" in self.strategies:`
   - `if "compress_repeated" in self.strategies:`
   - `if "remove_comments" in self.strategies or "shorten_names" in self.strategies:`
4. Update `from_config()` (`prompt_optimizer.py:154-162`) to pass `strategies=config.strategies`.
5. Update `build_optimizer()` (`src/factory.py:58-60`) to pass `strategies=config.strategies`
   in the `PromptOptimizer.from_config(...)` call.
6. Update `STATUS.md:12` roadmap entry to mark Gap B closed.
7. Run: `ruff check src/ scripts/ tests/` — must pass.
8. Run: `uv run pytest tests/ -q --tb=short` — must pass.
9. Run all gate scripts — must pass.

**Relevant Context:**
- `src/config/schema.py:38-56` — `OptimizerConfig` with `strategies` field + `__post_init__`
- `src/config/validator.py:134-144` — strategy validation (4 allowed names)
- `src/optimizer/prompt_optimizer.py:44-56` — constructor (no `strategies` param)
- `src/optimizer/prompt_optimizer.py:137-162` — `from_config()` (does not pass `strategies`)
- `src/optimizer/prompt_optimizer.py:200-204` — hardcoded strategy calls
- `src/optimizer/prompt_optimizer.py:265-360` — `_normalize_whitespace`, `_remove_redundancy`,
  `_compress_content` method implementations
- `src/factory.py:42-60` — `build_optimizer()`
- `tests/e2e/test_optimizer_config_integration.py:88-98` — strategy config test (currently
  only asserts the config field, not optimizer behaviour)

**Status:** [x] closed — strategies wired through `from_config()` and `build_optimizer()`; three method calls conditional; tests pass.

---

## Sub-task 2 — Name the TOCTOU window in THREAT_MODEL.md residual register (Gap G)

**Intent:**  
The threat model's residual risks section (lines 135-157) has three entries. None names the
classic TOCTOU (time-of-check / time-of-use) window that exists in `src/tools/`:
`resolve_within()` validates the path, then the caller checks existence, then reads the file —
three separate steps. An attacker with write access to the directory could replace the symlink
between validation and open. This is explicitly a LOW residual in the local-CLI context
(operator owns the filesystem) but a Tier-1 threat model must name it explicitly.  
This is a **documentation-only** change (no code changes).

**Expected Outcomes:**
- `docs/security/threat-model.md` residual register gains a 4th entry explicitly named
  "TOCTOU: check-then-use window in path validation".
- The entry names the exact window (`resolve_within` → `.exists()` → file open), gives the
  severity in local-CLI context (Low — operator owns the filesystem), and notes the hosted
  escalation risk.
- `STATUS.md:12` roadmap note for Gap G updated to "Closed".

**Todo List:**
1. Read `src/tools/safe_paths.py` in full to confirm the exact window.
2. Read `src/tools/batch_file_reader.py`, `src/tools/component_analyzer.py`,
   `src/tools/kb_query.py` to identify where the three-step pattern (validate → exists →
   open) occurs.
3. Append a 4th residual entry to `docs/security/threat-model.md §Residual risks`,
   citing the specific file:line for each step.
4. Update `STATUS.md:12` roadmap entry to mark Gap G closed.
5. Run: `python3 scripts/check_status_consistency.py` — must pass.
6. Run all gate scripts to confirm green.

**Relevant Context:**
- `docs/security/threat-model.md:135-158` — residual risks section (3 current entries)
- `src/tools/safe_paths.py` — `resolve_within()` implementation
- `src/tools/batch_file_reader.py` — pattern: `resolve_within` → `exists()` → `open()`

**Status:** [x] closed — TOCTOU residual-4 named in THREAT_MODEL.md; TOCTOU window subsequently narrowed from 3-step to 2-step (G1 in a-plus-plan.md).

---

## Sub-task 3 — Update architecture-audit post-remediation note (Dim 4 fix)

**Intent:**  
`docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md` (frozen snapshot, lines
393-401) has a post-remediation note that says:
> "Dimension 4 is held at B+ because `ARCHITECTURE.md:74` still incorrectly states
> `src/tools/` is 'excluded from coverage gates'"

That claim is now **false** — `docs/architecture/architecture.md:73-74` currently reads:
> "Included in the coverage and type gates with a per-package floor of 85%"

The exclusion claim was corrected (last session). The frozen audit note needs an addendum so
the snapshot remains accurate as a historical record (without editing its findings, which are
frozen as-of the original audit).

**Expected Outcomes:**
- The architecture-audit doc gains a brief second addendum (dated 2026-07-14+) noting that
  `ARCHITECTURE.md:74` was subsequently corrected, Dimension 4 is now A, and the weighted
  overall moves from ~A− (3.65) to ~A (3.75+).
- The note is clearly marked as a **post-snapshot correction note**, not a rewrite of the
  frozen findings.
- No gate scripts are affected (this is a research-doc update only).

**Todo List:**
1. Read `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md:370-415` to
   see the exact existing post-remediation note structure.
2. Read `docs/architecture/architecture.md:70-78` to confirm line 74's current content.
3. Append a second addendum block (clearly labelled with a new date/phase) below the
   existing post-remediation note, noting: (a) `ARCHITECTURE.md:74` was corrected, (b)
   Dimension 4 moves from B+ to A, (c) new estimated weighted score ~3.75 (A).
4. No gate scripts need re-running (research doc only).

**Relevant Context:**
- `docs/knowledge-base/research/architecture-audit-mece-2026-07-14.md:393-401` — the outdated note
- `docs/architecture/architecture.md:70-78` — the corrected line

**Status:** [x] closed — ARCHITECTURE.md:74 corrected; post-remediation addendum added to architecture-audit doc.

---

## Sub-task 4 — Commit all changes and open PR

**Intent:**  
The `fix-multilevel-cache-race` branch has a large number of uncommitted changes from the
prior session (see git status in context prompt). Once sub-tasks 1–3 are complete and gates
are green, everything should be committed with well-scoped messages and a PR opened.

**Expected Outcomes:**
- All modified/new/deleted files are committed with logical, grouped commit messages.
- PR is opened on `fix-multilevel-cache-race` against the default base branch.
- PR description summarises the work: documentation remediation, gap closures (B, G),
  architecture doc fixes, session activation tooling, README replacement.

**Todo List:**
1. After sub-tasks 1–3 are complete, run all gate scripts one final time.
2. Stage and commit in logical groups (e.g., one commit per: docs/, src/ schema fix,
   scripts/, test changes).
3. Use the `create_pr_workflow` workflow to generate and submit the PR.

**Relevant Context:**
- Git status from context prompt lists all modified/new/deleted files.
- Use `start_workflow` with `create_pr_workflow` for PR creation.

**Status:** [x] closed — committed and pushed as part of this session.
