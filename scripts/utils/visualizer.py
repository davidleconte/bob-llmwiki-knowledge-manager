#!/usr/bin/env python3
"""
Visualization Generator Utility
Creates charts and diagrams from analysis data
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

ChartType = Literal["bar", "pie", "line", "timeline", "tree"]


class Visualizer:
    """Generate visualizations from analysis data"""

    def __init__(self, output_dir: str = "reports/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        data: Dict,
        chart_type: ChartType,
        title: str,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        Generate a visualization
        
        Args:
            data: Data to visualize
            chart_type: Type of chart to generate
            title: Chart title
            output_file: Output filename (auto-generated if None)
            
        Returns:
            Dictionary with generation result
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{chart_type}_{timestamp}.txt"

        output_path = self.output_dir / output_file

        try:
            if chart_type == "bar":
                content = self._generate_bar_chart(data, title)
            elif chart_type == "pie":
                content = self._generate_pie_chart(data, title)
            elif chart_type == "line":
                content = self._generate_line_chart(data, title)
            elif chart_type == "timeline":
                content = self._generate_timeline(data, title)
            elif chart_type == "tree":
                content = self._generate_tree(data, title)
            else:
                return {"error": f"Unknown chart type: {chart_type}"}

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "chart_type": chart_type,
                "title": title,
                "output_file": str(output_path),
                "preview": content[:500] + "..." if len(content) > 500 else content
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_bar_chart(self, data: Dict, title: str) -> str:
        """Generate ASCII bar chart"""
        if "values" not in data or "labels" not in data:
            raise ValueError("Data must contain 'values' and 'labels' keys")

        values = data["values"]
        labels = data["labels"]

        if len(values) != len(labels):
            raise ValueError("Values and labels must have same length")

        # Calculate max value for scaling
        max_value = max(values) if values else 1
        max_label_len = max(len(str(label)) for label in labels) if labels else 0

        # Chart width
        chart_width = 60

        lines = []
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append("")

        for label, value in zip(labels, values):
            # Calculate bar length
            bar_len = int((value / max_value) * chart_width) if max_value > 0 else 0
            bar = "█" * bar_len

            # Format line
            label_str = str(label).ljust(max_label_len)
            value_str = f"{value:,}"
            line = f"{label_str} | {bar} {value_str}"
            lines.append(line)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_pie_chart(self, data: Dict, title: str) -> str:
        """Generate ASCII pie chart representation"""
        if "values" not in data or "labels" not in data:
            raise ValueError("Data must contain 'values' and 'labels' keys")

        values = data["values"]
        labels = data["labels"]

        if len(values) != len(labels):
            raise ValueError("Values and labels must have same length")

        total = sum(values)

        lines = []
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append("")

        # Calculate percentages
        for label, value in zip(labels, values):
            percentage = (value / total * 100) if total > 0 else 0
            bar_len = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_len

            line = f"{label:20} | {bar} {percentage:5.1f}% ({value:,})"
            lines.append(line)

        lines.append("")
        lines.append(f"Total: {total:,}")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_line_chart(self, data: Dict, title: str) -> str:
        """Generate ASCII line chart"""
        if "values" not in data or "labels" not in data:
            raise ValueError("Data must contain 'values' and 'labels' keys")

        values = data["values"]
        labels = data["labels"]

        if len(values) != len(labels):
            raise ValueError("Values and labels must have same length")

        # Chart dimensions
        height = 20
        width = len(values)

        # Scale values to chart height
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max_value - min_value if max_value != min_value else 1

        scaled_values = [
            int((v - min_value) / value_range * (height - 1))
            for v in values
        ]

        lines = []
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append("")

        # Draw chart from top to bottom
        for row in range(height - 1, -1, -1):
            line_chars = []

            # Y-axis label
            value_at_row = min_value + (row / (height - 1)) * value_range
            line_chars.append(f"{value_at_row:8.1f} |")

            # Plot points
            for i, scaled_val in enumerate(scaled_values):
                if scaled_val == row:
                    line_chars.append("●")
                elif scaled_val > row and i > 0 and scaled_values[i-1] <= row:
                    line_chars.append("╱")
                elif scaled_val < row and i > 0 and scaled_values[i-1] >= row:
                    line_chars.append("╲")
                elif i > 0 and min(scaled_val, scaled_values[i-1]) <= row <= max(scaled_val, scaled_values[i-1]):
                    line_chars.append("│")
                else:
                    line_chars.append(" ")

            lines.append("".join(line_chars))

        # X-axis
        lines.append("         " + "─" * width)

        # X-axis labels (show every nth label to avoid crowding)
        step = max(1, len(labels) // 10)
        label_line = "         "
        for i, label in enumerate(labels):
            if i % step == 0:
                label_line += str(label)[:3].ljust(step)
        lines.append(label_line)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_timeline(self, data: Dict, title: str) -> str:
        """Generate ASCII timeline"""
        if "events" not in data:
            raise ValueError("Data must contain 'events' key")

        events = data["events"]

        lines = []
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append("")

        for i, event in enumerate(events):
            date = event.get("date", "Unknown")
            description = event.get("description", "")
            details = event.get("details", "")

            # Timeline connector
            if i == 0:
                connector = "●"
            else:
                connector = "│\n●"

            lines.append(connector)
            lines.append(f"  {date}")
            lines.append(f"  {description}")

            if details:
                lines.append(f"    └─ {details}")

            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_tree(self, data: Dict, title: str) -> str:
        """Generate ASCII tree structure"""
        if "root" not in data:
            raise ValueError("Data must contain 'root' key")

        lines = []
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append("")

        def render_node(node: Dict, prefix: str = "", is_last: bool = True):
            """Recursively render tree nodes"""
            name = node.get("name", "Unknown")
            children = node.get("children", [])

            # Current node
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + name)

            # Children
            if children:
                extension = "    " if is_last else "│   "
                for i, child in enumerate(children):
                    is_last_child = (i == len(children) - 1)
                    render_node(child, prefix + extension, is_last_child)

        # Render root
        root = data["root"]
        lines.append(root.get("name", "Root"))

        children = root.get("children", [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            render_node(child, "", is_last_child)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_security_report(self, security_data: Dict) -> Dict:
        """Generate security analysis visualization"""
        # Severity distribution
        severity_chart = self.generate(
            {
                "labels": ["Critical", "High", "Medium", "Low"],
                "values": [
                    security_data.get("critical", 0),
                    security_data.get("high", 0),
                    security_data.get("medium", 0),
                    security_data.get("low", 0)
                ]
            },
            "bar",
            "Security Issues by Severity",
            "security_severity.txt"
        )

        return severity_chart

    def generate_quality_report(self, quality_data: Dict) -> Dict:
        """Generate code quality visualization"""
        # Quality metrics
        metrics_chart = self.generate(
            {
                "labels": ["Total Lines", "Functions", "Long Functions", "Complex Functions"],
                "values": [
                    quality_data.get("total_lines", 0),
                    quality_data.get("total_functions", 0),
                    quality_data.get("long_functions", 0),
                    quality_data.get("complex_functions", 0)
                ]
            },
            "bar",
            "Code Quality Metrics",
            "quality_metrics.txt"
        )

        return metrics_chart

    def generate_dependency_tree(self, dependencies: Dict) -> Dict:
        """Generate dependency tree visualization"""
        # Convert dependencies to tree structure
        tree_data = {
            "root": {
                "name": "Project Dependencies",
                "children": [
                    {
                        "name": dep,
                        "children": [
                            {"name": sub_dep, "children": []}
                            for sub_dep in deps[:5]  # Limit to first 5
                        ]
                    }
                    for dep, deps in list(dependencies.items())[:10]  # Limit to first 10
                ]
            }
        }

        return self.generate(
            tree_data,
            "tree",
            "Dependency Tree",
            "dependency_tree.txt"
        )

    def generate_progress_timeline(self, milestones: List[Dict]) -> Dict:
        """Generate project progress timeline"""
        timeline_data = {
            "events": milestones
        }

        return self.generate(
            timeline_data,
            "timeline",
            "Project Progress Timeline",
            "progress_timeline.txt"
        )


def main():
    """CLI interface for visualizer"""
    import argparse

    parser = argparse.ArgumentParser(description="Visualization Generator Utility")
    parser.add_argument("--output-dir", default="reports/visualizations", help="Output directory")
    parser.add_argument("--data", required=True, help="JSON data file or JSON string")
    parser.add_argument(
        "--type",
        choices=["bar", "pie", "line", "timeline", "tree"],
        required=True,
        help="Chart type"
    )
    parser.add_argument("--title", required=True, help="Chart title")
    parser.add_argument("--output", help="Output filename")

    args = parser.parse_args()

    # Load data
    try:
        if Path(args.data).exists():
            with open(args.data, 'r') as f:
                data = json.load(f)
        else:
            data = json.loads(args.data)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    # Generate visualization
    visualizer = Visualizer(args.output_dir)
    result = visualizer.generate(
        data,
        args.type,
        args.title,
        args.output
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    print(f"\n✓ Visualization generated: {result['output_file']}")
    print("\nPreview:")
    print(result['preview'])


if __name__ == "__main__":
    main()
