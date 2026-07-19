"""B3/CODE-10: delegation token counts route through the one TokenCounter home.

Six sub-agents used to count tokens as ``len(str(result_data)) // 4`` (security via
``len(json.dumps(data)) // 4``), a parallel model-blind counting home that fed the
reported totals. They now call ``SubAgent.count_tokens``, which delegates to a shared
``TokenCounter`` — so delegation totals are model-correct and honour the tokenizer's
exact/approximate flag.
"""

from __future__ import annotations

import re
from pathlib import Path

import src.delegation.base as base
from src.delegation.base import SubAgent, SubAgentResult, SubAgentStatus, SubAgentTask
from src.optimizer.token_counter import TokenCounter

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _FakeCounter:
    """Records calls and returns a fixed sentinel count."""

    def __init__(self, value: int) -> None:
        self.value = value
        self.calls: list[str] = []

    def count_tokens(self, text: str) -> int:
        self.calls.append(text)
        return self.value


class _CountingAgent(SubAgent):
    """Minimal concrete agent whose analyze counts via the shared home."""

    def __init__(self, **kwargs):
        super().__init__("counting", "test", **kwargs)

    def analyze(self, task: SubAgentTask) -> SubAgentResult:
        result_data = {"finding": "x", "items": ["a", "b", "c"], "n": 3}
        return SubAgentResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=SubAgentStatus.SUCCESS,
            data=result_data,
            token_count=self.count_tokens(result_data),
        )

    def get_capabilities(self):
        return ["test"]


def test_count_tokens_routes_through_injected_counter():
    """SubAgent.count_tokens delegates to its TokenCounter (injectable)."""
    fake = _FakeCounter(4242)
    agent = _CountingAgent(token_counter=fake)
    assert agent.count_tokens({"a": 1}) == 4242
    assert fake.calls, "the injected counter was not called"


def test_agent_analyze_token_count_uses_shared_counter(monkeypatch):
    """An agent with no injected counter routes analyze() through the shared one."""
    shared = base._get_shared_token_counter()
    monkeypatch.setattr(shared, "count_tokens", lambda text: 777)

    agent = _CountingAgent()  # -> shared counter
    result = agent.execute(SubAgentTask(task_id="t", task_type="x", target="/p"))

    assert result.token_count == 777, "analyze did not count via the shared TokenCounter"


def test_count_tokens_is_real_tokenizer_not_div4():
    """count_tokens returns the real tokenizer count, not the old len//4 heuristic."""
    agent = _CountingAgent()
    data = {"issues": ["x" * 100, "y" * 100], "count": 2}
    text = str(data)

    assert agent.count_tokens(data) == TokenCounter().count_tokens(text)
    # The whole point of B3: it is NOT the len//4 approximation.
    assert agent.count_tokens(data) != len(text) // 4


def test_no_div4_token_heuristic_in_agents():
    """RED->GREEN grep guard: no sub-agent counts tokens with ``// 4``.

    Reverting any agent to ``len(str(result_data)) // 4`` reintroduces the parallel
    counting home and fails here. (base.py may reference the pattern in prose — only
    the agent modules are scanned, and inline comments are stripped.)
    """
    agents_dir = _REPO_ROOT / "src" / "delegation" / "agents"
    offenders: list[str] = []
    for path in sorted(agents_dir.glob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]  # ignore trailing comments
            if re.search(r"//\s*4\b", code):
                offenders.append(f"{path.name}:{lineno}: {line.strip()}")

    assert not offenders, (
        "delegation agents must count via self.count_tokens(...), not `// 4`:\n"
        + "\n".join(offenders)
    )
