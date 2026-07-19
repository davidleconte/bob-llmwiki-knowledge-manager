"""Bob Shell LLM-Wiki Knowledge Manager - Token Optimization System.

A token-optimization library: multi-level caching, prompt optimization,
intelligent truncation, and monitoring, composed behind a single facade.

Components:
- cache: Multi-level caching (exact + semantic)
- optimizer: Prompt compression and optimization
- truncation: Intelligent content truncation
- monitoring: Metrics, logging, and observability
- config: Typed configuration wired to the runtime
- facade: TokenOptimizer, the unified entry point (also exposed via the CLI)
"""

__version__ = "1.1.0"
__author__ = "Bob Shell Team"

from src.cache import ExactCache, MultiLevelCache, SemanticCache
from src.facade import TokenOptimizer
from src.optimizer import PromptOptimizer, TokenCounter
from src.truncation import Truncator

__all__ = [
    "TokenOptimizer",
    "MultiLevelCache",
    "ExactCache",
    "SemanticCache",
    "PromptOptimizer",
    "TokenCounter",
    "Truncator",
]
