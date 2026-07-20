"""A/B developer-velocity measurement harness — the measured before/after.

Every independent review of the submission named the *same* single gap: the only
reproducible figure is token compression — a proxy — and there is no *controlled*
developer-velocity number. This harness produces one with the same rigour as the
compression harness (:mod:`src.validation`): a paired,
counterbalanced, pre-registered A/B over a frozen task list, reported with the
median, the full distribution, N, and a bootstrap 95% CI — behind honesty guards
that make the number defensible instead of anecdotal.

Honesty guards enforced *here* (not left to the operator):
  * **Report everything** — every pre-registered task appears in the output,
    including ties and tasks where memory did not help; none can be dropped.
  * **Quality gate** — a *faster-but-worse* B result is not a win; a task whose B
    answer fails its done-criterion is flagged and excluded from the headline,
    but kept in the report.
  * **Refuse to over-claim** — no headline below the protocol's minimum of five
    valid paired tasks; the reason is stated instead.
  * **Manifest or it did not happen** — the report carries a reproducibility
    manifest (task-list hash, KB commit, seed, versions).

The harness does **not** fabricate timings: the wall-clock and Bobcoin readings
are recorded by a human running each task on Bob under both conditions (cold / no
KB vs. with KB). This module freezes the design, computes the statistics, and
emits the manifest — it is the measurement *instrument*, not the measurement.

Usage::

    python -m src.velocity --tasks evaluation/velocity/tasks.json \\
        --measurements <your-recorded-runs>.json --out evaluation/results/velocity-ab-<date>/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from src.validation.manifest import build_manifest, missing_fields, write_manifest

MIN_VALID_TASKS = 5  # protocol floor: N=8 target, 5 minimum
BOOTSTRAP_ITERS = 2000  # same resample count as the 20% harness
DEFAULT_SEED = 0


def task_list_hash(tasks: Sequence[Dict[str, object]]) -> str:
    """Stable sha256 over the pre-registered task list (the freeze artifact)."""
    canonical = json.dumps(
        [{"id": t.get("id"), "done_criterion": t.get("done_criterion")} for t in tasks],
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _bootstrap_ci(
    values: Sequence[float],
    seed: int,
    stat: Callable[[Sequence[float]], float],
    iters: int = BOOTSTRAP_ITERS,
    alpha: float = 0.05,
) -> List[float]:
    """Percentile bootstrap CI for ``stat`` — the same procedure as the 20% harness."""
    clean = list(values)
    if len(clean) < 2:
        point = clean[0] if clean else 0.0
        return [round(point, 4), round(point, 4)]
    rng = random.Random(seed)
    n = len(clean)
    stats_: List[float] = []
    for _ in range(iters):
        resample = [clean[rng.randrange(n)] for _ in range(n)]
        stats_.append(stat(resample))
    stats_.sort()
    lo = stats_[int((alpha / 2) * iters)]
    hi = stats_[min(int((1 - alpha / 2) * iters), iters - 1)]
    return [round(lo, 4), round(hi, 4)]


@dataclass
class TaskResult:
    """The paired A/B outcome for a single pre-registered task (kept even if invalid)."""

    task_id: str
    valid: bool
    reason: str
    order: str
    a_wall_clock_min: Optional[float]
    b_wall_clock_min: Optional[float]
    a_bobcoin: Optional[float]
    b_bobcoin: Optional[float]
    delta_time_pct: Optional[float]
    delta_bobcoin_pct: Optional[float]


def _pct_reduction(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """Percentage reduction from A to B; ``None`` if A is missing or non-positive."""
    if a is None or b is None or a <= 0:
        return None
    return round((a - b) / a * 100.0, 4)


def _pair(measurements: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Group measurements by task id, then by condition (A / B)."""
    by_task: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for m in measurements:
        by_task.setdefault(str(m["task_id"]), {})[str(m["condition"]).upper()] = m
    return by_task


def _summary(deltas: List[float], seed: int) -> Dict[str, object]:
    """Median-centred summary with a bootstrap CI, or a refusal below the floor."""
    if len(deltas) < MIN_VALID_TASKS:
        return {
            "headline": None,
            "reason": (
                f"insufficient valid paired tasks (need >={MIN_VALID_TASKS}, have {len(deltas)}) "
                "— no velocity claim permitted"
            ),
            "n": len(deltas),
        }
    return {
        "median_pct": round(statistics.median(deltas), 4),
        "mean_pct": round(statistics.mean(deltas), 4),
        "min_pct": round(min(deltas), 4),
        "max_pct": round(max(deltas), 4),
        "ci95_median": _bootstrap_ci(deltas, seed, statistics.median),
        "n": len(deltas),
        "distribution": sorted(round(d, 2) for d in deltas),
    }


def _allowed_claim(n_valid: int) -> str:
    if n_valid < MIN_VALID_TASKS:
        return (
            f"No velocity claim permitted: fewer than the minimum {MIN_VALID_TASKS} valid paired "
            "tasks. Run more tasks; do not extrapolate and do not cite a number."
        )
    return (
        "Permitted: 'median X% wall-clock and Y% Bobcoin reduction per iteration cycle "
        "(N valid paired tasks, 95% CI [...]), single-project, paired A/B.' "
        "NOT permitted: annualising, generalising across teams, or blending with the 20%/cache numbers."
    )


def analyze(
    tasks: Sequence[Dict[str, Any]],
    measurements: Sequence[Dict[str, Any]],
    *,
    seed: int = DEFAULT_SEED,
    kb_commit: str = "",
    bob_version: str = "",
    repo_root: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, object]:
    """Compute the paired A/B velocity report with honesty guards + manifest."""
    repo_root = repo_root or Path.cwd()
    by_task = _pair(measurements)

    results: List[TaskResult] = []
    for task in tasks:
        tid = str(task["id"])
        pair = by_task.get(tid, {})
        run_a, run_b = pair.get("A"), pair.get("B")
        order = str(task.get("order", ""))
        if run_a is None or run_b is None:
            results.append(
                TaskResult(tid, False, "incomplete: missing A or B run", order,
                           None, None, None, None, None, None)
            )
            continue
        a_time, b_time = float(run_a["wall_clock_min"]), float(run_b["wall_clock_min"])
        a_coin, b_coin = float(run_a["bobcoin"]), float(run_b["bobcoin"])
        # Quality gate: B must be verified at least as correct as A to count.
        valid = bool(run_a.get("quality_pass", False)) and bool(run_b.get("quality_pass", False))
        reason = "ok" if valid else "quality gate: B not verified at least as correct as A (excluded)"
        results.append(
            TaskResult(
                tid, valid, reason, order,
                a_time, b_time, a_coin, b_coin,
                _pct_reduction(a_time, b_time), _pct_reduction(a_coin, b_coin),
            )
        )

    valid_results = [r for r in results if r.valid]
    time_deltas = [r.delta_time_pct for r in valid_results if r.delta_time_pct is not None]
    coin_deltas = [r.delta_bobcoin_pct for r in valid_results if r.delta_bobcoin_pct is not None]

    manifest = build_manifest(
        config={
            "protocol": "paired-counterbalanced-prereg-AB",
            "min_valid_tasks": MIN_VALID_TASKS,
            "bootstrap_iters": BOOTSTRAP_ITERS,
            "token_source": "bob-session-readout (not local tiktoken)",
        },
        data_hash=task_list_hash(tasks),
        seed=seed,
        model=bob_version or "bob-session",
        tiktoken_active=False,
        repo_root=repo_root,
        timestamp=timestamp,
        extra={
            "kb_commit": kb_commit,
            "bob_version": bob_version,
            "n_tasks": len(tasks),
            "n_valid": len(valid_results),
        },
    )

    report: Dict[str, object] = {
        "measurement": "developer-velocity A/B (paired, counterbalanced, pre-registered)",
        "task_list_hash": task_list_hash(tasks),
        "wall_clock_reduction": _summary(time_deltas, seed),
        "bobcoin_reduction": _summary(coin_deltas, seed + 1),
        "n_tasks": len(tasks),
        "n_valid": len(valid_results),
        "per_task": [r.__dict__ for r in results],
        "manifest": manifest,
        "manifest_complete": not missing_fields(manifest),
        "allowed_claim": _allowed_claim(len(valid_results)),
    }
    # Report-everything invariant: no pre-registered task may be silently dropped.
    assert len(report["per_task"]) == len(tasks), "report-everything invariant violated"  # type: ignore[arg-type]
    return report


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.velocity",
        description="A/B developer-velocity measurement (paired, counterbalanced, pre-registered).",
    )
    parser.add_argument("--tasks", required=True, type=Path, help="Pre-registered tasks JSON")
    parser.add_argument(
        "--measurements", required=True, type=Path, help="Recorded A/B measurements JSON"
    )
    parser.add_argument(
        "--out", type=Path, default=None, help="Output dir for report.json + manifest.json"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)

    tasks_doc = _load(args.tasks)
    m_doc = _load(args.measurements)
    report = analyze(
        list(tasks_doc["tasks"]),
        list(m_doc.get("measurements", [])),
        seed=args.seed,
        kb_commit=str(m_doc.get("kb_commit", "")),
        bob_version=str(m_doc.get("bob_version", "")),
    )

    preview = {k: v for k, v in report.items() if k != "per_task"}
    print(json.dumps(preview, indent=2, default=str))

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8"
        )
        write_manifest(args.out / "manifest.json", report["manifest"])  # type: ignore[arg-type]
        print(f"\nWrote {args.out}/report.json + manifest.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
