"""A8 — scale-regression gate (governance of WS-A).

Encodes the WS-A scaling ratios as hard assertions. Unlike the benchmark job
(main-only, ``--benchmark-only``), this module runs as a plain pytest step on
every PR (see the "Scale-regression gate (A8)" step in ``.github/workflows/
ci.yml``), so a re-introduced quadratic in any of the four WS-A hot paths —
PageRank dangling redistribution (A1), ``build_semantic`` similarity (A2), the
index cold rebuild (A3ii), or L2 eviction (A4) — blows the corresponding ratio
and fails CI before it reaches ``main``.

Design:
  * **Ratios, not absolute times** — a growth factor across a size step is
    machine-independent and survives shared-runner noise.
  * **Ceilings live in one home** — ``config/gates/gate-config.yaml::perf_scale``,
    a CODEOWNERS-reviewed file, so a weakening is conspicuous (the ATK-GATE-07
    tie-in). This module *reads* them; it never restates a literal.
  * **min-of-trials** for the cheap in-memory paths (PageRank, eviction) filters
    scheduling / GC noise; the index-building paths measure once under a generous
    ceiling because a repeat would triple the embed cost.

The synthetic-corpus and timing helpers are reused from ``test_dos_hardening`` so
the regression fixtures and this gate stay in lockstep.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import yaml

from src.graph.graph import KnowledgeGraph
from tests.performance.test_dos_hardening import (
    _indexed_kb,
    _per_eviction_seconds,
    _rebuild_time,
    _time_build_semantic,
)

_GATE_CONFIG = Path(__file__).resolve().parents[2] / "config" / "gates" / "gate-config.yaml"


def _perf_scale() -> dict:
    """Load the A8 ratio ceilings from their single home (gate-config.yaml)."""
    with _GATE_CONFIG.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)["perf_scale"]


def _min_of(fn: Callable[[], float], trials: int = 3) -> float:
    """Minimum wall-time across *trials* — the standard robust timing estimator:
    the least-contended run is the one closest to the algorithm's true cost."""
    return min(fn() for _ in range(trials))


def _assert_ratio_under(ratio: float, ceiling: float, label: str, detail: str = "") -> None:
    assert ratio < ceiling, (
        f"{label}: growth ratio {ratio:.2f} ≥ ceiling {ceiling} — a WS-A hot path "
        f"may have regressed to super-linear. {detail}"
    )


# --------------------------------------------------------------------------- #
# A1 — PageRank dangling redistribution
# --------------------------------------------------------------------------- #


def _time_pagerank(n: int) -> float:
    """Time PageRank on the adversarial mixed-dangling graph at *n* nodes.

    N-2 dangling nodes + a 2-node feedback cycle (slow ~damping convergence) — the
    structure test_dos_hardening uses to expose the O(N^2) dangling loop. All-
    dangling would converge in one iteration and hide a regression.
    """
    graph = KnowledgeGraph()
    for i in range(n):
        graph.add_node(f"concepts/doc_{i}.md")
    graph.add_edge("concepts/doc_0.md", "concepts/doc_1.md", "semantic", 1.0)
    graph.add_edge("concepts/doc_1.md", "concepts/doc_0.md", "semantic", 1.0)
    t0 = time.perf_counter()
    graph.pagerank()
    return time.perf_counter() - t0


def _pagerank_ratio(n_small: int, n_large: int) -> float:
    t_small = _min_of(lambda: _time_pagerank(n_small))
    t_large = _min_of(lambda: _time_pagerank(n_large))
    return t_large / max(t_small, 1e-6)


def test_pagerank_scale_ratio():
    """PageRank t(4k)/t(1k) must stay under the perf_scale ceiling (A1/ATK-DOS-01)."""
    ceiling = _perf_scale()["pagerank_4k_over_1k"]
    _assert_ratio_under(_pagerank_ratio(1000, 4000), ceiling, "PageRank t(4k)/t(1k)")


# --------------------------------------------------------------------------- #
# A2 — build_semantic similarity
# --------------------------------------------------------------------------- #


def test_build_semantic_scale_ratio(tmp_path):
    """build_semantic t(2k)/t(500) must stay under the ceiling (A2/CODE-13)."""
    ceiling = _perf_scale()["build_semantic_2k_over_500"]
    t500, e500 = _time_build_semantic(*_indexed_kb(tmp_path, 500))
    t2k, e2k = _time_build_semantic(*_indexed_kb(tmp_path, 2000))
    assert e500 > 0 and e2k > 0, f"expected clustered edges, got {e500}/{e2k}"
    _assert_ratio_under(
        t2k / max(t500, 1e-6),
        ceiling,
        "build_semantic t(2k)/t(500)",
        f"(t500={t500 * 1e3:.0f}ms t2k={t2k * 1e3:.0f}ms)",
    )


# --------------------------------------------------------------------------- #
# A3(ii) — index cold rebuild
# --------------------------------------------------------------------------- #


def test_cold_rebuild_scale_ratio(tmp_path):
    """Cold rebuild t(2k)/t(500) must stay under the ceiling (A3ii/ATK-DOS-04)."""
    ceiling = _perf_scale()["cold_rebuild_2k_over_500"]
    t500 = _rebuild_time(tmp_path, 500)
    t2k = _rebuild_time(tmp_path, 2000)
    _assert_ratio_under(
        t2k / max(t500, 1e-6),
        ceiling,
        "cold rebuild t(2k)/t(500)",
        f"(t500={t500 * 1e3:.0f}ms t2k={t2k * 1e3:.0f}ms)",
    )


# --------------------------------------------------------------------------- #
# A4 — L2 eviction
# --------------------------------------------------------------------------- #


def test_l2_eviction_scale_ratio():
    """Per-eviction cost must stay ~flat as the cache grows 8× (A4, O(1) not O(N))."""
    ceiling = _perf_scale()["l2_evict_ratio"]
    small = _min_of(lambda: _per_eviction_seconds(500, 2000), trials=5)
    large = _min_of(lambda: _per_eviction_seconds(4000, 2000), trials=5)
    _assert_ratio_under(
        large / max(small, 1e-9),
        ceiling,
        "L2 per-eviction 500→4000",
        f"(small={small * 1e6:.2f}µs large={large * 1e6:.2f}µs)",
    )
