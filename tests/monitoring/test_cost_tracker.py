"""
Behavioral tests for the Bobcoin cost-tracking module.

Every assertion here exercises real behaviour: cost aggregation, token->Bobcoin
conversion, budget guards, alert triggering, and reset semantics. Cost
expectations are derived from ``src.pricing`` (the single home for the
conversion rate) so the tests cannot silently drift from the production rate.

Time-dependent paths (cost rate) are made deterministic by patching the
module-level clock via ``monkeypatch`` -- no sleeps, no wall-clock assertions.
Alert/summary ISO timestamps are asserted structurally (type/shape), never by
value.

NOTE (production bug surfaced by this suite, now fixed): ``CostTracker.reset()``
and ``CostTracker.set_budget()`` previously self-deadlocked -- they hold
``self._lock`` and then call ``reset_alerts()``, which re-acquires it. The lock
is now an ``RLock`` (``cost_tracker.py:178``), mirroring the C-8b
``MetricsCollector`` fix; ``TestReentrantLockRegression`` guards against a
regression. Global-touching tests still null ``_global_tracker`` via
``monkeypatch`` purely for isolation (restored before the autouse teardown runs).
"""

import threading

import pytest

from src import pricing
from src.monitoring import cost_tracker as ct
from src.monitoring.cost_tracker import (
    CostMetrics,
    BudgetAlert,
    CostTracker,
    get_cost_tracker,
    reset_cost_tracker,
    tokens_to_bobcoins,
    bobcoins_to_tokens,
    TOKENS_PER_BOBCOIN,
    DEFAULT_BUDGET_BOBCOINS,
)


def bc(tokens: int) -> float:
    """Bobcoins for ``tokens``, derived from the pricing single-source-of-truth."""
    return pricing.tokens_to_bobcoins(tokens)


class TestModuleConstants:
    """The module re-exports pricing constants; they must match the one home."""

    def test_reexported_constants_match_pricing(self):
        assert TOKENS_PER_BOBCOIN == pricing.TOKENS_PER_BOBCOIN
        assert DEFAULT_BUDGET_BOBCOINS == pricing.DEFAULT_BUDGET_BOBCOINS

    def test_tokens_to_bobcoins_delegates_to_pricing(self):
        assert tokens_to_bobcoins(2500) == pricing.tokens_to_bobcoins(2500)
        assert tokens_to_bobcoins(2500) == 2.5

    def test_bobcoins_to_tokens_delegates_to_pricing(self):
        assert bobcoins_to_tokens(2.5) == pricing.bobcoins_to_tokens(2.5)
        assert bobcoins_to_tokens(2.5) == 2500


class TestCostMetrics:
    """CostMetrics: the pure accounting core."""

    def test_record_cost_returns_spent_and_saved(self):
        m = CostMetrics()
        spent, saved = m.record_cost("optimization", tokens_used=2000, tokens_saved=500)
        assert spent == bc(2000) == 2.0
        assert saved == bc(500) == 0.5

    def test_record_cost_accumulates_totals(self):
        m = CostMetrics()
        m.record_cost("token_counting", 1000)
        m.record_cost("token_counting", 3000)
        assert m.total_tokens_used == 4000
        assert m.total_bobcoins_spent == bc(4000) == 4.0
        assert m.operations_count == 2
        assert m.tokens_by_operation["token_counting"] == 4000
        assert m.cost_by_operation["token_counting"] == bc(4000)

    def test_record_cost_breaks_down_by_operation(self):
        m = CostMetrics()
        m.record_cost("token_counting", 1000)
        m.record_cost("cache_miss", 2000)
        assert m.cost_by_operation["token_counting"] == bc(1000)
        assert m.cost_by_operation["cache_miss"] == bc(2000)
        assert m.tokens_by_operation["cache_miss"] == 2000

    def test_savings_recorded_only_when_positive(self):
        m = CostMetrics()
        # tokens_saved == 0 -> no savings_by_source entry for this op
        m.record_cost("token_counting", 1000, tokens_saved=0)
        assert "token_counting" not in m.savings_by_source
        # tokens_saved > 0 -> recorded
        m.record_cost("optimization", 500, tokens_saved=1500)
        assert m.savings_by_source["optimization"] == bc(1500) == 1.5
        assert m.total_bobcoins_saved == bc(1500)
        assert m.total_tokens_saved == 1500

    def test_get_net_cost(self):
        m = CostMetrics()
        m.record_cost("optimization", 2000, tokens_saved=3000)  # spent 2.0, saved 3.0
        assert m.get_net_cost() == pytest.approx(2.0 - 3.0)

    def test_get_roi_percent(self):
        m = CostMetrics()
        m.record_cost("optimization", 2000, tokens_saved=1000)  # spent 2.0, saved 1.0
        # roi = saved/spent*100 = 50%
        assert m.get_roi_percent() == pytest.approx(50.0)

    def test_get_roi_percent_zero_spent(self):
        m = CostMetrics()
        m.record_cost("cache_hit", 0, tokens_saved=1000)  # spent 0
        assert m.get_roi_percent() == 0.0

    def test_get_average_cost_per_operation(self):
        m = CostMetrics()
        m.record_cost("a", 1000)
        m.record_cost("b", 3000)
        # total spent 4.0 over 2 ops
        assert m.get_average_cost_per_operation() == pytest.approx(2.0)

    def test_get_average_cost_per_operation_no_ops(self):
        assert CostMetrics().get_average_cost_per_operation() == 0.0

    def test_to_dict_structure_and_rounding(self):
        m = CostMetrics()
        m.record_cost("optimization", 3333, tokens_saved=1111)
        d = m.to_dict()
        assert d["total_tokens_used"] == 3333
        assert d["total_tokens_saved"] == 1111
        assert d["total_bobcoins_spent"] == round(bc(3333), 4)
        assert d["total_bobcoins_saved"] == round(bc(1111), 4)
        assert d["net_cost_bobcoins"] == round(bc(3333) - bc(1111), 4)
        assert d["operations_count"] == 1
        assert d["cost_by_operation"]["optimization"] == round(bc(3333), 4)
        assert d["tokens_by_operation"]["optimization"] == 3333
        assert d["savings_by_source"]["optimization"] == round(bc(1111), 4)


class TestBudgetAlert:
    """BudgetAlert: one-shot threshold guard."""

    def test_check_triggers_at_threshold(self):
        alert = BudgetAlert(threshold_percent=50.0)
        # 60 spent of 100 budget => 60% >= 50%
        assert alert.check(spent=60.0, budget=100.0) is True
        assert alert.triggered is True
        assert alert.triggered_at is not None

    def test_check_is_one_shot(self):
        alert = BudgetAlert(threshold_percent=50.0)
        assert alert.check(60.0, 100.0) is True
        # already triggered -> does not re-fire even if still over
        assert alert.check(70.0, 100.0) is False
        assert alert.triggered is True

    def test_check_below_threshold_does_not_trigger(self):
        alert = BudgetAlert(threshold_percent=90.0)
        assert alert.check(50.0, 100.0) is False
        assert alert.triggered is False
        assert alert.triggered_at is None

    def test_check_zero_or_negative_budget_returns_false(self):
        alert = BudgetAlert(threshold_percent=50.0)
        assert alert.check(10.0, 0.0) is False
        assert alert.check(10.0, -5.0) is False
        assert alert.triggered is False

    def test_reset_clears_state(self):
        alert = BudgetAlert(threshold_percent=50.0)
        alert.check(60.0, 100.0)
        assert alert.triggered is True
        alert.reset()
        assert alert.triggered is False
        assert alert.triggered_at is None


class TestCostTrackerInit:
    """Construction / default configuration."""

    def test_default_budget_and_alert_thresholds(self):
        tracker = CostTracker()
        assert tracker.budget_bobcoins == DEFAULT_BUDGET_BOBCOINS
        assert [a.threshold_percent for a in tracker.alerts] == [50.0, 75.0, 90.0]
        assert all(a.triggered is False for a in tracker.alerts)

    def test_custom_budget_and_thresholds(self):
        tracker = CostTracker(budget_bobcoins=42.0, alert_thresholds=[80.0])
        assert tracker.budget_bobcoins == 42.0
        assert [a.threshold_percent for a in tracker.alerts] == [80.0]


class TestCostTrackerRecording:
    """Per-operation recording APIs and their side effects."""

    def test_record_token_counting(self):
        tracker = CostTracker()
        spent = tracker.record_token_counting(1500)
        assert spent == bc(1500) == 1.5
        metrics = tracker.get_cost_metrics()
        assert metrics["total_tokens_used"] == 1500
        assert metrics["total_bobcoins_spent"] == round(bc(1500), 4)
        assert metrics["operations_count"] == 1
        # recorded in the recent-costs trend buffer
        assert len(tracker.recent_costs) == 1
        op, cost, _ts = tracker.recent_costs[0]
        assert op == "token_counting"
        assert cost == bc(1500)

    def test_record_optimization_returns_spent_and_saved(self):
        tracker = CostTracker()
        spent, saved = tracker.record_optimization(original_tokens=2000, optimized_tokens=500)
        # spent on optimized tokens, saved on the delta
        assert spent == bc(500) == 0.5
        assert saved == bc(1500) == 1.5
        metrics = tracker.get_cost_metrics()
        assert metrics["total_tokens_used"] == 500
        assert metrics["total_tokens_saved"] == 1500
        assert metrics["savings_by_source"]["optimization"] == round(bc(1500), 4)

    def test_record_cache_hit_is_pure_savings(self):
        tracker = CostTracker()
        saved = tracker.record_cache_hit(tokens_saved=1000)
        assert saved == bc(1000) == 1.0
        metrics = tracker.get_cost_metrics()
        assert metrics["total_bobcoins_saved"] == round(bc(1000), 4)
        assert metrics["total_bobcoins_spent"] == 0.0
        # cache hits are pure savings: not appended to the recent-costs trend buffer
        assert len(tracker.recent_costs) == 0

    def test_record_cache_miss(self):
        tracker = CostTracker()
        spent = tracker.record_cache_miss(tokens_used=2000)
        assert spent == bc(2000) == 2.0
        assert tracker.get_cost_metrics()["cost_by_operation"]["cache_miss"] == round(bc(2000), 4)
        assert len(tracker.recent_costs) == 1

    def test_record_truncation(self):
        tracker = CostTracker()
        spent, saved = tracker.record_truncation(original_tokens=1000, truncated_tokens=400)
        assert spent == bc(400)
        assert saved == bc(600)
        metrics = tracker.get_cost_metrics()
        assert metrics["tokens_by_operation"]["truncation"] == 400
        assert metrics["savings_by_source"]["truncation"] == round(bc(600), 4)

    def test_record_custom_operation(self):
        tracker = CostTracker()
        spent, saved = tracker.record_custom_operation("embedding", tokens_used=800, tokens_saved=200)
        assert spent == bc(800)
        assert saved == bc(200)
        metrics = tracker.get_cost_metrics()
        assert metrics["cost_by_operation"]["embedding"] == round(bc(800), 4)
        assert metrics["savings_by_source"]["embedding"] == round(bc(200), 4)


class TestBudgetStatus:
    """Budget accounting and the over-budget guard."""

    def test_budget_status_within_budget(self):
        tracker = CostTracker(budget_bobcoins=100.0)
        tracker.record_token_counting(30000)  # 30 BC
        tracker.record_cache_hit(5000)         # save 5 BC
        status = tracker.get_budget_status()
        assert status["budget_bobcoins"] == 100.0
        assert status["spent_bobcoins"] == round(bc(30000), 4) == 30.0
        assert status["saved_bobcoins"] == round(bc(5000), 4) == 5.0
        assert status["net_spent_bobcoins"] == round(30.0 - 5.0, 4) == 25.0
        assert status["remaining_bobcoins"] == round(100.0 - 25.0, 4) == 75.0
        assert status["percent_used"] == pytest.approx(25.0)
        assert status["is_over_budget"] is False

    def test_budget_status_over_budget_guard(self):
        tracker = CostTracker(budget_bobcoins=10.0)
        tracker.record_token_counting(12000)  # 12 BC net > 10 budget
        status = tracker.get_budget_status()
        assert status["net_spent_bobcoins"] == round(bc(12000), 4) == 12.0
        assert status["remaining_bobcoins"] == round(10.0 - 12.0, 4) == -2.0
        assert status["is_over_budget"] is True
        assert status["percent_used"] == pytest.approx(120.0)

    def test_budget_status_zero_budget(self):
        tracker = CostTracker(budget_bobcoins=0.0)
        tracker.record_token_counting(1000)
        status = tracker.get_budget_status()
        # guard against division by zero -> percent_used pinned at 0
        assert status["percent_used"] == 0
        assert status["is_over_budget"] is True


class TestCostRate:
    """Cost rate is time-dependent; the clock is frozen for determinism."""

    def _freeze_clock(self, monkeypatch, holder):
        monkeypatch.setattr(ct.time, "time", lambda: holder["t"])

    def test_cost_rate_with_elapsed_time(self, monkeypatch):
        holder = {"t": 1000.0}
        self._freeze_clock(monkeypatch, holder)
        tracker = CostTracker()          # _start_time captured at t=1000
        tracker.record_token_counting(2000)  # 2.0 BC spent (still t=1000)
        holder["t"] = 1010.0             # 10 seconds later
        rate = tracker.get_cost_rate()
        # 2.0 BC / 10 s
        assert rate["bobcoins_per_second"] == round(2.0 / 10.0, 6) == 0.2
        assert rate["bobcoins_per_minute"] == round(0.2 * 60, 4) == 12.0
        assert rate["bobcoins_per_hour"] == round(0.2 * 3600, 2) == 720.0

    def test_cost_rate_zero_elapsed(self, monkeypatch):
        holder = {"t": 500.0}
        self._freeze_clock(monkeypatch, holder)
        tracker = CostTracker()
        tracker.record_token_counting(1000)  # clock never advances -> elapsed == 0
        rate = tracker.get_cost_rate()
        assert rate == {
            "bobcoins_per_second": 0.0,
            "bobcoins_per_minute": 0.0,
            "bobcoins_per_hour": 0.0,
        }


class TestAlerts:
    """Alert triggering, listing, and reset."""

    def test_alerts_trigger_on_spend(self):
        tracker = CostTracker(budget_bobcoins=10.0, alert_thresholds=[50.0, 75.0])
        tracker.record_token_counting(6000)  # 6 BC of 10 -> 60% : trips 50 only
        active = tracker.get_active_alerts()
        thresholds = {a["threshold_percent"] for a in active}
        assert thresholds == {50.0}
        # triggered_at surfaced as an ISO-ish string, not asserted by value
        assert isinstance(active[0]["triggered_at"], str)
        assert active[0]["triggered_at"]

    def test_alerts_escalate_with_more_spend(self):
        tracker = CostTracker(budget_bobcoins=10.0, alert_thresholds=[50.0, 75.0, 90.0])
        tracker.record_token_counting(6000)   # 60%
        tracker.record_token_counting(3500)   # cumulative 95%
        thresholds = {a["threshold_percent"] for a in tracker.get_active_alerts()}
        assert thresholds == {50.0, 75.0, 90.0}

    def test_no_active_alerts_when_under_threshold(self):
        tracker = CostTracker(budget_bobcoins=100.0)
        tracker.record_token_counting(1000)  # 1%
        assert tracker.get_active_alerts() == []

    def test_reset_alerts(self):
        tracker = CostTracker(budget_bobcoins=10.0, alert_thresholds=[50.0])
        tracker.record_token_counting(6000)
        assert tracker.get_active_alerts()
        tracker.reset_alerts()
        assert tracker.get_active_alerts() == []
        assert all(a.triggered is False for a in tracker.alerts)


class TestReentrantLockRegression:
    """Regression guards for the reset()/set_budget() self-deadlock (now fixed).

    ``CostTracker.reset()`` and ``CostTracker.set_budget()`` hold ``self._lock``
    and then call ``reset_alerts()``, which re-acquires it. With a plain
    non-reentrant ``Lock`` this self-deadlocked -- a live P0 bug of the identical
    class already fixed for ``MetricsCollector`` (C-8b). ``self._lock`` is now an
    ``RLock`` (``cost_tracker.py:178``), so these re-entrant paths complete.

    Each call runs in a daemon thread with a bounded join and is asserted to
    COMPLETE: if someone reverts to a non-reentrant lock the join times out and
    these fail. The bound is not a timing race -- on the fixed path the call
    returns in microseconds, and a true deadlock never completes.
    """

    @staticmethod
    def _completes_within(fn, timeout=5.0):
        done = threading.Event()

        def _run():
            try:
                fn()
            finally:
                done.set()

        threading.Thread(target=_run, daemon=True).start()
        return done.wait(timeout=timeout)

    def test_reset_completes_and_clears_costs(self):
        tracker = CostTracker(budget_bobcoins=10.0)
        tracker.record_token_counting(1000)
        assert self._completes_within(tracker.reset) is True, (
            "CostTracker.reset() did not complete -- the reset_alerts() "
            "self-deadlock has regressed (self._lock must be an RLock)."
        )
        # reset() actually cleared the accumulated cost.
        assert tracker.get_summary()["costs"]["operations_count"] == 0

    def test_set_budget_completes_and_updates(self):
        tracker = CostTracker(budget_bobcoins=10.0)
        assert self._completes_within(lambda: tracker.set_budget(50.0)) is True, (
            "CostTracker.set_budget() did not complete -- the reset_alerts() "
            "self-deadlock has regressed (self._lock must be an RLock)."
        )
        assert tracker.budget_bobcoins == 50.0

    def test_reset_cost_tracker_completes(self, monkeypatch):
        # Isolate + auto-restore the global so this doesn't leak into other tests.
        monkeypatch.setattr(ct, "_global_tracker", None)
        tracker = get_cost_tracker()
        tracker.record_token_counting(1000)
        assert self._completes_within(reset_cost_tracker) is True, (
            "reset_cost_tracker() did not complete -- CostTracker.reset() "
            "self-deadlock has regressed."
        )


class TestSummary:
    """get_summary aggregates the sub-reports."""

    def test_summary_shape(self):
        tracker = CostTracker(budget_bobcoins=100.0)
        tracker.record_token_counting(2000)
        summary = tracker.get_summary()
        assert set(summary.keys()) == {"timestamp", "budget", "costs", "rate", "alerts"}
        assert summary["budget"]["spent_bobcoins"] == round(bc(2000), 4)
        assert summary["costs"]["operations_count"] == 1
        assert isinstance(summary["alerts"], list)
        # timestamp normalised to a Z-suffixed ISO string (structural check only)
        assert isinstance(summary["timestamp"], str)
        assert summary["timestamp"].endswith("Z")


class TestGlobalSingleton:
    """Module-level singleton helpers.

    Each test that creates the global tracker nulls ``_global_tracker`` via
    ``monkeypatch`` first, so it is auto-restored to ``None`` at teardown --
    BEFORE the autouse conftest teardown runs ``reset_cost_tracker()``. Without
    this, a populated global would make that teardown call ``reset()`` and hang
    (see ``TestKnownDeadlockBugs``). ``reset_cost_tracker`` itself is exercised
    only on the ``None`` (no-op) branch here; its ``reset()`` branch deadlocks
    and is guarded in ``TestKnownDeadlockBugs``.
    """

    def test_get_cost_tracker_returns_singleton(self, monkeypatch):
        monkeypatch.setattr(ct, "_global_tracker", None)
        t1 = get_cost_tracker()
        t2 = get_cost_tracker()
        assert isinstance(t1, CostTracker)
        assert t1 is t2

    def test_get_cost_tracker_applies_budget_on_first_call_only(self, monkeypatch):
        monkeypatch.setattr(ct, "_global_tracker", None)
        first = get_cost_tracker(budget_bobcoins=7.0)
        assert first.budget_bobcoins == 7.0
        # A later call with a different budget returns the SAME instance and
        # does not re-apply the budget (singleton semantics).
        again = get_cost_tracker(budget_bobcoins=999.0)
        assert again is first
        assert again.budget_bobcoins == 7.0

    def test_reset_cost_tracker_noop_when_uninitialised(self, monkeypatch):
        # Force the "no tracker yet" branch: reset must be a safe no-op.
        monkeypatch.setattr(ct, "_global_tracker", None)
        reset_cost_tracker()  # must not raise
        assert ct._global_tracker is None
