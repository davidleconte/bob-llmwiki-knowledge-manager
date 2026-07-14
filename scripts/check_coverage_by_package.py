#!/usr/bin/env python3
"""Enforce per-package coverage floors from a ``coverage.json`` report.

The global coverage gate lives once in ``pyproject.toml`` (``[tool.coverage.report]
fail_under``). This script adds *per-package* floors that ``coverage.py`` cannot
express natively, so a subsystem can't quietly rot while the global number is
propped up elsewhere. Floors are declared here, in one place, with their rationale.

Usage::

    coverage json -o coverage.json        # or: pytest --cov=src --cov-report=json:coverage.json
    python scripts/check_coverage_by_package.py [coverage.json]

Exits non-zero (and prints every breach) if any package is below its floor.
"""

from __future__ import annotations

import json
import sys

# Per-package minimum line coverage (%). One home for these values.
#
# monitoring: live runtime code (cost/metrics/health) — held at the 70% bar.
# delegation: STAGED. It is orphaned (nothing in src/ imports it) and slated for a
#   Phase-4 rewrite, so testing its agents/* subpackage now would be coverage
#   theater. Floor is pinned at roughly its current honest level to lock the gain
#   and catch regressions; ratchet to 70 in Phase 4 once it is wired into runtime.
FLOORS = {
    "src/monitoring": 70.0,
    "src/delegation": 54.0,
}


def _normalize(path: str) -> str:
    return "/" + path.replace("\\", "/").lstrip("/")


def _package_coverage(report: dict, package: str) -> tuple[int, int]:
    """Aggregate (covered_lines, num_statements) across files under ``package``."""
    needle = _normalize(package) + "/"
    covered = statements = 0
    for path, data in report.get("files", {}).items():
        if needle in _normalize(path):
            summary = data.get("summary", {})
            covered += summary.get("covered_lines", 0)
            statements += summary.get("num_statements", 0)
    return covered, statements


def main(argv: list[str]) -> int:
    report_path = argv[1] if len(argv) > 1 else "coverage.json"
    try:
        with open(report_path, encoding="utf-8") as fh:
            report = json.load(fh)
    except FileNotFoundError:
        print(
            f"ERROR: coverage report not found: {report_path}\n"
            f"Generate it with: pytest --cov=src --cov-report=json:{report_path}",
            file=sys.stderr,
        )
        return 2

    failures = []
    print("Per-package coverage floors:")
    for package, floor in sorted(FLOORS.items()):
        covered, statements = _package_coverage(report, package)
        if statements == 0:
            print(f"  ERROR {package}: no statements found in report (path mismatch?)")
            failures.append(package)
            continue
        pct = 100.0 * covered / statements
        status = "OK " if pct >= floor else "FAIL"
        if pct < floor:
            failures.append(package)
        print(
            f"  {status} {package}: {pct:5.1f}%  (floor {floor:.0f}%, {covered}/{statements} stmts)"
        )

    if failures:
        print(
            f"\nFAILED: {len(failures)} package(s) below floor: {', '.join(sorted(failures))}",
            file=sys.stderr,
        )
        return 1
    print("\nAll per-package coverage floors satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
