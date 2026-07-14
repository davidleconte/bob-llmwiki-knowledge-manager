# cost_tracker

Cost tracking module for the Token Optimization System.

Provides Bobcoin cost tracking, budget monitoring, and cost optimization metrics.
Integrates with the existing metrics system to provide comprehensive cost visibility.

## Constants

- `TOKENS_PER_BOBCOIN`
- `DEFAULT_BUDGET_BOBCOINS`

## Functions

### `get_cost_tracker(budget_bobcoins: float) -> CostTracker`

Get global cost tracker instance.

Args:
    budget_bobcoins: Budget in Bobcoins (only used on first call)

Returns:
    CostTracker instance


### `reset_cost_tracker() -> None`

Reset global cost tracker.


### `tokens_to_bobcoins(tokens: int) -> float`

Convert tokens to Bobcoins.

Args:
    tokens: Number of tokens

Returns:
    Equivalent Bobcoins


### `bobcoins_to_tokens(bobcoins: float) -> int`

Convert Bobcoins to tokens.

Args:
    bobcoins: Number of Bobcoins

Returns:
    Equivalent tokens


## Classes

### `CostMetrics`

Metrics for cost tracking.

#### Methods

##### `record_cost(operation: str, tokens_used: int, tokens_saved: int) -> Tuple[float, float]`

Record cost for an operation.

Args:
    operation: Operation type (e.g., "token_counting", "optimization", "cache_hit")
    tokens_used: Number of tokens used
    tokens_saved: Number of tokens saved (if applicable)

Returns:
    Tuple of (bobcoins_spent, bobcoins_saved)


##### `get_net_cost() -> float`

Calculate net cost (spent - saved).


##### `get_roi_percent() -> float`

Calculate ROI percentage.


##### `get_average_cost_per_operation() -> float`

Calculate average cost per operation.


##### `to_dict() -> Dict[str, Any]`

Convert to dictionary.



### `BudgetAlert`

Budget alert configuration and state.

#### Methods

##### `check(spent: float, budget: float) -> bool`

Check if alert should trigger.

Args:
    spent: Amount spent
    budget: Total budget

Returns:
    True if alert should trigger


##### `reset() -> None`

Reset alert state.



### `CostTracker`

Cost tracking system for Bobcoin monitoring and budget management.

Features:
- Real-time cost tracking per operation
- Token-to-Bobcoin conversion
- Budget monitoring with alerts
- ROI calculation
- Cost breakdown by operation type
- Savings tracking by source

Example:
    >>> tracker = CostTracker(budget_bobcoins=100.0)
    >>> tracker.record_token_counting(1500)  # 1.5 Bobcoins
    >>> tracker.record_cache_hit(1000)  # Saved 1.0 Bobcoins
    >>> print(tracker.get_budget_status())
    {'spent': 1.5, 'saved': 1.0, 'remaining': 98.5, 'percent_used': 1.5}

#### Methods

##### `__init__(budget_bobcoins: float, alert_thresholds: Optional[List[float]])`

Initialize cost tracker.

Args:
    budget_bobcoins: Total budget in Bobcoins
    alert_thresholds: List of alert thresholds (e.g., [50, 75, 90])


##### `record_token_counting(tokens: int) -> float`

Record token counting operation cost.

Args:
    tokens: Number of tokens counted

Returns:
    Bobcoins spent


##### `record_optimization(original_tokens: int, optimized_tokens: int) -> Tuple[float, float]`

Record optimization operation cost and savings.

Args:
    original_tokens: Original token count
    optimized_tokens: Optimized token count

Returns:
    Tuple of (bobcoins_spent, bobcoins_saved)


##### `record_cache_hit(tokens_saved: int) -> float`

Record cache hit (pure savings, no cost).

Args:
    tokens_saved: Number of tokens saved by cache hit

Returns:
    Bobcoins saved


##### `record_cache_miss(tokens_used: int) -> float`

Record cache miss (cost with no savings).

Args:
    tokens_used: Number of tokens used

Returns:
    Bobcoins spent


##### `record_truncation(original_tokens: int, truncated_tokens: int) -> Tuple[float, float]`

Record truncation operation cost and savings.

Args:
    original_tokens: Original token count
    truncated_tokens: Truncated token count

Returns:
    Tuple of (bobcoins_spent, bobcoins_saved)


##### `record_custom_operation(operation: str, tokens_used: int, tokens_saved: int) -> Tuple[float, float]`

Record custom operation cost.

Args:
    operation: Operation name
    tokens_used: Number of tokens used
    tokens_saved: Number of tokens saved

Returns:
    Tuple of (bobcoins_spent, bobcoins_saved)


##### `get_budget_status() -> Dict[str, Any]`

Get current budget status.

Returns:
    Dictionary with budget information


##### `get_cost_metrics() -> Dict[str, Any]`

Get detailed cost metrics.

Returns:
    Dictionary with cost metrics


##### `get_cost_rate() -> Dict[str, float]`

Get cost rate (Bobcoins per second).

Returns:
    Dictionary with rate information


##### `get_active_alerts() -> List[Dict[str, Any]]`

Get list of active budget alerts.

Returns:
    List of active alerts


##### `reset_alerts() -> None`

Reset all budget alerts.


##### `set_budget(budget_bobcoins: float) -> None`

Set new budget.

Args:
    budget_bobcoins: New budget in Bobcoins


##### `reset() -> None`

Reset all cost tracking.


##### `get_summary() -> Dict[str, Any]`

Get cost tracking summary.

Returns:
    Dictionary with summary information


