"""Prompt optimization module.

Token optimization for LLM prompts (whitespace/repeat compression). Measured
optimizer compression is ~20% mean savings on real prose, manifest-backed; see
``STATUS.md`` and ``evaluation/results/validation-2026-07-14/``. (The earlier
"89.3% savings / 91.80% quality" figures were fabricated and are retracted.)
"""

from src.optimizer.prompt_optimizer import PromptOptimizer
from src.optimizer.token_counter import TokenCounter

__all__ = ["PromptOptimizer", "TokenCounter"]
