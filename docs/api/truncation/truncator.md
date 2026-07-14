# truncator

Truncator for applying truncation strategies.

This module provides a unified interface for applying different
truncation strategies to prompts.

## Classes

### `Truncator`

Unified interface for prompt truncation.

Supports multiple truncation strategies and provides
statistics on truncation operations.

Attributes:
    token_counter: Token counting utility
    default_strategy: Default truncation strategy
    strategies: Available truncation strategies

#### Methods

##### `__init__(model: str, default_strategy: str)`

Initialize truncator.

Args:
    model: Model name for token counting
    default_strategy: Default strategy name


##### `truncate(text: str, max_tokens: int, strategy: Optional[str]) -> Dict[str, Any]`

Truncate text using specified strategy.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    strategy: Strategy name (uses default if not specified)

Returns:
    Dictionary with truncation results


##### `add_strategy(name: str, strategy: TruncationStrategy) -> None`

Add custom truncation strategy.

Args:
    name: Strategy name
    strategy: TruncationStrategy instance


##### `get_strategies() -> list[str]`

Get list of available strategy names.

Returns:
    List of strategy names


##### `set_default_strategy(strategy: str) -> None`

Set default truncation strategy.

Args:
    strategy: Strategy name


##### `get_stats() -> Dict[str, Any]`

Get truncation statistics.

Returns:
    Dictionary with statistics


##### `reset_stats() -> None`

Reset statistics counters.


##### `compare_strategies(text: str, max_tokens: int) -> Dict[str, Dict[str, Any]]`

Compare all strategies on given text.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed

Returns:
    Dictionary mapping strategy names to results


##### `auto_select_strategy(text: str, max_tokens: int) -> str`

Automatically select best strategy for text.

Args:
    text: Text to analyze
    max_tokens: Maximum tokens allowed

Returns:
    Recommended strategy name


