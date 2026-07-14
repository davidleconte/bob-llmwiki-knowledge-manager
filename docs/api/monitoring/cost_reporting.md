# cost_reporting

Cost reporting utilities for generating dashboards and summaries.

Provides formatted reports, dashboards, and cost analysis tools for
the Token Optimization System's Bobcoin tracking.

## Functions

### `generate_cost_summary() -> Dict[str, Any]`

Generate comprehensive cost summary.

Returns:
    Dictionary with cost summary data


### `generate_cost_dashboard() -> str`

Generate ASCII dashboard for cost tracking.

Returns:
    Formatted dashboard string


### `generate_cost_report(include_breakdown: bool, include_trends: bool) -> Dict[str, Any]`

Generate detailed cost report.

Args:
    include_breakdown: Include cost breakdown by operation
    include_trends: Include trend analysis (future feature)

Returns:
    Dictionary with report data


### `export_cost_data(filepath: str, format: str) -> None`

Export cost data to file.

Args:
    filepath: Path to export file
    format: Export format (json, csv)


### `get_cost_alerts() -> List[Dict[str, Any]]`

Get list of active cost alerts.

Returns:
    List of alert dictionaries


### `check_budget_health() -> Dict[str, Any]`

Check budget health status.

Returns:
    Dictionary with health status


### `calculate_projected_costs(operations_per_hour: int, hours: int) -> Dict[str, Any]`

Calculate projected costs based on current rate.

Args:
    operations_per_hour: Expected operations per hour
    hours: Number of hours to project

Returns:
    Dictionary with projections


### `get_top_cost_operations(limit: int) -> List[Dict[str, Any]]`

Get top cost operations.

Args:
    limit: Number of top operations to return

Returns:
    List of operation dictionaries sorted by cost


### `get_savings_summary() -> Dict[str, Any]`

Get summary of token savings.

Returns:
    Dictionary with savings summary


### `print_cost_dashboard() -> None`

Print cost dashboard to console.


### `print_cost_summary() -> None`

Print cost summary to console.

