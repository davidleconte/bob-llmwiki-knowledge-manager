#!/usr/bin/env python3
"""Enforce 'one home per value' for status/coverage claims across live docs.

Two values in this repo have a single, authoritative home:

* the **coverage gate** -> ``fail_under`` in ``pyproject.toml``
  (``[tool.coverage.report]``);
* the **maturity status** -> ``STATUS.md`` at the repo root.

This validator fails CI when a *live* status document contradicts either home:

1. Any coverage-**gate** threshold cited in a live doc must equal ``fail_under``.
   A doc may still quote a dated *measured* snapshot (e.g. "82.5% coverage as of
   2026-07-13") -- only explicit gate-shaped assertions are checked
   (``>=80%``, ``80%+``, ``fail_under = 80``). Measured snapshots and unrelated
   percentages are ignored, so the durable claim is the gate, not a number that
   rots as coverage moves.
2. Known-fabricated maturity phrasing (e.g. "All Phases Complete") must not
   appear as a live claim, and ``STATUS.md`` must still declare the canonical
   "Not Production Ready" status.

Dated audit snapshots (``docs/knowledge-base/research/**``, ``evaluation/**``)
and any file explicitly banner-marked ``DEPRECATED``/``STALE`` are not
authoritative and are skipped -- they are frozen point-in-time records.

Usage::

    python scripts/check_status_consistency.py

Exits non-zero (and prints every divergence) if any live doc contradicts a home.
This is the "one home per value" guard the institutional audit scoped to Phase 6,
pulled forward to stop status drift from recurring.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Live status surfaces whose undated claims must agree with the single homes.
# Curated (not a glob) so dated audit snapshots under docs/**/research and
# evaluation/** stay out -- those are frozen point-in-time records.
LIVE_DOCS = (
    "STATUS.md",
    "README.md",
    "AGENTS.md",
    "tests/README.md",
    "docs/project-management/project-status.md",
)

# A doc carrying one of these in its first lines has explicitly recused itself
# from being authoritative; skip it.
DEPRECATION_MARKERS = ("DEPRECATED", "STALE")
DEPRECATION_SCAN_LINES = 15

# Maturity phrasings that were fabricated/retracted and must never reappear as a
# live claim (case-insensitive substring match).
FORBIDDEN_MATURITY = ("All Phases Complete",)

# Assertions that were true pre-remediation but are now false. The code + the
# CHANGELOG "Fixed" section are the home for what is fixed; a live doc must not
# contradict them. ("correctness bugs remain open" was STATUS.md's own stale
# claim -- C1-C7 + the RLock deadlock are fixed with revert-tested regressions.)
FORBIDDEN_STALE_CLAIMS = ("correctness bugs remain open",)

# The canonical maturity string that STATUS.md must continue to assert.
CANONICAL_STATUS = "Not Production Ready"

# ATK-GATE-06: Grade validation constants.
# A fabricated grade like "A+ (5.00/4.30)" must be rejected.
_GRADE_RE = re.compile(r"\*\*([A-F][+-]?)\s+\((\d+\.\d+)/4\.30\)\*\*")
_MAX_NUMERIC_GRADE = 4.30
# Minimum numeric threshold for each letter prefix (A+ = ≥4.0, A = ≥3.7, etc.)
_GRADE_THRESHOLDS = {
    "A+": 4.0, "A": 3.7, "A-": 3.3,
    "B+": 3.0, "B": 2.7, "B-": 2.3,
    "C+": 2.0, "C": 1.7, "C-": 1.3,
    "D+": 1.0, "D": 0.7, "D-": 0.3,
    "F": 0.0,
}

# The delegation per-package coverage floor is cited in prose (AGENTS.md); its
# single home is scripts/check_coverage_by_package.py. This catches the stale
# "~54%" that contradicted the real 52.0.
_FLOOR_CLAIM = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*per-package(?:\s+coverage)?\s+floor")

# Gate-shaped coverage assertions. Deliberately NOT "any % on a coverage line":
# a measured snapshot ("82.5% coverage as of ...") is legitimate and must not
# trip this -- only these gate token shapes capture a number.
_GATE_TOKEN = re.compile(
    r"[>≥]=?\s*(\d+(?:\.\d+)?)\s*%"  # >=80% or  >=80 %  (>= and Unicode >=)
    r"|(\d+(?:\.\d+)?)\s*%\+"  # 80%+
    r"|fail_under\s*[=:]\s*(\d+(?:\.\d+)?)"  # fail_under = 80
)


def read_fail_under() -> int:
    """Read the single-home coverage gate from pyproject.toml (regex, no toml dep)."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r"^\s*fail_under\s*=\s*(\d+)", text, re.MULTILINE)
    if not m:
        raise SystemExit(
            "ERROR: could not find [tool.coverage.report] fail_under "
            "in pyproject.toml -- the coverage gate has no single home."
        )
    return int(m.group(1))


def read_delegation_floor() -> float:
    """Read the delegation per-package coverage floor from its single home."""
    text = (REPO_ROOT / "scripts" / "check_coverage_by_package.py").read_text(encoding="utf-8")
    m = re.search(r'"src/delegation"\s*:\s*(\d+(?:\.\d+)?)', text)
    if not m:
        raise SystemExit(
            "ERROR: could not find the src/delegation floor in "
            "scripts/check_coverage_by_package.py -- it has no single home."
        )
    return float(m.group(1))


def is_deprecated(text: str) -> bool:
    head = "\n".join(text.splitlines()[:DEPRECATION_SCAN_LINES]).upper()
    return any(marker in head for marker in DEPRECATION_MARKERS)


# Ordered grade scale from highest to lowest (for upper-bound checking).
_GRADE_ORDER = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]


def _validate_grade(text: str) -> list[str]:
    """Return problems for any grade strings that exceed the maximum or mismatch their letter.

    Catches fabricated grades like 'A+ (5.00/4.30)' (ATK-GATE-06).
    Checks both lower bound (numeric ≥ threshold for letter) and upper bound
    (numeric < threshold for the grade one step above).
    """
    problems: list[str] = []
    for m in _GRADE_RE.finditer(text):
        letter = m.group(1)
        numeric = float(m.group(2))
        if numeric > _MAX_NUMERIC_GRADE:
            problems.append(
                f"    fabricated grade: {m.group(0)} — numeric {numeric} exceeds max {_MAX_NUMERIC_GRADE}"
            )
            continue
        threshold = _GRADE_THRESHOLDS.get(letter)
        if threshold is not None and numeric < threshold:
            problems.append(
                f"    grade mismatch: {m.group(0)} — {letter} requires numeric ≥ {threshold}, "
                f"got {numeric}"
            )
            continue
        # Upper bound: numeric must not be ≥ threshold of the grade one step above.
        # e.g. "C (4.29/4.30)" — 4.29 ≥ threshold for A+ (4.0) → mismatch.
        if letter in _GRADE_ORDER:
            idx = _GRADE_ORDER.index(letter)
            if idx > 0:  # there is a grade above
                grade_above = _GRADE_ORDER[idx - 1]
                threshold_above = _GRADE_THRESHOLDS.get(grade_above, _MAX_NUMERIC_GRADE)
                if numeric >= threshold_above:
                    problems.append(
                        f"    grade mismatch: {m.group(0)} — numeric {numeric} qualifies for "
                        f"{grade_above} (threshold ≥ {threshold_above}), not {letter}"
                    )
    return problems


def gate_claims(text: str) -> list[tuple[int, float, str]]:
    """Return (line_no, value, line) for every coverage-gate assertion in text.

    Only lines that mention coverage (or fail_under) are considered, so a
    gate-shaped token in unrelated prose (e.g. ">=70% uptime") is ignored.
    """
    claims: list[tuple[int, float, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        low = line.lower()
        if "cover" not in low and "fail_under" not in low:
            continue
        for m in _GATE_TOKEN.finditer(line):
            value = next(g for g in m.groups() if g is not None)
            claims.append((line_no, float(value), line.strip()))
    return claims


_DECIMAL_PCT = re.compile(r"\d+\.\d+\s*%")


def measured_coverage_snapshots(text: str) -> list[tuple[int, str]]:
    """(line_no, line) for coverage lines carrying a *measured* decimal snapshot.

    CLM-03: a measured coverage number (e.g. "89.12%") has a single home,
    STATUS.md; every other live doc must defer to it rather than restate a value
    that rots as coverage moves. Gate-shaped tokens (``>=80%``, ``80%+``,
    ``fail_under=80``) are legitimate anywhere and are stripped before the check,
    so only a residual decimal percentage on a coverage line is flagged.
    """
    out: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if "cover" not in line.lower():
            continue
        if _DECIMAL_PCT.search(_GATE_TOKEN.sub("", line)):
            out.append((line_no, line.strip()))
    return out


def _doc_problems(
    text: str,
    fail_under: float,
    delegation_floor: float,
    is_status_home: bool = False,
) -> list[str]:
    """Every single-home inconsistency in one doc's text. Pure (no I/O)."""
    problems: list[str] = []

    # (1) coverage-gate consistency
    for line_no, value, line in gate_claims(text):
        if value != fail_under:
            problems.append(
                f"    L{line_no}: cites coverage gate {value:g}% != "
                f"{fail_under:g}% (pyproject fail_under)\n        {line}"
            )

    # (2) forbidden maturity phrasing
    low = text.lower()
    for phrase in FORBIDDEN_MATURITY:
        if phrase.lower() in low:
            problems.append(
                f"    forbidden maturity claim present: {phrase!r} (defer to STATUS.md)"
            )

    # (2b) forbidden stale correctness claims
    for phrase in FORBIDDEN_STALE_CLAIMS:
        if phrase.lower() in low:
            problems.append(
                f"    forbidden stale claim present: {phrase!r} "
                "(those bugs are fixed -- see CHANGELOG.md -> Fixed)"
            )

    # (2c) delegation coverage-floor consistency (one home per value)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for m in _FLOOR_CLAIM.finditer(line):
            value = float(m.group(1))
            if value != delegation_floor:
                problems.append(
                    f"    L{line_no}: cites per-package coverage floor {value:g}% != "
                    f"{delegation_floor:g}% (scripts/check_coverage_by_package.py)\n"
                    f"        {line.strip()}"
                )

    # (2d) ATK-GATE-06: grade validation — numeric must not exceed 4.30
    problems.extend(_validate_grade(text))

    # (2e) CLM-03: a measured coverage snapshot belongs only in STATUS.md.
    if not is_status_home:
        for line_no, line in measured_coverage_snapshots(text):
            problems.append(
                f"    L{line_no}: measured coverage snapshot outside STATUS.md — "
                "defer to STATUS.md, the single home for the measured number\n"
                f"        {line}"
            )

    return problems


def _selftest() -> int:
    """Verify the per-doc detectors on planted good/bad text (no filesystem)."""
    fail_under, floor = 80, 52.0
    checks = [
        ("clean gate + floor", "Coverage gate is >= 80% enforced; 52% per-package floor.", False),
        ("wrong coverage gate", "The coverage gate is >= 95% enforced.", True),
        ("wrong delegation floor", "delegation held at a 60% per-package floor", True),
        ("forbidden maturity", "Status: All Phases Complete.", True),
        ("forbidden stale claim", "Note: correctness bugs remain open.", True),
    ]
    failures: list[str] = []
    for label, text, expect in checks:
        got = bool(_doc_problems(text, fail_under, floor))
        if got != expect:
            failures.append(f"{label}: problems={got}, expected={expect}: {text!r}")

    # CLM-03: measured snapshot flagged off-home, allowed on-home; gate token clean.
    snap = "Point-in-time snapshot: 89.12% global coverage."
    if not _doc_problems(snap, fail_under, floor, is_status_home=False):
        failures.append("measured coverage snapshot off-home not flagged")
    if _doc_problems(snap, fail_under, floor, is_status_home=True):
        failures.append("measured coverage snapshot on-home wrongly flagged")
    if _doc_problems("Coverage gate is >= 80% enforced.", fail_under, floor, is_status_home=False):
        failures.append("coverage gate token wrongly flagged as measured snapshot")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: {len(checks)} status-consistency cases classified correctly.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return _selftest()
    fail_under = read_fail_under()
    delegation_floor = read_delegation_floor()
    failures: list[str] = []
    print(f"Single-home coverage gate (pyproject.toml fail_under): {fail_under}%")
    print(f"Single-home delegation floor (check_coverage_by_package.py): {delegation_floor:g}%")
    print("Checking live status docs:\n")

    for rel in LIVE_DOCS:
        path = REPO_ROOT / rel
        if not path.exists():
            # ATK-GATE-02: fail closed on missing live docs; skipping masks renames
            failures.append(rel)
            print(f"  FAIL {rel}: not found — rename must be reflected in LIVE_DOCS list")
            continue
        text = path.read_text(encoding="utf-8")
        if is_deprecated(text):
            print(f"  SKIP {rel}: banner-marked deprecated/stale")
            continue

        problems = _doc_problems(
            text, fail_under, delegation_floor, is_status_home=(rel == "STATUS.md")
        )

        if problems:
            failures.append(rel)
            print(f"  FAIL {rel}:")
            print("\n".join(problems))
        else:
            print(f"  OK   {rel}")

    # (3) STATUS.md must still assert the canonical maturity string.
    status_path = REPO_ROOT / "STATUS.md"
    if (
        status_path.exists()
        and CANONICAL_STATUS.lower() not in status_path.read_text(encoding="utf-8").lower()
    ):
        failures.append("STATUS.md")
        print(f"  FAIL STATUS.md: canonical status {CANONICAL_STATUS!r} not found")

    if failures:
        print(
            f"\nFAILED: {len(failures)} doc(s) diverge from the single home(s): "
            f"{', '.join(sorted(set(failures)))}",
            file=sys.stderr,
        )
        return 1
    print("\nAll live status docs are consistent with the single homes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
