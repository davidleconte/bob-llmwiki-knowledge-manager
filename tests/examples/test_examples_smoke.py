"""Smoke tests for the bundled ``examples/`` demo scripts.

Replaces the former ``tests/validation/*`` suite, which asserted a *fabricated*
API against these demo scripts — wrong constructor kwargs
(``baseline_sessions=``, ``output_dir=``), methods that never existed
(``.load``, ``.get_summary``, ``calculate_basic_stats``), an undefined
``SessionAnalyzer`` class, and a literal ``BobShellBobShellSessionTracker``
typo. Those tests exercised ``examples/`` — never ``src/`` — so they contributed
nothing to src coverage and were deleted in the Phase 2 triage.

This lightweight replacement still catches *real* breakage of the demo scripts
(syntax errors, bad imports, API drift) by importing every example module. All
example scripts guard execution under ``if __name__ == "__main__"``, so import
runs only their top-level definitions, not the demos. A module that ``sys.exit``s
because an *optional* dependency (e.g. matplotlib) is absent is skipped, not
failed — so this suite is green on a minimal install and gives real coverage on
a full one.
"""
import importlib
from pathlib import Path

import pytest

_EXAMPLES_DIR = Path(__file__).resolve().parents[1].parent / "examples"
_EXAMPLE_MODULES = sorted(
    p.stem for p in _EXAMPLES_DIR.glob("*.py") if not p.stem.startswith("_")
)


def test_examples_dir_discovered():
    """Guard: the parametrization actually found the example scripts."""
    assert _EXAMPLE_MODULES, f"no example modules found under {_EXAMPLES_DIR}"


@pytest.mark.parametrize("module_name", _EXAMPLE_MODULES)
def test_example_module_imports(module_name):
    """Every example script imports cleanly (or skips if an optional dep is missing)."""
    try:
        importlib.import_module(f"examples.{module_name}")
    except SystemExit as exc:
        # e.g. examples/visualization.py calls sys.exit(1) when matplotlib is absent.
        pytest.skip(
            f"examples/{module_name}.py exited on import "
            f"(optional dependency missing): {exc}"
        )
