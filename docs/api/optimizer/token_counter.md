# token_counter

Token counting utilities for prompt optimization.

Model-aware counting via a multi-backend resolver (B1/CODE-10):

- ``gpt*`` / ``o1*`` / legacy OpenAI ids  -> tiktoken (exact)
- ``claude*``                             -> Anthropic backend if installed, else approx
- ``granite*`` / ``watsonx*`` / ``ibm*``  -> HF/Granite tokenizer if installed, else approx
- anything else                           -> approximation

An unavailable *exact* tokenizer NEVER raises on the hot path (availability is
deployment-dependent) but is **loud**: exactly one ``logging.warning`` per
``(process, model)``, and ``TokenCounter.approximate`` is set so no *published*
number silently rides on an approximation (the validation manifest's
``tiktoken_active`` gate already blocks a run whose counts are not exact).

## Constants

- `_OPENAI_PREFIXES`

## Functions

### `_approximate_token_count(text: str) -> int`

Model-blind heuristic: words + special_chars // 2 (~±15% of exact).


### `_resolve_openai(model: str) -> Optional[Tokenizer]`


### `_resolve_granite(model: str) -> Optional[Tokenizer]`


### `resolve_tokenizer(model: str) -> Tokenizer`

Resolve a :class:`Tokenizer` for *model* by family; never raises.

An unavailable exact backend degrades to a loud approximation: exactly one
``logging.warning`` per ``(process, model)`` and an ``exact=False`` tokenizer.


## Classes

### `Tokenizer(Protocol)`

A resolved counting backend for one model.

``exact`` is True only when the count comes from the model's real tokenizer;
``False`` marks the loud approximation path.

#### Methods

##### `count(text: str) -> int`



### `_TiktokenTokenizer`

Exact OpenAI BPE via tiktoken. Exposes ``encoding`` for accurate truncation.

#### Methods

##### `__init__(encoding: Any, name: str) -> None`


##### `count(text: str) -> int`



### `_CallableTokenizer`

Exact count from an external callable (e.g. a HF/Granite ``encode``).

#### Methods

##### `__init__(count_fn: Any, name: str) -> None`


##### `count(text: str) -> int`



### `_ApproxTokenizer`

Model-blind heuristic backend (``exact=False``) — the loud fallback.

#### Methods

##### `__init__(name: str) -> None`


##### `count(text: str) -> int`



### `TokenCounter`

Token counter for LLM prompts.

Provides accurate token counting using tiktoken when available,
with fallback to approximation methods.

Attributes:
    model: Model name for token counting
    tokenizer: Resolved counting backend (:class:`Tokenizer`)
    approximate: True when counts are a heuristic (not the model's tokenizer)
    encoding: Tiktoken encoding (only when the backend is tiktoken)
    use_tiktoken: Whether the exact tiktoken backend is in effect
    track_costs: Whether to track costs with CostTracker

#### Methods

##### `__init__(model: str, track_costs: bool)`

Initialize token counter.

Args:
    model: Model name (e.g., "gpt-4", "claude-sonnet-5", "granite-3-8b")
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


##### `estimate_cost(tokens: int, model: Optional[str]) -> Optional[float]`

Estimate the input-token cost for a token count.

Delegates to the single pricing source (:func:`src.pricing.usd_cost`),
pricing *tokens* as input tokens. An unpriced model is **loud, not silent**
(B2/CODE-10): one warning per (process, model) and ``None`` — the cost is
genuinely unknown, never a default-rate guess.

Args:
    tokens: Number of tokens (priced as input tokens).
    model: Model name (uses self.model if not provided).

Returns:
    Estimated USD cost, or ``None`` when the model has no price.


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


