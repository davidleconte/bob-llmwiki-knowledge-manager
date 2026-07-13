#!/usr/bin/env python3
"""
Savings Measurement Demo

Demonstrates how to measure token savings in real-world Bob Shell usage.
This provides the measurement framework for Phase 3 validation.

Usage:
    # Run interactive demo
    python savings_measurement_demo.py
    
    # Run automated measurement
    python savings_measurement_demo.py --automated --queries 10
    
    # Compare baseline vs optimized
    python savings_measurement_demo.py --compare
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass

from src.optimizer import PromptOptimizer, TokenCounter
from src.cache import MultiLevelCache
from src.truncation import Truncator
from src.monitoring import get_logger

logger = get_logger("savings_demo")


@dataclass
class MeasurementResult:
    """Result of a single measurement."""
    query: str
    context: str
    baseline_tokens: int
    optimized_tokens: int
    tokens_saved: int
    savings_percent: float
    cache_hit: bool
    optimization_applied: bool
    truncation_applied: bool
    latency_ms: float


class SavingsMeasurementFramework:
    """
    Framework for measuring token savings in real-world scenarios.
    
    This framework provides:
    1. Baseline measurement (no optimization)
    2. Optimized measurement (with optimization)
    3. Comparison and analysis
    4. Statistical validation
    """
    
    def __init__(self):
        """Initialize measurement framework."""
        self.optimizer = PromptOptimizer()
        self.cache = MultiLevelCache()
        self.truncator = Truncator()
        self.token_counter = TokenCounter()
        
        logger.info("framework_initialized")
    
    def measure_baseline(
        self,
        query: str,
        context: str = ""
    ) -> Tuple[int, float]:
        """
        Measure baseline token usage (no optimization).
        
        Args:
            query: User query
            context: Context text
        
        Returns:
            Tuple of (token_count, latency_ms)
        """
        start_time = time.time()
        
        # Count tokens without any optimization
        tokens = self.token_counter.count_tokens(query + context)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return tokens, latency_ms
    
    def measure_optimized(
        self,
        query: str,
        context: str = "",
        response: str = ""
    ) -> MeasurementResult:
        """
        Measure optimized token usage (with optimization).
        
        Args:
            query: User query
            context: Context text
            response: Response text (for caching)
        
        Returns:
            MeasurementResult with detailed measurements
        """
        start_time = time.time()
        
        # Calculate baseline first
        baseline_tokens = self.token_counter.count_tokens(query + context)
        
        # Track optimization steps
        cache_hit = False
        optimization_applied = False
        truncation_applied = False
        
        # Check cache
        cache_key = query
        cached_response = self.cache.get(cache_key)
        
        if cached_response:
            cache_hit = True
            optimized_tokens = 0  # No tokens used
        else:
            # Apply optimization
            opt_result = self.optimizer.optimize(query)
            if opt_result["tokens_saved"] > 0:
                optimization_applied = True
                query = opt_result["optimized"]
            
            # Apply truncation if needed
            if context and len(context.split()) > 500:
                trunc_result = self.truncator.truncate(
                    context,
                    query,
                    max_tokens=2000
                )
                if trunc_result["tokens_saved"] > 0:
                    truncation_applied = True
                    context = trunc_result["truncated"]
            
            # Count optimized tokens
            optimized_tokens = self.token_counter.count_tokens(query + context)
            
            # Cache response
            if response:
                self.cache.set(cache_key, response)
        
        # Calculate savings
        tokens_saved = baseline_tokens - optimized_tokens
        savings_percent = (
            (tokens_saved / baseline_tokens * 100)
            if baseline_tokens > 0 else 0.0
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return MeasurementResult(
            query=query[:50] + "..." if len(query) > 50 else query,
            context=context[:50] + "..." if len(context) > 50 else context,
            baseline_tokens=baseline_tokens,
            optimized_tokens=optimized_tokens,
            tokens_saved=tokens_saved,
            savings_percent=savings_percent,
            cache_hit=cache_hit,
            optimization_applied=optimization_applied,
            truncation_applied=truncation_applied,
            latency_ms=latency_ms
        )
    
    def compare_measurements(
        self,
        queries: List[Tuple[str, str]]
    ) -> Dict:
        """
        Compare baseline vs optimized measurements for multiple queries.
        
        Args:
            queries: List of (query, context) tuples
        
        Returns:
            Comparison results with statistics
        """
        results = []
        
        for query, context in queries:
            result = self.measure_optimized(query, context)
            results.append(result)
        
        # Calculate statistics
        total_baseline = sum(r.baseline_tokens for r in results)
        total_optimized = sum(r.optimized_tokens for r in results)
        total_saved = total_baseline - total_optimized
        
        overall_savings = (
            (total_saved / total_baseline * 100)
            if total_baseline > 0 else 0.0
        )
        
        cache_hit_rate = sum(1 for r in results if r.cache_hit) / len(results)
        optimization_rate = sum(1 for r in results if r.optimization_applied) / len(results)
        truncation_rate = sum(1 for r in results if r.truncation_applied) / len(results)
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        return {
            "total_queries": len(results),
            "total_baseline_tokens": total_baseline,
            "total_optimized_tokens": total_optimized,
            "total_tokens_saved": total_saved,
            "overall_savings_percent": overall_savings,
            "cache_hit_rate": cache_hit_rate,
            "optimization_rate": optimization_rate,
            "truncation_rate": truncation_rate,
            "avg_latency_ms": avg_latency,
            "results": results
        }


def generate_sample_queries() -> List[Tuple[str, str]]:
    """Generate sample queries for demonstration."""
    return [
        (
            "Can you please explain how the caching system works?",
            "The caching system uses a multi-level approach with L1 and L2 caches. " * 20
        ),
        (
            "I would like to understand the optimization strategy",
            "The optimization strategy involves prompt compression and token reduction. " * 25
        ),
        (
            "What are the performance characteristics?",
            "Performance is measured in terms of latency and throughput. " * 15
        ),
        (
            "Please help me understand the architecture",
            "The architecture consists of multiple components working together. " * 30
        ),
        (
            "Can you explain how the caching system works?",  # Duplicate for cache hit
            "The caching system uses a multi-level approach. " * 10
        ),
        (
            "How does the token counting work?",
            "Token counting uses the tiktoken library for accurate measurements. " * 20
        ),
        (
            "What is the truncation strategy?",
            "Truncation preserves the most relevant content while reducing tokens. " * 25
        ),
        (
            "Please describe the monitoring system",
            "The monitoring system tracks metrics and health status. " * 15
        ),
        (
            "Can you help me with the optimization?",
            "Optimization reduces token usage while maintaining quality. " * 20
        ),
        (
            "What are the key features?",
            "Key features include caching, optimization, and truncation. " * 10
        ),
    ]


def run_interactive_demo():
    """Run interactive demonstration."""
    print("\n" + "="*60)
    print("SAVINGS MEASUREMENT DEMO")
    print("="*60)
    print("\nThis demo shows how token savings are measured.")
    print("Enter queries to see baseline vs optimized token counts.\n")
    
    framework = SavingsMeasurementFramework()
    
    while True:
        try:
            query = input("\nQuery (or 'quit' to exit): ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            context = input("Context (optional): ").strip()
            
            # Measure
            result = framework.measure_optimized(query, context)
            
            # Display results
            print("\n" + "-"*60)
            print(f"Baseline Tokens:    {result.baseline_tokens:,}")
            print(f"Optimized Tokens:   {result.optimized_tokens:,}")
            print(f"Tokens Saved:       {result.tokens_saved:,}")
            print(f"Savings:            {result.savings_percent:.1f}%")
            print(f"Cache Hit:          {result.cache_hit}")
            print(f"Optimization:       {result.optimization_applied}")
            print(f"Truncation:         {result.truncation_applied}")
            print(f"Latency:            {result.latency_ms:.2f}ms")
            print("-"*60)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue


def run_automated_demo(num_queries: int = 10):
    """Run automated demonstration with sample queries."""
    print("\n" + "="*60)
    print("AUTOMATED SAVINGS MEASUREMENT")
    print("="*60)
    print(f"\nMeasuring {num_queries} sample queries...\n")
    
    framework = SavingsMeasurementFramework()
    queries = generate_sample_queries()[:num_queries]
    
    # Run comparison
    comparison = framework.compare_measurements(queries)
    
    # Display results
    print("\n" + "="*60)
    print("MEASUREMENT RESULTS")
    print("="*60)
    print(f"\nTotal Queries:          {comparison['total_queries']}")
    print(f"Total Baseline Tokens:  {comparison['total_baseline_tokens']:,}")
    print(f"Total Optimized Tokens: {comparison['total_optimized_tokens']:,}")
    print(f"Total Tokens Saved:     {comparison['total_tokens_saved']:,}")
    print(f"Overall Savings:        {comparison['overall_savings_percent']:.1f}%")
    print(f"\nCache Hit Rate:         {comparison['cache_hit_rate']:.1%}")
    print(f"Optimization Rate:      {comparison['optimization_rate']:.1%}")
    print(f"Truncation Rate:        {comparison['truncation_rate']:.1%}")
    print(f"Avg Latency:            {comparison['avg_latency_ms']:.2f}ms")
    
    print("\n" + "-"*60)
    print("INDIVIDUAL RESULTS")
    print("-"*60)
    
    for i, result in enumerate(comparison['results'], 1):
        print(f"\nQuery {i}:")
        print(f"  Query: {result.query}")
        print(f"  Baseline: {result.baseline_tokens:,} tokens")
        print(f"  Optimized: {result.optimized_tokens:,} tokens")
        print(f"  Savings: {result.savings_percent:.1f}%")
        print(f"  Cache Hit: {result.cache_hit}")
    
    print("\n" + "="*60 + "\n")


def run_comparison_demo():
    """Run comparison between baseline and optimized modes."""
    print("\n" + "="*60)
    print("BASELINE VS OPTIMIZED COMPARISON")
    print("="*60)
    
    framework = SavingsMeasurementFramework()
    queries = generate_sample_queries()
    
    # Measure baseline
    print("\nMeasuring baseline (no optimization)...")
    baseline_total = 0
    baseline_latency = 0
    
    for query, context in queries:
        tokens, latency = framework.measure_baseline(query, context)
        baseline_total += tokens
        baseline_latency += latency
    
    baseline_avg_latency = baseline_latency / len(queries)
    
    # Measure optimized
    print("Measuring optimized (with optimization)...")
    comparison = framework.compare_measurements(queries)
    
    # Display comparison
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    print(f"\nBaseline Mode:")
    print(f"  Total Tokens:  {baseline_total:,}")
    print(f"  Avg Latency:   {baseline_avg_latency:.2f}ms")
    
    print(f"\nOptimized Mode:")
    print(f"  Total Tokens:  {comparison['total_optimized_tokens']:,}")
    print(f"  Tokens Saved:  {comparison['total_tokens_saved']:,}")
    print(f"  Savings:       {comparison['overall_savings_percent']:.1f}%")
    print(f"  Cache Hits:    {comparison['cache_hit_rate']:.1%}")
    print(f"  Avg Latency:   {comparison['avg_latency_ms']:.2f}ms")
    
    print(f"\nImprovement:")
    print(f"  Token Reduction:    {comparison['overall_savings_percent']:.1f}%")
    print(f"  Latency Overhead:   {comparison['avg_latency_ms'] - baseline_avg_latency:.2f}ms")
    
    print("\n" + "="*60 + "\n")


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="Savings Measurement Demo")
    parser.add_argument(
        "--automated",
        action="store_true",
        help="Run automated demo with sample queries"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=10,
        help="Number of queries for automated demo"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run baseline vs optimized comparison"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        run_comparison_demo()
    elif args.automated:
        run_automated_demo(args.queries)
    else:
        run_interactive_demo()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
