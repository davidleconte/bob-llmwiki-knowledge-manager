# pipeline

Delegation analysis pipeline.

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

## Functions

### `analyze_and_ingest(target_dir: str, kb_path: str, output_dir: str, max_workers: int, depth: str) -> AnalysisPipelineResult`

Run parallel delegation analysis and ingest results into the KB.

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


### `_result_to_markdown(task_id: str, agent_type: str, data: Dict[str, Any], target_dir: str, date_str: str) -> str`

Render an agent result dict as a KB research document.


## Classes

### `AnalysisPipelineResult`

Outcome of a :func:`analyze_and_ingest` run.

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

