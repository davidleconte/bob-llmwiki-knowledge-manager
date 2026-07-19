"""ATK-FS-01: symlink escape via KB read paths.

Verifies that KnowledgeBaseQuery never returns content from files that
are symlinks or whose resolved path escapes the KB root, regardless of
which internal code path (full-scan vs index) is exercised.
"""
import os
import pytest
from pathlib import Path
from src.tools.kb_query import KnowledgeBaseQuery


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def kb_with_symlink(tmp_path):
    """Minimal KB with one legitimate doc and one symlink pointing outside."""
    kb = tmp_path / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)

    # Legitimate document — must survive; trust_tier: verified so content is not withheld
    (kb / "concepts" / "legit.md").write_text(
        "---\ntitle: Real Doc\ntrust_tier: verified\n---\n# Real Doc\nSafe content."
    )

    # Determine a target outside the KB root
    if Path("/etc/passwd").exists():
        target = "/etc/passwd"
    else:
        secret = tmp_path / "secret.txt"
        secret.write_text("SECRET_CONTENT")
        target = str(secret)

    # Plant the symlink inside the KB tree
    os.symlink(target, kb / "references" / "leak.md")

    return kb, target


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _all_content(result: dict) -> str:
    """Concatenate every content/preview string from a query result dict."""
    return " ".join(
        r.get("content", r.get("preview", "")) for r in result.get("results", [])
    )


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def test_symlink_not_returned_in_query(kb_with_symlink):
    """High-level query() must not expose symlinked-file contents."""
    kb, _target = kb_with_symlink
    kbq = KnowledgeBaseQuery(str(kb))
    result = kbq.query("root", include_content=True)
    content = _all_content(result)
    assert "SECRET_CONTENT" not in content
    assert "root:x:" not in content  # /etc/passwd marker


def test_symlink_not_returned_in_full_scan(kb_with_symlink):
    """_query_full_scan() must not expose symlinked-file contents."""
    kb, _target = kb_with_symlink
    kbq = KnowledgeBaseQuery(str(kb))
    result = kbq._query_full_scan("root", ["references"], 10, True)
    content = " ".join(r.get("content", "") for r in result.get("results", []))
    assert "SECRET_CONTENT" not in content
    assert "root:x:" not in content


def test_legitimate_doc_still_returned(kb_with_symlink):
    """The legitimate document must not be suppressed by the symlink guard."""
    kb, _target = kb_with_symlink
    kbq = KnowledgeBaseQuery(str(kb))
    result = kbq._query_full_scan("Safe content", ["concepts"], 10, True)
    content = " ".join(r.get("content", "") for r in result.get("results", []))
    assert "Safe content" in content


def test_list_documents_excludes_symlink(kb_with_symlink):
    """list_documents() must not list the symlinked file."""
    kb, _target = kb_with_symlink
    kbq = KnowledgeBaseQuery(str(kb))
    result = kbq.list_documents(category="references")
    files = [doc["file"] for doc in result.get("documents", {}).get("references", [])]
    assert "leak.md" not in files


def test_get_statistics_excludes_symlink(kb_with_symlink):
    """get_statistics() must not count or read the symlinked file."""
    kb, _target = kb_with_symlink
    kbq = KnowledgeBaseQuery(str(kb))
    # Should not raise; symlink is silently skipped
    stats = kbq.get_statistics()
    assert "references" in stats["categories"]
    # The symlinked file must not have inflated the document count
    assert stats["categories"]["references"]["document_count"] == 0
