"""D1 / MEM-08: mnemox-lessons.sh bounds Recent Additions to ≤10 on every run.

End-to-end lock on the writer-prune wiring: the shell prepends one entry per run and
then invokes compact_index_recent_additions.py, so an index that had grown past 10
comes back to ≤10 instead of growing unbounded.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "mnemox-lessons.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("python3") is None,
    reason="needs bash + python3",
)


def _seed_kb(root: Path, ra_entries: int) -> Path:
    kb = root / "docs" / "knowledge-base"
    for d in ("concepts", "guides", "references", "research"):
        (kb / d).mkdir(parents=True)
    lines = ["# KB Index", "", "## Recent Additions"]
    for i in range(ra_entries):
        lines.append(f"- 2026-01-{i + 1:02d}: [Doc {i}](concepts/doc{i}.md) - seeded")
        (kb / "concepts" / f"doc{i}.md").write_text(f"# Doc {i}\n")
    lines += ["", "## All Documents", "", "### Concepts"]
    # Every seeded doc is ALSO in the catalog, so trimming Recent Additions is orphan-safe.
    for i in range(ra_entries):
        lines.append(f"- [Doc {i}](concepts/doc{i}.md)")
    lines += ["", "## Usage", ""]
    (kb / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return kb


def _ra_count(index: Path) -> int:
    txt = index.read_text(encoding="utf-8").split("## Recent Additions", 1)[1]
    txt = txt.split("## All Documents", 1)[0]
    return sum(1 for ln in txt.splitlines() if ln.strip().startswith("- "))


def test_mnemox_lessons_caps_recent_additions(tmp_path):
    kb = _seed_kb(tmp_path, ra_entries=15)
    assert _ra_count(kb / "index.md") == 15

    result = subprocess.run(["bash", str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr

    # The run prepends one entry (16) then compacts back to ≤10.
    assert _ra_count(kb / "index.md") <= 10
