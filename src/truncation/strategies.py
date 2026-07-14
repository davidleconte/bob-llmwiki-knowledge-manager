"""Truncation strategies for prompt optimization.

This module provides various strategies for truncating prompts
while preserving quality and meaning.
"""

import re
from abc import ABC, abstractmethod
from typing import List


class TruncationStrategy(ABC):
    """Base class for truncation strategies."""

    @abstractmethod
    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            token_counter: TokenCounter instance

        Returns:
            Truncated text
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass

    # --- shared budget helpers (inherited by every strategy) -------------- #
    def _token_safe_prefix(self, text: str, max_tokens: int, token_counter) -> str:
        """Longest character prefix of ``text`` with token count <= ``max_tokens``.

        Binary search on the character index using the real token counter, so the
        invariant holds for any tokenizer (including multibyte text).
        """
        if max_tokens <= 0:
            return ""
        lo, hi, best = 0, len(text), 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if token_counter.count_tokens(text[:mid]) <= max_tokens:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return text[:best]

    def _enforce_budget(self, text: str, max_tokens: int, token_counter) -> str:
        """Final guarantee that assembled output honours ``max_tokens``.

        Strategies that reassemble pieces (priority/semantic/sliding-window) sum
        the per-piece token counts, which omits the separators (and any marker)
        added when the pieces are joined -- so the assembled string can exceed the
        budget by a few tokens even though each piece was counted. Any residual
        overshoot is trimmed here with a token-accurate prefix, so every strategy
        honours ``count_tokens(out) <= max_tokens``.
        """
        if token_counter.count_tokens(text) <= max_tokens:
            return text
        return self._token_safe_prefix(text, max_tokens, token_counter)


class SimpleTruncationStrategy(TruncationStrategy):
    """Simple truncation by character count.

    Truncates text at approximate character position based on
    token-to-character ratio. Fast but may cut mid-sentence.
    """

    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text to a token-accurate prefix with an ellipsis marker.

        Uses the token counter directly (binary search) so the result never
        exceeds ``max_tokens``. A fixed chars-per-token ratio undershoots for
        multibyte/CJK text and overshoots the budget.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            token_counter: TokenCounter instance

        Returns:
            Truncated text whose token count is <= ``max_tokens``
        """
        current_tokens = token_counter.count_tokens(text)

        if current_tokens <= max_tokens:
            return text

        if max_tokens <= 0:
            return ""

        ellipsis = "..."
        ellipsis_tokens = token_counter.count_tokens(ellipsis)

        # Reserve room for the ellipsis marker when it fits, then verify the
        # combined result stays within budget (BPE can merge across the join).
        if ellipsis_tokens < max_tokens:
            prefix = self._token_safe_prefix(text, max_tokens - ellipsis_tokens, token_counter)
            candidate = (prefix + ellipsis) if prefix else ellipsis
            if token_counter.count_tokens(candidate) <= max_tokens:
                return candidate

        # Fall back to using the full budget for content (no marker).
        return self._token_safe_prefix(text, max_tokens, token_counter)

    def get_name(self) -> str:
        """Get strategy name."""
        return "simple"


class PriorityTruncationStrategy(TruncationStrategy):
    """Priority-based truncation preserving important sections.

    Identifies and preserves high-priority content:
    - Headers and titles
    - First and last paragraphs
    - Numbered/bulleted lists
    - Code blocks
    """

    def __init__(self, preserve_headers: bool = True, preserve_first_last: bool = True):
        """Initialize priority truncation strategy.

        Args:
            preserve_headers: Whether to preserve headers
            preserve_first_last: Whether to preserve first/last paragraphs
        """
        self.preserve_headers = preserve_headers
        self.preserve_first_last = preserve_first_last

    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text preserving high-priority sections.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            token_counter: TokenCounter instance

        Returns:
            Truncated text
        """
        current_tokens = token_counter.count_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # Split into sections
        sections = self._split_sections(text)

        # Prioritize sections (each carries its original index)
        prioritized = self._prioritize_sections(sections)

        # SELECT high-priority sections within the token budget, remembering
        # each one's original position. We choose by priority but must EMIT in
        # original document order -- appending in priority order scrambled the
        # document (e.g. the last section landed before earlier ones) (C-9).
        # Each emitted section after the first is joined with "\n\n"; that
        # separator costs tokens the per-section sums would otherwise omit -- the
        # budget overshoot the Phase-8 sign-off found. Charge it during selection.
        sep_tokens = token_counter.count_tokens("\n\n")
        selected: list[tuple[int, str]] = []  # (original_index, text_to_emit)
        total_tokens = 0

        for index, section, priority in prioritized:
            section_tokens = token_counter.count_tokens(section)
            join_cost = sep_tokens if selected else 0

            if total_tokens + join_cost + section_tokens <= max_tokens:
                selected.append((index, section))
                total_tokens += join_cost + section_tokens
            elif total_tokens + join_cost < max_tokens:
                # Partial section
                remaining = max_tokens - total_tokens - join_cost
                truncated_section = SimpleTruncationStrategy().truncate(
                    section, remaining, token_counter
                )
                selected.append((index, truncated_section))
                break
            else:
                break

        # Restore original document order before joining.
        selected.sort(key=lambda item: item[0])
        result = "\n\n".join(text for _, text in selected)
        return self._enforce_budget(result, max_tokens, token_counter)

    def _split_sections(self, text: str) -> List[str]:
        """Split text into sections.

        Args:
            text: Text to split

        Returns:
            List of sections
        """
        # Split by double newlines (paragraphs)
        sections = re.split(r"\n\n+", text)
        return [s.strip() for s in sections if s.strip()]

    def _prioritize_sections(self, sections: List[str]) -> List[tuple]:
        """Prioritize sections by importance.

        Args:
            sections: List of sections

        Returns:
            List of (original_index, section, priority) tuples, sorted by
            priority (highest first). The index lets the caller restore
            original document order after selecting by priority.
        """
        prioritized = []

        for i, section in enumerate(sections):
            priority = self._calculate_priority(section, i, len(sections))
            prioritized.append((i, section, priority))

        # Sort by priority (higher first)
        prioritized.sort(key=lambda x: x[2], reverse=True)

        return prioritized

    def _calculate_priority(self, section: str, index: int, total: int) -> float:
        """Calculate section priority.

        Args:
            section: Section text
            index: Section index
            total: Total number of sections

        Returns:
            Priority score (higher is more important)
        """
        priority = 0.0

        # Headers (markdown style)
        if self.preserve_headers and re.match(r"^#+\s", section):
            priority += 10.0

        # First paragraph
        if self.preserve_first_last and index == 0:
            priority += 8.0

        # Last paragraph
        if self.preserve_first_last and index == total - 1:
            priority += 7.0

        # Lists
        if re.match(r"^[\*\-\d]+[\.\)]\s", section):
            priority += 5.0

        # Code blocks
        if "```" in section or section.startswith("    "):
            priority += 6.0

        # Length bonus (longer sections may be more important)
        priority += min(len(section) / 1000, 2.0)

        return priority

    def get_name(self) -> str:
        """Get strategy name."""
        return "priority"


class SemanticTruncationStrategy(TruncationStrategy):
    """Semantic-aware truncation preserving meaning.

    Truncates at sentence boundaries and preserves semantic coherence.
    """

    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text at sentence boundaries.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            token_counter: TokenCounter instance

        Returns:
            Truncated text
        """
        current_tokens = token_counter.count_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # Split into sentences
        sentences = self._split_sentences(text)

        # Build truncated text sentence by sentence
        result: list[str] = []
        total_tokens = 0

        # Sentences are re-joined with a single space; count that separator so the
        # running total matches the assembled string (Phase-8 overshoot fix).
        sep_tokens = token_counter.count_tokens(" ")
        for sentence in sentences:
            sentence_tokens = token_counter.count_tokens(sentence)
            join_cost = sep_tokens if result else 0

            if total_tokens + join_cost + sentence_tokens <= max_tokens:
                result.append(sentence)
                total_tokens += join_cost + sentence_tokens
            else:
                break

        if result:
            return self._enforce_budget(" ".join(result), max_tokens, token_counter)
        else:
            # Fallback to simple truncation if first sentence is too long
            return SimpleTruncationStrategy().truncate(text, max_tokens, token_counter)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def get_name(self) -> str:
        """Get strategy name."""
        return "semantic"


class SlidingWindowStrategy(TruncationStrategy):
    """Sliding window truncation for context preservation.

    Maintains a sliding window of recent content, useful for
    conversational contexts where recent information is most relevant.
    """

    def __init__(self, window_overlap: float = 0.1):
        """Initialize sliding window strategy.

        Args:
            window_overlap: Overlap ratio between windows (0-1)
        """
        self.window_overlap = window_overlap

    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text using sliding window.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            token_counter: TokenCounter instance

        Returns:
            Truncated text (most recent content)
        """
        current_tokens = token_counter.count_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # Split into lines for granular control
        lines = text.splitlines()

        # We only reach here when the text exceeds the budget, so a truncation
        # marker WILL be prepended -- reserve its tokens up front. Kept lines are
        # joined with "\n", so charge that separator too. Both were previously
        # omitted from the running total, overshooting the budget (Phase-8 fix).
        marker = "[...earlier content truncated...]\n"
        marker_tokens = token_counter.count_tokens(marker)
        newline_tokens = token_counter.count_tokens("\n")
        budget = max_tokens - marker_tokens

        # Start from the end (most recent)
        result: List[str] = []
        total_tokens = 0

        for line in reversed(lines):
            line_tokens = token_counter.count_tokens(line)
            join_cost = newline_tokens if result else 0

            if total_tokens + join_cost + line_tokens <= budget:
                result.insert(0, line)
                total_tokens += join_cost + line_tokens
            else:
                break

        if result:
            truncated = "\n".join(result)

            # Add indicator that content was truncated
            if len(result) < len(lines):
                truncated = marker + truncated

            return self._enforce_budget(truncated, max_tokens, token_counter)
        else:
            # Fallback if the first (most recent) line alone overruns the budget
            return SimpleTruncationStrategy().truncate(text, max_tokens, token_counter)

    def get_name(self) -> str:
        """Get strategy name."""
        return "sliding_window"
