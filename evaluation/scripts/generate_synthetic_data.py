#!/usr/bin/env python3
"""
Synthetic Data Generator for Token Savings Validation

Generates realistic repository structures and code patterns for testing
token optimization across all 4 phases.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class SyntheticDataGenerator:
    """Generates synthetic repositories and knowledge bases for testing."""
    
    def __init__(self, output_dir: str = "evaluation/data/synthetic"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Code patterns for different analysis types
        self.security_patterns = [
            'password = "hardcoded123"',
            'API_KEY = "sk-1234567890abcdef"',
            'query = f"SELECT * FROM users WHERE id = {user_id}"',  # SQL injection
            'html = f"<div>{user_input}</div>"',  # XSS
            'hashlib.md5(password.encode())',  # Weak crypto
        ]
        
        self.performance_patterns = [
            'for i in range(n):\n    for j in range(n):',  # O(n²)
            'for item in items:\n    db.query(item.id)',  # N+1
            'time.sleep(5)',  # Blocking
            'result = [x for x in range(1000000)]',  # Memory intensive
        ]
        
        self.quality_patterns = [
            'def long_function():\n' + '    pass\n' * 60,  # Long function
            'if a and b and c and d and e and f:',  # Complex condition
            'global_var = None',  # Global variable
        ]
    
    def generate_repository(self, size: str = "medium") -> Dict[str, Any]:
        """Generate a synthetic repository structure.
        
        Args:
            size: Repository size - "small", "medium", or "large"
            
        Returns:
            Dictionary with repository metadata and file contents
        """
        sizes = {
            "small": {"files": 20, "lines_per_file": 250, "components": 3},
            "medium": {"files": 50, "lines_per_file": 300, "components": 8},
            "large": {"files": 100, "lines_per_file": 350, "components": 15}
        }
        
        config = sizes[size]
        repo = {
            "metadata": {
                "size": size,
                "total_files": config["files"],
                "total_lines": config["files"] * config["lines_per_file"],
                "components": config["components"],
                "generated_at": datetime.now().isoformat()
            },
            "files": {},
            "issues": {
                "security": [],
                "performance": [],
                "quality": []
            }
        }
        
        # Generate files
        for i in range(config["files"]):
            file_path = self._generate_file_path(i, config["components"])
            content, issues = self._generate_file_content(
                config["lines_per_file"],
                i % 3  # Vary issue types
            )
            
            repo["files"][file_path] = content
            
            # Track issues
            for issue_type, issue_list in issues.items():
                repo["issues"][issue_type].extend([
                    {"file": file_path, "line": line, "pattern": pattern}
                    for line, pattern in issue_list
                ])
        
        return repo
    
    def _generate_file_path(self, index: int, num_components: int) -> str:
        """Generate a realistic file path."""
        components = ["auth", "api", "database", "utils", "models", "views", 
                     "services", "controllers", "middleware", "config"]
        
        component = components[index % min(num_components, len(components))]
        filename = f"module_{index % 10}.py"
        
        return f"src/{component}/{filename}"
    
    def _generate_file_content(self, num_lines: int, issue_type: int) -> tuple:
        """Generate file content with embedded issues.
        
        Args:
            num_lines: Number of lines to generate
            issue_type: 0=security, 1=performance, 2=quality
            
        Returns:
            Tuple of (content, issues_dict)
        """
        lines = []
        issues = {"security": [], "performance": [], "quality": []}
        
        # Header
        lines.append('"""Generated module for testing."""')
        lines.append("")
        lines.append("import os")
        lines.append("import sys")
        lines.append("import time")
        lines.append("import hashlib")
        lines.append("")
        
        # Add issues based on type
        if issue_type == 0:  # Security
            for i, pattern in enumerate(self.security_patterns[:2]):
                line_num = 10 + i * 5
                lines.append(f"# Security issue {i+1}")
                lines.append(pattern)
                issues["security"].append((line_num, pattern))
                lines.append("")
        
        elif issue_type == 1:  # Performance
            for i, pattern in enumerate(self.performance_patterns[:2]):
                line_num = 10 + i * 5
                lines.append(f"# Performance issue {i+1}")
                lines.append(pattern)
                issues["performance"].append((line_num, pattern))
                lines.append("")
        
        else:  # Quality
            for i, pattern in enumerate(self.quality_patterns[:2]):
                line_num = 10 + i * 5
                lines.append(f"# Quality issue {i+1}")
                lines.append(pattern)
                issues["quality"].append((line_num, pattern))
                lines.append("")
        
        # Fill remaining lines with boilerplate
        while len(lines) < num_lines:
            lines.append(f"def function_{len(lines)}():")
            lines.append("    \"\"\"Generated function.\"\"\"")
            lines.append("    return True")
            lines.append("")
        
        return "\n".join(lines[:num_lines]), issues
    
    def generate_knowledge_base(self, size: str = "medium") -> Dict[str, Any]:
        """Generate a synthetic knowledge base.
        
        Args:
            size: KB size - "small", "medium", or "large"
            
        Returns:
            Dictionary with KB metadata and documents
        """
        sizes = {
            "small": {"concepts": 20, "guides": 10, "references": 5, "research": 15},
            "medium": {"concepts": 50, "guides": 30, "references": 20, "research": 40},
            "large": {"concepts": 100, "guides": 60, "references": 40, "research": 80}
        }
        
        config = sizes[size]
        kb = {
            "metadata": {
                "size": size,
                "total_documents": sum(config.values()),
                "generated_at": datetime.now().isoformat()
            },
            "documents": {
                "concepts": [],
                "guides": [],
                "references": [],
                "research": []
            }
        }
        
        # Generate documents
        for doc_type, count in config.items():
            for i in range(count):
                doc = self._generate_document(doc_type, i)
                kb["documents"][doc_type].append(doc)
        
        return kb
    
    def _generate_document(self, doc_type: str, index: int) -> Dict[str, str]:
        """Generate a single KB document."""
        templates = {
            "concepts": {
                "title": f"Concept: {self._random_topic()} {index}",
                "content": "# Overview\n\nThis concept explains...\n\n# Details\n\n" + 
                          "Lorem ipsum " * 50
            },
            "guides": {
                "title": f"Guide: How to {self._random_action()} {index}",
                "content": "# Prerequisites\n\n# Steps\n\n1. First step\n2. Second step\n\n" +
                          "Lorem ipsum " * 40
            },
            "references": {
                "title": f"Reference: {self._random_api()} API {index}",
                "content": "# API Endpoints\n\n## GET /api/resource\n\n" +
                          "Lorem ipsum " * 30
            },
            "research": {
                "title": f"Research: {self._random_topic()} Study {index}",
                "content": "# Hypothesis\n\n# Methodology\n\n# Results\n\n" +
                          "Lorem ipsum " * 60
            }
        }
        
        template = templates[doc_type]
        return {
            "id": f"{doc_type}_{index}",
            "title": template["title"],
            "content": template["content"],
            "word_count": len(template["content"].split())
        }
    
    def _random_topic(self) -> str:
        """Generate random topic name."""
        topics = ["Authentication", "Caching", "Database", "API", "Security",
                 "Performance", "Testing", "Deployment", "Monitoring", "Logging"]
        return random.choice(topics)
    
    def _random_action(self) -> str:
        """Generate random action."""
        actions = ["implement", "configure", "optimize", "debug", "test",
                  "deploy", "monitor", "secure", "scale", "maintain"]
        return random.choice(actions)
    
    def _random_api(self) -> str:
        """Generate random API name."""
        apis = ["User", "Auth", "Product", "Order", "Payment",
               "Notification", "Analytics", "Search", "Upload", "Export"]
        return random.choice(apis)
    
    def save_repository(self, repo: Dict[str, Any], name: str):
        """Save repository to disk."""
        repo_dir = self.output_dir / "repositories" / name
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        with open(repo_dir / "metadata.json", "w") as f:
            json.dump(repo["metadata"], f, indent=2)
        
        # Save files
        for file_path, content in repo["files"].items():
            full_path = repo_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
        
        # Save issues
        with open(repo_dir / "issues.json", "w") as f:
            json.dump(repo["issues"], f, indent=2)
        
        print(f"✓ Saved repository '{name}' to {repo_dir}")
    
    def save_knowledge_base(self, kb: Dict[str, Any], name: str):
        """Save knowledge base to disk."""
        kb_dir = self.output_dir / "knowledge_bases" / name
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        with open(kb_dir / "metadata.json", "w") as f:
            json.dump(kb["metadata"], f, indent=2)
        
        # Save documents
        for doc_type, documents in kb["documents"].items():
            type_dir = kb_dir / doc_type
            type_dir.mkdir(exist_ok=True)
            
            for doc in documents:
                doc_file = type_dir / f"{doc['id']}.md"
                with open(doc_file, "w") as f:
                    f.write(f"# {doc['title']}\n\n{doc['content']}")
        
        print(f"✓ Saved knowledge base '{name}' to {kb_dir}")
    
    def generate_all_scenarios(self):
        """Generate all test scenarios."""
        print("Generating synthetic data for all scenarios...")
        print("=" * 60)
        
        # Scenario 1: Small repository
        print("\n[1/5] Generating small repository...")
        small_repo = self.generate_repository("small")
        self.save_repository(small_repo, "scenario_1_small")
        
        # Scenario 2: Medium repository
        print("\n[2/5] Generating medium repository...")
        medium_repo = self.generate_repository("medium")
        self.save_repository(medium_repo, "scenario_2_medium")
        
        # Scenario 3: Large repository
        print("\n[3/5] Generating large repository...")
        large_repo = self.generate_repository("large")
        self.save_repository(large_repo, "scenario_3_large")
        
        # Scenario 4: Medium repository with KB
        print("\n[4/5] Generating medium repository with knowledge base...")
        self.save_repository(medium_repo, "scenario_4_deep_analysis")
        medium_kb = self.generate_knowledge_base("medium")
        self.save_knowledge_base(medium_kb, "scenario_4_kb")
        
        # Scenario 5: Medium repository for parallel testing
        print("\n[5/5] Generating repository for parallel execution test...")
        self.save_repository(medium_repo, "scenario_5_parallel")
        
        print("\n" + "=" * 60)
        print("✓ All synthetic data generated successfully!")
        print(f"✓ Output directory: {self.output_dir.absolute()}")
        
        # Generate summary
        summary = {
            "generated_at": datetime.now().isoformat(),
            "scenarios": [
                {
                    "id": 1,
                    "name": "Small Repository",
                    "files": small_repo["metadata"]["total_files"],
                    "lines": small_repo["metadata"]["total_lines"],
                    "components": small_repo["metadata"]["components"]
                },
                {
                    "id": 2,
                    "name": "Medium Repository",
                    "files": medium_repo["metadata"]["total_files"],
                    "lines": medium_repo["metadata"]["total_lines"],
                    "components": medium_repo["metadata"]["components"]
                },
                {
                    "id": 3,
                    "name": "Large Repository",
                    "files": large_repo["metadata"]["total_files"],
                    "lines": large_repo["metadata"]["total_lines"],
                    "components": large_repo["metadata"]["components"]
                },
                {
                    "id": 4,
                    "name": "Deep Analysis (Medium + KB)",
                    "files": medium_repo["metadata"]["total_files"],
                    "kb_documents": medium_kb["metadata"]["total_documents"]
                },
                {
                    "id": 5,
                    "name": "Parallel Execution",
                    "files": medium_repo["metadata"]["total_files"],
                    "parallel_tasks": 6
                }
            ]
        }
        
        with open(self.output_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Summary saved to {self.output_dir / 'summary.json'}")


def main():
    """Main entry point."""
    generator = SyntheticDataGenerator()
    generator.generate_all_scenarios()


if __name__ == "__main__":
    main()
