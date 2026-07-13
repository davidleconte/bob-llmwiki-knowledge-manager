#!/usr/bin/env python3
"""
Simple Cost Tracking Demo - Fast execution

Quick demonstration of the Bobcoin cost tracking system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimizer import TokenCounter
from src.cache import ExactCache
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker
from src.monitoring.cost_reporting import generate_cost_dashboard


def main():
    """Run simple cost tracking demo."""
    print("\n" + "="*70)
    print("BOBCOIN COST TRACKING - SIMPLE DEMO")
    print("="*70)
    
    # Initialize
    reset_cost_tracker()
    tracker = get_cost_tracker(budget_bobcoins=100.0)
    
    # Create components with cost tracking
    counter = TokenCounter(model="gpt-4", track_costs=True)
    cache = ExactCache(max_size=100, track_costs=True)
    
    print("\n1. Token Counting (with cost tracking)")
    print("-" * 70)
    
    prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        tokens = counter.count_tokens(prompt)
        print(f"  {i}. '{prompt}' = {tokens} tokens")
    
    metrics = tracker.get_cost_metrics()
    print(f"\n  → Tokens used: {metrics['total_tokens_used']}")
    print(f"  → Cost: {metrics['total_bobcoins_spent']:.4f} Bobcoins")
    
    print("\n2. Cache Operations (with savings tracking)")
    print("-" * 70)
    
    # Store in cache
    for prompt in prompts:
        tokens = counter.count_tokens(prompt)
        cache.set(prompt, f"Response: {prompt}", metadata={'tokens': tokens})
        print(f"  Cached: '{prompt}'")
    
    # Retrieve from cache (saves tokens)
    print("\n  Retrieving from cache:")
    for prompt in prompts:
        result = cache.get(prompt)
        print(f"  ✓ Cache hit: '{prompt}'")
    
    metrics = tracker.get_cost_metrics()
    print(f"\n  → Tokens saved: {metrics['total_tokens_saved']}")
    print(f"  → Savings: {metrics['total_bobcoins_saved']:.4f} Bobcoins")
    
    print("\n3. Cost Dashboard")
    print("="*70)
    
    dashboard = generate_cost_dashboard()
    print(dashboard)
    
    print("\n" + "="*70)
    print("DEMO COMPLETE ✓")
    print("="*70)
    print("\nCost tracking is working! All operations were monitored.")
    print("\nFor full demo with optimization, see:")
    print("  examples/cost_tracking_demo.py")
    print("\nFor documentation, see:")
    print("  docs/knowledge-base/guides/cost-tracking-guide.md")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
