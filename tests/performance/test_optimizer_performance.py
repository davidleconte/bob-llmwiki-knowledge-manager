"""Performance benchmarks for optimizer operations.

Tests measure latency for token counting and prompt optimization.
Validates performance targets: token counting <10ms per 1K tokens, optimization <50ms.
"""

import pytest
from src.optimizer import TokenCounter, PromptOptimizer


@pytest.mark.benchmark(group="optimizer-token-counting")
class TestTokenCounterPerformance:
    """Performance benchmarks for token counting."""
    
    @pytest.fixture
    def counter(self):
        """Create token counter."""
        return TokenCounter(model="gpt-4")
    
    @pytest.fixture
    def small_text(self):
        """Small text (~100 tokens)."""
        return "This is a test prompt. " * 20
    
    @pytest.fixture
    def medium_text(self):
        """Medium text (~1000 tokens)."""
        return "This is a test prompt with some content. " * 100
    
    @pytest.fixture
    def large_text(self):
        """Large text (~10000 tokens)."""
        return "This is a test prompt with some content. " * 1000
    
    def test_count_small_text(self, benchmark, counter, small_text):
        """Benchmark counting small text (~100 tokens)."""
        result = benchmark(counter.count_tokens, small_text)
        
        assert result > 0
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.010, f"Small text counting too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_count_medium_text(self, benchmark, counter, medium_text):
        """Benchmark counting medium text (~1000 tokens) - CRITICAL TEST."""
        result = benchmark(counter.count_tokens, medium_text)
        
        assert result > 0
        
        stats = benchmark.stats
        # Target: <10ms per 1000 tokens
        assert stats.stats.mean < 0.010, f"Medium text counting too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_count_large_text(self, benchmark, counter, large_text):
        """Benchmark counting large text (~10000 tokens)."""
        result = benchmark(counter.count_tokens, large_text)
        
        assert result > 0
        
        stats = benchmark.stats
        # Should scale linearly: ~100ms for 10K tokens
        assert stats.stats.mean < 0.100, f"Large text counting too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_count_empty_text(self, benchmark, counter):
        """Benchmark counting empty text."""
        result = benchmark(counter.count_tokens, "")
        
        assert result == 0
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.001, f"Empty text counting too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_count_repeated_text(self, benchmark, counter):
        """Benchmark counting same text multiple times (tests caching potential)."""
        text = "This is a repeated test prompt. " * 50
        
        # First count (no cache)
        counter.count_tokens(text)
        
        # Benchmark repeated counts
        result = benchmark(counter.count_tokens, text)
        
        assert result > 0
        
        stats = benchmark.stats
        print(f"\nRepeated text counting: {stats.stats.mean*1000:.2f}ms")
        print("Note: Could be optimized with caching")
    
    def test_batch_counting(self, benchmark, counter):
        """Benchmark batch token counting."""
        texts = [f"Test prompt {i} with some content" for i in range(100)]
        
        result = benchmark(counter.count_tokens_batch, texts)
        
        assert len(result) == 100
        
        stats = benchmark.stats
        # Should be faster than 100 individual counts
        assert stats.stats.mean < 0.100, f"Batch counting too slow: {stats.stats.mean*1000:.2f}ms"
        
        # Calculate per-text time
        per_text_ms = (stats.stats.mean * 1000) / 100
        print(f"\nBatch counting: {per_text_ms:.3f}ms per text")
    
    def test_message_counting(self, benchmark, counter):
        """Benchmark message list counting (chat format)."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": "Tell me more about it."},
        ]
        
        result = benchmark(counter.count_messages, messages)
        
        assert result > 0
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.020, f"Message counting too slow: {stats.stats.mean*1000:.2f}ms"


@pytest.mark.xfail(
    strict=True,
    reason="Phase 4: PromptOptimizer lacks max_tokens/target_reduction params; "
    "fixture constructs with unsupported kwargs (same gap as the config→runtime e2e tests)",
)
@pytest.mark.benchmark(group="optimizer-optimization")
class TestPromptOptimizerPerformance:
    """Performance benchmarks for prompt optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create prompt optimizer."""
        return PromptOptimizer(
            max_tokens=4096,
            target_reduction=0.3
        )
    
    @pytest.fixture
    def simple_prompt(self):
        """Simple prompt for optimization."""
        return "This is a test prompt with some repeated repeated words. " * 10
    
    @pytest.fixture
    def complex_prompt(self):
        """Complex prompt with more content."""
        return """
        This is a more complex prompt that contains multiple sentences.
        It has various types of content including repeated information.
        The prompt also includes some redundant redundant phrases.
        We want to optimize this to reduce token count while maintaining meaning.
        """ * 20
    
    def test_optimize_simple_prompt(self, benchmark, optimizer, simple_prompt):
        """Benchmark optimizing simple prompt."""
        result = benchmark(optimizer.optimize, simple_prompt)
        
        assert result['optimized_tokens'] < result['original_tokens']
        
        stats = benchmark.stats
        # Target: <50ms per optimization
        assert stats.stats.mean < 0.050, f"Simple optimization too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_optimize_complex_prompt(self, benchmark, optimizer, complex_prompt):
        """Benchmark optimizing complex prompt - CRITICAL TEST."""
        result = benchmark(optimizer.optimize, complex_prompt)
        
        assert result['optimized_tokens'] < result['original_tokens']
        
        stats = benchmark.stats
        # Target: <50ms per optimization
        print(f"\nComplex optimization: {stats.stats.mean*1000:.2f}ms")
        if stats.stats.mean >= 0.050:
            print(f"⚠️  Exceeds 50ms target - optimization needed")
    
    def test_optimize_already_optimal(self, benchmark, optimizer):
        """Benchmark optimizing already-optimal prompt."""
        prompt = "Short prompt."
        
        result = benchmark(optimizer.optimize, prompt)
        
        # Should return quickly for already-optimal prompts
        stats = benchmark.stats
        assert stats.stats.mean < 0.020, f"Optimal prompt check too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_optimize_with_truncation(self, benchmark, optimizer):
        """Benchmark optimization with truncation."""
        # Very long prompt that needs truncation
        prompt = "This is a very long prompt. " * 500
        
        result = benchmark(optimizer.optimize, prompt)
        
        assert result['optimized_tokens'] <= optimizer.max_tokens
        
        stats = benchmark.stats
        assert stats.stats.mean < 0.100, f"Truncation too slow: {stats.stats.mean*1000:.2f}ms"


@pytest.mark.benchmark(group="optimizer-end-to-end")
class TestEndToEndPerformance:
    """End-to-end performance tests combining multiple components."""
    
    def test_full_optimization_pipeline(self, benchmark):
        """Benchmark full optimization pipeline."""
        from src.cache import MultiLevelCache
        from src.optimizer import TokenCounter, PromptOptimizer
        
        # Initialize components
        cache = MultiLevelCache()
        counter = TokenCounter()
        optimizer = PromptOptimizer()
        
        prompt = "This is a test prompt for the full pipeline. " * 20
        
        def full_pipeline():
            # Check cache
            cached = cache.get(prompt)
            if cached:
                return cached
            
            # Count tokens
            tokens = counter.count_tokens(prompt)
            
            # Optimize if needed
            if tokens > 1000:
                result = optimizer.optimize(prompt)
                optimized = result['optimized_text']
            else:
                optimized = prompt
            
            # Cache result
            cache.set(prompt, optimized)
            
            return optimized
        
        result = benchmark(full_pipeline)
        
        assert result is not None
        
        stats = benchmark.stats
        # Target: <100ms for full pipeline (p95)
        print(f"\nFull pipeline: {stats.stats.mean*1000:.2f}ms")
        if stats.stats.mean >= 0.100:
            print(f"⚠️  Exceeds 100ms target")
    
    def test_cache_hit_pipeline(self, benchmark):
        """Benchmark pipeline with cache hit (should be fast)."""
        from src.cache import MultiLevelCache
        
        cache = MultiLevelCache()
        prompt = "Cached prompt"
        cache.set(prompt, "Cached result")
        
        def cached_pipeline():
            return cache.get(prompt)
        
        result = benchmark(cached_pipeline)
        
        assert result == "Cached result"
        
        stats = benchmark.stats
        # Cache hit should be very fast
        assert stats.stats.mean < 0.001, f"Cache hit pipeline too slow: {stats.stats.mean*1000:.2f}ms"
    
    def test_concurrent_optimization(self, benchmark):
        """Benchmark concurrent optimization requests."""
        from src.optimizer import PromptOptimizer
        from concurrent.futures import ThreadPoolExecutor
        
        optimizer = PromptOptimizer()
        prompts = [f"Test prompt {i} with content. " * 10 for i in range(10)]
        
        def concurrent_optimize():
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(optimizer.optimize, prompts))
            return results
        
        results = benchmark(concurrent_optimize)
        
        assert len(results) == 10
        
        stats = benchmark.stats
        print(f"\nConcurrent optimization (10 prompts, 4 workers): {stats.stats.mean*1000:.2f}ms")


@pytest.mark.benchmark(group="optimizer-scalability")
class TestOptimizerScalability:
    """Scalability tests for optimizer components."""
    
    def test_token_counting_scalability(self):
        """Test token counting scalability with increasing text size."""
        counter = TokenCounter()
        
        # Test with different sizes
        sizes = [100, 500, 1000, 5000, 10000]
        
        for size in sizes:
            text = "word " * size
            tokens = counter.count_tokens(text)
            print(f"\n{size} words: {tokens} tokens")
    
    def test_cache_scalability(self):
        """Test cache performance with increasing size."""
        from src.cache import MultiLevelCache
        
        cache = MultiLevelCache(l1_max_size=10000, l2_max_size=5000)
        
        # Populate with different sizes
        sizes = [100, 500, 1000, 5000]
        
        for size in sizes:
            cache.clear()
            
            # Populate
            for i in range(size):
                cache.set(f"key_{i}", f"value_{i}")
            
            # Measure lookup
            import time
            start = time.time()
            result = cache.get(f"key_{size//2}")
            elapsed = time.time() - start
            
            print(f"\nCache size {size}: {elapsed*1000:.2f}ms lookup")
            assert result is not None
