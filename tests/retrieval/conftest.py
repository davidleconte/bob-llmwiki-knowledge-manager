"""Shared fixtures for retrieval regression tests.
Re-exports the tmp_kb fixture from tests/security/conftest.py for convenience.
"""

import textwrap
from pathlib import Path

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
