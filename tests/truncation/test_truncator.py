"""Tests for Truncator.

Tests cover:
- Basic truncation
- Strategy selection
- Statistics tracking
- Strategy comparison
- Auto-selection
"""

import pytest

from src.truncation.strategies import SimpleTruncationStrategy
from src.truncation.truncator import Truncator


class TestTruncator:
    """Test suite for Truncator."""

    def test_initialization_default(self):
        """Test default initialization."""
        truncator = Truncator()

        assert truncator.token_counter.model == "gpt-4"
        assert truncator.default_strategy == "semantic"
        assert len(truncator.strategies) == 4

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        truncator = Truncator(model="gpt-3.5-turbo", default_strategy="simple")

        assert truncator.token_counter.model == "gpt-3.5-turbo"
        assert truncator.default_strategy == "simple"

    def test_truncate_no_truncation_needed(self):
        """Test when text fits within limit."""
        truncator = Truncator()

        text = "Short text"
        result = truncator.truncate(text, max_tokens=100)

        assert result["was_truncated"] is False
        assert result["original"] == text
        assert result["truncated"] == text
        assert result["tokens_removed"] == 0

    def test_truncate_with_default_strategy(self):
        """Test truncation with default strategy."""
        truncator = Truncator()

        text = " ".join(["word"] * 100)
        result = truncator.truncate(text, max_tokens=20)

        assert result["was_truncated"] is True
        assert result["truncated_tokens"] <= 20
        assert result["tokens_removed"] > 0
        assert result["strategy"] == "semantic"

    def test_truncate_with_specific_strategy(self):
        """Test truncation with specific strategy."""
        truncator = Truncator()

        text = " ".join(["word"] * 100)
        result = truncator.truncate(text, max_tokens=20, strategy="simple")

        assert result["was_truncated"] is True
        assert result["strategy"] == "simple"

    def test_truncate_invalid_strategy(self):
        """Test error handling for invalid strategy."""
        truncator = Truncator()

        with pytest.raises(ValueError, match="Unknown strategy"):
            truncator.truncate("text", max_tokens=10, strategy="invalid")

    def test_add_custom_strategy(self):
        """Test adding custom strategy."""
        truncator = Truncator()

        custom_strategy = SimpleTruncationStrategy()
        truncator.add_strategy("custom", custom_strategy)

        assert "custom" in truncator.get_strategies()

    def test_get_strategies(self):
        """Test getting list of strategies."""
        truncator = Truncator()

        strategies = truncator.get_strategies()

        assert "simple" in strategies
        assert "priority" in strategies
        assert "semantic" in strategies
        assert "sliding_window" in strategies

    def test_set_default_strategy(self):
        """Test setting default strategy."""
        truncator = Truncator()

        truncator.set_default_strategy("simple")

        assert truncator.default_strategy == "simple"

    def test_set_invalid_default_strategy(self):
        """Test error handling for invalid default strategy."""
        truncator = Truncator()

        with pytest.raises(ValueError, match="Unknown strategy"):
            truncator.set_default_strategy("invalid")

    def test_statistics_tracking(self):
        """Test statistics tracking."""
        truncator = Truncator()

        text = " ".join(["word"] * 100)

        truncator.truncate(text, max_tokens=20)
        truncator.truncate(text, max_tokens=30)

        stats = truncator.get_stats()

        assert stats["truncations_count"] == 2
        assert stats["total_tokens_removed"] > 0
        assert stats["total_original_tokens"] > 0
        assert stats["average_removal_percentage"] > 0

    def test_reset_stats(self):
        """Test resetting statistics."""
        truncator = Truncator()

        text = " ".join(["word"] * 100)
        truncator.truncate(text, max_tokens=20)

        truncator.reset_stats()

        stats = truncator.get_stats()
        assert stats["truncations_count"] == 0
        assert stats["total_tokens_removed"] == 0
        assert stats["total_original_tokens"] == 0

    def test_compare_strategies(self):
        """Test comparing all strategies."""
        truncator = Truncator()

        text = """# Header
First paragraph with content.

Second paragraph with more content.

Third paragraph."""

        results = truncator.compare_strategies(text, max_tokens=20)

        assert "simple" in results
        assert "priority" in results
        assert "semantic" in results
        assert "sliding_window" in results

        for strategy, result in results.items():
            assert "truncated" in result
            assert "truncated_tokens" in result

    def test_auto_select_strategy_headers(self):
        """Test auto-selection for text with headers."""
        truncator = Truncator()

        text = """# Important Header
Content here."""

        strategy = truncator.auto_select_strategy(text, max_tokens=20)

        assert strategy == "priority"

    def test_auto_select_strategy_lists(self):
        """Test auto-selection for text with lists."""
        truncator = Truncator()

        text = """* Item 1
* Item 2
* Item 3"""

        strategy = truncator.auto_select_strategy(text, max_tokens=20)

        assert strategy == "priority"

    def test_auto_select_strategy_long_text(self):
        """Test auto-selection for long sequential text."""
        truncator = Truncator()

        lines = [f"Line {i}" for i in range(30)]
        text = "\n".join(lines)

        strategy = truncator.auto_select_strategy(text, max_tokens=20)

        assert strategy == "sliding_window"

    def test_auto_select_strategy_paragraphs(self):
        """Test auto-selection for text with paragraphs."""
        truncator = Truncator()

        text = """First paragraph with content here.

Second paragraph with more content.

Third paragraph with additional text.

Fourth paragraph to complete."""

        strategy = truncator.auto_select_strategy(text, max_tokens=20)

        assert strategy == "semantic"

    def test_auto_select_strategy_simple(self):
        """Test auto-selection for simple text."""
        truncator = Truncator()

        text = "Simple short text"

        strategy = truncator.auto_select_strategy(text, max_tokens=20)

        assert strategy == "simple"

    def test_removal_percentage_calculation(self):
        """Test removal percentage calculation."""
        truncator = Truncator()

        text = " ".join(["word"] * 100)
        result = truncator.truncate(text, max_tokens=20)

        expected_pct = (result["tokens_removed"] / result["original_tokens"]) * 100

        assert result["removal_percentage"] == pytest.approx(expected_pct, rel=0.01)

    def test_unicode_handling(self):
        """Test handling of unicode text."""
        truncator = Truncator()

        text = "Hello 世界 " * 50
        result = truncator.truncate(text, max_tokens=20)

        assert result["was_truncated"] is True
        assert result["truncated_tokens"] <= 20

    def test_empty_text(self):
        """Test handling of empty text."""
        truncator = Truncator()

        result = truncator.truncate("", max_tokens=10)

        assert result["was_truncated"] is False
        assert result["original_tokens"] == 0
        assert result["truncated_tokens"] == 0

    @pytest.mark.parametrize("strategy", ["simple", "priority", "semantic", "sliding_window"])
    @pytest.mark.parametrize(
        "text",
        [
            "Hello 世界 " * 50,  # CJK / multibyte, no sentence punctuation
            "word " * 200,  # long, no punctuation (one "sentence")
            "supercalifragilistic" * 40,  # one long token-dense stream
            "A. " * 100,  # many tiny sentences
        ],
    )
    def test_truncation_never_exceeds_budget(self, strategy, text):
        """Invariant (audit C-3): truncated tokens must never exceed max_tokens.

        A fixed chars-per-token ratio in SimpleTruncationStrategy overshot the
        budget for multibyte/CJK text; every strategy must respect max_tokens.
        """
        truncator = Truncator()
        max_tokens = 20
        result = truncator.truncate(text, max_tokens=max_tokens, strategy=strategy)
        assert result["was_truncated"] is True
        assert result["truncated_tokens"] <= max_tokens


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
