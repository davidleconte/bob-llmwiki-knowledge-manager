"""Regression tests for the tool-layer path-containment fix.

Covers ``src.tools.safe_paths.resolve_within`` directly, plus the three tool
entry points it hardens (``ComponentAnalyzer``, ``KnowledgeBaseQuery``,
``BatchFileReader``). A ``../`` sequence or an absolute path must be refused
before any file is read — the mitigation for the STRIDE Information-Disclosure
finding (``docs/security/THREAT_MODEL.md``). ``src/tools`` is excluded from the
coverage gate, but these behavioural assertions still run under pytest.
"""

from __future__ import annotations

import pytest

from src.tools.batch_file_reader import BatchFileReader
from src.tools.component_analyzer import ComponentAnalyzer
from src.tools.kb_query import KnowledgeBaseQuery
from src.tools.safe_paths import resolve_within


class TestResolveWithin:
    def test_allows_legitimate_relative_path(self, tmp_path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "file.txt").write_text("ok")
        resolved = resolve_within(tmp_path, "sub/file.txt")
        assert resolved == (tmp_path / "sub" / "file.txt").resolve()

    def test_allows_base_itself(self, tmp_path):
        assert resolve_within(tmp_path, "") == tmp_path.resolve()

    def test_rejects_parent_traversal(self, tmp_path):
        with pytest.raises(ValueError):
            resolve_within(tmp_path, "../secret.txt")

    def test_rejects_deep_traversal(self, tmp_path):
        with pytest.raises(ValueError):
            resolve_within(tmp_path, "a/b/../../../etc/passwd")

    def test_rejects_absolute_path(self, tmp_path):
        with pytest.raises(ValueError):
            resolve_within(tmp_path, "/etc/passwd")

    def test_rejects_symlink_escape(self, tmp_path):
        outside = tmp_path.parent / "outside_target"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret")
        base = tmp_path / "base"
        base.mkdir()
        (base / "link").symlink_to(outside)
        with pytest.raises(ValueError):
            resolve_within(base, "link/secret.txt")


class TestComponentAnalyzerContainment:
    def test_traversal_is_refused(self, tmp_path):
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("../../../etc/passwd")
        assert "Invalid component path" in result.get("error", "")

    def test_legitimate_file_still_analyzed(self, tmp_path):
        (tmp_path / "mod.py").write_text("def f():\n    return 1\n")
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("mod.py")
        assert result.get("error", "").find("Invalid component path") == -1
        assert result["type"] == "file"


class TestKnowledgeBaseQueryContainment:
    def _make_kb(self, tmp_path):
        for cat in ("concepts", "guides", "references", "research"):
            (tmp_path / cat).mkdir()
        (tmp_path / "concepts" / "doc.md").write_text("# Doc\n[x](other.md)\n")
        return KnowledgeBaseQuery(str(tmp_path))

    def test_traversal_is_refused(self, tmp_path):
        kb = self._make_kb(tmp_path)
        result = kb.get_cross_references("../../etc/passwd")
        assert "Invalid file path" in result.get("error", "")

    def test_legitimate_file_still_read(self, tmp_path):
        kb = self._make_kb(tmp_path)
        result = kb.get_cross_references("concepts/doc.md")
        assert "Invalid file path" not in result.get("error", "")
        assert result["file"] == "concepts/doc.md"


class TestBatchFileReaderContainment:
    def test_traversal_is_refused(self, tmp_path):
        results = BatchFileReader(str(tmp_path)).read_files(["../../../etc/passwd"])
        assert "Invalid file path" in results["../../../etc/passwd"]["error"]

    def test_legitimate_file_still_read(self, tmp_path):
        (tmp_path / "data.txt").write_text("hello\n")
        results = BatchFileReader(str(tmp_path)).read_files(["data.txt"])
        assert "error" not in results["data.txt"]
        assert results["data.txt"]["content"] == "hello\n"
