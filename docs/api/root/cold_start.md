# cold_start

Cold-start context map — the files a fresh session auto-loads (D1 / MEM-08).

A new session loads a fixed set of files verbatim to orient itself. ``.bob/settings.json``
(``context.fileName``) is the single source of truth for that list — today ``AGENTS.md``
plus the KB index. "A system built to save tokens shouldn't spend five figures mapping
itself," so this module totals the map's token cost via the shared
:class:`~src.optimizer.token_counter.TokenCounter`. Both ``bob-optimize kb-status``
(visibility) and the CI budget gate (regression) call it, so they measure the same thing
from one home rather than drifting apart.

## Constants

- `_DEFAULT_COLD_START_FILES`
- `COLD_START_BUDGET_TOKENS`

## Functions

### `cold_start_files(repo_root: Path) -> list[Path]`

Return the existing files auto-loaded at cold start, per ``.bob/settings.json``.

Reads ``context.fileName`` so the map definition has a single home. Non-existent
entries are skipped (the caller measures what is actually loaded).


### `cold_start_map_tokens(repo_root: Path) -> int`

Total token cost of the auto-loaded cold-start map (0 if no files present).

