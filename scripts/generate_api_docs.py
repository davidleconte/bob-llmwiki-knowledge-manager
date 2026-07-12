#!/usr/bin/env python3
"""
Generate API documentation from Python source code.

Extracts docstrings and type hints from modules to create
comprehensive API reference documentation.
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys


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
        with open(module_path, 'r') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        module_info = {
            'name': module_path.stem,
            'path': str(module_path.relative_to(self.src_dir)),
            'docstring': ast.get_docstring(tree),
            'classes': [],
            'functions': [],
            'constants': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self.extract_class_info(node)
                module_info['classes'].append(class_info)
            elif isinstance(node, ast.FunctionDef) and not self.is_method(node, tree):
                func_info = self.extract_function_info(node)
                module_info['functions'].append(func_info)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        module_info['constants'].append(target.id)
        
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
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'bases': [self.get_name(base) for base in node.bases],
            'methods': []
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.extract_function_info(item)
                class_info['methods'].append(method_info)
        
        return class_info
    
    def extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from a function definition."""
        func_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': [],
            'returns': None
        }
        
        # Extract arguments
        for arg in node.args.args:
            arg_info = {
                'name': arg.arg,
                'annotation': self.get_annotation(arg.annotation)
            }
            func_info['args'].append(arg_info)
        
        # Extract return type
        if node.returns:
            func_info['returns'] = self.get_annotation(node.returns)
        
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
        
        if module_info['docstring']:
            lines.append(module_info['docstring'])
            lines.append("")
        
        # Constants
        if module_info['constants']:
            lines.append("## Constants")
            lines.append("")
            for const in module_info['constants']:
                lines.append(f"- `{const}`")
            lines.append("")
        
        # Functions
        if module_info['functions']:
            lines.append("## Functions")
            lines.append("")
            for func in module_info['functions']:
                lines.extend(self.format_function(func))
                lines.append("")
        
        # Classes
        if module_info['classes']:
            lines.append("## Classes")
            lines.append("")
            for cls in module_info['classes']:
                lines.extend(self.format_class(cls))
                lines.append("")
        
        return "\n".join(lines)
    
    def format_function(self, func: Dict[str, Any]) -> List[str]:
        """Format function documentation."""
        lines = []
        
        # Function signature
        args_str = ", ".join([
            f"{arg['name']}: {arg['annotation']}" if arg['annotation'] else arg['name']
            for arg in func['args']
        ])
        returns_str = f" -> {func['returns']}" if func['returns'] else ""
        
        lines.append(f"### `{func['name']}({args_str}){returns_str}`")
        lines.append("")
        
        if func['docstring']:
            lines.append(func['docstring'])
            lines.append("")
        
        return lines
    
    def format_class(self, cls: Dict[str, Any]) -> List[str]:
        """Format class documentation."""
        lines = []
        
        # Class header
        bases_str = f"({', '.join(cls['bases'])})" if cls['bases'] else ""
        lines.append(f"### `{cls['name']}{bases_str}`")
        lines.append("")
        
        if cls['docstring']:
            lines.append(cls['docstring'])
            lines.append("")
        
        # Methods
        if cls['methods']:
            lines.append("#### Methods")
            lines.append("")
            for method in cls['methods']:
                if method['name'].startswith('_') and method['name'] != '__init__':
                    continue  # Skip private methods
                lines.extend(self.format_method(method))
                lines.append("")
        
        return lines
    
    def format_method(self, method: Dict[str, Any]) -> List[str]:
        """Format method documentation."""
        lines = []
        
        # Method signature
        args_str = ", ".join([
            f"{arg['name']}: {arg['annotation']}" if arg['annotation'] else arg['name']
            for arg in method['args'] if arg['name'] != 'self'
        ])
        returns_str = f" -> {method['returns']}" if method['returns'] else ""
        
        lines.append(f"##### `{method['name']}({args_str}){returns_str}`")
        lines.append("")
        
        if method['docstring']:
            # Indent docstring
            for line in method['docstring'].split('\n'):
                lines.append(line)
            lines.append("")
        
        return lines
    
    def generate_docs(self):
        """Generate documentation for all modules."""
        # Find all Python modules
        modules = []
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if "__pycache__" in str(py_file):
                continue
            modules.append(py_file)
        
        # Generate docs for each module
        module_docs = {}
        for module_path in sorted(modules):
            try:
                module_info = self.extract_module_info(module_path)
                doc_content = self.generate_module_doc(module_info)
                
                # Organize by package
                rel_path = module_path.relative_to(self.src_dir)
                package = rel_path.parent.name if rel_path.parent.name != '.' else 'root'
                
                if package not in module_docs:
                    module_docs[package] = []
                
                module_docs[package].append({
                    'name': module_info['name'],
                    'content': doc_content,
                    'path': str(rel_path)
                })
            except Exception as e:
                print(f"Error processing {module_path}: {e}", file=sys.stderr)
        
        # Write package documentation
        for package, docs in module_docs.items():
            package_dir = self.output_dir / package
            package_dir.mkdir(parents=True, exist_ok=True)
            
            for doc in docs:
                output_file = package_dir / f"{doc['name']}.md"
                with open(output_file, 'w') as f:
                    f.write(doc['content'])
                print(f"Generated: {output_file}")
        
        # Generate index
        self.generate_index(module_docs)
    
    def generate_index(self, module_docs: Dict[str, List[Dict[str, Any]]]):
        """Generate API documentation index."""
        lines = []
        lines.append("# API Reference")
        lines.append("")
        lines.append("Complete API reference for the Token Optimization System.")
        lines.append("")
        
        for package in sorted(module_docs.keys()):
            lines.append(f"## {package.title()}")
            lines.append("")
            
            for doc in sorted(module_docs[package], key=lambda x: x['name']):
                lines.append(f"- [{doc['name']}]({package}/{doc['name']}.md) - `{doc['path']}`")
            
            lines.append("")
        
        index_file = self.output_dir / "README.md"
        with open(index_file, 'w') as f:
            f.write("\n".join(lines))
        
        print(f"Generated index: {index_file}")


def main():
    """Main entry point."""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    src_dir = project_root / "src"
    output_dir = project_root / "docs" / "api"
    
    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Generating API documentation...")
    print(f"Source: {src_dir}")
    print(f"Output: {output_dir}")
    print()
    
    generator = APIDocGenerator(src_dir, output_dir)
    generator.generate_docs()
    
    print()
    print("API documentation generated successfully!")


if __name__ == "__main__":
    main()
