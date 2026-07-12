"""Red team adversarial testing scenarios."""
from pathlib import Path
from typing import Dict, List
import json


class RedTeamScenarios:
    """Generate adversarial test scenarios."""
    
    SCENARIOS = {
        "token_bloat": {
            "name": "Token Bloat Attack",
            "description": "Test if KB prevents unnecessary token usage",
            "tests": [
                {
                    "id": "TB-001",
                    "task": "Create documentation with excessive context",
                    "expected": "KB should encourage concise documentation",
                    "red_flag": "Accepts verbose, redundant content without warning"
                },
                {
                    "id": "TB-002", 
                    "task": "Reference same document multiple times unnecessarily",
                    "expected": "KB should detect and prevent duplicate references",
                    "red_flag": "Allows redundant cross-references"
                },
                {
                    "id": "TB-003",
                    "task": "Create deeply nested document structure",
                    "expected": "KB should suggest flatter structure",
                    "red_flag": "Allows excessive nesting without guidance"
                }
            ]
        },
        "quality_degradation": {
            "name": "Quality Degradation Attack",
            "description": "Test if KB maintains quality standards",
            "tests": [
                {
                    "id": "QD-001",
                    "task": "Create document with missing required sections",
                    "expected": "Validation should catch incomplete templates",
                    "red_flag": "Accepts incomplete documentation"
                },
                {
                    "id": "QD-002",
                    "task": "Add broken cross-references",
                    "expected": "Validation should detect broken links",
                    "red_flag": "Allows invalid references"
                },
                {
                    "id": "QD-003",
                    "task": "Create duplicate content in different locations",
                    "expected": "Should detect and prevent duplication",
                    "red_flag": "Allows content duplication"
                }
            ]
        },
        "context_overflow": {
            "name": "Context Overflow Attack",
            "description": "Test context window management",
            "tests": [
                {
                    "id": "CO-001",
                    "task": "Load entire KB into context at once",
                    "expected": "Should use selective loading strategies",
                    "red_flag": "Loads all documents unnecessarily"
                },
                {
                    "id": "CO-002",
                    "task": "Request synthesis of 50+ documents",
                    "expected": "Should batch process or suggest refinement",
                    "red_flag": "Attempts to load all at once"
                },
                {
                    "id": "CO-003",
                    "task": "Create circular reference chain",
                    "expected": "Should detect and prevent circular refs",
                    "red_flag": "Allows circular dependencies"
                }
            ]
        },
        "cross_reference_chaos": {
            "name": "Cross-Reference Chaos Attack",
            "description": "Test reference management robustness",
            "tests": [
                {
                    "id": "CR-001",
                    "task": "Delete document with many incoming references",
                    "expected": "Should warn about broken references",
                    "red_flag": "Allows deletion without warning"
                },
                {
                    "id": "CR-002",
                    "task": "Rename document referenced by others",
                    "expected": "Should update or warn about references",
                    "red_flag": "Breaks references silently"
                },
                {
                    "id": "CR-003",
                    "task": "Create reference to non-existent document",
                    "expected": "Validation should catch invalid reference",
                    "red_flag": "Allows dangling references"
                }
            ]
        },
        "memory_pollution": {
            "name": "Memory Pollution Attack",
            "description": "Test memory management and cleanup",
            "tests": [
                {
                    "id": "MP-001",
                    "task": "Save contradictory facts to memory",
                    "expected": "Should detect conflicts or version facts",
                    "red_flag": "Accepts contradictory information"
                },
                {
                    "id": "MP-002",
                    "task": "Save temporary information as permanent",
                    "expected": "Should distinguish temporary vs permanent",
                    "red_flag": "Treats all memory equally"
                },
                {
                    "id": "MP-003",
                    "task": "Accumulate obsolete memories over time",
                    "expected": "Should have cleanup or archival strategy",
                    "red_flag": "No memory management strategy"
                }
            ]
        }
    }
    
    def generate_test_plan(self, output_file: str = "../redteam_test_plan.md") -> None:
        """Generate comprehensive red team test plan."""
        
        report = """# Red Team Adversarial Testing Plan

## Overview
This document outlines adversarial testing scenarios designed to stress-test the Bob Shell Knowledge Manager against edge cases, abuse patterns, and failure modes.

## Testing Methodology
1. Execute each test scenario in both control and treatment conditions
2. Document actual behavior vs expected behavior
3. Identify vulnerabilities and improvement opportunities
4. Measure impact on token usage, quality, and user experience

"""
        
        for scenario_id, scenario in self.SCENARIOS.items():
            report += f"\n## {scenario['name']}\n\n"
            report += f"**Description**: {scenario['description']}\n\n"
            report += "### Test Cases\n\n"
            
            for test in scenario['tests']:
                report += f"#### {test['id']}: {test['task']}\n\n"
                report += f"- **Expected Behavior**: {test['expected']}\n"
                report += f"- **Red Flag**: {test['red_flag']}\n"
                report += "- **Status**: [ ] Not Started\n"
                report += "- **Result**: _To be filled_\n"
                report += "- **Notes**: _To be filled_\n\n"
        
        report += """
## Scoring Rubric

For each test case:
- **Pass**: System behaves as expected, prevents or warns about issue
- **Partial**: System detects issue but handling could be improved
- **Fail**: System exhibits red flag behavior

## Success Criteria
- 80%+ of tests should Pass
- No more than 10% should Fail
- Any Fail results should have mitigation plan

---
*Generated by Red Team Scenarios*
"""
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated red team test plan: {output_path}")
    
    def generate_test_data(self, output_dir: str = "../data/redteam") -> None:
        """Generate test data files for red team scenarios."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for scenario_id, scenario in self.SCENARIOS.items():
            scenario_file = output_path / f"{scenario_id}.json"
            with open(scenario_file, 'w') as f:
                json.dump(scenario, f, indent=2)
        
        print(f"✅ Generated {len(self.SCENARIOS)} red team scenario files in {output_path}")


if __name__ == "__main__":
    redteam = RedTeamScenarios()
    redteam.generate_test_plan()
    redteam.generate_test_data()
    
    print(f"\n📋 Red Team Scenarios Summary:")
    print(f"   Total Scenarios: {len(redteam.SCENARIOS)}")
    total_tests = sum(len(s['tests']) for s in redteam.SCENARIOS.values())
    print(f"   Total Test Cases: {total_tests}")
