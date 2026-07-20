#!/usr/bin/env python3
"""MEM-10: content-hash delta of KB research docs (replaces the mtime ``-newer`` scan).

``mnemox-lessons.sh`` lists "New Analysis Reports Filed" since the previous run. It
used ``find -newer .mnemox-last-run``, but **mtime is unreliable**: ``git checkout``,
``git clone``, ``cp``, and ``touch`` all reset mtimes, so unchanged files get
re-listed and genuinely new content can be missed. This computes the delta by
**content hash** against a manifest — a doc is "new/changed" iff its sha256 differs
from (or is absent in) the manifest — which is invariant under mtime churn.

Manifest format: one ``<sha256>  <path>`` line per ``*.md`` (like ``sha256sum``).

Usage::

    mnemox_doc_delta.py <research_dir> <manifest_path> [--update]

Prints one markdown bullet per new/changed ``*.md`` (sorted), or a "(none …)" line
if empty. With ``--update`` it rewrites the manifest to the current state AFTER
printing the delta, so the next run compares against this run.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(manifest: Path) -> dict[str, str]:
    """Parse a ``<sha256>  <path>`` manifest into ``{path: sha}`` (empty if absent)."""
    out: dict[str, str] = {}
    if not manifest.exists():
        return out
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)  # sha, then the (possibly spaced) path
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


def compute_delta(research_dir: Path, manifest: Path) -> list[str]:
    """Return sorted paths of ``*.md`` whose content hash is new or changed vs *manifest*.

    Purely content-driven: a file whose mtime moved but whose bytes are identical is
    NOT in the delta (the property the mtime scan got wrong).
    """
    prev = read_manifest(manifest)
    changed: list[str] = []
    for md in sorted(research_dir.rglob("*.md")):
        key = str(md)
        if prev.get(key) != _hash(md):
            changed.append(key)
    return changed


def manifest_text(research_dir: Path) -> str:
    """Serialize the current hash state of *research_dir* as manifest text."""
    lines = [f"{_hash(md)}  {md}" for md in sorted(research_dir.rglob("*.md"))]
    return "\n".join(lines) + ("\n" if lines else "")


def write_manifest(research_dir: Path, manifest: Path) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(manifest_text(research_dir), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    update = "--update" in args
    positional = [a for a in args if a != "--update"]
    if len(positional) < 2:
        print(
            "usage: mnemox_doc_delta.py <research_dir> <manifest_path> [--update]",
            file=sys.stderr,
        )
        return 2

    research_dir, manifest = Path(positional[0]), Path(positional[1])
    if not research_dir.is_dir():
        print("(no research directory yet)")
        return 0

    delta = compute_delta(research_dir, manifest)
    if delta:
        for rel in delta:
            print(f"- `{rel}`")
    else:
        print("(no new or changed analysis reports since last run)")

    if update:
        write_manifest(research_dir, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
