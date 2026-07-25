"""Audit-2026-07-25 regression: the Markdown link gate must catch what CI missed.

The tree carried ~103 broken relative references that no gate saw, because the only
link checker (``scripts/validate-kb.sh``) is scoped to ``docs/knowledge-base/`` and
because macOS resolves wrong-case paths that GitHub and Linux CI 404.

These tests pin the two properties that make :mod:`scripts.check_md_links` able to see
that class of defect at all:

1. It resolves against the **git index**, not the filesystem — so a case-only mismatch
   is a violation even though ``Path.exists()`` would return True on APFS.
2. It distinguishes *case-mismatch* from *missing* from *citation-in-link*, because the
   three have different fixes.

Plus the standard gate contract: frozen audit trail is exempt, and the detector can
demonstrably fail (a gate that cannot fail proves nothing).
"""

from scripts.check_md_links import (
    classify,
    is_exempt,
    iter_links,
    scan,
    tracked_dirs,
)

TRACKED = {
    "docs/SLA.md",
    "docs/security/threat-model.md",
    "docs/knowledge-base/index.md",
    "docs/README.md",
    "docs/adr/README.md",
    "config/custom_modes.yaml",
}
DIRS = tracked_dirs(TRACKED)


def _kind(source: str, target: str) -> str | None:
    verdict = classify(source, target, TRACKED, DIRS)
    return None if verdict is None else verdict[0]


# ── The signature defect: case-only mismatch ──────────────────────────────────────


def test_case_only_mismatch_is_flagged_not_silently_resolved():
    """`sla.md` vs tracked `SLA.md` — the exact defect the inverted CI rule enforced."""
    assert _kind("docs/README.md", "sla.md") == "case-mismatch"


def test_uppercase_kb_index_is_flagged():
    """`knowledge-base/INDEX.md` broke 6 live links; disk is lowercase `index.md`."""
    assert _kind("docs/README.md", "knowledge-base/INDEX.md") == "case-mismatch"


def test_correct_case_passes():
    assert _kind("docs/README.md", "SLA.md") is None
    assert _kind("docs/README.md", "knowledge-base/index.md") is None


def test_case_mismatch_detail_names_the_actual_file():
    """The fix must be obvious from the message alone."""
    verdict = classify("docs/README.md", "sla.md", TRACKED, DIRS)
    assert verdict is not None
    assert "docs/SLA.md" in verdict[1]


# ── Case + separator rename is `missing`, not `case-mismatch` ──────────────────────


def test_case_plus_separator_rename_is_missing():
    """THREAT_MODEL.md -> threat-model.md changes `_`->`-` too, so lowercasing alone
    cannot find it. Reporting it as `missing` is correct, and this test exists because
    the gate's own self-test caught the author expecting `case-mismatch` here."""
    assert _kind("docs/README.md", "security/THREAT_MODEL.md") == "missing"


def test_deleted_target_is_missing():
    assert _kind("docs/README.md", "archive/BOOK_TABLE_OF_CONTENTS.md") == "missing"


# ── path:LINE citations written as link targets ───────────────────────────────────


def test_path_line_citation_is_flagged_even_when_file_exists():
    """`](../config/custom_modes.yaml:180)` — file is real, link 404s on GitHub."""
    assert _kind("docs/README.md", "../config/custom_modes.yaml:180") == "citation-in-link"


def test_path_line_citation_on_missing_file_is_distinguished():
    assert _kind("docs/README.md", "../config/nope.yaml:12") == "missing+citation"


# ── Things that must never be flagged ─────────────────────────────────────────────


def test_external_and_anchor_links_are_ignored():
    for target in ("https://example.com/x.md", "http://example.com", "mailto:a@b.c", "#heading"):
        assert _kind("docs/README.md", target) is None


def test_placeholders_are_ignored():
    """Prose describing link syntax, and template stubs, are not real links."""
    for target in ("path", "target", "./related-concept.md"):
        assert _kind("docs/README.md", target) is None


def test_directory_target_resolves():
    """`](adr/)` points at a directory implied by the index, not a file."""
    assert _kind("docs/README.md", "adr/") is None


def test_anchor_is_stripped_before_resolution():
    assert _kind("docs/README.md", "SLA.md#latency") is None


# ── Fenced code blocks are not links ─────────────────────────────────────────────


def test_links_inside_fences_are_not_extracted():
    text = "\n".join(
        [
            "[real](a.md)",
            "```",
            "[not a link](TOTALLY_MISSING.md)",
            "```",
            "[real2](b.md)",
        ]
    )
    targets = [t for _, t in iter_links(text)]
    assert targets == ["a.md", "b.md"]


def test_tilde_fences_also_suppress():
    text = "~~~\n[x](MISSING.md)\n~~~\n"
    assert iter_links(text) == []


# ── Frozen audit trail is exempt, by explicit allowlist ──────────────────────────


def test_frozen_trees_are_exempt():
    for rel in (
        "docs/archive/book-chapter-01.md",
        "docs/architecture/deprecated/BATCH.md",
        "docs/project-management/planning/gap-closure-plan.md",
    ):
        assert is_exempt(rel), rel


def test_dated_snapshot_is_exempt_anywhere():
    assert is_exempt("docs/knowledge-base/research/audit-2026-07-13-institutional.md")


def test_live_docs_are_not_exempt():
    for rel in ("README.md", "docs/README.md", "docs/INDEX.md", "AGENTS.md"):
        assert not is_exempt(rel), rel


def test_fixtures_and_vendored_packs_are_exempt():
    assert is_exempt("evaluation/data/synthetic/knowledge_bases/scenario_4_kb/research/x.md")
    assert is_exempt(".bob/skills/techzone/README.md")


# ── The gate must be able to fail ────────────────────────────────────────────────


def test_scan_flags_a_planted_defect(tmp_path, monkeypatch):
    """A gate that cannot fail proves nothing — plant a bad link and require a hit."""
    import scripts.check_md_links as mod

    src = tmp_path / "live.md"
    src.write_text("[bad](does/not/exist.md)\n", encoding="utf-8")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    violations = mod.scan(tracked={"live.md"})
    assert violations, "planted broken link was not detected"
    assert violations[0][2] == "missing"


def test_scan_clean_on_a_resolvable_tree(tmp_path, monkeypatch):
    import scripts.check_md_links as mod

    (tmp_path / "a.md").write_text("[ok](b.md)\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n", encoding="utf-8")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    assert mod.scan(tracked={"a.md", "b.md"}) == []


def test_scan_returns_the_documented_tuple_shape():
    """Downstream (CI output, --list) depends on (source, line, kind, detail)."""
    for row in scan()[:5]:
        assert len(row) == 4
        source, line_no, kind, detail = row
        assert isinstance(source, str) and isinstance(line_no, int)
        assert kind in {"case-mismatch", "missing", "citation-in-link", "missing+citation"}
        assert isinstance(detail, str)
