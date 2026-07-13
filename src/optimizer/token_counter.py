"""Token counting utilities for prompt optimization.

This module provides accurate token counting for various LLM models,
supporting both tiktoken (OpenAI) and approximate counting methods.
"""

from typing import Optional, Dict, Any
import re
import time

from src.pricing import DEFAULT_MODEL, usd_cost


class TokenCounter:
    """Token counter for LLM prompts.
    
    Provides accurate token counting using tiktoken when available,
    with fallback to approximation methods.
    
    Attributes:
        model: Model name for token counting
        encoding: Tiktoken encoding (if available)
        use_tiktoken: Whether tiktoken is available
        track_costs: Whether to track costs with CostTracker
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, track_costs: bool = False):
        """Initialize token counter.

        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            track_costs: Whether to track costs with CostTracker
        """
        self.model = model
        self.encoding = None
        self.use_tiktoken = False
        self.track_costs = track_costs
        
        # Try to import tiktoken
        try:
            import tiktoken
            self.encoding = tiktoken.encoding_for_model(model)
            self.use_tiktoken = True
        except (ImportError, KeyError):
            # Fallback to approximation
            self.use_tiktoken = False
        
        # Initialize cost tracker if enabled
        self._cost_tracker = None
        if self.track_costs:
            try:
                from ..monitoring.cost_tracker import get_cost_tracker
                self._cost_tracker = get_cost_tracker()
            except ImportError:
                self.track_costs = False
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        start_time = time.time()
        
        if self.use_tiktoken and self.encoding:
            tokens = len(self.encoding.encode(text))
        else:
            # Approximation: ~4 characters per token
            tokens = self._approximate_tokens(text)
        
        # Track cost if enabled
        if self.track_costs and self._cost_tracker:
            self._cost_tracker.record_token_counting(tokens)
        
        return tokens
    
    def _approximate_tokens(self, text: str) -> int:
        """Approximate token count.
        
        Uses heuristic: ~4 characters per token for English text.
        More accurate than simple character count.
        
        Args:
            text: Text to count
            
        Returns:
            Approximate token count
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Count words and special characters
        words = len(text.split())
        special_chars = len(re.findall(r'[^\w\s]', text))
        
        # Heuristic: words + special_chars / 2
        # Most words are 1 token, special chars often share tokens
        return words + (special_chars // 2)
    
    def count_messages(self, messages: list[Dict[str, str]]) -> int:
        """Count tokens in message list (chat format).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Total token count including message formatting overhead
        """
        total = 0
        
        for message in messages:
            # Count content tokens
            content = message.get('content', '')
            total += self.count_tokens(content)
            
            # Add overhead for message formatting
            # Typical: 4 tokens per message for role/formatting
            total += 4
        
        # Add overhead for conversation structure
        total += 2
        
        return total
    
    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """Estimate cost for token count.
        
        Args:
            tokens: Number of tokens
            model: Model name (uses self.model if not provided)
            
        Returns:
            Estimated cost in USD
        """
        model = model or self.model
        # Delegate to the single pricing source (src.pricing) so USD rates and
        # the default-model fallback have exactly one home.
        return usd_cost(tokens, model)
    
    def get_stats(self, text: str) -> Dict[str, Any]:
        """Get comprehensive token statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with token statistics
        """
        tokens = self.count_tokens(text)
        
        return {
            "tokens": tokens,
            "characters": len(text),
            "words": len(text.split()),
            "lines": len(text.splitlines()),
            "chars_per_token": len(text) / tokens if tokens > 0 else 0,
            "estimated_cost": self.estimate_cost(tokens),
            "model": self.model,
            "method": "tiktoken" if self.use_tiktoken else "approximation",
        }
    
    def compare_texts(self, original: str, optimized: str) -> Dict[str, Any]:
        """Compare token counts between original and optimized text.
        
        Args:
            original: Original text
            optimized: Optimized text
            
        Returns:
            Dictionary with comparison statistics
        """
        original_tokens = self.count_tokens(original)
        optimized_tokens = self.count_tokens(optimized)
        
        savings = original_tokens - optimized_tokens
        savings_pct = (savings / original_tokens * 100) if original_tokens > 0 else 0
        
        # Track optimization cost if enabled
        if self.track_costs and self._cost_tracker and savings > 0:
            self._cost_tracker.record_optimization(original_tokens, optimized_tokens)
        
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": savings,
            "savings_percentage": savings_pct,
            "compression_ratio": optimized_tokens / original_tokens if original_tokens > 0 else 0,
            "original_cost": self.estimate_cost(original_tokens),
            "optimized_cost": self.estimate_cost(optimized_tokens),
            "cost_savings": self.estimate_cost(savings),
        }
    
    def fits_context(self, text: str, max_tokens: int = 8192) -> bool:
        """Check if text fits within context window.
        
        Args:
            text: Text to check
            max_tokens: Maximum context window size
            
        Returns:
            True if text fits, False otherwise
        """
        return self.count_tokens(text) <= max_tokens
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit.
        
        Simple truncation by characters, approximating token count.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            
        Returns:
            Truncated text
        """
        current_tokens = self.count_tokens(text)
        
        if current_tokens <= max_tokens:
            return text
        
        # Approximate character limit
        # Use conservative ratio to ensure we don't exceed
        char_limit = int(max_tokens * 3.5)  # ~3.5 chars per token
        
        if len(text) <= char_limit:
            return text
        
        # Truncate and add ellipsis
        return text[:char_limit - 3] + "..."
