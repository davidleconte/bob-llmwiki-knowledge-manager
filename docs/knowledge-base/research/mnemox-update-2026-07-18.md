# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T18:04:39Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
d91ae80 fix: sync-skill-templates idempotency + --help text + lessons
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 13 |
| Guides     | 26 |
| References | 4 |
| Research   | 59 |
| **Total**  | **103** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`

## Findings

### 1. Idempotency guard pattern for shell template sync

`scripts/sync-skill-templates.sh` was patched to compute a SHA256 digest of the
current SKILL.md block before comparing it against the template. It now exits 3
(`Already current`) instead of re-writing identical content. This eliminates a
class of spurious `git commit` entries on every `mnemox` run — whenever templates
haven't changed, Step 3 produces no diff and no commit noise. The pattern
(hash → compare → skip-or-write) is the correct idempotency primitive for any
script that injects file blocks.

### 2. `set +e` / `set -e` bracketing around subprocess calls that use non-zero exit conventions

Python subprocesses called from a `set -euo pipefail` script can exit non-zero
to signal "no-op" (exit 2 = no template found, exit 3 = already current). Without
`set +e` bracketing around such calls, the outer script aborts on any non-zero
return — even a successful "nothing to do". The fix: `set +e` before the
subprocess call, capture `$?`, `set -e` immediately after, then branch on the
captured code. Apply this pattern to every place mnemox scripts call external
programs that use exit-code signalling rather than stdout.

### 3. Plan files belong in `docs/project-management/plans/`, not the repo root

Two plan files (`readme-challenge-framing-plan.md`, `mnemox-command-plan.md`)
were found at the repo root this session and relocated. The root should only hold
conventional top-level documents: `README.md`, `AGENTS.md`, `STATUS.md`,
`CHANGELOG.md`, `INTEGRATIONS.md`. Any file whose name includes `plan`, `roadmap`,
or similar should default to `docs/project-management/plans/`.

### 4. `mnemox --quick` is the right daily driver

The full update path (7-phase analysis + lessons + graph + commit) is expensive.
`--quick` skips the analysis and runs only lessons capture, graph rebuild, and
git commit — completing in seconds. Use `--quick` after code-only changes or
housekeeping; reserve `--full` for sessions where new source files, schemas, or
architectural decisions were introduced that warrant a fresh analysis snapshot.

## Conclusions

### Recommendations

1. **Extend the SHA256 idempotency guard** to any other shell script that injects
   blocks into YAML or Markdown files (e.g., `init-project.sh` template writing).
2. **Add a root-file hygiene check** to `scripts/validate-kb.sh` or a new
   `scripts/lint-root.sh` that warns when any `*.md` file other than the five
   conventional root docs is found at the project root.
3. **Document the `--quick` vs `--full` decision rule** in `README.md §5` so
   users know which flag to reach for without consulting SKILL.md.

### Next Steps

- [ ] Implement root-file lint check (see Recommendation 2)
- [ ] Update `README.md §5` with `--quick` / `--full` usage note
- [ ] Verify SHA256 idempotency guard works correctly under macOS `shasum` and
      Linux `sha256sum` (command name differs — use `shasum -a 256` as the portable form)

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
