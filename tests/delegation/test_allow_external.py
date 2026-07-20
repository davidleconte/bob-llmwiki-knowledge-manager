"""Security + capability tests for ``--allow-external`` on the analyze pipeline (D3 part 1).

``--allow-external <dir>`` lets ``bob-optimize analyze`` run against a directory
*outside* the current working directory (e.g. a checked-out foreign repo) while
preserving the ATK-FS path-containment guarantee: the same ``resolve_within`` guard
applies, only rebased onto ``<dir>``. A target that escapes ``<dir>`` via a ``../``
sequence, an absolute path, or a symlink pointing outside is still refused.

These tests lock in BOTH the new capability (an external base is honored) and the
retained guard (escapes are refused), across all three containment layers:

1. the pipeline gate in :func:`analyze_and_ingest`;
2. the four ``ComponentAnalyzer``-backed agents (security/quality/performance/architecture);
3. :class:`DocumentationAgent` (its own ``resolve_within`` + ``BatchFileReader``).

Regression intent: if any layer is rebased onto the external root WITHOUT keeping the
guard (or is left pinned to cwd so the external base is ignored), one of these fails.
See ``docs/security/THREAT_MODEL.md`` (ATK-FS-01).
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.delegation.agents.architecture_agent import ArchitectureAgent
from src.delegation.agents.documentation_agent import DocumentationAgent
from src.delegation.agents.performance_agent import PerformanceAgent
from src.delegation.agents.quality_agent import QualityAgent
from src.delegation.agents.security_agent import SecurityAgent
from src.delegation.base import SubAgentStatus, SubAgentTask
from src.delegation.pipeline import AnalysisPipelineResult, analyze_and_ingest

# The four agents whose containment is enforced via ComponentAnalyzer(base_path=...).
COMPONENT_AGENT_CLASSES = [SecurityAgent, QualityAgent, PerformanceAgent, ArchitectureAgent]


def _task(target: str, agent_type: str = "generic", **params) -> SubAgentTask:
    return SubAgentTask(
        task_id=f"{agent_type}-test",
        task_type=agent_type,
        target=target,
        parameters=params,
    )


def _outside_target() -> str:
    """A directory guaranteed to exist outside any tmp base (for abs/symlink escapes)."""
    return "/etc" if Path("/etc").is_dir() else str(Path.home())


@pytest.fixture
def ext_base(tmp_path):
    """An external base dir (outside cwd) holding one analyzable package."""
    base = tmp_path / "external-repo"
    (base / "proj").mkdir(parents=True)
    (base / "proj" / "mod.py").write_text(
        'def add(a, b):\n    """Add two numbers."""\n    return a + b\n'
    )
    return base


def _fake_stats() -> dict:
    return {
        "total_tasks": 0,
        "completed_tasks": 0,
        "failed_tasks": 0,
        "success_rate": 0.0,
        "total_execution_time_ms": 0.0,
        "parallel_execution_time_ms": 0.0,
        "parallelization_factor": 0.0,
        "total_tokens": 0,
        "registered_agents": 6,
        "start_time": "2026-07-20T00:00:00+00:00",
        "end_time": "2026-07-20T00:00:01+00:00",
    }


# --------------------------------------------------------------------------- #
# Layer 1 — pipeline gate (analyze_and_ingest)
# --------------------------------------------------------------------------- #


class TestPipelineGate:
    def test_external_base_is_honored(self, ext_base, tmp_path, monkeypatch):
        """With allow_external set, a target inside that base runs (coordinator mocked)."""
        monkeypatch.chdir(tmp_path)  # cwd is NOT the external base
        with (
            patch("src.delegation.pipeline.DelegationCoordinator") as MockCoord,
            patch("src.delegation.pipeline.TokenOptimizer"),
        ):
            inst = MockCoord.return_value
            inst.execute_parallel.return_value = {}
            inst.get_statistics.return_value = _fake_stats()
            result = analyze_and_ingest(
                target_dir="proj",
                allow_external=str(ext_base),
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )
        assert isinstance(result, AnalysisPipelineResult)

    def test_external_base_relative_escape_refused(self, ext_base, tmp_path, monkeypatch):
        """A ``../`` target escaping the external base is refused."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="escapes"):
            analyze_and_ingest(
                target_dir="../../../etc/passwd",
                allow_external=str(ext_base),
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

    def test_external_base_absolute_escape_refused(self, ext_base, tmp_path, monkeypatch):
        """An absolute target outside the external base is refused."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="escapes"):
            analyze_and_ingest(
                target_dir=_outside_target(),
                allow_external=str(ext_base),
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

    def test_external_base_symlink_escape_refused(self, ext_base, tmp_path, monkeypatch):
        """A symlink *inside* the external base pointing outside is refused."""
        os.symlink(_outside_target(), ext_base / "escape")
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="escapes"):
            analyze_and_ingest(
                target_dir="escape",
                allow_external=str(ext_base),
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

    def test_external_base_must_be_existing_directory(self, tmp_path, monkeypatch):
        """A non-existent (or non-dir) --allow-external base is refused up front."""
        monkeypatch.chdir(tmp_path)
        missing = tmp_path / "nope"
        with pytest.raises(ValueError, match="allow-external"):
            analyze_and_ingest(
                target_dir=".",
                allow_external=str(missing),
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )

    def test_default_base_still_rejects_traversal(self, tmp_path, monkeypatch):
        """Regression: without allow_external, cwd stays the base and the old message holds."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="escapes working directory"):
            analyze_and_ingest(
                target_dir="../../../etc/passwd",
                kb_path=str(tmp_path / "kb"),
                output_dir=str(tmp_path / "out"),
            )


# --------------------------------------------------------------------------- #
# Layer 2 — the four ComponentAnalyzer-backed agents, rebased onto an external base
# --------------------------------------------------------------------------- #


class TestComponentAgentsExternalBase:
    @pytest.mark.parametrize("agent_cls", COMPONENT_AGENT_CLASSES)
    def test_external_base_honored(self, agent_cls, ext_base, tmp_path, monkeypatch):
        """An in-base target is analyzed even though it lies outside cwd."""
        monkeypatch.chdir(tmp_path)  # cwd is NOT the external base
        agent = agent_cls(agent_id="ext-test", base_path=str(ext_base))
        result = agent.analyze(_task("proj", agent_type=agent.agent_type))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data

    @pytest.mark.parametrize("agent_cls", COMPONENT_AGENT_CLASSES)
    def test_relative_escape_refused(self, agent_cls, ext_base, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = agent_cls(agent_id="ext-test", base_path=str(ext_base))
        result = agent.analyze(_task("../../../../etc", agent_type=agent.agent_type))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("agent_cls", COMPONENT_AGENT_CLASSES)
    def test_absolute_escape_refused(self, agent_cls, ext_base, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = agent_cls(agent_id="ext-test", base_path=str(ext_base))
        result = agent.analyze(_task(_outside_target(), agent_type=agent.agent_type))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("agent_cls", COMPONENT_AGENT_CLASSES)
    def test_symlink_escape_refused(self, agent_cls, ext_base, tmp_path, monkeypatch):
        """A symlink inside the external base that resolves outside it is refused."""
        os.symlink(_outside_target(), ext_base / "escape")
        monkeypatch.chdir(tmp_path)
        agent = agent_cls(agent_id="ext-test", base_path=str(ext_base))
        result = agent.analyze(_task("escape", agent_type=agent.agent_type))
        assert result.status == SubAgentStatus.FAILED
        assert any("escapes" in e.lower() for e in result.errors)


# --------------------------------------------------------------------------- #
# Layer 3 — DocumentationAgent (own resolve_within + BatchFileReader), external base
# --------------------------------------------------------------------------- #


class TestDocumentationAgentExternalBase:
    def test_external_base_honored(self, ext_base, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = DocumentationAgent(agent_id="doc-ext", base_path=str(ext_base))
        result = agent.analyze(_task("proj"))
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data["files_analyzed"] >= 1

    def test_relative_escape_refused(self, ext_base, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = DocumentationAgent(agent_id="doc-ext", base_path=str(ext_base))
        result = agent.analyze(_task("../../../../etc"))
        assert result.status == SubAgentStatus.FAILED
        assert "escapes" in " ".join(result.errors).lower()

    def test_absolute_escape_refused(self, ext_base, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agent = DocumentationAgent(agent_id="doc-ext", base_path=str(ext_base))
        result = agent.analyze(_task(_outside_target()))
        assert result.status == SubAgentStatus.FAILED
        assert "escapes" in " ".join(result.errors).lower()

    def test_symlink_escape_refused(self, ext_base, tmp_path, monkeypatch):
        os.symlink(_outside_target(), ext_base / "escape")
        monkeypatch.chdir(tmp_path)
        agent = DocumentationAgent(agent_id="doc-ext", base_path=str(ext_base))
        result = agent.analyze(_task("escape"))
        assert result.status == SubAgentStatus.FAILED
        assert "escapes" in " ".join(result.errors).lower()
