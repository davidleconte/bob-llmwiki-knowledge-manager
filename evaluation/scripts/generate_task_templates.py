"""Generate task templates for baseline data collection."""
from pathlib import Path
import json
from collect_metrics import create_task_template


def generate_control_tasks():
    """Generate 30 control task templates."""
    tasks = []
    
    # Document Creation (10 tasks)
    for i in range(1, 11):
        task = create_task_template(
            f'DC_C_{i:03d}',
            'document_creation',
            'control',
            'user1'
        )
        tasks.append(task)
    
    # Retrieval (10 tasks)
    for i in range(1, 11):
        task = create_task_template(
            f'RT_C_{i:03d}',
            'retrieval',
            'control',
            'user1'
        )
        tasks.append(task)
    
    # Maintenance (5 tasks)
    for i in range(1, 6):
        task = create_task_template(
            f'MT_C_{i:03d}',
            'maintenance',
            'control',
            'user1'
        )
        tasks.append(task)
    
    # Synthesis (5 tasks)
    for i in range(1, 6):
        task = create_task_template(
            f'SY_C_{i:03d}',
            'synthesis',
            'control',
            'user1'
        )
        tasks.append(task)
    
    return tasks


def generate_treatment_tasks():
    """Generate 30 treatment task templates."""
    tasks = []
    
    # Document Creation (10 tasks)
    for i in range(1, 11):
        task = create_task_template(
            f'DC_T_{i:03d}',
            'document_creation',
            'treatment',
            'user1'
        )
        tasks.append(task)
    
    # Retrieval (10 tasks)
    for i in range(1, 11):
        task = create_task_template(
            f'RT_T_{i:03d}',
            'retrieval',
            'treatment',
            'user1'
        )
        tasks.append(task)
    
    # Maintenance (5 tasks)
    for i in range(1, 6):
        task = create_task_template(
            f'MT_T_{i:03d}',
            'maintenance',
            'treatment',
            'user1'
        )
        tasks.append(task)
    
    # Synthesis (5 tasks)
    for i in range(1, 6):
        task = create_task_template(
            f'SY_T_{i:03d}',
            'synthesis',
            'treatment',
            'user1'
        )
        tasks.append(task)
    
    return tasks


def save_templates(output_dir: str = "../data/templates"):
    """Save task templates to JSON files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate control tasks
    control_tasks = generate_control_tasks()
    control_file = output_path / "control_tasks.json"
    with open(control_file, 'w') as f:
        json.dump(control_tasks, f, indent=2)
    print(f"✅ Generated {len(control_tasks)} control task templates: {control_file}")
    
    # Generate treatment tasks
    treatment_tasks = generate_treatment_tasks()
    treatment_file = output_path / "treatment_tasks.json"
    with open(treatment_file, 'w') as f:
        json.dump(treatment_tasks, f, indent=2)
    print(f"✅ Generated {len(treatment_tasks)} treatment task templates: {treatment_file}")
    
    # Create task list summary
    summary = {
        "total_tasks": len(control_tasks) + len(treatment_tasks),
        "control_tasks": len(control_tasks),
        "treatment_tasks": len(treatment_tasks),
        "scenarios": {
            "document_creation": 10,
            "retrieval": 10,
            "maintenance": 5,
            "synthesis": 5
        }
    }
    
    summary_file = output_path / "task_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Generated task summary: {summary_file}")
    
    return control_tasks, treatment_tasks


if __name__ == "__main__":
    control, treatment = save_templates()
    print(f"\n📋 Task Templates Summary:")
    print(f"   Control Tasks: {len(control)}")
    print(f"   Treatment Tasks: {len(treatment)}")
    print(f"   Total: {len(control) + len(treatment)}")
    print(f"\n💡 Next: Fill in metrics after completing each task")
