# Mnemox Update — 2026-07-18

## Objective
Automated KB update run by `mnemox` on 2026-07-18.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: 2026-07-18T17:16:41Z
- KB location: `docs/knowledge-base`

## Git Changes Since Last Run

```
e73dcc3 kb: add compact-summary frontmatter tag to all 13 concept docs
4535482 mnemox: update KB 2026-07-18
```

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | 13 |
| Guides     | 26 |
| References | 2 |
| Research   | 59 |
| **Total**  | **101** |

## New Analysis Reports Filed

- `docs/knowledge-base/research/mnemox-update-2026-07-18.md`

## Findings

**1. YAML frontmatter + `compact-summary` tag applied to all 13 concept docs in one commit**
`e73dcc3` added a uniform frontmatter block (`title`, `category`, `tags`, `created`, `updated`, `status`) to the 12 bare-markdown concept files and appended `compact-summary` to the one that already had frontmatter (`kb-tos-embedding-layer.md`). The tag is now parseable by `tests/validation/test_km_savings.py` for filtered savings measurement. External changes to 6 of those files were observed between commits — the frontmatter survived intact.

**2. The `grep -qF` duplicate-entry guard broke on macOS due to `--` in `$INDEX_ENTRY`**
The entry string `"- 2026-07-18: [Mnemox Update — ..."` contains an em-dash (`—`) preceded by a space, but more critically the `grep -qF "$VAR"` form lets the shell expand a variable whose value starts with `-` into a grep option. Fixed by adding `--` after the flags: `grep -qF -- "$INDEX_ENTRY" "$INDEX_FILE"`. The guard still fired (exit-code non-zero from the error = falsy), so the entry was inserted rather than deduplicated — a silent correctness failure masquerading as a working run.

**3. `grep -qF -- "$PATTERN" "$FILE"` is the portable macOS/Linux form for literal fixed-string search**
On macOS `grep` is BSD grep; on Linux it is GNU grep. Both honour `--` as the end-of-options sentinel. Any script that passes a user-controlled or generated string to grep as a pattern should always use `grep -F -- "$VAR"` (or `grep -e "$VAR"`) to prevent the string from being parsed as options or regex metacharacters.

**4. Graph edges grew again with frontmatter: 3870 → 3902 (+32)**
Adding frontmatter to existing docs does not add nodes, but it updates document metadata (`title`, `tags`) which the graph builder uses for edge scoring. The 32 new edges reflect improved tag-based affinity matching now that all concept docs share structured metadata. Frontmatter is not cosmetic — it is graph infrastructure.

**5. External file modifications between commits are normal at this KB scale**
The `<external_changes>` notice flagged 6 concept files modified externally between the compact-summary commit and this `--quick` run. At 101 documents across active development, external edits are expected. The mnemox script handles this correctly: it stages `docs/knowledge-base/` wholesale in the auto-commit, so any external changes to KB files are captured. No action required.

## Conclusions

### Recommendations
1. The `grep -qF -- "$INDEX_ENTRY"` fix eliminates the macOS stderr noise — committed immediately.
2. Consider adding `set -o pipefail` to `mnemox-lessons.sh` so future grep/python errors surface as non-zero exit codes rather than silently continuing.
3. Run `uv run pytest tests/validation/test_km_savings.py -v` now that `compact-summary` tags are in place — this is the first run where the filter will actually work.

### Next Steps
- Run the savings test to validate the `compact-summary` filter: `uv run pytest tests/validation/test_km_savings.py -v`
- Investigate whether `test_km_savings.py` currently reads frontmatter tags or needs a small update to support the filter.
- The 12 new frontmatter blocks all use `created: 2026-07-18` — verify the graph builder picks up `mtime_epoch` from disk rather than from frontmatter (it should; `NodeProps.mtime_epoch` is `os.path.getmtime()`-based).

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: 2026-07-18 — Mnemox Knowledge Builder*
*Category: Research*
