"""MEM-11: the correction loop verifies pointer rewrites with validate-kb.sh.

The root cause (counter-audit 2026-07-19): a documented pointer "fix" introduced two
new broken pointers because the correction step ran no verification. The remedy is
that any pointer rewrite MUST be followed by ``scripts/validate-kb.sh``, which exits
non-zero on a broken link and so blocks a correction that dangles a reference.

These tests lock that verification mechanism: a rewrite that breaks a link is caught
(exit 1); an intact KB passes (exit 0). The procedure that must invoke it is
documented in ``.bob/skills/knowledge-manager/SKILL.md`` (Correction Verification).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE = REPO_ROOT / "scripts" / "validate-kb.sh"

# validate-kb.sh uses perl to strip code fences and extract links.
pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("perl") is None,
    reason="validate-kb.sh needs bash + perl",
)


def _make_kb(root: Path) -> Path:
    kb = root / "docs" / "knowledge-base"
    for d in ("concepts", "guides", "references", "research"):
        (kb / d).mkdir(parents=True)
    (kb / "concepts" / "target.md").write_text("# Target\n", encoding="utf-8")
    return kb


def _run_validate(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(VALIDATE)], cwd=cwd, capture_output=True, text=True)


def test_intact_pointers_pass(tmp_path):
    """A KB whose index pointer resolves passes the post-correction check."""
    kb = _make_kb(tmp_path)
    (kb / "index.md").write_text(
        "# Index\n\n## Concepts\n- [Target](concepts/target.md)\n", encoding="utf-8"
    )
    result = _run_validate(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_correction_loop_verifies(tmp_path):
    """A pointer rewrite that breaks a link is caught by post-rewrite validate-kb.sh."""
    kb = _make_kb(tmp_path)
    index = kb / "index.md"
    index.write_text("# Index\n\n## Concepts\n- [Target](concepts/target.md)\n", encoding="utf-8")
    assert _run_validate(tmp_path).returncode == 0, "baseline KB must be clean"

    # Simulate a bad correction: rewrite the pointer to a doc that does not exist.
    index.write_text(
        "# Index\n\n## Concepts\n- [Target](concepts/renamed-typo.md)\n",
        encoding="utf-8",
    )
    result = _run_validate(tmp_path)
    assert result.returncode == 1, (
        "post-rewrite validate-kb.sh must block a dangling pointer (MEM-11)"
    )
    assert "broken link" in (result.stdout + result.stderr).lower()
