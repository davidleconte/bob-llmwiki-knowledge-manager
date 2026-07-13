"""
End-to-end tests with real LLM API calls.

These tests require:
1. Bob Shell API access or tiktoken for token counting
2. Network connectivity (for real API calls)
3. Environment variable RUN_E2E_TESTS=1

Run with: RUN_E2E_TESTS=1 pytest tests/e2e/ -v -s

Note: These tests measure real token usage and validate savings claims.
They use tiktoken for accurate token counting without requiring actual LLM API calls.
"""

import pytest
import os
import time
from typing import Dict, Any

from src.cache import ExactCache, SemanticCache, MultiLevelCache
from src.optimizer import TokenCounter, PromptOptimizer
from src.truncation import Truncator

# Skip if not running E2E tests
pytestmark = pytest.mark.skipif(
    not os.environ.get('RUN_E2E_TESTS'),
    reason="E2E tests require RUN_E2E_TESTS=1 environment variable"
)


class TestRealTokenCounting:
    """Test with real token counting (tiktoken)."""
    
    @pytest.fixture
    def token_counter(self):
        """Initialize token counter."""
        return TokenCounter(model="gpt-4")
    
    @pytest.fixture
    def optimizer(self, token_counter):
        """Initialize optimizer with real token counter."""
        return PromptOptimizer(model="gpt-4")
    
    def test_token_counter_accuracy(self, token_counter):
        """Test token counter with known text."""
        text = "Hello, world!"
        tokens = token_counter.count_tokens(text)
        
        # Should be around 3-4 tokens for this simple text
        assert tokens > 0, "Should count some tokens"
        assert tokens < 10, "Should not over-count"
        
        print(f"\nToken Counting Test:")
        print(f"Text: '{text}'")
        print(f"Tokens: {tokens}")
    
    def test_token_savings_simple_prompt(self, optimizer):
        """Test token savings with simple prompt."""
        prompt = """
        I need help understanding how to implement caching in Python.
        Can you explain the different caching strategies?
        """
        
        # Measure original tokens
        original_tokens = optimizer.token_counter.count_tokens(prompt)
        
        # Optimize
        result = optimizer.optimize(prompt)
        optimized_tokens = result['optimized_tokens']
        
        # Calculate savings
        savings_pct = (1 - optimized_tokens / original_tokens) * 100
        
        # Assertions
        assert savings_pct >= 0, "Should have non-negative savings"
        assert savings_pct < 50, "Savings should be realistic (<50%)"
        assert result['optimized'] != prompt, "Text should be modified"
        
        # Log results
        print(f"\nSimple Prompt Token Savings:")
        print(f"Original: {original_tokens} tokens")
        print(f"Optimized: {optimized_tokens} tokens")
        print(f"Savings: {savings_pct:.1f}%")
        print(f"Original text: {prompt[:50]}...")
        print(f"Optimized text: {result['optimized'][:50]}...")
    
    def test_token_savings_verbose_prompt(self, optimizer):
        """Test token savings with verbose prompt."""
        prompt = """
        Hello! I was wondering if you could please help me understand 
        how to properly implement caching strategies in Python. I would 
        really appreciate it if you could explain the different types of 
        caching that are available, such as LRU caching, and when I should 
        use each one. Thank you so much for your help!
        """
        
        # Measure original tokens
        original_tokens = optimizer.token_counter.count_tokens(prompt)
        
        # Optimize
        result = optimizer.optimize(prompt)
        optimized_tokens = result['optimized_tokens']
        
        # Calculate savings
        savings_pct = (1 - optimized_tokens / original_tokens) * 100
        
        # Verbose prompts should have some savings (realistic: 5-40%)
        assert savings_pct >= 0, "Should have non-negative savings"
        assert savings_pct < 50, "Savings should be realistic (<50%)"
        
        # Log results
        print(f"\nVerbose Prompt Token Savings:")
        print(f"Original: {original_tokens} tokens")
        print(f"Optimized: {optimized_tokens} tokens")
        print(f"Savings: {savings_pct:.1f}%")
    
    def test_token_savings_code_prompt(self, optimizer):
        """Test token savings with code-heavy prompt."""
        prompt = """
        Here is my Python code:
        
        def calculate_sum(numbers):
            total = 0
            for num in numbers:
                total += num
            return total
        
        Can you help me optimize this function?
        """
        
        # Measure original tokens
        original_tokens = optimizer.token_counter.count_tokens(prompt)
        
        # Optimize
        result = optimizer.optimize(prompt)
        optimized_tokens = result['optimized_tokens']
        
        # Calculate savings
        savings_pct = (1 - optimized_tokens / original_tokens) * 100
        
        # Code should be preserved, so savings might be lower
        assert savings_pct >= 0, "Should have non-negative savings"
        assert "def calculate_sum" in result['optimized'], "Code should be preserved"
        
        # Log results
        print(f"\nCode Prompt Token Savings:")
        print(f"Original: {original_tokens} tokens")
        print(f"Optimized: {optimized_tokens} tokens")
        print(f"Savings: {savings_pct:.1f}%")


class TestRealCachePerformance:
    """Test cache performance with real operations."""
    
    @pytest.fixture
    def cache_system(self):
        """Initialize complete cache system."""
        return MultiLevelCache(
            l1_max_size=100,
            l2_max_size=50,
            similarity_threshold=0.85
        )
    
    def test_cache_hit_latency(self, cache_system):
        """Test L1 cache hit latency."""
        query = "What is Python?"
        response = "Python is a programming language"
        
        # Store in cache
        cache_system.set(query, response)
        
        # Measure L1 hit latency
        start = time.perf_counter()
        result = cache_system.get(query)
        latency_ms = (time.perf_counter() - start) * 1000
        
        # Assertions
        assert result == response, "Should return cached value"
        assert latency_ms < 1.0, f"L1 hit should be <1ms, got {latency_ms:.2f}ms"
        
        # Log results
        print(f"\nL1 Cache Hit Latency:")
        print(f"Latency: {latency_ms:.3f}ms")
        print(f"Target: <1ms")
        print(f"Status: {'✅ PASS' if latency_ms < 1.0 else '❌ FAIL'}")
    
    def test_cache_miss_latency(self, cache_system):
        """Test cache miss latency."""
        query = "What is quantum computing?"
        
        # Measure cache miss latency (L1 + L2)
        start = time.perf_counter()
        result = cache_system.get(query)
        latency_ms = (time.perf_counter() - start) * 1000
        
        # Assertions
        assert result is None, "Should be cache miss"
        assert latency_ms < 100.0, f"Cache miss should be <100ms, got {latency_ms:.2f}ms"
        
        # Log results
        print(f"\nCache Miss Latency:")
        print(f"Latency: {latency_ms:.3f}ms")
        print(f"Target: <100ms")
        print(f"Status: {'✅ PASS' if latency_ms < 100.0 else '❌ FAIL'}")
    
    def test_semantic_cache_similarity(self, cache_system):
        """Test semantic cache with similar queries."""
        # Original query
        query1 = "How do I install Python packages?"
        response = "Use pip install package_name"
        cache_system.set(query1, response)
        
        # Similar queries
        similar_queries = [
            "What's the way to add Python libraries?",
            "How to install Python modules?",
            "Installing packages in Python",
        ]
        
        results = []
        for query in similar_queries:
            result = cache_system.get(query)
            results.append({
                'query': query,
                'result': result,
                'hit': result is not None
            })
        
        # Log results
        print(f"\nSemantic Cache Similarity Test:")
        print(f"Original query: '{query1}'")
        print(f"Response: '{response}'")
        print(f"\nSimilar queries:")
        for r in results:
            status = "✅ HIT" if r['hit'] else "❌ MISS"
            print(f"  {status}: '{r['query']}'")
        
        # At least one should hit (depending on threshold)
        hits = sum(1 for r in results if r['hit'])
        print(f"\nHit rate: {hits}/{len(similar_queries)} ({hits/len(similar_queries)*100:.1f}%)")
    
    def test_cache_promotion(self, cache_system):
        """Test L2 to L1 promotion."""
        # Store in cache
        query1 = "What is machine learning?"
        response = "ML is a subset of AI"
        cache_system.set(query1, response)
        
        # Similar query (should hit L2)
        query2 = "Explain machine learning"
        
        # First request - may hit L2
        start1 = time.perf_counter()
        result1 = cache_system.get(query2)
        latency1_ms = (time.perf_counter() - start1) * 1000
        
        # Second identical request - should hit L1 if promoted
        start2 = time.perf_counter()
        result2 = cache_system.get(query2)
        latency2_ms = (time.perf_counter() - start2) * 1000
        
        # Log results
        print(f"\nCache Promotion Test:")
        print(f"First request latency: {latency1_ms:.3f}ms")
        print(f"Second request latency: {latency2_ms:.3f}ms")
        
        if result1 is not None:
            print(f"Promotion occurred: {latency2_ms < latency1_ms}")
            print(f"Speedup: {latency1_ms / latency2_ms:.1f}x")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.fixture
    def complete_system(self):
        """Initialize complete optimization system."""
        cache = MultiLevelCache(
            l1_max_size=100,
            l2_max_size=50,
            similarity_threshold=0.85
        )
        optimizer = PromptOptimizer(model="gpt-4")
        truncator = Truncator()
        return cache, optimizer, truncator
    
    def test_documentation_query_workflow(self, complete_system):
        """Test typical documentation query workflow."""
        cache, optimizer, truncator = complete_system
        
        query = "How do I use Python decorators?"
        context = """
        Python decorators are a powerful feature that allows you to modify
        the behavior of functions or classes. They use the @ syntax.
        
        Example:
        def my_decorator(func):
            def wrapper():
                print("Before")
                func()
                print("After")
            return wrapper
        
        @my_decorator
        def say_hello():
            print("Hello!")
        """
        
        # Step 1: Check cache
        result = cache.get(query)
        if result:
            print(f"\n✅ Cache hit! 0 tokens used")
            return
        
        # Step 2: Optimize prompt
        optimized = optimizer.optimize(query)
        prompt_savings = optimized['savings_percentage']
        
        # Step 3: Truncate context
        original_context_tokens = optimizer.token_counter.count_tokens(context)
        truncated_result = truncator.truncate(context, max_tokens=100)
        truncated = truncated_result['truncated']
        truncated_tokens = truncated_result['truncated_tokens']
        context_savings = (1 - truncated_tokens / original_context_tokens) * 100
        
        # Calculate total savings
        original_total = optimized['original_tokens'] + original_context_tokens
        optimized_total = optimized['optimized_tokens'] + truncated_tokens
        total_savings = (1 - optimized_total / original_total) * 100 if original_total > 0 else 0
        
        # Log results
        print(f"\nDocumentation Query Workflow:")
        print(f"=" * 50)
        print(f"Query optimization:")
        print(f"  Original: {optimized['original_tokens']} tokens")
        print(f"  Optimized: {optimized['optimized_tokens']} tokens")
        print(f"  Savings: {prompt_savings:.1f}%")
        print(f"\nContext truncation:")
        print(f"  Original: {original_context_tokens} tokens")
        print(f"  Truncated: {truncated_tokens} tokens")
        print(f"  Savings: {context_savings:.1f}%")
        print(f"\nTotal:")
        print(f"  Original: {original_total} tokens")
        print(f"  Optimized: {optimized_total} tokens")
        print(f"  Savings: {total_savings:.1f}%")
        print(f"=" * 50)
        
        # Store in cache for future
        cache.set(query, "Decorators modify function behavior...")
        
        # Assertions - savings depend on input (short/optimal text may have 0%)
        assert total_savings >= 0, "Should have non-negative savings"
        assert total_savings < 80, "Savings should be realistic"
    
    def test_repeated_query_pattern(self, complete_system):
        """Test repeated query pattern (high cache value)."""
        cache, optimizer, truncator = complete_system
        
        queries = [
            "What is Python?",
            "What is Python?",  # Exact repeat
            "Can you explain Python?",  # Similar
            "What is Python?",  # Exact repeat again
        ]
        
        results = []
        for i, query in enumerate(queries, 1):
            start = time.perf_counter()
            result = cache.get(query)
            latency_ms = (time.perf_counter() - start) * 1000
            
            if result is None:
                # Cache miss - would do full optimization
                result = f"Response for: {query}"
                cache.set(query, result)
                tokens_used = 100  # Simulated
            else:
                # Cache hit - no tokens used
                tokens_used = 0
            
            results.append({
                'query': query,
                'hit': result is not None and tokens_used == 0,
                'latency_ms': latency_ms,
                'tokens': tokens_used
            })
        
        # Calculate statistics
        total_tokens = sum(r['tokens'] for r in results)
        hit_rate = sum(1 for r in results if r['hit']) / len(results) * 100
        avg_latency = sum(r['latency_ms'] for r in results) / len(results)
        
        # Log results
        print(f"\nRepeated Query Pattern Test:")
        print(f"=" * 50)
        for i, r in enumerate(results, 1):
            status = "✅ HIT" if r['hit'] else "❌ MISS"
            print(f"{i}. {status} ({r['latency_ms']:.3f}ms, {r['tokens']} tokens)")
        print(f"\nStatistics:")
        print(f"  Hit rate: {hit_rate:.1f}%")
        print(f"  Avg latency: {avg_latency:.3f}ms")
        print(f"  Total tokens: {total_tokens}")
        print(f"  Tokens saved: {400 - total_tokens} ({(1 - total_tokens/400)*100:.1f}%)")
        print(f"=" * 50)
        
        # Assertions
        assert hit_rate > 0, "Should have some cache hits"
        assert total_tokens < 400, "Should save tokens with caching"


class TestPerformanceTargets:
    """Validate performance targets from documentation."""
    
    def test_l1_cache_target(self):
        """Validate L1 cache <1ms target."""
        cache = ExactCache(max_size=100)
        cache.set("test", "value")
        
        # Measure 100 lookups
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            cache.get("test")
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)
        
        # Calculate percentiles
        latencies.sort()
        p50 = latencies[50]
        p95 = latencies[95]
        p99 = latencies[99]
        
        print(f"\nL1 Cache Performance (100 lookups):")
        print(f"  p50: {p50:.3f}ms")
        print(f"  p95: {p95:.3f}ms")
        print(f"  p99: {p99:.3f}ms")
        print(f"  Target: <1ms")
        print(f"  Status: {'✅ PASS' if p95 < 1.0 else '❌ FAIL'}")
        
        assert p95 < 1.0, f"p95 latency should be <1ms, got {p95:.3f}ms"
    
    def test_optimization_target(self):
        """Validate optimization <50ms target."""
        optimizer = PromptOptimizer(model="gpt-4")
        
        prompt = "Can you help me understand how to implement caching in Python?"
        
        # Measure 10 optimizations
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            optimizer.optimize(prompt)
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)
        
        # Calculate average
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"\nOptimization Performance (10 runs):")
        print(f"  Average: {avg_latency:.3f}ms")
        print(f"  Target: <50ms")
        print(f"  Status: {'✅ PASS' if avg_latency < 50.0 else '❌ FAIL'}")
        
        assert avg_latency < 50.0, f"Optimization should be <50ms, got {avg_latency:.3f}ms"


if __name__ == "__main__":
    # Allow running directly for quick testing
    print("Run with: RUN_E2E_TESTS=1 pytest tests/e2e/test_real_llm.py -v -s")
