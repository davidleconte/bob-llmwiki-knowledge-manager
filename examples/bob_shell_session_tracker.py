#!/usr/bin/env python3
"""
Bob Shell Session Tracker

Tracks Bob Shell sessions to measure token usage and optimization effectiveness.
This is the foundation for Phase 3 real-world validation.

Usage:
    # Track a session without optimization (baseline)
    python bob_shell_session_tracker.py --mode baseline --session-id baseline_001
    
    # Track a session with optimization enabled
    python bob_shell_session_tracker.py --mode optimized --session-id optimized_001
    
    # Analyze results
    python bob_shell_session_tracker.py --analyze
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

# Import optimization components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimizer import PromptOptimizer, TokenCounter
from src.cache import MultiLevelCache
from src.truncation import Truncator
from src.monitoring import get_logger, get_metrics_collector

logger = get_logger("session_tracker")
metrics = get_metrics_collector()


@dataclass
class QueryRecord:
    """Record of a single query in a session."""
    query_id: str
    timestamp: float
    query_text: str
    context_text: str
    baseline_tokens: int
    optimized_tokens: int
    tokens_saved: int
    savings_percent: float
    cache_hit: bool
    optimization_applied: bool
    truncation_applied: bool
    latency_ms: float


@dataclass
class SessionSummary:
    """Summary of a complete session."""
    session_id: str
    mode: str  # 'baseline' or 'optimized'
    start_time: float
    end_time: float
    duration_seconds: float
    total_queries: int
    total_baseline_tokens: int
    total_optimized_tokens: int
    total_tokens_saved: int
    overall_savings_percent: float
    cache_hit_rate: float
    optimization_rate: float
    truncation_rate: float
    avg_latency_ms: float
    queries: List[QueryRecord]


class BobShellSessionTracker:
    """
    Tracks Bob Shell sessions to measure token usage and optimization effectiveness.
    
    This tracker can operate in two modes:
    1. Baseline mode: Measures token usage without optimization
    2. Optimized mode: Measures token usage with optimization enabled
    
    The tracker records:
    - Token counts (baseline vs optimized)
    - Cache effectiveness
    - Optimization application rate
    - Latency measurements
    - Query patterns
    """
    
    def __init__(
        self,
        session_id: str,
        mode: str = "baseline",
        data_dir: Optional[Path] = None
    ):
        """
        Initialize session tracker.
        
        Args:
            session_id: Unique identifier for this session
            mode: 'baseline' or 'optimized'
            data_dir: Directory to store session data (default: ./data/sessions)
        """
        self.session_id = session_id
        self.mode = mode
        self.data_dir = data_dir or Path(__file__).parent.parent / "evaluation" / "data" / "sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components (only if optimized mode)
        self.optimizer = PromptOptimizer() if mode == "optimized" else None
        self.cache = MultiLevelCache() if mode == "optimized" else None
        self.truncator = Truncator() if mode == "optimized" else None
        self.token_counter = TokenCounter()
        
        # Session state
        self.start_time = time.time()
        self.queries: List[QueryRecord] = []
        self.query_counter = 0
        
        logger.info(
            "session_started",
            session_id=session_id,
            mode=mode,
            timestamp=self.start_time
        )
    
    def track_query(
        self,
        query_text: str,
        context_text: str = "",
        response_text: str = ""
    ) -> QueryRecord:
        """
        Track a single query in the session.
        
        Args:
            query_text: The user's query
            context_text: Context provided with the query
            response_text: The response (for caching)
        
        Returns:
            QueryRecord with measurements
        """
        self.query_counter += 1
        query_id = f"{self.session_id}_q{self.query_counter:03d}"
        start_time = time.time()
        
        # Calculate baseline tokens (always)
        baseline_tokens = self.token_counter.count_tokens(query_text + context_text)
        
        # Initialize tracking variables
        optimized_tokens = baseline_tokens
        cache_hit = False
        optimization_applied = False
        truncation_applied = False
        
        if self.mode == "optimized":
            # Check cache first
            cache_key = query_text
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                cache_hit = True
                optimized_tokens = 0  # No tokens used for cached response
                logger.info("cache_hit", query_id=query_id, cache_type="exact")
            else:
                # Apply optimization
                opt_result = self.optimizer.optimize(query_text)
                if opt_result["tokens_saved"] > 0:
                    optimization_applied = True
                    query_text = opt_result["optimized"]
                
                # Apply truncation if context is large
                if context_text and len(context_text.split()) > 500:
                    trunc_result = self.truncator.truncate(
                        context_text,
                        query_text,
                        max_tokens=2000
                    )
                    if trunc_result["tokens_saved"] > 0:
                        truncation_applied = True
                        context_text = trunc_result["truncated"]
                
                # Calculate optimized tokens
                optimized_tokens = self.token_counter.count_tokens(
                    query_text + context_text
                )
                
                # Cache the response
                if response_text:
                    self.cache.set(cache_key, response_text)
        
        # Calculate savings
        tokens_saved = baseline_tokens - optimized_tokens
        savings_percent = (tokens_saved / baseline_tokens * 100) if baseline_tokens > 0 else 0.0
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Create record
        record = QueryRecord(
            query_id=query_id,
            timestamp=time.time(),
            query_text=query_text[:100] + "..." if len(query_text) > 100 else query_text,
            context_text=context_text[:100] + "..." if len(context_text) > 100 else context_text,
            baseline_tokens=baseline_tokens,
            optimized_tokens=optimized_tokens,
            tokens_saved=tokens_saved,
            savings_percent=savings_percent,
            cache_hit=cache_hit,
            optimization_applied=optimization_applied,
            truncation_applied=truncation_applied,
            latency_ms=latency_ms
        )
        
        self.queries.append(record)
        
        # Log metrics
        logger.info(
            "query_tracked",
            query_id=query_id,
            baseline_tokens=baseline_tokens,
            optimized_tokens=optimized_tokens,
            savings_percent=savings_percent,
            cache_hit=cache_hit
        )
        
        if self.mode == "optimized":
            metrics.record_optimization(
                baseline_tokens,
                optimized_tokens,
                latency_ms
            )
            if cache_hit:
                metrics.record_cache_hit("L1", latency_ms)
        
        return record
    
    def end_session(self) -> SessionSummary:
        """
        End the session and generate summary.
        
        Returns:
            SessionSummary with complete session metrics
        """
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Calculate aggregates
        total_queries = len(self.queries)
        total_baseline_tokens = sum(q.baseline_tokens for q in self.queries)
        total_optimized_tokens = sum(q.optimized_tokens for q in self.queries)
        total_tokens_saved = total_baseline_tokens - total_optimized_tokens
        
        overall_savings_percent = (
            (total_tokens_saved / total_baseline_tokens * 100)
            if total_baseline_tokens > 0 else 0.0
        )
        
        cache_hit_rate = (
            sum(1 for q in self.queries if q.cache_hit) / total_queries
            if total_queries > 0 else 0.0
        )
        
        optimization_rate = (
            sum(1 for q in self.queries if q.optimization_applied) / total_queries
            if total_queries > 0 else 0.0
        )
        
        truncation_rate = (
            sum(1 for q in self.queries if q.truncation_applied) / total_queries
            if total_queries > 0 else 0.0
        )
        
        avg_latency_ms = (
            sum(q.latency_ms for q in self.queries) / total_queries
            if total_queries > 0 else 0.0
        )
        
        # Create summary
        summary = SessionSummary(
            session_id=self.session_id,
            mode=self.mode,
            start_time=self.start_time,
            end_time=end_time,
            duration_seconds=duration,
            total_queries=total_queries,
            total_baseline_tokens=total_baseline_tokens,
            total_optimized_tokens=total_optimized_tokens,
            total_tokens_saved=total_tokens_saved,
            overall_savings_percent=overall_savings_percent,
            cache_hit_rate=cache_hit_rate,
            optimization_rate=optimization_rate,
            truncation_rate=truncation_rate,
            avg_latency_ms=avg_latency_ms,
            queries=self.queries
        )
        
        # Save to file
        self._save_session(summary)
        
        # Log summary
        logger.info(
            "session_ended",
            session_id=self.session_id,
            total_queries=total_queries,
            overall_savings_percent=overall_savings_percent,
            cache_hit_rate=cache_hit_rate
        )
        
        return summary
    
    def _save_session(self, summary: SessionSummary) -> None:
        """Save session summary to file."""
        filename = f"{self.session_id}.json"
        filepath = self.data_dir / filename
        
        # Convert to dict
        data = asdict(summary)
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("session_saved", filepath=str(filepath))
    
    @staticmethod
    def load_session(session_id: str, data_dir: Optional[Path] = None) -> SessionSummary:
        """Load a saved session."""
        data_dir = data_dir or Path(__file__).parent.parent / "evaluation" / "data" / "sessions"
        filepath = data_dir / f"{session_id}.json"
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert queries back to QueryRecord objects
        data['queries'] = [QueryRecord(**q) for q in data['queries']]
        
        return SessionSummary(**data)
    
    @staticmethod
    def analyze_sessions(
        baseline_sessions: List[str],
        optimized_sessions: List[str],
        data_dir: Optional[Path] = None
    ) -> Dict:
        """
        Analyze and compare baseline vs optimized sessions.
        
        Args:
            baseline_sessions: List of baseline session IDs
            optimized_sessions: List of optimized session IDs
            data_dir: Directory containing session data
        
        Returns:
            Analysis results with comparison metrics
        """
        data_dir = data_dir or Path(__file__).parent.parent / "evaluation" / "data" / "sessions"
        
        # Load sessions
        baseline = [
            BobShellSessionTracker.load_session(sid, data_dir)
            for sid in baseline_sessions
        ]
        optimized = [
            BobShellSessionTracker.load_session(sid, data_dir)
            for sid in optimized_sessions
        ]
        
        # Calculate baseline metrics
        baseline_total_tokens = sum(s.total_baseline_tokens for s in baseline)
        baseline_avg_latency = sum(s.avg_latency_ms for s in baseline) / len(baseline)
        
        # Calculate optimized metrics
        optimized_total_baseline = sum(s.total_baseline_tokens for s in optimized)
        optimized_total_optimized = sum(s.total_optimized_tokens for s in optimized)
        optimized_total_saved = optimized_total_baseline - optimized_total_optimized
        optimized_savings_percent = (
            (optimized_total_saved / optimized_total_baseline * 100)
            if optimized_total_baseline > 0 else 0.0
        )
        optimized_avg_cache_hit = sum(s.cache_hit_rate for s in optimized) / len(optimized)
        optimized_avg_latency = sum(s.avg_latency_ms for s in optimized) / len(optimized)
        
        # Create analysis
        analysis = {
            "baseline": {
                "sessions": len(baseline),
                "total_tokens": baseline_total_tokens,
                "avg_latency_ms": baseline_avg_latency
            },
            "optimized": {
                "sessions": len(optimized),
                "total_baseline_tokens": optimized_total_baseline,
                "total_optimized_tokens": optimized_total_optimized,
                "total_tokens_saved": optimized_total_saved,
                "savings_percent": optimized_savings_percent,
                "avg_cache_hit_rate": optimized_avg_cache_hit,
                "avg_latency_ms": optimized_avg_latency
            },
            "comparison": {
                "token_reduction": optimized_savings_percent,
                "latency_overhead_ms": optimized_avg_latency - baseline_avg_latency,
                "cache_effectiveness": optimized_avg_cache_hit
            }
        }
        
        return analysis


def main():
    """CLI interface for session tracker."""
    parser = argparse.ArgumentParser(description="Bob Shell Session Tracker")
    parser.add_argument(
        "--mode",
        choices=["baseline", "optimized"],
        help="Tracking mode"
    )
    parser.add_argument(
        "--session-id",
        help="Session identifier"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze saved sessions"
    )
    parser.add_argument(
        "--baseline-sessions",
        nargs="+",
        help="Baseline session IDs for analysis"
    )
    parser.add_argument(
        "--optimized-sessions",
        nargs="+",
        help="Optimized session IDs for analysis"
    )
    
    args = parser.parse_args()
    
    if args.analyze:
        if not args.baseline_sessions or not args.optimized_sessions:
            print("Error: --analyze requires --baseline-sessions and --optimized-sessions")
            return 1
        
        analysis = BobShellSessionTracker.analyze_sessions(
            args.baseline_sessions,
            args.optimized_sessions
        )
        
        print("\n" + "="*60)
        print("SESSION ANALYSIS")
        print("="*60)
        print(f"\nBaseline Sessions: {analysis['baseline']['sessions']}")
        print(f"Total Tokens: {analysis['baseline']['total_tokens']:,}")
        print(f"Avg Latency: {analysis['baseline']['avg_latency_ms']:.2f}ms")
        print(f"\nOptimized Sessions: {analysis['optimized']['sessions']}")
        print(f"Total Baseline Tokens: {analysis['optimized']['total_baseline_tokens']:,}")
        print(f"Total Optimized Tokens: {analysis['optimized']['total_optimized_tokens']:,}")
        print(f"Tokens Saved: {analysis['optimized']['total_tokens_saved']:,}")
        print(f"Savings: {analysis['optimized']['savings_percent']:.1f}%")
        print(f"Cache Hit Rate: {analysis['optimized']['avg_cache_hit_rate']:.1%}")
        print(f"Avg Latency: {analysis['optimized']['avg_latency_ms']:.2f}ms")
        print(f"\nComparison:")
        print(f"Token Reduction: {analysis['comparison']['token_reduction']:.1f}%")
        print(f"Latency Overhead: {analysis['comparison']['latency_overhead_ms']:.2f}ms")
        print(f"Cache Effectiveness: {analysis['comparison']['cache_effectiveness']:.1%}")
        print("="*60 + "\n")
        
        return 0
    
    if not args.mode or not args.session_id:
        print("Error: --mode and --session-id required (or use --analyze)")
        return 1
    
    # Interactive tracking mode
    tracker = BobShellSessionTracker(args.session_id, args.mode)
    
    print(f"\nSession Tracker Started")
    print(f"Session ID: {args.session_id}")
    print(f"Mode: {args.mode}")
    print("\nEnter queries (or 'quit' to end session):\n")
    
    while True:
        try:
            query = input("Query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            context = input("Context (optional): ").strip()
            response = input("Response (optional): ").strip()
            
            record = tracker.track_query(query, context, response)
            
            print(f"\n  Baseline Tokens: {record.baseline_tokens}")
            print(f"  Optimized Tokens: {record.optimized_tokens}")
            print(f"  Savings: {record.savings_percent:.1f}%")
            print(f"  Cache Hit: {record.cache_hit}")
            print(f"  Latency: {record.latency_ms:.2f}ms\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue
    
    # End session
    summary = tracker.end_session()
    
    print("\n" + "="*60)
    print("SESSION SUMMARY")
    print("="*60)
    print(f"Session ID: {summary.session_id}")
    print(f"Mode: {summary.mode}")
    print(f"Duration: {summary.duration_seconds:.1f}s")
    print(f"Total Queries: {summary.total_queries}")
    print(f"Total Baseline Tokens: {summary.total_baseline_tokens:,}")
    print(f"Total Optimized Tokens: {summary.total_optimized_tokens:,}")
    print(f"Tokens Saved: {summary.total_tokens_saved:,}")
    print(f"Overall Savings: {summary.overall_savings_percent:.1f}%")
    print(f"Cache Hit Rate: {summary.cache_hit_rate:.1%}")
    print(f"Optimization Rate: {summary.optimization_rate:.1%}")
    print(f"Truncation Rate: {summary.truncation_rate:.1%}")
    print(f"Avg Latency: {summary.avg_latency_ms:.2f}ms")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())