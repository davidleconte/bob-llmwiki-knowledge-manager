#!/usr/bin/env python3
"""CLI entry point for the code-component analyzer.

The implementation lives in ``src/tools/component_analyzer.py`` (library layer)
so that ``src/`` code can import it without an upward ``src/ -> scripts/``
dependency. This thin wrapper preserves the documented
``python3 scripts/utils/component_analyzer.py ...`` invocation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.component_analyzer import main  # noqa: E402

if __name__ == "__main__":
    main()
