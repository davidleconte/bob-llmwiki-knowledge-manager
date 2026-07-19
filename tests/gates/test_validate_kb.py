"""Regression test for scripts/validate-kb.sh.

Verifies two exit-code contracts:
  1. The script exits 1 when a non-research KB document contains a broken
     Markdown link  (guards the subshell counter fix).
  2. The script exits 0 on a clean KB with no broken links.

These tests do NOT require any Python dependencies beyond the standard library;
they spin up a minimal temp KB directory and invoke the shell script directly.
"""

import subprocess
import tempfile
import textwrap
from pathlib import Path

SCRIPT = str(Path(__file__).parent.parent.parent / "scripts" / "validate-kb.sh")


def _make_minimal_kb(root: Path, *, with_broken_link: bool = False) -> None:
    """Scaffold the minimum KB structure validate-kb.sh requires."""
    for subdir in ("concepts", "guides", "references", "research"):
        (root / subdir).mkdir(parents=True, exist_ok=True)

    (root / "index.md").write_text("# Index\n", encoding="utf-8")

    # A well-formed concept document with complete frontmatter.
    good_doc = textwrap.dedent(
        """\
        ---
        title: "Test Concept"
        category: concept
        tags: [test]
        created: 2026-01-01
        updated: 2026-01-01
        status: active
        ---

        # Test Concept

        Some content with a [valid self-reference](./test-concept.md).
        """
    )
    (root / "concepts" / "test-concept.md").write_text(good_doc, encoding="utf-8")

    if with_broken_link:
        broken_doc = textwrap.dedent(
            """\
            ---
            title: "Broken"
            category: guide
            tags: [test]
            created: 2026-01-01
            updated: 2026-01-01
            status: active
            ---

            # Broken

            [This link is broken](./no-such-file.md)
            """
        )
        (root / "guides" / "broken.md").write_text(broken_doc, encoding="utf-8")


def _run_script(kb_root: Path) -> subprocess.CompletedProcess:
    """Run validate-kb.sh with KB_DIR overridden to kb_root."""
    # We patch KB_DIR by writing a tiny wrapper that re-sets the variable
    # before sourcing the real script.  A sed substitution is simpler and
    # avoids mutating the real script.
    patched_script = Path(tempfile.mkstemp(suffix=".sh")[1])
    original = Path(SCRIPT).read_text(encoding="utf-8")
    patched_script.write_text(
        original.replace('KB_DIR="docs/knowledge-base"', f'KB_DIR="{kb_root}"'),
        encoding="utf-8",
    )
    patched_script.chmod(0o755)
    try:
        return subprocess.run(
            ["bash", str(patched_script)],
            capture_output=True,
            text=True,
            cwd=str(kb_root),  # run from the temp dir so root-hygiene check is neutral
        )
    finally:
        patched_script.unlink(missing_ok=True)


class TestValidateKbScript:
    """validate-kb.sh exit-code contract tests."""

    def test_exits_zero_on_clean_kb(self, tmp_path):
        """A KB with no broken links must exit 0."""
        _make_minimal_kb(tmp_path, with_broken_link=False)
        result = _run_script(tmp_path)
        assert result.returncode == 0, (
            f"Expected exit 0 on clean KB.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "No broken links found" in result.stdout

    def test_exits_nonzero_on_broken_link_in_guide(self, tmp_path):
        """A broken link in a non-research doc must exit 1 (subshell bug guard)."""
        _make_minimal_kb(tmp_path, with_broken_link=True)
        result = _run_script(tmp_path)
        assert result.returncode == 1, (
            f"Expected exit 1 when broken link present.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "Broken link" in result.stdout

    def test_research_broken_link_is_informational_only(self, tmp_path):
        """A broken link inside research/ must NOT cause exit 1 (frozen snapshot rule)."""
        _make_minimal_kb(tmp_path, with_broken_link=False)
        research_doc = textwrap.dedent(
            """\
            ---
            title: "Old Research"
            category: research
            tags: [test]
            created: 2026-01-01
            updated: 2026-01-01
            status: active
            ---

            # Old Research

            [Deleted artefact](./deleted-artefact.md)
            """
        )
        (tmp_path / "research" / "old-research.md").write_text(research_doc, encoding="utf-8")
        result = _run_script(tmp_path)
        # Should still exit 0 — research/ links are informational
        assert result.returncode == 0, (
            f"Expected exit 0 for broken link in research/ (informational only).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "informational" in result.stdout
