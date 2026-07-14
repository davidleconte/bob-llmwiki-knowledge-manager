"""Behavioural tests for ``src.tools.kb_query.KnowledgeBaseQuery``.

Exercises relevance scoring, listing, cross-reference discovery, statistics,
and the CLI ``main`` entry point. Each test builds a throwaway knowledge base
inside ``tmp_path`` with the four real categories
(``concepts``/``guides``/``references``/``research``) so nothing touches the
repository's live ``docs/knowledge-base``.
"""

from __future__ import annotations

import sys

import pytest

from src.tools.kb_query import KnowledgeBaseQuery, main

CATEGORIES = ("concepts", "guides", "references", "research")


def _make_kb(tmp_path):
    """Create the four category directories and return the tmp_path root."""
    for cat in CATEGORIES:
        (tmp_path / cat).mkdir()
    return tmp_path


# --------------------------------------------------------------------------- #
# Construction
# --------------------------------------------------------------------------- #


class TestConstruction:
    def test_missing_path_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Knowledge base not found"):
            KnowledgeBaseQuery(str(tmp_path / "does-not-exist"))

    def test_existing_path_sets_categories(self, tmp_path):
        kb = KnowledgeBaseQuery(str(_make_kb(tmp_path)))
        assert kb.categories == ["concepts", "guides", "references", "research"]


# --------------------------------------------------------------------------- #
# query()
# --------------------------------------------------------------------------- #


class TestQuery:
    def test_title_match_scores_highest(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "ml.md").write_text(
            "# Machine Learning Basics\n\nSome notes about machine learning.\n"
        )
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("machine learning")
        assert result["total_results"] == 1
        top = result["results"][0]
        assert top["title"] == "Machine Learning Basics"
        assert top["score"] >= 10.0
        assert top["category"] == "concepts"
        assert "preview" in top  # include_content defaults to False

    def test_filename_match_without_content_match_uses_first_lines_preview(self, tmp_path):
        _make_kb(tmp_path)
        # Query word appears in the filename but not in the body -> the
        # filename bonus makes score > 0 while _generate_preview finds no
        # matching line and falls back to the first few lines.
        (tmp_path / "guides" / "neural-networks.md").write_text(
            "# Overview\n\nUnrelated body content here.\nLine three.\n"
        )
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("neural")
        assert result["total_results"] == 1
        top = result["results"][0]
        assert top["matches"] == []
        assert "Overview" in top["preview"]

    def test_heading_and_multiword_phrase_bonus(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "references" / "config.md").write_text(
            "# Reference\n\n## Configuration Options\n\nSet configuration options in the file.\n"
        )
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("configuration options")
        assert result["total_results"] == 1
        top = result["results"][0]
        # +3 heading, +2 adjacent-phrase, plus per-word content weight.
        assert top["score"] > 5.0
        assert any("Configuration Options" in m["text"] for m in top["matches"])

    def test_short_query_word_is_skipped(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "model.md").write_text("# Notes\n\nWe train a model with data.\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        # "ai" (len 2) is skipped; "model" (len 5) still scores.
        result = kb.query("ai model")
        assert result["total_results"] == 1
        assert result["results"][0]["score"] > 0

    def test_include_content_returns_full_body(self, tmp_path):
        _make_kb(tmp_path)
        body = "# Deep Learning\n\nContent about deep learning goes here.\n"
        (tmp_path / "concepts" / "dl.md").write_text(body)
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("deep learning", include_content=True)
        top = result["results"][0]
        assert top["content"] == body
        assert "preview" not in top

    def test_invalid_categories_returns_error(self, tmp_path):
        kb = KnowledgeBaseQuery(str(_make_kb(tmp_path)))
        result = kb.query("anything", categories=["bogus", "concepts"])
        assert "Invalid categories" in result["error"]
        assert "bogus" in result["error"]

    def test_restrict_to_single_category(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "a.md").write_text("# Alpha\n\nalpha topic\n")
        (tmp_path / "guides" / "b.md").write_text("# Alpha\n\nalpha topic\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("alpha", categories=["concepts"])
        assert result["categories_searched"] == ["concepts"]
        assert result["total_results"] == 1
        assert result["results"][0]["category"] == "concepts"

    def test_no_match_returns_empty(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "a.md").write_text("# Alpha\n\nsome text\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("zzzznotpresent")
        assert result["total_results"] == 0
        assert result["results"] == []

    def test_max_results_truncates(self, tmp_path):
        _make_kb(tmp_path)
        for i in range(5):
            (tmp_path / "concepts" / f"doc{i}.md").write_text(
                f"# Topic {i}\n\ncommon keyword body\n"
            )
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("keyword", max_results=2)
        assert result["total_results"] == 5
        assert len(result["results"]) == 2

    def test_untitled_when_no_heading(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "plain.md").write_text("no heading here keyword\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.query("keyword")
        assert result["results"][0]["title"] == "Untitled"


# --------------------------------------------------------------------------- #
# list_documents()
# --------------------------------------------------------------------------- #


class TestListDocuments:
    def test_list_all(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "a.md").write_text("# A\n\nbody\n")
        (tmp_path / "guides" / "b.md").write_text("# B\n\nbody\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.list_documents()
        assert result["total_documents"] == 2
        assert len(result["documents"]["concepts"]) == 1
        doc = result["documents"]["concepts"][0]
        assert doc["file"] == "a.md"
        assert doc["title"] == "A"
        assert doc["line_count"] >= 1

    def test_list_single_category(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "a.md").write_text("# A\n\nbody\n")
        (tmp_path / "guides" / "b.md").write_text("# B\n\nbody\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.list_documents(category="concepts")
        assert result["categories"] == ["concepts"]
        assert result["total_documents"] == 1

    def test_list_invalid_category(self, tmp_path):
        kb = KnowledgeBaseQuery(str(_make_kb(tmp_path)))
        result = kb.list_documents(category="nope")
        assert "Invalid category" in result["error"]


# --------------------------------------------------------------------------- #
# get_cross_references()
# --------------------------------------------------------------------------- #


class TestCrossReferences:
    def test_parses_links_and_referenced_by(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "maindoc.md").write_text(
            "# Main Doc\n\nSee [Guide](guide.md) and [Site](https://example.com).\n"
        )
        (tmp_path / "guides" / "other.md").write_text(
            "# Other\n\nRefers to maindoc.md for details.\n"
        )
        kb = KnowledgeBaseQuery(str(tmp_path))
        result = kb.get_cross_references("concepts/maindoc.md")
        assert result["file"] == "concepts/maindoc.md"
        assert result["title"] == "Main Doc"
        assert {"text": "Guide", "file": "guide.md"} in result["kb_references"]
        assert result["external_references"][0]["url"] == "https://example.com"
        ref_files = [r["file"] for r in result["referenced_by"]]
        assert "guides/other.md" in ref_files

    def test_escaping_path_refused(self, tmp_path):
        kb = KnowledgeBaseQuery(str(_make_kb(tmp_path)))
        result = kb.get_cross_references("../../etc/passwd")
        assert "Invalid file path" in result["error"]

    def test_missing_file(self, tmp_path):
        kb = KnowledgeBaseQuery(str(_make_kb(tmp_path)))
        result = kb.get_cross_references("concepts/ghost.md")
        assert "File not found" in result["error"]


# --------------------------------------------------------------------------- #
# get_statistics()
# --------------------------------------------------------------------------- #


class TestStatistics:
    def test_statistics_aggregate(self, tmp_path):
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "a.md").write_text("# A\n\none two three\n")
        (tmp_path / "concepts" / "b.md").write_text("# B\n\nfour\n")
        (tmp_path / "guides" / "c.md").write_text("# C\n\nfive\n")
        kb = KnowledgeBaseQuery(str(tmp_path))
        stats = kb.get_statistics()
        assert stats["total_documents"] == 3
        assert stats["categories"]["concepts"]["document_count"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["total_lines"] > 0


# --------------------------------------------------------------------------- #
# CLI main()
# --------------------------------------------------------------------------- #


def _kb_with_content(tmp_path):
    for cat in CATEGORIES:
        (tmp_path / cat).mkdir()
    (tmp_path / "concepts" / "maindoc.md").write_text(
        "# Main Doc\n\nAbout searching with [Guide](guide.md) and "
        "[Site](https://example.com).\nSearch keyword lives here.\n"
    )
    (tmp_path / "guides" / "other.md").write_text("# Other\n\nRefers to maindoc.md for details.\n")
    return tmp_path


class TestMainCLI:
    def test_query_text_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(sys, "argv", ["kb", "--kb-path", str(tmp_path), "query", "keyword"])
        main()
        out = capsys.readouterr().out
        assert "Query: keyword" in out
        assert "Main Doc" in out

    def test_query_json_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(
            sys,
            "argv",
            ["kb", "--kb-path", str(tmp_path), "--output", "json", "query", "keyword"],
        )
        main()
        out = capsys.readouterr().out
        assert '"total_results"' in out

    def test_list_text_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(sys, "argv", ["kb", "--kb-path", str(tmp_path), "list"])
        main()
        out = capsys.readouterr().out
        assert "Knowledge Base Documents" in out
        assert "CONCEPTS" in out

    def test_xref_text_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(
            sys, "argv", ["kb", "--kb-path", str(tmp_path), "xref", "concepts/maindoc.md"]
        )
        main()
        out = capsys.readouterr().out
        assert "Cross-References: Main Doc" in out
        assert "guide.md" in out

    def test_xref_error_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(
            sys, "argv", ["kb", "--kb-path", str(tmp_path), "xref", "../../etc/passwd"]
        )
        main()
        out = capsys.readouterr().out
        assert "Error:" in out

    def test_stats_text_output(self, tmp_path, monkeypatch, capsys):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(sys, "argv", ["kb", "--kb-path", str(tmp_path), "stats"])
        main()
        out = capsys.readouterr().out
        assert "Knowledge Base Statistics" in out

    def test_no_command_prints_help_and_exits(self, tmp_path, monkeypatch):
        _kb_with_content(tmp_path)
        monkeypatch.setattr(sys, "argv", ["kb", "--kb-path", str(tmp_path)])
        with pytest.raises(SystemExit):
            main()

    def test_invalid_kb_path_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["kb", "--kb-path", "/no/such/kb/dir", "stats"])
        with pytest.raises(SystemExit):
            main()
