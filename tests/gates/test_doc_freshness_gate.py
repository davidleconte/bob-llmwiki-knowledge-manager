"""Audit-2026-07-25 regression (V-6): a document that asserts currency must be current.

STATUS.md declares itself "the canonical maturity status" and every other document is
told to defer to it. At audit time it read ``As of 2026-07-19`` while 18 PRs had merged
after that date, so every doc that dutifully deferred inherited a pre-Wave-2 snapshot.

Nothing caught it because staleness has no syntax — a stale date is perfectly
well-formed, and only its relationship to the commit log makes it wrong.
"""

from datetime import date

import pytest

from scripts.check_doc_freshness import WATCHED, declared_date, is_shallow, stale_documents

# A shallow clone has one commit, so `git log -1 -- <path>` returns it for every path
# and every watched doc reads as modified today. This assertion is unevaluable there —
# skipping says so, where a red would blame the change under review. CI checks out with
# fetch-depth: 0 for the jobs that run this, so the skip should not fire in CI.
needs_history = pytest.mark.skipif(
    is_shallow(), reason="shallow clone: per-file commit dates are not meaningful"
)


@pytest.mark.parametrize(
    "text,expected",
    [
        # STATUS.md's real table-row form. The first draft of the pattern returned None
        # here, which made the live scan pass by *skipping* the file the gate is for.
        ("| **As of** | 2026-07-25 |", date(2026, 7, 25)),
        ("**Last Updated:** 2026-07-18", date(2026, 7, 18)),
        ("**Last updated:** 2026-07-25 · **Maturity:** see STATUS.md", date(2026, 7, 25)),
        ("updated: 2026-07-20", date(2026, 7, 20)),
    ],
)
def test_real_date_forms_parse(text, expected):
    assert declared_date(text) == expected


def test_undated_document_is_ignored():
    assert declared_date("A document with no currency claim at all.") is None


def test_prose_dates_are_out_of_scope():
    """`July 17, 2026` is deliberately not parsed — narrow beats clever here."""
    assert declared_date("**Last Updated:** July 17, 2026") is None


def test_stale_document_is_reported(tmp_path, monkeypatch):
    """The exact relationship the audit found: declared date < last commit date."""
    import scripts.check_doc_freshness as mod

    doc = tmp_path / "STATUS.md"
    doc.write_text("| **As of** | 2026-07-19 |\n", encoding="utf-8")
    monkeypatch.setattr(mod, "last_commit_date", lambda rel, root=None: date(2026, 7, 21))
    stale = mod.stale_documents(tmp_path)
    assert stale and stale[0][0] == "STATUS.md"
    assert stale[0][1] == date(2026, 7, 19)
    assert stale[0][2] == date(2026, 7, 21)


def test_current_document_passes(tmp_path, monkeypatch):
    import scripts.check_doc_freshness as mod

    (tmp_path / "STATUS.md").write_text("| **As of** | 2026-07-25 |\n", encoding="utf-8")
    monkeypatch.setattr(mod, "last_commit_date", lambda rel, root=None: date(2026, 7, 25))
    assert mod.stale_documents(tmp_path) == []


def test_same_day_is_not_stale(tmp_path, monkeypatch):
    """Equal dates pass: a doc updated in the same commit is current, not late."""
    import scripts.check_doc_freshness as mod

    (tmp_path / "docs/INDEX.md").parent.mkdir(parents=True)
    (tmp_path / "docs/INDEX.md").write_text("**Last Updated:** 2026-07-25\n", encoding="utf-8")
    monkeypatch.setattr(mod, "last_commit_date", lambda rel, root=None: date(2026, 7, 25))
    assert mod.stale_documents(tmp_path) == []


def test_status_md_is_watched():
    """The document the finding was about must be in scope."""
    assert "STATUS.md" in WATCHED


@needs_history
def test_live_tree_is_fresh():
    stale = stale_documents()
    assert stale == [], "stale: " + ", ".join(f"{r} ({d} < {c})" for r, d, c in stale)
