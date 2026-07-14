"""Tests for truncation strategies.

Tests cover:
- SimpleTruncationStrategy
- PriorityTruncationStrategy
- SemanticTruncationStrategy
- SlidingWindowStrategy
"""

import pytest

from src.optimizer.token_counter import TokenCounter
from src.truncation.strategies import (
    PriorityTruncationStrategy,
    SemanticTruncationStrategy,
    SimpleTruncationStrategy,
    SlidingWindowStrategy,
)


class TestSimpleTruncationStrategy:
    """Test suite for SimpleTruncationStrategy."""

    def test_no_truncation_needed(self):
        """Test when text fits within limit."""
        strategy = SimpleTruncationStrategy()
        counter = TokenCounter()

        text = "Short text"
        result = strategy.truncate(text, max_tokens=100, token_counter=counter)

        assert result == text

    def test_truncation_with_ellipsis(self):
        """Test truncation adds ellipsis."""
        strategy = SimpleTruncationStrategy()
        counter = TokenCounter()

        text = " ".join(["word"] * 100)
        result = strategy.truncate(text, max_tokens=20, token_counter=counter)

        assert len(result) < len(text)
        assert result.endswith("...")

    def test_respects_token_limit(self):
        """Test that result respects token limit."""
        strategy = SimpleTruncationStrategy()
        counter = TokenCounter()

        text = " ".join(["word"] * 100)
        max_tokens = 30
        result = strategy.truncate(text, max_tokens=max_tokens, token_counter=counter)

        result_tokens = counter.count_tokens(result)
        assert result_tokens <= max_tokens

    def test_get_name(self):
        """Test strategy name."""
        strategy = SimpleTruncationStrategy()
        assert strategy.get_name() == "simple"


class TestPriorityTruncationStrategy:
    """Test suite for PriorityTruncationStrategy."""

    def test_preserves_headers(self):
        """Test that headers are preserved."""
        strategy = PriorityTruncationStrategy(preserve_headers=True)
        counter = TokenCounter()

        text = """# Important Header
Some content here.

More content that can be removed.

Even more content."""

        result = strategy.truncate(text, max_tokens=20, token_counter=counter)

        # Should preserve header
        assert "# Important Header" in result

    def test_preserves_first_paragraph(self):
        """Test that first paragraph is preserved."""
        strategy = PriorityTruncationStrategy(preserve_first_last=True)
        counter = TokenCounter()

        text = """First paragraph is important.

Middle paragraph.

Last paragraph."""

        result = strategy.truncate(text, max_tokens=15, token_counter=counter)

        # Should preserve first paragraph
        assert "First paragraph" in result

    def test_no_truncation_needed(self):
        """Test when text fits within limit."""
        strategy = PriorityTruncationStrategy()
        counter = TokenCounter()

        text = "Short text"
        result = strategy.truncate(text, max_tokens=100, token_counter=counter)

        assert result == text

    def test_get_name(self):
        """Test strategy name."""
        strategy = PriorityTruncationStrategy()
        assert strategy.get_name() == "priority"

    def test_preserves_original_section_order(self):
        """Kept sections must stay in original document order (C-9 regression).

        Previously the strategy appended sections in PRIORITY order and joined,
        so the output scrambled the document: with preserve_first_last, the last
        section (high priority) was emitted before earlier middle sections,
        producing text whose sections were out of their original sequence.
        """
        strategy = PriorityTruncationStrategy(preserve_first_last=True)
        counter = TokenCounter()

        # Six plainly-ordered sections, each uniquely identifiable by a marker.
        sections = [f"MARKER{i} some ordinary section content here" for i in range(6)]
        text = "\n\n".join(sections)

        # Budget for roughly half -> forces a proper subset, guaranteeing that
        # the high-priority first & last plus at least one middle survive.
        total = counter.count_tokens(text)
        result = strategy.truncate(text, max_tokens=total // 2, token_counter=counter)

        # Recover which original sections survived, in output order.
        present = [i for i in range(6) if f"MARKER{i}" in result]
        output_order = sorted(present, key=lambda i: result.index(f"MARKER{i}"))

        assert len(present) >= 3, f"expected a proper subset to survive, got {present}"
        # Their order in the output must match their original document order.
        assert output_order == sorted(output_order), (
            f"sections emitted out of original order: {output_order}"
        )


class TestSemanticTruncationStrategy:
    """Test suite for SemanticTruncationStrategy."""

    def test_truncates_at_sentence_boundary(self):
        """Test truncation at sentence boundaries."""
        strategy = SemanticTruncationStrategy()
        counter = TokenCounter()

        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = strategy.truncate(text, max_tokens=10, token_counter=counter)

        # Should end with complete sentence
        assert result.endswith(".")

    def test_preserves_complete_sentences(self):
        """Test that complete sentences are preserved."""
        strategy = SemanticTruncationStrategy()
        counter = TokenCounter()

        text = "Sentence one. Sentence two. Sentence three."
        result = strategy.truncate(text, max_tokens=8, token_counter=counter)

        # Should contain complete sentences
        assert "Sentence one." in result

    def test_no_truncation_needed(self):
        """Test when text fits within limit."""
        strategy = SemanticTruncationStrategy()
        counter = TokenCounter()

        text = "Short text."
        result = strategy.truncate(text, max_tokens=100, token_counter=counter)

        assert result == text

    def test_fallback_for_long_sentence(self):
        """Test fallback when first sentence is too long."""
        strategy = SemanticTruncationStrategy()
        counter = TokenCounter()

        # Very long sentence
        text = " ".join(["word"] * 100) + "."
        result = strategy.truncate(text, max_tokens=20, token_counter=counter)

        # Should use fallback truncation
        assert len(result) < len(text)

    def test_get_name(self):
        """Test strategy name."""
        strategy = SemanticTruncationStrategy()
        assert strategy.get_name() == "semantic"


class TestSlidingWindowStrategy:
    """Test suite for SlidingWindowStrategy."""

    def test_preserves_recent_content(self):
        """Test that recent content is preserved."""
        strategy = SlidingWindowStrategy()
        counter = TokenCounter()

        lines = [f"Line {i}" for i in range(20)]
        text = "\n".join(lines)

        result = strategy.truncate(text, max_tokens=20, token_counter=counter)

        # Should contain recent lines
        assert "Line 19" in result or "Line 18" in result

    def test_adds_truncation_indicator(self):
        """Test that truncation indicator is added."""
        strategy = SlidingWindowStrategy()
        counter = TokenCounter()

        lines = [f"Line {i}" for i in range(20)]
        text = "\n".join(lines)

        result = strategy.truncate(text, max_tokens=20, token_counter=counter)

        # Should indicate truncation
        if len(result.splitlines()) < len(lines):
            assert "[...earlier content truncated...]" in result

    def test_no_truncation_needed(self):
        """Test when text fits within limit."""
        strategy = SlidingWindowStrategy()
        counter = TokenCounter()

        text = "Short text"
        result = strategy.truncate(text, max_tokens=100, token_counter=counter)

        assert result == text

    def test_get_name(self):
        """Test strategy name."""
        strategy = SlidingWindowStrategy()
        assert strategy.get_name() == "sliding_window"


class TestBudgetInvariant:
    """The core promise of a token truncator: ``count_tokens(out) <= max_tokens``.

    Before the Phase-8 fix, Priority/Semantic/SlidingWindow summed per-piece token
    counts and ignored the separators (and SlidingWindow's marker) added when the
    pieces are re-joined, so the assembled output overshot the budget (e.g. Priority
    on 6 sections: budget 25 -> 29). Only ``Simple`` self-verified. These cases fail
    if any strategy's accounting or the ``_enforce_budget`` clamp is reverted.
    """

    ALL_STRATEGIES = [
        SimpleTruncationStrategy,
        PriorityTruncationStrategy,
        SemanticTruncationStrategy,
        SlidingWindowStrategy,
    ]

    # Multi-section (\n\n), multi-line (\n), and multi-sentence inputs -- the shapes
    # that exercise each strategy's join separator.
    SECTIONS = "\n\n".join(f"Section {i}: alpha beta gamma delta epsilon" for i in range(8))
    LINES = "\n".join(f"line {i} with several words to count" for i in range(30))
    SENTENCES = " ".join(f"This is sentence number {i} in the document." for i in range(30))
    INPUTS = [SECTIONS, LINES, SENTENCES]

    @pytest.mark.parametrize("strategy_cls", ALL_STRATEGIES)
    @pytest.mark.parametrize("max_tokens", [1, 3, 5, 8, 10, 15, 20, 25, 40, 60])
    @pytest.mark.parametrize("text", INPUTS)
    def test_never_exceeds_budget(self, strategy_cls, max_tokens, text):
        counter = TokenCounter()
        out = strategy_cls().truncate(text, max_tokens, counter)
        assert counter.count_tokens(out) <= max_tokens, (
            f"{strategy_cls.__name__} overshoot: budget={max_tokens} "
            f"got={counter.count_tokens(out)}"
        )

    def test_priority_multi_section_regression(self):
        """The exact overshoot the sign-off reproduced: Priority, 6 sections, budget 25."""
        counter = TokenCounter()
        text = "\n\n".join(f"Section {i}: alpha beta gamma delta epsilon" for i in range(6))
        out = PriorityTruncationStrategy().truncate(text, 25, counter)
        assert counter.count_tokens(out) <= 25

    def test_sliding_multiline_marker_regression(self):
        """SlidingWindow must fit budget *including* its prepended marker + \\n joins."""
        counter = TokenCounter()
        text = "\n".join(f"log line {i} carrying a few tokens each" for i in range(40))
        out = SlidingWindowStrategy().truncate(text, 20, counter)
        assert counter.count_tokens(out) <= 20


try:
    from hypothesis import given, settings
    from hypothesis import strategies as st

    _HAS_HYPOTHESIS = True
except ImportError:  # pragma: no cover - hypothesis is a dev dependency
    _HAS_HYPOTHESIS = False


@pytest.mark.skipif(not _HAS_HYPOTHESIS, reason="hypothesis not installed")
class TestBudgetInvariantProperty:
    """Property test: no strategy exceeds the budget for arbitrary text/limits."""

    if _HAS_HYPOTHESIS:

        @given(
            text=st.text(
                alphabet=st.characters(min_codepoint=32, max_codepoint=0x2E7F),
                min_size=0,
                max_size=400,
            ),
            max_tokens=st.integers(min_value=1, max_value=50),
            strategy_cls=st.sampled_from(TestBudgetInvariant.ALL_STRATEGIES),
        )
        @settings(max_examples=200, deadline=None)
        def test_invariant_holds(self, text, max_tokens, strategy_cls):
            counter = TokenCounter()
            out = strategy_cls().truncate(text, max_tokens, counter)
            assert counter.count_tokens(out) <= max_tokens


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
