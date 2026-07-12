#!/usr/bin/env python3
"""
Batch File Reader Utility
Efficiently reads multiple files with different strategies
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Literal
import json

Strategy = Literal["full", "summary", "search"]


class BatchFileReader:
    """Reads multiple files efficiently with different strategies"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
    
    def read_files(
        self,
        file_paths: List[str],
        strategy: Strategy = "full",
        search_pattern: Optional[str] = None,
        max_lines_per_file: int = 1000
    ) -> Dict[str, any]:
        """
        Read multiple files with specified strategy
        
        Args:
            file_paths: List of file paths to read
            strategy: Reading strategy (full, summary, search)
            search_pattern: Pattern to search for (only for search strategy)
            max_lines_per_file: Maximum lines to read per file
            
        Returns:
            Dictionary with file paths as keys and content/analysis as values
        """
        results = {}
        
        for file_path in file_paths:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                results[file_path] = {"error": "File not found"}
                continue
            
            try:
                if strategy == "full":
                    results[file_path] = self._read_full(full_path, max_lines_per_file)
                elif strategy == "summary":
                    results[file_path] = self._read_summary(full_path)
                elif strategy == "search":
                    results[file_path] = self._read_search(full_path, search_pattern)
                else:
                    results[file_path] = {"error": f"Unknown strategy: {strategy}"}
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def _read_full(self, file_path: Path, max_lines: int) -> Dict:
        """Read full file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            truncated = total_lines > max_lines
            
            return {
                "strategy": "full",
                "content": "".join(lines[:max_lines]),
                "total_lines": total_lines,
                "truncated": truncated,
                "lines_read": min(total_lines, max_lines)
            }
        except UnicodeDecodeError:
            return {
                "strategy": "full",
                "error": "Binary file or encoding issue",
                "is_binary": True
            }
    
    def _read_summary(self, file_path: Path) -> Dict:
        """Read file structure summary (imports, classes, functions)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            summary = {
                "strategy": "summary",
                "file_type": file_path.suffix,
                "size_bytes": len(content),
                "line_count": content.count('\n') + 1
            }
            
            # Language-specific parsing
            if file_path.suffix == '.py':
                summary.update(self._parse_python_summary(content))
            elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                summary.update(self._parse_javascript_summary(content))
            elif file_path.suffix in ['.go']:
                summary.update(self._parse_go_summary(content))
            else:
                summary["note"] = "Generic summary only"
            
            return summary
            
        except Exception as e:
            return {
                "strategy": "summary",
                "error": str(e)
            }
    
    def _parse_python_summary(self, content: str) -> Dict:
        """Parse Python file for structure"""
        lines = content.split('\n')
        
        imports = []
        classes = []
        functions = []
        
        for line in lines:
            stripped = line.strip()
            
            # Imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
            
            # Classes
            elif stripped.startswith('class '):
                class_name = stripped.split('(')[0].replace('class ', '').strip(':')
                classes.append(class_name)
            
            # Functions
            elif stripped.startswith('def '):
                func_name = stripped.split('(')[0].replace('def ', '')
                functions.append(func_name)
        
        return {
            "language": "python",
            "imports": imports[:20],  # Limit to first 20
            "classes": classes,
            "functions": functions[:50],  # Limit to first 50
            "import_count": len(imports),
            "class_count": len(classes),
            "function_count": len(functions)
        }
    
    def _parse_javascript_summary(self, content: str) -> Dict:
        """Parse JavaScript/TypeScript file for structure"""
        lines = content.split('\n')
        
        imports = []
        exports = []
        functions = []
        classes = []
        
        for line in lines:
            stripped = line.strip()
            
            # Imports
            if stripped.startswith('import '):
                imports.append(stripped)
            
            # Exports
            elif stripped.startswith('export '):
                exports.append(stripped[:80])  # Truncate long exports
            
            # Functions
            elif 'function ' in stripped or '=>' in stripped:
                functions.append(stripped[:80])
            
            # Classes
            elif stripped.startswith('class '):
                class_name = stripped.split('{')[0].replace('class ', '').strip()
                classes.append(class_name)
        
        return {
            "language": "javascript/typescript",
            "imports": imports[:20],
            "exports": exports[:20],
            "functions": functions[:30],
            "classes": classes,
            "import_count": len(imports),
            "export_count": len(exports),
            "function_count": len(functions),
            "class_count": len(classes)
        }
    
    def _parse_go_summary(self, content: str) -> Dict:
        """Parse Go file for structure"""
        lines = content.split('\n')
        
        imports = []
        functions = []
        types = []
        
        in_import_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # Import blocks
            if stripped.startswith('import ('):
                in_import_block = True
                continue
            elif in_import_block:
                if stripped == ')':
                    in_import_block = False
                elif stripped:
                    imports.append(stripped)
                continue
            
            # Single imports
            if stripped.startswith('import '):
                imports.append(stripped)
            
            # Functions
            elif stripped.startswith('func '):
                func_name = stripped.split('(')[0].replace('func ', '')
                functions.append(func_name)
            
            # Types
            elif stripped.startswith('type '):
                type_name = stripped.split(' ')[1]
                types.append(type_name)
        
        return {
            "language": "go",
            "imports": imports[:20],
            "functions": functions[:50],
            "types": types[:30],
            "import_count": len(imports),
            "function_count": len(functions),
            "type_count": len(types)
        }
    
    def _read_search(self, file_path: Path, pattern: Optional[str]) -> Dict:
        """Search for pattern in file"""
        if not pattern:
            return {
                "strategy": "search",
                "error": "No search pattern provided"
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            matches = []
            for line_num, line in enumerate(lines, 1):
                if pattern.lower() in line.lower():
                    matches.append({
                        "line_number": line_num,
                        "content": line.strip(),
                        "context_before": lines[max(0, line_num-2):line_num-1] if line_num > 1 else [],
                        "context_after": lines[line_num:min(len(lines), line_num+2)]
                    })
            
            return {
                "strategy": "search",
                "pattern": pattern,
                "match_count": len(matches),
                "matches": matches[:50],  # Limit to first 50 matches
                "total_lines": len(lines)
            }
            
        except Exception as e:
            return {
                "strategy": "search",
                "error": str(e)
            }


def main():
    """CLI interface for batch file reader"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch File Reader Utility")
    parser.add_argument("files", nargs="+", help="Files to read")
    parser.add_argument(
        "--strategy",
        choices=["full", "summary", "search"],
        default="full",
        help="Reading strategy"
    )
    parser.add_argument("--search", help="Search pattern (for search strategy)")
    parser.add_argument("--max-lines", type=int, default=1000, help="Max lines per file")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    reader = BatchFileReader()
    results = reader.read_files(
        args.files,
        strategy=args.strategy,
        search_pattern=args.search,
        max_lines_per_file=args.max_lines
    )
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        for file_path, result in results.items():
            print(f"\n{'='*80}")
            print(f"File: {file_path}")
            print('='*80)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            if result["strategy"] == "full":
                print(f"Lines: {result['lines_read']}/{result['total_lines']}")
                if result.get("truncated"):
                    print("(truncated)")
                print("\nContent:")
                print(result["content"])
            
            elif result["strategy"] == "summary":
                print(f"Type: {result.get('file_type', 'unknown')}")
                print(f"Size: {result.get('size_bytes', 0)} bytes")
                print(f"Lines: {result.get('line_count', 0)}")
                
                if "language" in result:
                    print(f"\nLanguage: {result['language']}")
                    print(f"Imports: {result.get('import_count', 0)}")
                    print(f"Classes: {result.get('class_count', 0)}")
                    print(f"Functions: {result.get('function_count', 0)}")
            
            elif result["strategy"] == "search":
                print(f"Pattern: {result['pattern']}")
                print(f"Matches: {result['match_count']}")
                
                for match in result.get("matches", [])[:10]:
                    print(f"\nLine {match['line_number']}: {match['content']}")


if __name__ == "__main__":
    main()
