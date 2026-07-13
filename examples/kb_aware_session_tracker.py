#!/usr/bin/env python3
"""
Knowledge Base Aware Session Tracker

Extends LiveSessionTracker to track savings from knowledge base usage.
Tracks when KB prevents redundant research, documentation, or analysis.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.live_session_tracker import LiveSessionTracker


class KBAwareSessionTracker(LiveSessionTracker):
    """
    Session tracker that includes knowledge base usage savings.
    
    Tracks additional savings from:
    - KB lookups (avoiding redundant research)
    - Reusing documented knowledge
    - Avoiding duplicate documentation
    - Cross-reference efficiency
    """
    
    def __init__(self, session_id: str, budget_bobcoins: float = 1000.0):
        """Initialize KB-aware session tracker."""
        super().__init__(session_id, budget_bobcoins)
        
        # KB-specific tracking
        self.kb_lookups = []
        self.kb_savings = {
            "research_avoided": [],
            "documentation_reused": [],
            "cross_reference_hits": [],
            "duplicate_prevention": []
        }
    
    def track_kb_lookup(
        self,
        query: str,
        found: bool,
        documents_found: int = 0,
        estimated_research_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        Track a knowledge base lookup.
        
        Args:
            query: Search query
            found: Whether relevant documents were found
            documents_found: Number of documents found
            estimated_research_tokens: Tokens that would have been used for research
            
        Returns:
            Lookup tracking data
        """
        lookup = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "found": found,
            "documents_found": documents_found,
            "estimated_research_tokens": estimated_research_tokens
        }
        
        self.kb_lookups.append(lookup)
        
        if found and estimated_research_tokens > 0:
            # KB hit saved research tokens
            savings = {
                "type": "kb_research_avoided",
                "tokens_saved": estimated_research_tokens,
                "bobcoins_saved": estimated_research_tokens / 1000,
                "source": "knowledge_base_lookup",
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "documents_found": documents_found
            }
            self.savings_log.append(savings)
            self.kb_savings["research_avoided"].append(savings)
            
            # Track with cost tracker (record as savings only)
            self.tracker.metrics.record_cost(
                operation="kb_lookup",
                tokens_used=0,
                tokens_saved=estimated_research_tokens
            )
        
        return lookup
    
    def track_kb_reuse(
        self,
        document_path: str,
        content_tokens: int,
        reuse_type: str = "documentation"
    ) -> Dict[str, Any]:
        """
        Track reuse of existing KB documentation.
        
        Args:
            document_path: Path to KB document
            content_tokens: Tokens in reused content
            reuse_type: Type of reuse (documentation/guide/reference/concept)
            
        Returns:
            Reuse tracking data
        """
        savings = {
            "type": "kb_documentation_reused",
            "tokens_saved": content_tokens,
            "bobcoins_saved": content_tokens / 1000,
            "source": "knowledge_base_reuse",
            "timestamp": datetime.now().isoformat(),
            "document": document_path,
            "reuse_type": reuse_type
        }
        
        self.savings_log.append(savings)
        self.kb_savings["documentation_reused"].append(savings)
        
        # Track with cost tracker (record as savings only)
        self.tracker.metrics.record_cost(
            operation="kb_reuse",
            tokens_used=0,
            tokens_saved=content_tokens
        )
        
        return savings
    
    def track_cross_reference(
        self,
        from_doc: str,
        to_doc: str,
        tokens_saved: int
    ) -> Dict[str, Any]:
        """
        Track savings from cross-references between KB documents.
        
        Args:
            from_doc: Source document
            to_doc: Referenced document
            tokens_saved: Tokens saved by referencing instead of duplicating
            
        Returns:
            Cross-reference tracking data
        """
        savings = {
            "type": "kb_cross_reference",
            "tokens_saved": tokens_saved,
            "bobcoins_saved": tokens_saved / 1000,
            "source": "knowledge_base_cross_reference",
            "timestamp": datetime.now().isoformat(),
            "from_document": from_doc,
            "to_document": to_doc
        }
        
        self.savings_log.append(savings)
        self.kb_savings["cross_reference_hits"].append(savings)
        
        # Track with cost tracker (record as savings only)
        self.tracker.metrics.record_cost(
            operation="kb_cross_reference",
            tokens_used=0,
            tokens_saved=tokens_saved
        )
        
        return savings
    
    def track_duplicate_prevention(
        self,
        topic: str,
        existing_doc: str,
        tokens_saved: int
    ) -> Dict[str, Any]:
        """
        Track savings from preventing duplicate documentation.
        
        Args:
            topic: Topic that was already documented
            existing_doc: Path to existing document
            tokens_saved: Tokens saved by not creating duplicate
            
        Returns:
            Duplicate prevention tracking data
        """
        savings = {
            "type": "kb_duplicate_prevented",
            "tokens_saved": tokens_saved,
            "bobcoins_saved": tokens_saved / 1000,
            "source": "knowledge_base_duplicate_prevention",
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "existing_document": existing_doc
        }
        
        self.savings_log.append(savings)
        self.kb_savings["duplicate_prevention"].append(savings)
        
        # Track with cost tracker (record as savings only)
        self.tracker.metrics.record_cost(
            operation="kb_duplicate_prevention",
            tokens_used=0,
            tokens_saved=tokens_saved
        )
        
        return savings
    
    def get_kb_savings_breakdown(self) -> Dict[str, Any]:
        """Get detailed KB savings breakdown."""
        breakdown = {
            "total_kb_savings_bobcoins": 0.0,
            "total_kb_tokens_saved": 0,
            "kb_lookups_count": len(self.kb_lookups),
            "kb_hits": sum(1 for l in self.kb_lookups if l["found"]),
            "kb_hit_rate": 0.0,
            "by_kb_type": {}
        }
        
        # Calculate totals
        for category, savings_list in self.kb_savings.items():
            if savings_list:
                category_total_bc = sum(s["bobcoins_saved"] for s in savings_list)
                category_total_tokens = sum(s["tokens_saved"] for s in savings_list)
                
                breakdown["total_kb_savings_bobcoins"] += category_total_bc
                breakdown["total_kb_tokens_saved"] += category_total_tokens
                
                breakdown["by_kb_type"][category] = {
                    "bobcoins": category_total_bc,
                    "tokens": category_total_tokens,
                    "count": len(savings_list)
                }
        
        # Calculate hit rate
        if breakdown["kb_lookups_count"] > 0:
            breakdown["kb_hit_rate"] = (breakdown["kb_hits"] / breakdown["kb_lookups_count"]) * 100
        
        return breakdown
    
    def print_live_dashboard(self) -> None:
        """Print live dashboard with KB savings included."""
        # Call parent dashboard
        super().print_live_dashboard()
        
        # Add KB-specific section
        kb_savings = self.get_kb_savings_breakdown()
        
        if kb_savings["total_kb_savings_bobcoins"] > 0:
            print("\n" + "="*80)
            print("📚 KNOWLEDGE BASE SAVINGS")
            print("="*80)
            
            print(f"\n  Total KB Savings:  {kb_savings['total_kb_savings_bobcoins']:>12.4f} BC")
            print(f"  Tokens Saved:      {kb_savings['total_kb_tokens_saved']:>12,}")
            print(f"  KB Lookups:        {kb_savings['kb_lookups_count']:>12}")
            print(f"  KB Hits:           {kb_savings['kb_hits']:>12}")
            print(f"  Hit Rate:          {kb_savings['kb_hit_rate']:>12.1f}%")
            
            if kb_savings["by_kb_type"]:
                print("\n  Savings by KB Type:")
                for kb_type, data in kb_savings["by_kb_type"].items():
                    type_name = kb_type.replace("_", " ").title()
                    print(f"    {type_name:30} {data['bobcoins']:>10.4f} BC  ({data['tokens']:>6,} tokens, {data['count']:>3} events)")
            
            # Calculate KB contribution to total savings
            total_savings = self.get_savings_breakdown()["total_savings_bobcoins"]
            if total_savings > 0:
                kb_contribution = (kb_savings["total_kb_savings_bobcoins"] / total_savings) * 100
                print(f"\n  KB Contribution:   {kb_contribution:>12.1f}% of total savings")
            
            print("\n" + "="*80)


def demo_kb_aware_tracking():
    """Demonstrate KB-aware session tracking."""
    print("\n" + "="*80)
    print("KNOWLEDGE BASE AWARE SESSION TRACKING")
    print("="*80)
    print("\nTracking savings from knowledge base usage...\n")
    
    # Initialize tracker
    tracker = KBAwareSessionTracker(
        session_id="kb-demo-session",
        budget_bobcoins=1000.0
    )
    
    print("🔄 Simulating session with KB interactions...\n")
    
    # Exchange 1: User asks about token optimization
    print("Exchange 1: User asks about token optimization")
    
    # KB lookup finds existing documentation
    tracker.track_kb_lookup(
        query="token optimization",
        found=True,
        documents_found=2,
        estimated_research_tokens=500  # Would have needed research
    )
    
    # Reuse existing concept document
    tracker.track_kb_reuse(
        document_path="concepts/token-optimization.md",
        content_tokens=300,
        reuse_type="concept"
    )
    
    tracker.track_exchange(
        user_message="What is token optimization?",
        assistant_response="Based on our knowledge base, token optimization is a systematic approach to reducing LLM token consumption through caching, optimization, and truncation. [Referenced: concepts/token-optimization.md]",
        tool_uses=["read_file: concepts/token-optimization.md"]
    )
    
    # Exchange 2: User asks about caching
    print("Exchange 2: User asks about multi-level caching")
    
    # KB lookup finds documentation
    tracker.track_kb_lookup(
        query="multi-level caching",
        found=True,
        documents_found=1,
        estimated_research_tokens=400
    )
    
    # Cross-reference to related concept
    tracker.track_cross_reference(
        from_doc="concepts/multi-level-caching.md",
        to_doc="concepts/token-optimization.md",
        tokens_saved=150  # Saved by referencing instead of duplicating
    )
    
    tracker.track_exchange(
        user_message="Explain multi-level caching",
        assistant_response="Multi-level caching combines L1 (exact match) and L2 (semantic similarity) caches. See concepts/multi-level-caching.md for details.",
        tool_uses=["read_file: concepts/multi-level-caching.md"]
    )
    
    # Exchange 3: User wants to document something already documented
    print("Exchange 3: User wants to create guide (already exists)")
    
    # Prevent duplicate documentation
    tracker.track_duplicate_prevention(
        topic="setting up token optimization",
        existing_doc="guides/setup-token-optimization.md",
        tokens_saved=800  # Saved by not creating duplicate
    )
    
    tracker.track_exchange(
        user_message="Create a guide for setting up token optimization",
        assistant_response="A comprehensive guide already exists at guides/setup-token-optimization.md. Would you like me to update it instead?",
        tool_uses=["search_docs: setup token optimization"]
    )
    
    # Exchange 4: KB lookup miss (needs research)
    print("Exchange 4: New topic requiring research")
    
    # KB lookup doesn't find anything
    tracker.track_kb_lookup(
        query="quantum computing integration",
        found=False,
        documents_found=0,
        estimated_research_tokens=0  # No savings, needs research
    )
    
    tracker.track_exchange(
        user_message="How do we integrate quantum computing?",
        assistant_response="This is a new topic not yet in our knowledge base. Let me research and create documentation...",
        tool_uses=["web_fetch: quantum computing integration"]
    )
    
    # Exchange 5: Reuse guide
    print("Exchange 5: User needs setup instructions")
    
    tracker.track_kb_lookup(
        query="cost tracking setup",
        found=True,
        documents_found=1,
        estimated_research_tokens=600
    )
    
    tracker.track_kb_reuse(
        document_path="guides/cost-tracking-guide.md",
        content_tokens=450,
        reuse_type="guide"
    )
    
    tracker.track_exchange(
        user_message="How do I set up cost tracking?",
        assistant_response="Follow the comprehensive guide at guides/cost-tracking-guide.md which covers installation, configuration, and usage.",
        tool_uses=["read_file: guides/cost-tracking-guide.md"]
    )
    
    print("\n✅ All exchanges tracked with KB savings!\n")
    
    # Display comprehensive dashboard
    tracker.print_live_dashboard()
    
    # Show detailed KB analysis
    kb_savings = tracker.get_kb_savings_breakdown()
    
    print("\n" + "="*80)
    print("📊 DETAILED KB IMPACT ANALYSIS")
    print("="*80)
    
    print(f"\nKB Efficiency:")
    print(f"  Lookups:          {kb_savings['kb_lookups_count']}")
    print(f"  Hits:             {kb_savings['kb_hits']}")
    print(f"  Misses:           {kb_savings['kb_lookups_count'] - kb_savings['kb_hits']}")
    print(f"  Hit Rate:         {kb_savings['kb_hit_rate']:.1f}%")
    
    print(f"\nKB Savings Impact:")
    print(f"  Total Saved:      {kb_savings['total_kb_savings_bobcoins']:.4f} BC")
    print(f"  Tokens Saved:     {kb_savings['total_kb_tokens_saved']:,}")
    
    # Calculate what would have been spent without KB
    total_savings = tracker.get_savings_breakdown()
    budget = tracker.tracker.get_budget_status()
    without_kb = budget['spent_bobcoins'] + kb_savings['total_kb_savings_bobcoins']
    
    print(f"\nCost Comparison:")
    print(f"  With KB:          {budget['spent_bobcoins']:.4f} BC")
    print(f"  Without KB:       {without_kb:.4f} BC (estimated)")
    print(f"  KB Savings:       {kb_savings['total_kb_savings_bobcoins']:.4f} BC")
    print(f"  Efficiency Gain:  {(kb_savings['total_kb_savings_bobcoins'] / without_kb * 100):.1f}%")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nThe KB-aware tracker shows:")
    print("  ✓ Savings from KB lookups (avoiding research)")
    print("  ✓ Savings from reusing documentation")
    print("  ✓ Savings from cross-references")
    print("  ✓ Savings from duplicate prevention")
    print("  ✓ KB hit rate and efficiency metrics")
    print("  ✓ Total KB contribution to cost savings")
    print("\nIntegrate with Bob Shell to track KB value!")
    print("="*80 + "\n")
    
    return tracker


def main():
    """Run KB-aware tracking demo."""
    try:
        tracker = demo_kb_aware_tracking()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
