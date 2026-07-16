"""Behavioural tests for ``src.tools.batch_file_reader.BatchFileReader``.

Covers the three read strategies (``full`` with truncation and the binary
fallback, ``summary`` across the python/js/go/generic parsers, and ``search``),
the missing-file and path-escape error branches, and the CLI ``main`` entry
point. The reader is always constructed with ``base_path=str(tmp_path)`` and fed
paths relative to it, matching the containment contract in
``src.tools.safe_paths.resolve_within``.
"""

from __future__ import annotations

import sys

from src.tools.batch_file_reader import BatchFileReader

PY_SOURCE = (
    "import os\n"
    "from pathlib import Path\n"
    "\n"
    "class Widget:\n"
    "    pass\n"
    "\n"
    "def build():\n"
    "    return Widget()\n"
)

TS_SOURCE = (
    "import { a } from './a';\n"
    "export const x = 1;\n"
    "function doThing() { return 1; }\n"
    "const arrow = () => 2;\n"
    "class Thing {\n"
    "}\n"
)

GO_SOURCE = (
    "package main\n"
    "\n"
    "import (\n"
    '    "fmt"\n'
    '    "os"\n'
    ")\n"
    "\n"
    "type Server struct {\n"
    "}\n"
    "\n"
    "func Run() {\n"
    '    fmt.Println("hi")\n'
    "}\n"
)


# --------------------------------------------------------------------------- #
# strategy: full
# --------------------------------------------------------------------------- #


class TestReadFull:
    def test_reads_full_content(self, tmp_path):
        (tmp_path / "data.txt").write_text("line1\nline2\nline3\n")
        results = BatchFileReader(str(tmp_path)).read_files(["data.txt"], strategy="full")
        res = results["data.txt"]
        assert res["strategy"] == "full"
        assert res["content"] == "line1\nline2\nline3\n"
        assert res["total_lines"] == 3  # readlines() -> 3 elements for 3 newlines
        assert res["truncated"] is False

    def test_truncates_at_max_lines(self, tmp_path):
        (tmp_path / "big.txt").write_text("".join(f"line{i}\n" for i in range(50)))
        results = BatchFileReader(str(tmp_path)).read_files(
            ["big.txt"], strategy="full", max_lines_per_file=10
        )
        res = results["big.txt"]
        assert res["truncated"] is True
        assert res["lines_read"] == 10
        assert res["content"].count("\n") == 10

    def test_binary_file_reports_error(self, tmp_path):
        (tmp_path / "blob.py").write_bytes(b"\xff\xfe\x00\x01binary")
        results = BatchFileReader(str(tmp_path)).read_files(["blob.py"], strategy="full")
        res = results["blob.py"]
        assert res["is_binary"] is True
        assert "Binary file" in res["error"]


# --------------------------------------------------------------------------- #
# strategy: summary
# --------------------------------------------------------------------------- #


class TestReadSummary:
    def test_python_summary(self, tmp_path):
        (tmp_path / "mod.py").write_text(PY_SOURCE)
        res = BatchFileReader(str(tmp_path)).read_files(["mod.py"], strategy="summary")["mod.py"]
        assert res["language"] == "python"
        assert res["file_type"] == ".py"
        assert res["class_count"] == 1
        assert "Widget" in res["classes"]
        assert res["function_count"] == 1
        assert res["import_count"] == 2

    def test_javascript_summary(self, tmp_path):
        (tmp_path / "app.ts").write_text(TS_SOURCE)
        res = BatchFileReader(str(tmp_path)).read_files(["app.ts"], strategy="summary")["app.ts"]
        assert res["language"] == "javascript/typescript"
        assert res["import_count"] == 1
        assert res["export_count"] == 1
        assert res["function_count"] >= 1
        assert "Thing" in res["classes"]

    def test_go_summary(self, tmp_path):
        (tmp_path / "srv.go").write_text(GO_SOURCE)
        res = BatchFileReader(str(tmp_path)).read_files(["srv.go"], strategy="summary")["srv.go"]
        assert res["language"] == "go"
        assert "Server" in res["types"]
        assert "Run" in res["functions"]
        assert res["import_count"] == 2  # "fmt" and "os" inside the import block

    def test_generic_summary(self, tmp_path):
        (tmp_path / "notes.txt").write_text("just some text\nmore text\n")
        res = BatchFileReader(str(tmp_path)).read_files(["notes.txt"], strategy="summary")[
            "notes.txt"
        ]
        assert res["note"] == "Generic summary only"
        assert res["file_type"] == ".txt"

    def test_binary_summary_reports_error(self, tmp_path):
        (tmp_path / "blob.py").write_bytes(b"\xff\xfe\x00")
        res = BatchFileReader(str(tmp_path)).read_files(["blob.py"], strategy="summary")["blob.py"]
        assert res["strategy"] == "summary"
        assert "error" in res


# --------------------------------------------------------------------------- #
# strategy: search
# --------------------------------------------------------------------------- #


class TestReadSearch:
    def test_search_finds_matches_with_context(self, tmp_path):
        # "def" appears on line 1 (context_before -> []) and on a later line
        # (context_before -> populated), covering both branches.
        (tmp_path / "mod.py").write_text("def first():\n    pass\n\n\ndef second():\n    pass\n")
        res = BatchFileReader(str(tmp_path)).read_files(
            ["mod.py"], strategy="search", search_pattern="def"
        )["mod.py"]
        assert res["strategy"] == "search"
        assert res["pattern"] == "def"
        assert res["match_count"] == 2
        first_match = res["matches"][0]
        assert first_match["line_number"] == 1
        assert first_match["context_before"] == []
        assert res["matches"][1]["context_before"] != []

    def test_search_without_pattern_errors(self, tmp_path):
        (tmp_path / "mod.py").write_text("anything\n")
        res = BatchFileReader(str(tmp_path)).read_files(["mod.py"], strategy="search")["mod.py"]
        assert res["error"] == "No search pattern provided"


# --------------------------------------------------------------------------- #
# error branches
# --------------------------------------------------------------------------- #


class TestErrorBranches:
    def test_missing_file(self, tmp_path):
        res = BatchFileReader(str(tmp_path)).read_files(["ghost.txt"])["ghost.txt"]
        assert res["error"] == "File not found"

    def test_escaping_relative_path(self, tmp_path):
        res = BatchFileReader(str(tmp_path)).read_files(["../outside.txt"])["../outside.txt"]
        assert "Invalid file path" in res["error"]

    def test_absolute_path_outside_base(self, tmp_path):
        res = BatchFileReader(str(tmp_path)).read_files(["/etc/passwd"])["/etc/passwd"]
        assert "Invalid file path" in res["error"]

    def test_unknown_strategy(self, tmp_path):
        (tmp_path / "data.txt").write_text("x\n")
        res = BatchFileReader(str(tmp_path)).read_files(["data.txt"], strategy="bogus")["data.txt"]
        assert "Unknown strategy" in res["error"]

    def test_multiple_files_mixed_results(self, tmp_path):
        (tmp_path / "ok.txt").write_text("ok\n")
        results = BatchFileReader(str(tmp_path)).read_files(["ok.txt", "missing.txt"])
        assert "error" not in results["ok.txt"]
        assert results["missing.txt"]["error"] == "File not found"

    def test_file_deleted_after_resolution_returns_error_not_exception(self, tmp_path):
        """TOCTOU regression: file exists at call time but is deleted before open().

        Previously the code called full_path.exists() → open(); now it calls
        open() directly inside try/except FileNotFoundError.  If the file
        vanishes between resolve_within() and open() the call must return an
        error dict, not raise an unhandled exception.
        """
        # Create the file so resolve_within succeeds (it checks containment,
        # not existence on older versions).
        p = tmp_path / "vanishing.txt"
        p.write_text("hello\n")
        reader = BatchFileReader(str(tmp_path))

        # Simulate deletion between resolve and open by removing before the call.
        # Because resolve_within resolves to an absolute path and doesn't re-check
        # existence, deleting now exercises the FileNotFoundError branch in open().
        p.unlink()

        result = reader.read_files(["vanishing.txt"])["vanishing.txt"]
        assert "error" in result
        assert result["error"] == "File not found"


# --------------------------------------------------------------------------- #
# CLI main()
# --------------------------------------------------------------------------- #


class TestMainCLI:
    def test_full_text_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "data.txt").write_text("hello\nworld\n")
        monkeypatch.setattr(sys, "argv", ["batch", "data.txt"])
        from src.tools.batch_file_reader import main

        main()
        out = capsys.readouterr().out
        assert "File: data.txt" in out
        assert "Content:" in out

    def test_summary_text_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mod.py").write_text(PY_SOURCE)
        monkeypatch.setattr(sys, "argv", ["batch", "mod.py", "--strategy", "summary"])
        from src.tools.batch_file_reader import main

        main()
        out = capsys.readouterr().out
        assert "Language: python" in out

    def test_search_json_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mod.py").write_text(PY_SOURCE)
        monkeypatch.setattr(
            sys,
            "argv",
            ["batch", "mod.py", "--strategy", "search", "--search", "def", "--output", "json"],
        )
        from src.tools.batch_file_reader import main

        main()
        out = capsys.readouterr().out
        assert '"match_count"' in out

    def test_error_display(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["batch", "missing.txt"])
        from src.tools.batch_file_reader import main

        main()
        out = capsys.readouterr().out
        assert "Error: File not found" in out
