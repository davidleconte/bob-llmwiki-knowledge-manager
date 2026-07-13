#!/usr/bin/env python3
"""
Bob Shell Session Cost Tracker

Integration example showing how Bob Shell could track actual session costs.
This demonstrates tracking real conversation costs in a Bob Shell session.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimizer import TokenCounter
from src.monitoring.cost_tracker import get_cost_tracker, reset_cost_tracker
from src.monitoring.cost_reporting import generate_cost_dashboard


class BobShellSessionTracker:
    """
    Tracks costs for a Bob Shell conversation session.
    
    Integrates with Bob Shell to monitor:
    - User message tokens
    - Assistant response tokens
    - Tool usage tokens
    - Total session costs
    """
    
    def __init__(self, session_id: str, budget_bobcoins: float = 1000.0):
        """
        Initialize session tracker.
        
        Args:
            session_id: Unique session identifier
            budget_bobcoins: Budget for this session
        """
        self.session_id = session_id
        self.start_time = datetime.utcnow()
        
        # Initialize cost tracker
        reset_cost_tracker()
        self.tracker = get_cost_tracker(budget_bobcoins=budget_bobcoins)
        
        # Initialize token counter with cost tracking
        self.counter = TokenCounter(model="gpt-4", track_costs=True)
        
        # Session statistics
        self.exchanges = []
        self.total_user_tokens = 0
        self.total_assistant_tokens = 0
        self.total_tool_tokens = 0
    
    def track_exchange(
        self,
        user_message: str,
        assistant_response: str,
        tool_uses: List[str] = None
    ) -> Dict[str, Any]:
        """
        Track a single conversation exchange.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            tool_uses: List of tool usage descriptions
            
        Returns:
            Dictionary with exchange statistics
        """
        # Count tokens
        user_tokens = self.counter.count_tokens(user_message)
        assistant_tokens = self.counter.count_tokens(assistant_response)
        
        tool_tokens = 0
        if tool_uses:
            for tool_use in tool_uses:
                tool_tokens += self.counter.count_tokens(tool_use)
        
        # Update totals
        self.total_user_tokens += user_tokens
        self.total_assistant_tokens += assistant_tokens
        self.total_tool_tokens += tool_tokens
        
        # Record exchange
        exchange = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_tokens": user_tokens,
            "assistant_tokens": assistant_tokens,
            "tool_tokens": tool_tokens,
            "total_tokens": user_tokens + assistant_tokens + tool_tokens
        }
        self.exchanges.append(exchange)
        
        return exchange
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive session summary.
        
        Returns:
            Dictionary with session statistics
        """
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Get cost metrics
        cost_metrics = self.tracker.get_cost_metrics()
        budget_status = self.tracker.get_budget_status()
        
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() + "Z",
            "duration_seconds": round(duration, 2),
            "exchanges": len(self.exchanges),
            "tokens": {
                "user": self.total_user_tokens,
                "assistant": self.total_assistant_tokens,
                "tools": self.total_tool_tokens,
                "total": self.total_user_tokens + self.total_assistant_tokens + self.total_tool_tokens
            },
            "costs": {
                "spent_bobcoins": budget_status['spent_bobcoins'],
                "budget_bobcoins": budget_status['budget_bobcoins'],
                "remaining_bobcoins": budget_status['remaining_bobcoins'],
                "percent_used": budget_status['percent_used']
            },
            "averages": {
                "tokens_per_exchange": round(
                    (self.total_user_tokens + self.total_assistant_tokens + self.total_tool_tokens) / len(self.exchanges)
                    if self.exchanges else 0, 2
                ),
                "cost_per_exchange": round(
                    budget_status['spent_bobcoins'] / len(self.exchanges)
                    if self.exchanges else 0, 4
                )
            }
        }
    
    def print_session_dashboard(self) -> None:
        """Print session cost dashboard."""
        summary = self.get_session_summary()
        
        print("\n" + "="*70)
        print(f"BOB SHELL SESSION COST TRACKER - {self.session_id}")
        print("="*70)
        
        print("\nSESSION INFO")
        print("-"*70)
        print(f"  Start Time:       {summary['start_time']}")
        print(f"  Duration:         {summary['duration_seconds']:.2f} seconds")
        print(f"  Exchanges:        {summary['exchanges']}")
        
        print("\nTOKEN USAGE")
        print("-"*70)
        print(f"  User Messages:    {summary['tokens']['user']:>10,} tokens")
        print(f"  Assistant:        {summary['tokens']['assistant']:>10,} tokens")
        print(f"  Tool Usage:       {summary['tokens']['tools']:>10,} tokens")
        print(f"  Total:            {summary['tokens']['total']:>10,} tokens")
        
        print("\nCOST SUMMARY")
        print("-"*70)
        print(f"  Budget:           {summary['costs']['budget_bobcoins']:>10.4f} BC")
        print(f"  Spent:            {summary['costs']['spent_bobcoins']:>10.4f} BC")
        print(f"  Remaining:        {summary['costs']['remaining_bobcoins']:>10.4f} BC")
        print(f"  Used:             {summary['costs']['percent_used']:>10.2f}%")
        
        # Budget bar
        bar_width = 50
        used_width = int((summary['costs']['percent_used'] / 100) * bar_width)
        bar = "█" * used_width + "░" * (bar_width - used_width)
        print(f"  [{bar}]")
        
        print("\nAVERAGES")
        print("-"*70)
        print(f"  Tokens/Exchange:  {summary['averages']['tokens_per_exchange']:>10.2f}")
        print(f"  Cost/Exchange:    {summary['averages']['cost_per_exchange']:>10.4f} BC")
        
        print("\n" + "="*70)
    
    def export_session_data(self, filepath: str) -> None:
        """
        Export session data to JSON file.
        
        Args:
            filepath: Path to export file
        """
        import json
        
        summary = self.get_session_summary()
        summary['exchanges_detail'] = self.exchanges
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Session data exported to: {filepath}")


def demo_current_session():
    """
    Demonstrate tracking a Bob Shell session.
    
    This simulates what would happen if Bob Shell integrated cost tracking
    for the actual conversation we're having right now.
    """
    print("\n" + "="*70)
    print("BOB SHELL SESSION COST TRACKING DEMO")
    print("="*70)
    print("\nThis demonstrates how Bob Shell could track the actual session costs")
    print("for our current conversation.\n")
    
    # Initialize session tracker
    session = BobShellSessionTracker(
        session_id="bob-session-2026-07-13",
        budget_bobcoins=1000.0
    )
    
    # Simulate exchanges from our actual conversation
    # (These are approximations of our real exchanges)
    
    print("Tracking conversation exchanges...")
    
    # Exchange 1: Initial task
    session.track_exchange(
        user_message="add lessons learned to knowledge base",
        assistant_response="Got it. Thanks for the additional context! [Created E2E testing guide with lessons learned]",
        tool_uses=["write_to_file: e2e-testing-setup-guide.md"]
    )
    print("  ✓ Exchange 1: E2E testing guide creation")
    
    # Exchange 2: Update INDEX
    session.track_exchange(
        user_message="[Automatic continuation]",
        assistant_response="[Updated knowledge base INDEX with new guide]",
        tool_uses=["read_file: INDEX.md", "apply_diff: INDEX.md"]
    )
    print("  ✓ Exchange 2: Knowledge base INDEX update")
    
    # Exchange 3: Next steps
    session.track_exchange(
        user_message="what are the next best tasks based on the plan?",
        assistant_response="Based on the improvement plan and current status, here are the best next tasks prioritized by impact...",
        tool_uses=["read_file: PROJECT_STATUS.md", "read_file: repository-improvement-plan.md"]
    )
    print("  ✓ Exchange 3: Next steps analysis")
    
    # Exchange 4: Cost tracking implementation
    session.track_exchange(
        user_message="Implement Cost Tracking System - Bobcoin monitoring and metrics (4 days, high impact)",
        assistant_response="[Implemented comprehensive cost tracking system with CostTracker, reporting utilities, integration, tests, and documentation]",
        tool_uses=[
            "write_to_file: cost_tracker.py",
            "write_to_file: cost_reporting.py",
            "apply_diff: token_counter.py",
            "apply_diff: exact_cache.py",
            "apply_diff: semantic_cache.py",
            "apply_diff: prompt_optimizer.py",
            "write_to_file: test_cost_tracking.py",
            "write_to_file: cost-tracking-guide.md",
            "apply_diff: PROJECT_STATUS.md",
            "apply_diff: INDEX.md"
        ]
    )
    print("  ✓ Exchange 4: Cost tracking implementation")
    
    # Exchange 5: Demo request
    session.track_exchange(
        user_message="can you show me the cost tracker application?",
        assistant_response="[Created and ran cost tracking demos showing live dashboard and metrics]",
        tool_uses=[
            "write_to_file: cost_tracking_demo.py",
            "write_to_file: cost_tracking_simple_demo.py",
            "execute_command: python3 cost_tracking_simple_demo.py"
        ]
    )
    print("  ✓ Exchange 5: Demo creation and execution")
    
    # Exchange 6: Current exchange
    session.track_exchange(
        user_message="Implement cost tracking for actual Bob Shell session",
        assistant_response="[Creating Bob Shell session tracker integration example]",
        tool_uses=["write_to_file: bob_shell_session_tracker.py"]
    )
    print("  ✓ Exchange 6: Session tracker implementation")
    
    print("\n" + "-"*70)
    print("Session tracking complete!")
    print("-"*70)
    
    # Display dashboard
    session.print_session_dashboard()
    
    # Show how to integrate with Bob Shell
    print("\n" + "="*70)
    print("HOW TO INTEGRATE WITH BOB SHELL")
    print("="*70)
    print("""
Bob Shell would need to add this to its conversation loop:

```python
from examples.bob_shell_session_tracker import BobShellSessionTracker

# Initialize at session start
session_tracker = BobShellSessionTracker(
    session_id=f"bob-{datetime.now().isoformat()}",
    budget_bobcoins=1000.0
)

# Track each exchange
def process_user_message(user_msg):
    # Get assistant response
    assistant_response = generate_response(user_msg)
    
    # Track tool uses if any
    tool_uses = extract_tool_uses(assistant_response)
    
    # Track the exchange
    session_tracker.track_exchange(
        user_message=user_msg,
        assistant_response=assistant_response,
        tool_uses=tool_uses
    )
    
    return assistant_response

# Display costs at any time
session_tracker.print_session_dashboard()

# Export session data
session_tracker.export_session_data('session_costs.json')
```

This would provide real-time cost tracking for every Bob Shell conversation!
""")
    
    print("="*70)
    
    return session


def main():
    """Run the demo."""
    try:
        session = demo_current_session()
        
        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print("\nThe session tracker is ready for Bob Shell integration!")
        print("\nKey Features:")
        print("  ✓ Tracks every conversation exchange")
        print("  ✓ Monitors user, assistant, and tool token usage")
        print("  ✓ Calculates real-time costs in Bobcoins")
        print("  ✓ Provides session dashboard and summaries")
        print("  ✓ Exports session data for analysis")
        print("\nNext Steps:")
        print("  1. Bob Shell developers integrate BobShellSessionTracker")
        print("  2. Track actual conversation costs in real-time")
        print("  3. Monitor budget usage across sessions")
        print("  4. Optimize based on cost insights")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
