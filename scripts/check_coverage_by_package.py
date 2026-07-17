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
# validation: Phase-5 harness that produces the *published* savings numbers, so it
#   must itself be trustworthy — held well above the global bar. Measured 90.5% at
#   introduction; floor set to 85.0 to lock the gain with a small margin.
# tools: the untrusted-path handlers (kb_query / batch_file_reader / component_analyzer)
#   reached via each tool's CLI and the delegation task.target. Folded into the gated
#   denominator in Phase 8 (previously coverage-omitted). Behavioral tests took it from
#   ~19-45% per module to ~94%; floor pinned at 85.0 to lock that gain, since this is
#   the most security-relevant code and must not silently regress.
FLOORS = {
    "src/monitoring": 70.0,
    "src/delegation": 52.0,
    "src/embeddings": 80.0,  # disk-backed index I/O; floor matches the global gate.
    "src/validation": 85.0,
    "src/tools": 85.0,
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


def _evaluate(report: dict) -> tuple[list[str], list[str]]:
    """Compare every package against its floor. Pure (no I/O).

    Returns ``(failures, rows)`` where ``failures`` is the list of packages below
    floor (or with no measured statements) and ``rows`` are the printable lines.
    """
    failures: list[str] = []
    rows: list[str] = []
    for package, floor in sorted(FLOORS.items()):
        covered, statements = _package_coverage(report, package)
        if statements == 0:
            rows.append(f"  ERROR {package}: no statements found in report (path mismatch?)")
            failures.append(package)
            continue
        pct = 100.0 * covered / statements
        status = "OK " if pct >= floor else "FAIL"
        if pct < floor:
            failures.append(package)
        rows.append(
            f"  {status} {package}: {pct:5.1f}%  (floor {floor:.0f}%, {covered}/{statements} stmts)"
        )
    return failures, rows


def _selftest() -> int:
    """Verify the floor comparison flags a below-floor package and passes above-floor."""

    def _report(below=None) -> dict:
        files = {}
        for pkg, floor in FLOORS.items():
            pct = (floor - 10.0) if pkg == below else (floor + 5.0)
            pct = max(0.0, min(100.0, pct))
            covered = int(round(pct / 100.0 * 1000))
            files[f"{pkg}/mod.py"] = {"summary": {"covered_lines": covered, "num_statements": 1000}}
        return {"files": files}

    failures: list[str] = []
    if _evaluate(_report())[0]:
        failures.append("an all-above-floor report should produce no failures")
    for target in FLOORS:
        flagged = _evaluate(_report(below=target))[0]
        if target not in flagged:
            failures.append(f"{target} below its floor should be flagged (got {flagged})")
    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: floor comparison correct for {len(FLOORS)} packages.")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
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

    failures, rows = _evaluate(report)
    print("Per-package coverage floors:")
    for row in rows:
        print(row)
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
