#!/usr/bin/env python3
"""
Analysis and Reporting Tools for Phase 3 Validation

This module provides comprehensive analysis and reporting capabilities for
comparing baseline and optimized measurements. It includes:
- Statistical analysis (mean, median, p95, confidence intervals)
- Visualization (charts, graphs, dashboards)
- Comparison reports (baseline vs optimized)
- Export formats (CSV, JSON, HTML reports)

Usage:
    # Analyze sessions
    python3 analysis_and_reporting.py --analyze \
        --baseline baseline_001 baseline_002 \
        --optimized optimized_001 optimized_002

    # Generate report
    python3 analysis_and_reporting.py --report \
        --baseline baseline_001 baseline_002 \
        --optimized optimized_001 optimized_002 \
        --output report.html

    # Export data
    python3 analysis_and_reporting.py --export \
        --baseline baseline_001 baseline_002 \
        --format csv \
        --output data.csv
"""

import argparse
import json
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sys

# Try to import optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available. Some statistical features will be limited.", file=sys.stderr)

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Visualization features will be disabled.", file=sys.stderr)


@dataclass
class SessionStats:
    """Statistics for a single session."""
    session_id: str
    mode: str
    total_queries: int
    total_baseline_tokens: int
    total_optimized_tokens: int
    tokens_saved: int
    savings_percent: float
    cache_hit_rate: float
    optimization_rate: float
    truncation_rate: float
    avg_latency_ms: float
    duration_seconds: float


@dataclass
class AggregateStats:
    """Aggregate statistics across multiple sessions."""
    num_sessions: int
    total_queries: int
    
    # Token statistics
    total_baseline_tokens: int
    total_optimized_tokens: int
    total_tokens_saved: int
    overall_savings_percent: float
    
    # Savings distribution
    mean_savings_percent: float
    median_savings_percent: float
    p95_savings_percent: float
    min_savings_percent: float
    max_savings_percent: float
    
    # Cache statistics
    mean_cache_hit_rate: float
    median_cache_hit_rate: float
    
    # Optimization statistics
    mean_optimization_rate: float
    median_optimization_rate: float
    
    # Truncation statistics
    mean_truncation_rate: float
    median_truncation_rate: float
    
    # Latency statistics
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    
    # Confidence intervals (95%)
    savings_ci_lower: float
    savings_ci_upper: float


@dataclass
class ComparisonReport:
    """Comparison report between baseline and optimized sessions."""
    baseline_stats: AggregateStats
    optimized_stats: AggregateStats
    
    # Improvements
    token_reduction_percent: float
    cache_effectiveness: float
    optimization_effectiveness: float
    latency_overhead_ms: float
    
    # Statistical significance
    is_significant: bool
    confidence_level: float
    
    # Recommendations
    recommendations: List[str]


class SessionAnalyzer:
    """Analyzes session data and generates statistics."""
    
    def __init__(self, data_dir: str = "evaluation/data/sessions"):
        """Initialize analyzer with data directory."""
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session from disk."""
        session_file = self.data_dir / f"{session_id}.json"
        if not session_file.exists():
            print(f"Warning: Session file not found: {session_file}", file=sys.stderr)
            return None
        
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}", file=sys.stderr)
            return None
    
    def extract_stats(self, session_data: Dict[str, Any]) -> SessionStats:
        """Extract statistics from session data."""
        return SessionStats(
            session_id=session_data['session_id'],
            mode=session_data['mode'],
            total_queries=session_data['total_queries'],
            total_baseline_tokens=session_data['total_baseline_tokens'],
            total_optimized_tokens=session_data['total_optimized_tokens'],
            tokens_saved=session_data['total_baseline_tokens'] - session_data['total_optimized_tokens'],
            savings_percent=session_data['overall_savings_percent'],
            cache_hit_rate=session_data['cache_hit_rate'],
            optimization_rate=session_data['optimization_rate'],
            truncation_rate=session_data['truncation_rate'],
            avg_latency_ms=session_data['avg_latency_ms'],
            duration_seconds=session_data['duration_seconds']
        )
    
    def analyze_sessions(self, session_ids: List[str]) -> AggregateStats:
        """Analyze multiple sessions and compute aggregate statistics."""
        sessions = []
        for session_id in session_ids:
            session_data = self.load_session(session_id)
            if session_data:
                sessions.append(self.extract_stats(session_data))
        
        if not sessions:
            raise ValueError("No valid sessions found")
        
        # Compute aggregate statistics
        num_sessions = len(sessions)
        total_queries = sum(s.total_queries for s in sessions)
        total_baseline_tokens = sum(s.total_baseline_tokens for s in sessions)
        total_optimized_tokens = sum(s.total_optimized_tokens for s in sessions)
        total_tokens_saved = total_baseline_tokens - total_optimized_tokens
        overall_savings_percent = (total_tokens_saved / total_baseline_tokens * 100) if total_baseline_tokens > 0 else 0.0
        
        # Savings distribution
        savings_percents = [s.savings_percent for s in sessions]
        mean_savings = statistics.mean(savings_percents)
        median_savings = statistics.median(savings_percents)
        min_savings = min(savings_percents)
        max_savings = max(savings_percents)
        
        # P95 savings
        if HAS_NUMPY:
            p95_savings = float(np.percentile(savings_percents, 95))
        else:
            sorted_savings = sorted(savings_percents)
            p95_idx = int(len(sorted_savings) * 0.95)
            p95_savings = sorted_savings[min(p95_idx, len(sorted_savings) - 1)]
        
        # Cache statistics
        cache_rates = [s.cache_hit_rate for s in sessions]
        mean_cache = statistics.mean(cache_rates)
        median_cache = statistics.median(cache_rates)
        
        # Optimization statistics
        opt_rates = [s.optimization_rate for s in sessions]
        mean_opt = statistics.mean(opt_rates)
        median_opt = statistics.median(opt_rates)
        
        # Truncation statistics
        trunc_rates = [s.truncation_rate for s in sessions]
        mean_trunc = statistics.mean(trunc_rates)
        median_trunc = statistics.median(trunc_rates)
        
        # Latency statistics
        latencies = [s.avg_latency_ms for s in sessions]
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        
        if HAS_NUMPY:
            p95_latency = float(np.percentile(latencies, 95))
        else:
            sorted_latencies = sorted(latencies)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)]
        
        # Confidence intervals (95%)
        if len(savings_percents) > 1:
            stdev = statistics.stdev(savings_percents)
            stderr = stdev / (len(savings_percents) ** 0.5)
            # 1.96 is the z-score for 95% confidence
            margin = 1.96 * stderr
            ci_lower = mean_savings - margin
            ci_upper = mean_savings + margin
        else:
            ci_lower = mean_savings
            ci_upper = mean_savings
        
        return AggregateStats(
            num_sessions=num_sessions,
            total_queries=total_queries,
            total_baseline_tokens=total_baseline_tokens,
            total_optimized_tokens=total_optimized_tokens,
            total_tokens_saved=total_tokens_saved,
            overall_savings_percent=overall_savings_percent,
            mean_savings_percent=mean_savings,
            median_savings_percent=median_savings,
            p95_savings_percent=p95_savings,
            min_savings_percent=min_savings,
            max_savings_percent=max_savings,
            mean_cache_hit_rate=mean_cache,
            median_cache_hit_rate=median_cache,
            mean_optimization_rate=mean_opt,
            median_optimization_rate=median_opt,
            mean_truncation_rate=mean_trunc,
            median_truncation_rate=median_trunc,
            mean_latency_ms=mean_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            savings_ci_lower=ci_lower,
            savings_ci_upper=ci_upper
        )
    
    def compare_sessions(
        self,
        baseline_ids: List[str],
        optimized_ids: List[str]
    ) -> ComparisonReport:
        """Compare baseline and optimized sessions."""
        baseline_stats = self.analyze_sessions(baseline_ids)
        optimized_stats = self.analyze_sessions(optimized_ids)
        
        # Calculate improvements
        token_reduction = (
            (baseline_stats.total_baseline_tokens - optimized_stats.total_optimized_tokens)
            / baseline_stats.total_baseline_tokens * 100
        )
        
        cache_effectiveness = optimized_stats.mean_cache_hit_rate
        optimization_effectiveness = optimized_stats.mean_optimization_rate
        latency_overhead = optimized_stats.mean_latency_ms - baseline_stats.mean_latency_ms
        
        # Statistical significance (simple t-test approximation)
        # If confidence intervals don't overlap, it's significant
        is_significant = (
            baseline_stats.savings_ci_lower > optimized_stats.savings_ci_upper or
            baseline_stats.savings_ci_upper < optimized_stats.savings_ci_lower
        )
        confidence_level = 0.95
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            baseline_stats, optimized_stats, token_reduction,
            cache_effectiveness, optimization_effectiveness, latency_overhead
        )
        
        return ComparisonReport(
            baseline_stats=baseline_stats,
            optimized_stats=optimized_stats,
            token_reduction_percent=token_reduction,
            cache_effectiveness=cache_effectiveness,
            optimization_effectiveness=optimization_effectiveness,
            latency_overhead_ms=latency_overhead,
            is_significant=is_significant,
            confidence_level=confidence_level,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        baseline: AggregateStats,
        optimized: AggregateStats,
        token_reduction: float,
        cache_effectiveness: float,
        optimization_effectiveness: float,
        latency_overhead: float
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Token savings
        if token_reduction > 30:
            recommendations.append(
                f"✅ Excellent token reduction ({token_reduction:.1f}%). "
                "System is highly effective."
            )
        elif token_reduction > 15:
            recommendations.append(
                f"✅ Good token reduction ({token_reduction:.1f}%). "
                "Consider increasing cache size for better results."
            )
        else:
            recommendations.append(
                f"⚠️ Moderate token reduction ({token_reduction:.1f}%). "
                "Review optimization strategies and cache configuration."
            )
        
        # Cache effectiveness
        if cache_effectiveness > 0.5:
            recommendations.append(
                f"✅ High cache hit rate ({cache_effectiveness:.1%}). "
                "Cache is working well."
            )
        elif cache_effectiveness > 0.3:
            recommendations.append(
                f"⚠️ Moderate cache hit rate ({cache_effectiveness:.1%}). "
                "Consider increasing cache size or adjusting similarity threshold."
            )
        else:
            recommendations.append(
                f"❌ Low cache hit rate ({cache_effectiveness:.1%}). "
                "Review cache configuration and query patterns."
            )
        
        # Optimization effectiveness
        if optimization_effectiveness > 0.7:
            recommendations.append(
                f"✅ High optimization rate ({optimization_effectiveness:.1%}). "
                "Prompt optimization is effective."
            )
        elif optimization_effectiveness > 0.5:
            recommendations.append(
                f"⚠️ Moderate optimization rate ({optimization_effectiveness:.1%}). "
                "Some prompts may not benefit from optimization."
            )
        else:
            recommendations.append(
                f"❌ Low optimization rate ({optimization_effectiveness:.1%}). "
                "Review optimization strategies and prompt patterns."
            )
        
        # Latency overhead
        if latency_overhead < 10:
            recommendations.append(
                f"✅ Minimal latency overhead ({latency_overhead:.1f}ms). "
                "Performance impact is negligible."
            )
        elif latency_overhead < 50:
            recommendations.append(
                f"⚠️ Moderate latency overhead ({latency_overhead:.1f}ms). "
                "Consider optimizing cache lookup performance."
            )
        else:
            recommendations.append(
                f"❌ High latency overhead ({latency_overhead:.1f}ms). "
                "Review cache implementation and consider async operations."
            )
        
        return recommendations


class ReportGenerator:
    """Generates reports in various formats."""
    
    def __init__(self, analyzer: SessionAnalyzer):
        """Initialize report generator."""
        self.analyzer = analyzer
    
    def generate_text_report(self, comparison: ComparisonReport) -> str:
        """Generate a text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("PHASE 3 VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Baseline statistics
        lines.append("BASELINE STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Sessions: {comparison.baseline_stats.num_sessions}")
        lines.append(f"Total Queries: {comparison.baseline_stats.total_queries}")
        lines.append(f"Total Tokens: {comparison.baseline_stats.total_baseline_tokens:,}")
        lines.append(f"Mean Latency: {comparison.baseline_stats.mean_latency_ms:.1f}ms")
        lines.append("")
        
        # Optimized statistics
        lines.append("OPTIMIZED STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Sessions: {comparison.optimized_stats.num_sessions}")
        lines.append(f"Total Queries: {comparison.optimized_stats.total_queries}")
        lines.append(f"Total Tokens: {comparison.optimized_stats.total_optimized_tokens:,}")
        lines.append(f"Tokens Saved: {comparison.optimized_stats.total_tokens_saved:,}")
        lines.append(f"Savings: {comparison.optimized_stats.overall_savings_percent:.1f}%")
        lines.append(f"Cache Hit Rate: {comparison.optimized_stats.mean_cache_hit_rate:.1%}")
        lines.append(f"Optimization Rate: {comparison.optimized_stats.mean_optimization_rate:.1%}")
        lines.append(f"Mean Latency: {comparison.optimized_stats.mean_latency_ms:.1f}ms")
        lines.append("")
        
        # Comparison
        lines.append("COMPARISON")
        lines.append("-" * 80)
        lines.append(f"Token Reduction: {comparison.token_reduction_percent:.1f}%")
        lines.append(f"Cache Effectiveness: {comparison.cache_effectiveness:.1%}")
        lines.append(f"Optimization Effectiveness: {comparison.optimization_effectiveness:.1%}")
        lines.append(f"Latency Overhead: {comparison.latency_overhead_ms:.1f}ms")
        lines.append(f"Statistical Significance: {'Yes' if comparison.is_significant else 'No'}")
        lines.append(f"Confidence Level: {comparison.confidence_level:.0%}")
        lines.append("")
        
        # Savings distribution
        lines.append("SAVINGS DISTRIBUTION")
        lines.append("-" * 80)
        lines.append(f"Mean: {comparison.optimized_stats.mean_savings_percent:.1f}%")
        lines.append(f"Median: {comparison.optimized_stats.median_savings_percent:.1f}%")
        lines.append(f"P95: {comparison.optimized_stats.p95_savings_percent:.1f}%")
        lines.append(f"Min: {comparison.optimized_stats.min_savings_percent:.1f}%")
        lines.append(f"Max: {comparison.optimized_stats.max_savings_percent:.1f}%")
        lines.append(f"95% CI: [{comparison.optimized_stats.savings_ci_lower:.1f}%, "
                    f"{comparison.optimized_stats.savings_ci_upper:.1f}%]")
        lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for i, rec in enumerate(comparison.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def generate_html_report(self, comparison: ComparisonReport, output_file: str):
        """Generate an HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Phase 3 Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .good {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .bad {{ color: #F44336; }}
        .recommendation {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #2196F3; }}
    </style>
</head>
<body>
    <h1>Phase 3 Validation Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Summary</h2>
    <div class="metric">
        Token Reduction: {comparison.token_reduction_percent:.1f}%
    </div>
    <div class="metric">
        Tokens Saved: {comparison.optimized_stats.total_tokens_saved:,}
    </div>
    
    <h2>Baseline Statistics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Sessions</td><td>{comparison.baseline_stats.num_sessions}</td></tr>
        <tr><td>Total Queries</td><td>{comparison.baseline_stats.total_queries}</td></tr>
        <tr><td>Total Tokens</td><td>{comparison.baseline_stats.total_baseline_tokens:,}</td></tr>
        <tr><td>Mean Latency</td><td>{comparison.baseline_stats.mean_latency_ms:.1f}ms</td></tr>
    </table>
    
    <h2>Optimized Statistics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Sessions</td><td>{comparison.optimized_stats.num_sessions}</td></tr>
        <tr><td>Total Queries</td><td>{comparison.optimized_stats.total_queries}</td></tr>
        <tr><td>Total Tokens</td><td>{comparison.optimized_stats.total_optimized_tokens:,}</td></tr>
        <tr><td>Tokens Saved</td><td>{comparison.optimized_stats.total_tokens_saved:,}</td></tr>
        <tr><td>Savings</td><td>{comparison.optimized_stats.overall_savings_percent:.1f}%</td></tr>
        <tr><td>Cache Hit Rate</td><td>{comparison.optimized_stats.mean_cache_hit_rate:.1%}</td></tr>
        <tr><td>Optimization Rate</td><td>{comparison.optimized_stats.mean_optimization_rate:.1%}</td></tr>
        <tr><td>Mean Latency</td><td>{comparison.optimized_stats.mean_latency_ms:.1f}ms</td></tr>
    </table>
    
    <h2>Savings Distribution</h2>
    <table>
        <tr><th>Statistic</th><th>Value</th></tr>
        <tr><td>Mean</td><td>{comparison.optimized_stats.mean_savings_percent:.1f}%</td></tr>
        <tr><td>Median</td><td>{comparison.optimized_stats.median_savings_percent:.1f}%</td></tr>
        <tr><td>P95</td><td>{comparison.optimized_stats.p95_savings_percent:.1f}%</td></tr>
        <tr><td>Min</td><td>{comparison.optimized_stats.min_savings_percent:.1f}%</td></tr>
        <tr><td>Max</td><td>{comparison.optimized_stats.max_savings_percent:.1f}%</td></tr>
        <tr><td>95% CI</td><td>[{comparison.optimized_stats.savings_ci_lower:.1f}%, {comparison.optimized_stats.savings_ci_upper:.1f}%]</td></tr>
    </table>
    
    <h2>Recommendations</h2>
"""
        for rec in comparison.recommendations:
            html += f'    <div class="recommendation">{rec}</div>\n'
        
        html += """
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"HTML report generated: {output_file}")
    
    def export_csv(self, session_ids: List[str], output_file: str):
        """Export session data to CSV."""
        import csv
        
        sessions = []
        for session_id in session_ids:
            session_data = self.analyzer.load_session(session_id)
            if session_data:
                sessions.append(self.analyzer.extract_stats(session_data))
        
        if not sessions:
            print("No sessions to export", file=sys.stderr)
            return
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(sessions[0]).keys())
            writer.writeheader()
            for session in sessions:
                writer.writerow(asdict(session))
        
        print(f"CSV exported: {output_file}")
    
    def export_json(self, session_ids: List[str], output_file: str):
        """Export session data to JSON."""
        sessions = []
        for session_id in session_ids:
            session_data = self.analyzer.load_session(session_id)
            if session_data:
                sessions.append(asdict(self.analyzer.extract_stats(session_data)))
        
        if not sessions:
            print("No sessions to export", file=sys.stderr)
            return
        
        with open(output_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        print(f"JSON exported: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analysis and reporting tools for Phase 3 validation"
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze sessions and print statistics'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comparison report'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export session data'
    )
    
    parser.add_argument(
        '--baseline',
        nargs='+',
        help='Baseline session IDs'
    )
    
    parser.add_argument(
        '--optimized',
        nargs='+',
        help='Optimized session IDs'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'html', 'csv', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    
    parser.add_argument(
        '--data-dir',
        default='evaluation/data/sessions',
        help='Data directory (default: evaluation/data/sessions)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = SessionAnalyzer(args.data_dir)
    generator = ReportGenerator(analyzer)
    
    # Analyze sessions
    if args.analyze:
        if not args.baseline and not args.optimized:
            print("Error: Specify --baseline or --optimized session IDs", file=sys.stderr)
            return 1
        
        if args.baseline:
            print("\nBASELINE ANALYSIS")
            print("=" * 80)
            stats = analyzer.analyze_sessions(args.baseline)
            print(f"Sessions: {stats.num_sessions}")
            print(f"Total Queries: {stats.total_queries}")
            print(f"Total Tokens: {stats.total_baseline_tokens:,}")
            print(f"Mean Savings: {stats.mean_savings_percent:.1f}%")
            print(f"Median Savings: {stats.median_savings_percent:.1f}%")
            print(f"P95 Savings: {stats.p95_savings_percent:.1f}%")
            print(f"Mean Latency: {stats.mean_latency_ms:.1f}ms")
        
        if args.optimized:
            print("\nOPTIMIZED ANALYSIS")
            print("=" * 80)
            stats = analyzer.analyze_sessions(args.optimized)
            print(f"Sessions: {stats.num_sessions}")
            print(f"Total Queries: {stats.total_queries}")
            print(f"Total Tokens: {stats.total_optimized_tokens:,}")
            print(f"Tokens Saved: {stats.total_tokens_saved:,}")
            print(f"Overall Savings: {stats.overall_savings_percent:.1f}%")
            print(f"Mean Savings: {stats.mean_savings_percent:.1f}%")
            print(f"Cache Hit Rate: {stats.mean_cache_hit_rate:.1%}")
            print(f"Optimization Rate: {stats.mean_optimization_rate:.1%}")
            print(f"Mean Latency: {stats.mean_latency_ms:.1f}ms")
    
    # Generate report
    if args.report:
        if not args.baseline or not args.optimized:
            print("Error: Specify both --baseline and --optimized session IDs", file=sys.stderr)
            return 1
        
        comparison = analyzer.compare_sessions(args.baseline, args.optimized)
        
        if args.format == 'text':
            report = generator.generate_text_report(comparison)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Report saved to: {args.output}")
            else:
                print(report)
        
        elif args.format == 'html':
            if not args.output:
                args.output = 'validation_report.html'
            generator.generate_html_report(comparison, args.output)
    
    # Export data
    if args.export:
        if not args.baseline and not args.optimized:
            print("Error: Specify --baseline or --optimized session IDs", file=sys.stderr)
            return 1
        
        session_ids = (args.baseline or []) + (args.optimized or [])
        
        if args.format == 'csv':
            if not args.output:
                args.output = 'sessions.csv'
            generator.export_csv(session_ids, args.output)
        
        elif args.format == 'json':
            if not args.output:
                args.output = 'sessions.json'
            generator.export_json(session_ids, args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
