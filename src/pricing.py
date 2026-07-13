"""Single source of truth for model pricing and Bobcoin conversion.

Both the USD per-model rate table (used by :mod:`src.optimizer.token_counter`
for cost estimates) and the Bobcoin conversion (used by
:mod:`src.monitoring.cost_tracker` for internal cost accounting) live here, so
the two cannot drift apart. To change a price or add a model, edit exactly one
place: this module.

Units:
- USD list price is per 1,000 tokens, per model.
- A Bobcoin is the product's internal cost unit: 1 Bobcoin == ``TOKENS_PER_BOBCOIN``
  tokens, model-independent.
"""

from typing import Dict

# The default model used across the optimizer, token counter, and truncator.
DEFAULT_MODEL: str = "gpt-4"

# USD list price per 1,000 tokens, by model (list prices as of 2024).
# One home for rates -- do not duplicate this table elsewhere.
USD_PER_1K_TOKENS: Dict[str, float] = {
    "gpt-4": 0.03,
    "gpt-4-32k": 0.06,
    "gpt-3.5-turbo": 0.002,
    "gpt-3.5-turbo-16k": 0.004,
}

# Rate applied when a model is not in the table (falls back to the default model).
DEFAULT_USD_PER_1K: float = USD_PER_1K_TOKENS[DEFAULT_MODEL]

# Bobcoin conversion (internal cost unit): 1 Bobcoin == 1,000 tokens.
TOKENS_PER_BOBCOIN: int = 1000
DEFAULT_BUDGET_BOBCOINS: float = 100.0


def usd_cost(tokens: int, model: str = DEFAULT_MODEL) -> float:
    """Estimate the USD cost of ``tokens`` tokens under ``model``'s list price.

    Unknown models fall back to :data:`DEFAULT_USD_PER_1K`.
    """
    rate = USD_PER_1K_TOKENS.get(model, DEFAULT_USD_PER_1K)
    return (tokens / 1000) * rate


def tokens_to_bobcoins(tokens: int) -> float:
    """Convert a token count to Bobcoins (1 Bobcoin == ``TOKENS_PER_BOBCOIN`` tokens)."""
    return tokens / TOKENS_PER_BOBCOIN


def bobcoins_to_tokens(bobcoins: float) -> int:
    """Convert Bobcoins to an equivalent token count."""
    return int(bobcoins * TOKENS_PER_BOBCOIN)
