#!/usr/bin/env python3
"""
Cost Tracking System Demo

Demonstrates the Bobcoin cost tracking system with real operations.
Shows budget monitoring, cost breakdown, and dashboard generation.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimizer import TokenCounter, PromptOptimizer
from src.cache import ExactCache, SemanticCache, MultiLevelCache
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker
from src.monitoring.cost_reporting import (
    generate_cost_dashboard,
    check_budget_health,
    get_top_cost_operations,
    calculate_projected_costs
)


def demo_basic_tracking():
    """Demonstrate basic cost tracking."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Cost Tracking")
    print("="*70)
    
    # Reset and initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=50.0)
    
    # Create components with cost tracking enabled
    counter = TokenCounter(model="gpt-4", track_costs=True)
    
    # Perform operations
    prompts = [
        "What is machine learning?",
        "Explain neural networks in detail",
        "How does deep learning work?"
    ]
    
    print("\nCounting tokens for 3 prompts...")
    for i, prompt in enumerate(prompts, 1):
        tokens = counter.count_tokens(prompt)
        print(f"  {i}. '{prompt[:40]}...' = {tokens} tokens")
        time.sleep(0.1)
    
    # Show results
    print("\n" + "-"*70)
    metrics = tracker.get_cost_metrics()
    budget = tracker.get_budget_status()
    
    print(f"Operations: {metrics['operations_count']}")
    print(f"Total Tokens: {metrics['total_tokens_used']:,}")
    print(f"Bobcoins Spent: {budget['spent_bobcoins']:.4f} BC")
    print(f"Budget Remaining: {budget['remaining_bobcoins']:.4f} BC")
    print(f"Budget Used: {budget['percent_used']:.2f}%")


def demo_optimization_tracking():
    """Demonstrate optimization cost tracking."""
    print("\n" + "="*70)
    print("DEMO 2: Optimization Cost Tracking")
    print("="*70)
    
    # Reset and initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=50.0)
    
    # Create optimizer with cost tracking
    optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
    
    # Verbose prompt for optimization
    verbose_prompt = """
    This is a very verbose prompt with lots of unnecessary whitespace and 
    redundant information that can be optimized for token efficiency.
    The optimization process should reduce the number of tokens while 
    preserving the essential meaning and information content of the text.
    This demonstrates how the cost tracking system monitors both the cost
    of optimization and the savings achieved through token reduction.
    """
    
    print("\nOptimizing verbose prompt...")
    result = optimizer.optimize(verbose_prompt)
    
    print(f"\nOriginal tokens: {result['original_tokens']}")
    print(f"Optimized tokens: {result['optimized_tokens']}")
    print(f"Tokens saved: {result['tokens_saved']}")
    print(f"Savings: {result['savings_percentage']:.2f}%")
    
    # Show cost metrics
    print("\n" + "-"*70)
    metrics = tracker.get_cost_metrics()
    budget = tracker.get_budget_status()
    
    print(f"Bobcoins Spent: {budget['spent_bobcoins']:.4f} BC")
    print(f"Bobcoins Saved: {budget['saved_bobcoins']:.4f} BC")
    print(f"Net Cost: {budget['net_spent_bobcoins']:.4f} BC")
    print(f"ROI: {metrics['roi_percent']:.2f}%")


def demo_cache_tracking():
    """Demonstrate cache hit savings tracking."""
    print("\n" + "="*70)
    print("DEMO 3: Cache Hit Savings Tracking")
    print("="*70)
    
    # Reset and initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=50.0)
    
    # Create cache with cost tracking
    cache = ExactCache(max_size=100, track_costs=True)
    counter = TokenCounter(model="gpt-4")
    
    prompts = [
        "What is Python?",
        "Explain JavaScript",
        "What is Python?",  # Cache hit
        "Describe TypeScript",
        "Explain JavaScript",  # Cache hit
        "What is Python?"  # Cache hit
    ]
    
    print("\nProcessing prompts (some will hit cache)...")
    for i, prompt in enumerate(prompts, 1):
        # Check cache first
        cached = cache.get(prompt)
        
        if cached:
            print(f"  {i}. '{prompt}' - CACHE HIT ✓")
        else:
            # Count tokens and cache
            tokens = counter.count_tokens(prompt)
            cache.set(prompt, f"Response to: {prompt}", metadata={'tokens': tokens})
            print(f"  {i}. '{prompt}' - CACHE MISS (cached for next time)")
        
        time.sleep(0.1)
    
    # Show results
    print("\n" + "-"*70)
    metrics = tracker.get_cost_metrics()
    budget = tracker.get_budget_status()
    
    print(f"Cache Hits: 3 (saved tokens)")
    print(f"Cache Misses: 3 (counted tokens)")
    print(f"Bobcoins Saved: {budget['saved_bobcoins']:.4f} BC")
    print(f"Total Savings: {metrics['total_tokens_saved']:,} tokens")


def demo_full_workflow():
    """Demonstrate full workflow with cost tracking."""
    print("\n" + "="*70)
    print("DEMO 4: Full Workflow with Cost Tracking")
    print("="*70)
    
    # Reset and initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=100.0)
    
    # Create all components with cost tracking
    counter = TokenCounter(model="gpt-4", track_costs=True)
    optimizer = PromptOptimizer(model="gpt-4", use_cache=True, track_costs=True)
    cache = MultiLevelCache()
    
    # Enable cache cost tracking
    cache.l1_cache.track_costs = True
    cache.l1_cache._cost_tracker = tracker
    cache.l2_cache.track_costs = True
    cache.l2_cache._cost_tracker = tracker
    
    prompts = [
        "Explain machine learning concepts",
        "What are neural networks?",
        "Explain machine learning concepts",  # Will hit cache
        "Describe deep learning algorithms",
        "What are neural networks?"  # Will hit cache
    ]
    
    print("\nProcessing prompts through full workflow...")
    for i, prompt in enumerate(prompts, 1):
        # Check cache
        cached = cache.get(prompt)
        
        if cached:
            print(f"  {i}. Cache hit: '{prompt[:35]}...'")
        else:
            # Count, optimize, and cache
            original_tokens = counter.count_tokens(prompt)
            result = optimizer.optimize(prompt)
            cache.set(prompt, result['optimized'], 
                     metadata={'tokens': result['optimized_tokens']})
            print(f"  {i}. Processed: '{prompt[:35]}...' ({original_tokens} → {result['optimized_tokens']} tokens)")
        
        time.sleep(0.1)
    
    # Show comprehensive results
    print("\n" + "-"*70)
    print("FINAL COST SUMMARY")
    print("-"*70)
    
    metrics = tracker.get_cost_metrics()
    budget = tracker.get_budget_status()
    
    print(f"Total Operations: {metrics['operations_count']}")
    print(f"Tokens Used: {metrics['total_tokens_used']:,}")
    print(f"Tokens Saved: {metrics['total_tokens_saved']:,}")
    print(f"Bobcoins Spent: {budget['spent_bobcoins']:.4f} BC")
    print(f"Bobcoins Saved: {budget['saved_bobcoins']:.4f} BC")
    print(f"Net Cost: {budget['net_spent_bobcoins']:.4f} BC")
    print(f"ROI: {metrics['roi_percent']:.2f}%")
    print(f"Budget Used: {budget['percent_used']:.2f}%")


def demo_dashboard():
    """Demonstrate cost dashboard."""
    print("\n" + "="*70)
    print("DEMO 5: Cost Dashboard")
    print("="*70)
    
    # Reset and initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=100.0)
    
    # Simulate various operations
    counter = TokenCounter(model="gpt-4", track_costs=True)
    optimizer = PromptOptimizer(model="gpt-4", use_cache=False, track_costs=True)
    cache = ExactCache(max_size=100, track_costs=True)
    
    print("\nSimulating operations...")
    
    # Token counting
    for i in range(5):
        counter.count_tokens(f"Test prompt {i} " * 20)
    
    # Optimizations
    for i in range(3):
        optimizer.optimize("This is a verbose test prompt " * 30)
    
    # Cache operations
    for i in range(4):
        prompt = f"Cache test {i}"
        tokens = counter.count_tokens(prompt)
        cache.set(prompt, f"Response {i}", metadata={'tokens': tokens})
        cache.get(prompt)  # Hit
    
    print("Operations complete!\n")
    
    # Generate and display dashboard
    dashboard = generate_cost_dashboard()
    print(dashboard)
    
    # Additional insights
    print("\n" + "="*70)
    print("ADDITIONAL INSIGHTS")
    print("="*70)
    
    # Budget health
    health = check_budget_health()
    print(f"\nBudget Health: {health['status'].upper()}")
    print(f"Message: {health['message']}")
    
    # Top operations
    print("\nTop Cost Operations:")
    top_ops = get_top_cost_operations(limit=3)
    for i, op in enumerate(top_ops, 1):
        print(f"  {i}. {op['operation']}: {op['cost_bobcoins']:.4f} BC ({op['tokens']:,} tokens)")
    
    # Projections
    print("\nCost Projections (next 24 hours at current rate):")
    projection = calculate_projected_costs(operations_per_hour=50, hours=24)
    print(f"  Expected operations: {projection['total_operations']:,}")
    print(f"  Projected cost: {projection['projected_cost_bobcoins']:.4f} BC")
    print(f"  Will exceed budget: {'YES ⚠️' if projection['will_exceed_budget'] else 'NO ✓'}")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("BOBCOIN COST TRACKING SYSTEM - INTERACTIVE DEMO")
    print("="*70)
    print("\nThis demo showcases the cost tracking system's capabilities:")
    print("  1. Basic token counting cost tracking")
    print("  2. Optimization cost and savings tracking")
    print("  3. Cache hit savings tracking")
    print("  4. Full workflow integration")
    print("  5. Cost dashboard and reporting")
    
    try:
        # Run all demos
        demo_basic_tracking()
        time.sleep(1)
        
        demo_optimization_tracking()
        time.sleep(1)
        
        demo_cache_tracking()
        time.sleep(1)
        
        demo_full_workflow()
        time.sleep(1)
        
        demo_dashboard()
        
        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print("\nThe cost tracking system is fully operational!")
        print("All operations were tracked, costs calculated, and budgets monitored.")
        print("\nFor more information, see:")
        print("  - docs/knowledge-base/guides/cost-tracking-guide.md")
        print("  - tests/e2e/test_cost_tracking.py")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
