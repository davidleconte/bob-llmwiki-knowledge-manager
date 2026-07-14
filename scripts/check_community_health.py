#!/usr/bin/env python3
"""Enforce that the community-health / governance file set stays present.

The institutional audit graded Project Governance (Dimension G) a **D** because
the standard community-health set was almost entirely absent
(``audit-2026-07-13-institutional.md:146-163``). Phase 7 created that set; this
guard keeps it from silently regressing -- a governance file deleted, emptied,
or reduced to a stub would otherwise pass CI unnoticed.

It is the governance analogue of ``check_value_homes.py``: a curated tuple (not
a glob) of the artifacts the project commits to maintain, each checked for two
failure modes:

* ``MISSING`` -- the file does not exist; and
* ``STUB``    -- the file exists but has less real content than ``min_chars``
  (a placeholder heading with nothing under it).

Add an artifact here when the project takes on a new governance commitment;
remove one only with a deliberate decision (governance files are not casually
dropped).

Usage::

    python scripts/check_community_health.py
    python scripts/check_community_health.py --selftest   # verify the engine

Exits non-zero (and prints every gap) on any missing or stub artifact.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# A reader maps a repo-relative path to its text, or None if the file is
# missing. Injected so the engine is testable without the filesystem (see
# ``_selftest``).
Reader = Callable[[str], Optional[str]]


@dataclass(frozen=True)
class Artifact:
    """A governance/community-health file the project commits to keep."""

    path: str
    min_chars: int = 150  # strip()'d length below this reads as a stub
    note: str = ""


# --- The required set: one entry per committed governance artifact. ------------
# Curated (not a glob) so the list is an explicit, reviewed commitment and so
# adding/removing a governance file is a deliberate edit here.
REQUIRED: tuple[Artifact, ...] = (
    Artifact("SECURITY.md", 400, "vulnerability disclosure policy"),
    Artifact("CONTRIBUTING.md", 400, "contributor guide + gate suite"),
    Artifact("CODE_OF_CONDUCT.md", 400, "Contributor Covenant"),
    Artifact("GOVERNANCE.md", 300, "decision model"),
    Artifact("SUPPORT.md", 200, "where to get help"),
    Artifact("LICENSE", 200, "MIT license text"),
    Artifact("docs/security/THREAT_MODEL.md", 800, "STRIDE threat model"),
    Artifact(".github/CODEOWNERS", 40, "review ownership"),
    Artifact(".github/PULL_REQUEST_TEMPLATE.md", 200, "PR checklist"),
    Artifact(".github/ISSUE_TEMPLATE/bug_report.md", 150, "bug template"),
    Artifact(".github/ISSUE_TEMPLATE/feature_request.md", 150, "feature template"),
    Artifact(".github/ISSUE_TEMPLATE/config.yml", 60, "issue-template config"),
)


def check_artifact(artifact: Artifact, read: Reader) -> Optional[str]:
    """Return a human-readable problem for one artifact, or None if it is OK."""
    text = read(artifact.path)
    if text is None:
        return f"MISSING: {artifact.path} ({artifact.note})"
    if len(text.strip()) < artifact.min_chars:
        return (
            f"STUB:    {artifact.path} has {len(text.strip())} chars "
            f"(< {artifact.min_chars} expected; {artifact.note})"
        )
    return None


def _repo_reader() -> Reader:
    def read(rel: str) -> Optional[str]:
        path = REPO_ROOT / rel
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    return read


def _selftest() -> int:
    """Verify the engine flags a missing file and a stub, and passes a full set."""
    artifacts = (
        Artifact("present", 10),
        Artifact("missing", 10),
        Artifact("stub", 100),
    )
    body = "x" * 50  # 50 real chars
    passing: dict[str, str] = {"present": body, "missing": body, "stub": "y" * 100}
    broken: dict[str, str] = {"present": body, "stub": "   short   "}  # 'missing' absent

    failures: list[str] = []
    if any(check_artifact(a, passing.get) for a in artifacts):
        failures.append("matched fixture reported a false gap")
    problems = [check_artifact(a, broken.get) for a in artifacts]
    flagged = [p for p in problems if p]
    if len(flagged) != 2:
        failures.append(f"planted gaps: expected 2 problems, got {len(flagged)}: {flagged}")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("SELFTEST OK: planted missing+stub flagged (2), full fixture clean.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    read = _repo_reader()
    problems: list[str] = []
    print("Checking the community-health / governance set:\n")
    for artifact in REQUIRED:
        problem = check_artifact(artifact, read)
        if problem:
            problems.append(problem)
            print(f"  FAIL {artifact.path}")
        else:
            print(f"  OK   {artifact.path}")

    if problems:
        print("\nGovernance set has gaps:\n", file=sys.stderr)
        for problem in sorted(problems):
            print(f"  {problem}", file=sys.stderr)
        print(
            "\nRestore the file (see Phase 7 / audit Dimension G) or, if the "
            "removal is intentional, update REQUIRED in "
            "scripts/check_community_health.py.",
            file=sys.stderr,
        )
        return 1
    print(f"\nAll {len(REQUIRED)} community-health artifacts present and non-stub.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
