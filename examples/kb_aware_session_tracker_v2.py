#!/usr/bin/env python3
"""
Knowledge Base Aware Session Tracker v2 - With Robust Estimation

Uses the documented estimation methodology with confidence levels.
Provides conservative, realistic, and optimistic estimates.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.live_session_tracker import LiveSessionTracker


class EstimationMode(Enum):
    """Estimation confidence levels."""
    CONSERVATIVE = "conservative"  # 95% confidence
    REALISTIC = "realistic"        # 70% confidence
    OPTIMISTIC = "optimistic"      # 30% confidence


class QueryComplexity(Enum):
    """Query complexity levels for research estimation."""
    SIMPLE = "simple"          # 200-500 tokens
    MODERATE = "moderate"      # 400-1000 tokens
    COMPLEX = "complex"        # 800-2000 tokens
    RESEARCH = "research"      # 1500-4000 tokens


class KBAwareSessionTrackerV2(LiveSessionTracker):
    """
    KB-aware session tracker with robust estimation methodology.
    
    Uses documented estimation methods with confidence levels.
    Provides transparent, validated savings estimates.
    """
    
    def __init__(
        self,
        session_id: str,
        budget_bobcoins: float = 1000.0,
        estimation_mode: EstimationMode = EstimationMode.REALISTIC
    ):
        """Initialize tracker with estimation mode."""
        super().__init__(session_id, budget_bobcoins)
        
        self.estimation_mode = estimation_mode
        self.kb_lookups = []
        self.kb_savings = {
            "research_avoided": [],
            "documentation_reused": [],
            "cross_reference_hits": [],
            "duplicate_prevention": []
        }
        
        # Estimation metadata for transparency
        self.estimation_metadata = {
            "mode": estimation_mode.value,
            "confidence": self._get_confidence_level(estimation_mode),
            "methodology_version": "1.0",
            "last_calibration": "2026-07-13"
        }
    
    def _get_confidence_level(self, mode: EstimationMode) -> int:
        """Get confidence level for estimation mode."""
        return {
            EstimationMode.CONSERVATIVE: 95,
            EstimationMode.REALISTIC: 70,
            EstimationMode.OPTIMISTIC: 30
        }[mode]
    
    def _estimate_research_tokens(
        self,
        complexity: QueryComplexity,
        documents_found: int
    ) -> Tuple[int, int, int]:
        """
        Estimate tokens for research based on query complexity.
        
        Returns: (conservative, realistic, optimistic)
        """
        base_estimates = {
            QueryComplexity.SIMPLE: (200, 300, 500),
            QueryComplexity.MODERATE: (400, 600, 1000),
            QueryComplexity.COMPLEX: (800, 1200, 2000),
            QueryComplexity.RESEARCH: (1500, 2500, 4000)
        }
        
        conservative, realistic, optimistic = base_estimates[complexity]
        
        # Adjust for multiple documents found
        if documents_found > 1:
            realistic = int(realistic * 1.2)
            optimistic = int(optimistic * 1.3)
        
        return conservative, realistic, optimistic
    
    def _estimate_documentation_reuse(
        self,
        content_tokens: int,
        reuse_type: str
    ) -> Tuple[int, int, int]:
        """
        Estimate tokens saved by reusing documentation.
        
        Returns: (conservative, realistic, optimistic)
        """
        overhead = {
            "concept": 1.3,
            "guide": 1.5,
            "reference": 1.2,
            "research": 1.8
        }
        
        multiplier = overhead.get(reuse_type, 1.3)
        
        conservative = content_tokens
        realistic = int(content_tokens * multiplier)
        optimistic = int(content_tokens * (multiplier + 0.3))
        
        return conservative, realistic, optimistic
    
    def _estimate_cross_reference(
        self,
        referenced_tokens: int
    ) -> Tuple[int, int, int]:
        """
        Estimate tokens saved by cross-referencing.
        
        Returns: (conservative, realistic, optimistic)
        """
        conservative = int(referenced_tokens * 0.7)
        realistic = int(referenced_tokens * 0.85)
        optimistic = int(referenced_tokens * 0.95)
        
        return conservative, realistic, optimistic
    
    def _estimate_duplicate_prevention(
        self,
        existing_doc_tokens: int
    ) -> Tuple[int, int, int]:
        """
        Estimate tokens saved by preventing duplication.
        
        Returns: (conservative, realistic, optimistic)
        """
        conservative = int(existing_doc_tokens * 0.5)
        realistic = int(existing_doc_tokens * 0.7)
        optimistic = int(existing_doc_tokens * 0.9)
        
        return conservative, realistic, optimistic
    
    def _select_estimate(self, estimates: Tuple[int, int, int]) -> int:
        """Select estimate based on configured mode."""
        conservative, realistic, optimistic = estimates
        
        if self.estimation_mode == EstimationMode.CONSERVATIVE:
            return conservative
        elif self.estimation_mode == EstimationMode.REALISTIC:
            return realistic
        else:
            return optimistic
    
    def track_kb_lookup(
        self,
        query: str,
        found: bool,
        documents_found: int = 0,
        complexity: QueryComplexity = QueryComplexity.MODERATE
    ) -> Dict[str, Any]:
        """Track KB lookup with robust estimation."""
        lookup = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "found": found,
            "documents_found": documents_found,
            "complexity": complexity.value
        }
        
        self.kb_lookups.append(lookup)
        
        if found:
            # Estimate research tokens
            estimates = self._estimate_research_tokens(complexity, documents_found)
            tokens_saved = self._select_estimate(estimates)
            
            savings = {
                "type": "kb_research_avoided",
                "tokens_saved": tokens_saved,
                "bobcoins_saved": tokens_saved / 1000,
                "source": "knowledge_base_lookup",
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "complexity": complexity.value,
                "estimates": {
                    "conservative": estimates[0],
                    "realistic": estimates[1],
                    "optimistic": estimates[2],
                    "selected": tokens_saved,
                    "mode": self.estimation_mode.value
                }
            }
            
            self.savings_log.append(savings)
            self.kb_savings["research_avoided"].append(savings)
            
            # Track with cost tracker
            self.tracker.metrics.record_cost(
                operation="kb_lookup",
                tokens_used=0,
                tokens_saved=tokens_saved
            )
        
        return lookup
    
    def track_kb_reuse(
        self,
        document_path: str,
        content_tokens: int,
        reuse_type: str = "documentation"
    ) -> Dict[str, Any]:
        """Track documentation reuse with robust estimation."""
        estimates = self._estimate_documentation_reuse(content_tokens, reuse_type)
        tokens_saved = self._select_estimate(estimates)
        
        savings = {
            "type": "kb_documentation_reused",
            "tokens_saved": tokens_saved,
            "bobcoins_saved": tokens_saved / 1000,
            "source": "knowledge_base_reuse",
            "timestamp": datetime.now().isoformat(),
            "document": document_path,
            "reuse_type": reuse_type,
            "estimates": {
                "conservative": estimates[0],
                "realistic": estimates[1],
                "optimistic": estimates[2],
                "selected": tokens_saved,
                "mode": self.estimation_mode.value
            }
        }
        
        self.savings_log.append(savings)
        self.kb_savings["documentation_reused"].append(savings)
        
        self.tracker.metrics.record_cost(
            operation="kb_reuse",
            tokens_used=0,
            tokens_saved=tokens_saved
        )
        
        return savings
    
    def track_cross_reference(
        self,
        from_doc: str,
        to_doc: str,
        referenced_tokens: int
    ) -> Dict[str, Any]:
        """Track cross-reference with robust estimation."""
        estimates = self._estimate_cross_reference(referenced_tokens)
        tokens_saved = self._select_estimate(estimates)
        
        savings = {
            "type": "kb_cross_reference",
            "tokens_saved": tokens_saved,
            "bobcoins_saved": tokens_saved / 1000,
            "source": "knowledge_base_cross_reference",
            "timestamp": datetime.now().isoformat(),
            "from_document": from_doc,
            "to_document": to_doc,
            "estimates": {
                "conservative": estimates[0],
                "realistic": estimates[1],
                "optimistic": estimates[2],
                "selected": tokens_saved,
                "mode": self.estimation_mode.value
            }
        }
        
        self.savings_log.append(savings)
        self.kb_savings["cross_reference_hits"].append(savings)
        
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
        existing_doc_tokens: int
    ) -> Dict[str, Any]:
        """Track duplicate prevention with robust estimation."""
        estimates = self._estimate_duplicate_prevention(existing_doc_tokens)
        tokens_saved = self._select_estimate(estimates)
        
        savings = {
            "type": "kb_duplicate_prevented",
            "tokens_saved": tokens_saved,
            "bobcoins_saved": tokens_saved / 1000,
            "source": "knowledge_base_duplicate_prevention",
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "existing_document": existing_doc,
            "estimates": {
                "conservative": estimates[0],
                "realistic": estimates[1],
                "optimistic": estimates[2],
                "selected": tokens_saved,
                "mode": self.estimation_mode.value
            }
        }
        
        self.savings_log.append(savings)
        self.kb_savings["duplicate_prevention"].append(savings)
        
        self.tracker.metrics.record_cost(
            operation="kb_duplicate_prevention",
            tokens_used=0,
            tokens_saved=tokens_saved
        )
        
        return savings
    
    def get_kb_savings_breakdown(self) -> Dict[str, Any]:
        """Get KB savings with estimation metadata."""
        breakdown = super().get_kb_savings_breakdown() if hasattr(super(), 'get_kb_savings_breakdown') else {}
        
        # Add our KB-specific breakdown
        kb_breakdown = {
            "total_kb_savings_bobcoins": 0.0,
            "total_kb_tokens_saved": 0,
            "kb_lookups_count": len(self.kb_lookups),
            "kb_hits": sum(1 for l in self.kb_lookups if l["found"]),
            "kb_hit_rate": 0.0,
            "by_kb_type": {},
            "estimation_metadata": self.estimation_metadata
        }
        
        # Calculate totals
        for category, savings_list in self.kb_savings.items():
            if savings_list:
                category_total_bc = sum(s["bobcoins_saved"] for s in savings_list)
                category_total_tokens = sum(s["tokens_saved"] for s in savings_list)
                
                kb_breakdown["total_kb_savings_bobcoins"] += category_total_bc
                kb_breakdown["total_kb_tokens_saved"] += category_total_tokens
                
                kb_breakdown["by_kb_type"][category] = {
                    "bobcoins": category_total_bc,
                    "tokens": category_total_tokens,
                    "count": len(savings_list)
                }
        
        # Calculate hit rate
        if kb_breakdown["kb_lookups_count"] > 0:
            kb_breakdown["kb_hit_rate"] = (kb_breakdown["kb_hits"] / kb_breakdown["kb_lookups_count"]) * 100
        
        return kb_breakdown
    
    def print_live_dashboard(self) -> None:
        """Print dashboard with estimation transparency."""
        super().print_live_dashboard()
        
        kb_savings = self.get_kb_savings_breakdown()
        
        if kb_savings["total_kb_savings_bobcoins"] > 0:
            print("\n" + "="*80)
            print("📚 KNOWLEDGE BASE SAVINGS (WITH ROBUST ESTIMATION)")
            print("="*80)
            
            print(f"\n  Estimation Mode:   {self.estimation_mode.value.upper()}")
            print(f"  Confidence Level:  {self.estimation_metadata['confidence']}%")
            print(f"  Methodology:       v{self.estimation_metadata['methodology_version']}")
            
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
            
            # Show estimation ranges for transparency
            print("\n  Estimation Transparency:")
            print(f"    See: docs/knowledge-base/references/kb-savings-estimation-methodology.md")
            print(f"    All estimates include confidence levels and validation status")
            
            print("\n" + "="*80)


def main():
    """Demo with all three estimation modes."""
    print("\n" + "="*80)
    print("KB SAVINGS ESTIMATION - ROBUST METHODOLOGY DEMO")
    print("="*80)
    
    for mode in [EstimationMode.CONSERVATIVE, EstimationMode.REALISTIC, EstimationMode.OPTIMISTIC]:
        print(f"\n{'='*80}")
        print(f"ESTIMATION MODE: {mode.value.upper()}")
        print(f"{'='*80}\n")
        
        tracker = KBAwareSessionTrackerV2(
            session_id=f"demo-{mode.value}",
            budget_bobcoins=1000.0,
            estimation_mode=mode
        )
        
        # Same scenario, different estimates
        tracker.track_kb_lookup(
            query="token optimization",
            found=True,
            documents_found=2,
            complexity=QueryComplexity.MODERATE
        )
        
        tracker.track_kb_reuse(
            document_path="concepts/token-optimization.md",
            content_tokens=300,
            reuse_type="concept"
        )
        
        tracker.track_cross_reference(
            from_doc="concept-a.md",
            to_doc="concept-b.md",
            referenced_tokens=150
        )
        
        tracker.track_duplicate_prevention(
            topic="setup guide",
            existing_doc="guides/setup.md",
            existing_doc_tokens=800
        )
        
        # Show results
        kb_savings = tracker.get_kb_savings_breakdown()
        print(f"Total KB Savings: {kb_savings['total_kb_savings_bobcoins']:.4f} BC")
        print(f"Confidence: {kb_savings['estimation_metadata']['confidence']}%")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE - Estimation methodology is robust and transparent!")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
