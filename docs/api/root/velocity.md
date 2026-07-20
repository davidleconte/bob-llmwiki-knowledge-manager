# velocity

A/B developer-velocity measurement harness — the measured before/after.

Every independent review of the submission named the *same* single gap: the only
reproducible figure is token compression — a proxy — and there is no *controlled*
developer-velocity number. This harness produces one with the same rigour as the
compression harness (:mod:`src.validation`): a paired,
counterbalanced, pre-registered A/B over a frozen task list, reported with the
median, the full distribution, N, and a bootstrap 95% CI — behind honesty guards
that make the number defensible instead of anecdotal.

Honesty guards enforced *here* (not left to the operator):
  * **Report everything** — every pre-registered task appears in the output,
    including ties and tasks where memory did not help; none can be dropped.
  * **Quality gate** — a *faster-but-worse* B result is not a win; a task whose B
    answer fails its done-criterion is flagged and excluded from the headline,
    but kept in the report.
  * **Refuse to over-claim** — no headline below the protocol's minimum of five
    valid paired tasks; the reason is stated instead.
  * **Manifest or it did not happen** — the report carries a reproducibility
    manifest (task-list hash, KB commit, seed, versions).

The harness does **not** fabricate timings: the wall-clock and Bobcoin readings
are recorded by a human running each task on Bob under both conditions (cold / no
KB vs. with KB). This module freezes the design, computes the statistics, and
emits the manifest — it is the measurement *instrument*, not the measurement.

Usage::

    python -m src.velocity --tasks evaluation/velocity/tasks.json \
        --measurements <your-recorded-runs>.json --out evaluation/results/velocity-ab-<date>/

## Constants

- `MIN_VALID_TASKS`
- `BOOTSTRAP_ITERS`
- `DEFAULT_SEED`

## Functions

### `task_list_hash(tasks: Sequence[Dict[str, object]]) -> str`

Stable sha256 over the pre-registered task list (the freeze artifact).


### `_bootstrap_ci(values: Sequence[float], seed: int, stat: Callable[[Sequence[float]], float], iters: int, alpha: float) -> List[float]`

Percentile bootstrap CI for ``stat`` — the same procedure as the 20% harness.


### `_pct_reduction(a: Optional[float], b: Optional[float]) -> Optional[float]`

Percentage reduction from A to B; ``None`` if A is missing or non-positive.


### `_pair(measurements: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]`

Group measurements by task id, then by condition (A / B).


### `_summary(deltas: List[float], seed: int) -> Dict[str, object]`

Median-centred summary with a bootstrap CI, or a refusal below the floor.


### `_allowed_claim(n_valid: int) -> str`


### `analyze(tasks: Sequence[Dict[str, Any]], measurements: Sequence[Dict[str, Any]]) -> Dict[str, object]`

Compute the paired A/B velocity report with honesty guards + manifest.


### `_load(path: Path) -> Dict[str, Any]`


### `main(argv: Optional[List[str]]) -> int`


## Classes

### `TaskResult`

The paired A/B outcome for a single pre-registered task (kept even if invalid).

