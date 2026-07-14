"""Tests for the unified CLI (src/cli.py).

Each test drives ``main([...])`` (or a subprocess for the ``python -m src`` entry
point) and asserts on the dispatched result. Logs go to stderr, so stdout is pure
program output and ``--json`` output parses directly.
"""

import io
import json
import subprocess
import sys

import pytest

from src.cli import build_parser, main
from src.config import ConfigManager


@pytest.fixture(autouse=True)
def _reset_config():
    """Isolate the ConfigManager singletons between CLI invocations."""
    import src.config.manager as manager_mod

    ConfigManager._instance = None
    manager_mod._global_config = None
    yield
    ConfigManager._instance = None
    manager_mod._global_config = None


def _run_json(capsys, argv):
    """Run the CLI and parse its stdout as JSON."""
    assert main(argv) == 0
    return json.loads(capsys.readouterr().out)


class TestCli:
    def test_count_json(self, capsys):
        out = _run_json(capsys, ["--json", "count", "hello world this is a test"])
        assert out["tokens"] > 0

    def test_count_human_readable(self, capsys):
        assert main(["count", "hello world"]) == 0
        assert "tokens:" in capsys.readouterr().out

    def test_optimize_json_has_optimized_text(self, capsys):
        out = _run_json(capsys, ["--json", "optimize", "Hello    world   with   extra   spaces"])
        assert "optimized_text" in out
        assert out["optimized_tokens"] <= out["original_tokens"]

    def test_optimize_respects_max_tokens(self, capsys):
        long_text = " ".join(["word"] * 200)
        out = _run_json(capsys, ["--json", "optimize", long_text, "--max-tokens", "10"])
        assert out["optimized_tokens"] <= 10

    def test_truncate_respects_budget(self, capsys):
        text = " ".join(f"sentence number {i}." for i in range(200))
        out = _run_json(capsys, ["--json", "truncate", text, "--max-tokens", "20"])
        assert out["truncated_tokens"] <= 20

    def test_truncate_requires_max_tokens(self):
        with pytest.raises(SystemExit):
            main(["truncate", "some text"])  # --max-tokens is required

    def test_cache_stats_json(self, capsys):
        assert isinstance(_run_json(capsys, ["--json", "cache-stats"]), dict)

    def test_metrics_json(self, capsys):
        assert isinstance(_run_json(capsys, ["--json", "metrics"]), dict)

    def test_health_json(self, capsys):
        out = _run_json(capsys, ["--json", "health"])
        assert "status" in out

    def test_cost_report_json(self, capsys):
        assert isinstance(_run_json(capsys, ["--json", "cost-report"]), dict)

    def test_config_json(self, capsys):
        out = _run_json(capsys, ["--json", "config"])
        for section in ("cache", "optimizer", "monitoring"):
            assert section in out

    def test_stdin_input(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("piped in text"))
        out = _run_json(capsys, ["--json", "count", "-"])
        assert out["tokens"] > 0

    def test_no_command_errors(self):
        with pytest.raises(SystemExit):
            main([])  # subcommand is required

    def test_parser_exposes_all_subcommands(self):
        parser = build_parser()
        actions = [a for a in parser._actions if a.dest == "command"]
        assert actions, "no subparser action found"
        choices = set(actions[0].choices)
        assert {
            "optimize",
            "truncate",
            "count",
            "cache-stats",
            "cost-report",
            "metrics",
            "health",
            "config",
        } <= choices


class TestModuleEntryPoint:
    def test_python_m_src(self):
        """`python -m src` runs the CLI end to end in a fresh process."""
        proc = subprocess.run(
            [sys.executable, "-m", "src", "--json", "count", "hello there"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
        assert json.loads(proc.stdout)["tokens"] > 0
