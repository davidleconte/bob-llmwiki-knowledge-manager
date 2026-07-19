"""Delegation analysis pipeline.

Runs the six delegation agents in parallel over a target directory, compresses each
agent report through :class:`~src.facade.TokenOptimizer`, and writes structured
KB research documents to *output_dir*.

This module is the **integration surface** between the delegation subsystem and the
Token Optimization System.  It deliberately keeps the surface small (~60 lines of
logic) so the coordinator and agents remain independently testable.

Usage::

    from src.delegation.pipeline import analyze_and_ingest

    result = analyze_and_ingest("src/cache", output_dir="docs/knowledge-base/research")
    print(result.agents_succeeded, "agents succeeded")
    print(result.compression_ratios)   # per-agent compression ratio
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.delegation.agents import (
    ArchitectureAgent,
    DocumentationAgent,
    PerformanceAgent,
    QualityAgent,
    ResearchAgent,
    SecurityAgent,
)
from src.delegation.base import SubAgentPriority, SubAgentTask
from src.delegation.coordinator import DelegationCoordinator
from src.facade import TokenOptimizer
from src.tools.safe_paths import resolve_within

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class AnalysisPipelineResult:
    """Outcome of a :func:`analyze_and_ingest` run.

    Attributes:
        target_dir: The directory that was analysed.
        agents_run: Total number of agents that were dispatched.
        agents_succeeded: Number that completed with SUCCESS status.
        agents_failed: Number that failed or timed out.
        compression_ratios: Mapping of task_id → compression_ratio (1.0 = no compression).
        total_tokens_saved: Estimated tokens saved across all compressed reports.
        wall_clock_ms: Total wall-clock time in milliseconds.
        output_files: Paths of KB research docs written to *output_dir*.
        coordinator_stats: Raw statistics from :meth:`DelegationCoordinator.get_statistics`.
    """

    target_dir: str
    agents_run: int
    agents_succeeded: int
    agents_failed: int
    compression_ratios: Dict[str, float] = field(default_factory=dict)
    total_tokens_saved: int = 0
    wall_clock_ms: float = 0.0
    output_files: List[str] = field(default_factory=list)
    coordinator_stats: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_and_ingest(
    target_dir: str,
    kb_path: str = "docs/knowledge-base",
    output_dir: str = "docs/knowledge-base/research",
    max_workers: int = 5,
    depth: str = "shallow",
    *,
    compress: bool = True,
) -> AnalysisPipelineResult:
    """Run parallel delegation analysis and ingest results into the KB.

    Sequences:

    1. ``ResearchAgent`` runs first (no dependencies) to load prior KB findings.
    2. All other agents run in parallel after research completes (dependency wave).
    3. Each successful result is optionally compressed via ``TokenOptimizer``.
    4. Compressed (or raw) reports are written as KB research docs to *output_dir*.

    Args:
        target_dir: Directory (or file) to analyse.  Must not escape cwd.
        kb_path: KB root for :class:`~src.delegation.agents.ResearchAgent` context lookup.
        output_dir: Directory to write generated research docs.
        max_workers: Maximum parallel agent workers.
        depth: Analysis depth — ``"shallow"`` or ``"deep"``.
        compress: Pass agent reports through :class:`~src.facade.TokenOptimizer`
            before writing.  Set ``False`` to write raw JSON.

    Returns:
        :class:`AnalysisPipelineResult` with per-agent status and compression metrics.
    """
    # ------------------------------------------------------------------
    # Path containment: reject target_dir that escapes cwd.
    # ------------------------------------------------------------------
    cwd = Path.cwd()
    try:
        resolve_within(cwd, target_dir)
    except ValueError as exc:
        raise ValueError(f"target_dir escapes working directory: {exc}") from exc

    # ------------------------------------------------------------------
    # Build coordinator and register agents.
    # ------------------------------------------------------------------
    coordinator = DelegationCoordinator(max_workers=max_workers, timeout_seconds=600)
    coordinator.register_agent(ResearchAgent("research-1", kb_path=kb_path))
    coordinator.register_agent(SecurityAgent("security-1"))
    coordinator.register_agent(QualityAgent("quality-1"))
    coordinator.register_agent(PerformanceAgent("perf-1"))
    coordinator.register_agent(ArchitectureAgent("arch-1"))
    coordinator.register_agent(DocumentationAgent("doc-1"))

    # ResearchAgent runs first (no deps); all others depend on its task_id so the
    # coordinator dispatches them in the second wave after research completes.
    coordinator.add_tasks(
        [
            SubAgentTask(
                task_id="research-task",
                task_type="research",
                target=target_dir,
                priority=SubAgentPriority.CRITICAL,
                parameters={
                    "query": f"prior findings security quality performance architecture {Path(target_dir).name}",
                    "max_results": 5,
                },
            ),
            SubAgentTask(
                "security-task",
                "security",
                target_dir,
                priority=SubAgentPriority.HIGH,
                dependencies=["research-task"],
                parameters={"depth": depth},
            ),
            SubAgentTask(
                "quality-task",
                "quality",
                target_dir,
                priority=SubAgentPriority.MEDIUM,
                dependencies=["research-task"],
                parameters={"depth": depth},
            ),
            SubAgentTask(
                "perf-task",
                "performance",
                target_dir,
                priority=SubAgentPriority.MEDIUM,
                dependencies=["research-task"],
                parameters={"depth": depth},
            ),
            SubAgentTask(
                "arch-task",
                "architecture",
                target_dir,
                priority=SubAgentPriority.MEDIUM,
                dependencies=["research-task"],
                parameters={"depth": depth},
            ),
            SubAgentTask(
                "docs-task",
                "documentation",
                target_dir,
                priority=SubAgentPriority.LOW,
                dependencies=["research-task"],
                parameters={"depth": depth},
            ),
        ]
    )

    optimizer = TokenOptimizer() if compress else None
    results = coordinator.execute_parallel()
    stats = coordinator.get_statistics()

    # ------------------------------------------------------------------
    # Compress and write each successful result to the KB.
    # ------------------------------------------------------------------
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # ATK-MEM-06: sign each generated document's provenance so a hand-forged
    # `generated_by: delegation-pipeline` stamp (or a tampered body) is detectable.
    from src.provenance import attach_signature, load_or_create_key

    _prov_key = load_or_create_key(out_path)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_slug = re.sub(r"[^a-zA-Z0-9]+", "-", target_dir).strip("-")

    compression_ratios: Dict[str, float] = {}
    total_tokens_saved = 0
    output_files: List[str] = []

    for task_id, result in results.items():
        if not result.is_success():
            continue

        agent_type = result.agent_type
        report_text = _result_to_markdown(task_id, agent_type, result.data, target_dir, date_str)

        if optimizer is not None:
            optimized = optimizer.optimize(report_text)
            content = optimized["optimized_text"]
            ratio = float(optimized.get("compression_ratio", 1.0))
            saved = optimized.get("original_tokens", 0) - optimized.get("optimized_tokens", 0)
            total_tokens_saved += max(0, int(saved))
        else:
            content = report_text
            ratio = 1.0

        compression_ratios[task_id] = ratio

        filename = f"delegation-{agent_type}-{target_slug}-{date_str}.md"
        try:
            full_out = resolve_within(out_path, filename)
        except ValueError:
            continue  # skip unsafe filenames

        content = attach_signature(content, _prov_key)
        full_out.write_text(content, encoding="utf-8")
        output_files.append(str(full_out))

    return AnalysisPipelineResult(
        target_dir=target_dir,
        agents_run=stats.get("total_tasks", 0),
        agents_succeeded=stats.get("completed_tasks", 0),
        agents_failed=stats.get("failed_tasks", 0),
        compression_ratios=compression_ratios,
        total_tokens_saved=total_tokens_saved,
        wall_clock_ms=stats.get("total_execution_time_ms", 0.0),
        output_files=output_files,
        coordinator_stats=stats,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _result_to_markdown(
    task_id: str,
    agent_type: str,
    data: Dict[str, Any],
    target_dir: str,
    date_str: str,
) -> str:
    """Render an agent result dict as a KB research document."""
    title = f"{agent_type.capitalize()} Analysis: {target_dir}"
    body = json.dumps(data, indent=2, default=str)

    return f"""---
title: "{title}"
date: {date_str}
type: research
status: generated
trust_tier: generated
tags: [delegation, {agent_type}, analysis]
generated_by: delegation-pipeline
source: delegation-pipeline
target: {target_dir}
task_id: {task_id}
---

# {title}

*Generated by `bob-optimize analyze` on {date_str}.*

```json
{body}
```
"""
