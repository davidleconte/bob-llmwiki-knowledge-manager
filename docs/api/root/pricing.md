# pricing

Single source of truth for model pricing and Bobcoin conversion.

Both the USD per-model rate table (used by :mod:`src.optimizer.token_counter`
for cost estimates) and the Bobcoin conversion (used by
:mod:`src.monitoring.cost_tracker` for internal cost accounting) live here, so
the two cannot drift apart. To change a price or add a model, edit exactly one
place: this module.

Units:
- USD list price is per 1,000 tokens, per model.
- A Bobcoin is the product's internal cost unit: 1 Bobcoin == ``TOKENS_PER_BOBCOIN``
  tokens, model-independent.

## Functions

### `usd_cost(tokens: int, model: str) -> float`

Estimate the USD cost of ``tokens`` tokens under ``model``'s list price.

Unknown models fall back to :data:`DEFAULT_USD_PER_1K`.


### `tokens_to_bobcoins(tokens: int) -> float`

Convert a token count to Bobcoins (1 Bobcoin == ``TOKENS_PER_BOBCOIN`` tokens).


### `bobcoins_to_tokens(bobcoins: float) -> int`

Convert Bobcoins to an equivalent token count.

