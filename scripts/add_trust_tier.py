#!/usr/bin/env python3
"""Migration script: add trust_tier to KB documents that are missing it.

Scans all *.md files under docs/knowledge-base/, detects files whose YAML
frontmatter lacks a ``trust_tier:`` field, and inserts
``trust_tier: generated`` (conservative default) after the ``status:`` line
(or at the end of the frontmatter block if no status line is present).

This is a one-time migration to bring existing documents into the trust-tier
model introduced in Sub-Task 7 (ATK-MEM-02 remediation).

Usage::

    python scripts/add_trust_tier.py [--dry-run] [--kb-path PATH]

Options:
    --dry-run    Print what would change without writing files.
    --kb-path    Path to the KB root (default: docs/knowledge-base).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KB = REPO_ROOT / "docs" / "knowledge-base"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TRUST_TIER_RE = re.compile(r"^trust_tier:", re.MULTILINE)


def _insert_trust_tier(text: str) -> str | None:
    """Return text with trust_tier inserted, or None if already present."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None  # no frontmatter — cannot insert safely

    fm_block = m.group(1)
    if _TRUST_TIER_RE.search(fm_block):
        return None  # already has trust_tier

    # Find insertion point: after status: line if present, else before closing ---
    lines = fm_block.split("\n")
    insert_after = None
    for i, line in enumerate(lines):
        if line.strip().startswith("status:"):
            insert_after = i
            break

    if insert_after is not None:
        lines.insert(insert_after + 1, "trust_tier: generated")
    else:
        lines.append("trust_tier: generated")

    new_fm = "\n".join(lines)
    # Rebuild the document: replace the old frontmatter block
    end = m.end()
    return f"---\n{new_fm}\n---\n{text[end:]}"


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    dry_run = "--dry-run" in args
    kb_path = DEFAULT_KB
    if "--kb-path" in args:
        idx = args.index("--kb-path")
        if idx + 1 < len(args):
            kb_path = Path(args[idx + 1])

    if not kb_path.exists():
        print(f"ERROR: KB path not found: {kb_path}", file=sys.stderr)
        return 1

    modified = 0
    skipped = 0
    total = 0

    for md_file in sorted(kb_path.rglob("*.md")):
        total += 1
        try:
            original = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  SKIP {md_file}: read error: {e}")
            skipped += 1
            continue

        updated = _insert_trust_tier(original)
        if updated is None:
            continue  # already has trust_tier or no frontmatter

        rel = md_file.relative_to(REPO_ROOT)
        if dry_run:
            print(f"  DRY-RUN: would add trust_tier: generated to {rel}")
        else:
            md_file.write_text(updated, encoding="utf-8")
            print(f"  ADDED trust_tier: generated to {rel}")
        modified += 1

    print(
        f"\nScanned {total} files: {modified} updated"
        + (" (dry run — no files written)" if dry_run else "")
        + f", {skipped} skipped."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
