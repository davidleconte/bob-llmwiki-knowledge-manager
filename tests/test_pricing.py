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
    assert tc.estimate_cost(1000) == pricing.usd_cost(1000, model="gpt-4")
    assert tc.estimate_cost(1000, "gpt-3.5-turbo") == pricing.usd_cost(1000, model="gpt-3.5-turbo")
    # gpt-4 input rate is pinned (worked cost example / value-homes gate).
    assert tc.estimate_cost(1000) == pytest.approx(0.03, rel=0.01)
    # gpt-3.5-turbo now uses the real dated input list price (0.0005), not the
    # old flat 0.002 (B2 fidelity).
    assert tc.estimate_cost(1000, "gpt-3.5-turbo") == pytest.approx(0.0005, rel=0.01)
    # Unknown model is LOUD, not a silent default-rate fallback (B2): usd_cost
    # raises and estimate_cost returns None.
    assert tc.estimate_cost(1000, "no-such-model") is None
    with pytest.raises(pricing.UnknownModelPriceError):
        pricing.usd_cost(1000, model="no-such-model")


def test_bobcoin_conversion_has_one_home():
    """Bobcoin constants/conversions resolve to the same objects as pricing."""
    assert cost_tracker.TOKENS_PER_BOBCOIN is pricing.TOKENS_PER_BOBCOIN
    assert cost_tracker.DEFAULT_BUDGET_BOBCOINS == pricing.DEFAULT_BUDGET_BOBCOINS
    assert cost_tracker.tokens_to_bobcoins(2500) == pricing.tokens_to_bobcoins(2500)
    assert cost_tracker.bobcoins_to_tokens(2.5) == pricing.bobcoins_to_tokens(2.5)


# --------------------------------------------------------------------------- #
# B2/CODE-10: split-aware, dated, loud-on-unknown per-model price table
# --------------------------------------------------------------------------- #


def test_unknown_model_price_is_loud():
    """RED->GREEN: an unpriced model raises, not a silent gpt-4-rate fallback.

    Pre-fix, usd_cost(tokens, "granite-x") returned the DEFAULT (gpt-4) rate — a
    watsonx cost silently priced as OpenAI. It now raises UnknownModelPriceError.
    """
    with pytest.raises(pricing.UnknownModelPriceError):
        pricing.usd_cost(1000, model="granite-x")
    # The error must not be the same as a real (gpt-4) cost.
    assert pricing.usd_cost(1000, model="gpt-4") == pytest.approx(0.03)


def test_input_output_split():
    """Input and output tokens are priced independently."""
    # gpt-4: input 0.03, output 0.06 per 1k -> output costs 2x input.
    input_only = pricing.usd_cost(1000, 0, "gpt-4")
    output_only = pricing.usd_cost(0, 1000, "gpt-4")
    assert input_only == pytest.approx(0.03)
    assert output_only == pytest.approx(0.06)
    assert output_only != input_only
    # Split call sums both legs.
    assert pricing.usd_cost(1000, 1000, "gpt-4") == pytest.approx(0.09)


def test_price_table_has_dates_and_sources():
    """Every ModelPrice carries an ISO as_of_date and an http source_url.

    Guards against a silently-stale or unsourced price entering the table.
    """
    assert pricing.PRICES, "price table must not be empty"
    for model, price in pricing.PRICES.items():
        assert isinstance(price, pricing.ModelPrice), model
        # ISO-ish date YYYY-MM-DD
        assert len(price.as_of_date) == 10 and price.as_of_date[4] == "-", (
            f"{model}: as_of_date {price.as_of_date!r} is not an ISO date"
        )
        assert price.source_url.startswith("http"), (
            f"{model}: source_url {price.source_url!r} is not a URL"
        )
        assert price.currency, f"{model}: missing currency"
        assert price.input_per_1k >= 0 and price.output_per_1k >= 0, model


def test_covers_gpt_claude_and_granite_families():
    """The table spans the three target families (OpenAI, Claude, watsonx Granite)."""
    models = pricing.PRICES
    assert any(m.startswith("gpt") for m in models)
    assert any(m.startswith("claude") for m in models)
    assert any(m.startswith("granite") for m in models)


def test_pricing_single_home_gate_passes():
    """check_value_homes.py must still pass (no price literal drifts from pricing.py)."""
    import subprocess
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/check_value_homes.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"check_value_homes.py failed after the pricing change:\n{result.stdout}\n{result.stderr}"
    )
