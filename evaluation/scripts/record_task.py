#!/usr/bin/env python3
"""Interactive script to record task metrics."""
import json
from pathlib import Path
from collect_metrics import MetricsCollector


def load_template(task_id: str, templates_dir: str = "../data/templates"):
    """Load a task template by ID."""
    templates_path = Path(templates_dir)
    
    # Try control tasks
    control_file = templates_path / "control_tasks.json"
    if control_file.exists():
        with open(control_file, 'r') as f:
            control_tasks = json.load(f)
            for task in control_tasks:
                if task['task_id'] == task_id:
                    return task
    
    # Try treatment tasks
    treatment_file = templates_path / "treatment_tasks.json"
    if treatment_file.exists():
        with open(treatment_file, 'r') as f:
            treatment_tasks = json.load(f)
            for task in treatment_tasks:
                if task['task_id'] == task_id:
                    return task
    
    return None


def record_metrics_interactive():
    """Interactive metrics recording."""
    print("=" * 60)
    print("Task Metrics Recording")
    print("=" * 60)
    
    # Get task ID
    task_id = input("\nTask ID (e.g., DC_C_001): ").strip()
    
    # Load template
    task = load_template(task_id)
    if not task:
        print(f"❌ Template not found for {task_id}")
        print("Available prefixes: DC_C, RT_C, MT_C, SY_C (control)")
        print("                    DC_T, RT_T, MT_T, SY_T (treatment)")
        return
    
    print(f"\n✅ Loaded template for {task_id}")
    print(f"   Scenario: {task['scenario']}")
    print(f"   Condition: {task['condition']}")
    
    # Collect metrics
    print("\n" + "-" * 60)
    print("Enter Metrics:")
    print("-" * 60)
    
    try:
        tokens = int(input("Tokens used: "))
        cost = float(input("Bobcoin cost (e.g., 0.045): "))
        time_sec = int(input("Time in seconds: "))
        
        print("\nQuality Scores (0-25 each):")
        completeness = int(input("  Completeness: "))
        accuracy = int(input("  Accuracy: "))
        consistency = int(input("  Consistency: "))
        usability = int(input("  Usability: "))
        
        # Update task
        task['metrics']['tokens_used'] = tokens
        task['metrics']['bobcoin_cost'] = cost
        task['metrics']['time_seconds'] = time_sec
        task['metrics']['quality_score']['completeness'] = completeness
        task['metrics']['quality_score']['accuracy'] = accuracy
        task['metrics']['quality_score']['consistency'] = consistency
        task['metrics']['quality_score']['usability'] = usability
        task['metrics']['quality_score']['total'] = completeness + accuracy + consistency + usability
        
        # Treatment-specific metrics
        if task['condition'] == 'treatment':
            print("\nTreatment-specific metrics:")
            task['metrics']['cross_references'] = int(input("  Cross-references used: "))
            task['metrics']['search_queries'] = int(input("  Search queries: "))
            task['metrics']['memory_recalls'] = int(input("  Memory recalls: "))
        
        # Save
        collector = MetricsCollector()
        collector.record_task(task)
        
        print("\n" + "=" * 60)
        print(f"✅ Task {task_id} recorded successfully!")
        print(f"   Quality Score: {task['metrics']['quality_score']['total']}/100")
        print(f"   Tokens: {tokens}")
        print(f"   Cost: ${cost:.3f}")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
    except KeyboardInterrupt:
        print("\n\n❌ Recording cancelled")


def quick_record():
    """Quick record with command-line args."""
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python3 record_task.py TASK_ID TOKENS COST TIME [QUALITY]")
        print("Example: python3 record_task.py DC_C_001 450 0.045 120 85")
        return
    
    task_id = sys.argv[1]
    tokens = int(sys.argv[2])
    cost = float(sys.argv[3])
    time_sec = int(sys.argv[4])
    quality = int(sys.argv[5]) if len(sys.argv) > 5 else 85
    
    task = load_template(task_id)
    if not task:
        print(f"❌ Template not found for {task_id}")
        return
    
    # Distribute quality score evenly
    per_category = quality // 4
    remainder = quality % 4
    
    task['metrics']['tokens_used'] = tokens
    task['metrics']['bobcoin_cost'] = cost
    task['metrics']['time_seconds'] = time_sec
    task['metrics']['quality_score']['completeness'] = per_category + (1 if remainder > 0 else 0)
    task['metrics']['quality_score']['accuracy'] = per_category + (1 if remainder > 1 else 0)
    task['metrics']['quality_score']['consistency'] = per_category + (1 if remainder > 2 else 0)
    task['metrics']['quality_score']['usability'] = per_category
    task['metrics']['quality_score']['total'] = quality
    
    collector = MetricsCollector()
    collector.record_task(task)
    
    print(f"✅ Recorded {task_id}: {tokens} tokens, ${cost:.3f}, {time_sec}s, quality {quality}/100")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        quick_record()
    else:
        record_metrics_interactive()
