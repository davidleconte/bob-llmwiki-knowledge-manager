#!/usr/bin/env python3
"""
Visualization Tools for Phase 3 Validation

This module provides visualization capabilities for session analysis:
- Token savings charts
- Cache effectiveness graphs
- Latency distribution plots
- Comparison dashboards

Usage:
    # Generate all visualizations
    python3 visualization.py --all \
        --baseline baseline_001 baseline_002 \
        --optimized optimized_001 optimized_002 \
        --output-dir reports/

    # Generate specific chart
    python3 visualization.py --savings-chart \
        --baseline baseline_001 \
        --optimized optimized_001 \
        --output savings.png
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Error: matplotlib is required for visualization", file=sys.stderr)
    print("Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)

# Try to import numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available. Some features will be limited.", file=sys.stderr)


class SessionVisualizer:
    """Creates visualizations for session analysis."""
    
    def __init__(self, data_dir: str = "evaluation/data/sessions"):
        """Initialize visualizer with data directory."""
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {data_dir}")
    
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
    
    def load_sessions(self, session_ids: List[str]) -> List[Dict[str, Any]]:
        """Load multiple sessions."""
        sessions = []
        for session_id in session_ids:
            session = self.load_session(session_id)
            if session:
                sessions.append(session)
        return sessions
    
    def plot_savings_comparison(
        self,
        baseline_ids: List[str],
        optimized_ids: List[str],
        output_file: str
    ):
        """Plot token savings comparison."""
        baseline_sessions = self.load_sessions(baseline_ids)
        optimized_sessions = self.load_sessions(optimized_ids)
        
        if not baseline_sessions or not optimized_sessions:
            print("Error: No sessions to plot", file=sys.stderr)
            return
        
        # Extract data
        baseline_tokens = [s['total_baseline_tokens'] for s in baseline_sessions]
        optimized_tokens = [s['total_optimized_tokens'] for s in optimized_sessions]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Bar chart: Total tokens
        x = range(len(baseline_sessions))
        width = 0.35
        ax1.bar([i - width/2 for i in x], baseline_tokens, width, label='Baseline', color='#FF6B6B')
        ax1.bar([i + width/2 for i in x], optimized_tokens, width, label='Optimized', color='#4ECDC4')
        ax1.set_xlabel('Session')
        ax1.set_ylabel('Total Tokens')
        ax1.set_title('Token Usage: Baseline vs Optimized')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Savings percentage
        savings = [(b - o) / b * 100 for b, o in zip(baseline_tokens, optimized_tokens)]
        ax2.bar(x, savings, color='#95E1D3')
        ax2.axhline(y=sum(savings)/len(savings), color='r', linestyle='--', label=f'Mean: {sum(savings)/len(savings):.1f}%')
        ax2.set_xlabel('Session')
        ax2.set_ylabel('Savings (%)')
        ax2.set_title('Token Savings per Session')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Savings comparison chart saved: {output_file}")
    
    def plot_cache_effectiveness(
        self,
        session_ids: List[str],
        output_file: str
    ):
        """Plot cache effectiveness metrics."""
        sessions = self.load_sessions(session_ids)
        
        if not sessions:
            print("Error: No sessions to plot", file=sys.stderr)
            return
        
        # Extract data
        cache_hit_rates = [s['cache_hit_rate'] * 100 for s in sessions]
        optimization_rates = [s['optimization_rate'] * 100 for s in sessions]
        truncation_rates = [s['truncation_rate'] * 100 for s in sessions]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(sessions))
        width = 0.25
        
        ax.bar([i - width for i in x], cache_hit_rates, width, label='Cache Hit Rate', color='#4ECDC4')
        ax.bar(x, optimization_rates, width, label='Optimization Rate', color='#95E1D3')
        ax.bar([i + width for i in x], truncation_rates, width, label='Truncation Rate', color='#F38181')
        
        ax.set_xlabel('Session')
        ax.set_ylabel('Rate (%)')
        ax.set_title('Cache and Optimization Effectiveness')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Cache effectiveness chart saved: {output_file}")
    
    def plot_latency_distribution(
        self,
        baseline_ids: List[str],
        optimized_ids: List[str],
        output_file: str
    ):
        """Plot latency distribution comparison."""
        baseline_sessions = self.load_sessions(baseline_ids)
        optimized_sessions = self.load_sessions(optimized_ids)
        
        if not baseline_sessions or not optimized_sessions:
            print("Error: No sessions to plot", file=sys.stderr)
            return
        
        # Extract latencies from all queries
        baseline_latencies = []
        for session in baseline_sessions:
            for query in session.get('queries', []):
                baseline_latencies.append(query['latency_ms'])
        
        optimized_latencies = []
        for session in optimized_sessions:
            for query in session.get('queries', []):
                optimized_latencies.append(query['latency_ms'])
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram
        ax1.hist(baseline_latencies, bins=30, alpha=0.5, label='Baseline', color='#FF6B6B')
        ax1.hist(optimized_latencies, bins=30, alpha=0.5, label='Optimized', color='#4ECDC4')
        ax1.set_xlabel('Latency (ms)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Latency Distribution')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Box plot
        bp = ax2.boxplot([baseline_latencies, optimized_latencies])
        ax2.set_xticklabels(['Baseline', 'Optimized'])
        ax2.set_ylabel('Latency (ms)')
        ax2.set_title('Latency Comparison')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Latency distribution chart saved: {output_file}")
    
    def plot_savings_over_time(
        self,
        session_ids: List[str],
        output_file: str
    ):
        """Plot token savings over time."""
        sessions = self.load_sessions(session_ids)
        
        if not sessions:
            print("Error: No sessions to plot", file=sys.stderr)
            return
        
        # Extract cumulative savings
        cumulative_baseline = 0
        cumulative_optimized = 0
        cumulative_savings = []
        session_numbers = []
        
        for i, session in enumerate(sessions, 1):
            cumulative_baseline += session['total_baseline_tokens']
            cumulative_optimized += session['total_optimized_tokens']
            savings_percent = (cumulative_baseline - cumulative_optimized) / cumulative_baseline * 100
            cumulative_savings.append(savings_percent)
            session_numbers.append(i)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(session_numbers, cumulative_savings, marker='o', linewidth=2, markersize=8, color='#4ECDC4')
        ax.fill_between(session_numbers, cumulative_savings, alpha=0.3, color='#4ECDC4')
        ax.set_xlabel('Session Number')
        ax.set_ylabel('Cumulative Savings (%)')
        ax.set_title('Token Savings Over Time')
        ax.grid(True, alpha=0.3)
        
        # Add final savings annotation
        final_savings = cumulative_savings[-1]
        ax.annotate(
            f'Final: {final_savings:.1f}%',
            xy=(session_numbers[-1], final_savings),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
        )
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Savings over time chart saved: {output_file}")
    
    def create_dashboard(
        self,
        baseline_ids: List[str],
        optimized_ids: List[str],
        output_file: str
    ):
        """Create a comprehensive dashboard with multiple visualizations."""
        baseline_sessions = self.load_sessions(baseline_ids)
        optimized_sessions = self.load_sessions(optimized_ids)
        
        if not baseline_sessions or not optimized_sessions:
            print("Error: No sessions to plot", file=sys.stderr)
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Token usage comparison
        ax1 = fig.add_subplot(gs[0, 0])
        baseline_tokens = [s['total_baseline_tokens'] for s in baseline_sessions]
        optimized_tokens = [s['total_optimized_tokens'] for s in optimized_sessions]
        x = range(len(baseline_sessions))
        width = 0.35
        ax1.bar([i - width/2 for i in x], baseline_tokens, width, label='Baseline', color='#FF6B6B')
        ax1.bar([i + width/2 for i in x], optimized_tokens, width, label='Optimized', color='#4ECDC4')
        ax1.set_xlabel('Session')
        ax1.set_ylabel('Total Tokens')
        ax1.set_title('Token Usage Comparison')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Savings percentage
        ax2 = fig.add_subplot(gs[0, 1])
        savings = [(b - o) / b * 100 for b, o in zip(baseline_tokens, optimized_tokens)]
        ax2.bar(x, savings, color='#95E1D3')
        ax2.axhline(y=sum(savings)/len(savings), color='r', linestyle='--', 
                   label=f'Mean: {sum(savings)/len(savings):.1f}%')
        ax2.set_xlabel('Session')
        ax2.set_ylabel('Savings (%)')
        ax2.set_title('Token Savings per Session')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Cache effectiveness
        ax3 = fig.add_subplot(gs[1, 0])
        cache_hit_rates = [s['cache_hit_rate'] * 100 for s in optimized_sessions]
        optimization_rates = [s['optimization_rate'] * 100 for s in optimized_sessions]
        x_opt = range(len(optimized_sessions))
        width = 0.35
        ax3.bar([i - width/2 for i in x_opt], cache_hit_rates, width, label='Cache Hit Rate', color='#4ECDC4')
        ax3.bar([i + width/2 for i in x_opt], optimization_rates, width, label='Optimization Rate', color='#95E1D3')
        ax3.set_xlabel('Session')
        ax3.set_ylabel('Rate (%)')
        ax3.set_title('Cache and Optimization Effectiveness')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        ax3.set_ylim(0, 100)
        
        # 4. Latency comparison
        ax4 = fig.add_subplot(gs[1, 1])
        baseline_latencies = []
        for session in baseline_sessions:
            for query in session.get('queries', []):
                baseline_latencies.append(query['latency_ms'])
        optimized_latencies = []
        for session in optimized_sessions:
            for query in session.get('queries', []):
                optimized_latencies.append(query['latency_ms'])
        bp = ax4.boxplot([baseline_latencies, optimized_latencies])
        ax4.set_xticklabels(['Baseline', 'Optimized'])
        ax4.set_ylabel('Latency (ms)')
        ax4.set_title('Latency Comparison')
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. Cumulative savings
        ax5 = fig.add_subplot(gs[2, :])
        cumulative_baseline = 0
        cumulative_optimized = 0
        cumulative_savings = []
        session_numbers = []
        for i, (b_session, o_session) in enumerate(zip(baseline_sessions, optimized_sessions), 1):
            cumulative_baseline += b_session['total_baseline_tokens']
            cumulative_optimized += o_session['total_optimized_tokens']
            savings_percent = (cumulative_baseline - cumulative_optimized) / cumulative_baseline * 100
            cumulative_savings.append(savings_percent)
            session_numbers.append(i)
        ax5.plot(session_numbers, cumulative_savings, marker='o', linewidth=2, markersize=8, color='#4ECDC4')
        ax5.fill_between(session_numbers, cumulative_savings, alpha=0.3, color='#4ECDC4')
        ax5.set_xlabel('Session Number')
        ax5.set_ylabel('Cumulative Savings (%)')
        ax5.set_title('Token Savings Over Time')
        ax5.grid(True, alpha=0.3)
        
        # Add title
        fig.suptitle('Phase 3 Validation Dashboard', fontsize=16, fontweight='bold')
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard saved: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Visualization tools for Phase 3 validation"
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all visualizations'
    )
    
    parser.add_argument(
        '--savings-chart',
        action='store_true',
        help='Generate token savings comparison chart'
    )
    
    parser.add_argument(
        '--cache-chart',
        action='store_true',
        help='Generate cache effectiveness chart'
    )
    
    parser.add_argument(
        '--latency-chart',
        action='store_true',
        help='Generate latency distribution chart'
    )
    
    parser.add_argument(
        '--savings-over-time',
        action='store_true',
        help='Generate savings over time chart'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Generate comprehensive dashboard'
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
        '--output',
        help='Output file path'
    )
    
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for multiple files (default: reports)'
    )
    
    parser.add_argument(
        '--data-dir',
        default='evaluation/data/sessions',
        help='Data directory (default: evaluation/data/sessions)'
    )
    
    args = parser.parse_args()
    
    # Initialize visualizer
    visualizer = SessionVisualizer(args.data_dir)
    
    # Create output directory if needed
    if args.all or args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    if args.all:
        if not args.baseline or not args.optimized:
            print("Error: Specify both --baseline and --optimized session IDs", file=sys.stderr)
            return 1
        
        output_dir = Path(args.output_dir)
        
        print("Generating all visualizations...")
        visualizer.plot_savings_comparison(
            args.baseline, args.optimized,
            str(output_dir / 'savings_comparison.png')
        )
        visualizer.plot_cache_effectiveness(
            args.optimized,
            str(output_dir / 'cache_effectiveness.png')
        )
        visualizer.plot_latency_distribution(
            args.baseline, args.optimized,
            str(output_dir / 'latency_distribution.png')
        )
        visualizer.plot_savings_over_time(
            args.optimized,
            str(output_dir / 'savings_over_time.png')
        )
        visualizer.create_dashboard(
            args.baseline, args.optimized,
            str(output_dir / 'dashboard.png')
        )
        print(f"\nAll visualizations saved to: {output_dir}")
    
    elif args.savings_chart:
        if not args.baseline or not args.optimized:
            print("Error: Specify both --baseline and --optimized session IDs", file=sys.stderr)
            return 1
        output = args.output or 'savings_comparison.png'
        visualizer.plot_savings_comparison(args.baseline, args.optimized, output)
    
    elif args.cache_chart:
        if not args.optimized:
            print("Error: Specify --optimized session IDs", file=sys.stderr)
            return 1
        output = args.output or 'cache_effectiveness.png'
        visualizer.plot_cache_effectiveness(args.optimized, output)
    
    elif args.latency_chart:
        if not args.baseline or not args.optimized:
            print("Error: Specify both --baseline and --optimized session IDs", file=sys.stderr)
            return 1
        output = args.output or 'latency_distribution.png'
        visualizer.plot_latency_distribution(args.baseline, args.optimized, output)
    
    elif args.savings_over_time:
        if not args.optimized:
            print("Error: Specify --optimized session IDs", file=sys.stderr)
            return 1
        output = args.output or 'savings_over_time.png'
        visualizer.plot_savings_over_time(args.optimized, output)
    
    elif args.dashboard:
        if not args.baseline or not args.optimized:
            print("Error: Specify both --baseline and --optimized session IDs", file=sys.stderr)
            return 1
        output = args.output or 'dashboard.png'
        visualizer.create_dashboard(args.baseline, args.optimized, output)
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
