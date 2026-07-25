"""C3 / ATK-GATE-07: the gate-integrity structural check.

A single owner authors the code, the gates, and the claims those gates check
(bus-factor 1). Absent a second human reviewer, ``scripts/check_gate_integrity.py``
mechanically blocks the single-PR "weaken the gate + plant the overclaim" attack: a
PR whose diff touches BOTH a gate definition and a claim surface fails. This suite
pins that behaviour and the SECURITY.md / CODEOWNERS disclosure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_gate_integrity import check, is_claim_surface, is_gate_file

_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "path",
    [
        "config/gates/gate-config.yaml",
        "scripts/check_savings_claims.py",
        "scripts/check_gate_integrity.py",
        "src/validation/__init__.py",
        "./scripts/check_metric_claims.py",  # leading ./ normalised
    ],
)
def test_gate_files_classified(path):
    assert is_gate_file(path)
    assert not is_claim_surface(path)


@pytest.mark.parametrize(
    "path",
    [
        "STATUS.md",
        "README.md",
        "docs/knowledge-base/concepts/token-optimization.md",
        "docs/architecture/ARCHITECTURE.md",
    ],
)
def test_claim_surfaces_classified(path):
    assert is_claim_surface(path)
    assert not is_gate_file(path)


@pytest.mark.parametrize(
    "path",
    [
        "src/optimizer/token_counter.py",
        "tests/gates/test_gate_integrity.py",
        ".github/CODEOWNERS",
        "docs/api/root/pricing.md",  # generated reference -> NOT a claim surface
        # SECURITY.md moved OUT of this list on 2026-07-25 — see
        # test_security_md_is_now_a_claim_surface below.
    ],
)
def test_neutral_files_are_neither(path):
    assert not is_gate_file(path)
    assert not is_claim_surface(path)


# ── Audit 2026-07-25: scope corrections (G-1, G-2) ────────────────────────────────


def test_ci_workflow_is_a_gate_definition():
    """G-2: a gate is only a gate if CI invokes it, so the workflow IS a gate def.

    Before this, one PR could delete a gate's CI step and plant a claim in README.md
    and pass — the exact ATK-GATE-07 attack, through an unwatched path. Demonstrated
    by the audit: tests/performance/test_dos_hardening.py ran in no CI job for weeks.
    """
    assert is_gate_file(".github/workflows/ci.yml")
    assert check([".github/workflows/ci.yml", "README.md"]), (
        "disabling a CI gate step alongside a claim edit must be blocked"
    )


def test_security_md_is_now_a_claim_surface():
    """SECURITY.md documents the gate-independence posture itself — a gate change must
    not ride alongside an edit to it."""
    assert is_claim_surface("SECURITY.md")


@pytest.mark.parametrize("path", ["AGENTS.md", "INTEGRATIONS.md"])
def test_maturity_bearing_root_docs_are_claim_surfaces(path):
    """AGENTS.md was found asserting a ~51% savings figure and a 4.8x-understated LOC
    count; INTEGRATIONS.md carries the compression baseline."""
    assert is_claim_surface(path)


def test_submission_pack_is_a_claim_surface():
    """G-1: 13 tracked files written for external judges, previously outside every
    gate's scope."""
    assert is_claim_surface("2026_IBMer_Watsonx_Challenge/03-solution-impact.md")
    assert check(
        ["scripts/check_savings_claims.py", "2026_IBMer_Watsonx_Challenge/03-solution-impact.md"]
    )


def test_ci_only_change_still_allowed():
    """Tightening CI without touching a claim must remain a single clean PR."""
    assert not check([".github/workflows/ci.yml", "scripts/check_md_links.py"])


def test_gate_integrity_blocks_mixed_pr():
    """RED->GREEN: a diff touching both a gate and a claim surface is flagged."""
    problems = check(["scripts/check_savings_claims.py", "STATUS.md"])
    assert problems, "a gate + claim co-modification must be flagged"
    assert "gate" in problems[0].lower() and "claim" in problems[0].lower()


def test_gate_only_pr_passes():
    assert check(["scripts/check_savings_claims.py", "config/gates/gate-config.yaml"]) == []


def test_claim_only_pr_passes():
    assert check(["STATUS.md", "README.md", "docs/knowledge-base/concepts/x.md"]) == []


def test_validation_plus_generated_api_docs_passes():
    """A src/validation change + its regenerated docs/api/ must NOT be blocked.

    docs/api/** is generated and pinned to src/ by the freshness gate; treating it
    as a claim surface would contradict the mandatory API-doc regeneration.
    """
    assert check(["src/validation/measure.py", "docs/api/validation/measure.md"]) == []


def test_empty_diff_passes():
    assert check([]) == []


def test_security_md_has_gate_independence_section():
    """SECURITY.md carries §Gate Independence and CODEOWNERS no longer dangles."""
    security = (_REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    codeowners = (_REPO_ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")

    assert "## Gate Independence" in security, "SECURITY.md must document §Gate Independence"
    # CODEOWNERS references the section + the structural check -> both must exist.
    assert "Gate Independence" in codeowners
    assert "check_gate_integrity.py" in codeowners
    assert (_REPO_ROOT / "scripts" / "check_gate_integrity.py").exists()


def test_gate_integrity_cli_passes_on_gate_plus_nonclaim():
    """The CLI exits 0 for a gate + genuinely-neutral diff.

    SECURITY.md was dropped from this case on 2026-07-25: it became a claim surface,
    because it is where the gate-independence posture is documented.
    """
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_gate_integrity.py",
            "scripts/check_gate_integrity.py",
            ".github/CODEOWNERS",
            "src/optimizer/token_counter.py",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_gate_integrity_cli_fails_on_mixed():
    """The CLI exits 1 for a gate + claim diff."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_gate_integrity.py",
            "scripts/check_savings_claims.py",
            "README.md",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
