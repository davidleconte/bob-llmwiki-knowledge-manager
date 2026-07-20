"""Cold-start context map — the files a fresh session auto-loads (D1 / MEM-08).

A new session loads a fixed set of files verbatim to orient itself. ``.bob/settings.json``
(``context.fileName``) is the single source of truth for that list — today ``AGENTS.md``
plus the KB index. "A system built to save tokens shouldn't spend five figures mapping
itself," so this module totals the map's token cost via the shared
:class:`~src.optimizer.token_counter.TokenCounter`. Both ``bob-optimize kb-status``
(visibility) and the CI budget gate (regression) call it, so they measure the same thing
from one home rather than drifting apart.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.optimizer.token_counter import TokenCounter

# Fallback if .bob/settings.json is missing/unreadable — matches the committed default.
_DEFAULT_COLD_START_FILES = ("AGENTS.md", "docs/knowledge-base/index.md")

# Regression ceiling for the auto-loaded cold-start map, in tokens. This is a
# bloat-regression gate, NOT the wave-3 spec's aspirational "< 3k": that target is
# infeasible because the KB's own 100+-doc "All Documents" catalog listing alone far
# exceeds 3k, and gutting it to hit a number would be gaming the metric. After the
# Recent-Additions trim (D1/MEM-08) the map is ~11.3k tokens (AGENTS.md + index.md);
# this ceiling (~24% headroom) catches gross regression — a Recent-Additions regrowth
# or non-catalog bloat — while tolerating normal per-doc catalog growth. The ≤10
# Recent-Additions bound is enforced separately (compact_index_recent_additions.py
# --check). Revisit this number if the KB grows substantially.
COLD_START_BUDGET_TOKENS = 14000


def cold_start_files(repo_root: Path) -> list[Path]:
    """Return the existing files auto-loaded at cold start, per ``.bob/settings.json``.

    Reads ``context.fileName`` so the map definition has a single home. Non-existent
    entries are skipped (the caller measures what is actually loaded).
    """
    settings = repo_root / ".bob" / "settings.json"
    names: list[str] = []
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            names = list(data.get("context", {}).get("fileName", []) or [])
        except (json.JSONDecodeError, OSError):
            names = []
    if not names:
        names = list(_DEFAULT_COLD_START_FILES)
    return [repo_root / n for n in names if (repo_root / n).is_file()]


def cold_start_map_tokens(repo_root: Path) -> int:
    """Total token cost of the auto-loaded cold-start map (0 if no files present)."""
    counter = TokenCounter()
    total = 0
    for f in cold_start_files(repo_root):
        total += counter.count_tokens(f.read_text(encoding="utf-8"))
    return total
