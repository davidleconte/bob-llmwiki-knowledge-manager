"""Truncator for applying truncation strategies.

This module provides a unified interface for applying different
truncation strategies to prompts.
"""

import re
import time
from typing import Any, Dict, Optional

from src.monitoring import get_logger, get_metrics_collector
from src.optimizer.token_counter import TokenCounter
from src.pricing import DEFAULT_MODEL
from src.truncation.strategies import (
    PriorityTruncationStrategy,
    SemanticTruncationStrategy,
    SimpleTruncationStrategy,
    SlidingWindowStrategy,
    TruncationStrategy,
)


class Truncator:
    """Unified interface for prompt truncation.

    Supports multiple truncation strategies and provides
    statistics on truncation operations.

    Attributes:
        token_counter: Token counting utility
        default_strategy: Default truncation strategy
        strategies: Available truncation strategies
    """

    def __init__(self, model: str = DEFAULT_MODEL, default_strategy: str = "semantic"):
        """Initialize truncator.

        Args:
            model: Model name for token counting
            default_strategy: Default strategy name
        """
        self.token_counter = TokenCounter(model=model)

        # Initialize strategies
        self.strategies: Dict[str, TruncationStrategy] = {
            "simple": SimpleTruncationStrategy(),
            "priority": PriorityTruncationStrategy(),
            "semantic": SemanticTruncationStrategy(),
            "sliding_window": SlidingWindowStrategy(),
        }

        self.default_strategy = default_strategy

        # Initialize monitoring
        self._logger = get_logger("truncation.truncator")
        self._metrics = get_metrics_collector()

        # Statistics
        self.truncations_count = 0
        self.total_tokens_removed = 0
        self.total_original_tokens = 0

        self._logger.info(
            "truncator_initialized",
            model=model,
            default_strategy=default_strategy,
            available_strategies=list(self.strategies.keys()),
        )

    def truncate(
        self, text: str, max_tokens: int, strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Truncate text using specified strategy.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            strategy: Strategy name (uses default if not specified)

        Returns:
            Dictionary with truncation results
        """
        start_time = time.time()
        strategy_name = strategy or self.default_strategy

        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # Count original tokens
        original_tokens = self.token_counter.count_tokens(text)

        # Check if truncation needed
        if original_tokens <= max_tokens:
            self._logger.debug(
                "truncation_skipped",
                original_tokens=original_tokens,
                max_tokens=max_tokens,
                strategy=strategy_name,
            )
            return {
                "original": text,
                "truncated": text,
                "original_tokens": original_tokens,
                "truncated_tokens": original_tokens,
                "tokens_removed": 0,
                "was_truncated": False,
                "strategy": strategy_name,
            }

        # Apply truncation
        truncation_strategy = self.strategies[strategy_name]
        truncated = truncation_strategy.truncate(text, max_tokens, self.token_counter)

        # Count truncated tokens
        truncated_tokens = self.token_counter.count_tokens(truncated)

        # Enforce the hard invariant: never exceed the token budget, regardless
        # of which strategy ran (a strategy may overshoot on unusual input).
        if truncated_tokens > max_tokens:
            truncated = SimpleTruncationStrategy().truncate(
                truncated, max_tokens, self.token_counter
            )
            truncated_tokens = self.token_counter.count_tokens(truncated)
        tokens_removed = original_tokens - truncated_tokens
        latency_ms = (time.time() - start_time) * 1000

        # Update statistics
        self.truncations_count += 1
        self.total_tokens_removed += tokens_removed
        self.total_original_tokens += original_tokens

        # Record metrics
        self._metrics.record_truncation(
            strategy_name, original_tokens, truncated_tokens, latency_ms
        )

        # Log truncation
        self._logger.info(
            "truncation_complete",
            strategy=strategy_name,
            original_tokens=original_tokens,
            truncated_tokens=truncated_tokens,
            tokens_removed=tokens_removed,
            reduction_pct=(tokens_removed / original_tokens * 100) if original_tokens > 0 else 0,
            latency_ms=latency_ms,
        )

        return {
            "original": text,
            "truncated": truncated,
            "original_tokens": original_tokens,
            "truncated_tokens": truncated_tokens,
            "tokens_removed": tokens_removed,
            "removal_percentage": (tokens_removed / original_tokens * 100)
            if original_tokens > 0
            else 0,
            "was_truncated": True,
            "strategy": strategy_name,
        }

    def add_strategy(self, name: str, strategy: TruncationStrategy) -> None:
        """Add custom truncation strategy.

        Args:
            name: Strategy name
            strategy: TruncationStrategy instance
        """
        self.strategies[name] = strategy

    def get_strategies(self) -> list[str]:
        """Get list of available strategy names.

        Returns:
            List of strategy names
        """
        return list(self.strategies.keys())

    def set_default_strategy(self, strategy: str) -> None:
        """Set default truncation strategy.

        Args:
            strategy: Strategy name
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        self.default_strategy = strategy

    def get_stats(self) -> Dict[str, Any]:
        """Get truncation statistics.

        Returns:
            Dictionary with statistics
        """
        avg_removal = (
            (self.total_tokens_removed / self.total_original_tokens * 100)
            if self.total_original_tokens > 0
            else 0
        )

        return {
            "truncations_count": self.truncations_count,
            "total_tokens_removed": self.total_tokens_removed,
            "total_original_tokens": self.total_original_tokens,
            "average_removal_percentage": avg_removal,
            "default_strategy": self.default_strategy,
            "available_strategies": self.get_strategies(),
        }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.truncations_count = 0
        self.total_tokens_removed = 0
        self.total_original_tokens = 0

    def compare_strategies(self, text: str, max_tokens: int) -> Dict[str, Dict[str, Any]]:
        """Compare all strategies on given text.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Dictionary mapping strategy names to results
        """
        results = {}

        for strategy_name in self.strategies.keys():
            result = self.truncate(text, max_tokens, strategy=strategy_name)
            results[strategy_name] = result

        return results

    def auto_select_strategy(self, text: str, max_tokens: int) -> str:
        """Automatically select best strategy for text.

        Args:
            text: Text to analyze
            max_tokens: Maximum tokens allowed

        Returns:
            Recommended strategy name
        """
        # Heuristics for strategy selection

        # Check for structured content (headers, lists)
        has_headers = bool(re.search(r"^#+\s", text, re.MULTILINE))
        has_lists = bool(re.search(r"^[\*\-]\s|\d+[\.\)]\s", text, re.MULTILINE))

        if has_headers or has_lists:
            return "priority"

        # Check for conversational/sequential content
        lines = text.splitlines()
        if len(lines) > 20:
            return "sliding_window"

        # Check for prose/paragraphs
        paragraphs = text.split("\n\n")
        if len(paragraphs) > 3:
            return "semantic"

        # Default to simple for short/unstructured text
        return "simple"
