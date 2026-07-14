#!/usr/bin/env python3
"""Token-savings validation runner (Phase 5: real, manifest-backed).

HISTORICAL NOTE -- this script previously **fabricated** its headline: it
constructed a ``PromptOptimizer`` but never invoked it, and the
"68.96% / 95% CI / VALIDATED" figures were arithmetic between two hand-written
literal functions with ``std=0`` across 90 duplicates (institutional audit
A1-A3; see ``evaluation/VALIDATION_DISCLAIMER.md``).

It is now a thin shim over the real harness in :mod:`src.validation`, which
invokes the actual product over a real corpus and writes a reproducibility
manifest per run. This preserves the documented invocation
(``python evaluation/scripts/run_token_validation.py``); it is exactly
equivalent to::

    python -m src.validation

Pass ``--help`` for options (corpus tier, seed, output dir, ...). The retracted
``evaluation/results/validation_report.json`` is left untouched as a frozen
audit-trail record; real runs write to ``evaluation/results/validation-<date>/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# evaluation/scripts -> repo root, so `src` is importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.validation.__main__ import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
