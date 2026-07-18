"""Smoke + containment tests for the five delegation agents that are not yet
covered by existing test files (security, quality, performance, architecture,
research).

Each agent is tested with:
1. A path-traversal target that must be rejected (FAILED + "escapes" in errors).
2. A legitimate in-tree target that must succeed (SUCCESS + non-empty data).

This is intentionally minimal — the goal is to push delegation package coverage
above the 70% floor without duplicating the deeper coordinator / base tests.
"""

from __future__ import annotations

from pathlib import Path

from src.delegation.base import SubAgentStatus, SubAgentTask

REPO_ROOT = Path(__file__).resolve().parents[2]


def _task(target: str, agent_type: str = "generic", **params) -> SubAgentTask:
    return SubAgentTask(
        task_id=f"{agent_type}-test",
        task_type=agent_type,
        target=target,
        parameters=params,
    )


# ---------------------------------------------------------------------------
# SecurityAgent
# ---------------------------------------------------------------------------


class TestSecurityAgent:
    def test_rejects_traversal(self, monkeypatch) -> None:
        from src.delegation.agents.security_agent import SecurityAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = SecurityAgent(agent_id="sec-test")
        result = agent.analyze(_task("../../../../etc", agent_type="security"))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    def test_accepts_in_tree_target(self, monkeypatch) -> None:
        from src.delegation.agents.security_agent import SecurityAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = SecurityAgent(agent_id="sec-test")
        result = agent.analyze(_task("src/delegation/agents", agent_type="security"))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data


# ---------------------------------------------------------------------------
# QualityAgent
# ---------------------------------------------------------------------------


class TestQualityAgent:
    def test_rejects_traversal(self, monkeypatch) -> None:
        from src.delegation.agents.quality_agent import QualityAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = QualityAgent(agent_id="qual-test")
        result = agent.analyze(_task("../../../../etc", agent_type="quality"))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    def test_accepts_in_tree_target(self, monkeypatch) -> None:
        from src.delegation.agents.quality_agent import QualityAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = QualityAgent(agent_id="qual-test")
        result = agent.analyze(_task("src/delegation/agents", agent_type="quality"))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data


# ---------------------------------------------------------------------------
# PerformanceAgent
# ---------------------------------------------------------------------------


class TestPerformanceAgent:
    def test_rejects_traversal(self, monkeypatch) -> None:
        from src.delegation.agents.performance_agent import PerformanceAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = PerformanceAgent(agent_id="perf-test")
        result = agent.analyze(_task("../../../../etc", agent_type="performance"))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    def test_accepts_in_tree_target(self, monkeypatch) -> None:
        from src.delegation.agents.performance_agent import PerformanceAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = PerformanceAgent(agent_id="perf-test")
        result = agent.analyze(_task("src/delegation/agents", agent_type="performance"))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data


# ---------------------------------------------------------------------------
# ArchitectureAgent
# ---------------------------------------------------------------------------


class TestArchitectureAgent:
    def test_rejects_traversal(self, monkeypatch) -> None:
        from src.delegation.agents.architecture_agent import ArchitectureAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = ArchitectureAgent(agent_id="arch-test")
        result = agent.analyze(_task("../../../../etc", agent_type="architecture"))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    def test_accepts_in_tree_target(self, monkeypatch) -> None:
        from src.delegation.agents.architecture_agent import ArchitectureAgent

        monkeypatch.chdir(REPO_ROOT)
        agent = ArchitectureAgent(agent_id="arch-test")
        result = agent.analyze(_task("src/delegation/agents", agent_type="architecture"))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data


# ---------------------------------------------------------------------------
# ResearchAgent
# ---------------------------------------------------------------------------


class TestResearchAgent:
    def test_gracefully_handles_missing_kb(self, tmp_path: Path) -> None:
        """A non-existent kb_path produces FAILED with a clear error message."""
        from src.delegation.agents.research_agent import ResearchAgent

        agent = ResearchAgent(agent_id="res-test", kb_path=str(tmp_path / "no-kb"))
        result = agent.analyze(
            _task("src/delegation", agent_type="research", query="test query", max_results=3)
        )
        assert result.status == SubAgentStatus.FAILED
        assert result.errors

    def test_accepts_valid_kb(self, tmp_path: Path) -> None:
        """A valid (possibly empty) kb_path returns SUCCESS."""
        from src.delegation.agents.research_agent import ResearchAgent

        # Create a minimal KB tree so KnowledgeBaseQuery does not raise ValueError.
        kb = tmp_path / "kb"
        for sub in ("concepts", "guides", "references", "research"):
            (kb / sub).mkdir(parents=True)

        agent = ResearchAgent(agent_id="res-test", kb_path=str(kb))
        result = agent.analyze(
            _task("src/delegation", agent_type="research", query="test query", max_results=3)
        )
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data
