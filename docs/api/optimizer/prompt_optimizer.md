# prompt_optimizer

Prompt optimizer for token reduction and quality preservation.

Implements near-lossless prompt compression (whitespace normalization +
redundant-phrase removal) with a lexical quality heuristic, integrated with the
multi-level cache.

Savings are **measured**, not asserted here: the Phase-5 harness
(``python -m src.validation``) reports the manifest-backed compression figure
over a real corpus. See ``evaluation/results/validation-<date>/`` for the
current run; earlier hard-coded "89.3% / 91.80%" claims were fabricated and are
retracted.

## Classes

### `PromptOptimizer`

Optimize prompts for token efficiency while preserving quality.

Implements multiple optimization strategies:
- Whitespace normalization
- Redundancy removal
- Content prioritization
- Semantic compression

Attributes:
    token_counter: Token counting utility
    cache: Exact (L1) cache for optimized prompts
    max_tokens: Optional default cap on optimized-output tokens (from config)
    target_reduction: Target fraction of tokens to remove
    min_quality_score: Minimum quality threshold

#### Methods

##### `__init__(model: str, max_tokens: Optional[int], target_reduction: float, min_quality_score: float, use_cache: bool, track_costs: bool)`

Initialize prompt optimizer.

Tunables use the canonical ``OptimizerConfig`` field names
(``max_tokens``, ``target_reduction``, ``min_quality_score``) so a config
object wires straight through -- see :meth:`from_config`.

Args:
    model: Model name for token counting.
    max_tokens: Optional hard cap on optimized-output tokens; when set it
        applies on every ``optimize()`` call (a per-call ``max_tokens``
        still overrides it). ``None`` means no default cap.
    target_reduction: Target fraction of tokens to remove (0-1); drives
        the ``meets_target`` flag.
    min_quality_score: Minimum quality score to treat the optimization as
        on-target (0-1).
    use_cache: Whether to use caching.
    track_costs: Whether to track costs with CostTracker.
    cache: Optional pre-built L1 :class:`~src.cache.exact_cache.ExactCache`
        to use instead of constructing a default one. The facade injects
        its ``MultiLevelCache``'s L1 here so ``config.cache.l1`` (size/TTL)
        actually governs the optimize() cache and the two are one shared
        instance rather than disjoint. Ignored when ``use_cache`` is False.
    target_savings: Deprecated alias for ``target_reduction`` (same
        concept: fraction of tokens saved). Overrides it if given.
    min_quality: Deprecated alias for ``min_quality_score``.


##### `from_config(cls, config: 'OptimizerConfig') -> 'PromptOptimizer'`

Build an optimizer from an :class:`~src.config.schema.OptimizerConfig`.

The canonical config->runtime path: the config's ``max_tokens``,
``target_reduction`` and ``min_quality_score`` map 1:1 onto the
constructor. ``model``/``use_cache``/``track_costs``/``cache`` are not
part of ``OptimizerConfig`` and are passed separately; ``cache`` lets the
facade share its config-built L1 (see :meth:`__init__`).


##### `target_savings() -> float`

Deprecated alias for :attr:`target_reduction` (fraction of tokens saved).


##### `min_quality() -> float`

Deprecated alias for :attr:`min_quality_score`.


##### `optimize(prompt: str, max_tokens: Optional[int], preserve_structure: bool) -> Dict[str, Any]`

Optimize prompt for token efficiency.

Args:
    prompt: Original prompt text
    max_tokens: Maximum tokens allowed (optional)
    preserve_structure: Whether to preserve text structure

Returns:
    Dictionary with optimized prompt and statistics


##### `optimize_batch(prompts: List[str]) -> List[Dict[str, Any]]`

Optimize multiple prompts.

Args:
    prompts: List of prompts to optimize

Returns:
    List of optimization results


##### `get_stats() -> Dict[str, Any]`

Get optimizer statistics.

Returns:
    Dictionary with statistics


##### `reset_stats() -> None`

Reset statistics counters.


