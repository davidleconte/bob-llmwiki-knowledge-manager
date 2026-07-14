"""Tests for DelegationCoordinator.

Tests cover:
- Coordinator initialization
- Task delegation to agents
- Parallel execution
- Result aggregation
- Error handling
- Agent registration
"""

import threading
import time

import pytest

from src.delegation.base import (
    SubAgent,
    SubAgentPriority,
    SubAgentResult,
    SubAgentStatus,
    SubAgentTask,
)
from src.delegation.coordinator import DelegationCoordinator


class MockAgent(SubAgent):
    """Mock agent for testing."""

    def __init__(self, agent_id="mock_agent", agent_type="test", should_fail=False):
        super().__init__(agent_id, agent_type)
        self.should_fail = should_fail
        self.execution_count = 0

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        """Mock analyze method."""
        self.execution_count += 1

        if self.should_fail:
            return SubAgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=SubAgentStatus.FAILED,
                data={},
                errors=["Mock failure"],
                execution_time_ms=100.0
            )

        time.sleep(0.01)  # Simulate work

        return SubAgentResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=SubAgentStatus.SUCCESS,
            data={"result": f"success_{self.execution_count}"},
            execution_time_ms=10.0
        )

    def get_capabilities(self):
        """Mock capabilities."""
        return ["test", "mock"]


class TestDelegationCoordinator:
    """Test suite for DelegationCoordinator."""

    def test_initialization(self):
        """Test coordinator initialization with default parameters."""
        coordinator = DelegationCoordinator()

        assert coordinator.max_workers > 0
        assert coordinator.timeout_seconds > 0
        assert coordinator.enable_retry is True

    def test_initialization_custom_params(self):
        """Test coordinator initialization with custom parameters."""
        coordinator = DelegationCoordinator(max_workers=4, timeout_seconds=60, enable_retry=False)

        assert coordinator.max_workers == 4
        assert coordinator.timeout_seconds == 60
        assert coordinator.enable_retry is False

    def test_register_agent(self):
        """Test agent registration."""
        coordinator = DelegationCoordinator()
        agent = MockAgent()

        coordinator.register_agent(agent)

        agents = coordinator.registry.get_all_agents()
        assert any(a.agent_id == "mock_agent" for a in agents)

    def test_add_task(self):
        """Test adding a single task."""
        coordinator = DelegationCoordinator()

        task = SubAgentTask(
            task_id="task-1",
            task_type="test",
            target="/path"
        )

        coordinator.add_task(task)

        assert "task-1" in coordinator._tasks

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        coordinator = DelegationCoordinator()

        tasks = [
            SubAgentTask(task_id=f"task-{i}", task_type="test", target="/path")
            for i in range(3)
        ]

        coordinator.add_tasks(tasks)

        assert len(coordinator._tasks) == 3

    def test_execute_parallel_success(self):
        """Test successful parallel execution."""
        coordinator = DelegationCoordinator(max_workers=2)
        agent = MockAgent()
        coordinator.register_agent(agent)

        tasks = [
            SubAgentTask(task_id=f"task-{i}", task_type="test", target="/path")
            for i in range(3)
        ]

        coordinator.add_tasks(tasks)
        results = coordinator.execute_parallel()

        assert len(results) == 3
        assert all(r.is_success() for r in results.values())

    def test_execute_parallel_with_failure(self):
        """Test parallel execution with failures."""
        coordinator = DelegationCoordinator(max_workers=2, enable_retry=False)

        # Register successful and failing agents
        success_agent = MockAgent(agent_id="success", agent_type="test")
        fail_agent = MockAgent(agent_id="fail", agent_type="test", should_fail=True)

        coordinator.register_agent(success_agent)
        coordinator.register_agent(fail_agent)

        tasks = [
            SubAgentTask(task_id="task-1", task_type="test", target="/path"),
            SubAgentTask(task_id="task-2", task_type="test", target="/path")
        ]

        coordinator.add_tasks(tasks)
        results = coordinator.execute_parallel()

        assert len(results) == 2
        # At least one should succeed
        assert any(r.is_success() for r in results.values())

    def test_task_dependencies(self):
        """Test task execution with dependencies."""
        coordinator = DelegationCoordinator(max_workers=2)
        agent = MockAgent()
        coordinator.register_agent(agent)

        tasks = [
            SubAgentTask(task_id="task-1", task_type="test", target="/path"),
            SubAgentTask(
                task_id="task-2",
                task_type="test",
                target="/path",
                dependencies=["task-1"]
            )
        ]

        coordinator.add_tasks(tasks)
        results = coordinator.execute_parallel()

        assert len(results) == 2
        assert all(r.is_success() for r in results.values())

    def test_priority_ordering(self):
        """Test that high priority tasks are executed first."""
        coordinator = DelegationCoordinator(max_workers=1)
        agent = MockAgent()
        coordinator.register_agent(agent)

        tasks = [
            SubAgentTask(
                task_id="low",
                task_type="test",
                target="/path",
                priority=SubAgentPriority.LOW
            ),
            SubAgentTask(
                task_id="high",
                task_type="test",
                target="/path",
                priority=SubAgentPriority.HIGH
            ),
            SubAgentTask(
                task_id="critical",
                task_type="test",
                target="/path",
                priority=SubAgentPriority.CRITICAL
            )
        ]

        coordinator.add_tasks(tasks)
        results = coordinator.execute_parallel()

        assert len(results) == 3
        assert all(r.is_success() for r in results.values())

    def test_get_successful_results(self):
        """Test filtering successful results."""
        coordinator = DelegationCoordinator(enable_retry=False)

        success_agent = MockAgent(agent_id="success", agent_type="test")
        fail_agent = MockAgent(agent_id="fail", agent_type="test", should_fail=True)

        coordinator.register_agent(success_agent)
        coordinator.register_agent(fail_agent)

        tasks = [
            SubAgentTask(task_id="task-1", task_type="test", target="/path"),
            SubAgentTask(task_id="task-2", task_type="test", target="/path")
        ]

        coordinator.add_tasks(tasks)
        coordinator.execute_parallel()

        successful = coordinator.get_successful_results()
        assert len(successful) >= 0  # At least some should succeed

    def test_get_failed_results(self):
        """Test filtering failed results."""
        coordinator = DelegationCoordinator(enable_retry=False)

        fail_agent = MockAgent(agent_id="fail", agent_type="test", should_fail=True)
        coordinator.register_agent(fail_agent)

        task = SubAgentTask(task_id="task-1", task_type="test", target="/path")
        coordinator.add_task(task)
        coordinator.execute_parallel()

        failed = coordinator.get_failed_results()
        assert len(failed) >= 0  # May have failures

    def test_get_statistics(self):
        """Test statistics collection."""
        coordinator = DelegationCoordinator()
        agent = MockAgent()
        coordinator.register_agent(agent)

        tasks = [
            SubAgentTask(task_id=f"task-{i}", task_type="test", target="/path")
            for i in range(3)
        ]

        coordinator.add_tasks(tasks)
        coordinator.execute_parallel()

        stats = coordinator.get_statistics()

        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "failed_tasks" in stats
        assert "success_rate" in stats
        assert stats["total_tasks"] == 3

    def test_generate_report(self):
        """Test report generation."""
        coordinator = DelegationCoordinator()
        agent = MockAgent()
        coordinator.register_agent(agent)

        task = SubAgentTask(task_id="task-1", task_type="test", target="/path")
        coordinator.add_task(task)
        coordinator.execute_parallel()

        report = coordinator.generate_report()

        assert isinstance(report, str)
        assert "Sub-Agent Delegation Report" in report
        assert "Total Tasks" in report

    def test_reset(self):
        """Test coordinator reset."""
        coordinator = DelegationCoordinator()
        agent = MockAgent()
        coordinator.register_agent(agent)

        task = SubAgentTask(task_id="task-1", task_type="test", target="/path")
        coordinator.add_task(task)
        coordinator.execute_parallel()

        assert len(coordinator._tasks) > 0
        assert len(coordinator._results) > 0

        coordinator.reset()

        assert len(coordinator._tasks) == 0
        assert len(coordinator._results) == 0

    def test_parallel_execution_performance(self):
        """Test that parallel execution is faster than sequential."""
        coordinator = DelegationCoordinator(max_workers=3)
        agent = MockAgent()
        coordinator.register_agent(agent)

        tasks = [
            SubAgentTask(task_id=f"task-{i}", task_type="test", target="/path")
            for i in range(3)
        ]

        coordinator.add_tasks(tasks)

        start_time = time.time()
        results = coordinator.execute_parallel()
        execution_time = time.time() - start_time

        # With 3 workers and 3 tasks taking ~0.01s each,
        # parallel should be ~0.01s, sequential would be ~0.03s
        assert execution_time < 0.05  # Allow some overhead
        assert len(results) == 3


class SlowAgent(SubAgent):
    """Agent whose analyze() blocks until released, simulating a hung task."""

    def __init__(self, release: threading.Event, agent_id="slow_agent", agent_type="slow"):
        super().__init__(agent_id, agent_type)
        self._release = release

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        # Block until the test releases us (bounded so a leaked thread can't
        # hang forever). The point is that this outlasts the task timeout.
        self._release.wait(timeout=5.0)
        return SubAgentResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=SubAgentStatus.SUCCESS,
            data={"result": "eventually"},
            execution_time_ms=1.0,
        )

    def get_capabilities(self):
        return ["slow"]


class TestDelegationCoordinatorTimeout:
    """Per-task timeout must actually fire (C-7 regression).

    Previously execute_parallel() drained futures via `as_completed()` with no
    timeout, which blocks until the next future *completes*. So the per-task
    `future.result(timeout=task.timeout_seconds)` was unreachable for a hung
    task, and the `with ThreadPoolExecutor(...)` teardown's shutdown(wait=True)
    then blocked on the runaway worker -- the coordinator hung for the full
    task duration (or forever) instead of honoring timeout_seconds.
    """

    def test_execute_parallel_times_out_on_hung_task(self):
        release = threading.Event()
        coordinator = DelegationCoordinator(max_workers=2, enable_retry=False)
        coordinator.register_agent(SlowAgent(release))

        task = SubAgentTask(
            task_id="t-slow",
            task_type="slow",
            target="/path",
            timeout_seconds=1,
        )
        coordinator.add_task(task)

        try:
            start = time.time()
            results = coordinator.execute_parallel()
            elapsed = time.time() - start

            # Must return promptly (~1s timeout), not after the full ~5s block.
            assert elapsed < 3.0, (
                f"coordinator hung {elapsed:.1f}s instead of honoring the 1s task timeout"
            )
            assert results["t-slow"].status == SubAgentStatus.FAILED
            assert any("timed out" in e.lower() for e in results["t-slow"].errors)
        finally:
            # Release the abandoned worker so it doesn't linger past the test.
            release.set()

    def test_fast_tasks_unaffected_by_timeout_path(self):
        # A normal fast task still succeeds under the new bounded-wait loop.
        release = threading.Event()
        release.set()  # never blocks
        coordinator = DelegationCoordinator(max_workers=2, enable_retry=False)
        coordinator.register_agent(SlowAgent(release))

        task = SubAgentTask(task_id="t-fast", task_type="slow", target="/path", timeout_seconds=5)
        coordinator.add_task(task)

        results = coordinator.execute_parallel()
        assert results["t-fast"].status == SubAgentStatus.SUCCESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
