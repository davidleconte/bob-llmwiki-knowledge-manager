#!/usr/bin/env python3
"""
Live Session Tracker - Demo with Actual Savings

Demonstrates the live session tracker with real savings from:
- Cache hits (repeated prompts)
- Prompt optimization
- Efficiency gains
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.live_session_tracker import LiveSessionTracker


def main():
    """Run demo showing actual savings."""
    print("\n" + "="*80)
    print("LIVE SESSION TRACKER - SAVINGS DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows REAL savings from cache hits and optimizations\n")
    
    # Initialize tracker
    tracker = LiveSessionTracker(
        session_id="savings-demo-session",
        budget_bobcoins=1000.0
    )
    
    print("🔄 Running exchanges with repeated content to show savings...\n")
    
    # Exchange 1: First time (no cache, will be cached)
    print("Exchange 1: Initial request (will be cached)")
    tracker.track_exchange(
        user_message="What is machine learning and how does it work?",
        assistant_response="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It works by using algorithms to parse data, learn from it, and make predictions or decisions.",
        tool_uses=["search: machine learning concepts"]
    )
    
    # Exchange 2: Repeat user message (CACHE HIT!)
    print("Exchange 2: Repeated question (CACHE HIT - saves tokens!)")
    tracker.track_exchange(
        user_message="What is machine learning and how does it work?",  # Same as before
        assistant_response="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
        tool_uses=["search: machine learning concepts"]  # Same tool
    )
    
    # Exchange 3: New verbose content (will be optimized)
    print("Exchange 3: Verbose prompt (will be optimized)")
    verbose_prompt = """
    I would like to understand the fundamental concepts and principles behind 
    neural networks and deep learning architectures. Could you please provide 
    a comprehensive explanation that covers the basic building blocks, the 
    mathematical foundations, and how these systems are trained using 
    backpropagation and gradient descent optimization techniques?
    """ * 3  # Make it long enough to trigger optimization
    
    tracker.track_exchange(
        user_message=verbose_prompt,
        assistant_response="Neural networks are computational models inspired by biological neural networks. They consist of layers of interconnected nodes that process information through weighted connections, trained via backpropagation.",
        tool_uses=["analyze: neural networks"]
    )
    
    # Exchange 4: Repeat the verbose prompt (CACHE HIT on optimized version!)
    print("Exchange 4: Repeated verbose prompt (CACHE HIT on optimized version!)")
    tracker.track_exchange(
        user_message=verbose_prompt,  # Same verbose prompt
        assistant_response="Neural networks are computational models inspired by biological neural networks.",
        tool_uses=["analyze: neural networks"]
    )
    
    # Exchange 5: Another new question
    print("Exchange 5: New question (will be cached)")
    tracker.track_exchange(
        user_message="Explain deep learning",
        assistant_response="Deep learning is a subset of machine learning using neural networks with multiple layers.",
        tool_uses=["search: deep learning"]
    )
    
    # Exchange 6: Repeat (CACHE HIT!)
    print("Exchange 6: Repeated question (CACHE HIT!)")
    tracker.track_exchange(
        user_message="Explain deep learning",  # Same as before
        assistant_response="Deep learning is a subset of machine learning using neural networks with multiple layers.",
        tool_uses=["search: deep learning"]  # Same tool
    )
    
    print("\n✅ All exchanges tracked with savings!\n")
    
    # Display comprehensive dashboard
    tracker.print_live_dashboard()
    
    # Show savings details
    savings = tracker.get_savings_breakdown()
    
    print("\n" + "="*80)
    print("💎 DETAILED SAVINGS ANALYSIS")
    print("="*80)
    
    if savings['savings_events'] > 0:
        print(f"\nTotal Savings Events: {savings['savings_events']}")
        print(f"Total Bobcoins Saved: {savings['total_savings_bobcoins']:.4f} BC")
        print(f"Total Tokens Saved: {savings['total_tokens_saved']:,}")
        
        print("\n📊 Savings by Type:")
        for stype, data in savings['by_type'].items():
            pct = (data['bobcoins'] / savings['total_savings_bobcoins'] * 100) if savings['total_savings_bobcoins'] > 0 else 0
            print(f"  {stype:20} {data['bobcoins']:>10.4f} BC ({pct:>5.1f}%) - {data['count']} events")
        
        print("\n📊 Savings by Source:")
        for source, data in savings['by_source'].items():
            pct = (data['bobcoins'] / savings['total_savings_bobcoins'] * 100) if savings['total_savings_bobcoins'] > 0 else 0
            print(f"  {source:20} {data['bobcoins']:>10.4f} BC ({pct:>5.1f}%) - {data['count']} events")
        
        print("\n🎯 Key Insights:")
        cache_savings = savings['by_type'].get('cache_hit', {}).get('bobcoins', 0)
        opt_savings = savings['by_type'].get('optimization', {}).get('bobcoins', 0)
        
        if cache_savings > 0:
            print(f"  • Cache hits saved {cache_savings:.4f} BC by reusing previous results")
        if opt_savings > 0:
            print(f"  • Optimizations saved {opt_savings:.4f} BC by reducing token usage")
        
        total_spent = tracker.tracker.get_budget_status()['spent_bobcoins']
        if total_spent > 0:
            efficiency = (savings['total_savings_bobcoins'] / total_spent) * 100
            print(f"  • Efficiency gain: {efficiency:.1f}% (saved vs spent)")
    else:
        print("\nNo savings yet - run more exchanges with repeated content!")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nThis demonstrates how the live tracker captures:")
    print("  ✓ Cache hits when content is repeated")
    print("  ✓ Optimization savings for verbose prompts")
    print("  ✓ Detailed breakdown by type and source")
    print("  ✓ Real-time efficiency metrics")
    print("\nIntegrate with Bob Shell to track actual session savings!")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
