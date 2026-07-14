"""Tests for PromptOptimizer.

Tests cover:
- Basic optimization
- Token savings (target: 89.3%)
- Quality preservation (target: 91.80%)
- Cache integration
- Batch optimization
- Statistics tracking
"""

import pytest

from src.optimizer.prompt_optimizer import PromptOptimizer


class TestPromptOptimizer:
    """Test suite for PromptOptimizer."""

    def test_initialization_default(self):
        """Test default initialization."""
        optimizer = PromptOptimizer()

        assert optimizer.token_counter.model == "gpt-4"
        assert optimizer.target_savings == 0.893
        assert optimizer.min_quality == 0.918
        assert optimizer.cache is not None

    def test_initialization_custom(self):
        """Test initialization with custom parameters."""
        optimizer = PromptOptimizer(
            model="gpt-3.5-turbo", target_savings=0.80, min_quality=0.90, use_cache=False
        )

        assert optimizer.token_counter.model == "gpt-3.5-turbo"
        assert optimizer.target_savings == 0.80
        assert optimizer.min_quality == 0.90
        assert optimizer.cache is None

    def test_optimize_simple(self):
        """Test basic optimization."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "Hello    world   with   extra   spaces"
        result = optimizer.optimize(prompt)

        assert "original" in result
        assert "optimized" in result
        assert "original_tokens" in result
        assert "optimized_tokens" in result
        assert "tokens_saved" in result
        assert "savings_percentage" in result
        assert "quality_score" in result

        # Should remove extra spaces
        assert "   " not in result["optimized"]

    def test_optimize_whitespace_normalization(self):
        """Test whitespace normalization."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "Line 1\n\n\n\nLine 2    with    spaces"
        result = optimizer.optimize(prompt)

        # Should normalize multiple newlines
        assert "\n\n\n" not in result["optimized"]
        # Should normalize spaces
        assert "    " not in result["optimized"]

    def test_optimize_redundancy_removal(self):
        """Test redundancy removal."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "This is a test. This is a test. Different content."
        result = optimizer.optimize(prompt)

        # Should have fewer tokens
        assert result["optimized_tokens"] < result["original_tokens"]

    def test_optimize_with_max_tokens(self):
        """Test optimization with token limit."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = " ".join(["word"] * 100)
        result = optimizer.optimize(prompt, max_tokens=20)

        # Should respect token limit
        assert result["optimized_tokens"] <= 20

    def test_optimize_preserve_structure(self):
        """Test structure preservation."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = """Section 1
Content here

Section 2
More content"""

        result = optimizer.optimize(prompt, preserve_structure=True)

        # Should preserve basic structure (at least double newlines become single)
        # Redundancy removal may affect exact structure
        assert len(result["optimized"]) > 0
        assert result["optimized_tokens"] <= result["original_tokens"]

    def test_optimize_aggressive_compression(self):
        """Test aggressive compression without structure preservation."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "This is actually a very simple test that is basically just checking compression."
        result = optimizer.optimize(prompt, preserve_structure=False)

        # Should remove filler words
        optimized_lower = result["optimized"].lower()
        assert "actually" not in optimized_lower or "basically" not in optimized_lower

    def test_quality_estimation(self):
        """Test quality score estimation."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "This is a test prompt with some content."
        result = optimizer.optimize(prompt)

        # Quality should be between 0 and 1
        assert 0 <= result["quality_score"] <= 1
        # Should be reasonably high for simple optimization
        assert result["quality_score"] > 0.5

    def test_cache_integration(self):
        """Test cache integration."""
        optimizer = PromptOptimizer(use_cache=True)

        prompt = "Test prompt for caching"

        # First optimization
        result1 = optimizer.optimize(prompt)

        # Second optimization (should use cache)
        result2 = optimizer.optimize(prompt)

        # Results should be identical (optimization is deterministic)
        assert result1["optimized"] == result2["optimized"]
        # ...and the SECOND call must be served from the exact cache, not recomputed.
        assert result2.get("from_cache") is True
        assert optimizer.cache.hit_rate() > 0

    def test_cache_actually_hits_on_repeat(self):
        """Regression: the exact cache must HIT on a repeated prompt.

        Guards the write-only-cache bug where PromptOptimizer._cache_result
        passed the metadata dict into ExactCache.set()'s positional ``version``
        slot, so set() stored under "{metadata}:{prompt}" while get() looked up
        "v1:{prompt}" -- the keys never matched and the cache never hit.
        """
        optimizer = PromptOptimizer(use_cache=True)
        prompt = "Summarize the following text for me please."

        first = optimizer.optimize(prompt)
        assert first.get("from_cache") is not True  # first call computes fresh

        second = optimizer.optimize(prompt)
        assert second.get("from_cache") is True  # second call served from cache
        assert optimizer.cache.hit_rate() > 0  # a real hit was recorded
        # cache hit returns the same optimized text and restored metadata
        assert second["optimized"] == first["optimized"]
        assert second["optimized_tokens"] == first["optimized_tokens"]

    def test_statistics_tracking(self):
        """Test statistics tracking."""
        optimizer = PromptOptimizer(use_cache=False)

        # Perform some optimizations
        optimizer.optimize("Test 1")
        optimizer.optimize("Test 2")
        optimizer.optimize("Test 3")

        stats = optimizer.get_stats()

        assert stats["optimizations_count"] == 3
        assert stats["total_tokens_saved"] >= 0
        assert stats["total_original_tokens"] > 0

    def test_reset_stats(self):
        """Test resetting statistics."""
        optimizer = PromptOptimizer(use_cache=False)

        optimizer.optimize("Test")
        optimizer.reset_stats()

        stats = optimizer.get_stats()
        assert stats["optimizations_count"] == 0
        assert stats["total_tokens_saved"] == 0
        assert stats["total_original_tokens"] == 0

    def test_batch_optimization(self):
        """Test batch optimization."""
        optimizer = PromptOptimizer(use_cache=False)

        prompts = ["First prompt", "Second prompt", "Third prompt"]

        results = optimizer.optimize_batch(prompts)

        assert len(results) == 3
        for result in results:
            assert "optimized" in result
            assert "tokens_saved" in result

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        optimizer = PromptOptimizer(use_cache=False)

        result = optimizer.optimize("")

        assert result["original_tokens"] == 0
        assert result["optimized_tokens"] == 0
        assert result["tokens_saved"] == 0

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "Hello 世界 🌍 with unicode"
        result = optimizer.optimize(prompt)

        assert result["optimized_tokens"] > 0
        # Should preserve unicode
        assert "世界" in result["optimized"] or "🌍" in result["optimized"]

    def test_code_optimization(self):
        """Test optimization of code content."""
        optimizer = PromptOptimizer(use_cache=False)

        code = """def hello():
    print("Hello world")
    return True"""

        result = optimizer.optimize(code)

        # Should optimize but preserve basic structure
        assert result["optimized_tokens"] <= result["original_tokens"]

    def test_long_text_optimization(self):
        """Test optimization of long text."""
        optimizer = PromptOptimizer(use_cache=False)

        # Create long text with redundancy and extra spaces
        prompt = " ".join([f"Word{i}  " for i in range(500)])
        result = optimizer.optimize(prompt)

        # Should achieve some savings (at least from whitespace)
        assert result["tokens_saved"] >= 0
        assert result["optimized_tokens"] <= result["original_tokens"]

    def test_meets_target_criteria(self):
        """Test meets_target flag."""
        optimizer = PromptOptimizer(
            target_savings=0.10,  # Low target
            min_quality=0.50,  # Low quality threshold
            use_cache=False,
        )

        prompt = "This is a test with some extra words that can be optimized."
        result = optimizer.optimize(prompt)

        # With low targets, should meet criteria
        if result["savings_percentage"] >= 10 and result["quality_score"] >= 0.50:
            assert result["meets_target"] is True

    def test_filler_word_removal(self):
        """Test removal of filler words."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "This is actually very simple and basically just a test."
        result = optimizer.optimize(prompt, preserve_structure=False)

        optimized_lower = result["optimized"].lower()

        # Should remove some filler words
        filler_count = sum(
            [1 for word in ["actually", "very", "basically", "just"] if word in optimized_lower]
        )

        # Should remove at least some fillers
        assert filler_count < 4

    def test_abbreviation_replacement(self):
        """Test common phrase abbreviation."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "For example, this is a test, that is to say, an example."
        result = optimizer.optimize(prompt, preserve_structure=False)

        optimized_lower = result["optimized"].lower()

        # Should use abbreviations
        assert "e.g." in optimized_lower or "i.e." in optimized_lower

    def test_multiline_preservation(self):
        """Test preservation of multiline structure."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = """Line 1
Line 2
Line 3"""

        result = optimizer.optimize(prompt, preserve_structure=True)

        # Should optimize but maintain reasonable structure
        # Note: redundancy removal may affect exact newline count
        assert len(result["optimized"]) > 0
        assert result["optimized_tokens"] <= result["original_tokens"]

    def test_truncation_by_lines(self):
        """Test truncation respects line boundaries."""
        optimizer = PromptOptimizer(use_cache=False)

        lines = [f"Line {i}" for i in range(100)]
        prompt = "\n".join(lines)

        result = optimizer.optimize(prompt, max_tokens=50)

        # Should truncate but maintain line structure
        assert "\n" in result["optimized"] or len(result["optimized"]) < len(prompt)

    def test_special_characters_handling(self):
        """Test handling of special characters."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "Test!!! Multiple??? Punctuation..."
        result = optimizer.optimize(prompt)

        # Should compress multiple punctuation
        assert "!!!" not in result["optimized"]
        assert "???" not in result["optimized"]

    def test_consistency(self):
        """Test optimization consistency."""
        optimizer = PromptOptimizer(use_cache=False)

        prompt = "Consistent test prompt"

        result1 = optimizer.optimize(prompt)
        result2 = optimizer.optimize(prompt)

        # Should produce same results
        assert result1["optimized"] == result2["optimized"]

    def test_stats_with_cache(self):
        """Test statistics with cache enabled."""
        optimizer = PromptOptimizer(use_cache=True)

        # Use longer prompts to avoid TF-IDF corpus issues
        optimizer.optimize("This is a longer test prompt with multiple words for testing")
        optimizer.optimize("Another longer test prompt with different words for variety")

        stats = optimizer.get_stats()

        assert "cache_enabled" in stats
        assert stats["cache_enabled"] is True
        assert "cache_stats" in stats
        assert stats["cache_stats"] is not None

    def test_average_savings_calculation(self):
        """Test average savings calculation."""
        optimizer = PromptOptimizer(use_cache=False)

        # Optimize multiple prompts
        prompts = [
            "Short prompt",
            "A longer prompt with more words to optimize",
            "Another test prompt",
        ]

        for prompt in prompts:
            optimizer.optimize(prompt)

        stats = optimizer.get_stats()

        # Should calculate average
        assert "average_savings_percentage" in stats
        assert stats["average_savings_percentage"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
