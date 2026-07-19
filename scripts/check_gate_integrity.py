#!/usr/bin/env python3
"""Gate-integrity check (ATK-GATE-07 / C3): forbid weakening a gate and planting a
claim in the SAME pull request.

One actor authoring the code, the gates that check it, and the claims those gates
guard is bus-factor 1. Absent a second human reviewer, this structural check
mechanically blocks the single-PR "weaken the gate + plant the overclaim" attack:
a PR whose diff touches BOTH a gate definition AND a claim surface fails.

- GATE definitions:  ``config/gates/**``, ``scripts/check_*.py``, ``src/validation/**``
- CLAIM surfaces:     ``STATUS.md``, ``README.md``, ``docs/**`` (except ``docs/api/**``)

``docs/api/**`` is excluded because it is generated from ``src/`` docstrings and
pinned to them by the API-doc freshness gate — it is not a hand-authored claim
surface, and including it would contradict the mandatory API-doc regeneration that
accompanies a ``src/validation/**`` change.

A gate-only PR (tightening a check) and a claim-only PR (updating a doc) both pass;
only their combination in one PR is blocked. Split such a change into two PRs so the
gate change lands and is independently reviewable BEFORE any claim relies on it.
This is disclosed in ``SECURITY.md`` §Gate Independence as the honest substitute for
a second required human reviewer.

Usage::

    check_gate_integrity.py <changed_file> [<changed_file> ...]
    check_gate_integrity.py --base origin/main      # diff against a base ref
    git diff --name-only main...HEAD | check_gate_integrity.py --stdin
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Iterable, List

# One-home constants so the tests and the doc can reference the same definitions.
GATE_DIR_PREFIXES = ("config/gates/", "src/validation/")
CLAIM_FILES = frozenset({"STATUS.md", "README.md"})
CLAIM_DIR_PREFIX = "docs/"
CLAIM_DIR_EXCLUDE = "docs/api/"  # generated reference, pinned by the freshness gate


def _normalise(path: str) -> str:
    """Strip a leading ``./`` and normalise separators to forward slashes."""
    p = path.strip().replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def is_gate_file(path: str) -> bool:
    """True if *path* is a gate definition (config, gate script, or validation)."""
    p = _normalise(path)
    if any(p.startswith(prefix) for prefix in GATE_DIR_PREFIXES):
        return True
    # scripts/check_*.py — the honesty gate scripts themselves.
    return (
        p.startswith("scripts/") and p.rsplit("/", 1)[-1].startswith("check_") and p.endswith(".py")
    )


def is_claim_surface(path: str) -> bool:
    """True if *path* is a hand-authored claim surface (status/readme/docs)."""
    p = _normalise(path)
    if p in CLAIM_FILES:
        return True
    return p.startswith(CLAIM_DIR_PREFIX) and not p.startswith(CLAIM_DIR_EXCLUDE)


def check(changed_files: Iterable[str]) -> List[str]:
    """Return a list of problems (empty == OK) for a set of changed files.

    A single problem is reported when the diff touches both a gate and a claim
    surface, naming the offending files on each side.
    """
    files = [_normalise(f) for f in changed_files if f.strip()]
    gates = sorted({f for f in files if is_gate_file(f)})
    claims = sorted({f for f in files if is_claim_surface(f)})
    if gates and claims:
        return [
            "This PR modifies BOTH a gate definition and a claim surface, which the "
            "single-owner gate-integrity rule forbids (ATK-GATE-07). Split it into two "
            "PRs: land the gate change first (independently reviewable), then the claim.\n"
            f"  gate files:  {', '.join(gates)}\n"
            f"  claim files: {', '.join(claims)}"
        ]
    return []


def _changed_files_from_base(base: str) -> List[str]:
    """Return files changed between *base* and HEAD (three-dot / merge-base diff)."""
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Changed file paths to classify.")
    parser.add_argument("--base", help="Diff against this git ref (base...HEAD).")
    parser.add_argument("--stdin", action="store_true", help="Read file paths from stdin.")
    args = parser.parse_args(argv)

    if args.base:
        changed = _changed_files_from_base(args.base)
    elif args.stdin:
        changed = [line for line in sys.stdin.read().splitlines() if line.strip()]
    else:
        changed = args.files

    problems = check(changed)
    if problems:
        print("❌ Gate-integrity check failed (ATK-GATE-07):\n")
        for p in problems:
            print(p)
        print(
            "\nSee SECURITY.md §Gate Independence. If the co-change is genuinely "
            "atomic, land the gate change in its own PR first."
        )
        return 1
    print("✅ Gate-integrity check passed: no gate + claim co-modification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
