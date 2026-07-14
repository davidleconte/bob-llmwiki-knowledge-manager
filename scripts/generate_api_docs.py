#!/usr/bin/env python3
"""
Generate API documentation from Python source code.

Extracts docstrings and type hints from modules to create
comprehensive API reference documentation.
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class APIDocGenerator:
    """Generate API documentation from Python source code."""

    def __init__(self, src_dir: Path, output_dir: Path):
        """
        Initialize API doc generator.

        Args:
            src_dir: Source code directory
            output_dir: Output directory for documentation
        """
        self.src_dir = src_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_module_info(self, module_path: Path) -> Dict[str, Any]:
        """
        Extract information from a Python module.

        Args:
            module_path: Path to Python module

        Returns:
            Dictionary containing module information
        """
        with open(module_path, "r") as f:
            source = f.read()

        tree = ast.parse(source)

        module_info = {
            "name": module_path.stem,
            "path": str(module_path.relative_to(self.src_dir)),
            "docstring": ast.get_docstring(tree),
            "classes": [],
            "functions": [],
            "constants": [],
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self.extract_class_info(node)
                module_info["classes"].append(class_info)
            elif isinstance(node, ast.FunctionDef) and not self.is_method(node, tree):
                func_info = self.extract_function_info(node)
                module_info["functions"].append(func_info)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        module_info["constants"].append(target.id)

        return module_info

    def is_method(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if function is a class method."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False

    def extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition."""
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "bases": [self.get_name(base) for base in node.bases],
            "methods": [],
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.extract_function_info(item)
                class_info["methods"].append(method_info)

        return class_info

    def extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from a function definition."""
        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "args": [],
            "returns": None,
        }

        # Extract arguments
        for arg in node.args.args:
            arg_info = {"name": arg.arg, "annotation": self.get_annotation(arg.annotation)}
            func_info["args"].append(arg_info)

        # Extract return type
        if node.returns:
            func_info["returns"] = self.get_annotation(node.returns)

        return func_info

    def get_name(self, node: ast.expr) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_name(node.value)}.{node.attr}"
        return str(node)

    def get_annotation(self, node: Optional[ast.expr]) -> Optional[str]:
        """Get type annotation as string."""
        if node is None:
            return None
        return ast.unparse(node)

    def generate_module_doc(self, module_info: Dict[str, Any]) -> str:
        """Generate markdown documentation for a module."""
        lines = []

        # Module header
        lines.append(f"# {module_info['name']}")
        lines.append("")

        if module_info["docstring"]:
            lines.append(module_info["docstring"])
            lines.append("")

        # Constants
        if module_info["constants"]:
            lines.append("## Constants")
            lines.append("")
            for const in module_info["constants"]:
                lines.append(f"- `{const}`")
            lines.append("")

        # Functions
        if module_info["functions"]:
            lines.append("## Functions")
            lines.append("")
            for func in module_info["functions"]:
                lines.extend(self.format_function(func))
                lines.append("")

        # Classes
        if module_info["classes"]:
            lines.append("## Classes")
            lines.append("")
            for cls in module_info["classes"]:
                lines.extend(self.format_class(cls))
                lines.append("")

        return "\n".join(lines)

    def format_function(self, func: Dict[str, Any]) -> List[str]:
        """Format function documentation."""
        lines = []

        # Function signature
        args_str = ", ".join(
            [
                f"{arg['name']}: {arg['annotation']}" if arg["annotation"] else arg["name"]
                for arg in func["args"]
            ]
        )
        returns_str = f" -> {func['returns']}" if func["returns"] else ""

        lines.append(f"### `{func['name']}({args_str}){returns_str}`")
        lines.append("")

        if func["docstring"]:
            lines.append(func["docstring"])
            lines.append("")

        return lines

    def format_class(self, cls: Dict[str, Any]) -> List[str]:
        """Format class documentation."""
        lines = []

        # Class header
        bases_str = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
        lines.append(f"### `{cls['name']}{bases_str}`")
        lines.append("")

        if cls["docstring"]:
            lines.append(cls["docstring"])
            lines.append("")

        # Methods
        if cls["methods"]:
            lines.append("#### Methods")
            lines.append("")
            for method in cls["methods"]:
                if method["name"].startswith("_") and method["name"] != "__init__":
                    continue  # Skip private methods
                lines.extend(self.format_method(method))
                lines.append("")

        return lines

    def format_method(self, method: Dict[str, Any]) -> List[str]:
        """Format method documentation."""
        lines = []

        # Method signature
        args_str = ", ".join(
            [
                f"{arg['name']}: {arg['annotation']}" if arg["annotation"] else arg["name"]
                for arg in method["args"]
                if arg["name"] != "self"
            ]
        )
        returns_str = f" -> {method['returns']}" if method["returns"] else ""

        lines.append(f"##### `{method['name']}({args_str}){returns_str}`")
        lines.append("")

        if method["docstring"]:
            # Indent docstring
            for line in method["docstring"].split("\n"):
                lines.append(line)
            lines.append("")

        return lines

    def build_all(self) -> Dict[str, str]:
        """Build every output doc in memory: ``{relative_output_path: content}``.

        The single source for both writing (:meth:`generate_docs`) and the
        freshness check (:meth:`check_docs`), so the two can never disagree.
        Output is deterministic (modules and packages sorted; per-module content
        is AST-derived), which is what makes ``--check`` a stable CI gate.
        """
        modules = [
            py
            for py in self.src_dir.rglob("*.py")
            if py.name != "__init__.py" and "__pycache__" not in str(py)
        ]

        module_index: Dict[str, List[Dict[str, str]]] = {}
        outputs: Dict[str, str] = {}
        for module_path in sorted(modules):
            try:
                module_info = self.extract_module_info(module_path)
            except Exception as e:  # pragma: no cover - defensive, per-module
                print(f"Error processing {module_path}: {e}", file=sys.stderr)
                continue
            rel_path = module_path.relative_to(self.src_dir)
            # Hierarchical package = the module's parent dir under src/ ("root"
            # for top-level modules). Preserves nesting (e.g. delegation/agents)
            # and avoids the empty-package -> absolute-path bug for top-level
            # modules like src/facade.py.
            parent = rel_path.parent
            package = "root" if parent == Path(".") else str(parent)
            module_index.setdefault(package, []).append(
                {"name": module_info["name"], "path": str(rel_path)}
            )
            outputs[f"{package}/{module_info['name']}.md"] = self.generate_module_doc(module_info)

        outputs["README.md"] = self._index_content(module_index)
        return outputs

    def _index_content(self, module_index: Dict[str, List[Dict[str, str]]]) -> str:
        """Render the API index (README.md) from the per-package module list."""
        lines = [
            "# API Reference",
            "",
            "Complete API reference for the Token Optimization System.",
            "",
            "> Generated from source docstrings by `scripts/generate_api_docs.py`.",
            "> Do not edit by hand — run the generator and commit. CI (`docs-freshness`)",
            "> fails if this tree drifts from `src/` via `generate_api_docs.py --check`.",
            "",
        ]
        for package in sorted(module_index.keys()):
            lines.append(f"## {package.title()}")
            lines.append("")
            for doc in sorted(module_index[package], key=lambda x: x["name"]):
                lines.append(f"- [{doc['name']}]({package}/{doc['name']}.md) - `{doc['path']}`")
            lines.append("")
        return "\n".join(lines)

    def generate_docs(self) -> None:
        """Write every generated doc under ``output_dir``."""
        for rel, content in self.build_all().items():
            out = self.output_dir / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
            print(f"Generated: {out}")

    def check_docs(self) -> int:
        """Compare committed docs against a fresh build; non-zero on any drift.

        Detects three kinds of drift: a committed page whose content no longer
        matches the source (STALE), a source module with no committed page
        (MISSING), and a committed page with no corresponding source module
        (ORPHAN). This is the drift-resistant API-doc pattern, enforced.
        """
        expected = self.build_all()
        problems: List[str] = []

        for rel, content in sorted(expected.items()):
            path = self.output_dir / rel
            if not path.exists():
                problems.append(f"MISSING: docs/api/{rel} (module added; regenerate)")
            elif path.read_text(encoding="utf-8") != content:
                problems.append(
                    f"STALE:   docs/api/{rel} (docstring/signature changed; regenerate)"
                )

        expected_paths = {(self.output_dir / rel).resolve() for rel in expected}
        for existing in self.output_dir.rglob("*.md"):
            if existing.resolve() not in expected_paths:
                rel = existing.relative_to(self.output_dir)
                problems.append(f"ORPHAN:  docs/api/{rel} (module removed; delete the stale doc)")

        if problems:
            print("API docs are out of date vs src/ docstrings:\n", file=sys.stderr)
            for problem in sorted(problems):
                print(f"  {problem}", file=sys.stderr)
            print(
                "\nRun `python scripts/generate_api_docs.py` and commit docs/api/.",
                file=sys.stderr,
            )
            return 1
        print(f"API docs are in sync with src/ ({len(expected)} files).")
        return 0


def _selftest() -> int:
    """Verify ``--check`` detects STALE / MISSING / ORPHAN drift.

    Runs entirely inside a temp directory (no side effects on the real
    ``docs/api/`` -- the bug this replaces was ``--selftest`` silently running the
    real generator and rewriting committed docs).
    """
    import contextlib
    import io
    import tempfile

    failures: list[str] = []
    buf = io.StringIO()
    with (
        tempfile.TemporaryDirectory() as d,
        contextlib.redirect_stdout(buf),
        contextlib.redirect_stderr(buf),
    ):
        root = Path(d)
        src = root / "src"
        src.mkdir()
        (src / "__init__.py").write_text('"""Temp package for selftest."""\n', encoding="utf-8")
        (src / "mod.py").write_text(
            '"""A module.\n\nWith a docstring."""\n\n\ndef greet(name):\n'
            '    """Return a greeting."""\n    return name\n',
            encoding="utf-8",
        )
        out = root / "api"
        APIDocGenerator(src, out).generate_docs()
        docs = sorted(out.rglob("*.md"))
        if not docs:
            failures.append("generator produced no docs")
        else:
            # in sync
            if APIDocGenerator(src, out).check_docs() != 0:
                failures.append("fresh docs should be in sync (0)")
            # STALE: a committed page drifted from source
            docs[0].write_text(
                docs[0].read_text(encoding="utf-8") + "\n<!--x-->\n", encoding="utf-8"
            )
            if APIDocGenerator(src, out).check_docs() != 1:
                failures.append("edited page should be STALE (1)")
            # MISSING: a source page with no committed doc
            APIDocGenerator(src, out).generate_docs()
            docs[0].unlink()
            if APIDocGenerator(src, out).check_docs() != 1:
                failures.append("deleted page should be MISSING (1)")
            # ORPHAN: a committed doc with no source
            APIDocGenerator(src, out).generate_docs()
            (out / "orphan_ghost.md").write_text("no source\n", encoding="utf-8")
            if APIDocGenerator(src, out).check_docs() != 1:
                failures.append("orphan doc should fail (1)")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("SELFTEST OK: --check detects STALE / MISSING / ORPHAN drift.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Generate the API docs, or (with ``--check``) verify they are current."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    check = "--check" in argv

    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"
    output_dir = project_root / "docs" / "api"

    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}", file=sys.stderr)
        return 2

    generator = APIDocGenerator(src_dir, output_dir)
    if check:
        return generator.check_docs()

    print("Generating API documentation...")
    print(f"Source: {src_dir}")
    print(f"Output: {output_dir}")
    print()
    generator.generate_docs()
    print()
    print("API documentation generated successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
