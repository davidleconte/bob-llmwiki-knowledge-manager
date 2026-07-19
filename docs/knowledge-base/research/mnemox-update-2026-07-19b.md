---
title: "Mnemox Update — 2026-07-19 (documentation sync)"
category: research
tags: [mnemox, lessons-learned, documentation, adversarial-audit, status]
created: 2026-07-19
updated: 2026-07-19
status: active
---

# Mnemox Update — 2026-07-19 (documentation sync)

## Objective

Documentation catch-up run (`mnemox --quick`) synchronising all project-facing
documents with the 2026-07-19 adversarial audit findings, new test packages,
and remediation plan.

## Background

- Session type: `mnemox --quick` (lessons + index + validate, no repo analysis)
- KB location: `docs/knowledge-base`
- Trigger: "adjust documentation based on latest changes"

## Changes Made This Session

### Files Updated

| File | Change |
|---|---|
| `STATUS.md` | As-of → 2026-07-19; grade qualified as self-assessed; counter-audit 2.9/5 cited; new test packages documented; 3 failing CI gates noted |
| `CHANGELOG.md` | `[Unreleased]` section added: 3 audit docs, 5 new test packages, adversarial-remediation-plan |
| `README.md §11` | Maturity table now dual-column (self-assessed vs independent); A+ qualified; trajectory updated |
| `README.md §12` | Security warning callout added for ATK-FS-01/02, ATK-MEM-01 |
| `README.md §13` | 2026-07-19 audit artefacts callout added |
| `docs/knowledge-base/index.md` | Grade correction banner added; doc count updated to 114; audit entries sharpened; `adversarial-remediation-plan.md` referenced in Recent Additions and Planning Artefacts section |
| `.bob/skills/knowledge-manager/SKILL.md` | `INDEX.md` → `index.md` (MEM-02 fix: case-sensitive filesystem compatibility) |

### KB Corpus State

| Category   | Documents |
|------------|-----------|
| Concepts   | 14 |
| Guides     | 27 |
| References | 4 |
| Research   | 69 (this note) |
| **Total**  | **115** |

## Findings

### 1. STATUS.md's grade table was the single largest credibility risk

The `STATUS.md` "A+ (4.30/4.30)" entry with no qualification was directly contradicted
by the counter-audit's 2.9/5 score filed in the same KB. A reader who opens STATUS.md
first, then counter-audit-2026-07-19-independent.md, sees an immediate contradiction.
**Every self-assessed grade must be flagged as such and the most recent independent
verdict cited alongside it.** The fix (adding "self-assessed, not independently
confirmed; counter-audit 2.9/5") is 12 words that transform a credibility liability
into a credibility asset.

### 2. CHANGELOG.md `[Unreleased]` is the right vehicle for untracked work

Five new test packages (`tests/security/`, `tests/gates/`, `tests/retrieval/`,
`tests/performance/test_dos_hardening.py`, `tests/optimizer/test_optimizer_integrity.py`)
exist on disk but are untracked in git. They cannot appear in a versioned release.
The `[Unreleased]` section in CHANGELOG.md is the correct home: it acknowledges the
work, describes it precisely, and explicitly tags it "pending merge" so reviewers
know the test count will change. **Untracked work-in-progress must be documented
in [Unreleased], not silently excluded.**

### 3. `INDEX.md` vs `index.md` is a silent cold-start failure on any case-sensitive system

`SKILL.md` referenced `INDEX.md` (uppercase) in its maintenance instructions, while
the actual file is `index.md`. On macOS (case-insensitive by default) this is invisible.
On Linux CI it silently fails the auto-load. Fixed to `index.md`. **Every
auto-load path must use the exact filename as it exists on disk.**
This is MEM-02 from the counter-audit — now closed in the SKILL.

### 4. `.docx` files in `docs/knowledge-base/research/` are a hygiene issue

The directory listing shows three `.docx` files alongside their `.md` counterparts:
`adversarial-audit-2026-07-19.docx`, `counter-audit-2026-07-19-independent.docx`,
`innovation-portfolio-2026-07-19.docx`. These are binary exports that should be
in `.gitignore` or `kb-export/`, not committed alongside the authoritative `.md`
source files. They bloat the repo, confuse the KB indexer, and duplicate content.
**Action required:** add `docs/knowledge-base/**/*.docx` to `.gitignore`.

### 5. The adversarial-remediation-plan.md root file needs a `.gitignore` entry or a KB copy

`adversarial-remediation-plan.md` sits at the repo root (H-2 hygiene class: root plan files).
It is currently untracked (`??` in git status). It should either be moved to
`docs/knowledge-base/guides/adversarial-remediation-plan.md` and committed, or left at
root and added to `.gitignore` if it is intentionally ephemeral. Given it is the gate
document for the independent re-grade, it should be committed and filed in the KB.
**Decision needed: move to KB tree or commit at root.**

## Conclusions

### Recommendations

1. **Immediate:** Add `docs/knowledge-base/**/*.docx` to `.gitignore` — binary exports
   do not belong in the authoritative KB tree.
2. **Before next commit:** Decide whether `adversarial-remediation-plan.md` stays at
   root (commit it as-is) or moves to `docs/knowledge-base/guides/` — either is fine,
   but it must be tracked.
3. **Next engineering session:** Implement compact cold-start index (innovation C2) —
   highest-ROI single action, directly cuts per-session cold-start tax.
4. **Ongoing:** Run `validate-kb.sh` before every KB commit — the subshell counter
   bug (MEM-04) is still open but the orphan detection works.

### Next Steps

- `echo 'docs/knowledge-base/**/*.docx' >> .gitignore` — remove .docx from tracking
- `git add adversarial-remediation-plan.md` — commit the remediation plan
- Run `uv run bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic`
- `git add docs/knowledge-base/ STATUS.md CHANGELOG.md README.md .bob/skills/ .gitignore`
- `git commit -m "docs: sync documentation with 2026-07-19 audit findings"`

## Related Documents

- [Knowledge Base Index](../index.md)
- [Adversarial Audit 2026-07-19](./adversarial-audit-2026-07-19.md)
- [Independent Counter-Audit 2026-07-19](./counter-audit-2026-07-19-independent.md)
- [Innovation Portfolio 2026-07-19](./innovation-portfolio-2026-07-19.md)
- [Mnemox Update 2026-07-19 (earlier)](./mnemox-update-2026-07-19.md)

---
*Generated: 2026-07-19 — Mnemox Knowledge Builder (mnemox --quick)*
*Category: Research*
