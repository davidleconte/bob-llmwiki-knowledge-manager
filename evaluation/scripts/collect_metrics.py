"""Metrics collection for adversarial review."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class MetricsCollector:
    """Collect and store metrics for adversarial review tasks."""
    
    def __init__(self, output_dir: str = "../data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def record_task(self, task_data: Dict[str, Any]) -> None:
        """Record metrics for a single task.
        
        Args:
            task_data: Dictionary containing task metrics and metadata
        """
        task_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Validate required fields
        required_fields = ['task_id', 'scenario', 'condition']
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"Missing required field: {field}")
        
        filename = f"{task_data['task_id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        print(f"✅ Recorded task: {task_data['task_id']}")
    
    def load_all_tasks(self) -> List[Dict[str, Any]]:
        """Load all recorded tasks.
        
        Returns:
            List of task data dictionaries
        """
        tasks = []
        for filepath in self.output_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                tasks.append(json.load(f))
        return tasks
    
    def get_task_count(self) -> int:
        """Get total number of recorded tasks."""
        return len(list(self.output_dir.glob("*.json")))
    
    def get_tasks_by_condition(self, condition: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific condition.
        
        Args:
            condition: 'control' or 'treatment'
            
        Returns:
            List of task data for the specified condition
        """
        all_tasks = self.load_all_tasks()
        return [t for t in all_tasks if t.get('condition') == condition]
    
    def get_tasks_by_scenario(self, scenario: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific scenario.
        
        Args:
            scenario: Scenario name
            
        Returns:
            List of task data for the specified scenario
        """
        all_tasks = self.load_all_tasks()
        return [t for t in all_tasks if t.get('scenario') == scenario]


def create_task_template(
    task_id: str,
    scenario: str,
    condition: str,
    participant: str = "default"
) -> Dict[str, Any]:
    """Create a task data template.
    
    Args:
        task_id: Unique task identifier
        scenario: Scenario name (document_creation, retrieval, maintenance, synthesis)
        condition: 'control' or 'treatment'
        participant: Participant identifier
        
    Returns:
        Task data template dictionary
    """
    return {
        "task_id": task_id,
        "scenario": scenario,
        "condition": condition,
        "participant": participant,
        "timestamp": None,  # Will be set by record_task
        "metrics": {
            "tokens_used": 0,
            "bobcoin_cost": 0.0,
            "time_seconds": 0,
            "quality_score": {
                "completeness": 0,
                "accuracy": 0,
                "consistency": 0,
                "usability": 0,
                "total": 0
            },
            "cross_references": 0,
            "search_queries": 0,
            "memory_recalls": 0
        },
        "artifacts": {
            "input": "",
            "output": "",
            "transcript": ""
        }
    }


if __name__ == "__main__":
    # Example usage
    collector = MetricsCollector()
    
    # Create example task
    task = create_task_template(
        task_id="test_001",
        scenario="document_creation",
        condition="control",
        participant="user1"
    )
    
    # Simulate metrics
    task["metrics"]["tokens_used"] = 450
    task["metrics"]["bobcoin_cost"] = 0.045
    task["metrics"]["time_seconds"] = 120
    task["metrics"]["quality_score"]["total"] = 85
    
    # Record task
    collector.record_task(task)
    
    print(f"Total tasks recorded: {collector.get_task_count()}")
