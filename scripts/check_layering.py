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


def _selftest() -> int:
    """Verify the AST detector flags upward imports and ignores look-alikes."""
    import tempfile

    cases: list[tuple[str, bool]] = [
        ("import scripts.foo\n", True),
        ("from scripts import foo\n", True),
        ("from scripts.sub import foo\n", True),
        ("import src.tools.foo\n", False),
        ("from src.cache import x\n", False),
        ("from . import sibling\n", False),  # relative import, never reaches scripts/
        ("x = 'from scripts import y'  # a string, not an import\n", False),  # AST-immune
        ("import scripts_helper\n", False),  # prefix look-alike, not the scripts package
    ]
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as d:
        for i, (source, should_flag) in enumerate(cases):
            p = Path(d) / f"case_{i}.py"
            p.write_text(source, encoding="utf-8")
            flagged = bool(_violations_in_file(p))
            if flagged != should_flag:
                failures.append(f"{source!r}: flagged={flagged}, expected={should_flag}")
    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: {len(cases)} layering cases classified correctly.")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
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
