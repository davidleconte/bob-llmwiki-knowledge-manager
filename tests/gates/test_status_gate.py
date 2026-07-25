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
    _validate_grade_provenance,
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
# Unit tests: _validate_grade_provenance (C5 / CLM-02) — a live grade must be
# independently sourced or honestly self-labeled; the arithmetic gate cannot tell
# a self-conferred A+ from an independent one.
# ---------------------------------------------------------------------------


def test_unprovenanced_grade_flagged():
    """A bare live grade with no provenance must be flagged (C5)."""
    problems = _validate_grade_provenance("Final grade **A+ (4.30/4.30)** achieved.")
    assert problems and any("unprovenanced" in p for p in problems), problems


def test_self_labeled_grade_passes():
    """A self-assessed / withdrawn grade is honestly labeled and passes."""
    assert not _validate_grade_provenance(
        "The self-assessed **A+ (4.30/4.30)** has since been withdrawn."
    )


def test_independent_grade_passes():
    """A grade citing an independent re-grade (grader: + evaluation/regrade/…) passes."""
    text = (
        "Grade **A (3.80/4.30)**\n"
        "grader: external-panel; method: dual-rubric\n"
        "see evaluation/regrade/verdict-2026-08.md"
    )
    assert not _validate_grade_provenance(text)


def test_grade_provenance_window_is_bounded():
    """Provenance more than 2 lines from the grade does not launder it."""
    text = (
        "Grade **A+ (4.30/4.30)** is our final verdict.\n"
        "filler\nfiller\nfiller\n"
        "grader: external; evaluation/regrade/v.md"
    )
    assert _validate_grade_provenance(text), "provenance 4 lines away must not count"


def test_arithmetic_valid_but_unprovenanced_grade_still_fails():
    """A syntactically valid A+ that is self-conferred (no provenance) is still rejected."""
    # _validate_grade (arithmetic) passes it; _validate_grade_provenance must not.
    line = "Grade: **A+ (4.30/4.30)**"
    assert not _validate_grade(line), "arithmetic must accept the max grade"
    assert _validate_grade_provenance(line), "provenance must reject the bare self-grade"


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


# ── Audit 2026-07-25 (N-5): the grade-provenance blind spot ────────────────────────
#
# `_GRADE_RE` matched only the bold `**<letter> (n.nn/4.30)**` shape and was the sole
# input to the provenance check, so BOTH live overclaims were structurally invisible to
# a gate whose stated job was to catch exactly them. These pin each historical evasion.


def test_provenance_catches_slash_five_score():
    """README.md:450 published `2.9 -> 3.8 -> 4.2/5` as an achieved independent verdict
    when the tracked source gives 4.2 as a projected target. `/5` != `/4.30`, so the
    old pattern never saw it."""
    from scripts.check_status_consistency import _validate_grade_provenance

    text = (
        "re-verified by re-running the original exploits\n"
        "the independent audit score moved **2.9 -> 3.8 -> 4.2/5** (re-grade pending).\n"
    )
    assert _validate_grade_provenance(text), "a /5-denominator score must need provenance"


def test_provenance_catches_unbolded_letter_grade():
    """docs/INDEX.md:56 shipped `- ✅ A+ (4.30/4.30)` — correct rubric, no bold."""
    from scripts.check_status_consistency import _validate_grade_provenance

    text = "**Key Findings:**\n- A+ (4.30/4.30) — all 4 structural gaps closed\n- more\n"
    assert _validate_grade_provenance(text), "an unbolded grade must need provenance"


def test_provenance_catches_bare_letter_status():
    """docs/architecture/README.md:4 shipped `**Status:** A+ — see STATUS.md`."""
    from scripts.check_status_consistency import _validate_grade_provenance

    text = "# Architecture Documentation\n**Status:** A+ — see [STATUS.md](../../STATUS.md)\n"
    assert _validate_grade_provenance(text), "a bare letter status must need provenance"


def test_provenance_accepts_withdrawal_label():
    from scripts.check_status_consistency import _validate_grade_provenance

    text = 'the earlier self-assessed "A+" grade has been **withdrawn** —\nnot independent.\n'
    assert _validate_grade_provenance(text) == []


def test_provenance_accepts_named_on_file_verdict():
    """Naming the verdict a score comes from is valid provenance."""
    from scripts.check_status_consistency import _validate_grade_provenance

    text = (
        "On-file independent verdicts: counter-audit (2026-07-19) **2.9/5**;\n"
        "last graded verdict **NO-GO 3.46/4.3** (2026-07-14).\n"
    )
    assert _validate_grade_provenance(text) == []


def test_provenance_accepts_explicit_projection():
    """A forward-looking target is honest as long as it says so — which is precisely
    what README.md failed to do when it republished 4.2/5 as achieved."""
    from scripts.check_status_consistency import _validate_grade_provenance

    text = "that figure is a *projected target after remediation*, not a verdict:\n4.2/5.\n"
    assert _validate_grade_provenance(text) == []


def test_navigation_docs_are_in_scope():
    """N-3: docs/INDEX.md and docs/architecture/README.md each published the withdrawn
    A+ while absent from LIVE_DOCS, so the gate never opened them."""
    from scripts.check_status_consistency import LIVE_DOCS

    for rel in ("docs/INDEX.md", "docs/README.md", "docs/architecture/README.md"):
        assert rel in LIVE_DOCS, rel
