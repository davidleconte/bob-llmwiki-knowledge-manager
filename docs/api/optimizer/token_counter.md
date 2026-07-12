# token_counter

Token counting utilities for prompt optimization.

This module provides accurate token counting for various LLM models,
supporting both tiktoken (OpenAI) and approximate counting methods.

## Classes

### `TokenCounter`

Token counter for LLM prompts.

Provides accurate token counting using tiktoken when available,
with fallback to approximation methods.

Attributes:
    model: Model name for token counting
    encoding: Tiktoken encoding (if available)
    use_tiktoken: Whether tiktoken is available

#### Methods

##### `__init__(model: str)`

Initialize token counter.

Args:
    model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")


##### `count_tokens(text: str) -> int`

Count tokens in text.

Args:
    text: Text to count tokens for
    
Returns:
    Number of tokens


##### `count_messages(messages: list[Dict[str, str]]) -> int`

Count tokens in message list (chat format).

Args:
    messages: List of message dicts with 'role' and 'content'
    
Returns:
    Total token count including message formatting overhead


##### `estimate_cost(tokens: int, model: Optional[str]) -> float`

Estimate cost for token count.

Args:
    tokens: Number of tokens
    model: Model name (uses self.model if not provided)
    
Returns:
    Estimated cost in USD


##### `get_stats(text: str) -> Dict[str, Any]`

Get comprehensive token statistics.

Args:
    text: Text to analyze
    
Returns:
    Dictionary with token statistics


##### `compare_texts(original: str, optimized: str) -> Dict[str, Any]`

Compare token counts between original and optimized text.

Args:
    original: Original text
    optimized: Optimized text
    
Returns:
    Dictionary with comparison statistics


##### `fits_context(text: str, max_tokens: int) -> bool`

Check if text fits within context window.

Args:
    text: Text to check
    max_tokens: Maximum context window size
    
Returns:
    True if text fits, False otherwise


##### `truncate_to_tokens(text: str, max_tokens: int) -> str`

Truncate text to fit within token limit.

Simple truncation by characters, approximating token count.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    
Returns:
    Truncated text


