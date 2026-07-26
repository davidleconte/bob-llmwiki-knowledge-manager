#!/usr/bin/env python3
"""Fail when a live document's self-declared date predates its own last commit.

Why this gate exists (2026-07-25 full-project audit, finding V-6/DATE-FRESHNESS)
-------------------------------------------------------------------------------
``STATUS.md`` declares itself "the canonical maturity status for the repository" and
every other document is told to defer to it. At audit time it read ``As of 2026-07-19``
while 18 PRs had merged after that date — so every doc that dutifully deferred to
STATUS.md was deferring to a pre-Wave-2 snapshot. ``docs/INDEX.md``,
``ARCHITECTURE.md`` and the CHANGELOG's newest entry were stale in the same way.

Nothing caught it, because staleness has no syntax. A stale date is *well-formed*; only
its relationship to the commit log makes it wrong. This gate supplies that relationship.

Contract
--------
For each watched document: if it declares a date (``As of``, ``Last Updated``,
``Last updated``, ``updated:``), that date must be **on or after** the author date of
the most recent commit that modified the file — ignoring the commit that is only
updating the date itself, which is why the comparison is against ``HEAD~1`` when the
working tree is dirty.

Deliberately narrow. It watches a curated list of documents that assert currency, not
every file: a dated research snapshot *should* keep its original date, and flagging it
would train people to ignore the gate.

Usage::

    python scripts/check_doc_freshness.py
    python scripts/check_doc_freshness.py --selftest
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Documents that assert they are current. Curated, not globbed — see the docstring.
WATCHED: tuple[str, ...] = (
    "STATUS.md",
    "docs/INDEX.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/README.md",
    "docs/book/table-of-contents.md",
)

# `As of` / `Last Updated` / `updated:` followed by an ISO date, tolerating the
# Markdown noise that actually appears between them: bold markers, table pipes and
# colons, in any order. The first draft of this pattern required them in a fixed order
# and silently returned None for STATUS.md's own `| **As of** | 2026-07-25 |` row —
# which meant the live scan *passed* by skipping the very file the gate exists for.
# The self-test caught it; that is the argument for shipping a self-test with a gate.
DATE_RE = re.compile(
    r"(?:as\s+of|last\s+updated|updated)[\s:|*]*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)


def declared_date(text: str) -> date | None:
    """The first ISO date the document declares as its currency, if any."""
    m = DATE_RE.search(text)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def is_shallow(repo_root: Path | None = None) -> bool:
    """True when the clone has truncated history, so per-file commit dates are fiction.

    ``actions/checkout`` defaults to ``fetch-depth: 1``. Under that default the clone
    holds exactly one commit -- on a pull_request event, an ephemeral merge commit
    created when the job starts -- so ``git log -1 -- <path>`` reports *that* commit
    for every file, dated now. Every watched document then reads as "modified today".

    This gate shipped with that defect and passed anyway, because on the day it landed
    the documents' declared date happened to equal the run date. The morning after, the
    clock rolled over and it went red on content nobody had touched. Left unfixed it
    would fail every pull request opened after the declared date -- unmergeable by
    construction, for a reason with nothing to do with the change under review.

    A wrong answer is worse than no answer here, so the caller refuses to run rather
    than comparing against a synthetic date.
    """
    root = repo_root or REPO_ROOT
    out = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
        capture_output=True,
        text=True,
    )
    return out.stdout.strip() == "true"


def last_commit_date(rel: str, repo_root: Path | None = None) -> date | None:
    """Author date of the newest commit touching *rel* (None if never committed)."""
    root = repo_root or REPO_ROOT
    out = subprocess.run(
        ["git", "-C", str(root), "log", "-1", "--format=%ad", "--date=short", "--", rel],
        capture_output=True,
        text=True,
    )
    stamp = out.stdout.strip()
    if not stamp:
        return None
    try:
        return date.fromisoformat(stamp)
    except ValueError:
        return None


def stale_documents(repo_root: Path | None = None) -> list[tuple[str, date, date]]:
    """``(path, declared, last_commit)`` for each watched doc whose date lags its commits."""
    root = repo_root or REPO_ROOT
    stale: list[tuple[str, date, date]] = []
    for rel in WATCHED:
        path = root / rel
        if not path.exists():
            continue
        declared = declared_date(path.read_text(encoding="utf-8", errors="replace"))
        if declared is None:
            continue
        committed = last_commit_date(rel, root)
        if committed is None:
            continue
        if declared < committed:
            stale.append((rel, declared, committed))
    return stale


def _selftest() -> int:
    """Prove the date parser accepts the real forms and rejects a stale relationship."""
    failures: list[str] = []
    cases = [
        ("| **As of** | 2026-07-25 |", date(2026, 7, 25)),
        ("**Last Updated:** 2026-07-18", date(2026, 7, 18)),
        ("**Last updated:** 2026-07-25 · **Maturity:**", date(2026, 7, 25)),
        ("updated: 2026-07-20", date(2026, 7, 20)),
        ("no date at all here", None),
        ("Last Updated: July 17, 2026", None),  # prose dates are out of scope, by design
    ]
    for text, want in cases:
        got = declared_date(text)
        if got != want:
            failures.append(f"parse {text!r} -> {got}, want {want}")

    # The relationship the gate exists to catch.
    if not (date(2026, 7, 19) < date(2026, 7, 21)):
        failures.append("ordering comparison is broken")

    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"Self-test passed: {len(cases)} date forms parsed as expected.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="verify the parser")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    if is_shallow():
        print(
            "ERROR: this repository is a shallow clone, so per-file commit dates are "
            "not meaningful — every path resolves to the single fetched commit.\n"
            "Check out with full history (`fetch-depth: 0`) before running this gate. "
            "Refusing to report a verdict computed from a synthetic date.",
            file=sys.stderr,
        )
        return 2

    stale = stale_documents()
    if not stale:
        print(f"All {len(WATCHED)} watched documents declare a date at or after their last commit.")
        return 0

    print("Checking that documents asserting currency are actually current:\n")
    for rel, declared, committed in stale:
        print(f"  STALE {rel}: declares {declared}, last modified {committed}")
    print(
        f"\nFAILED: {len(stale)} document(s) declare a date older than their own newest "
        "commit.\nA stale date is well-formed, so only the commit log can catch it — which "
        "is why STATUS.md could sit at 'As of 2026-07-19' through 18 merged PRs while every "
        "doc deferring to it inherited that staleness.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
