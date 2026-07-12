"""Tests for truncation strategies.

Tests cover:
- SimpleTruncationStrategy
- PriorityTruncationStrategy
- SemanticTruncationStrategy
- SlidingWindowStrategy
"""

import pytest
from src.truncation.strategies import (
    SimpleTruncationStrategy,
    PriorityTruncationStrategy,
    SemanticTruncationStrategy,
    SlidingWindowStrategy,
)
from src.optimizer.token_counter import TokenCounter


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
