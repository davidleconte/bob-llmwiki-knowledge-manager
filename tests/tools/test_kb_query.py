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

    def test_file_deleted_after_resolution_returns_error_not_exception(self, tmp_path):
        """TOCTOU regression: file exists during resolve but is removed before open().

        Previously the code called full_path.exists() → open(); removing the
        exists() check and catching FileNotFoundError on open() means a file
        deleted in the TOCTOU window returns an error dict rather than an
        unhandled exception.
        """
        kb_root = _make_kb(tmp_path)
        p = kb_root / "concepts" / "disappearing.md"
        p.write_text("# Disappearing\n\n[link](other.md)\n")
        kb = KnowledgeBaseQuery(str(kb_root))
        p.unlink()

        result = kb.get_cross_references("concepts/disappearing.md")
        assert "error" in result
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


# --------------------------------------------------------------------------- #
# Embedding scorer (P1-1 / ADR-014)
# --------------------------------------------------------------------------- #


class TestEmbeddingScorer:
    """Tests for the hybrid keyword + embedding scoring path."""

    def test_embedding_weight_zero_uses_keyword_only(self, tmp_path):
        """Default weight=0.0: no EmbeddingGenerator import, keyword scorer unchanged."""
        from src.cache.embeddings import EmbeddingGenerator

        _make_kb(tmp_path)
        (tmp_path / "concepts" / "cache.md").write_text(
            "# Cache Design\n\nThis document covers cache eviction strategies.\n"
        )
        # Provide an embedder but leave weight at 0 — embedding must NOT be called.
        embedder = EmbeddingGenerator()
        kb = KnowledgeBaseQuery(str(tmp_path), embedder=embedder, embedding_weight=0.0)
        result = kb.query("cache eviction")
        assert result["total_results"] == 1
        # score must equal pure keyword score (>0 because word matches exist)
        assert result["results"][0]["score"] > 0
        # embeddings_cache must be empty: the embedding path was not entered
        assert embedder.cache_size() == 0

    def test_embedding_weight_nonzero_blends_scores(self, tmp_path):
        """Weight=0.5: result is a blend; score > 0; embedder was called."""
        from src.cache.embeddings import EmbeddingGenerator

        _make_kb(tmp_path)
        body = "# Token Optimization\n\nReducing token counts with caching and compression.\n"
        (tmp_path / "concepts" / "tokens.md").write_text(body)
        embedder = EmbeddingGenerator()
        kb = KnowledgeBaseQuery(str(tmp_path), embedder=embedder, embedding_weight=0.5)
        result = kb.query("token caching")
        assert result["total_results"] == 1
        assert result["results"][0]["score"] > 0
        # The query "token caching" embedding was cached (use_cache=True for queries)
        assert embedder.cache_size() >= 1

    def test_embedder_uses_cache_false_for_documents(self, tmp_path):
        """Document content must NOT be cached (AF-5 memory safety / ADR-014)."""
        from unittest.mock import patch

        from src.cache.embeddings import EmbeddingGenerator

        _make_kb(tmp_path)
        doc_content = "# Memory Safety\n\nDocument content that is large and unique.\n"
        (tmp_path / "concepts" / "memory.md").write_text(doc_content)
        embedder = EmbeddingGenerator()
        kb = KnowledgeBaseQuery(str(tmp_path), embedder=embedder, embedding_weight=0.3)

        # Spy on generate() calls to assert use_cache=False for doc content
        original_generate = embedder.generate
        calls = []

        def spy_generate(text, use_cache=True):
            calls.append((text[:50], use_cache))
            return original_generate(text, use_cache=use_cache)

        with patch.object(embedder, "generate", side_effect=spy_generate):
            kb.query("memory large document")

        # Exactly two generate() calls per matching document:
        #   1) query text        → use_cache=True
        #   2) document content  → use_cache=False  (AF-5 guard)
        doc_calls = [(txt, cached) for txt, cached in calls if cached is False]
        assert len(doc_calls) >= 1, "Document embedding must use use_cache=False"
        query_calls = [(txt, cached) for txt, cached in calls if cached is True]
        assert len(query_calls) >= 1, "Query embedding should use use_cache=True"

    def test_invalid_embedding_weight_raises(self, tmp_path):
        """Constructor rejects weight outside [0.0, 1.0]."""
        from src.cache.embeddings import EmbeddingGenerator

        kb_root = _make_kb(tmp_path)
        embedder = EmbeddingGenerator()
        with pytest.raises(ValueError, match="embedding_weight"):
            KnowledgeBaseQuery(str(kb_root), embedder=embedder, embedding_weight=1.5)
        with pytest.raises(ValueError, match="embedding_weight"):
            KnowledgeBaseQuery(str(kb_root), embedder=embedder, embedding_weight=-0.1)

    def test_no_embedder_with_nonzero_weight_uses_keyword_only(self, tmp_path):
        """embedder=None + embedding_weight=0.5: falls back to keyword (no crash)."""
        _make_kb(tmp_path)
        (tmp_path / "concepts" / "x.md").write_text("# Alpha\n\nalpha keyword content\n")
        # No embedder — weight is non-zero but should be ignored
        kb = KnowledgeBaseQuery(str(tmp_path), embedding_weight=0.5)
        result = kb.query("keyword")
        assert result["total_results"] == 1
        assert result["results"][0]["score"] > 0


# --------------------------------------------------------------------------- #
# Graph scorer (P3)
# --------------------------------------------------------------------------- #


class TestGraphScorer:
    """Tests for the graph= / graph_weight= parameters (ADR-017 Decision 7)."""

    def _kb(self, tmp_path):
        kb = _make_kb(tmp_path)
        (kb / "concepts" / "hub.md").write_text(
            "# Hub Document\n\nThis is the hub concept with rich content.\n"
        )
        (kb / "guides" / "spoke.md").write_text(
            "# Spoke Guide\n\nhub guide content explanation\n"
        )
        return kb

    def test_graph_weight_zero_leaves_scores_unchanged(self, tmp_path):
        """graph_weight=0.0 must produce identical results to no-graph baseline."""
        from src.graph.graph import KnowledgeGraph

        kb = self._kb(tmp_path)
        g = KnowledgeGraph()
        g.add_node("concepts/hub.md", title="Hub")
        g.add_node("guides/spoke.md", title="Spoke")

        baseline = KnowledgeBaseQuery(str(kb)).query("hub")
        with_graph = KnowledgeBaseQuery(str(kb), graph=g, graph_weight=0.0).query("hub")

        assert [r["file"] for r in baseline["results"]] == [r["file"] for r in with_graph["results"]]
        for b, w in zip(baseline["results"], with_graph["results"]):
            assert b["score"] == pytest.approx(w["score"])

    def test_graph_none_with_nonzero_weight_uses_similarity_only(self, tmp_path):
        """graph=None disables re-ranking even when graph_weight > 0."""
        kb = self._kb(tmp_path)
        result = KnowledgeBaseQuery(str(kb), graph=None, graph_weight=0.5).query("hub")
        assert result["total_results"] >= 1
        # No graph_score field in results (graph path never activated)
        for r in result["results"]:
            assert "graph_score" not in r

    def test_graph_reranking_adds_graph_score_field(self, tmp_path):
        """When graph re-ranking is active, results gain a graph_score field."""
        from src.graph.graph import KnowledgeGraph

        kb = self._kb(tmp_path)
        g = KnowledgeGraph()
        g.add_node("concepts/hub.md", title="Hub")
        g.add_node("guides/spoke.md", title="Spoke")
        g.add_edge("guides/spoke.md", "concepts/hub.md", "explicit", 1.0)

        result = KnowledgeBaseQuery(str(kb), graph=g, graph_weight=0.3).query("hub")
        assert all("graph_score" in r for r in result["results"])

    def test_invalid_graph_weight_raises(self, tmp_path):
        kb = self._kb(tmp_path)
        with pytest.raises(ValueError, match="graph_weight"):
            KnowledgeBaseQuery(str(kb), graph_weight=1.5)



# --------------------------------------------------------------------------- #
# P4 Sub-Task 4 — recency_weight and date_filter
# --------------------------------------------------------------------------- #


class TestRecencyWeight:
    """P4: recency_weight blends file mtime into result scores."""

    def _kb(self, tmp_path):
        return _make_kb(tmp_path)

    def test_recency_weight_zero_is_unchanged(self, tmp_path):
        """recency_weight=0.0 produces identical results to the default."""
        kb = self._kb(tmp_path)
        (kb / "concepts" / "caching.md").write_text(
            "# Caching\n\nMulti-level caching strategy for token optimisation.\n"
        )
        baseline = KnowledgeBaseQuery(str(kb)).query("caching")
        with_recency = KnowledgeBaseQuery(str(kb), recency_weight=0.0).query("caching")
        for b, r in zip(baseline["results"], with_recency["results"]):
            assert b["score"] == pytest.approx(r["score"])

    def test_recency_weight_promotes_newer_doc(self, tmp_path):
        """recency_weight=1.0 ranks the newer of two otherwise-identical docs first."""
        import os
        import time

        kb = self._kb(tmp_path)
        # Write older doc first, touch it to an old timestamp
        old_doc = kb / "concepts" / "old.md"
        old_doc.write_text("# Cache\n\nA note about caching strategy.\n")
        old_time = time.time() - 3600  # 1 hour ago
        os.utime(old_doc, (old_time, old_time))

        # Write newer doc — has current mtime
        new_doc = kb / "concepts" / "new.md"
        new_doc.write_text("# Cache\n\nA note about caching strategy.\n")

        result = KnowledgeBaseQuery(str(kb), recency_weight=1.0).query("caching strategy")
        files = [r["file"] for r in result["results"]]
        # "new.md" should outrank "old.md" when recency dominates
        assert files.index("concepts/new.md") < files.index("concepts/old.md"), (
            "Newer doc must rank above older doc with recency_weight=1.0"
        )

    def test_invalid_recency_weight_raises(self, tmp_path):
        kb = self._kb(tmp_path)
        with pytest.raises(ValueError, match="recency_weight"):
            KnowledgeBaseQuery(str(kb), recency_weight=1.5)


class TestDateFilter:
    """P4: date_filter excludes results whose frontmatter date: field doesn't match."""

    def _kb(self, tmp_path):
        return _make_kb(tmp_path)

    def test_date_filter_excludes_non_matching(self, tmp_path):
        """A doc with date: 2026-06 is excluded when date_filter='2026-07'."""
        kb = self._kb(tmp_path)
        (kb / "research" / "old.md").write_text(
            "---\ndate: 2026-06-15\n---\n# Old Research\n\nSome research notes here.\n"
        )
        (kb / "research" / "new.md").write_text(
            "---\ndate: 2026-07-10\n---\n# New Research\n\nSome research notes here.\n"
        )
        result = KnowledgeBaseQuery(str(kb)).query(
            "research notes", date_filter="2026-07"
        )
        files = [r["file"] for r in result["results"]]
        assert "research/new.md" in files
        assert "research/old.md" not in files

    def test_date_filter_none_is_unchanged(self, tmp_path):
        """date_filter=None returns same results as baseline."""
        kb = self._kb(tmp_path)
        (kb / "research" / "a.md").write_text(
            "---\ndate: 2026-06-01\n---\n# Alpha\n\nAlpha content.\n"
        )
        baseline = KnowledgeBaseQuery(str(kb)).query("alpha content")
        filtered = KnowledgeBaseQuery(str(kb)).query("alpha content", date_filter=None)
        assert [r["file"] for r in baseline["results"]] == [r["file"] for r in filtered["results"]]

    def test_date_filter_includes_undated_docs(self, tmp_path):
        """Docs without a date: field are always included (fail-open)."""
        kb = self._kb(tmp_path)
        (kb / "concepts" / "no-date.md").write_text(
            "# No Date\n\nThis document has no frontmatter date field.\n"
        )
        result = KnowledgeBaseQuery(str(kb)).query("no date", date_filter="2026-07")
        files = [r["file"] for r in result["results"]]
        assert "concepts/no-date.md" in files
