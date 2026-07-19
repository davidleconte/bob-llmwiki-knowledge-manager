"""Shared fixtures for adversarial security regression tests."""

import os
import textwrap
from pathlib import Path
from typing import Optional

import pytest


@pytest.fixture
def tmp_kb(tmp_path: Path) -> Path:
    """Create a minimal KB directory structure in a temp directory."""
    kb = tmp_path / "knowledge-base"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    (kb / "concepts" / "example.md").write_text(
        textwrap.dedent("""\
            ---
            title: Example Concept
            trust_tier: verified
            ---
            # Example Concept
            This is a test document about example concepts.
        """),
        encoding="utf-8",
    )
    return kb


def plant_symlink(kb_dir: Path, category: str, name: str, target: str) -> Path:
    """Plant a symlink inside a KB category directory pointing at target."""
    link = kb_dir / category / name
    os.symlink(target, link)
    return link


def plant_document(
    kb_dir: Path,
    category: str,
    name: str,
    content: str,
    frontmatter: Optional[dict] = None,
) -> Path:
    """Write a KB document with optional YAML frontmatter."""
    doc = kb_dir / category / name
    if frontmatter:
        fm_str = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
        text = f"---\n{fm_str}\n---\n\n{content}"
    else:
        text = content
    doc.write_text(text, encoding="utf-8")
    return doc


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# No pytest fixture wrappers needed: import plain helpers directly in tests.
# ---------------------------------------------------------------------------
