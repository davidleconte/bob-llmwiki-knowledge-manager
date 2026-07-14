"""Regression tests for the single-source pricing module (audit bug C-2).

Before the fix, pricing lived in two divergent homes: a per-model USD table in
``token_counter.estimate_cost`` and a flat Bobcoin rate in ``cost_tracker``.
These tests pin the invariant that both now resolve through ``src.pricing``.
"""

import pytest

from src import pricing
from src.monitoring import cost_tracker
from src.optimizer.token_counter import TokenCounter


def test_default_model_has_one_home():
    """The default model string is defined once, in pricing."""
    assert TokenCounter().model == pricing.DEFAULT_MODEL


def test_estimate_cost_delegates_to_pricing():
    """USD cost estimates come from the pricing module, not a local table."""
    tc = TokenCounter(model="gpt-4")
    assert tc.estimate_cost(1000) == pricing.usd_cost(1000, "gpt-4")
    assert tc.estimate_cost(1000, "gpt-3.5-turbo") == pricing.usd_cost(1000, "gpt-3.5-turbo")
    # Preserve historical values so downstream cost claims don't shift.
    assert tc.estimate_cost(1000) == pytest.approx(0.03, rel=0.01)
    assert tc.estimate_cost(1000, "gpt-3.5-turbo") == pytest.approx(0.002, rel=0.01)
    # Unknown model falls back to the default rate in exactly one place.
    assert tc.estimate_cost(1000, "no-such-model") == pricing.DEFAULT_USD_PER_1K


def test_bobcoin_conversion_has_one_home():
    """Bobcoin constants/conversions resolve to the same objects as pricing."""
    assert cost_tracker.TOKENS_PER_BOBCOIN is pricing.TOKENS_PER_BOBCOIN
    assert cost_tracker.DEFAULT_BUDGET_BOBCOINS == pricing.DEFAULT_BUDGET_BOBCOINS
    assert cost_tracker.tokens_to_bobcoins(2500) == pricing.tokens_to_bobcoins(2500)
    assert cost_tracker.bobcoins_to_tokens(2.5) == pricing.bobcoins_to_tokens(2.5)
