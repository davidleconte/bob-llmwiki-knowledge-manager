"""Behavioural tests for ``src.tools.component_analyzer.ComponentAnalyzer``.

Drives each ``analysis_type`` (security/performance/quality/architecture/
comprehensive) at both ``shallow`` and ``deep`` depth, over both single files
and directories, plus the containment/missing/binary error branches and the
CLI ``main`` entry point. Inputs are crafted so the security, performance, and
quality detectors actually fire (hardcoded password, ``eval``, nested-loop
comment, an over-long function). The analyzer is constructed with
``base_path=str(tmp_path)`` and given paths relative to it.
"""

from __future__ import annotations

import sys

from src.tools.component_analyzer import ComponentAnalyzer

# Hits the security detectors (password/eval/os.system) and the performance
# detectors (nested-loop comment, time.sleep, SELECT *).
SECURITY_PERF_SOURCE = (
    "import os\n"
    "import time\n"
    "\n"
    'password = "supersecret123"\n'
    "\n"
    "def run(cmd):\n"
    "    eval(cmd)\n"
    '    os.system("ls")\n'
    "    time.sleep(1)\n"
    "    # for i in a: for j in b: work()\n"
    '    query = "SELECT * FROM users"\n'
    "    return query\n"
)


def _long_function_source() -> str:
    """A single top-level function whose body exceeds the 50-line threshold."""
    body = "\n".join(f"    x{i} = {i}" for i in range(60))
    return f"import sys\n\ndef big():\n{body}\n"


# --------------------------------------------------------------------------- #
# error branches
# --------------------------------------------------------------------------- #


class TestErrorBranches:
    def test_missing_component(self, tmp_path):
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("ghost.py")
        assert "Component not found" in result["error"]

    def test_escaping_path_refused(self, tmp_path):
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("../outside.py")
        assert "Invalid component path" in result["error"]

    def test_absolute_path_outside_base(self, tmp_path):
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("/etc/passwd")
        assert "Invalid component path" in result["error"]

    def test_binary_file(self, tmp_path):
        (tmp_path / "blob.py").write_bytes(b"\xff\xfe\x00\x01")
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("blob.py")
        assert "Binary file" in result["error"]


# --------------------------------------------------------------------------- #
# single-file analysis
# --------------------------------------------------------------------------- #


class TestFileAnalysis:
    def test_file_metadata_and_language(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component("mod.py")
        assert result["type"] == "file"
        assert result["language"] == "python"
        assert result["size_bytes"] > 0
        assert result["line_count"] > 1

    def test_unknown_language(self, tmp_path):
        (tmp_path / "notes.txt").write_text("plain text\n")
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "notes.txt", analysis_type="architecture"
        )
        assert result["language"] == "unknown"

    def test_security_only(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "mod.py", analysis_type="security"
        )
        sec = result["security"]
        assert sec["total_issues"] >= 3
        assert sec["critical"] >= 1  # hardcoded password
        assert sec["high"] >= 1  # eval()
        assert "performance" not in result
        assert "quality" not in result

    def test_performance_only(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "mod.py", analysis_type="performance"
        )
        perf = result["performance"]
        assert perf["total_issues"] >= 3
        assert "security" not in result

    def test_quality_only_flags_long_function(self, tmp_path):
        (tmp_path / "big.py").write_text(_long_function_source())
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "big.py", analysis_type="quality"
        )
        qual = result["quality"]
        assert qual["function_count"] == 1
        assert qual["long_functions"] == 1
        assert qual["avg_line_length"] >= 0

    def test_architecture_only_extracts_imports(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "mod.py", analysis_type="architecture"
        )
        arch = result["architecture"]
        assert arch["import_count"] == 2
        assert "import os" in arch["imports"]

    def test_comprehensive_has_all_sections(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "mod.py", analysis_type="comprehensive"
        )
        for key in ("security", "performance", "quality", "architecture"):
            assert key in result

    def test_deep_depth_returns_full_issue_lists(self, tmp_path):
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        shallow = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "mod.py", analysis_type="comprehensive", depth="deep"
        )
        assert shallow["depth"] == "deep"
        assert "issues" in shallow["security"]


# --------------------------------------------------------------------------- #
# directory analysis
# --------------------------------------------------------------------------- #


def _make_pkg(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "a.py").write_text(SECURITY_PERF_SOURCE)
    (pkg / "b.js").write_text("import x from 'x';\nfunction f() {}\n")
    (pkg / "c.ts").write_text("export const y = 1;\n")
    (pkg / "d.go").write_text("package main\nfunc Main() {}\n")
    return pkg


class TestDirectoryAnalysis:
    def test_comprehensive_shallow(self, tmp_path):
        _make_pkg(tmp_path)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "pkg", analysis_type="comprehensive"
        )
        assert result["type"] == "directory"
        assert result["file_count"] == 4
        assert result["security"]["total_issues"] >= 1
        assert result["performance"]["total_issues"] >= 1
        assert result["quality"]["total_functions"] >= 1
        assert result["architecture"]["total_files"] == 4
        # Shallow: dependencies map is intentionally empty.
        assert result["architecture"]["dependencies"] == {}

    def test_deep_populates_dependencies(self, tmp_path):
        _make_pkg(tmp_path)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "pkg", analysis_type="architecture", depth="deep"
        )
        assert result["architecture"]["dependencies"] != {}

    def test_security_directory_only(self, tmp_path):
        _make_pkg(tmp_path)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "pkg", analysis_type="security", depth="deep"
        )
        assert "security" in result
        assert "quality" not in result

    def test_quality_directory_deep(self, tmp_path):
        _make_pkg(tmp_path)
        (tmp_path / "pkg" / "long.py").write_text(_long_function_source())
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "pkg", analysis_type="quality", depth="deep"
        )
        assert result["quality"]["long_functions"] >= 1

    def test_performance_directory_only(self, tmp_path):
        _make_pkg(tmp_path)
        result = ComponentAnalyzer(str(tmp_path)).analyze_component(
            "pkg", analysis_type="performance"
        )
        assert "performance" in result
        assert "security" not in result


# --------------------------------------------------------------------------- #
# CLI main()
# --------------------------------------------------------------------------- #


class TestMainCLI:
    def test_file_comprehensive_text(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        monkeypatch.setattr(sys, "argv", ["ca", "mod.py"])
        from src.tools.component_analyzer import main

        main()
        out = capsys.readouterr().out
        assert "Component Analysis: mod.py" in out
        assert "Security Analysis" in out

    def test_json_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mod.py").write_text(SECURITY_PERF_SOURCE)
        monkeypatch.setattr(sys, "argv", ["ca", "mod.py", "--type", "security", "--output", "json"])
        from src.tools.component_analyzer import main

        main()
        out = capsys.readouterr().out
        assert '"security"' in out

    def test_directory_text(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        _make_pkg(tmp_path)
        monkeypatch.setattr(sys, "argv", ["ca", "pkg"])
        from src.tools.component_analyzer import main

        main()
        out = capsys.readouterr().out
        assert "Total Files:" in out

    def test_error_display(self, tmp_path, monkeypatch, capsys):
        # A binary file yields a merged error dict that still carries the
        # component/type keys, so main's header prints and the error branch
        # is reached cleanly.
        monkeypatch.chdir(tmp_path)
        (tmp_path / "blob.py").write_bytes(b"\xff\xfe\x00")
        monkeypatch.setattr(sys, "argv", ["ca", "blob.py"])
        from src.tools.component_analyzer import main

        main()
        out = capsys.readouterr().out
        assert "Error:" in out
