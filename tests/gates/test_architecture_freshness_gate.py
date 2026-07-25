"""Audit-2026-07-25 regression (A-11): pin the hand-written architecture layer to src/.

The generated reference (``docs/api/``) was in perfect sync — 55 module docs for 55
modules — while ``docs/architecture/ARCHITECTURE.md``, self-described as "the single
authoritative architecture document", named **none** of six modules added after its last
update. Two were security controls (``provenance.py``, ``limits.py``) and three
(``attest.py``, ``cold_start.py``, ``kb_paths.py``) appeared in no live document at all.

The difference between the two layers was not diligence. One had a freshness gate whose
failure blocked CI; the other had nothing. These tests pin the replacement.
"""

from pathlib import Path

from scripts.check_architecture_freshness import (
    ARCHITECTURE_DOC,
    EXEMPT_STEMS,
    source_modules,
    undocumented,
)


def _fixture(root: Path, *, arch: str = "", adr: str = "", modules: tuple[str, ...] = ()) -> Path:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "docs/architecture").mkdir(parents=True, exist_ok=True)
    (root / "docs/adr").mkdir(parents=True, exist_ok=True)
    for m in modules:
        target = root / "src" / m
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x = 1\n", encoding="utf-8")
    (root / ARCHITECTURE_DOC).write_text(arch, encoding="utf-8")
    (root / "docs/adr/001-x.md").write_text(adr, encoding="utf-8")
    return root


def test_undocumented_module_fails(tmp_path):
    _fixture(tmp_path, arch="Nothing relevant here.\n", modules=("orphan.py",))
    assert "src/orphan.py" in undocumented(tmp_path)


def test_module_named_in_architecture_doc_passes(tmp_path):
    _fixture(tmp_path, arch="The provenance module signs documents.\n", modules=("provenance.py",))
    assert undocumented(tmp_path) == []


def test_module_named_only_in_an_adr_passes(tmp_path):
    """Recording the decision in an ADR is equally valid documentation."""
    _fixture(tmp_path, arch="", adr="We chose limits for DoS ceilings.\n", modules=("limits.py",))
    assert undocumented(tmp_path) == []


def test_nested_package_module_is_checked(tmp_path):
    """The six delegation agents live two levels down and were all undocumented."""
    _fixture(tmp_path, arch="", modules=("delegation/agents/security_agent.py",))
    assert "src/delegation/agents/security_agent.py" in undocumented(tmp_path)


def test_dunder_and_private_modules_are_exempt(tmp_path):
    _fixture(tmp_path, arch="", modules=("__init__.py", "__main__.py", "_internal.py"))
    assert undocumented(tmp_path) == []
    assert "__init__" in EXEMPT_STEMS


def test_source_modules_excludes_exempt_stems(tmp_path):
    _fixture(tmp_path, modules=("real.py", "__init__.py"))
    assert source_modules(tmp_path) == ["src/real.py"]


# NOTE: assertions about the *live tree* satisfying this gate live in the
# claim-surface PR that fixes the tree, not here. This file tests the detector.
