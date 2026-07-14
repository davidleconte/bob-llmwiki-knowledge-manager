# strategies

Truncation strategies for prompt optimization.

This module provides various strategies for truncating prompts
while preserving quality and meaning.

## Classes

### `TruncationStrategy(ABC)`

Base class for truncation strategies.

#### Methods

##### `truncate(text: str, max_tokens: int, token_counter) -> str`

Truncate text to fit within token limit.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    token_counter: TokenCounter instance

Returns:
    Truncated text


##### `get_name() -> str`

Get strategy name.



### `SimpleTruncationStrategy(TruncationStrategy)`

Simple truncation by character count.

Truncates text at approximate character position based on
token-to-character ratio. Fast but may cut mid-sentence.

#### Methods

##### `truncate(text: str, max_tokens: int, token_counter) -> str`

Truncate text to a token-accurate prefix with an ellipsis marker.

Uses the token counter directly (binary search) so the result never
exceeds ``max_tokens``. A fixed chars-per-token ratio undershoots for
multibyte/CJK text and overshoots the budget.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    token_counter: TokenCounter instance

Returns:
    Truncated text whose token count is <= ``max_tokens``


##### `get_name() -> str`

Get strategy name.



### `PriorityTruncationStrategy(TruncationStrategy)`

Priority-based truncation preserving important sections.

Identifies and preserves high-priority content:
- Headers and titles
- First and last paragraphs
- Numbered/bulleted lists
- Code blocks

#### Methods

##### `__init__(preserve_headers: bool, preserve_first_last: bool)`

Initialize priority truncation strategy.

Args:
    preserve_headers: Whether to preserve headers
    preserve_first_last: Whether to preserve first/last paragraphs


##### `truncate(text: str, max_tokens: int, token_counter) -> str`

Truncate text preserving high-priority sections.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    token_counter: TokenCounter instance

Returns:
    Truncated text


##### `get_name() -> str`

Get strategy name.



### `SemanticTruncationStrategy(TruncationStrategy)`

Semantic-aware truncation preserving meaning.

Truncates at sentence boundaries and preserves semantic coherence.

#### Methods

##### `truncate(text: str, max_tokens: int, token_counter) -> str`

Truncate text at sentence boundaries.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    token_counter: TokenCounter instance

Returns:
    Truncated text


##### `get_name() -> str`

Get strategy name.



### `SlidingWindowStrategy(TruncationStrategy)`

Sliding window truncation for context preservation.

Maintains a sliding window of recent content, useful for
conversational contexts where recent information is most relevant.

#### Methods

##### `__init__(window_overlap: float)`

Initialize sliding window strategy.

Args:
    window_overlap: Overlap ratio between windows (0-1)


##### `truncate(text: str, max_tokens: int, token_counter) -> str`

Truncate text using sliding window.

Args:
    text: Text to truncate
    max_tokens: Maximum tokens allowed
    token_counter: TokenCounter instance

Returns:
    Truncated text (most recent content)


##### `get_name() -> str`

Get strategy name.


