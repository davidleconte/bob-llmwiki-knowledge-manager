#!/usr/bin/env python3
"""CLI entry point for the batch file reader.

The implementation lives in ``src/tools/batch_file_reader.py`` (library layer)
so that ``src/`` code can import it without an upward ``src/ -> scripts/``
dependency. This thin wrapper preserves the documented
``python3 scripts/utils/batch_file_reader.py ...`` invocation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.batch_file_reader import main  # noqa: E402

if __name__ == "__main__":
    main()
