"""Single source of truth for model pricing and Bobcoin conversion.

The per-model USD price table (used by :mod:`src.optimizer.token_counter` for cost
estimates) and the Bobcoin conversion (used by :mod:`src.monitoring.cost_tracker`
for internal cost accounting) both live here, so the two cannot drift apart. To
change a price or add a model, edit exactly one place: this module.

Units:
- USD list price is per 1,000 tokens, split into ``input_per_1k`` / ``output_per_1k``
  (B2/CODE-10). Each :class:`ModelPrice` carries an ``as_of_date`` and ``source_url``
  so an out-of-date entry is auditable — treat every entry as a *dated list price*.
- A Bobcoin is the product's internal cost unit: 1 Bobcoin == ``TOKENS_PER_BOBCOIN``
  tokens, model-independent. Its USD anchor IS model-dependent (a model's
  ``input_per_1k``); do not assume a single USD/Bobcoin rate across models.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# The default model used across the optimizer, token counter, and truncator.
DEFAULT_MODEL: str = "gpt-4"


@dataclass(frozen=True)
class ModelPrice:
    """A model's list price per 1,000 tokens, split by input/output, with provenance.

    ``as_of_date`` (ISO date) and ``source_url`` make a stale or wrong price
    auditable — these are *list prices*, clearly dated; verify before quoting.
    """

    input_per_1k: float
    output_per_1k: float
    currency: str
    as_of_date: str
    source_url: str


# USD list prices per 1,000 tokens, split by input/output, per model.
# ONE home for rates -- never duplicate a rate literal elsewhere (check_value_homes).
# Dated list prices; confirm against source_url before publishing a cost figure.
PRICES: Dict[str, ModelPrice] = {
    # OpenAI (https://openai.com/api/pricing/)
    "gpt-4": ModelPrice(
        input_per_1k=0.03,
        output_per_1k=0.06,
        currency="USD",
        as_of_date="2024-06-01",
        source_url="https://openai.com/api/pricing/",
    ),
    "gpt-4-32k": ModelPrice(
        input_per_1k=0.06,
        output_per_1k=0.12,
        currency="USD",
        as_of_date="2024-06-01",
        source_url="https://openai.com/api/pricing/",
    ),
    "gpt-3.5-turbo": ModelPrice(
        input_per_1k=0.0005,
        output_per_1k=0.0015,
        currency="USD",
        as_of_date="2024-06-01",
        source_url="https://openai.com/api/pricing/",
    ),
    "gpt-3.5-turbo-16k": ModelPrice(
        input_per_1k=0.003,
        output_per_1k=0.004,
        currency="USD",
        as_of_date="2023-11-01",
        source_url="https://openai.com/api/pricing/",
    ),
    # Anthropic Claude (https://www.anthropic.com/pricing)
    "claude-3-5-sonnet": ModelPrice(
        input_per_1k=0.003,
        output_per_1k=0.015,
        currency="USD",
        as_of_date="2024-06-20",
        source_url="https://www.anthropic.com/pricing",
    ),
    "claude-3-opus": ModelPrice(
        input_per_1k=0.015,
        output_per_1k=0.075,
        currency="USD",
        as_of_date="2024-03-01",
        source_url="https://www.anthropic.com/pricing",
    ),
    "claude-3-haiku": ModelPrice(
        input_per_1k=0.00025,
        output_per_1k=0.00125,
        currency="USD",
        as_of_date="2024-03-01",
        source_url="https://www.anthropic.com/pricing",
    ),
    # IBM watsonx Granite (https://www.ibm.com/products/watsonx-ai) — list-price
    # estimate; watsonx bills per resource-unit, verify against the source before quoting.
    "granite-3-8b-instruct": ModelPrice(
        input_per_1k=0.0002,
        output_per_1k=0.0002,
        currency="USD",
        as_of_date="2024-10-01",
        source_url="https://www.ibm.com/products/watsonx-ai",
    ),
    "granite-3-2b-instruct": ModelPrice(
        input_per_1k=0.0001,
        output_per_1k=0.0001,
        currency="USD",
        as_of_date="2024-10-01",
        source_url="https://www.ibm.com/products/watsonx-ai",
    ),
}

# Bobcoin conversion (internal cost unit): 1 Bobcoin == 1,000 tokens, model-independent.
TOKENS_PER_BOBCOIN: int = 1000
DEFAULT_BUDGET_BOBCOINS: float = 100.0


class UnknownModelPriceError(KeyError):
    """Raised when pricing is requested for a model absent from :data:`PRICES`.

    Deliberately loud (B2/CODE-10): an unpriced model must NOT silently fall back to
    a default (e.g. gpt-4) rate — that is how a watsonx cost figure silently becomes
    an OpenAI cost figure. Add the model to ``PRICES`` (with a dated source) instead.
    """


def price_for(model: str) -> Optional[ModelPrice]:
    """Return the :class:`ModelPrice` for *model*, or ``None`` if it is unpriced."""
    return PRICES.get(model)


def usd_cost(input_tokens: int, output_tokens: int = 0, model: str = DEFAULT_MODEL) -> float:
    """USD cost of *input_tokens* / *output_tokens* under *model*'s split list price.

    Raises :class:`UnknownModelPriceError` for a model absent from :data:`PRICES` —
    never a silent fallback to a default rate (B2/CODE-10). Pass ``output_tokens=0``
    (the default) to price input tokens only.
    """
    price = PRICES.get(model)
    if price is None:
        raise UnknownModelPriceError(
            f"no price for model {model!r}; add it to PRICES in src/pricing.py — "
            "unknown-model pricing must not fall back to a default rate"
        )
    return (input_tokens / 1000.0) * price.input_per_1k + (
        output_tokens / 1000.0
    ) * price.output_per_1k


def tokens_to_bobcoins(tokens: int) -> float:
    """Convert a token count to Bobcoins (1 Bobcoin == ``TOKENS_PER_BOBCOIN`` tokens)."""
    return tokens / TOKENS_PER_BOBCOIN


def bobcoins_to_tokens(bobcoins: float) -> int:
    """Convert Bobcoins to an equivalent token count."""
    return int(bobcoins * TOKENS_PER_BOBCOIN)
