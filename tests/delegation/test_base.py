"""Tests for delegation base classes.

Tests cover:
- SubAgentTask creation and validation
- SubAgentResult creation and validation
- SubAgentPriority enum
- SubAgent interface
"""

import pytest

from src.delegation.base import (
    SubAgent,
    SubAgentPriority,
    SubAgentResult,
    SubAgentStatus,
    SubAgentTask,
)


class TestSubAgentTask:
    """Test suite for SubAgentTask."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = SubAgentTask(
            task_id="task-123",
            task_type="security_scan",
            target="/path/to/repo",
            parameters={"depth": "full"},
            priority=SubAgentPriority.HIGH,
        )

        assert task.task_id == "task-123"
        assert task.task_type == "security_scan"
        assert task.target == "/path/to/repo"
        assert task.priority == SubAgentPriority.HIGH
        assert task.parameters["depth"] == "full"

    def test_task_default_priority(self):
        """Test that default priority is MEDIUM."""
        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        assert task.priority == SubAgentPriority.MEDIUM

    def test_task_can_execute_no_dependencies(self):
        """Test can_execute with no dependencies."""
        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        assert task.can_execute(set()) is True

    def test_task_can_execute_with_dependencies(self):
        """Test can_execute with dependencies."""
        task = SubAgentTask(
            task_id="task-123", task_type="test", target="/path", dependencies=["task-1", "task-2"]
        )

        # Not all dependencies met
        assert task.can_execute({"task-1"}) is False

        # All dependencies met
        assert task.can_execute({"task-1", "task-2"}) is True

    def test_task_should_retry(self):
        """Test retry logic."""
        task = SubAgentTask(task_id="task-123", task_type="test", target="/path", max_retries=3)

        assert task.should_retry() is True

        task.retry_count = 3
        assert task.should_retry() is False


class TestSubAgentResult:
    """Test suite for SubAgentResult."""

    def test_result_creation_success(self):
        """Test successful result creation."""
        result = SubAgentResult(
            agent_id="agent-123",
            agent_type="security",
            status=SubAgentStatus.SUCCESS,
            data={"findings": ["issue1", "issue2"]},
            execution_time_ms=1500.0,
        )

        assert result.agent_id == "agent-123"
        assert result.agent_type == "security"
        assert result.status == SubAgentStatus.SUCCESS
        assert result.data == {"findings": ["issue1", "issue2"]}
        assert result.execution_time_ms == 1500.0
        assert result.is_success() is True

    def test_result_creation_failure(self):
        """Test failed result creation."""
        result = SubAgentResult(
            agent_id="agent-123",
            agent_type="security",
            status=SubAgentStatus.FAILED,
            data={},
            errors=["Agent execution failed"],
            execution_time_ms=500.0,
        )

        assert result.agent_id == "agent-123"
        assert result.status == SubAgentStatus.FAILED
        assert result.is_success() is False
        assert result.has_errors() is True
        assert len(result.errors) == 1

    def test_result_to_dict(self):
        """Test result serialization to dict."""
        result = SubAgentResult(
            agent_id="agent-123",
            agent_type="security",
            status=SubAgentStatus.SUCCESS,
            data={"key": "value"},
            execution_time_ms=1500.0,
        )

        result_dict = result.to_dict()

        assert result_dict["agent_id"] == "agent-123"
        assert result_dict["agent_type"] == "security"
        assert result_dict["status"] == "success"
        assert result_dict["data"] == {"key": "value"}
        assert result_dict["execution_time_ms"] == 1500.0


class TestSubAgentPriority:
    """Test suite for SubAgentPriority enum."""

    def test_priority_values(self):
        """Test that priority enum has correct values."""
        assert SubAgentPriority.LOW.value == 1
        assert SubAgentPriority.MEDIUM.value == 2
        assert SubAgentPriority.HIGH.value == 3
        assert SubAgentPriority.CRITICAL.value == 4

    def test_priority_comparison(self):
        """Test priority comparison by value."""
        assert SubAgentPriority.CRITICAL.value > SubAgentPriority.HIGH.value
        assert SubAgentPriority.HIGH.value > SubAgentPriority.MEDIUM.value
        assert SubAgentPriority.MEDIUM.value > SubAgentPriority.LOW.value
        assert SubAgentPriority.LOW.value < SubAgentPriority.CRITICAL.value


class MockAgent(SubAgent):
    """Mock agent for testing SubAgent interface."""

    def __init__(self, agent_id="mock_agent", agent_type="test"):
        super().__init__(agent_id, agent_type)

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        """Mock analyze method."""
        return SubAgentResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=SubAgentStatus.SUCCESS,
            data={"result": "mock"},
            execution_time_ms=100.0,
        )

    def get_capabilities(self):
        """Mock capabilities."""
        return ["test", "mock"]


class TestSubAgent:
    """Test suite for SubAgent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MockAgent(agent_id="test_agent", agent_type="test")

        assert agent.agent_id == "test_agent"
        assert agent.agent_type == "test"
        assert agent.cache_enabled is True

    def test_agent_execute(self):
        """Test agent execute method."""
        agent = MockAgent()

        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        result = agent.execute(task)

        assert isinstance(result, SubAgentResult)
        assert result.agent_id == agent.agent_id
        assert result.agent_type == agent.agent_type
        assert result.is_success() is True

    def test_agent_get_capabilities(self):
        """Test get_capabilities method."""
        agent = MockAgent()

        capabilities = agent.get_capabilities()

        assert isinstance(capabilities, list)
        assert "test" in capabilities

    def test_agent_statistics(self):
        """Test agent statistics tracking."""
        agent = MockAgent()

        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        agent.execute(task)

        stats = agent.get_statistics()

        assert stats["tasks_completed"] == 1
        assert stats["tasks_failed"] == 0
        assert stats["agent_id"] == agent.agent_id

    def test_agent_cache(self):
        """Test agent caching."""
        agent = MockAgent()

        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        # First execution
        result1 = agent.execute(task)
        assert "from_cache" not in result1.metadata

        # Second execution (should be cached)
        result2 = agent.execute(task)
        assert result2.metadata.get("from_cache") is True

    def test_agent_clear_cache(self):
        """Test cache clearing."""
        agent = MockAgent()

        task = SubAgentTask(task_id="task-123", task_type="test", target="/path")

        agent.execute(task)
        assert len(agent._cache) > 0

        agent.clear_cache()
        assert len(agent._cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
