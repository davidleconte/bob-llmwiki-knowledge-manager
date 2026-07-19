# measure

Measurement core -- invokes the real product and reports honest numbers.

Three mechanisms save tokens in different ways and are measured **separately**;
blending them into one headline is exactly how the retracted 68.96% was
manufactured:

* :func:`measure_optimizer` -- lossless-ish prompt compression. Cache is turned
  **off** so this measures compression, not recompute-avoidance. This is the
  only "savings" headline.
* :func:`measure_cache` -- recompute-avoidance, which is a property of the
  *workload* (its repeat rate), not the system. Reported separately, with the
  repeat rate disclosed.
* :func:`measure_truncation` -- lossy budget-fit. Content is destroyed and there
  is no fidelity gate, so it is reported as reduction-under-budget and **excluded
  from savings**.

:func:`run_null_test` runs the optimizer over the shuffled null corpus; real
savings there must collapse below :data:`NULL_MAX_SAVINGS_PCT` or the
measurement is an artefact.

## Functions

### `_bootstrap_ci(values: Sequence[float], seed: int, iters: int, alpha: float) -> List[float]`

Percentile bootstrap CI for the mean; degenerate-safe for tiny N.


### `_percentile(values: Sequence[float], pct: float) -> float`


### `_trimmed_mean(values: List[float], trim: float) -> float`

Mean after dropping the top/bottom ``trim`` fraction -- robust to outliers.


### `_corpus_composition(scored: List[Dict[str, Any]], total_original: int) -> Dict[str, Any]`

Composition metrics that expose corpus cherry-picking (ATK-GATE-01).

Guard *composition, not magnitude*: we deliberately do NOT gate the savings
*value* -- gating a measurement re-incentivises fabrication. Instead these
metrics let :func:`composition_ok` gate whether the corpus is representative
enough to publish a number. Cherry-pick signatures: too few docs, a single doc
dominating the token weight, or a mean pulled far from the median by outliers.


### `measure_optimizer(config: 'ConfigSchema', model: str, docs: Sequence['Document']) -> Dict[str, Any]`

Per-document lossless-ish compression -- the only savings headline.

Two levers are deliberately set for an honest compression number:

* ``use_cache=False`` -- a repeated document must not register as a
  100%-savings cache hit and corrupt the compression measurement (cache
  recompute-avoidance is measured separately).
* ``max_tokens=None`` -- the config's hard token cap (default 4096) makes
  ``optimize()`` *truncate* long documents, and that lossy deletion would be
  counted here as "compression". Truncation is lossy budget-fit measured
  separately (:func:`measure_truncation`); disabling the cap keeps this
  headline to genuine, near-lossless compression. The optimizer's real
  tunables (``target_reduction``/``min_quality_score``) are still honoured.


### `measure_cache(config: 'ConfigSchema', docs: Sequence['Document'], repeat_rate: float, seed: int) -> Dict[str, Any]`

Recompute-avoidance under a workload with a *disclosed* repeat rate.

A cache hit avoids 100% of recompute, so the aggregate number is a property
of how repetitive the request stream is -- not of the system. We replay a
synthetic stream where each request repeats an already-seen document with
probability ``repeat_rate``, and report the realised hit rate alongside that
rate so the two can never be confused.


### `measure_truncation(model: str, docs: Sequence['Document'], budget: int) -> Dict[str, Any]`

Lossy budget-fit reduction -- reported, but EXCLUDED from savings.

Truncation deletes content to fit ``budget`` and there is no fidelity gate,
so removed tokens are not "saved" in any lossless sense. Reported here for
completeness with an explicit lossy label.


### `run_null_test(config: 'ConfigSchema', model: str, null_docs: Sequence['Document'], threshold: float) -> Dict[str, Any]`

Optimizer over the shuffled null corpus -- real savings must be < threshold.

