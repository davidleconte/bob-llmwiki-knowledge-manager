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


# ── The live tree must stay green ────────────────────────────────────────────────


def test_live_tree_has_no_undocumented_modules():
    """The condition the audit found violated: every src/ module is written down."""
    missing = undocumented()
    assert missing == [], (
        "these modules appear in neither ARCHITECTURE.md nor any ADR: " + ", ".join(missing)
    )


def test_the_six_audit_modules_are_documented():
    """Explicit regression on the exact modules the audit found missing, so a future
    rewrite of ARCHITECTURE.md cannot silently drop them again."""
    corpus = (Path(ARCHITECTURE_DOC).read_text(encoding="utf-8")).lower()
    for stem in ("attest", "cold_start", "kb_paths", "limits", "provenance", "velocity"):
        assert stem in corpus, f"{stem} missing from the authoritative architecture doc"


def test_security_controls_are_described_not_just_mentioned():
    """provenance/limits are security controls; a bare name-drop is not enough."""
    text = Path(ARCHITECTURE_DOC).read_text(encoding="utf-8")
    assert "Trust and safety controls" in text
    for token in ("verify_document", "MAX_FILE_BYTES", "resolve_within"):
        assert token in text, f"{token} should appear where the control is described"
