"""A/B velocity harness — the honesty guards are enforced in code, so test them.

These assert the four guards the protocol names: report-everything, the quality
gate, the refuse-to-over-claim floor, and manifest completeness — plus the delta
arithmetic. If any guard regressed, the harness could emit an anecdote as a
measurement; these go red first.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Dict, List

from src.velocity import MIN_VALID_TASKS, _bootstrap_ci, analyze, main, task_list_hash


def _tasks(n: int) -> List[Dict[str, object]]:
    return [
        {"id": f"T{i}", "done_criterion": f"crit {i}", "order": "A-first"} for i in range(1, n + 1)
    ]


def _pair(
    tid: str,
    a_time: float,
    b_time: float,
    *,
    a_ok: bool = True,
    b_ok: bool = True,
    a_coin: float = 1000,
    b_coin: float = 500,
) -> List[Dict[str, object]]:
    return [
        {
            "task_id": tid,
            "condition": "A",
            "wall_clock_min": a_time,
            "bobcoin": a_coin,
            "quality_pass": a_ok,
        },
        {
            "task_id": tid,
            "condition": "B",
            "wall_clock_min": b_time,
            "bobcoin": b_coin,
            "quality_pass": b_ok,
        },
    ]


def test_task_list_hash_is_stable_and_order_independent_of_extra_fields() -> None:
    a = [{"id": "T1", "done_criterion": "x", "order": "A-first"}]
    b = [
        {"id": "T1", "done_criterion": "x", "order": "B-first"}
    ]  # order not part of the freeze hash
    assert task_list_hash(a) == task_list_hash(b)
    c = [{"id": "T1", "done_criterion": "CHANGED"}]
    assert task_list_hash(a) != task_list_hash(c)


def test_delta_arithmetic() -> None:
    tasks = _tasks(5)
    measurements: List[Dict[str, object]] = []
    for i in range(1, 6):
        measurements += _pair(f"T{i}", 10.0, 5.0, a_coin=1000, b_coin=400)
    report = analyze(tasks, measurements, repo_root=Path.cwd())
    per_task = {r["task_id"]: r for r in report["per_task"]}  # type: ignore[union-attr]
    assert per_task["T1"]["delta_time_pct"] == 50.0  # (10-5)/10
    assert per_task["T1"]["delta_bobcoin_pct"] == 60.0  # (1000-400)/1000
    assert report["wall_clock_reduction"]["median_pct"] == 50.0


def test_report_everything_no_task_dropped() -> None:
    tasks = _tasks(8)
    # only provide measurements for 6 of the 8 tasks
    measurements: List[Dict[str, object]] = []
    for i in range(1, 7):
        measurements += _pair(f"T{i}", 10.0, 6.0)
    report = analyze(tasks, measurements, repo_root=Path.cwd())
    assert len(report["per_task"]) == 8  # every pre-registered task present
    incomplete = [r for r in report["per_task"] if not r["valid"]]  # type: ignore[union-attr]
    assert {r["task_id"] for r in incomplete} == {"T7", "T8"}
    assert all("incomplete" in r["reason"] for r in incomplete)  # type: ignore[union-attr]


def test_quality_gate_excludes_b_worse_but_keeps_it() -> None:
    tasks = _tasks(6)
    measurements: List[Dict[str, object]] = []
    for i in range(1, 6):
        measurements += _pair(f"T{i}", 10.0, 5.0)  # 5 clean wins
    measurements += _pair("T6", 10.0, 3.0, b_ok=False)  # faster but wrong -> excluded
    report = analyze(tasks, measurements, repo_root=Path.cwd())
    assert report["n_valid"] == 5  # the fast-but-wrong task did not count
    t6 = next(r for r in report["per_task"] if r["task_id"] == "T6")  # type: ignore[union-attr]
    assert t6["valid"] is False and "quality gate" in t6["reason"]  # kept, flagged


def test_refuses_headline_below_minimum() -> None:
    tasks = _tasks(4)
    measurements: List[Dict[str, object]] = []
    for i in range(1, 5):
        measurements += _pair(f"T{i}", 10.0, 5.0)
    report = analyze(tasks, measurements, repo_root=Path.cwd())
    assert report["n_valid"] < MIN_VALID_TASKS
    assert report["wall_clock_reduction"]["headline"] is None
    assert "insufficient" in report["wall_clock_reduction"]["reason"]
    assert "No velocity claim permitted" in report["allowed_claim"]  # type: ignore[operator]


def test_headline_emitted_with_enough_valid_tasks() -> None:
    tasks = _tasks(8)
    measurements: List[Dict[str, object]] = []
    for i in range(1, 9):
        measurements += _pair(f"T{i}", 10.0, 5.0 + (i % 3))
    report = analyze(tasks, measurements, repo_root=Path.cwd())
    wc = report["wall_clock_reduction"]
    assert wc["n"] == 8
    assert "median_pct" in wc and len(wc["ci95_median"]) == 2  # type: ignore[arg-type]
    assert len(wc["distribution"]) == 8  # full distribution reported


def test_manifest_is_complete() -> None:
    tasks = _tasks(5)
    measurements: List[Dict[str, object]] = []
    for i in range(1, 6):
        measurements += _pair(f"T{i}", 10.0, 5.0)
    report = analyze(
        tasks, measurements, kb_commit="deadbeef", bob_version="bob-1.0", repo_root=Path.cwd()
    )
    assert report["manifest_complete"] is True
    assert report["manifest"]["data_hash"] == report["task_list_hash"]  # type: ignore[index]
    assert report["manifest"]["extra"]["kb_commit"] == "deadbeef"  # type: ignore[index]


def test_bootstrap_degenerate_is_safe() -> None:
    assert _bootstrap_ci([42.0], seed=0, stat=statistics.median) == [42.0, 42.0]
    assert _bootstrap_ci([], seed=0, stat=statistics.median) == [0.0, 0.0]


def test_cli_main_writes_report_and_manifest(tmp_path: Path) -> None:
    tasks = {
        "tasks": [
            {"id": f"T{i}", "done_criterion": f"c{i}", "order": "A-first"} for i in range(1, 6)
        ]
    }
    measurements: List[Dict[str, object]] = []
    for i in range(1, 6):
        measurements += _pair(f"T{i}", 10.0, 5.0, a_coin=1000, b_coin=400)
    meas = {"kb_commit": "abc123", "bob_version": "bob-test", "measurements": measurements}
    tasks_f = tmp_path / "tasks.json"
    tasks_f.write_text(json.dumps(tasks), encoding="utf-8")
    meas_f = tmp_path / "meas.json"
    meas_f.write_text(json.dumps(meas), encoding="utf-8")
    out = tmp_path / "out"

    assert main(["--tasks", str(tasks_f), "--measurements", str(meas_f), "--out", str(out)]) == 0

    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["n_valid"] == 5
    assert report["wall_clock_reduction"]["median_pct"] == 50.0
    assert (out / "manifest.json").is_file()
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["extra"]["kb_commit"] == "abc123"
