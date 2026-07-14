"""Boundary-security test for the delegation DocumentationAgent (Phase 8).

The agent takes an untrusted ``task.target`` and used to call
``Path(target).rglob("*.py")`` directly, so a ``../`` or absolute target could
enumerate ``.py`` files anywhere on disk -- contradicting the containment claim
in ``docs/security/THREAT_MODEL.md``. It now routes ``task.target`` through
``resolve_within(Path.cwd(), target)`` first. These tests lock that in.
"""

from pathlib import Path

from src.delegation.agents.documentation_agent import DocumentationAgent
from src.delegation.base import SubAgentStatus, SubAgentTask

REPO_ROOT = Path(__file__).resolve().parents[2]


def _task(target: str) -> SubAgentTask:
    return SubAgentTask(task_id="doc-test", task_type="documentation", target=target)


def test_rejects_parent_traversal_target(monkeypatch):
    """A ``../`` target that escapes the working directory is refused."""
    monkeypatch.chdir(REPO_ROOT)
    agent = DocumentationAgent(agent_id="doc-1")

    result = agent.analyze(_task("../../../../etc"))

    assert result.status == SubAgentStatus.FAILED
    assert "escapes" in " ".join(result.errors).lower()


def test_rejects_absolute_out_of_tree_target(monkeypatch):
    """An absolute target outside the working directory is refused."""
    monkeypatch.chdir(REPO_ROOT)
    agent = DocumentationAgent(agent_id="doc-2")

    result = agent.analyze(_task("/etc"))

    assert result.status == SubAgentStatus.FAILED
    assert "escapes" in " ".join(result.errors).lower()


def test_accepts_in_tree_target(monkeypatch):
    """A legitimate in-tree target is analyzed normally."""
    monkeypatch.chdir(REPO_ROOT)
    agent = DocumentationAgent(agent_id="doc-3")

    result = agent.analyze(_task("src/delegation/agents"))

    assert result.status == SubAgentStatus.SUCCESS
    assert result.data["files_analyzed"] >= 1
