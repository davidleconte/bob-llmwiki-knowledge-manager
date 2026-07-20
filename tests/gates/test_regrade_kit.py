"""E1 / R14 / CLM-02: the independent re-grade *kit* is complete and same-lineage-safe.

The A+ was self-conferred by the same agentic lineage that did the remediation and has
been withdrawn (`STATUS.md`). R14 is discharged only by a verdict from a *genuinely
independent* grader — a human third party or an external agentic process with a distinct
model/lineage and no remediation involvement. This lineage's job (per
`docs/project-management/plans/wave3-technical-spec-2026-07-19.md` §E1) is to build the
KIT and the verdict SLOT, **not** to produce the grade.

Two gates:
  * ``test_regrade_kit_complete`` — the kit carries rubric + finding register + both
    manifests + a grader worksheet with a provenance block, AND states no live grade
    itself (a grade in the kit would be exactly the same-lineage self-grade R14 forbids).
  * ``test_status_cites_regrade_when_present`` — the verdict slot is defined; and *once*
    a real ``verdict-*.md`` is filed, ``STATUS.md`` cites it and the C5 grade-provenance
    gate stays green.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_status_consistency import _GRADE_RE, REPO_ROOT

REGRADE_DIR = REPO_ROOT / "evaluation" / "regrade"
KIT = REGRADE_DIR / "regrade-kit-2026-07.md"
VERDICT_TEMPLATE = REGRADE_DIR / "verdict-TEMPLATE.md"


def _real_verdicts() -> list[Path]:
    """Filed verdicts — date-stamped ``verdict-*.md``, excluding the empty template."""
    if not REGRADE_DIR.is_dir():
        return []
    return [p for p in REGRADE_DIR.glob("verdict-*.md") if "TEMPLATE" not in p.name]


def test_regrade_kit_complete():
    """The kit contains rubric + register + manifests + worksheet-with-provenance."""
    assert KIT.is_file(), f"re-grade kit missing: {KIT.relative_to(REPO_ROOT)}"
    text = KIT.read_text(encoding="utf-8")
    low = text.lower()

    # (1) rubric — BOTH scorecards of the dual rubric.
    assert "tier-1 vendor" in low, "kit must carry the Tier-1 vendor scorecard"
    assert "watsonx-jury" in low or "watsonx jury" in low, (
        "kit must carry the watsonx-jury scorecard"
    )

    # (2) finding register with per-finding disposition.
    assert "finding register" in low, "kit must carry the Critical/High finding register"

    # (3) both evidence manifests, cited by path so the grader can re-run them.
    assert "validation-2026-07-14/manifest.json" in text, "kit must cite the validation manifest"
    assert "retrieval-2026-07-19/manifest.json" in text, "kit must cite the retrieval manifest"

    # (4) grader worksheet + provenance block (the fields the C5 gate keys on).
    assert "grader worksheet" in low, "kit must carry the grader worksheet"
    for field in ("grader:", "method:", "date:", "commit:"):
        assert field in low, f"worksheet provenance block missing {field!r}"

    # (5) same-lineage safety: the kit must NOT state a live grade itself. A
    # ``**A (n.nn/4.30)**`` token in the kit is precisely the self-grade R14 forbids;
    # the kit hands grading off, it does not perform it.
    assert _GRADE_RE.search(text) is None, (
        "the re-grade kit must not itself assert a **letter (n.nn/4.30)** grade — that "
        "would be a same-lineage self-grade, which does not discharge R14"
    )


def test_verdict_slot_defined():
    """The verdict slot exists as an (unfilled) template the independent grader copies."""
    assert VERDICT_TEMPLATE.is_file(), (
        f"verdict slot/template missing: {VERDICT_TEMPLATE.relative_to(REPO_ROOT)}"
    )
    tpl = VERDICT_TEMPLATE.read_text(encoding="utf-8").lower()
    for field in ("grader:", "method:", "date:", "commit:"):
        assert field in tpl, f"verdict template missing provenance field {field!r}"
    # The template is a slot, not a verdict: it must not carry a filled grade.
    assert _GRADE_RE.search(VERDICT_TEMPLATE.read_text(encoding="utf-8")) is None, (
        "verdict-TEMPLATE.md must stay unfilled — no grade token"
    )


def test_status_cites_regrade_when_present():
    """Once a real verdict is filed, STATUS.md cites it and the C5 gate stays green.

    Before any independent verdict exists the assertion is vacuous by design (the slot is
    defined, tested separately); it becomes load-bearing the moment a ``verdict-<date>.md``
    lands, which is the only way a live grade may reappear.
    """
    verdicts = _real_verdicts()
    if not verdicts:
        # No independent verdict yet — nothing to cite. The slot is checked by
        # test_verdict_slot_defined; there is nothing to enforce on STATUS.md here.
        return

    status = (REPO_ROOT / "STATUS.md").read_text(encoding="utf-8")
    assert any(v.name in status for v in verdicts), (
        "a verdict-*.md exists but STATUS.md does not cite it — the live grade must point "
        f"at the independent verdict ({[v.name for v in verdicts]})"
    )
    result = subprocess.run(
        [sys.executable, "scripts/check_status_consistency.py"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"C5 grade-provenance gate is red with a verdict on file:\n{result.stdout}\n{result.stderr}"
    )
