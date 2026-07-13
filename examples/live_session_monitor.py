#!/usr/bin/env python3
"""
Real-Time Session Monitoring Dashboard

Monitors Bob Shell sessions in real-time, providing live feedback on:
- Progress toward 20 session target
- Token savings estimates
- Cache hit rates
- Session quality indicators
- Time remaining estimates

Usage:
    python3 examples/live_session_monitor.py [--baseline|--optimized]
    
    # Monitor baseline sessions (default)
    python3 examples/live_session_monitor.py --baseline
    
    # Monitor optimized sessions
    python3 examples/live_session_monitor.py --optimized
    
    # Press Ctrl+C to stop monitoring
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class SessionMonitor:
    """Real-time session monitoring dashboard."""
    
    def __init__(self, session_type: str = "baseline"):
        """Initialize the monitor.
        
        Args:
            session_type: Either "baseline" or "optimized"
        """
        self.session_type = session_type
        self.reports_dir = Path("reports")
        self.target_sessions = 20
        self.refresh_interval = 5  # seconds
        self.start_time = datetime.now()
        
        # Session tracking
        self.sessions: List[Dict] = []
        self.last_file_count = 0
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def load_sessions(self) -> List[Dict]:
        """Load all session files from reports directory.
        
        Returns:
            List of session data dictionaries
        """
        sessions = []
        
        if not self.reports_dir.exists():
            return sessions
            
        # Look for session JSON files
        pattern = f"*{self.session_type}*.json"
        for file_path in self.reports_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Add file metadata
                    data['file_path'] = str(file_path)
                    data['file_mtime'] = file_path.stat().st_mtime
                    sessions.append(data)
            except (json.JSONDecodeError, IOError) as e:
                # Skip invalid files
                continue
                
        # Sort by modification time (newest first)
        sessions.sort(key=lambda x: x.get('file_mtime', 0), reverse=True)
        
        return sessions
        
    def calculate_statistics(self) -> Dict:
        """Calculate current statistics from loaded sessions.
        
        Returns:
            Dictionary of statistics
        """
        if not self.sessions:
            return {
                'total_sessions': 0,
                'total_queries': 0,
                'avg_queries_per_session': 0,
                'total_tokens': 0,
                'avg_tokens_per_query': 0,
                'cache_hit_rate': 0,
                'estimated_savings': 0,
                'quality_score': 0,
                'sessions_remaining': self.target_sessions,
                'progress_percent': 0,
                'estimated_time_remaining': None
            }
            
        total_sessions = len(self.sessions)
        total_queries = sum(s.get('total_queries', 0) for s in self.sessions)
        total_tokens = sum(s.get('total_tokens', 0) for s in self.sessions)
        
        # Cache statistics (if available)
        cache_hits = sum(s.get('cache_hits', 0) for s in self.sessions)
        cache_total = sum(s.get('cache_total', 0) for s in self.sessions)
        cache_hit_rate = (cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        # Quality indicators
        min_queries = 5
        quality_sessions = sum(1 for s in self.sessions if s.get('total_queries', 0) >= min_queries)
        quality_score = (quality_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Progress
        progress_percent = (total_sessions / self.target_sessions * 100)
        sessions_remaining = max(0, self.target_sessions - total_sessions)
        
        # Time estimation
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if total_sessions > 0:
            avg_time_per_session = elapsed_time / total_sessions
            estimated_seconds_remaining = avg_time_per_session * sessions_remaining
            estimated_time_remaining = timedelta(seconds=int(estimated_seconds_remaining))
        else:
            estimated_time_remaining = None
            
        # Token savings estimate (for optimized sessions)
        estimated_savings = 0
        if self.session_type == "optimized" and total_tokens > 0:
            # Assume 30% savings (conservative estimate)
            baseline_tokens = total_tokens / 0.7  # If we saved 30%, optimized is 70% of baseline
            estimated_savings = baseline_tokens - total_tokens
            
        return {
            'total_sessions': total_sessions,
            'total_queries': total_queries,
            'avg_queries_per_session': total_queries / total_sessions if total_sessions > 0 else 0,
            'total_tokens': total_tokens,
            'avg_tokens_per_query': total_tokens / total_queries if total_queries > 0 else 0,
            'cache_hit_rate': cache_hit_rate,
            'estimated_savings': estimated_savings,
            'quality_score': quality_score,
            'sessions_remaining': sessions_remaining,
            'progress_percent': min(100, progress_percent),
            'estimated_time_remaining': estimated_time_remaining
        }
        
    def format_number(self, num: float, decimals: int = 0) -> str:
        """Format a number with thousands separators.
        
        Args:
            num: Number to format
            decimals: Number of decimal places
            
        Returns:
            Formatted string
        """
        if decimals == 0:
            return f"{int(num):,}"
        else:
            return f"{num:,.{decimals}f}"
            
    def get_progress_bar(self, percent: float, width: int = 40) -> str:
        """Create a text progress bar.
        
        Args:
            percent: Percentage complete (0-100)
            width: Width of the bar in characters
            
        Returns:
            Progress bar string
        """
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent:.1f}%"
        
    def get_quality_indicator(self, score: float) -> Tuple[str, str]:
        """Get quality indicator emoji and color.
        
        Args:
            score: Quality score (0-100)
            
        Returns:
            Tuple of (emoji, description)
        """
        if score >= 90:
            return "🟢", "Excellent"
        elif score >= 70:
            return "🟡", "Good"
        elif score >= 50:
            return "🟠", "Fair"
        else:
            return "🔴", "Poor"
            
    def render_dashboard(self):
        """Render the monitoring dashboard."""
        self.clear_screen()
        
        stats = self.calculate_statistics()
        
        # Header
        print("=" * 80)
        print(f"  📊 REAL-TIME SESSION MONITOR - {self.session_type.upper()}")
        print("=" * 80)
        print()
        
        # Progress Section
        print("📈 PROGRESS")
        print("-" * 80)
        progress_bar = self.get_progress_bar(stats['progress_percent'])
        print(f"  {progress_bar}")
        print(f"  Sessions: {stats['total_sessions']}/{self.target_sessions} completed")
        print(f"  Remaining: {stats['sessions_remaining']} sessions")
        
        if stats['estimated_time_remaining']:
            print(f"  Estimated time remaining: {stats['estimated_time_remaining']}")
        print()
        
        # Quality Section
        quality_emoji, quality_desc = self.get_quality_indicator(stats['quality_score'])
        print("✅ QUALITY INDICATORS")
        print("-" * 80)
        print(f"  Overall Quality: {quality_emoji} {quality_desc} ({stats['quality_score']:.1f}%)")
        print(f"  Total Queries: {self.format_number(stats['total_queries'])}")
        print(f"  Avg Queries/Session: {stats['avg_queries_per_session']:.1f}")
        print(f"  Quality Sessions: {int(stats['quality_score'] * stats['total_sessions'] / 100)}/{stats['total_sessions']}")
        print()
        
        # Token Statistics
        print("🎯 TOKEN STATISTICS")
        print("-" * 80)
        print(f"  Total Tokens: {self.format_number(stats['total_tokens'])}")
        print(f"  Avg Tokens/Query: {self.format_number(stats['avg_tokens_per_query'], 1)}")
        
        if self.session_type == "optimized":
            print(f"  Estimated Savings: {self.format_number(stats['estimated_savings'])} tokens")
            if stats['total_tokens'] > 0:
                savings_percent = (stats['estimated_savings'] / (stats['total_tokens'] + stats['estimated_savings'])) * 100
                print(f"  Savings Rate: {savings_percent:.1f}%")
        print()
        
        # Cache Statistics (if available)
        if stats['cache_hit_rate'] > 0:
            print("💾 CACHE PERFORMANCE")
            print("-" * 80)
            print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
            cache_emoji = "🟢" if stats['cache_hit_rate'] >= 70 else "🟡" if stats['cache_hit_rate'] >= 50 else "🔴"
            print(f"  Performance: {cache_emoji}")
            print()
        
        # Recent Sessions
        if self.sessions:
            print("📝 RECENT SESSIONS (Last 5)")
            print("-" * 80)
            for i, session in enumerate(self.sessions[:5], 1):
                queries = session.get('total_queries', 0)
                tokens = session.get('total_tokens', 0)
                timestamp = datetime.fromtimestamp(session.get('file_mtime', 0))
                quality = "✅" if queries >= 5 else "⚠️"
                print(f"  {i}. {quality} {queries} queries, {self.format_number(tokens)} tokens - {timestamp.strftime('%H:%M:%S')}")
            print()
        
        # Warnings
        warnings = []
        if stats['quality_score'] < 70:
            warnings.append("⚠️  Low quality score - ensure sessions have 5+ queries")
        if stats['total_sessions'] > 0 and stats['avg_queries_per_session'] < 5:
            warnings.append("⚠️  Low average queries per session")
        if self.session_type == "optimized" and stats['cache_hit_rate'] < 50:
            warnings.append("⚠️  Low cache hit rate - optimization may not be effective")
            
        if warnings:
            print("⚠️  WARNINGS")
            print("-" * 80)
            for warning in warnings:
                print(f"  {warning}")
            print()
        
        # Footer
        print("-" * 80)
        elapsed = datetime.now() - self.start_time
        print(f"  Monitoring for: {elapsed.seconds // 60}m {elapsed.seconds % 60}s")
        print(f"  Last update: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  Refresh interval: {self.refresh_interval}s")
        print(f"  Press Ctrl+C to stop")
        print("=" * 80)
        
    def check_for_new_sessions(self) -> bool:
        """Check if new sessions have been added.
        
        Returns:
            True if new sessions detected
        """
        current_sessions = self.load_sessions()
        new_count = len(current_sessions)
        
        if new_count != self.last_file_count:
            self.sessions = current_sessions
            self.last_file_count = new_count
            return True
            
        return False
        
    def run(self):
        """Run the monitoring dashboard."""
        print(f"Starting real-time monitor for {self.session_type} sessions...")
        print(f"Watching directory: {self.reports_dir.absolute()}")
        print(f"Press Ctrl+C to stop\n")
        time.sleep(2)
        
        try:
            # Initial load
            self.sessions = self.load_sessions()
            self.last_file_count = len(self.sessions)
            
            while True:
                # Check for updates
                self.check_for_new_sessions()
                
                # Render dashboard
                self.render_dashboard()
                
                # Check if target reached
                if len(self.sessions) >= self.target_sessions:
                    print("\n🎉 TARGET REACHED! All 20 sessions completed!")
                    print("Press Ctrl+C to exit or wait for more sessions...")
                
                # Wait for next refresh
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped by user")
            print(f"Final count: {len(self.sessions)} sessions")
            sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Real-time session monitoring dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor baseline sessions (default)
  python3 examples/live_session_monitor.py --baseline
  
  # Monitor optimized sessions
  python3 examples/live_session_monitor.py --optimized
  
  # Press Ctrl+C to stop monitoring
        """
    )
    
    parser.add_argument(
        '--baseline',
        action='store_const',
        const='baseline',
        dest='session_type',
        help='Monitor baseline sessions (default)'
    )
    
    parser.add_argument(
        '--optimized',
        action='store_const',
        const='optimized',
        dest='session_type',
        help='Monitor optimized sessions'
    )
    
    args = parser.parse_args()
    
    # Default to baseline if not specified
    session_type = args.session_type or 'baseline'
    
    # Create and run monitor
    monitor = SessionMonitor(session_type=session_type)
    monitor.run()


if __name__ == '__main__':
    main()
