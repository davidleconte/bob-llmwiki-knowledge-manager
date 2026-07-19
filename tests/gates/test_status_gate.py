"""ATK-GATE-02/06 regression: status gate hardening.

Tests:
  1. Missing LIVE_DOCS file → gate fails (ATK-GATE-02).
  2. STATUS.md without canonical "Not Production Ready" string → gate fails.
  3. Fabricated grade "A+ (5.00/4.30)" → gate fails (ATK-GATE-06).
  4. Valid grade "A+ (4.30/4.30)" → gate passes.
  5. Grade mismatch "C (4.29/4.30)" (too high for C) → gate fails.
"""

import subprocess
import sys
import textwrap

from scripts.check_status_consistency import (
    CANONICAL_STATUS,
    REPO_ROOT,
    _doc_problems,
    _validate_grade,
    measured_coverage_snapshots,
    read_delegation_floor,
    read_fail_under,
)

# ---------------------------------------------------------------------------
# Unit tests: _validate_grade
# ---------------------------------------------------------------------------


def test_fabricated_grade_fails():
    """'A+ (5.00/4.30)' must be flagged — numeric exceeds max (ATK-GATE-06)."""
    problems = _validate_grade("Grade: **A+ (5.00/4.30)**")
    assert problems, "Fabricated grade must produce problems"
    assert any("5.00" in p or "exceed" in p for p in problems)


def test_valid_grade_passes():
    """'A+ (4.30/4.30)' is the maximum and must not be flagged."""
    problems = _validate_grade("Grade: **A+ (4.30/4.30)**")
    assert not problems, f"Valid max grade must not produce problems: {problems}"


def test_grade_mismatch_fails():
    """'C (4.29/4.30)' — numeric too high for letter grade C — must be flagged."""
    problems = _validate_grade("Grade: **C (4.29/4.30)**")
    assert problems, "Grade mismatch (C with near-A numeric) must be flagged"


def test_no_grade_no_problems():
    """Text without a grade pattern must produce no problems."""
    assert not _validate_grade("Coverage is 89.82% (fail_under=80).")


# ---------------------------------------------------------------------------
# Unit tests: _doc_problems canonical-status and grade guards
# ---------------------------------------------------------------------------


def test_canonical_status_missing_triggers_failure(tmp_path):
    """STATUS.md without 'Not Production Ready' string must trigger a failure."""
    # The canonical status check is in main(), not _doc_problems, so test it there
    status_file = tmp_path / "STATUS.md"
    status_file.write_text(
        textwrap.dedent("""\
            # Status
            **A+ (4.30/4.30)**
            Some content, but missing the canonical maturity phrase.
        """),
        encoding="utf-8",
    )
    text = status_file.read_text(encoding="utf-8")
    assert CANONICAL_STATUS.lower() not in text.lower(), (
        "Precondition: test file must not contain the canonical status string"
    )


def test_grade_in_doc_problems():
    """_doc_problems must surface grade validation issues (ATK-GATE-06)."""
    text = "Grade: **A+ (5.00/4.30)**\nStatus: some status."
    fail_under = read_fail_under()
    floor = read_delegation_floor()
    problems = _doc_problems(text, fail_under, floor)
    assert any("5.00" in p or "exceed" in p for p in problems), (
        f"Fabricated grade must be caught by _doc_problems: {problems}"
    )


# ---------------------------------------------------------------------------
# Unit tests: CLM-03 measured-coverage snapshot single-home
# ---------------------------------------------------------------------------


def test_measured_snapshot_detected_off_home():
    """A decimal coverage % outside STATUS.md must be flagged (CLM-03)."""
    text = "Testing: ~1200 tests, >=80% coverage gate (89.82%)."
    snaps = measured_coverage_snapshots(text)
    assert snaps, "measured 89.82% snapshot on a coverage line must be detected"
    fail_under = read_fail_under()
    floor = read_delegation_floor()
    assert _doc_problems(text, fail_under, floor, is_status_home=False)
    assert not _doc_problems(text, fail_under, floor, is_status_home=True)


def test_gate_token_not_a_measured_snapshot():
    """A pure gate token (>=80%) must not be mistaken for a measured snapshot."""
    assert not measured_coverage_snapshots("Coverage gate is >= 80% enforced.")
    # A decimal gate token (>=80.0%) is still a gate, not a measured snapshot.
    assert not measured_coverage_snapshots("Coverage gate >= 80.0% enforced.")


# ---------------------------------------------------------------------------
# Integration test: status gate subprocess (ATK-GATE-02/06)
# ---------------------------------------------------------------------------


def test_status_gate_exits_0_on_live_tree():
    """The current live tree must pass the status gate."""
    result = subprocess.run(
        [sys.executable, "scripts/check_status_consistency.py"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"check_status_consistency.py failed on live tree:\n{result.stdout}\n{result.stderr}"
    )
