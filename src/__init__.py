"""Bob Shell LLM-Wiki Knowledge Manager - Token Optimization System.

This package implements a comprehensive token optimization system for Bob Shell,
achieving 89.3% token savings while maintaining 91.80% quality.

Components:
- cache: Multi-level caching (exact + semantic) [IMPLEMENTED]
- optimizer: Prompt compression and optimization [TODO]
- formatter: Format detection and enforcement [TODO]
- truncation: Intelligent content truncation [TODO]
- batch: Batch processing and scheduling [TODO]
- integration: Component integration and orchestration [TODO]
- monitoring: Metrics, logging, and observability [TODO]
"""

__version__ = "1.0.0-dev"
__author__ = "Bob Shell Team"

# Only import implemented components
from src.cache import ExactCache, MultiLevelCache, SemanticCache

__all__ = [
    "MultiLevelCache",
    "ExactCache",
    "SemanticCache",
]
