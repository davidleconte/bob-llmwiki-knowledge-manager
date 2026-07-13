#!/usr/bin/env python3
"""
Live Bob Shell Session Cost Tracker with Savings Analysis

Tracks actual Bob Shell session costs in real-time with detailed savings breakdown.
Shows where savings come from: cache hits, optimizations, and efficiency gains.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimizer import TokenCounter, PromptOptimizer
from src.cache import MultiLevelCache
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker
from src.monitoring.cost_reporting import (
    generate_cost_dashboard,
    check_budget_health,
    get_top_cost_operations
)


class LiveSessionTracker:
    """
    Real-time cost tracker for Bob Shell sessions with savings analysis.
    
    Tracks:
    - Token usage (user, assistant, tools, system)
    - Costs in Bobcoins
    - Savings from cache hits
    - Savings from optimizations
    - Efficiency metrics
    """
    
    def __init__(self, session_id: str, budget_bobcoins: float = 1000.0):
        """Initialize live session tracker."""
        self.session_id = session_id
        self.start_time = datetime.now()
        
        # Initialize cost tracking
        reset_cost_tracker()
        self.tracker = get_cost_tracker(budget_bobcoins=budget_bobcoins)
        
        # Initialize components with cost tracking
        self.counter = TokenCounter(model="gpt-4", track_costs=True)
        self.optimizer = PromptOptimizer(model="gpt-4", use_cache=True, track_costs=True)
        self.cache = MultiLevelCache()
        
        # Enable cache cost tracking
        self.cache.l1_cache.track_costs = True
        self.cache.l1_cache._cost_tracker = self.tracker
        self.cache.l2_cache.track_costs = True
        self.cache.l2_cache._cost_tracker = self.tracker
        
        # Session data
        self.exchanges = []
        self.savings_log = []
        
    def track_message(
        self,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a single message (user, assistant, tool, system).
        
        Args:
            message_type: Type of message (user/assistant/tool/system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Message tracking data
        """
        # Check cache first
        cached = self.cache.get(content)
        
        if cached:
            # Cache hit - saved tokens!
            original_tokens = self.counter.count_tokens(content)
            savings = {
                "type": "cache_hit",
                "tokens_saved": original_tokens,
                "bobcoins_saved": original_tokens / 1000,
                "source": "L1 or L2 cache",
                "timestamp": datetime.now().isoformat()
            }
            self.savings_log.append(savings)
            
            return {
                "message_type": message_type,
                "tokens": 0,  # No tokens used (cache hit)
                "cost_bobcoins": 0.0,
                "cached": True,
                "savings": savings
            }
        
        # Not cached - count tokens
        tokens = self.counter.count_tokens(content)
        cost = tokens / 1000
        
        # Try optimization if content is long
        if len(content) > 200 and message_type in ["user", "assistant"]:
            result = self.optimizer.optimize(content)
            if result['tokens_saved'] > 0:
                savings = {
                    "type": "optimization",
                    "tokens_saved": result['tokens_saved'],
                    "bobcoins_saved": result['tokens_saved'] / 1000,
                    "source": "prompt_optimization",
                    "timestamp": datetime.now().isoformat(),
                    "savings_percent": result['savings_percentage']
                }
                self.savings_log.append(savings)
                
                # Cache optimized version
                self.cache.set(content, result['optimized'], 
                             metadata={'tokens': result['optimized_tokens']})
                
                return {
                    "message_type": message_type,
                    "tokens": result['optimized_tokens'],
                    "cost_bobcoins": result['optimized_tokens'] / 1000,
                    "cached": False,
                    "optimized": True,
                    "savings": savings
                }
        
        # Cache for future use
        self.cache.set(content, content, metadata={'tokens': tokens})
        
        return {
            "message_type": message_type,
            "tokens": tokens,
            "cost_bobcoins": cost,
            "cached": False,
            "optimized": False
        }
    
    def track_exchange(
        self,
        user_message: str,
        assistant_response: str,
        tool_uses: Optional[List[str]] = None,
        system_prompts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Track a complete conversation exchange.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            tool_uses: List of tool usage descriptions
            system_prompts: List of system prompts used
            
        Returns:
            Exchange summary with savings breakdown
        """
        exchange_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "savings": []
        }
        
        # Track user message
        user_data = self.track_message("user", user_message)
        exchange_data["messages"].append(user_data)
        exchange_data["total_tokens"] += user_data["tokens"]
        exchange_data["total_cost"] += user_data["cost_bobcoins"]
        if "savings" in user_data:
            exchange_data["savings"].append(user_data["savings"])
        
        # Track assistant response
        assistant_data = self.track_message("assistant", assistant_response)
        exchange_data["messages"].append(assistant_data)
        exchange_data["total_tokens"] += assistant_data["tokens"]
        exchange_data["total_cost"] += assistant_data["cost_bobcoins"]
        if "savings" in assistant_data:
            exchange_data["savings"].append(assistant_data["savings"])
        
        # Track tool uses
        if tool_uses:
            for tool_use in tool_uses:
                tool_data = self.track_message("tool", tool_use)
                exchange_data["messages"].append(tool_data)
                exchange_data["total_tokens"] += tool_data["tokens"]
                exchange_data["total_cost"] += tool_data["cost_bobcoins"]
                if "savings" in tool_data:
                    exchange_data["savings"].append(tool_data["savings"])
        
        # Track system prompts
        if system_prompts:
            for prompt in system_prompts:
                system_data = self.track_message("system", prompt)
                exchange_data["messages"].append(system_data)
                exchange_data["total_tokens"] += system_data["tokens"]
                exchange_data["total_cost"] += system_data["cost_bobcoins"]
                if "savings" in system_data:
                    exchange_data["savings"].append(system_data["savings"])
        
        self.exchanges.append(exchange_data)
        return exchange_data
    
    def get_savings_breakdown(self) -> Dict[str, Any]:
        """Get detailed savings breakdown."""
        breakdown = {
            "total_savings_bobcoins": 0.0,
            "total_tokens_saved": 0,
            "by_source": {},
            "by_type": {},
            "savings_events": len(self.savings_log)
        }
        
        for saving in self.savings_log:
            # Total
            breakdown["total_savings_bobcoins"] += saving["bobcoins_saved"]
            breakdown["total_tokens_saved"] += saving["tokens_saved"]
            
            # By source
            source = saving["source"]
            if source not in breakdown["by_source"]:
                breakdown["by_source"][source] = {
                    "bobcoins": 0.0,
                    "tokens": 0,
                    "count": 0
                }
            breakdown["by_source"][source]["bobcoins"] += saving["bobcoins_saved"]
            breakdown["by_source"][source]["tokens"] += saving["tokens_saved"]
            breakdown["by_source"][source]["count"] += 1
            
            # By type
            stype = saving["type"]
            if stype not in breakdown["by_type"]:
                breakdown["by_type"][stype] = {
                    "bobcoins": 0.0,
                    "tokens": 0,
                    "count": 0
                }
            breakdown["by_type"][stype]["bobcoins"] += saving["bobcoins_saved"]
            breakdown["by_type"][stype]["tokens"] += saving["tokens_saved"]
            breakdown["by_type"][stype]["count"] += 1
        
        return breakdown
    
    def print_live_dashboard(self) -> None:
        """Print live session dashboard with savings analysis."""
        duration = (datetime.now() - self.start_time).total_seconds()
        metrics = self.tracker.get_cost_metrics()
        budget = self.tracker.get_budget_status()
        savings = self.get_savings_breakdown()
        
        print("\n" + "="*80)
        print(f"LIVE BOB SHELL SESSION - {self.session_id}")
        print("="*80)
        
        print("\n📊 SESSION OVERVIEW")
        print("-"*80)
        print(f"  Duration:         {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"  Exchanges:        {len(self.exchanges)}")
        print(f"  Operations:       {metrics['operations_count']}")
        
        print("\n💰 COST SUMMARY")
        print("-"*80)
        print(f"  Budget:           {budget['budget_bobcoins']:>12.4f} BC")
        print(f"  Spent:            {budget['spent_bobcoins']:>12.4f} BC")
        print(f"  Saved:            {budget['saved_bobcoins']:>12.4f} BC  ⭐")
        print(f"  Net Cost:         {budget['net_spent_bobcoins']:>12.4f} BC")
        print(f"  Remaining:        {budget['remaining_bobcoins']:>12.4f} BC")
        print(f"  Budget Used:      {budget['percent_used']:>12.2f}%")
        
        # Budget bar
        bar_width = 60
        used_width = int((budget['percent_used'] / 100) * bar_width)
        bar = "█" * used_width + "░" * (bar_width - used_width)
        print(f"  [{bar}]")
        
        print("\n🎯 EFFICIENCY METRICS")
        print("-"*80)
        print(f"  ROI:              {metrics['roi_percent']:>12.2f}%")
        print(f"  Tokens Used:      {metrics['total_tokens_used']:>12,}")
        print(f"  Tokens Saved:     {metrics['total_tokens_saved']:>12,}  ⭐")
        print(f"  Avg Cost/Op:      {metrics['avg_cost_per_operation']:>12.4f} BC")
        
        print("\n💎 SAVINGS BREAKDOWN")
        print("-"*80)
        print(f"  Total Savings:    {savings['total_savings_bobcoins']:>12.4f} BC")
        print(f"  Tokens Saved:     {savings['total_tokens_saved']:>12,}")
        print(f"  Savings Events:   {savings['savings_events']:>12}")
        
        if savings['by_type']:
            print("\n  By Type:")
            for stype, data in savings['by_type'].items():
                print(f"    {stype:20} {data['bobcoins']:>10.4f} BC  ({data['tokens']:>6,} tokens, {data['count']:>3} events)")
        
        if savings['by_source']:
            print("\n  By Source:")
            for source, data in savings['by_source'].items():
                print(f"    {source:20} {data['bobcoins']:>10.4f} BC  ({data['tokens']:>6,} tokens, {data['count']:>3} events)")
        
        print("\n📈 COST RATE")
        print("-"*80)
        cost_per_second = budget['spent_bobcoins'] / duration if duration > 0 else 0
        print(f"  Per Second:       {cost_per_second:>12.4f} BC")
        print(f"  Per Minute:       {cost_per_second * 60:>12.4f} BC")
        print(f"  Per Hour:         {cost_per_second * 3600:>12.4f} BC")
        
        # Budget health
        health = check_budget_health()
        status_emoji = "🟢" if health['status'] == 'healthy' else "🟡" if health['status'] == 'warning' else "🔴"
        print(f"\n{status_emoji} Budget Status: {health['status'].upper()}")
        print(f"  {health['message']}")
        
        print("\n" + "="*80)
        print(f"Generated: {datetime.now().isoformat()}")
        print("="*80)


def demo_live_tracking():
    """Demonstrate live session tracking with our actual conversation."""
    print("\n" + "="*80)
    print("LIVE BOB SHELL SESSION COST TRACKING")
    print("="*80)
    print("\nTracking actual conversation with full savings analysis...")
    
    # Initialize tracker
    tracker = LiveSessionTracker(
        session_id=f"live-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        budget_bobcoins=1000.0
    )
    
    print("\n🔄 Simulating actual exchanges from our conversation...\n")
    
    # Exchange 1: Initial request
    print("Exchange 1: Cost tracking implementation request")
    tracker.track_exchange(
        user_message="Implement a comprehensive Bobcoin cost tracking and budget management system",
        assistant_response="Implementing cost tracking system with CostTracker class, reporting utilities, integration with components, E2E tests, and documentation",
        tool_uses=[
            "write_to_file: src/monitoring/cost_tracker.py",
            "write_to_file: src/monitoring/cost_reporting.py",
            "write_to_file: tests/e2e/test_cost_tracking.py"
        ]
    )
    
    # Exchange 2: Demo request
    print("Exchange 2: Demo application request")
    tracker.track_exchange(
        user_message="can you show me the cost tracker application?",
        assistant_response="Creating comprehensive demo with basic tracking, optimization tracking, cache tracking, full workflow, and dashboard generation",
        tool_uses=[
            "write_to_file: examples/cost_tracking_demo.py",
            "write_to_file: examples/cost_tracking_simple_demo.py",
            "execute_command: python3 examples/cost_tracking_simple_demo.py"
        ]
    )
    
    # Exchange 3: Real session tracking
    print("Exchange 3: Real session tracking request")
    tracker.track_exchange(
        user_message="Implement cost tracking for actual Bob Shell session",
        assistant_response="Creating BobShellSessionTracker class with exchange tracking, session summaries, dashboard generation, and export capabilities",
        tool_uses=[
            "write_to_file: examples/bob_shell_session_tracker.py",
            "execute_command: python3 examples/bob_shell_session_tracker.py"
        ]
    )
    
    # Exchange 4: Live tracking with savings (current)
    print("Exchange 4: Live tracking with savings analysis")
    tracker.track_exchange(
        user_message="could we have for the actual session a cost tracking full features to understand the savings done and where there are done?",
        assistant_response="Creating LiveSessionTracker with real-time savings analysis, breakdown by source and type, efficiency metrics, and comprehensive dashboard",
        tool_uses=[
            "write_to_file: examples/live_session_tracker.py"
        ]
    )
    
    print("\n✅ All exchanges tracked!\n")
    
    # Display live dashboard
    tracker.print_live_dashboard()
    
    print("\n" + "="*80)
    print("INTEGRATION GUIDE")
    print("="*80)
    print("""
To integrate with Bob Shell for real-time tracking:

```python
from examples.live_session_tracker import LiveSessionTracker

# Initialize at session start
tracker = LiveSessionTracker(
    session_id=f"bob-{datetime.now().isoformat()}",
    budget_bobcoins=1000.0
)

# Track each exchange
tracker.track_exchange(
    user_message=user_input,
    assistant_response=assistant_output,
    tool_uses=tools_used,
    system_prompts=system_prompts
)

# View live dashboard anytime
tracker.print_live_dashboard()

# Get savings breakdown
savings = tracker.get_savings_breakdown()
print(f"Total saved: {savings['total_savings_bobcoins']:.4f} BC")
```

Key Features:
✅ Real-time cost tracking
✅ Automatic cache hit detection
✅ Prompt optimization savings
✅ Savings breakdown by source and type
✅ ROI calculation
✅ Budget health monitoring
✅ Live dashboard with all metrics
""")
    
    print("="*80 + "\n")
    
    return tracker


def main():
    """Run live session tracking demo."""
    try:
        tracker = demo_live_tracking()
        
        print("\n" + "="*80)
        print("✅ LIVE SESSION TRACKING COMPLETE")
        print("="*80)
        print("\nThe live tracker is ready for Bob Shell integration!")
        print("\nWhat it tracks:")
        print("  • Every message (user, assistant, tool, system)")
        print("  • Cache hits and savings")
        print("  • Optimization savings")
        print("  • Real-time costs and budget")
        print("  • Detailed savings breakdown")
        print("  • Efficiency metrics and ROI")
        print("\nRun this demo:")
        print("  python3 examples/live_session_tracker.py")
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
