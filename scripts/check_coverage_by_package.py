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
# delegation: STAGED. A separate, experimental subsystem (nothing in src/ imports
#   it) that solves a different problem domain than the optimizer — see
#   docs/knowledge-base/research/delegation-integration-analysis-2026-07-13.md.
#   Per the Phase-4 decision it stays separate (NOT facade-wired); its only Phase-4
#   change was the B3 layering fix (shared utils moved to src/tools/). The floor is
#   pinned at its current honest level to lock the gain and catch regressions — it
#   does NOT ratchet to 70, because the subsystem is intentionally not integrated.
#   Floor moved 54.0 -> 52.0 in Phase 4: the B3 fix deleted the per-agent
#   sys.path.insert + now-unused `import sys`/`from pathlib import Path` boilerplate
#   (~18 always-executed, 100%-covered import lines), which mechanically lowered the
#   ratio from ~54.3% to 52.9% without removing any tested logic. 52.0 tracks the new
#   honest level with a small margin.
FLOORS = {
    "src/monitoring": 70.0,
    "src/delegation": 52.0,
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
