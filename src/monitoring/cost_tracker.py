"""
Cost tracking module for the Token Optimization System.

Provides Bobcoin cost tracking, budget monitoring, and cost optimization metrics.
Integrates with the existing metrics system to provide comprehensive cost visibility.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from src import pricing

# Pricing/Bobcoin constants have one home (src.pricing). Re-exported here so
# this module's public API is unchanged.
TOKENS_PER_BOBCOIN = pricing.TOKENS_PER_BOBCOIN
DEFAULT_BUDGET_BOBCOINS = pricing.DEFAULT_BUDGET_BOBCOINS


@dataclass
class CostMetrics:
    """Metrics for cost tracking."""
    total_tokens_used: int = 0
    total_tokens_saved: int = 0
    total_bobcoins_spent: float = 0.0
    total_bobcoins_saved: float = 0.0
    operations_count: int = 0

    # Cost breakdown by operation type
    cost_by_operation: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    tokens_by_operation: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Savings breakdown
    savings_by_source: Dict[str, float] = field(default_factory=lambda: defaultdict(float))

    def record_cost(
        self,
        operation: str,
        tokens_used: int,
        tokens_saved: int = 0
    ) -> Tuple[float, float]:
        """
        Record cost for an operation.
        
        Args:
            operation: Operation type (e.g., "token_counting", "optimization", "cache_hit")
            tokens_used: Number of tokens used
            tokens_saved: Number of tokens saved (if applicable)
            
        Returns:
            Tuple of (bobcoins_spent, bobcoins_saved)
        """
        bobcoins_spent = tokens_used / TOKENS_PER_BOBCOIN
        bobcoins_saved = tokens_saved / TOKENS_PER_BOBCOIN

        self.total_tokens_used += tokens_used
        self.total_tokens_saved += tokens_saved
        self.total_bobcoins_spent += bobcoins_spent
        self.total_bobcoins_saved += bobcoins_saved
        self.operations_count += 1

        self.cost_by_operation[operation] += bobcoins_spent
        self.tokens_by_operation[operation] += tokens_used

        if tokens_saved > 0:
            self.savings_by_source[operation] += bobcoins_saved

        return bobcoins_spent, bobcoins_saved

    def get_net_cost(self) -> float:
        """Calculate net cost (spent - saved)."""
        return self.total_bobcoins_spent - self.total_bobcoins_saved

    def get_roi_percent(self) -> float:
        """Calculate ROI percentage."""
        if self.total_bobcoins_spent == 0:
            return 0.0
        return (self.total_bobcoins_saved / self.total_bobcoins_spent) * 100

    def get_average_cost_per_operation(self) -> float:
        """Calculate average cost per operation."""
        if self.operations_count == 0:
            return 0.0
        return self.total_bobcoins_spent / self.operations_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_tokens_saved": self.total_tokens_saved,
            "total_bobcoins_spent": round(self.total_bobcoins_spent, 4),
            "total_bobcoins_saved": round(self.total_bobcoins_saved, 4),
            "net_cost_bobcoins": round(self.get_net_cost(), 4),
            "roi_percent": round(self.get_roi_percent(), 2),
            "operations_count": self.operations_count,
            "avg_cost_per_operation": round(self.get_average_cost_per_operation(), 4),
            "cost_by_operation": {
                k: round(v, 4) for k, v in self.cost_by_operation.items()
            },
            "tokens_by_operation": dict(self.tokens_by_operation),
            "savings_by_source": {
                k: round(v, 4) for k, v in self.savings_by_source.items()
            }
        }


@dataclass
class BudgetAlert:
    """Budget alert configuration and state."""
    threshold_percent: float
    triggered: bool = False
    triggered_at: Optional[datetime] = None

    def check(self, spent: float, budget: float) -> bool:
        """
        Check if alert should trigger.
        
        Args:
            spent: Amount spent
            budget: Total budget
            
        Returns:
            True if alert should trigger
        """
        if budget <= 0:
            return False

        percent_used = (spent / budget) * 100
        should_trigger = percent_used >= self.threshold_percent and not self.triggered

        if should_trigger:
            self.triggered = True
            self.triggered_at = datetime.now(timezone.utc)

        return should_trigger

    def reset(self) -> None:
        """Reset alert state."""
        self.triggered = False
        self.triggered_at = None


class CostTracker:
    """
    Cost tracking system for Bobcoin monitoring and budget management.
    
    Features:
    - Real-time cost tracking per operation
    - Token-to-Bobcoin conversion
    - Budget monitoring with alerts
    - ROI calculation
    - Cost breakdown by operation type
    - Savings tracking by source
    
    Example:
        >>> tracker = CostTracker(budget_bobcoins=100.0)
        >>> tracker.record_token_counting(1500)  # 1.5 Bobcoins
        >>> tracker.record_cache_hit(1000)  # Saved 1.0 Bobcoins
        >>> print(tracker.get_budget_status())
        {'spent': 1.5, 'saved': 1.0, 'remaining': 98.5, 'percent_used': 1.5}
    """

    def __init__(
        self,
        budget_bobcoins: float = DEFAULT_BUDGET_BOBCOINS,
        alert_thresholds: Optional[List[float]] = None
    ):
        """
        Initialize cost tracker.
        
        Args:
            budget_bobcoins: Total budget in Bobcoins
            alert_thresholds: List of alert thresholds (e.g., [50, 75, 90])
        """
        # RLock (re-entrant): reset()/set_budget() hold the lock and then call
        # reset_alerts(), which re-acquires it. A plain Lock self-deadlocks there
        # — the same C-8b bug already fixed for MetricsCollector (metrics.py:213).
        self._lock = RLock()
        self.budget_bobcoins = budget_bobcoins
        self.metrics = CostMetrics()

        # Budget alerts
        if alert_thresholds is None:
            alert_thresholds = [50.0, 75.0, 90.0]
        self.alerts = [BudgetAlert(threshold) for threshold in alert_thresholds]

        # Recent costs for trend analysis
        self.recent_costs: deque = deque(maxlen=100)

        # Start time for rate calculations
        self._start_time = time.time()

    def record_token_counting(self, tokens: int) -> float:
        """
        Record token counting operation cost.
        
        Args:
            tokens: Number of tokens counted
            
        Returns:
            Bobcoins spent
        """
        with self._lock:
            spent, _ = self.metrics.record_cost("token_counting", tokens)
            self.recent_costs.append(("token_counting", spent, time.time()))
            self._check_alerts()
            return spent

    def record_optimization(
        self,
        original_tokens: int,
        optimized_tokens: int
    ) -> Tuple[float, float]:
        """
        Record optimization operation cost and savings.
        
        Args:
            original_tokens: Original token count
            optimized_tokens: Optimized token count
            
        Returns:
            Tuple of (bobcoins_spent, bobcoins_saved)
        """
        with self._lock:
            tokens_saved = original_tokens - optimized_tokens
            spent, saved = self.metrics.record_cost(
                "optimization",
                optimized_tokens,
                tokens_saved
            )
            self.recent_costs.append(("optimization", spent, time.time()))
            self._check_alerts()
            return spent, saved

    def record_cache_hit(self, tokens_saved: int) -> float:
        """
        Record cache hit (pure savings, no cost).
        
        Args:
            tokens_saved: Number of tokens saved by cache hit
            
        Returns:
            Bobcoins saved
        """
        with self._lock:
            _, saved = self.metrics.record_cost("cache_hit", 0, tokens_saved)
            return saved

    def record_cache_miss(self, tokens_used: int) -> float:
        """
        Record cache miss (cost with no savings).
        
        Args:
            tokens_used: Number of tokens used
            
        Returns:
            Bobcoins spent
        """
        with self._lock:
            spent, _ = self.metrics.record_cost("cache_miss", tokens_used)
            self.recent_costs.append(("cache_miss", spent, time.time()))
            self._check_alerts()
            return spent

    def record_truncation(
        self,
        original_tokens: int,
        truncated_tokens: int
    ) -> Tuple[float, float]:
        """
        Record truncation operation cost and savings.
        
        Args:
            original_tokens: Original token count
            truncated_tokens: Truncated token count
            
        Returns:
            Tuple of (bobcoins_spent, bobcoins_saved)
        """
        with self._lock:
            tokens_saved = original_tokens - truncated_tokens
            spent, saved = self.metrics.record_cost(
                "truncation",
                truncated_tokens,
                tokens_saved
            )
            self.recent_costs.append(("truncation", spent, time.time()))
            self._check_alerts()
            return spent, saved

    def record_custom_operation(
        self,
        operation: str,
        tokens_used: int,
        tokens_saved: int = 0
    ) -> Tuple[float, float]:
        """
        Record custom operation cost.
        
        Args:
            operation: Operation name
            tokens_used: Number of tokens used
            tokens_saved: Number of tokens saved
            
        Returns:
            Tuple of (bobcoins_spent, bobcoins_saved)
        """
        with self._lock:
            spent, saved = self.metrics.record_cost(
                operation,
                tokens_used,
                tokens_saved
            )
            self.recent_costs.append((operation, spent, time.time()))
            self._check_alerts()
            return spent, saved

    def get_budget_status(self) -> Dict[str, Any]:
        """
        Get current budget status.
        
        Returns:
            Dictionary with budget information
        """
        with self._lock:
            spent = self.metrics.total_bobcoins_spent
            saved = self.metrics.total_bobcoins_saved
            net_spent = spent - saved
            remaining = self.budget_bobcoins - net_spent
            percent_used = (net_spent / self.budget_bobcoins * 100) if self.budget_bobcoins > 0 else 0

            return {
                "budget_bobcoins": self.budget_bobcoins,
                "spent_bobcoins": round(spent, 4),
                "saved_bobcoins": round(saved, 4),
                "net_spent_bobcoins": round(net_spent, 4),
                "remaining_bobcoins": round(remaining, 4),
                "percent_used": round(percent_used, 2),
                "is_over_budget": net_spent > self.budget_bobcoins
            }

    def get_cost_metrics(self) -> Dict[str, Any]:
        """
        Get detailed cost metrics.
        
        Returns:
            Dictionary with cost metrics
        """
        with self._lock:
            return self.metrics.to_dict()

    def get_cost_rate(self) -> Dict[str, float]:
        """
        Get cost rate (Bobcoins per second).
        
        Returns:
            Dictionary with rate information
        """
        with self._lock:
            elapsed = time.time() - self._start_time
            if elapsed == 0:
                return {
                    "bobcoins_per_second": 0.0,
                    "bobcoins_per_minute": 0.0,
                    "bobcoins_per_hour": 0.0
                }

            rate = self.metrics.total_bobcoins_spent / elapsed
            return {
                "bobcoins_per_second": round(rate, 6),
                "bobcoins_per_minute": round(rate * 60, 4),
                "bobcoins_per_hour": round(rate * 3600, 2)
            }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of active budget alerts.
        
        Returns:
            List of active alerts
        """
        with self._lock:
            return [
                {
                    "threshold_percent": alert.threshold_percent,
                    "triggered_at": alert.triggered_at.isoformat() + "Z" if alert.triggered_at else None
                }
                for alert in self.alerts
                if alert.triggered
            ]

    def _check_alerts(self) -> None:
        """Check and trigger budget alerts (internal)."""
        spent = self.metrics.total_bobcoins_spent
        for alert in self.alerts:
            if alert.check(spent, self.budget_bobcoins):
                # Alert triggered - could log or notify here
                pass

    def reset_alerts(self) -> None:
        """Reset all budget alerts."""
        with self._lock:
            for alert in self.alerts:
                alert.reset()

    def set_budget(self, budget_bobcoins: float) -> None:
        """
        Set new budget.
        
        Args:
            budget_bobcoins: New budget in Bobcoins
        """
        with self._lock:
            self.budget_bobcoins = budget_bobcoins
            self.reset_alerts()

    def reset(self) -> None:
        """Reset all cost tracking."""
        with self._lock:
            self.metrics = CostMetrics()
            self.recent_costs.clear()
            self.reset_alerts()
            self._start_time = time.time()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get cost tracking summary.
        
        Returns:
            Dictionary with summary information
        """
        budget_status = self.get_budget_status()
        cost_metrics = self.get_cost_metrics()
        cost_rate = self.get_cost_rate()
        active_alerts = self.get_active_alerts()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "budget": budget_status,
            "costs": cost_metrics,
            "rate": cost_rate,
            "alerts": active_alerts
        }


# Global cost tracker instance
_global_tracker: Optional[CostTracker] = None


def get_cost_tracker(
    budget_bobcoins: float = DEFAULT_BUDGET_BOBCOINS
) -> CostTracker:
    """
    Get global cost tracker instance.
    
    Args:
        budget_bobcoins: Budget in Bobcoins (only used on first call)
        
    Returns:
        CostTracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker(budget_bobcoins=budget_bobcoins)
    return _global_tracker


def reset_cost_tracker() -> None:
    """Reset global cost tracker."""
    global _global_tracker
    if _global_tracker is not None:
        _global_tracker.reset()


def tokens_to_bobcoins(tokens: int) -> float:
    """
    Convert tokens to Bobcoins.
    
    Args:
        tokens: Number of tokens
        
    Returns:
        Equivalent Bobcoins
    """
    return pricing.tokens_to_bobcoins(tokens)


def bobcoins_to_tokens(bobcoins: float) -> int:
    """
    Convert Bobcoins to tokens.
    
    Args:
        bobcoins: Number of Bobcoins
        
    Returns:
        Equivalent tokens
    """
    return pricing.bobcoins_to_tokens(bobcoins)
