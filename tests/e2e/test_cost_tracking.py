"""
End-to-end tests for cost tracking with real token counting.

These tests validate that cost tracking works correctly with real operations.

Run with: RUN_E2E_TESTS=1 pytest tests/e2e/test_cost_tracking.py -v -s
"""

import pytest
import os
import time

from src.cache import ExactCache, SemanticCache, MultiLevelCache
from src.optimizer import TokenCounter, PromptOptimizer
from src.truncation import Truncator
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker, tokens_to_bobcoins
from src.monitoring.cost_reporting import (
    generate_cost_summary,
    generate_cost_dashboard,
    check_budget_health,
    get_top_cost_operations
)

# Skip if not running E2E tests
pytestmark = pytest.mark.skipif(
    not os.environ.get('RUN_E2E_TESTS'),
    reason="E2E tests require RUN_E2E_TESTS=1 environment variable"
)


class TestCostTracking:
    """Test cost tracking with real operations."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset cost tracker before each test."""
        reset_cost_tracker()
        yield
        reset_cost_tracker()
    
    @pytest.fixture
    def tracker(self):
        """Get cost tracker instance."""
        return get_cost_tracker(budget_bobcoins=100.0)
    
    def test_token_counting_cost_tracking(self, tracker):
        """Test that token counting records costs."""
        counter = TokenCounter(model="gpt-4", track_costs=True)
        
        text = "This is a test prompt for cost tracking validation."
        tokens = counter.count_tokens(text)
        
        # Verify cost was recorded
        metrics = tracker.get_cost_metrics()
        assert metrics['operations_count'] > 0, "Should record operation"
        assert metrics['total_tokens_used'] == tokens, "Should track tokens used"
        assert metrics['total_bobcoins_spent'] > 0, "Should calculate Bobcoins spent"
        
        # Verify cost calculation
        expected_bobcoins = tokens_to_bobcoins(tokens)
        assert abs(metrics['total_bobcoins_spent'] - expected_bobcoins) < 0.0001
    
    def test_cache_hit_cost_tracking(self, tracker):
        """Test that cache hits record savings."""
        cache = ExactCache(max_size=100, track_costs=True)
        
        prompt = "Test prompt for cache hit tracking"
        response = "Test response"
        
        # Store with token metadata
        counter = TokenCounter(model="gpt-4")
        tokens = counter.count_tokens(prompt)
        cache.set(prompt, response, metadata={'tokens': tokens})
        
        # Get from cache (should record savings)
        result = cache.get(prompt)
        assert result == response
        
        # Verify savings were recorded
        metrics = tracker.get_cost_metrics()
        assert metrics['total_bobcoins_saved'] > 0, "Should record savings"
        assert metrics['total_tokens_saved'] == tokens, "Should track tokens saved"
    
    def test_optimization_cost_tracking(self, tracker):
        """Test that optimization records costs and savings."""
        optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
        
        prompt = """
        This is a verbose prompt with lots of unnecessary whitespace and 
        redundant information that can be optimized for token efficiency.
        The optimization should reduce tokens while preserving meaning.
        """
        
        result = optimizer.optimize(prompt)
        
        # Verify optimization was tracked
        metrics = tracker.get_cost_metrics()
        assert metrics['operations_count'] > 0, "Should record optimization"
        assert metrics['total_tokens_used'] > 0, "Should track optimized tokens"
        
        # If savings occurred, verify they were tracked
        if result['tokens_saved'] > 0:
            assert metrics['total_tokens_saved'] > 0, "Should track savings"
            assert metrics['total_bobcoins_saved'] > 0, "Should calculate Bobcoin savings"
    
    def test_budget_monitoring(self, tracker):
        """Test budget monitoring and alerts."""
        # Set small budget for testing
        tracker.set_budget(10.0)
        
        # Perform operations to consume budget
        counter = TokenCounter(model="gpt-4", track_costs=True)
        
        # Use ~5000 tokens (5 Bobcoins)
        for i in range(5):
            text = "This is a test prompt " * 100  # ~1000 tokens each
            counter.count_tokens(text)
        
        # Check budget status
        budget_status = tracker.get_budget_status()
        assert budget_status['spent_bobcoins'] > 0, "Should have spent Bobcoins"
        assert budget_status['percent_used'] > 0, "Should show usage percentage"
        
        # Check health status
        health = check_budget_health()
        assert health['status'] in ['healthy', 'caution', 'warning', 'critical']
    
    def test_cost_reporting(self, tracker):
        """Test cost reporting utilities."""
        # Perform some operations
        counter = TokenCounter(model="gpt-4", track_costs=True)
        optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
        
        counter.count_tokens("Test prompt 1")
        counter.count_tokens("Test prompt 2")
        optimizer.optimize("Test prompt for optimization")
        
        # Generate summary
        summary = generate_cost_summary()
        assert 'budget' in summary
        assert 'costs' in summary
        assert 'rate' in summary
        
        # Generate dashboard
        dashboard = generate_cost_dashboard()
        assert 'BOBCOIN COST TRACKING DASHBOARD' in dashboard
        assert 'BUDGET STATUS' in dashboard
        assert 'COST METRICS' in dashboard
        
        # Get top operations
        top_ops = get_top_cost_operations(limit=3)
        assert isinstance(top_ops, list)
        if top_ops:
            assert 'operation' in top_ops[0]
            assert 'cost_bobcoins' in top_ops[0]
    
    def test_multi_level_cache_cost_tracking(self, tracker):
        """Test cost tracking with multi-level cache."""
        cache = MultiLevelCache(
            l1_max_size=100,
            l2_max_size=50,
            similarity_threshold=0.85
        )
        
        # Enable cost tracking on cache instances
        cache.l1_cache.track_costs = True
        cache.l1_cache._cost_tracker = tracker
        cache.l2_cache.track_costs = True
        cache.l2_cache._cost_tracker = tracker
        
        counter = TokenCounter(model="gpt-4")
        
        # Store prompts
        prompts = [
            "What is machine learning?",
            "Explain neural networks",
            "How does deep learning work?"
        ]
        
        for prompt in prompts:
            tokens = counter.count_tokens(prompt)
            cache.set(prompt, f"Response to: {prompt}", metadata={'tokens': tokens})
        
        # Get from cache (should record savings)
        for prompt in prompts:
            result = cache.get(prompt)
            assert result is not None
        
        # Verify savings were recorded
        metrics = tracker.get_cost_metrics()
        assert metrics['total_bobcoins_saved'] > 0, "Should record cache savings"
    
    def test_cost_rate_calculation(self, tracker):
        """Test cost rate calculations."""
        counter = TokenCounter(model="gpt-4", track_costs=True)
        
        # Perform operations
        for i in range(10):
            counter.count_tokens(f"Test prompt {i}")
            time.sleep(0.01)  # Small delay
        
        # Get cost rate
        rate = tracker.get_cost_rate()
        assert 'bobcoins_per_second' in rate
        assert 'bobcoins_per_minute' in rate
        assert 'bobcoins_per_hour' in rate
        assert rate['bobcoins_per_second'] >= 0
    
    def test_cost_breakdown_by_operation(self, tracker):
        """Test cost breakdown by operation type."""
        counter = TokenCounter(model="gpt-4", track_costs=True)
        optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
        cache = ExactCache(max_size=100, track_costs=True)
        
        # Perform different operations
        counter.count_tokens("Test 1")
        optimizer.optimize("Test prompt for optimization")
        
        tokens = counter.count_tokens("Cache test")
        cache.set("Cache test", "Response", metadata={'tokens': tokens})
        cache.get("Cache test")
        
        # Get cost breakdown
        metrics = tracker.get_cost_metrics()
        assert 'cost_by_operation' in metrics
        assert 'tokens_by_operation' in metrics
        
        # Should have multiple operation types
        assert len(metrics['cost_by_operation']) > 0
    
    def test_roi_calculation(self, tracker):
        """Test ROI calculation."""
        optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
        
        # Optimize a verbose prompt
        verbose_prompt = "This is a very verbose prompt " * 50
        result = optimizer.optimize(verbose_prompt)
        
        # Get metrics
        metrics = tracker.get_cost_metrics()
        
        # If savings occurred, ROI should be positive
        if metrics['total_bobcoins_saved'] > 0:
            assert metrics['roi_percent'] > 0, "Should have positive ROI"
        
        # ROI = (saved / spent) * 100
        if metrics['total_bobcoins_spent'] > 0:
            expected_roi = (metrics['total_bobcoins_saved'] / metrics['total_bobcoins_spent']) * 100
            assert abs(metrics['roi_percent'] - expected_roi) < 0.01


class TestCostTrackingIntegration:
    """Test cost tracking integration with full workflow."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset cost tracker before each test."""
        reset_cost_tracker()
        yield
        reset_cost_tracker()
    
    def test_full_workflow_cost_tracking(self):
        """Test cost tracking through full optimization workflow."""
        tracker = get_cost_tracker(budget_bobcoins=50.0)
        
        # Initialize components with cost tracking
        counter = TokenCounter(model="gpt-4", track_costs=True)
        optimizer = PromptOptimizer(model="gpt-4", use_cache=True, track_costs=True)
        cache = MultiLevelCache()
        
        # Workflow: count -> optimize -> cache -> retrieve
        prompts = [
            "Explain the concept of machine learning in detail",
            "What are the key differences between supervised and unsupervised learning?",
            "How do neural networks process information?"
        ]
        
        for prompt in prompts:
            # Count tokens
            original_tokens = counter.count_tokens(prompt)
            
            # Optimize
            result = optimizer.optimize(prompt)
            
            # Cache result
            cache.set(prompt, result['optimized'], metadata={'tokens': result['optimized_tokens']})
            
            # Retrieve from cache
            cached = cache.get(prompt)
            assert cached is not None
        
        # Verify comprehensive tracking
        metrics = tracker.get_cost_metrics()
        budget_status = tracker.get_budget_status()
        
        assert metrics['operations_count'] > 0, "Should track all operations"
        assert metrics['total_tokens_used'] > 0, "Should track tokens used"
        assert budget_status['spent_bobcoins'] > 0, "Should calculate total cost"
        
        # Generate final report
        summary = generate_cost_summary()
        assert summary['costs']['operations_count'] == metrics['operations_count']
        
        print("\n" + "="*70)
        print("FULL WORKFLOW COST TRACKING RESULTS")
        print("="*70)
        print(f"Operations: {metrics['operations_count']}")
        print(f"Tokens Used: {metrics['total_tokens_used']:,}")
        print(f"Tokens Saved: {metrics['total_tokens_saved']:,}")
        print(f"Bobcoins Spent: {budget_status['spent_bobcoins']:.4f}")
        print(f"Bobcoins Saved: {budget_status['saved_bobcoins']:.4f}")
        print(f"Net Cost: {budget_status['net_spent_bobcoins']:.4f}")
        print(f"ROI: {metrics['roi_percent']:.2f}%")
        print("="*70)
