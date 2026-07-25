#!/usr/bin/env python3
"""Resolve every relative Markdown link against the **git index**, case-sensitively.

Why this gate exists (2026-07-25 full-project audit, finding class 1)
--------------------------------------------------------------------
A partial ``UPPER_SNAKE.md`` -> ``kebab-case.md`` rename was applied to files but not
to the references pointing at them, leaving ~103 broken references in live docs. None
of them were caught, for two compounding reasons:

1. **The only link checker covered 4% of the docs.** ``scripts/validate-kb.sh`` sets
   ``KB_DIR="docs/knowledge-base"`` and never leaves it, so ``README.md``,
   ``AGENTS.md``, ``docs/README.md``, ``docs/INDEX.md`` and the canonical architecture
   doc were all unchecked.
2. **macOS hides the bug.** ``core.ignorecase=true`` on APFS means
   ``docs/security/THREAT_MODEL.md`` resolves locally to ``threat-model.md``. GitHub's
   renderer and Linux CI are case-sensitive, so those links are 404s for every reader
   on github.com while looking fine to the author.

Consequently this gate resolves against ``git ls-files`` — the Linux ground truth —
and **never** against the local filesystem. A check that used ``Path.exists()`` would
reproduce the very blindness it is meant to remove.

It also flags the ``path:LINE`` citation form written inside a link target
(``](../config/custom_modes.yaml:180)``): the file exists, but GitHub treats
``custom_modes.yaml:180`` as a literal filename and 404s it. The correct form is
``#L180``.

Scope
-----
Every tracked ``*.md`` file, minus:

* ``FROZEN_PREFIXES`` — deliberately frozen audit trail (dated snapshots, archived and
  deprecated trees). Their broken links are preserved history, not defects. This is an
  explicit allowlist, not a heuristic: adding a directory here is a visible decision.
* ``FIXTURE_PREFIXES`` — synthetic corpora and vendored third-party packs, which are
  test data rather than documentation.

Usage::

    python scripts/check_md_links.py            # scan; exit 1 on any violation
    python scripts/check_md_links.py --selftest # prove the detector can fail
    python scripts/check_md_links.py --list     # machine-readable violation list
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Frozen audit trail: preserved verbatim, reflects what was true at its date.
FROZEN_PREFIXES: tuple[str, ...] = (
    "docs/archive/",
    "docs/architecture/deprecated/",
    "docs/project-management/phases/",
    "docs/project-management/planning/",
    "docs/project-management/plans/",
    "docs/project-management/reviews/",
)

# Test data and vendored third-party content, not documentation.
FIXTURE_PREFIXES: tuple[str, ...] = (
    "evaluation/data/",
    ".bob/skills/",
    "examples/",
)

# A dated research snapshot is frozen wherever it lives (same rule the savings gate
# uses): a YYYY-MM-DD stamp in the filename marks a point-in-time record.
DATED_SNAPSHOT_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Link targets that are prose *about* link syntax, or template placeholders.
PLACEHOLDER_TARGETS: frozenset[str] = frozenset(
    {
        "path",
        "target",
        "url",
        "link",
        "file",
        "...",
        "./related-concept.md",
        "../guides/related-guide.md",
        "../concepts/related-concept.md",
    }
)

# Inline markdown link: the target is everything up to the closing paren, no spaces.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
# path:123 or path:12-34 written inside a link target.
CITATION_RE = re.compile(r"^(?P<path>.*?):(?P<line>\d+(?:-\d+)?)$")


def tracked_files() -> set[str]:
    """Every path in the git index, exactly as git spells it (the Linux truth)."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {p for p in out.stdout.split("\0") if p}


def tracked_dirs(tracked: set[str]) -> set[str]:
    """Directory prefixes implied by the index, so a link to ``docs/adr/`` resolves."""
    dirs: set[str] = set()
    for f in tracked:
        parts = f.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    return dirs


def is_exempt(rel: str) -> bool:
    """True if *rel* is frozen audit trail or test data rather than live documentation."""
    if rel.startswith(FROZEN_PREFIXES) or rel.startswith(FIXTURE_PREFIXES):
        return True
    return bool(DATED_SNAPSHOT_RE.search(Path(rel).name))


def iter_links(text: str) -> list[tuple[int, str]]:
    """(line_no, target) for every inline link outside fenced code blocks."""
    found: list[tuple[int, str]] = []
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK_RE.findall(line):
            found.append((line_no, target))
    return found


def classify(source: str, target: str, tracked: set[str], dirs: set[str]) -> tuple[str, str] | None:
    """Return ``(kind, resolved)`` if *target* is a violation, else ``None``."""
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if target in PLACEHOLDER_TARGETS:
        return None

    bare = target.split("#", 1)[0]
    if not bare:
        return None

    # `](path:180)` — the file may exist, but the link 404s on GitHub.
    citation = CITATION_RE.match(bare)
    probe = citation.group("path") if citation else bare

    resolved = Path(Path(source).parent / probe).as_posix()
    # Normalise ``.``/``..`` segments purely lexically — deliberately never touching the
    # filesystem, since resolving through APFS is what hides case defects on macOS.
    parts: list[str] = []
    for seg in resolved.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    resolved = "/".join(parts)

    exists = resolved in tracked or resolved.rstrip("/") in dirs
    if citation:
        # Distinguish the two failure modes: a citation-shaped link whose file is real
        # is a link-form bug; one whose file is missing is also a stale path.
        return ("citation-in-link" if exists else "missing+citation", resolved)
    if exists:
        return None
    # Case-only mismatch is the signature defect — name it explicitly so the fix is obvious.
    lowered = {t.lower(): t for t in tracked}
    actual = lowered.get(resolved.lower())
    if actual:
        return ("case-mismatch", f"{resolved}  ->  actual: {actual}")
    return ("missing", resolved)


def scan(tracked: set[str] | None = None) -> list[tuple[str, int, str, str]]:
    """Return ``(source, line_no, kind, detail)`` for every violation in live docs."""
    tracked = tracked if tracked is not None else tracked_files()
    dirs = tracked_dirs(tracked)
    violations: list[tuple[str, int, str, str]] = []
    for rel in sorted(f for f in tracked if f.endswith(".md")):
        if is_exempt(rel):
            continue
        try:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, target in iter_links(text):
            verdict = classify(rel, target, tracked, dirs)
            if verdict:
                kind, detail = verdict
                violations.append((rel, line_no, kind, f"{target}  ({detail})"))
    return violations


KIND_HELP = {
    "case-mismatch": "wrong filename case — resolves on macOS, 404s on GitHub/Linux",
    "missing": "target is not in the git index",
    "citation-in-link": "path:LINE citation used as a link target — use #L<n>",
    "missing+citation": "path:LINE citation AND the path is not in the git index",
}


def _selftest() -> int:
    """Prove the detector fails on planted defects and passes on correct links."""
    tracked = {
        "docs/SLA.md",
        "docs/security/threat-model.md",
        "docs/knowledge-base/index.md",
        "docs/README.md",
        "config/custom_modes.yaml",
    }
    dirs = tracked_dirs(tracked)
    # (source, target, expected kind, why) — `probe` below substitutes the wrong-case
    # spelling where the correct one is what appears in `tracked`.
    bad = [
        # Pure case difference: docs/sla.md vs the tracked docs/SLA.md.
        ("docs/README.md", "sla.md", "case-mismatch", "case-only: sla.md vs SLA.md"),
        # Also case-only, and the form that broke 6 live links.
        ("docs/README.md", "knowledge-base/INDEX.md", "case-mismatch", "case-only: INDEX vs index"),
        # THREAT_MODEL.md -> threat-model.md changed case AND `_`->`-`, so lowercasing
        # alone does not find it: correctly reported as `missing`, not `case-mismatch`.
        ("docs/README.md", "security/THREAT_MODEL.md", "missing", "case + separator rename"),
        ("docs/README.md", "archive/BOOK_TABLE_OF_CONTENTS.md", "missing", "deleted target"),
        ("docs/README.md", "../config/custom_modes.yaml:180", "citation-in-link", "path:line"),
    ]
    good = [
        ("docs/README.md", "SLA.md"),
        ("docs/README.md", "knowledge-base/index.md"),
        ("docs/README.md", "security/threat-model.md"),
        ("docs/README.md", "https://example.com/x.md"),
        ("docs/README.md", "#a-heading"),
        ("docs/README.md", "path"),
    ]
    failures: list[str] = []
    for source, target, expect_kind, why in bad:
        verdict = classify(source, target, tracked, dirs)
        if verdict is None:
            failures.append(f"MISSED ({why}): {target!r}")
        elif verdict[0] != expect_kind:
            failures.append(f"WRONG KIND ({why}): {target!r} -> {verdict[0]}, want {expect_kind}")
    for source, target in good:
        if classify(source, target, tracked, dirs) is not None:
            failures.append(f"FALSE POSITIVE: {target!r}")
    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"Self-test passed: {len(bad)} planted defects caught, {len(good)} good links clean.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="verify the detector can fail")
    parser.add_argument("--list", action="store_true", help="one violation per line, no prose")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    violations = scan()
    if args.list:
        for source, line_no, kind, detail in violations:
            print(f"{source}:{line_no}\t{kind}\t{detail}")
        return 1 if violations else 0

    by_file: dict[str, list[tuple[int, str, str]]] = {}
    for source, line_no, kind, detail in violations:
        by_file.setdefault(source, []).append((line_no, kind, detail))

    if not violations:
        print("All relative Markdown links in live docs resolve against the git index.")
        return 0

    print("Checking relative Markdown links against the git index (case-sensitively):\n")
    for source in sorted(by_file):
        print(f"  FAIL {source}:")
        for line_no, kind, detail in by_file[source]:
            print(f"    L{line_no}: [{kind}] {detail}")
    kinds = sorted({k for _, _, k, _ in violations})
    print(
        f"\nFAILED: {len(violations)} broken relative link(s) across {len(by_file)} file(s).",
        file=sys.stderr,
    )
    for k in kinds:
        n = sum(1 for _, _, kk, _ in violations if kk == k)
        print(f"  {k} ({n}): {KIND_HELP[k]}", file=sys.stderr)
    print(
        "\nResolve each target against `git ls-files` — not against the local "
        "filesystem, which is case-insensitive on macOS and hides exactly this class "
        "of defect.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
