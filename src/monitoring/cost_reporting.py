"""
Cost reporting utilities for generating dashboards and summaries.

Provides formatted reports, dashboards, and cost analysis tools for
the Token Optimization System's Bobcoin tracking.
"""

import json
from typing import Any, Dict, List

from src.monitoring.cost_tracker import get_cost_tracker


def generate_cost_summary() -> Dict[str, Any]:
    """
    Generate comprehensive cost summary.

    Returns:
        Dictionary with cost summary data
    """
    tracker = get_cost_tracker()
    return tracker.get_summary()


def generate_cost_dashboard() -> str:
    """
    Generate ASCII dashboard for cost tracking.

    Returns:
        Formatted dashboard string
    """
    tracker = get_cost_tracker()
    summary = tracker.get_summary()

    budget = summary["budget"]
    costs = summary["costs"]
    rate = summary["rate"]
    alerts = summary["alerts"]

    # Build dashboard
    lines = []
    lines.append("=" * 70)
    lines.append("BOBCOIN COST TRACKING DASHBOARD".center(70))
    lines.append("=" * 70)
    lines.append("")

    # Budget section
    lines.append("BUDGET STATUS".center(70))
    lines.append("-" * 70)
    lines.append(f"  Budget:           {budget['budget_bobcoins']:>10.4f} Bobcoins")
    lines.append(f"  Spent:            {budget['spent_bobcoins']:>10.4f} Bobcoins")
    lines.append(f"  Saved:            {budget['saved_bobcoins']:>10.4f} Bobcoins")
    lines.append(f"  Net Spent:        {budget['net_spent_bobcoins']:>10.4f} Bobcoins")
    lines.append(f"  Remaining:        {budget['remaining_bobcoins']:>10.4f} Bobcoins")
    lines.append(f"  Used:             {budget['percent_used']:>10.2f}%")

    # Budget bar
    bar_width = 50
    used_width = int((budget["percent_used"] / 100) * bar_width)
    bar = "█" * used_width + "░" * (bar_width - used_width)
    lines.append(f"  [{bar}]")

    if budget["is_over_budget"]:
        lines.append("  ⚠️  WARNING: OVER BUDGET!")
    lines.append("")

    # Cost metrics section
    lines.append("COST METRICS".center(70))
    lines.append("-" * 70)
    lines.append(f"  Total Operations:     {costs['operations_count']:>10}")
    lines.append(f"  Avg Cost/Operation:   {costs['avg_cost_per_operation']:>10.4f} Bobcoins")
    lines.append(f"  ROI:                  {costs['roi_percent']:>10.2f}%")
    lines.append(f"  Total Tokens Used:    {costs['total_tokens_used']:>10,}")
    lines.append(f"  Total Tokens Saved:   {costs['total_tokens_saved']:>10,}")
    lines.append("")

    # Cost breakdown
    lines.append("COST BY OPERATION".center(70))
    lines.append("-" * 70)
    for op, cost in sorted(costs["cost_by_operation"].items(), key=lambda x: x[1], reverse=True):
        tokens = costs["tokens_by_operation"].get(op, 0)
        lines.append(f"  {op:<25} {cost:>10.4f} BC  ({tokens:>8,} tokens)")
    lines.append("")

    # Savings breakdown
    if costs["savings_by_source"]:
        lines.append("SAVINGS BY SOURCE".center(70))
        lines.append("-" * 70)
        for source, savings in sorted(
            costs["savings_by_source"].items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"  {source:<25} {savings:>10.4f} BC")
        lines.append("")

    # Rate section
    lines.append("COST RATE".center(70))
    lines.append("-" * 70)
    lines.append(f"  Per Second:       {rate['bobcoins_per_second']:>10.6f} Bobcoins")
    lines.append(f"  Per Minute:       {rate['bobcoins_per_minute']:>10.4f} Bobcoins")
    lines.append(f"  Per Hour:         {rate['bobcoins_per_hour']:>10.2f} Bobcoins")
    lines.append("")

    # Alerts section
    if alerts:
        lines.append("ACTIVE ALERTS".center(70))
        lines.append("-" * 70)
        for alert in alerts:
            triggered_at = alert["triggered_at"] or "N/A"
            lines.append(f"  ⚠️  {alert['threshold_percent']}% threshold exceeded at {triggered_at}")
        lines.append("")

    # Footer
    lines.append("=" * 70)
    lines.append(f"Generated: {summary['timestamp']}")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_cost_report(
    include_breakdown: bool = True, include_trends: bool = False
) -> Dict[str, Any]:
    """
    Generate detailed cost report.

    Args:
        include_breakdown: Include cost breakdown by operation
        include_trends: Include trend analysis (future feature)

    Returns:
        Dictionary with report data
    """
    tracker = get_cost_tracker()
    summary = tracker.get_summary()

    report = {
        "timestamp": summary["timestamp"],
        "summary": {
            "total_spent": summary["budget"]["spent_bobcoins"],
            "total_saved": summary["budget"]["saved_bobcoins"],
            "net_cost": summary["budget"]["net_spent_bobcoins"],
            "roi_percent": summary["costs"]["roi_percent"],
            "operations_count": summary["costs"]["operations_count"],
        },
    }

    if include_breakdown:
        report["breakdown"] = {
            "by_operation": summary["costs"]["cost_by_operation"],
            "by_tokens": summary["costs"]["tokens_by_operation"],
            "savings_by_source": summary["costs"]["savings_by_source"],
        }

    if include_trends:
        # Future: Add trend analysis
        report["trends"] = {"note": "Trend analysis not yet implemented"}

    return report


def export_cost_data(filepath: str, format: str = "json") -> None:
    """
    Export cost data to file.

    Args:
        filepath: Path to export file
        format: Export format (json, csv)
    """
    tracker = get_cost_tracker()
    summary = tracker.get_summary()

    if format == "json":
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)
    elif format == "csv":
        # Future: Implement CSV export
        raise NotImplementedError("CSV export not yet implemented")
    else:
        raise ValueError(f"Unsupported format: {format}")


def get_cost_alerts() -> List[Dict[str, Any]]:
    """
    Get list of active cost alerts.

    Returns:
        List of alert dictionaries
    """
    tracker = get_cost_tracker()
    return tracker.get_active_alerts()


def check_budget_health() -> Dict[str, Any]:
    """
    Check budget health status.

    Returns:
        Dictionary with health status
    """
    tracker = get_cost_tracker()
    budget_status = tracker.get_budget_status()

    percent_used = budget_status["percent_used"]

    if percent_used >= 90:
        status = "critical"
        message = "Budget critically low (>90% used)"
    elif percent_used >= 75:
        status = "warning"
        message = "Budget running low (>75% used)"
    elif percent_used >= 50:
        status = "caution"
        message = "Budget half depleted (>50% used)"
    else:
        status = "healthy"
        message = "Budget healthy (<50% used)"

    return {
        "status": status,
        "message": message,
        "percent_used": percent_used,
        "remaining_bobcoins": budget_status["remaining_bobcoins"],
        "is_over_budget": budget_status["is_over_budget"],
    }


def calculate_projected_costs(operations_per_hour: int, hours: int = 24) -> Dict[str, Any]:
    """
    Calculate projected costs based on current rate.

    Args:
        operations_per_hour: Expected operations per hour
        hours: Number of hours to project

    Returns:
        Dictionary with projections
    """
    tracker = get_cost_tracker()

    # Get average cost per operation
    cost_metrics = tracker.get_cost_metrics()
    avg_cost = cost_metrics["avg_cost_per_operation"]

    # Calculate projections
    total_operations = operations_per_hour * hours
    projected_cost = avg_cost * total_operations

    # Get current budget status
    budget_status = tracker.get_budget_status()
    remaining = budget_status["remaining_bobcoins"]

    return {
        "operations_per_hour": operations_per_hour,
        "hours": hours,
        "total_operations": total_operations,
        "avg_cost_per_operation": avg_cost,
        "projected_cost_bobcoins": round(projected_cost, 4),
        "current_remaining_bobcoins": remaining,
        "will_exceed_budget": projected_cost > remaining,
        "budget_shortfall": max(0, projected_cost - remaining),
    }


def get_top_cost_operations(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get top cost operations.

    Args:
        limit: Number of top operations to return

    Returns:
        List of operation dictionaries sorted by cost
    """
    tracker = get_cost_tracker()
    cost_metrics = tracker.get_cost_metrics()

    operations = []
    for op, cost in cost_metrics["cost_by_operation"].items():
        tokens = cost_metrics["tokens_by_operation"].get(op, 0)
        operations.append({"operation": op, "cost_bobcoins": cost, "tokens": tokens})

    # Sort by cost descending
    operations.sort(key=lambda x: x["cost_bobcoins"], reverse=True)

    return operations[:limit]


def get_savings_summary() -> Dict[str, Any]:
    """
    Get summary of token savings.

    Returns:
        Dictionary with savings summary
    """
    tracker = get_cost_tracker()
    cost_metrics = tracker.get_cost_metrics()

    return {
        "total_tokens_saved": cost_metrics["total_tokens_saved"],
        "total_bobcoins_saved": cost_metrics["total_bobcoins_saved"],
        "roi_percent": cost_metrics["roi_percent"],
        "savings_by_source": cost_metrics["savings_by_source"],
    }


def print_cost_dashboard() -> None:
    """Print cost dashboard to console."""
    dashboard = generate_cost_dashboard()
    print(dashboard)


def print_cost_summary() -> None:
    """Print cost summary to console."""
    summary = generate_cost_summary()
    print(json.dumps(summary, indent=2))
