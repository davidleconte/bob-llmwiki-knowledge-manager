"""CODE-01/CODE-02 regression: #slug fix and retrieval stack wiring."""
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from src.tools.kb_query import KnowledgeBaseQuery


# ---------------------------------------------------------------------------
# CODE-01: #slug fragment in index doc_ids caused silent full-scan fallback
# ---------------------------------------------------------------------------

def test_slug_stripped_from_doc_id_before_path_join(tmp_kb):
    """doc_ids like 'concepts/foo.md#intro' must resolve to 'concepts/foo.md' (CODE-01)."""
    # Create a document in the tmp KB
    doc = tmp_kb / "concepts" / "retrieval-test.md"
    doc.write_text("# Retrieval Test\nThis document is about retrieval testing.", encoding="utf-8")

    # Mock a PersistentEmbeddingIndex that returns a chunk doc_id with #slug
    mock_index = MagicMock()
    mock_index.doc_count = 1
    # Return the chunk id WITH the fragment — this is what the real index returns
    mock_index.search.return_value = [("concepts/retrieval-test.md#intro", 0.95)]

    kbq = KnowledgeBaseQuery(str(tmp_kb), index=mock_index, embedding_weight=0.7)

    # Track whether the full-scan fallback was invoked
    full_scan_calls = []
    original_full_scan = kbq._query_full_scan

    def tracked_full_scan(*args, **kwargs):
        full_scan_calls.append(args)
        return original_full_scan(*args, **kwargs)

    kbq._query_full_scan = tracked_full_scan

    result = kbq.query("retrieval testing", include_content=False)

    # The index path must have returned results (no full-scan fallback needed)
    assert result["total_results"] > 0, "No results returned — index path may still be broken"
    # If the index returned a hit, full_scan should not have been called
    # (the result came from the index path, not the full-scan fallback)
    assert len(full_scan_calls) == 0, (
        "_query_full_scan was called — suggests index path fell through to fallback "
        "(possible #slug bug still present)"
    )


def test_slug_with_missing_file_falls_back_gracefully(tmp_kb):
    """If the file from a #slug doc_id does not exist, fall back to full scan without crashing."""
    mock_index = MagicMock()
    mock_index.doc_count = 1
    mock_index.search.return_value = [("concepts/nonexistent.md#section", 0.90)]

    kbq = KnowledgeBaseQuery(str(tmp_kb), index=mock_index, embedding_weight=0.7)
    # Should not raise — gracefully falls back to full scan
    result = kbq.query("anything")
    assert "results" in result


# ---------------------------------------------------------------------------
# CODE-02: index and graph must be wired (passed to KnowledgeBaseQuery)
# ---------------------------------------------------------------------------

def test_index_wired_to_kb_search(tmp_kb):
    """KnowledgeBaseQuery constructed with index= must use it for search (CODE-02)."""
    doc = tmp_kb / "concepts" / "wiring-test.md"
    doc.write_text("# Wiring Test\nThis is a wiring test document.", encoding="utf-8")

    mock_index = MagicMock()
    mock_index.doc_count = 1
    mock_index.search.return_value = [("concepts/wiring-test.md#body", 0.88)]

    kbq = KnowledgeBaseQuery(str(tmp_kb), index=mock_index, embedding_weight=0.7)
    kbq.query("wiring test")

    # The mock index's search method should have been called
    mock_index.search.assert_called_once(), "index.search was not called — index not wired"


def test_query_without_index_uses_full_scan(tmp_kb):
    """Without index=, _query_full_scan is the path (baseline check)."""
    doc = tmp_kb / "concepts" / "scan-test.md"
    doc.write_text("# Scan Test\nFull scan baseline document.", encoding="utf-8")

    kbq = KnowledgeBaseQuery(str(tmp_kb))  # no index=
    full_scan_calls = []
    original = kbq._query_full_scan

    def tracked(*args, **kwargs):
        full_scan_calls.append(args)
        return original(*args, **kwargs)

    kbq._query_full_scan = tracked
    kbq.query("scan test")
    assert len(full_scan_calls) > 0, "_query_full_scan was not called without index"
