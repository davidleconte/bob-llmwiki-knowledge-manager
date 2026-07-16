#!/usr/bin/env python3
"""
Component Analyzer Utility
Analyzes code components with specialized strategies
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Literal

from src.tools.safe_paths import resolve_within

AnalysisType = Literal["security", "performance", "quality", "architecture", "comprehensive"]
Depth = Literal["shallow", "deep"]


class ComponentAnalyzer:
    """Analyzes code components with different strategies"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()

    def analyze_component(
        self,
        component_path: str,
        analysis_type: AnalysisType = "comprehensive",
        depth: Depth = "shallow",
    ) -> Dict:
        """
        Analyze a component (file or directory)

        Args:
            component_path: Path to component (file or directory)
            analysis_type: Type of analysis to perform
            depth: Analysis depth (shallow or deep)

        Returns:
            Dictionary with analysis results
        """
        try:
            full_path = resolve_within(self.base_path, component_path)
        except ValueError:
            return {"error": f"Invalid component path (escapes base): {component_path}"}

        # Check type: is_dir() returns False (not raises) for missing paths, so
        # fall through to is_file() to distinguish "not a directory" from
        # "does not exist". Collapses the old exists()→is_dir() two-call pattern
        # into a single is_dir()+is_file() pair, narrowing the TOCTOU window.
        is_directory = full_path.is_dir()
        if not is_directory and not full_path.is_file():
            return {"error": f"Component not found: {component_path}"}

        result = {
            "component": component_path,
            "type": "directory" if is_directory else "file",
            "analysis_type": analysis_type,
            "depth": depth,
        }

        try:
            if is_directory:
                result.update(self._analyze_directory(full_path, analysis_type, depth))
            else:
                result.update(self._analyze_file(full_path, analysis_type, depth))
        except Exception as e:
            result["error"] = str(e)

        return result

    def _contained_files(self, files: List[Path]) -> List[Path]:
        """Drop any discovered leaf whose resolved target escapes ``base_path``.

        ``rglob`` follows symlinks, so a symlink planted inside an allowed
        directory can point outside the base and be read -- the entry path is
        validated in ``analyze_component`` but its rglob'd contents were not,
        leaking out-of-base file content into the analysis output. Re-validating
        every leaf through ``resolve_within`` (which follows symlinks and rejects
        escapes) applies the same containment to discovered files as to the entry
        path. ``BatchFileReader`` already re-checks per file; this mirrors it.
        """
        contained: List[Path] = []
        for f in files:
            try:
                resolve_within(self.base_path, str(f))
            except ValueError:
                continue
            contained.append(f)
        return contained

    def _analyze_directory(self, dir_path: Path, analysis_type: AnalysisType, depth: Depth) -> Dict:
        """Analyze a directory component"""
        files = self._contained_files(
            list(dir_path.rglob("*.py"))
            + list(dir_path.rglob("*.js"))
            + list(dir_path.rglob("*.ts"))
            + list(dir_path.rglob("*.go"))
        )

        result = {
            "file_count": len(files),
            "files": [str(f.relative_to(self.base_path)) for f in files[:50]],
        }

        if analysis_type in ["security", "comprehensive"]:
            result["security"] = self._analyze_security_directory(files, depth)

        if analysis_type in ["performance", "comprehensive"]:
            result["performance"] = self._analyze_performance_directory(files, depth)

        if analysis_type in ["quality", "comprehensive"]:
            result["quality"] = self._analyze_quality_directory(files, depth)

        if analysis_type in ["architecture", "comprehensive"]:
            result["architecture"] = self._analyze_architecture_directory(dir_path, files, depth)

        return result

    def _analyze_file(self, file_path: Path, analysis_type: AnalysisType, depth: Depth) -> Dict:
        """Analyze a single file component"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return {"error": "Binary file or encoding issue"}

        result = {
            "size_bytes": len(content),
            "line_count": content.count("\n") + 1,
            "language": self._detect_language(file_path),
        }

        if analysis_type in ["security", "comprehensive"]:
            result["security"] = self._analyze_security_file(content, file_path, depth)

        if analysis_type in ["performance", "comprehensive"]:
            result["performance"] = self._analyze_performance_file(content, file_path, depth)

        if analysis_type in ["quality", "comprehensive"]:
            result["quality"] = self._analyze_quality_file(content, file_path, depth)

        if analysis_type in ["architecture", "comprehensive"]:
            result["architecture"] = self._analyze_architecture_file(content, file_path, depth)

        return result

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c/cpp",
        }
        return ext_map.get(file_path.suffix, "unknown")

    # Security Analysis

    def _analyze_security_directory(self, files: List[Path], depth: Depth) -> Dict:
        """Analyze security for directory"""
        issues = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_issues = self._find_security_issues(content, file_path)
                if file_issues:
                    issues.extend(file_issues)
            except Exception:
                continue

        return {
            "total_issues": len(issues),
            "critical": len([i for i in issues if i["severity"] == "critical"]),
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"]),
            "issues": issues[:20] if depth == "deep" else issues[:5],
        }

    def _analyze_security_file(self, content: str, file_path: Path, depth: Depth) -> Dict:
        """Analyze security for single file"""
        issues = self._find_security_issues(content, file_path)

        return {
            "total_issues": len(issues),
            "critical": len([i for i in issues if i["severity"] == "critical"]),
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"]),
            "issues": issues if depth == "deep" else issues[:10],
        }

    def _find_security_issues(self, content: str, file_path: Path) -> List[Dict]:
        """Find security issues in code"""
        issues = []
        lines = content.split("\n")

        # Security patterns to check
        patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password", "critical"),
            (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded API key", "critical"),
            (r'secret\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded secret", "critical"),
            (r"eval\s*\(", "Use of eval()", "high"),
            (r"exec\s*\(", "Use of exec()", "high"),
            (r"pickle\.loads?\(", "Unsafe pickle usage", "high"),
            (r"subprocess\.call\([^)]*shell\s*=\s*True", "Shell injection risk", "high"),
            (r"os\.system\(", "OS command execution", "medium"),
            (r"\.innerHTML\s*=", "XSS vulnerability risk", "medium"),
            (r"dangerouslySetInnerHTML", "XSS vulnerability risk", "medium"),
            (r"SELECT.*FROM.*WHERE.*\+", "SQL injection risk", "high"),
            (r"md5\(", "Weak hash algorithm", "medium"),
            (r"sha1\(", "Weak hash algorithm", "medium"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        {
                            "file": str(file_path.name),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code": line.strip()[:100],
                        }
                    )

        return issues

    # Performance Analysis

    def _analyze_performance_directory(self, files: List[Path], depth: Depth) -> Dict:
        """Analyze performance for directory"""
        issues = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_issues = self._find_performance_issues(content, file_path)
                if file_issues:
                    issues.extend(file_issues)
            except Exception:
                continue

        return {
            "total_issues": len(issues),
            "issues": issues[:20] if depth == "deep" else issues[:5],
        }

    def _analyze_performance_file(self, content: str, file_path: Path, depth: Depth) -> Dict:
        """Analyze performance for single file"""
        issues = self._find_performance_issues(content, file_path)

        return {"total_issues": len(issues), "issues": issues if depth == "deep" else issues[:10]}

    def _find_performance_issues(self, content: str, file_path: Path) -> List[Dict]:
        """Find performance issues in code"""
        issues = []
        lines = content.split("\n")

        # Performance patterns
        patterns = [
            (r"for\s+\w+\s+in.*:\s*for\s+\w+\s+in", "Nested loops (O(n²))", "medium"),
            (r"\.append\(.*\)\s*for\s+", "List append in loop", "low"),
            (r"time\.sleep\(", "Blocking sleep", "medium"),
            (r"\.find\(.*\)\s*for\s+", "Repeated find in loop", "medium"),
            (r"SELECT \* FROM", "SELECT * query", "low"),
            (r"\.sort\(\).*for\s+", "Sort in loop", "medium"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        {
                            "file": str(file_path.name),
                            "line": line_num,
                            "severity": severity,
                            "description": description,
                            "code": line.strip()[:100],
                        }
                    )

        return issues

    # Quality Analysis

    def _analyze_quality_directory(self, files: List[Path], depth: Depth) -> Dict:
        """Analyze code quality for directory"""
        total_lines = 0
        total_functions = 0
        long_functions = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                total_lines += content.count("\n") + 1

                # Count functions and check length
                func_analysis = self._analyze_functions(content, file_path)
                total_functions += func_analysis["count"]
                long_functions.extend(func_analysis["long_functions"])
            except Exception:
                continue

        return {
            "total_lines": total_lines,
            "total_functions": total_functions,
            "long_functions": len(long_functions),
            "long_function_details": long_functions[:10] if depth == "deep" else long_functions[:3],
        }

    def _analyze_quality_file(self, content: str, file_path: Path, depth: Depth) -> Dict:
        """Analyze code quality for single file"""
        lines = content.split("\n")
        func_analysis = self._analyze_functions(content, file_path)

        return {
            "line_count": len(lines),
            "function_count": func_analysis["count"],
            "long_functions": len(func_analysis["long_functions"]),
            "long_function_details": func_analysis["long_functions"]
            if depth == "deep"
            else func_analysis["long_functions"][:5],
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
        }

    def _analyze_functions(self, content: str, file_path: Path) -> Dict:
        """Analyze functions in code"""
        lines = content.split("\n")
        functions = []
        current_func = None
        indent_level = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detect function start (Python)
            if stripped.startswith("def "):
                if current_func:
                    functions.append(current_func)

                func_name = stripped.split("(")[0].replace("def ", "")
                current_func = {"name": func_name, "start_line": line_num, "lines": 1}
                indent_level = len(line) - len(line.lstrip())

            # Count lines in current function
            elif current_func:
                current_indent = len(line) - len(line.lstrip())
                if stripped and current_indent <= indent_level and not stripped.startswith("#"):
                    functions.append(current_func)
                    current_func = None
                else:
                    current_func["lines"] += 1

        if current_func:
            functions.append(current_func)

        long_functions = [f for f in functions if f["lines"] > 50]

        return {"count": len(functions), "long_functions": long_functions}

    # Architecture Analysis

    def _analyze_architecture_directory(
        self, dir_path: Path, files: List[Path], depth: Depth
    ) -> Dict:
        """Analyze architecture for directory"""
        imports = set()
        dependencies = {}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_imports = self._extract_imports(content, file_path)
                imports.update(file_imports)

                rel_path = str(file_path.relative_to(self.base_path))
                dependencies[rel_path] = file_imports
            except Exception:
                continue

        return {
            "total_files": len(files),
            "unique_imports": len(imports),
            "imports": sorted(list(imports))[:50]
            if depth == "deep"
            else sorted(list(imports))[:10],
            "dependencies": dependencies if depth == "deep" else {},
        }

    def _analyze_architecture_file(self, content: str, file_path: Path, depth: Depth) -> Dict:
        """Analyze architecture for single file"""
        imports = self._extract_imports(content, file_path)

        return {"imports": sorted(list(imports)), "import_count": len(imports)}

    def _extract_imports(self, content: str, file_path: Path) -> set:
        """Extract imports from code"""
        imports = set()
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()

            # Python imports
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.add(stripped.split("#")[0].strip())

            # JavaScript/TypeScript imports
            elif stripped.startswith("import ") or stripped.startswith("require("):
                imports.add(stripped.split("//")[0].strip())

        return imports


def main():
    """CLI interface for component analyzer"""
    import argparse

    parser = argparse.ArgumentParser(description="Component Analyzer Utility")
    parser.add_argument("component", help="Component path to analyze")
    parser.add_argument(
        "--type",
        choices=["security", "performance", "quality", "architecture", "comprehensive"],
        default="comprehensive",
        help="Analysis type",
    )
    parser.add_argument(
        "--depth", choices=["shallow", "deep"], default="shallow", help="Analysis depth"
    )
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    analyzer = ComponentAnalyzer()
    result = analyzer.analyze_component(args.component, analysis_type=args.type, depth=args.depth)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        # Error dicts (missing component, path-escape) carry only "error" -- check
        # for it before printing the header, which reads component/type/etc.
        if "error" in result:
            print(f"\nError: {result['error']}")
            return

        print(f"\n{'=' * 80}")
        print(f"Component Analysis: {result['component']}")
        print(
            f"Type: {result['type']} | Analysis: {result['analysis_type']} | Depth: {result['depth']}"
        )
        print("=" * 80)

        # Print security results
        if "security" in result:
            sec = result["security"]
            print("\n🔒 Security Analysis:")
            print(f"  Total Issues: {sec['total_issues']}")
            print(
                f"  Critical: {sec['critical']} | High: {sec['high']} | Medium: {sec['medium']} | Low: {sec['low']}"
            )

            if sec.get("issues"):
                print("\n  Top Issues:")
                for issue in sec["issues"][:5]:
                    print(f"    [{issue['severity'].upper()}] {issue['description']}")
                    print(f"      {issue['file']}:{issue['line']}")

        # Print performance results
        if "performance" in result:
            perf = result["performance"]
            print("\n⚡ Performance Analysis:")
            print(f"  Total Issues: {perf['total_issues']}")

            if perf.get("issues"):
                print("\n  Top Issues:")
                for issue in perf["issues"][:5]:
                    print(f"    [{issue['severity'].upper()}] {issue['description']}")
                    print(f"      {issue['file']}:{issue['line']}")

        # Print quality results
        if "quality" in result:
            qual = result["quality"]
            print("\n📊 Quality Analysis:")
            if "total_lines" in qual:
                print(f"  Total Lines: {qual['total_lines']}")
                print(f"  Total Functions: {qual['total_functions']}")
            else:
                print(f"  Lines: {qual['line_count']}")
                print(f"  Functions: {qual['function_count']}")
            print(f"  Long Functions (>50 lines): {qual['long_functions']}")

        # Print architecture results
        if "architecture" in result:
            arch = result["architecture"]
            print("\n🏗️  Architecture Analysis:")
            if "total_files" in arch:
                print(f"  Total Files: {arch['total_files']}")
            print(f"  Unique Imports: {arch.get('unique_imports', arch.get('import_count', 0))}")


if __name__ == "__main__":
    main()
