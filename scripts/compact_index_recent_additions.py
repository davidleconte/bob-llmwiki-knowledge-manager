#!/usr/bin/env python3
"""D1 / MEM-08: bound the KB index's "Recent Additions" without orphaning docs.

``docs/knowledge-base/index.md`` is the auto-loaded cold-start map. Its
``## Recent Additions`` section grew unbounded (one prepended line per mnemox run)
and double-listed every doc already in ``## All Documents``. This trims it to the
``keep`` most-recent entries.

Safety: a doc referenced ONLY in Recent Additions would be orphaned by a naive trim
(``validate-kb.sh`` flags docs absent from ``index.md``). So before trimming, any
dropped entry whose target is not referenced elsewhere in the file is preserved under
a ``### Reconciled from Recent Additions`` heading in ``## All Documents`` — keeping
the reference, dropping only the duplication.

Pure ``compact(text, keep)`` for testability; ``main`` applies it to a file in place.

Usage::

    compact_index_recent_additions.py <index.md> [--keep N] [--check]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_MD_LINK = re.compile(r"\]\(([^)]+)\)")
_RECONCILE_HEADING = "### Reconciled from Recent Additions"


def _entry_paths(line: str) -> list[str]:
    """Markdown link targets on a line, fragment- and ./-normalised, *.md only."""
    out = []
    for m in _MD_LINK.finditer(line):
        p = m.group(1).split("#", 1)[0].strip().lstrip("./")
        if p.endswith(".md"):
            out.append(p)
    return out


def compact(text: str, keep: int = 10) -> str:
    """Return *text* with ``## Recent Additions`` trimmed to *keep* entries.

    Dropped entries whose target is not referenced anywhere else in the document are
    appended (verbatim) under a reconcile heading in ``## All Documents`` so no doc
    loses its only index reference. Idempotent once already compact.
    """
    lines = text.splitlines()

    def _heading_index(title: str) -> int:
        for i, ln in enumerate(lines):
            if ln.strip() == title:
                return i
        return -1

    ra = _heading_index("## Recent Additions")
    if ra == -1:
        return text  # nothing to do

    # Recent Additions runs until the next "## " heading (or EOF).
    ra_end = len(lines)
    for i in range(ra + 1, len(lines)):
        if lines[i].startswith("## "):
            ra_end = i
            break

    body = lines[ra + 1 : ra_end]
    entries = [ln for ln in body if ln.strip().startswith("- ")]

    kept = entries[:keep]
    dropped = entries[keep:]

    # A dropped entry is safe to remove iff its target is referenced elsewhere.
    rest = "\n".join(lines[:ra] + lines[ra_end:])
    orphaned = [ln for ln in dropped if any(p not in rest for p in _entry_paths(ln))]

    # Rebuild the Recent Additions section: heading, the kept entries, a trailing blank.
    new_ra = [lines[ra]] + kept + [""]
    new_lines = lines[:ra] + new_ra + lines[ra_end:]

    # Preserve orphan-risk entries under a reconcile heading in All Documents.
    if orphaned:
        text2 = "\n".join(new_lines)
        lines2 = text2.splitlines()
        # Insert before "## Usage" if present, else before the next top-level heading
        # after "## All Documents", else at end.
        insert_at = len(lines2)
        ad = next((i for i, ln in enumerate(lines2) if ln.strip() == "## All Documents"), -1)
        if ad != -1:
            insert_at = next(
                (i for i in range(ad + 1, len(lines2)) if lines2[i].strip() == "## Usage"),
                len(lines2),
            )
        existing = next((i for i, ln in enumerate(lines2) if ln.strip() == _RECONCILE_HEADING), -1)
        if existing != -1:
            block = orphaned + [""]
            lines2[existing + 1 : existing + 1] = block
        else:
            block = ["", _RECONCILE_HEADING, ""] + orphaned + [""]
            lines2[insert_at:insert_at] = block
        new_lines = lines2

    return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    check = "--check" in args
    args = [a for a in args if a != "--check"]
    keep = 10
    if "--keep" in args:
        i = args.index("--keep")
        keep = int(args[i + 1])
        del args[i : i + 2]
    if not args:
        print("usage: compact_index_recent_additions.py <index.md> [--keep N] [--check]")
        return 2

    path = Path(args[0])
    original = path.read_text(encoding="utf-8")
    compacted = compact(original, keep=keep)
    if check:
        if compacted != original:
            print(f"❌ {path} Recent Additions exceeds {keep} entries (run without --check to fix)")
            return 1
        print(f"✅ {path} Recent Additions is compact (≤{keep})")
        return 0
    path.write_text(compacted, encoding="utf-8")
    print(f"✅ compacted {path} Recent Additions to ≤{keep} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
