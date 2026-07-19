# pricing

Single source of truth for model pricing and Bobcoin conversion.

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

## Functions

### `price_for(model: str) -> Optional[ModelPrice]`

Return the :class:`ModelPrice` for *model*, or ``None`` if it is unpriced.


### `usd_cost(input_tokens: int, output_tokens: int, model: str) -> float`

USD cost of *input_tokens* / *output_tokens* under *model*'s split list price.

Raises :class:`UnknownModelPriceError` for a model absent from :data:`PRICES` —
never a silent fallback to a default rate (B2/CODE-10). Pass ``output_tokens=0``
(the default) to price input tokens only.


### `tokens_to_bobcoins(tokens: int) -> float`

Convert a token count to Bobcoins (1 Bobcoin == ``TOKENS_PER_BOBCOIN`` tokens).


### `bobcoins_to_tokens(bobcoins: float) -> int`

Convert Bobcoins to an equivalent token count.


## Classes

### `ModelPrice`

A model's list price per 1,000 tokens, split by input/output, with provenance.

``as_of_date`` (ISO date) and ``source_url`` make a stale or wrong price
auditable — these are *list prices*, clearly dated; verify before quoting.


### `UnknownModelPriceError(KeyError)`

Raised when pricing is requested for a model absent from :data:`PRICES`.

Deliberately loud (B2/CODE-10): an unpriced model must NOT silently fall back to
a default (e.g. gpt-4) rate — that is how a watsonx cost figure silently becomes
an OpenAI cost figure. Add the model to ``PRICES`` (with a dated source) instead.

