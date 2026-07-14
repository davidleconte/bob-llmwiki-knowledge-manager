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
    track_costs: Whether to track costs with CostTracker

#### Methods

##### `__init__(model: str, track_costs: bool)`

Initialize token counter.

Args:
    model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
    track_costs: Whether to track costs with CostTracker


##### `count_tokens(text: str) -> int`

Count tokens in text.

Args:
    text: Text to count tokens for

Returns:
    Number of tokens


##### `count_tokens_batch(texts: list[str]) -> list[int]`

Count tokens for a batch of texts.

Convenience wrapper over :meth:`count_tokens` for many texts at once.
Delegates per item so batch and single-count semantics stay identical
(empty-string handling, tiktoken-vs-approximation, cost tracking).

Args:
    texts: Texts to count tokens for.

Returns:
    Per-text token counts, in the same order as ``texts``.


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

Truncate text to fit within a token budget.

Guarantees ``count_tokens(result) <= max_tokens``. With tiktoken the text
is encoded, cut to the budget (reserving room for the "..." marker), then
decoded — so the postcondition holds for *any* text, including multibyte
scripts (emoji/CJK) where a fixed chars-per-token ratio overshoots. The
previous char-count heuristic (``int(max_tokens * 3.5)``) violated the
budget for dense/random text by up to ~2.6x and never fit at all for
``max_tokens <= 0``.

Args:
    text: Text to truncate.
    max_tokens: Maximum tokens allowed. ``<= 0`` yields an empty string
        (nothing fits in a zero budget).

Returns:
    Truncated text — ends with "..." when content was dropped, or the
    original text unchanged when it already fits.


