#!/usr/bin/env python3
"""
Sub-Agent Delegation Framework Example
Demonstrates parallel analysis using specialized sub-agents
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.delegation import DelegationCoordinator, SubAgentTask, SubAgentPriority
from src.delegation.agents import (
    SecurityAgent,
    PerformanceAgent,
    QualityAgent,
    ArchitectureAgent,
    DocumentationAgent,
    ResearchAgent
)


def main():
    """Example: Parallel repository analysis using sub-agents"""
    
    print("=" * 80)
    print("Sub-Agent Delegation Framework Example".center(80))
    print("=" * 80)
    print()
    
    # 1. Create coordinator
    print("1. Creating delegation coordinator...")
    coordinator = DelegationCoordinator(
        max_workers=5,
        timeout_seconds=600,
        enable_retry=True
    )
    
    # 2. Register specialized agents
    print("2. Registering specialized agents...")
    agents = [
        SecurityAgent("security-1"),
        PerformanceAgent("performance-1"),
        QualityAgent("quality-1"),
        ArchitectureAgent("architecture-1"),
        DocumentationAgent("documentation-1"),
        ResearchAgent("research-1")
    ]
    
    for agent in agents:
        coordinator.register_agent(agent)
        print(f"   ✓ Registered: {agent.agent_type} ({agent.agent_id})")
    
    print()
    
    # 3. Create analysis tasks
    print("3. Creating analysis tasks...")
    tasks = [
        SubAgentTask(
            task_id="security-cache",
            task_type="security",
            target="src/cache",
            parameters={"depth": "deep"},
            priority=SubAgentPriority.HIGH
        ),
        SubAgentTask(
            task_id="performance-cache",
            task_type="performance",
            target="src/cache",
            parameters={"depth": "shallow"},
            priority=SubAgentPriority.MEDIUM
        ),
        SubAgentTask(
            task_id="quality-cache",
            task_type="quality",
            target="src/cache",
            parameters={"depth": "shallow"},
            priority=SubAgentPriority.MEDIUM
        ),
        SubAgentTask(
            task_id="architecture-src",
            task_type="architecture",
            target="src",
            parameters={"depth": "shallow"},
            priority=SubAgentPriority.LOW
        ),
        SubAgentTask(
            task_id="documentation-src",
            task_type="documentation",
            target="src",
            parameters={},
            priority=SubAgentPriority.LOW
        ),
        SubAgentTask(
            task_id="research-caching",
            task_type="research",
            target="",
            parameters={
                "query": "caching strategy",
                "categories": ["concepts", "research"],
                "max_results": 5
            },
            priority=SubAgentPriority.MEDIUM
        )
    ]
    
    coordinator.add_tasks(tasks)
    print(f"   ✓ Added {len(tasks)} tasks")
    print()
    
    # 4. Execute tasks in parallel
    print("4. Executing tasks in parallel...")
    print("   (This may take a few moments...)")
    print()
    
    results = coordinator.execute_parallel()
    
    # 5. Display results
    print("5. Results:")
    print()
    
    successful = coordinator.get_successful_results()
    failed = coordinator.get_failed_results()
    
    print(f"   ✓ Successful: {len(successful)}")
    print(f"   ✗ Failed: {len(failed)}")
    print()
    
    # Display successful results
    if successful:
        print("   Successful Tasks:")
        for task_id, result in successful.items():
            print(f"      • {task_id}")
            print(f"        Agent: {result.agent_type}")
            print(f"        Time: {result.execution_time_ms:.0f}ms")
            print(f"        Tokens: {result.token_count}")
            
            # Show key findings
            if result.agent_type == "security":
                data = result.data
                print(f"        Issues: {data.get('total_issues', 0)} (Risk: {data.get('risk_level', 'N/A')})")
            elif result.agent_type == "performance":
                data = result.data
                print(f"        Issues: {data.get('total_issues', 0)} (Score: {data.get('optimization_score', 0):.0f})")
            elif result.agent_type == "quality":
                data = result.data
                print(f"        Grade: {data.get('quality_grade', 'N/A')} (Score: {data.get('quality_score', 0):.0f})")
            elif result.agent_type == "architecture":
                data = result.data
                print(f"        Imports: {data.get('unique_imports', 0)}")
            elif result.agent_type == "documentation":
                data = result.data
                print(f"        Coverage: {data.get('coverage_percentage', 0):.1f}% (Grade: {data.get('coverage_grade', 'N/A')})")
            elif result.agent_type == "research":
                data = result.data
                print(f"        Results: {data.get('total_results', 0)}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"        ⚠️  {warning}")
            print()
    
    # Display failed results
    if failed:
        print("   Failed Tasks:")
        for task_id, result in failed.items():
            print(f"      • {task_id}")
            for error in result.errors:
                print(f"        ✗ {error}")
            print()
    
    # 6. Display statistics
    print("6. Execution Statistics:")
    stats = coordinator.get_statistics()
    print(f"   Total Tasks: {stats['total_tasks']}")
    print(f"   Success Rate: {stats['success_rate']:.1%}")
    print(f"   Total Time: {stats['total_execution_time_ms']:.0f}ms")
    print(f"   Parallel Time: {stats['parallel_execution_time_ms']:.0f}ms")
    print(f"   Speedup: {stats['parallelization_factor']:.1f}x")
    print(f"   Total Tokens: {stats['total_tokens']:,}")
    print()
    
    # 7. Generate report
    print("7. Generating detailed report...")
    report = coordinator.generate_report()
    
    report_path = Path("reports/delegation_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    print(f"   ✓ Report saved to: {report_path}")
    print()
    
    print("=" * 80)
    print("Example Complete!".center(80))
    print("=" * 80)


if __name__ == "__main__":
    main()
