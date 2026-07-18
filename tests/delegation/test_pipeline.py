"""Tests for src/delegation/pipeline.py — analysis pipeline connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.delegation.base import SubAgentResult, SubAgentStatus
from src.delegation.pipeline import AnalysisPipelineResult, analyze_and_ingest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TASK_TYPES = ("research", "security", "quality", "performance", "architecture", "documentation")


def _make_success_results() -> Dict[str, SubAgentResult]:
    """Return a fake coordinator result dict — all six tasks succeed."""
    return {
        f"{t}-task": SubAgentResult(
            agent_id=f"{t}-1",
            agent_type=t,
            status=SubAgentStatus.SUCCESS,
            data={"target": "src/cache", "score": 80.0, "issues": [], "notes": f"{t} ok"},
            execution_time_ms=50.0,
            token_count=100,
        )
        for t in _TASK_TYPES
    }


def _make_coordinator_stats(n: int = 6) -> Dict[str, Any]:
    return {
        "total_tasks": n,
        "completed_tasks": n,
        "failed_tasks": 0,
        "success_rate": 1.0,
        "total_execution_time_ms": 300.0,
        "parallel_execution_time_ms": 250.0,
        "parallelization_factor": 4.0,
        "total_tokens": 600,
        "registered_agents": n,
        "start_time": "2026-07-17T00:00:00+00:00",
        "end_time": "2026-07-17T00:00:01+00:00",
    }


def _fake_optimize(text: str, **_kwargs) -> Dict[str, Any]:
    """Minimal fake TokenOptimizer.optimize — returns ~20% compression."""
    original_tokens = len(text) // 4
    optimized_tokens = int(original_tokens * 0.8)
    return {
        "optimized_text": text[: int(len(text) * 0.8)],
        "compression_ratio": 0.8,
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "savings_percentage": 20.0,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAnalyzeAndIngest:
    """Core pipeline behaviour."""

    def test_returns_pipeline_result_dataclass(self, tmp_path: Path) -> None:
        """analyze_and_ingest returns an AnalysisPipelineResult with correct shape."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()
            MockOpt.return_value.optimize.side_effect = _fake_optimize

            result = analyze_and_ingest(
                target_dir="src/cache",
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

        assert isinstance(result, AnalysisPipelineResult)
        assert result.target_dir == "src/cache"
        assert result.agents_run == 6
        assert result.agents_succeeded == 6
        assert result.agents_failed == 0

    def test_research_task_has_no_dependencies(self, tmp_path: Path) -> None:
        """ResearchAgent task must have empty dependencies so it runs first."""
        captured_tasks = []

        def _capture_add_tasks(tasks):
            captured_tasks.extend(tasks)

        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.add_tasks.side_effect = _capture_add_tasks
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()
            MockOpt.return_value.optimize.side_effect = _fake_optimize

            analyze_and_ingest(
                target_dir="src",
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

        research_task = next(t for t in captured_tasks if t.task_type == "research")
        assert research_task.dependencies == [], "ResearchAgent must have no dependencies"

        for t in captured_tasks:
            if t.task_type != "research":
                assert "research-task" in t.dependencies, (
                    f"{t.task_type} task must depend on research-task"
                )

    def test_output_files_written_under_output_dir(self, tmp_path: Path) -> None:
        """A .md file is written per successful agent."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()
            MockOpt.return_value.optimize.side_effect = _fake_optimize

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
            )

        assert len(result.output_files) == 6
        for fp in result.output_files:
            assert Path(fp).exists(), f"Expected output file: {fp}"
            assert Path(fp).suffix == ".md"
            content = Path(fp).read_text()
            assert "delegation-pipeline" in content  # frontmatter marker

    def test_compression_applied_when_compress_true(self, tmp_path: Path) -> None:
        """TokenOptimizer.optimize is called once per successful agent when compress=True."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()
            opt_inst = MockOpt.return_value
            opt_inst.optimize.side_effect = _fake_optimize

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
                compress=True,
            )

        assert opt_inst.optimize.call_count == 6
        assert len(result.compression_ratios) == 6
        for ratio in result.compression_ratios.values():
            assert ratio == pytest.approx(0.8)

    def test_compression_skipped_when_compress_false(self, tmp_path: Path) -> None:
        """TokenOptimizer is NOT instantiated when compress=False."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
                compress=False,
            )

        MockOpt.assert_not_called()
        # Compression ratios default to 1.0 (no compression).
        for ratio in result.compression_ratios.values():
            assert ratio == 1.0

    def test_failed_agents_not_written(self, tmp_path: Path) -> None:
        """Only successful agent results produce output files."""
        fake_results = _make_success_results()
        # Mark security-task as failed.
        fake_results["security-task"] = SubAgentResult(
            agent_id="security-1",
            agent_type="security",
            status=SubAgentStatus.FAILED,
            data={},
            errors=["analysis error"],
        )
        stats = _make_coordinator_stats()
        stats["completed_tasks"] = 5
        stats["failed_tasks"] = 1

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = stats
            MockOpt.return_value.optimize.side_effect = _fake_optimize

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
            )

        assert len(result.output_files) == 5
        assert "security-task" not in result.compression_ratios

    def test_path_traversal_rejected(self, tmp_path: Path) -> None:
        """target_dir that escapes cwd raises ValueError before any agent runs."""
        with pytest.raises(ValueError, match="escapes working directory"):
            analyze_and_ingest(
                target_dir="../../../etc/passwd",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
            )

    def test_coordinator_stats_included_in_result(self, tmp_path: Path) -> None:
        """coordinator_stats in the result contains total_tasks."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer"),
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
                compress=False,
            )

        assert "total_tasks" in result.coordinator_stats
        assert result.coordinator_stats["total_tasks"] == 6

    def test_result_is_serialisable(self, tmp_path: Path) -> None:
        """AnalysisPipelineResult must convert to dict cleanly (for CLI _emit)."""
        fake_results = _make_success_results()

        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer") as MockOpt,
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = fake_results
            inst.get_statistics.return_value = _make_coordinator_stats()
            MockOpt.return_value.optimize.side_effect = _fake_optimize

            result = analyze_and_ingest(
                target_dir="src/cache",
                output_dir=str(tmp_path / "out"),
                kb_path=str(tmp_path / "kb"),
            )

        d = result.__dict__
        import json

        json.dumps(d, default=str)  # must not raise
