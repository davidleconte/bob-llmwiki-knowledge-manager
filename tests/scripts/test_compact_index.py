"""D1 / MEM-08: compacting Recent Additions is bounded AND orphan-safe.

`compact()` trims `## Recent Additions` to `keep` entries. The load-bearing property:
a doc referenced ONLY in Recent Additions is not lost — it is preserved in the
`## All Documents` catalog so `validate-kb.sh`'s orphan check still finds it.
"""

from __future__ import annotations

import re

from scripts.compact_index_recent_additions import compact

_MD = re.compile(r"\]\(([^)]+)\)")


def _paths(text: str) -> set[str]:
    return {
        m.group(1).split("#")[0].lstrip("./")
        for m in _MD.finditer(text)
        if m.group(1).endswith(".md")
    }


def _ra_entries(text: str) -> list[str]:
    ra = text.split("## Recent Additions", 1)[1].split("## All Documents", 1)[0]
    return [ln for ln in ra.splitlines() if ln.strip().startswith("- ")]


_FIXTURE = (
    "# Index\n\n"
    "## Recent Additions\n"
    "- 2026-01-05: [A](concepts/a.md) - d\n"
    "- 2026-01-04: [B](concepts/b.md) - d\n"
    "- 2026-01-03: [C](concepts/c.md) - d\n"
    "- 2026-01-02: [Orphan](research/orphan.md) - d\n"  # only in RA -> must survive
    "- 2026-01-01: [D](concepts/d.md) - d\n"
    "\n"
    "## All Documents\n\n"
    "### Concepts\n"
    "- [A](concepts/a.md)\n- [B](concepts/b.md)\n- [C](concepts/c.md)\n- [D](concepts/d.md)\n"
    "\n"
    "## Usage\n"
)


def test_trims_to_keep():
    out = compact(_FIXTURE, keep=3)
    assert len(_ra_entries(out)) == 3
    # The three most-recent are kept.
    kept = "\n".join(_ra_entries(out))
    assert "concepts/a.md" in kept and "concepts/b.md" in kept and "concepts/c.md" in kept


def test_no_doc_is_orphaned():
    """Every doc referenced before the trim is still referenced after it."""
    before = _paths(_FIXTURE)
    after = _paths(compact(_FIXTURE, keep=3))
    assert before <= after, f"lost references: {before - after}"


def test_orphan_only_doc_is_reconciled_into_catalog():
    out = compact(_FIXTURE, keep=3)
    # 'Orphan' was only in Recent Additions and is dropped from it (beyond keep=3)…
    assert "research/orphan.md" not in "\n".join(_ra_entries(out))
    # …but preserved under the reconcile heading so it is not orphaned.
    assert "### Reconciled from Recent Additions" in out
    assert "research/orphan.md" in out


def test_catalog_only_dropped_entry_is_not_reconciled():
    """A dropped entry already in All Documents is simply removed, not duplicated."""
    out = compact(_FIXTURE, keep=3)
    # concepts/d.md (dropped, but in the catalog) must NOT appear under Reconciled.
    reconciled = out.split("### Reconciled from Recent Additions", 1)
    if len(reconciled) == 2:
        assert "concepts/d.md" not in reconciled[1].split("## Usage")[0]


def test_idempotent():
    once = compact(_FIXTURE, keep=3)
    assert compact(once, keep=3) == once


def test_already_compact_is_unchanged():
    small = (
        "# Index\n\n## Recent Additions\n- 2026-01-01: [A](concepts/a.md) - d\n\n"
        "## All Documents\n\n### Concepts\n- [A](concepts/a.md)\n\n## Usage\n"
    )
    assert compact(small, keep=10) == small
