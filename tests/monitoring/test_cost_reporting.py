"""
Behavioral tests for the cost-reporting layer.

The reporting helpers all read a cost tracker via ``get_cost_tracker``. Each
test seeds a tracker with precise, pricing-derived amounts and asserts on the
rendered/structured output: dashboard sections and rows, report shape, health
thresholds, projections, top-N ordering, and export behaviour.

Isolation note: the reporting layer normally reads the process-global
``CostTracker`` singleton, but that tracker's ``reset()``/``set_budget()``
currently self-deadlock (a real production bug -- see
``tests/monitoring/test_cost_tracker.py::TestKnownDeadlockBugs``). Once the
global tracker exists, the autouse ``_reset_monitoring_singletons`` teardown
would call ``reset_cost_tracker()`` -> ``reset()`` and hang. To stay green
without fighting that fixture, each test injects a fresh, LOCAL ``CostTracker``
by routing ``cost_reporting.get_cost_tracker`` to it; the global stays ``None``
so the conftest reset is a harmless no-op, and each test picks an explicit
budget at construction time instead of via the deadlocking ``set_budget``.

Timestamp/rate values are wall-clock dependent and are asserted structurally
only (presence of labels), never by value.
"""

import json

import pytest

from src import pricing
from src.monitoring import cost_reporting
from src.monitoring.cost_reporting import (
    calculate_projected_costs,
    check_budget_health,
    export_cost_data,
    generate_cost_dashboard,
    generate_cost_report,
    generate_cost_summary,
    get_cost_alerts,
    get_savings_summary,
    get_top_cost_operations,
    print_cost_dashboard,
    print_cost_summary,
)
from src.monitoring.cost_tracker import CostTracker


def bc(tokens: int) -> float:
    """Bobcoins for ``tokens``, from the pricing single source of truth."""
    return pricing.tokens_to_bobcoins(tokens)


@pytest.fixture
def make_tracker(monkeypatch):
    """Factory: build a fresh, isolated CostTracker with an explicit budget and
    route the reporting layer's ``get_cost_tracker()`` to it.

    Injecting a local instance (rather than populating the process-global
    singleton) is deliberate -- see the module docstring: it keeps the global
    ``None`` so the autouse conftest teardown does not hit the reset() deadlock,
    and it lets each test set a budget without the deadlocking ``set_budget``.
    """

    def _make(budget: float = 100.0) -> CostTracker:
        tracker = CostTracker(budget_bobcoins=budget)
        monkeypatch.setattr(cost_reporting, "get_cost_tracker", lambda *a, **k: tracker)
        return tracker

    return _make


@pytest.fixture
def tracker(make_tracker):
    """Convenience: a fresh injected tracker with the default 100 BC budget."""
    return make_tracker()


class TestGenerateCostSummary:
    def test_summary_matches_tracker_summary(self, tracker):
        tracker.record_token_counting(2000)
        summary = generate_cost_summary()
        assert set(summary.keys()) == {"timestamp", "budget", "costs", "rate", "alerts"}
        assert summary["budget"]["spent_bobcoins"] == round(bc(2000), 4)
        assert summary["costs"]["operations_count"] == 1


class TestGenerateCostDashboard:
    def test_dashboard_renders_all_core_sections(self, tracker):
        tracker.record_token_counting(20000)  # 20 BC spent
        tracker.record_optimization(4000, 1000)  # spends 1 BC, saves 3 BC
        dashboard = generate_cost_dashboard()

        assert "BOBCOIN COST TRACKING DASHBOARD" in dashboard
        assert "BUDGET STATUS" in dashboard
        assert "COST METRICS" in dashboard
        assert "COST BY OPERATION" in dashboard
        # optimization produced savings -> savings section renders
        assert "SAVINGS BY SOURCE" in dashboard
        assert "COST RATE" in dashboard
        # operation rows are present
        assert "token_counting" in dashboard
        assert "optimization" in dashboard
        # budget figures rendered
        assert "Budget:" in dashboard
        assert "Generated:" in dashboard

    def test_dashboard_over_budget_warning(self, make_tracker):
        tracker = make_tracker(budget=1.0)
        tracker.record_token_counting(5000)  # 5 BC net > 1 BC budget
        dashboard = generate_cost_dashboard()
        assert "OVER BUDGET" in dashboard

    def test_dashboard_empty_tracker_skips_optional_sections(self, tracker):
        # No operations, no savings, no alerts, within budget.
        dashboard = generate_cost_dashboard()
        assert "BUDGET STATUS" in dashboard
        assert "COST BY OPERATION" in dashboard
        # optional sections are omitted when there is nothing to show
        assert "SAVINGS BY SOURCE" not in dashboard
        assert "ACTIVE ALERTS" not in dashboard
        assert "OVER BUDGET" not in dashboard

    def test_dashboard_renders_active_alerts_section(self, make_tracker):
        tracker = make_tracker(budget=10.0)
        tracker.record_token_counting(6000)  # 60% -> trips 50% alert
        dashboard = generate_cost_dashboard()
        assert "ACTIVE ALERTS" in dashboard
        assert "threshold exceeded" in dashboard


class TestGenerateCostReport:
    def test_report_default_includes_breakdown_excludes_trends(self, tracker):
        tracker.record_optimization(4000, 1000)  # spent 1 BC, saved 3 BC
        report = generate_cost_report()
        assert set(report.keys()) == {"timestamp", "summary", "breakdown"}
        s = report["summary"]
        assert s["total_spent"] == round(bc(1000), 4)
        assert s["total_saved"] == round(bc(3000), 4)
        assert s["net_cost"] == round(bc(1000) - bc(3000), 4)
        assert s["operations_count"] == 1
        b = report["breakdown"]
        assert b["by_operation"]["optimization"] == round(bc(1000), 4)
        assert b["by_tokens"]["optimization"] == 1000
        assert b["savings_by_source"]["optimization"] == round(bc(3000), 4)

    def test_report_can_exclude_breakdown(self, tracker):
        tracker.record_token_counting(1000)
        report = generate_cost_report(include_breakdown=False)
        assert "breakdown" not in report
        assert "summary" in report

    def test_report_can_include_trends_placeholder(self, tracker):
        tracker.record_token_counting(1000)
        report = generate_cost_report(include_trends=True)
        assert "trends" in report
        assert report["trends"]["note"] == "Trend analysis not yet implemented"


class TestExportCostData:
    def test_export_json_writes_valid_summary(self, tracker, tmp_path):
        tracker.record_token_counting(3000)
        out = tmp_path / "cost.json"
        export_cost_data(str(out), format="json")
        assert out.exists()
        data = json.loads(out.read_text())
        assert set(data.keys()) == {"timestamp", "budget", "costs", "rate", "alerts"}
        assert data["costs"]["total_tokens_used"] == 3000
        assert data["budget"]["spent_bobcoins"] == round(bc(3000), 4)

    def test_export_csv_not_implemented(self, tracker, tmp_path):
        with pytest.raises(NotImplementedError):
            export_cost_data(str(tmp_path / "cost.csv"), format="csv")

    def test_export_unknown_format_raises_value_error(self, tracker, tmp_path):
        with pytest.raises(ValueError):
            export_cost_data(str(tmp_path / "cost.xml"), format="xml")


class TestGetCostAlerts:
    def test_returns_active_alerts(self, make_tracker):
        tracker = make_tracker(budget=10.0)
        tracker.record_token_counting(8000)  # 80% -> trips 50 and 75
        alerts = get_cost_alerts()
        thresholds = {a["threshold_percent"] for a in alerts}
        assert thresholds == {50.0, 75.0}

    def test_empty_when_no_alerts(self, tracker):
        tracker.record_token_counting(100)  # negligible
        assert get_cost_alerts() == []


class TestCheckBudgetHealth:
    """All four health bands are threshold-driven and deterministic."""

    def test_healthy_below_50(self, tracker):
        tracker.record_token_counting(10000)  # 10% of 100
        health = check_budget_health()
        assert health["status"] == "healthy"
        assert health["percent_used"] == pytest.approx(10.0)
        assert health["is_over_budget"] is False

    def test_caution_at_or_above_50(self, tracker):
        tracker.record_token_counting(60000)  # 60%
        health = check_budget_health()
        assert health["status"] == "caution"
        assert "50%" in health["message"]

    def test_warning_at_or_above_75(self, tracker):
        tracker.record_token_counting(80000)  # 80%
        health = check_budget_health()
        assert health["status"] == "warning"

    def test_critical_at_or_above_90(self, tracker):
        tracker.record_token_counting(95000)  # 95%
        health = check_budget_health()
        assert health["status"] == "critical"
        assert health["remaining_bobcoins"] == round(100.0 - 95.0, 4) == 5.0


class TestCalculateProjectedCosts:
    def test_projection_within_budget(self, tracker):
        # Two 1000-token ops -> avg 1.0 BC/op. Spent 2 BC of 100 -> remaining 98.
        tracker.record_token_counting(1000)
        tracker.record_token_counting(1000)
        proj = calculate_projected_costs(operations_per_hour=10, hours=2)
        assert proj["total_operations"] == 20
        assert proj["avg_cost_per_operation"] == 1.0
        assert proj["projected_cost_bobcoins"] == round(1.0 * 20, 4) == 20.0
        assert proj["current_remaining_bobcoins"] == round(100.0 - 2.0, 4) == 98.0
        assert proj["will_exceed_budget"] is False
        assert proj["budget_shortfall"] == 0

    def test_projection_exceeds_budget(self, tracker):
        tracker.record_token_counting(1000)
        tracker.record_token_counting(1000)  # avg 1.0 BC/op, remaining 98
        proj = calculate_projected_costs(operations_per_hour=1000, hours=24)
        assert proj["total_operations"] == 24000
        assert proj["projected_cost_bobcoins"] == round(1.0 * 24000, 4)
        assert proj["will_exceed_budget"] is True
        assert proj["budget_shortfall"] == pytest.approx(24000 - 98.0)

    def test_projection_default_hours(self, tracker):
        tracker.record_token_counting(1000)
        proj = calculate_projected_costs(operations_per_hour=5)
        assert proj["hours"] == 24
        assert proj["total_operations"] == 120


class TestGetTopCostOperations:
    def test_returns_operations_sorted_by_cost_desc(self, tracker):
        tracker.record_token_counting(5000)  # 5.0 BC
        tracker.record_cache_miss(3000)  # 3.0 BC
        tracker.record_custom_operation("embedding", 1000)  # 1.0 BC
        top = get_top_cost_operations()
        costs = [op["cost_bobcoins"] for op in top]
        assert costs == sorted(costs, reverse=True)
        assert top[0]["operation"] == "token_counting"
        assert top[0]["cost_bobcoins"] == round(bc(5000), 4) == 5.0
        assert top[0]["tokens"] == 5000

    def test_respects_limit(self, tracker):
        tracker.record_token_counting(5000)
        tracker.record_cache_miss(3000)
        tracker.record_custom_operation("embedding", 1000)
        top = get_top_cost_operations(limit=2)
        assert len(top) == 2
        assert [op["operation"] for op in top] == ["token_counting", "cache_miss"]

    def test_empty_when_no_operations(self, tracker):
        assert get_top_cost_operations() == []


class TestGetSavingsSummary:
    def test_savings_summary(self, tracker):
        tracker.record_optimization(4000, 1000)  # saves 3000 tokens
        tracker.record_cache_hit(2000)  # saves 2000 tokens
        summary = get_savings_summary()
        assert summary["total_tokens_saved"] == 5000
        assert summary["total_bobcoins_saved"] == round(bc(5000), 4) == 5.0
        assert summary["savings_by_source"]["optimization"] == round(bc(3000), 4)
        assert summary["savings_by_source"]["cache_hit"] == round(bc(2000), 4)

    def test_savings_summary_empty(self, tracker):
        summary = get_savings_summary()
        assert summary["total_tokens_saved"] == 0
        assert summary["total_bobcoins_saved"] == 0.0
        assert summary["savings_by_source"] == {}


class TestPrintHelpers:
    def test_print_cost_dashboard(self, tracker, capsys):
        tracker.record_token_counting(2000)
        print_cost_dashboard()
        out = capsys.readouterr().out
        assert "BOBCOIN COST TRACKING DASHBOARD" in out

    def test_print_cost_summary_emits_valid_json(self, tracker, capsys):
        tracker.record_token_counting(2000)
        print_cost_summary()
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed["costs"]["total_tokens_used"] == 2000
