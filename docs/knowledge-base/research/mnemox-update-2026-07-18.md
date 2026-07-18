# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T17:03:59Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
ff7f439 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 7 |
| Guides     | 26 |
| References | 2 |
| Research   | 59 |
| **Total**  | **95** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`

## Findings

**1. `README.md` emoji consistency — `📚` → `🧠` must be tracked as a single source of truth**
The mode name `🧠 Mnemox Knowledge Builder` was set in `.bob/custom_modes.yaml`, but `README.md §3a` still used `📚` for the same mode, and `tests/test_mode_config.py` asserted `📚`. All three diverged independently. Lesson: the mode emoji lives in one place (`customModes[slug].name`); every prose reference and every test assertion must derive from it. When the name changes, a grep for the old emoji across `README.md`, `AGENTS.md`, and `tests/` is the minimum required sweep.

**2. `INDEX.md → index.md` rename required a 5-file sweep beyond the scripts**
The kb index rename touched: `scripts/validate-kb.sh`, `scripts/init-project.sh`, `config/settings.json`, `tests/test_workflows.py`, and prose in `README.md` (7 occurrences). The `.bob/settings.json` `fileName` array and `config/custom_modes.yaml` inline instructions also held the old name. A rename of this file should always be paired with `grep -r "INDEX\.md"` across all non-excluded directories before committing.

**3. Test assertions on UI strings are brittle — pin to slug, not display name**
`test_mode_config.py` broke because it asserted on the emoji character in the display name, which is cosmetic and subject to change. More robust: assert on `slug` (already done) and that `name` is non-empty. If the emoji must be tested, extract it from the YAML rather than hardcoding it in the test.

**4. Kebab-case rename of 107 files + reference fix executed safely in one atomic pass**
The rename-then-fix-references pattern worked cleanly: (1) dry-run to preview all renames, (2) execute renames, (3) sed-based reference replacement across key files, (4) find-then-fix inside renamed docs, (5) test run as gate. The session also confirmed `.claude/`, `.bob/`, `.venv/`, and `.github/` are hard exclusion zones — references inside `.bob/custom_modes.yaml` to `ARCHITECTURE.md` are *content instructions to agents*, not file paths, and must not be rewritten.

**5. `scripts/mnemox.sh --quick` still echoes `✅ INDEX.md updated` (uppercase) in its output**
The script message on stdout says `INDEX.md` rather than `index.md`. This is cosmetic but will confuse future operators. The output string should be updated to match the renamed file.

## Conclusions

### Recommendations
1. Fix the cosmetic `INDEX.md` → `index.md` string in `scripts/mnemox-lessons.sh` (or whichever script emits the `✅ INDEX.md updated` stdout message).
2. Refactor `test_mode_config.py` emoji assertion to be derived from the YAML rather than hardcoded — or accept the current pin to `🧠` and document it as intentional.
3. Add a `grep -r "INDEX\.md"` pre-commit check (or CI lint step) so future index renames surface all references automatically.

### Next Steps
- Fix the `INDEX.md` stdout string in the mnemox lesson script (5-minute change).
- Consider promoting the kebab-case rename lessons into a durable **concept** document (`docs/knowledge-base/concepts/file-naming-conventions.md`) so future contributors find the rationale without reading git history.
- Thin the research backlog: 59 research notes, 7 concepts — at least 3–5 research findings are stable enough to graduate into concept documents.

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
