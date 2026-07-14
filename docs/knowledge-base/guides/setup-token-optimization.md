# Setting Up Token Optimization System Guide

## Overview
This guide walks you through installing, configuring, and verifying the Token Optimization System. By the end, you'll have a fully functional system ready to reduce token costs by up to 89.3% while preserving quality.

## Prerequisites
- Python 3.8 or higher
- pip package manager
- Basic understanding of Python virtual environments
- 50MB free disk space
- Internet connection for package downloads

## Steps

### Step 1: Clone or Download the Repository

If you haven't already, get the codebase:

```bash
# Clone the repository
git clone https://github.com/yourusername/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager
```

Or download and extract the ZIP file to your preferred location.

### Step 2: Create a Virtual Environment (Recommended)

Isolate the project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

Install required Python packages:

```bash
# Install the package with dev + monitoring extras (single home: pyproject.toml)
pip install -e ".[dev,monitoring]"
```

**Core Dependencies**:
- `numpy>=1.24.0` - Numerical operations for embeddings
- `scikit-learn>=1.3.0` - TF-IDF vectorization
- `tiktoken>=0.5.0` - Accurate token counting (optional but recommended)

**Installation Time**: ~2-3 minutes depending on your connection.

### Step 4: Verify Installation

Run the test suite to ensure everything is working:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Expected output:
# ==================== test session starts ====================
# collected 213 items
# 
# tests/cache/test_base.py ..................... PASSED
# tests/cache/test_exact_cache.py .............. PASSED
# tests/cache/test_semantic_cache.py ........... PASSED
# ...
# ==================== 213 passed in 5.23s ====================
```

All 213 tests should pass. If any fail, see the Troubleshooting section.

### Step 5: Basic Configuration

Create a simple configuration file:

```python
# config.py
from src.cache import ExactCache, SemanticCache, MultiLevelCache
from src.optimizer import TokenCounter, PromptOptimizer
from src.truncation import Truncator

# Configure cache sizes based on your needs
CACHE_CONFIG = {
    "l1_max_size": 1000,      # Exact match cache
    "l2_max_size": 500,       # Semantic cache
    "l2_threshold": 0.85      # Similarity threshold (0.0-1.0)
}

# Configure token counting
TOKEN_CONFIG = {
    "encoding": "cl100k_base"  # For GPT-4/GPT-3.5-turbo
}

# Configure truncation
TRUNCATION_CONFIG = {
    "default_strategy": "priority",  # or "simple", "semantic", "sliding_window"
    "max_length": 2000              # Maximum tokens for context
}
```

### Step 6: Initialize the System

Create your main application file:

```python
# main.py
from config import CACHE_CONFIG, TOKEN_CONFIG, TRUNCATION_CONFIG
from src.cache import ExactCache, SemanticCache, MultiLevelCache
from src.optimizer import TokenCounter, PromptOptimizer
from src.truncation import Truncator

# Initialize components
def initialize_system():
    # Setup cache
    l1_cache = ExactCache(max_size=CACHE_CONFIG["l1_max_size"])
    l2_cache = SemanticCache(
        max_size=CACHE_CONFIG["l2_max_size"],
        threshold=CACHE_CONFIG["l2_threshold"]
    )
    cache = MultiLevelCache(l1_cache, l2_cache)
    
    # Setup optimizer
    token_counter = TokenCounter(encoding=TOKEN_CONFIG["encoding"])
    optimizer = PromptOptimizer(token_counter=token_counter)
    
    # Setup truncator
    truncator = Truncator(
        default_strategy=TRUNCATION_CONFIG["default_strategy"]
    )
    
    return cache, optimizer, truncator

# Initialize
cache, optimizer, truncator = initialize_system()
print("✅ Token Optimization System initialized successfully!")
```

### Step 7: Test with a Sample Request

Create a test script to verify functionality:

```python
# test_system.py
from main import cache, optimizer, truncator

def test_optimization():
    # Sample query and context
    query = "Explain Python decorators with examples"
    context = """
    Python decorators are a powerful feature that allows you to modify
    the behavior of functions or classes. They use the @ syntax and are
    commonly used for logging, authentication, and caching.
    
    Here's a simple example:
    
    def my_decorator(func):
        def wrapper():
            print("Before function")
            func()
            print("After function")
        return wrapper
    
    @my_decorator
    def say_hello():
        print("Hello!")
    """
    
    # Step 1: Check cache
    print("Step 1: Checking cache...")
    result = cache.get(query)
    if result:
        print(f"✅ Cache hit! (0 tokens used)")
        return result
    print("❌ Cache miss, proceeding to optimization...")
    
    # Step 2: Optimize prompt
    print("\nStep 2: Optimizing prompt...")
    optimized = optimizer.optimize(query)
    print(f"Original tokens: {optimized['original_tokens']}")
    print(f"Optimized tokens: {optimized['optimized_tokens']}")
    print(f"Savings: {optimized['savings_percent']:.1f}%")
    
    # Step 3: Truncate context
    print("\nStep 3: Truncating context...")
    original_length = len(context)
    truncated = truncator.truncate(context, max_length=500)
    truncated_length = len(truncated)
    print(f"Original length: {original_length} chars")
    print(f"Truncated length: {truncated_length} chars")
    print(f"Savings: {(1 - truncated_length/original_length)*100:.1f}%")
    
    # Step 4: Store in cache for future use
    print("\nStep 4: Storing in cache...")
    response = "Decorators wrap functions to modify behavior..."
    cache.set(query, response)
    print("✅ Stored in cache")
    
    # Step 5: Verify cache
    print("\nStep 5: Verifying cache...")
    cached_result = cache.get(query)
    if cached_result:
        print("✅ Cache verification successful!")
    
    # Show statistics
    print("\n📊 Cache Statistics:")
    stats = cache.get_stats()
    print(f"L1 Hit Rate: {stats['l1_hit_rate']*100:.1f}%")
    print(f"L2 Hit Rate: {stats['l2_hit_rate']*100:.1f}%")
    print(f"Combined Hit Rate: {stats['combined_hit_rate']*100:.1f}%")

if __name__ == "__main__":
    test_optimization()
```

Run the test:

```bash
python3 test_system.py
```

## Verification

### Expected Output

You should see output similar to:

```
Step 1: Checking cache...
❌ Cache miss, proceeding to optimization...

Step 2: Optimizing prompt...
Original tokens: 8
Optimized tokens: 7
Savings: 12.5%

Step 3: Truncating context...
Original length: 456 chars
Truncated length: 350 chars
Savings: 23.2%

Step 4: Storing in cache...
✅ Stored in cache

Step 5: Verifying cache...
✅ Cache verification successful!

📊 Cache Statistics:
L1 Hit Rate: 50.0%
L2 Hit Rate: 0.0%
Combined Hit Rate: 50.0%
```

### Performance Verification

Run performance tests:

```bash
# Run performance-specific tests
python3 -m pytest tests/ -v -k "performance"
```

All performance tests should pass, confirming:
- L1 cache lookups < 1ms
- L2 cache lookups < 100ms
- Token counting < 10ms per 1000 tokens
- Optimization < 50ms per prompt

### Memory Verification

Check memory usage:

```python
# memory_check.py
import sys
from main import cache, optimizer, truncator

# Get approximate memory usage
l1_size = sys.getsizeof(cache.l1._cache)
l2_size = sys.getsizeof(cache.l2._cache)
total = l1_size + l2_size

print(f"L1 Cache: ~{l1_size/1024/1024:.1f} MB")
print(f"L2 Cache: ~{l2_size/1024/1024:.1f} MB")
print(f"Total: ~{total/1024/1024:.1f} MB")
```

Expected: ~20MB total for default configuration.

## Troubleshooting

### Issue 1: ImportError for tiktoken

**Symptoms**: 
```
ImportError: No module named 'tiktoken'
```

**Cause**: tiktoken not installed or installation failed.

**Solution**:
```bash
# Try installing tiktoken separately
pip install tiktoken

# If that fails, the system will use fallback counting
# (slightly less accurate but functional)
```

The system gracefully degrades to character-based counting if tiktoken is unavailable.

### Issue 2: Test Failures

**Symptoms**: Some tests fail with assertion errors.

**Cause**: Dependency version mismatch or incomplete installation.

**Solution**:
```bash
# Reinstall dependencies
pip uninstall -y numpy scikit-learn tiktoken
pip install -e ".[dev,monitoring]"

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Run tests again
python3 -m pytest tests/ -v
```

### Issue 3: Slow Performance

**Symptoms**: Operations take longer than expected.

**Cause**: Large cache sizes or system resource constraints.

**Solution**:
```python
# Reduce cache sizes in config.py
CACHE_CONFIG = {
    "l1_max_size": 500,   # Reduced from 1000
    "l2_max_size": 250,   # Reduced from 500
    "l2_threshold": 0.85
}
```

### Issue 4: Low Cache Hit Rate

**Symptoms**: Cache statistics show <10% combined hit rate.

**Cause**: Queries are too diverse or threshold too high.

**Solution**:
```python
# Lower semantic similarity threshold
CACHE_CONFIG = {
    "l1_max_size": 1000,
    "l2_max_size": 500,
    "l2_threshold": 0.80  # Lowered from 0.85
}
```

### Issue 5: Memory Issues

**Symptoms**: System runs out of memory or becomes slow.

**Cause**: Cache sizes too large for available RAM.

**Solution**:
```python
# Reduce cache sizes significantly
CACHE_CONFIG = {
    "l1_max_size": 100,   # Much smaller
    "l2_max_size": 50,    # Much smaller
    "l2_threshold": 0.85
}
```

## Next Steps

After successful setup:

1. **Integrate with Your Application**: Import and use the system in your LLM application
2. **Monitor Performance**: Track cache hit rates and token savings
3. **Tune Configuration**: Adjust cache sizes and thresholds based on your workload
4. **Review Documentation**: Read the API reference for advanced features

## Related Documents
- [Token Optimization Concept](../concepts/token-optimization.md) - Understanding the system
- [Multi-Level Caching Concept](../concepts/multi-level-caching.md) - Cache architecture details
- [Cache API Reference](../references/cache-api.md) - Complete API documentation
- [Performance Benchmarks](../research/performance-benchmarks.md) - Real-world performance data

## References
- [System Architecture](../../architecture/ACTUAL_SYSTEM_ARCHITECTURE.md) - Technical architecture
- [pyproject.toml](../../../pyproject.toml) - Complete dependency list (single home)
- [Test Suite](../../../tests/) - All test files

---
*Last Updated: 2026-07-13*
*Category: Guide*
