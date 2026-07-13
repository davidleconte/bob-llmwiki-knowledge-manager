"""Demo of vocabulary drift monitoring with semantic cache.

This example shows how to use the VocabularyDriftMonitor to detect
when the semantic cache's vocabulary has drifted significantly,
which may indicate the need for cache invalidation or retraining.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cache import SemanticCache
from src.monitoring import get_drift_monitor, configure_drift_monitor


def main():
    """Run vocabulary drift monitoring demo."""
    print("=" * 70)
    print("Vocabulary Drift Monitoring Demo")
    print("=" * 70)
    print()
    
    # Configure drift monitor
    print("1. Configuring drift monitor...")
    drift_monitor = configure_drift_monitor(
        drift_threshold=0.3,      # Trigger alert at 30% drift
        snapshot_interval=2.0,    # Take snapshots every 2 seconds
        max_snapshots=10          # Keep last 10 snapshots
    )
    print(f"   - Drift threshold: {drift_monitor.drift_threshold}")
    print(f"   - Snapshot interval: {drift_monitor.snapshot_interval}s")
    print(f"   - Max snapshots: {drift_monitor.max_snapshots}")
    print()
    
    # Create semantic cache
    print("2. Creating semantic cache...")
    cache = SemanticCache(max_size=100)
    print("   ✓ Cache created")
    print()
    
    # Phase 1: Initial vocabulary (tech topics)
    print("3. Phase 1: Building initial vocabulary (tech topics)...")
    tech_prompts = [
        "How do I implement a binary search tree in Python?",
        "What are the best practices for REST API design?",
        "Explain the difference between SQL and NoSQL databases",
        "How to optimize database query performance?",
        "What is the CAP theorem in distributed systems?",
    ]
    
    for prompt in tech_prompts:
        cache.set(prompt, f"Response for: {prompt}")
    
    # Take initial snapshot
    snapshot1 = drift_monitor.take_snapshot(cache.embedding_generator)
    print(f"   ✓ Initial vocabulary size: {snapshot1.vocabulary_size}")
    print(f"   ✓ Corpus size: {snapshot1.corpus_size}")
    print()
    
    # Wait for snapshot interval
    time.sleep(2.5)
    
    # Phase 2: Add similar content (more tech topics)
    print("4. Phase 2: Adding similar content (more tech topics)...")
    more_tech = [
        "How to implement caching in web applications?",
        "What are microservices architecture patterns?",
        "Explain containerization with Docker",
    ]
    
    for prompt in more_tech:
        cache.set(prompt, f"Response for: {prompt}")
    
    # Check for drift (should be minimal)
    drift1 = drift_monitor.check_drift(cache.embedding_generator)
    if drift1:
        print(f"   ⚠️  Drift detected: {drift1.drift_score:.2f}")
        print(f"      - New terms: {drift1.new_terms}")
        print(f"      - Removed terms: {drift1.removed_terms}")
    else:
        print("   ✓ No significant drift (similar topics)")
    print()
    
    # Wait for snapshot interval
    time.sleep(2.5)
    
    # Phase 3: Shift to completely different domain (cooking)
    print("5. Phase 3: Shifting to different domain (cooking)...")
    cooking_prompts = [
        "What is the best way to make sourdough bread?",
        "How do I properly season a cast iron skillet?",
        "What temperature should I cook a medium-rare steak?",
        "How to make authentic Italian carbonara?",
        "What are the essential knife skills for cooking?",
        "How to properly caramelize onions?",
        "What is the difference between baking soda and baking powder?",
    ]
    
    for prompt in cooking_prompts:
        cache.set(prompt, f"Response for: {prompt}")
    
    # Check for drift (should be significant)
    drift2 = drift_monitor.check_drift(cache.embedding_generator)
    if drift2:
        print(f"   🚨 SIGNIFICANT DRIFT DETECTED: {drift2.drift_score:.2f}")
        print(f"      - New terms: {drift2.new_terms}")
        print(f"      - Removed terms: {drift2.removed_terms}")
        print(f"      - Change rate: {drift2.change_rate:.2%}")
        print()
        print("   💡 Recommendation: Consider cache invalidation or retraining")
    else:
        print("   ✓ No significant drift")
    print()
    
    # Show drift history
    print("6. Drift History:")
    history = drift_monitor.get_drift_history()
    if history:
        for i, event in enumerate(history, 1):
            print(f"   Event {i}:")
            print(f"      - Timestamp: {time.strftime('%H:%M:%S', time.localtime(event['timestamp']))}")
            print(f"      - Drift score: {event['metrics']['drift_score']:.2f}")
            print(f"      - Vocabulary: {event['old_vocabulary_size']} → {event['new_vocabulary_size']}")
            print(f"      - Corpus: {event['old_corpus_size']} → {event['new_corpus_size']}")
    else:
        print("   No drift events recorded")
    print()
    
    # Show monitor statistics
    print("7. Monitor Statistics:")
    stats = drift_monitor.stats()
    print(f"   - Total snapshots: {stats['snapshots_count']}")
    print(f"   - Drift events: {stats['drift_events_count']}")
    if stats['current_drift']:
        print(f"   - Current drift score: {stats['current_drift']['drift_score']:.2f}")
    print()
    
    # Show cache statistics
    print("8. Cache Statistics:")
    cache_stats = cache.stats()
    print(f"   - Total entries: {cache_stats['size']}")
    print(f"   - Hits: {cache_stats['hits']}")
    print(f"   - Misses: {cache_stats['misses']}")
    print(f"   - Hit rate: {cache_stats['hit_rate']:.1%}")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print()
    print("Key Takeaways:")
    print("  • Vocabulary drift monitoring helps detect concept drift")
    print("  • Significant drift may indicate need for cache invalidation")
    print("  • Monitor can track drift over time with configurable thresholds")
    print("  • Useful for maintaining cache quality in production")
    print("=" * 70)


if __name__ == "__main__":
    main()
