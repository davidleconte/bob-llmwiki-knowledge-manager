# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T18:16:22Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
45690b9 feat: root-file lint, --quick/--full docs, sha256 portability note
5aa8067 docs(kb): synthesise mnemox --quick lessons 2026-07-18
8fdc2df mnemox: update KB 2026-07-18
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

### 1. Lint checks belong in the tool that already runs at the gate

The root-file hygiene check was added directly to `scripts/validate-kb.sh`
(Step 5 of every `mnemox` run) rather than a separate script. This is correct:
one gate, one call, one output block. The pattern generalises — any new static
check on repo structure belongs in `validate-kb.sh`, not as a standalone linter
that can be forgotten.

### 2. Allowlists must cover GitHub Community Health Files from the start

The initial allowlist (`README.md AGENTS.md STATUS.md CHANGELOG.md INTEGRATIONS.md`)
was immediately expanded to include `CODE_OF_CONDUCT.md CONTRIBUTING.md
GOVERNANCE.md SECURITY.md SUPPORT.md` because those 5 files are required at the
root by GitHub's community health framework. Any repo-hygiene allowlist must
account for the full set of GitHub-surfaced conventional root files, not just the
project's own conventions.

### 3. Documentation of operational flags closes the "how do I use this?" gap

The `--quick` / `--full` decision table in `README.md §5` converts an implicit
convention (known only to the author) into an explicit, scannable contract visible
to any new user or judge. The pattern: whenever a tool has multiple operating
modes, the README should show the decision rule as a table, not bury it in
`--help` output or skill docs.

### 4. "Portability concern" resolved without code change

The lessons note from the previous run flagged `shasum -a 256` vs `sha256sum`
portability. Investigation confirmed the SHA256 is computed entirely via Python
`hashlib` — no shell command involved. The fix was a one-line comment confirming
the design. Lesson: before writing a portability shim, verify whether the concern
is even applicable to the actual implementation.

### 5. Three `mnemox --quick` runs in one session produce clean, additive output

Each quick run rewrites the same dated note (`mnemox-update-2026-07-18.md`)
rather than creating duplicate files. The frontmatter step correctly adds
missing headers to the rewritten note. The graph rebuild is idempotent (same
node/edge counts on identical KB state). The git commit fires only when there
is a diff — the "nothing to commit" case is handled gracefully (warns, continues).
The session demonstrated that `--quick` is safe to run repeatedly without
accumulating noise.

## Conclusions

### Recommendations

1. **Gate pattern is established** — add all future repo-structure checks
   (e.g., orphaned KB docs not in INDEX.md, missing frontmatter fields) as
   new sections in `validate-kb.sh`, following the existing `🏠`, `🔗`, `📊`
   section pattern.
2. **Expand the decision-table pattern to `mnemox --full`** — README §5 now
   shows the two speeds; consider adding a "what the 7-phase analysis checks"
   one-liner so users know what they gain from `--full` vs `--quick`.
3. **Allowlist maintenance is a low-frequency, high-value task** — review the
   root-file allowlist whenever adding a new top-level conventional file; it
   takes 30 seconds and prevents false-positive lint noise.

### Next Steps

- [ ] Add orphan check to `validate-kb.sh`: warn on KB docs not referenced in `index.md`
- [ ] Add `--full` one-liner summary to README §5 (what the 7-phase analysis produces)
- [ ] Consider adding frontmatter completeness check to `validate-kb.sh` (required fields: title, category, tags, created, updated, status)

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
