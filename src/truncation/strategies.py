"""Truncation strategies for prompt optimization.

This module provides various strategies for truncating prompts
while preserving quality and meaning.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import re


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


class SimpleTruncationStrategy(TruncationStrategy):
    """Simple truncation by character count.
    
    Truncates text at approximate character position based on
    token-to-character ratio. Fast but may cut mid-sentence.
    """
    
    def truncate(self, text: str, max_tokens: int, token_counter) -> str:
        """Truncate text using simple character-based approach.
        
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
        
        # Estimate character limit (conservative: 3.5 chars per token)
        char_limit = int(max_tokens * 3.5)
        
        if len(text) <= char_limit:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:char_limit - 3] + "..."
        
        # Verify token count
        if token_counter.count_tokens(truncated) > max_tokens:
            # Be more aggressive
            char_limit = int(max_tokens * 3.0)
            truncated = text[:char_limit - 3] + "..."
        
        return truncated
    
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
    
    def __init__(self, preserve_headers: bool = True,
                 preserve_first_last: bool = True):
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
        
        # Prioritize sections
        prioritized = self._prioritize_sections(sections)
        
        # Build truncated text from high-priority sections
        result = []
        total_tokens = 0
        
        for section, priority in prioritized:
            section_tokens = token_counter.count_tokens(section)
            
            if total_tokens + section_tokens <= max_tokens:
                result.append(section)
                total_tokens += section_tokens
            elif total_tokens < max_tokens:
                # Partial section
                remaining = max_tokens - total_tokens
                truncated_section = SimpleTruncationStrategy().truncate(
                    section, remaining, token_counter
                )
                result.append(truncated_section)
                break
            else:
                break
        
        return "\n\n".join(result)
    
    def _split_sections(self, text: str) -> List[str]:
        """Split text into sections.
        
        Args:
            text: Text to split
            
        Returns:
            List of sections
        """
        # Split by double newlines (paragraphs)
        sections = re.split(r'\n\n+', text)
        return [s.strip() for s in sections if s.strip()]
    
    def _prioritize_sections(self, sections: List[str]) -> List[tuple]:
        """Prioritize sections by importance.
        
        Args:
            sections: List of sections
            
        Returns:
            List of (section, priority) tuples, sorted by priority
        """
        prioritized = []
        
        for i, section in enumerate(sections):
            priority = self._calculate_priority(section, i, len(sections))
            prioritized.append((section, priority))
        
        # Sort by priority (higher first)
        prioritized.sort(key=lambda x: x[1], reverse=True)
        
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
        if self.preserve_headers and re.match(r'^#+\s', section):
            priority += 10.0
        
        # First paragraph
        if self.preserve_first_last and index == 0:
            priority += 8.0
        
        # Last paragraph
        if self.preserve_first_last and index == total - 1:
            priority += 7.0
        
        # Lists
        if re.match(r'^[\*\-\d]+[\.\)]\s', section):
            priority += 5.0
        
        # Code blocks
        if '```' in section or section.startswith('    '):
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
        result = []
        total_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = token_counter.count_tokens(sentence)
            
            if total_tokens + sentence_tokens <= max_tokens:
                result.append(sentence)
                total_tokens += sentence_tokens
            else:
                break
        
        if result:
            return " ".join(result)
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
        sentences = re.split(r'(?<=[.!?])\s+', text)
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
        
        # Start from the end (most recent)
        result = []
        total_tokens = 0
        
        for line in reversed(lines):
            line_tokens = token_counter.count_tokens(line)
            
            if total_tokens + line_tokens <= max_tokens:
                result.insert(0, line)
                total_tokens += line_tokens
            else:
                break
        
        if result:
            truncated = "\n".join(result)
            
            # Add indicator that content was truncated
            if len(result) < len(lines):
                truncated = "[...earlier content truncated...]\n" + truncated
            
            return truncated
        else:
            # Fallback if first line is too long
            return SimpleTruncationStrategy().truncate(text, max_tokens, token_counter)
    
    def get_name(self) -> str:
        """Get strategy name."""
        return "sliding_window"
