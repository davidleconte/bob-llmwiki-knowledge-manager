#!/usr/bin/env python3
"""
Test script for analysis and visualization tools.

Creates mock session data and tests all analysis/visualization features.

Usage:
    python3 test_analysis_tools.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analysis_and_reporting import SessionAnalyzer, ReportGenerator


def create_mock_session(session_id: str, mode: str, num_queries: int = 10) -> dict:
    """Create a mock session with realistic data."""
    start_time = datetime.now() - timedelta(hours=1)
    queries = []
    
    total_baseline_tokens = 0
    total_optimized_tokens = 0
    cache_hits = 0
    optimizations = 0
    truncations = 0
    
    for i in range(num_queries):
        # Generate realistic token counts
        baseline_tokens = random.randint(500, 2000)
        
        # Optimized mode has savings
        if mode == "optimized":
            # Cache hit (30% chance)
            if random.random() < 0.3:
                cache_hit = True
                cache_hits += 1
                # High savings from cache
                optimized_tokens = int(baseline_tokens * random.uniform(0.3, 0.5))
            else:
                cache_hit = False
                # Optimization applied (70% chance)
                if random.random() < 0.7:
                    optimizations += 1
                    optimized_tokens = int(baseline_tokens * random.uniform(0.7, 0.85))
                else:
                    optimized_tokens = int(baseline_tokens * random.uniform(0.85, 0.95))
            
            # Truncation applied (40% chance)
            truncation_applied = random.random() < 0.4
            if truncation_applied:
                truncations += 1
                optimized_tokens = int(optimized_tokens * random.uniform(0.8, 0.9))
        else:
            # Baseline mode: no optimization
            cache_hit = False
            truncation_applied = False
            optimized_tokens = baseline_tokens
        
        tokens_saved = baseline_tokens - optimized_tokens
        savings_percent = (tokens_saved / baseline_tokens * 100) if baseline_tokens > 0 else 0.0
        
        # Latency (optimized has slight overhead)
        if mode == "optimized":
            latency_ms = random.uniform(5, 15)
        else:
            latency_ms = random.uniform(2, 8)
        
        query = {
            "query_id": f"q{i+1:03d}",
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "query_text": f"Sample query {i+1}",
            "context_text": f"Sample context for query {i+1}",
            "baseline_tokens": baseline_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "savings_percent": savings_percent,
            "cache_hit": cache_hit,
            "optimization_applied": not cache_hit and mode == "optimized",
            "truncation_applied": truncation_applied,
            "latency_ms": latency_ms
        }
        
        queries.append(query)
        total_baseline_tokens += baseline_tokens
        total_optimized_tokens += optimized_tokens
    
    end_time = start_time + timedelta(minutes=num_queries*5)
    duration_seconds = (end_time - start_time).total_seconds()
    
    overall_savings = total_baseline_tokens - total_optimized_tokens
    overall_savings_percent = (overall_savings / total_baseline_tokens * 100) if total_baseline_tokens > 0 else 0.0
    
    cache_hit_rate = cache_hits / num_queries if num_queries > 0 else 0.0
    optimization_rate = optimizations / num_queries if num_queries > 0 else 0.0
    truncation_rate = truncations / num_queries if num_queries > 0 else 0.0
    
    avg_latency = sum(q["latency_ms"] for q in queries) / len(queries) if queries else 0.0
    
    return {
        "session_id": session_id,
        "mode": mode,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration_seconds,
        "total_queries": num_queries,
        "total_baseline_tokens": total_baseline_tokens,
        "total_optimized_tokens": total_optimized_tokens,
        "overall_savings_percent": overall_savings_percent,
        "cache_hit_rate": cache_hit_rate,
        "optimization_rate": optimization_rate,
        "truncation_rate": truncation_rate,
        "avg_latency_ms": avg_latency,
        "queries": queries
    }


def main():
    """Main test function."""
    print("=" * 80)
    print("TESTING ANALYSIS AND VISUALIZATION TOOLS")
    print("=" * 80)
    print()
    
    # Create test data directory
    data_dir = Path("evaluation/data/sessions")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating mock session data in: {data_dir}")
    print()
    
    # Create baseline sessions
    baseline_ids = []
    for i in range(5):
        session_id = f"test_baseline_{i+1:03d}"
        session = create_mock_session(session_id, "baseline", num_queries=random.randint(8, 12))
        
        # Save to file
        session_file = data_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        baseline_ids.append(session_id)
        print(f"✓ Created baseline session: {session_id}")
    
    print()
    
    # Create optimized sessions
    optimized_ids = []
    for i in range(5):
        session_id = f"test_optimized_{i+1:03d}"
        session = create_mock_session(session_id, "optimized", num_queries=random.randint(8, 12))
        
        # Save to file
        session_file = data_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        optimized_ids.append(session_id)
        print(f"✓ Created optimized session: {session_id}")
    
    print()
    print("=" * 80)
    print("TESTING ANALYSIS")
    print("=" * 80)
    print()
    
    # Test analyzer
    analyzer = SessionAnalyzer(str(data_dir))
    
    # Analyze baseline sessions
    print("Analyzing baseline sessions...")
    baseline_stats = analyzer.analyze_sessions(baseline_ids)
    print(f"✓ Baseline sessions: {baseline_stats.num_sessions}")
    print(f"  Total queries: {baseline_stats.total_queries}")
    print(f"  Total tokens: {baseline_stats.total_baseline_tokens:,}")
    print(f"  Mean latency: {baseline_stats.mean_latency_ms:.1f}ms")
    print()
    
    # Analyze optimized sessions
    print("Analyzing optimized sessions...")
    optimized_stats = analyzer.analyze_sessions(optimized_ids)
    print(f"✓ Optimized sessions: {optimized_stats.num_sessions}")
    print(f"  Total queries: {optimized_stats.total_queries}")
    print(f"  Total tokens: {optimized_stats.total_optimized_tokens:,}")
    print(f"  Tokens saved: {optimized_stats.total_tokens_saved:,}")
    print(f"  Overall savings: {optimized_stats.overall_savings_percent:.1f}%")
    print(f"  Cache hit rate: {optimized_stats.mean_cache_hit_rate:.1%}")
    print(f"  Mean latency: {optimized_stats.mean_latency_ms:.1f}ms")
    print()
    
    # Compare sessions
    print("Comparing baseline vs optimized...")
    comparison = analyzer.compare_sessions(baseline_ids, optimized_ids)
    print(f"✓ Token reduction: {comparison.token_reduction_percent:.1f}%")
    print(f"  Cache effectiveness: {comparison.cache_effectiveness:.1%}")
    print(f"  Optimization effectiveness: {comparison.optimization_effectiveness:.1%}")
    print(f"  Latency overhead: {comparison.latency_overhead_ms:.1f}ms")
    print(f"  Statistical significance: {'Yes' if comparison.is_significant else 'No'}")
    print()
    
    print("=" * 80)
    print("TESTING REPORT GENERATION")
    print("=" * 80)
    print()
    
    # Test report generator
    generator = ReportGenerator(analyzer)
    
    # Generate text report
    print("Generating text report...")
    text_report = generator.generate_text_report(comparison)
    report_file = Path("reports/test_report.txt")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(text_report)
    print(f"✓ Text report saved: {report_file}")
    print()
    
    # Generate HTML report
    print("Generating HTML report...")
    html_file = Path("reports/test_report.html")
    generator.generate_html_report(comparison, str(html_file))
    print(f"✓ HTML report saved: {html_file}")
    print()
    
    # Export CSV
    print("Exporting CSV...")
    csv_file = Path("reports/test_sessions.csv")
    generator.export_csv(baseline_ids + optimized_ids, str(csv_file))
    print(f"✓ CSV exported: {csv_file}")
    print()
    
    # Export JSON
    print("Exporting JSON...")
    json_file = Path("reports/test_sessions.json")
    generator.export_json(baseline_ids + optimized_ids, str(json_file))
    print(f"✓ JSON exported: {json_file}")
    print()
    
    print("=" * 80)
    print("TESTING VISUALIZATION")
    print("=" * 80)
    print()
    
    # Test visualization (if matplotlib available)
    try:
        from visualization import SessionVisualizer
        
        visualizer = SessionVisualizer(str(data_dir))
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        print("Generating visualizations...")
        
        # Savings comparison
        print("  - Savings comparison chart...")
        visualizer.plot_savings_comparison(
            baseline_ids, optimized_ids,
            str(reports_dir / "test_savings_comparison.png")
        )
        
        # Cache effectiveness
        print("  - Cache effectiveness chart...")
        visualizer.plot_cache_effectiveness(
            optimized_ids,
            str(reports_dir / "test_cache_effectiveness.png")
        )
        
        # Latency distribution
        print("  - Latency distribution chart...")
        visualizer.plot_latency_distribution(
            baseline_ids, optimized_ids,
            str(reports_dir / "test_latency_distribution.png")
        )
        
        # Savings over time
        print("  - Savings over time chart...")
        visualizer.plot_savings_over_time(
            optimized_ids,
            str(reports_dir / "test_savings_over_time.png")
        )
        
        # Dashboard
        print("  - Comprehensive dashboard...")
        visualizer.create_dashboard(
            baseline_ids, optimized_ids,
            str(reports_dir / "test_dashboard.png")
        )
        
        print()
        print(f"✓ All visualizations saved to: {reports_dir}")
        print()
        
    except ImportError:
        print("⚠️  Matplotlib not available. Skipping visualization tests.")
        print("   Install with: pip install matplotlib")
        print()
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print("✅ All tests passed!")
    print()
    print("Generated files:")
    print(f"  - Mock sessions: {data_dir}")
    print(f"  - Reports: reports/")
    print()
    print("Next steps:")
    print("  1. Review generated reports and visualizations")
    print("  2. Verify analysis calculations are correct")
    print("  3. Test with real session data when available")
    print()
    print("To clean up test data:")
    print(f"  rm -rf {data_dir}/test_*")
    print("  rm -rf reports/test_*")
    print()


if __name__ == '__main__':
    main()
