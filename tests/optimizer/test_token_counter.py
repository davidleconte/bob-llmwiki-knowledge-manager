"""Tests for TokenCounter.

Tests cover:
- Token counting (with and without tiktoken)
- Message counting
- Cost estimation
- Statistics generation
- Text comparison
- Context window checking
- Truncation
"""

import pytest

from src.optimizer.token_counter import TokenCounter


class TestTokenCounter:
    """Test suite for TokenCounter."""

    def test_initialization_default(self):
        """Test default initialization."""
        counter = TokenCounter()

        assert counter.model == "gpt-4"
        assert counter.encoding is not None or not counter.use_tiktoken

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        counter = TokenCounter(model="gpt-3.5-turbo")

        assert counter.model == "gpt-3.5-turbo"

    def test_count_tokens_empty(self):
        """Test counting tokens in empty string."""
        counter = TokenCounter()

        assert counter.count_tokens("") == 0

    def test_count_tokens_simple(self):
        """Test counting tokens in simple text."""
        counter = TokenCounter()

        text = "Hello world"
        tokens = counter.count_tokens(text)

        assert tokens > 0
        assert tokens <= 5  # Should be 2-3 tokens typically

    def test_count_tokens_longer(self):
        """Test counting tokens in longer text."""
        counter = TokenCounter()

        text = "This is a longer piece of text with multiple words and sentences."
        tokens = counter.count_tokens(text)

        assert tokens > 10
        assert tokens < 30

    def test_count_tokens_batch(self):
        """Batch counting returns per-text counts identical to single counts."""
        counter = TokenCounter()

        texts = ["Hello world", "", "This is a longer piece of text."]
        batch = counter.count_tokens_batch(texts)

        assert len(batch) == len(texts)
        # Order preserved and each entry equals the single-count result.
        assert batch == [counter.count_tokens(t) for t in texts]
        # Empty string contributes 0, matching count_tokens semantics.
        assert batch[1] == 0

    def test_count_tokens_batch_empty_list(self):
        """Batch counting an empty list returns an empty list."""
        counter = TokenCounter()

        assert counter.count_tokens_batch([]) == []

    def test_approximate_tokens(self):
        """Test approximate token counting."""
        counter = TokenCounter()
        counter.use_tiktoken = False  # Force approximation

        text = "Hello world, how are you?"
        tokens = counter._approximate_tokens(text)

        assert tokens > 0
        # Should be roughly 5-7 tokens
        assert 4 <= tokens <= 8

    def test_count_messages_empty(self):
        """Test counting tokens in empty message list."""
        counter = TokenCounter()

        messages = []
        tokens = counter.count_messages(messages)

        assert tokens == 2  # Just overhead

    def test_count_messages_single(self):
        """Test counting tokens in single message."""
        counter = TokenCounter()

        messages = [{"role": "user", "content": "Hello"}]
        tokens = counter.count_messages(messages)

        # Content + message overhead + conversation overhead
        assert tokens > 5

    def test_count_messages_multiple(self):
        """Test counting tokens in multiple messages."""
        counter = TokenCounter()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        tokens = counter.count_messages(messages)

        # Should account for all messages + overhead
        assert tokens > 15

    def test_estimate_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        counter = TokenCounter(model="gpt-4")

        cost = counter.estimate_cost(1000)

        assert cost == pytest.approx(0.03, rel=0.01)

    def test_estimate_cost_gpt35(self):
        """Test cost estimation for GPT-3.5 (real dated input list price)."""
        counter = TokenCounter(model="gpt-3.5-turbo")

        cost = counter.estimate_cost(1000)

        assert cost == pytest.approx(0.0005, rel=0.01)

    def test_estimate_cost_custom_model(self):
        """Test cost estimation with custom model (real dated input list price)."""
        counter = TokenCounter()

        cost = counter.estimate_cost(1000, model="gpt-3.5-turbo")

        assert cost == pytest.approx(0.0005, rel=0.01)

    def test_get_stats(self):
        """Test getting comprehensive statistics."""
        counter = TokenCounter()

        text = "Hello world, this is a test."
        stats = counter.get_stats(text)

        assert "tokens" in stats
        assert "characters" in stats
        assert "words" in stats
        assert "lines" in stats
        assert "chars_per_token" in stats
        assert "estimated_cost" in stats
        assert "model" in stats
        assert "method" in stats

        assert stats["tokens"] > 0
        assert stats["characters"] == len(text)
        assert stats["words"] == 6
        assert stats["lines"] == 1

    def test_compare_texts(self):
        """Test comparing original and optimized texts."""
        counter = TokenCounter()

        original = "This is a very long piece of text with many words."
        optimized = "This is shorter text."

        comparison = counter.compare_texts(original, optimized)

        assert "original_tokens" in comparison
        assert "optimized_tokens" in comparison
        assert "tokens_saved" in comparison
        assert "savings_percentage" in comparison
        assert "compression_ratio" in comparison
        assert "original_cost" in comparison
        assert "optimized_cost" in comparison
        assert "cost_savings" in comparison

        assert comparison["original_tokens"] > comparison["optimized_tokens"]
        assert comparison["tokens_saved"] > 0
        assert comparison["savings_percentage"] > 0
        assert comparison["compression_ratio"] < 1.0

    def test_compare_texts_same(self):
        """Test comparing identical texts."""
        counter = TokenCounter()

        text = "Same text"
        comparison = counter.compare_texts(text, text)

        assert comparison["tokens_saved"] == 0
        assert comparison["savings_percentage"] == 0
        assert comparison["compression_ratio"] == 1.0

    def test_fits_context_true(self):
        """Test checking if text fits in context window."""
        counter = TokenCounter()

        text = "Short text"

        assert counter.fits_context(text, max_tokens=8192) is True

    def test_fits_context_false(self):
        """Test checking if text exceeds context window."""
        counter = TokenCounter()

        # Create very long text
        text = " ".join(["word"] * 10000)

        assert counter.fits_context(text, max_tokens=100) is False

    def test_truncate_to_tokens_no_truncation(self):
        """Test truncation when text already fits."""
        counter = TokenCounter()

        text = "Short text"
        result = counter.truncate_to_tokens(text, max_tokens=100)

        assert result == text

    def test_truncate_to_tokens_with_truncation(self):
        """Test truncation when text is too long."""
        counter = TokenCounter()

        text = " ".join(["word"] * 1000)
        result = counter.truncate_to_tokens(text, max_tokens=50)

        assert len(result) < len(text)
        assert result.endswith("...")
        assert counter.count_tokens(result) <= 50

    def test_truncate_to_tokens_multibyte_respects_budget(self):
        """Emoji/CJK are multiple tokens per character; token-accurate truncation
        must still honor the budget (the old char heuristic overshot ~10x)."""
        counter = TokenCounter()
        for text in ["\U0001f30d" * 1000, "世界" * 1000]:
            result = counter.truncate_to_tokens(text, max_tokens=50)
            assert counter.count_tokens(result) <= 50

    def test_truncate_to_tokens_dense_ascii_respects_budget(self):
        """Dense/random ASCII tokenizes near ~1.3 chars/token; truncation must not
        exceed the budget (the old int(N*3.5) heuristic overshot ~2.6x)."""
        counter = TokenCounter()
        text = "!@#$%^&*()_+" * 500
        result = counter.truncate_to_tokens(text, max_tokens=20)
        assert counter.count_tokens(result) <= 20

    def test_truncate_to_tokens_zero_or_negative_budget_is_empty(self):
        """A zero/negative token budget fits nothing -> empty string. The old
        heuristic returned text[:-3] (nearly the whole input) for N=0."""
        counter = TokenCounter()
        assert counter.truncate_to_tokens("word " * 1000, max_tokens=0) == ""
        assert counter.truncate_to_tokens("anything", max_tokens=-5) == ""

    def test_whitespace_handling(self):
        """Test handling of extra whitespace."""
        counter = TokenCounter()

        text1 = "Hello world"
        text2 = "Hello    world"
        text3 = "Hello\n\nworld"

        # Should normalize whitespace in approximation
        tokens1 = counter.count_tokens(text1)
        tokens2 = counter.count_tokens(text2)

        # Tokens should be similar (whitespace normalized)
        assert abs(tokens1 - tokens2) <= 1

    def test_special_characters(self):
        """Test handling of special characters."""
        counter = TokenCounter()

        text = "Hello! How are you? I'm fine, thanks."
        tokens = counter.count_tokens(text)

        assert tokens > 0
        # Special chars should be counted
        assert tokens >= 8

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        counter = TokenCounter()

        text = "Hello 世界 🌍"
        tokens = counter.count_tokens(text)

        assert tokens > 0

    def test_empty_message_content(self):
        """Test handling of messages with empty content."""
        counter = TokenCounter()

        messages = [{"role": "user", "content": ""}, {"role": "assistant", "content": "Response"}]
        tokens = counter.count_messages(messages)

        # Should handle gracefully
        assert tokens > 0

    def test_multiline_text(self):
        """Test counting tokens in multiline text."""
        counter = TokenCounter()

        text = """Line 1
Line 2
Line 3"""

        tokens = counter.count_tokens(text)
        stats = counter.get_stats(text)

        assert tokens > 0
        assert stats["lines"] == 3

    def test_code_text(self):
        """Test counting tokens in code."""
        counter = TokenCounter()

        code = """def hello():
    print("Hello world")
    return True"""

        tokens = counter.count_tokens(code)

        assert tokens > 0
        # Code typically has more tokens due to syntax
        assert tokens >= 8

    def test_consistency(self):
        """Test that counting is consistent."""
        counter = TokenCounter()

        text = "This is a test of consistency"

        tokens1 = counter.count_tokens(text)
        tokens2 = counter.count_tokens(text)

        assert tokens1 == tokens2

    def test_cost_scaling(self):
        """Test that cost scales linearly with tokens."""
        counter = TokenCounter()

        cost_1k = counter.estimate_cost(1000)
        cost_2k = counter.estimate_cost(2000)

        assert cost_2k == pytest.approx(cost_1k * 2, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
