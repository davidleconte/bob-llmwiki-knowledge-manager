"""Regression guard: each CI gate script must exit 0 on the current tree.

If any of these tests start failing it means a gate that was passing has been
broken by a subsequent commit — exactly the kind of silent regression this
sub-task exists to catch early.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def _run_gate(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def test_check_savings_claims_exits_zero() -> None:
    """check_savings_claims.py must exit 0 — no unbacked savings figures."""
    result = _run_gate("check_savings_claims.py")
    assert result.returncode == 0, (
        f"check_savings_claims.py exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_check_value_homes_exits_zero() -> None:
    """check_value_homes.py must exit 0 — all values agree with their canonical home."""
    result = _run_gate("check_value_homes.py")
    assert result.returncode == 0, (
        f"check_value_homes.py exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_generate_api_docs_check_exits_zero() -> None:
    """generate_api_docs.py --check must exit 0 — API docs are in sync with src/."""
    result = _run_gate("generate_api_docs.py", "--check")
    assert result.returncode == 0, (
        f"generate_api_docs.py --check exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
