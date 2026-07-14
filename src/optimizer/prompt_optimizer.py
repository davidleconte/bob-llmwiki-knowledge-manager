"""Prompt optimizer for token reduction and quality preservation.

Implements near-lossless prompt compression (whitespace normalization +
redundant-phrase removal) with a lexical quality heuristic, integrated with the
multi-level cache.

Savings are **measured**, not asserted here: the Phase-5 harness
(``python -m src.validation``) reports the manifest-backed compression figure
over a real corpus. See ``evaluation/results/validation-<date>/`` for the
current run; earlier hard-coded "89.3% / 91.80%" claims were fabricated and are
retracted.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.cache.exact_cache import ExactCache
    from src.config.schema import OptimizerConfig
import re
import time

from src.monitoring import get_logger, get_metrics_collector
from src.optimizer.token_counter import TokenCounter
from src.pricing import DEFAULT_MODEL


class PromptOptimizer:
    """Optimize prompts for token efficiency while preserving quality.

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
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: Optional[int] = None,
        target_reduction: float = 0.3,
        min_quality_score: float = 0.8,
        use_cache: bool = True,
        track_costs: bool = False,
        *,
        cache: Optional["ExactCache"] = None,
        target_savings: Optional[float] = None,
        min_quality: Optional[float] = None,
    ):
        """Initialize prompt optimizer.

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
        """
        # Reconcile deprecated pre-Phase-4 aliases with the canonical config names.
        if target_savings is not None:
            target_reduction = target_savings
        if min_quality is not None:
            min_quality_score = min_quality

        self.token_counter = TokenCounter(model=model, track_costs=track_costs)
        # Use only L1 (exact) cache to avoid semantic matches returning a wrong
        # prompt's optimization. When an ExactCache is injected (by the facade,
        # built from config.cache.l1), share it so config-driven sizing/TTL
        # governs this path and the facade's cache is not a second, disjoint L1.
        self.cache: Optional["ExactCache"] = None
        if use_cache:
            if cache is not None:
                self.cache = cache
            else:
                from src.cache.exact_cache import ExactCache

                self.cache = ExactCache(max_size=1000, track_costs=track_costs)
        self.max_tokens = max_tokens
        self.target_reduction = target_reduction
        self.min_quality_score = min_quality_score
        self.track_costs = track_costs

        # Statistics
        self.optimizations_count = 0
        self.total_tokens_saved = 0
        self.total_original_tokens = 0

        # Initialize monitoring
        self._logger = get_logger("optimizer.prompt")
        self._metrics = get_metrics_collector()

        # Initialize cost tracker if enabled
        self._cost_tracker = None
        if self.track_costs:
            try:
                from src.monitoring.cost_tracker import get_cost_tracker

                self._cost_tracker = get_cost_tracker()
            except ImportError:
                self.track_costs = False

        self._logger.info(
            "prompt_optimizer_initialized",
            model=model,
            max_tokens=max_tokens,
            target_reduction=target_reduction,
            min_quality_score=min_quality_score,
            use_cache=use_cache,
            track_costs=track_costs,
        )

    @classmethod
    def from_config(
        cls,
        config: "OptimizerConfig",
        *,
        model: str = DEFAULT_MODEL,
        use_cache: bool = True,
        track_costs: bool = False,
        cache: Optional["ExactCache"] = None,
    ) -> "PromptOptimizer":
        """Build an optimizer from an :class:`~src.config.schema.OptimizerConfig`.

        The canonical config->runtime path: the config's ``max_tokens``,
        ``target_reduction`` and ``min_quality_score`` map 1:1 onto the
        constructor. ``model``/``use_cache``/``track_costs``/``cache`` are not
        part of ``OptimizerConfig`` and are passed separately; ``cache`` lets the
        facade share its config-built L1 (see :meth:`__init__`).
        """
        return cls(
            model=model,
            max_tokens=config.max_tokens,
            target_reduction=config.target_reduction,
            min_quality_score=config.min_quality_score,
            use_cache=use_cache,
            track_costs=track_costs,
            cache=cache,
        )

    @property
    def target_savings(self) -> float:
        """Deprecated alias for :attr:`target_reduction` (fraction of tokens saved)."""
        return self.target_reduction

    @property
    def min_quality(self) -> float:
        """Deprecated alias for :attr:`min_quality_score`."""
        return self.min_quality_score

    def optimize(
        self, prompt: str, max_tokens: Optional[int] = None, preserve_structure: bool = True
    ) -> Dict[str, Any]:
        """Optimize prompt for token efficiency.

        Args:
            prompt: Original prompt text
            max_tokens: Maximum tokens allowed (optional)
            preserve_structure: Whether to preserve text structure

        Returns:
            Dictionary with optimized prompt and statistics
        """
        start_time = time.time()

        # Check cache first
        if self.cache:
            cached = self.cache.get(prompt)
            if cached is not None:
                entry = self.cache.get_entry(prompt)
                self._logger.debug("optimization_cache_hit", prompt_length=len(prompt))
                return self._parse_cached_result(cached, entry.metadata if entry else None)

        # Count original tokens
        original_tokens = self.token_counter.count_tokens(prompt)

        # Apply optimization strategies
        optimized = prompt
        optimized = self._normalize_whitespace(optimized, preserve_structure)
        optimized = self._remove_redundancy(optimized)
        optimized = self._compress_content(optimized, preserve_structure)

        # Apply token limit: a per-call max_tokens overrides the instance default
        # (self.max_tokens, set from config); otherwise fall back to that default.
        effective_max = max_tokens if max_tokens is not None else self.max_tokens
        if effective_max:
            optimized = self._truncate_to_limit(optimized, effective_max)

        # Count optimized tokens
        optimized_tokens = self.token_counter.count_tokens(optimized)

        # Calculate metrics
        tokens_saved = original_tokens - optimized_tokens
        savings_pct = (tokens_saved / original_tokens) if original_tokens > 0 else 0
        quality = self._estimate_quality(prompt, optimized)
        latency_ms = (time.time() - start_time) * 1000

        # Update statistics
        self.optimizations_count += 1
        self.total_tokens_saved += tokens_saved
        self.total_original_tokens += original_tokens

        # Record metrics
        self._metrics.record_optimization(original_tokens, optimized_tokens, latency_ms)

        # Log optimization
        self._logger.info(
            "optimization_complete",
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            tokens_saved=tokens_saved,
            savings_pct=savings_pct * 100,
            quality_score=quality,
            latency_ms=latency_ms,
            meets_target=savings_pct >= self.target_savings and quality >= self.min_quality,
        )

        # Track optimization cost if enabled
        if self.track_costs and self._cost_tracker:
            self._cost_tracker.record_optimization(original_tokens, optimized_tokens)

        result = {
            "original": prompt,
            "optimized": optimized,
            # "optimized_text" is the canonical key used by the config-integration
            # tests and the Phase-4 facade; "optimized" is kept for back-compat.
            "optimized_text": optimized,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "savings_percentage": savings_pct * 100,
            "quality_score": quality,
            "meets_target": savings_pct >= self.target_savings and quality >= self.min_quality,
        }

        # Cache result
        if self.cache:
            self._cache_result(prompt, result)

        return result

    def _normalize_whitespace(self, text: str, preserve_structure: bool = True) -> str:
        """Normalize whitespace for token efficiency.

        Args:
            text: Text to normalize
            preserve_structure: Whether to preserve line breaks

        Returns:
            Normalized text
        """
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        if preserve_structure:
            # Replace multiple newlines with double newline
            text = re.sub(r"\n\n+", "\n\n", text)

            # Remove trailing whitespace from lines
            text = "\n".join(line.rstrip() for line in text.splitlines())
        else:
            # Replace all newlines with spaces for aggressive compression
            text = re.sub(r"\n+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant content.

        Args:
            text: Text to process

        Returns:
            Text with redundancy removed
        """
        # Remove repeated phrases (3+ words)
        words = text.split()
        seen_phrases = set()
        result = []

        i = 0
        while i < len(words):
            # Check for repeated 3-word phrases
            if i + 2 < len(words):
                phrase = " ".join(words[i : i + 3])
                if phrase.lower() not in seen_phrases:
                    seen_phrases.add(phrase.lower())
                    result.append(words[i])
                    i += 1
                else:
                    # Skip repeated phrase
                    i += 3
            else:
                result.append(words[i])
                i += 1

        return " ".join(result)

    def _compress_content(self, text: str, preserve_structure: bool) -> str:
        """Compress content while preserving meaning.

        Args:
            text: Text to compress
            preserve_structure: Whether to preserve structure

        Returns:
            Compressed text
        """
        if not preserve_structure:
            # Aggressive compression
            text = self._remove_filler_words(text)
            text = self._abbreviate_common_phrases(text)

        # Remove unnecessary punctuation
        text = re.sub(r"[,;:]\s*([,;:])", r"\1", text)

        # Compress multiple punctuation
        text = re.sub(r"([.!?])\1+", r"\1", text)

        return text

    def _remove_filler_words(self, text: str) -> str:
        """Remove filler words that don't add meaning.

        Args:
            text: Text to process

        Returns:
            Text without filler words
        """
        filler_words = {
            "actually",
            "basically",
            "essentially",
            "literally",
            "really",
            "very",
            "quite",
            "rather",
            "somewhat",
            "just",
            "simply",
            "merely",
            "only",
        }

        words = text.split()
        filtered = [w for w in words if w.lower() not in filler_words]

        return " ".join(filtered)

    def _abbreviate_common_phrases(self, text: str) -> str:
        """Abbreviate common phrases.

        Args:
            text: Text to process

        Returns:
            Text with abbreviations
        """
        abbreviations = {
            "for example": "e.g.",
            "that is": "i.e.",
            "and so on": "etc.",
            "as soon as possible": "ASAP",
        }

        for phrase, abbr in abbreviations.items():
            text = re.sub(r"\b" + phrase + r"\b", abbr, text, flags=re.IGNORECASE)

        return text

    def _truncate_to_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens

        Returns:
            Truncated text
        """
        current_tokens = self.token_counter.count_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # Binary search for optimal truncation point
        lines = text.splitlines()
        left, right = 0, len(lines)

        while left < right:
            mid = (left + right + 1) // 2
            truncated = "\n".join(lines[:mid])

            if self.token_counter.count_tokens(truncated) <= max_tokens:
                left = mid
            else:
                right = mid - 1

        return "\n".join(lines[:left])

    def _estimate_quality(self, original: str, optimized: str) -> float:
        """Estimate quality preservation.

        Uses multiple heuristics:
        - Length ratio
        - Word overlap
        - Structure preservation

        Args:
            original: Original text
            optimized: Optimized text

        Returns:
            Quality score (0-1)
        """
        # Length ratio (should be reasonable)
        length_ratio = len(optimized) / len(original) if len(original) > 0 else 0
        length_score = min(1.0, length_ratio * 1.5)  # Penalize too much compression

        # Word overlap
        original_words = set(original.lower().split())
        optimized_words = set(optimized.lower().split())

        if len(original_words) > 0:
            overlap = len(original_words & optimized_words) / len(original_words)
        else:
            overlap = 1.0

        # Structure preservation (line count ratio)
        original_lines = len(original.splitlines())
        optimized_lines = len(optimized.splitlines())

        if original_lines > 0:
            structure_score = min(1.0, optimized_lines / original_lines)
        else:
            structure_score = 1.0

        # Weighted average
        quality = length_score * 0.3 + overlap * 0.5 + structure_score * 0.2

        return quality

    def _cache_result(self, prompt: str, result: Dict[str, Any]) -> None:
        """Cache optimization result.

        Args:
            prompt: Original prompt
            result: Optimization result
        """
        if not self.cache:
            return

        # Store optimized prompt with metadata
        metadata = {
            "original_tokens": result["original_tokens"],
            "optimized_tokens": result["optimized_tokens"],
            "quality_score": result["quality_score"],
        }

        # Pass metadata as a keyword arg: ExactCache.set()'s third positional
        # parameter is ``version`` -- passing metadata there corrupts the cache
        # key so set()/get() never agree (a write-only cache that never hits).
        self.cache.set(prompt, result["optimized"], metadata=metadata)

    def _parse_cached_result(
        self, cached: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse a cache hit into the standard result format.

        Restores the token/quality metadata stored alongside the cached
        response so savings tracking stays meaningful on cache hits. Falls back
        to recounting tokens when metadata is unavailable.

        Args:
            cached: Cached optimized prompt (the stored response).
            metadata: Metadata stored with the cache entry, if any.

        Returns:
            Result dictionary with ``from_cache`` set to True.
        """
        metadata = metadata or {}

        optimized_tokens = metadata.get("optimized_tokens")
        if optimized_tokens is None:
            optimized_tokens = self.token_counter.count_tokens(cached)
        original_tokens = metadata.get("original_tokens")
        quality = metadata.get("quality_score")

        tokens_saved = None
        savings_pct = None
        if original_tokens is not None and optimized_tokens is not None:
            tokens_saved = original_tokens - optimized_tokens
            savings_pct = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0.0

        return {
            "original": None,  # original prompt is not stored in the cache
            "optimized": cached,
            "optimized_text": cached,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "savings_percentage": savings_pct,
            "quality_score": quality,
            "meets_target": None,
            "from_cache": True,
        }

    def optimize_batch(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Optimize multiple prompts.

        Args:
            prompts: List of prompts to optimize

        Returns:
            List of optimization results
        """
        return [self.optimize(prompt) for prompt in prompts]

    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics.

        Returns:
            Dictionary with statistics
        """
        avg_savings = (
            (self.total_tokens_saved / self.total_original_tokens * 100)
            if self.total_original_tokens > 0
            else 0
        )

        return {
            "optimizations_count": self.optimizations_count,
            "total_tokens_saved": self.total_tokens_saved,
            "total_original_tokens": self.total_original_tokens,
            "average_savings_percentage": avg_savings,
            "target_savings": self.target_savings * 100,
            "min_quality": self.min_quality * 100,
            "cache_enabled": self.cache is not None,
            "cache_stats": self.cache.stats() if self.cache else None,
        }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.optimizations_count = 0
        self.total_tokens_saved = 0
        self.total_original_tokens = 0

        if self.cache:
            self.cache.reset_stats()
