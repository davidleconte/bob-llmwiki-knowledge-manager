#!/usr/bin/env python3
"""Enforce the src/ -> scripts/ layering rule: no library module may import from
the operational ``scripts/`` layer.

``src/`` is the reusable library; ``scripts/`` is the operational/CLI layer that
*consumes* the library. The dependency may only flow downward (scripts/ -> src/).
An upward ``src/ -> scripts/`` import (audit finding B3) couples the library to
throwaway tooling and forces ``sys.path`` hacks; it was removed in Phase 4 by
relocating the shared utilities into ``src/tools/``. This gate keeps it removed.

The check is AST-based (not a text grep) so it won't false-positive on the string
``"from scripts"`` in a docstring or comment.

Usage::

    python scripts/check_layering.py [src_dir]

Exits non-zero (and prints every violation as ``path:line``) if any ``src/``
module imports from ``scripts``.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# The forbidden top-level import root for anything under src/.
FORBIDDEN_ROOT = "scripts"


def _violations_in_file(path: Path) -> list[tuple[int, str]]:
    """Return (lineno, offending_module) for each import of ``scripts`` in ``path``."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:  # pragma: no cover - a syntax error is a louder failure elsewhere
        return [(exc.lineno or 0, f"<syntax error: {exc.msg}>")]

    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_ROOT or alias.name.startswith(FORBIDDEN_ROOT + "."):
                    found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            # module is None for `from . import x`; a relative import can never
            # reach scripts/ from inside src/, so only absolute imports matter.
            mod = node.module or ""
            if node.level == 0 and (mod == FORBIDDEN_ROOT or mod.startswith(FORBIDDEN_ROOT + ".")):
                found.append((node.lineno, mod))
    return found


def main(argv: list[str]) -> int:
    src_dir = Path(argv[1] if len(argv) > 1 else "src")
    if not src_dir.is_dir():
        print(f"ERROR: source directory not found: {src_dir}", file=sys.stderr)
        return 2

    violations: list[str] = []
    for py in sorted(src_dir.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        for lineno, mod in _violations_in_file(py):
            violations.append(f"{py}:{lineno}: imports '{mod}'")

    print(f"Layering gate: no src/ -> {FORBIDDEN_ROOT}/ imports")
    if violations:
        print(f"  FAIL: {len(violations)} upward import(s) found:", file=sys.stderr)
        for v in violations:
            print(f"    {v}", file=sys.stderr)
        print(
            "\nMove the shared code into src/ (e.g. src/tools/) and import it there;\n"
            "scripts/ may depend on src/, never the reverse.",
            file=sys.stderr,
        )
        return 1
    print("  OK: src/ has no upward dependency on scripts/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
