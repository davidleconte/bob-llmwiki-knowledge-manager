"""Measurement core -- invokes the real product and reports honest numbers.

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
"""

from __future__ import annotations

import random
import statistics
import time
from typing import TYPE_CHECKING, Any, Dict, List, Sequence

from src.factory import build_cache, build_truncator
from src.optimizer.prompt_optimizer import PromptOptimizer

if TYPE_CHECKING:
    from src.config.schema import ConfigSchema

    from .corpus import Document

# The null-test ceiling: optimizer "savings" on shuffled/high-entropy text must
# be below this, or the measurement is broken (a hard gate, not advisory).
NULL_MAX_SAVINGS_PCT: float = 5.0

# Bootstrap resamples for the mean-savings confidence interval. Honest about
# width on the small real corpus rather than pretending precision.
BOOTSTRAP_ITERS: int = 2000

DEFAULT_TRUNCATION_BUDGET: int = 256
DEFAULT_CACHE_REPEAT_RATE: float = 0.3


def _bootstrap_ci(
    values: Sequence[float], seed: int, iters: int = BOOTSTRAP_ITERS, alpha: float = 0.05
) -> List[float]:
    """Percentile bootstrap CI for the mean; degenerate-safe for tiny N."""
    clean = list(values)
    if len(clean) < 2:
        point = clean[0] if clean else 0.0
        return [point, point]
    rng = random.Random(seed)
    n = len(clean)
    means: List[float] = []
    for _ in range(iters):
        resample = [clean[rng.randrange(n)] for _ in range(n)]
        means.append(sum(resample) / n)
    means.sort()
    lo = means[int((alpha / 2) * iters)]
    hi = means[min(int((1 - alpha / 2) * iters), iters - 1)]
    return [round(lo, 4), round(hi, 4)]


def _percentile(values: Sequence[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(int(pct / 100 * len(ordered)), len(ordered) - 1)
    return ordered[idx]


def _trimmed_mean(values: List[float], trim: float = 0.1) -> float:
    """Mean after dropping the top/bottom ``trim`` fraction -- robust to outliers."""
    if not values:
        return 0.0
    ordered = sorted(values)
    k = int(len(ordered) * trim)
    core = ordered[k : len(ordered) - k] or ordered
    return statistics.mean(core)


def _corpus_composition(scored: List[Dict[str, Any]], total_original: int) -> Dict[str, Any]:
    """Composition metrics that expose corpus cherry-picking (ATK-GATE-01).

    Guard *composition, not magnitude*: we deliberately do NOT gate the savings
    *value* -- gating a measurement re-incentivises fabrication. Instead these
    metrics let :func:`composition_ok` gate whether the corpus is representative
    enough to publish a number. Cherry-pick signatures: too few docs, a single doc
    dominating the token weight, or a mean pulled far from the median by outliers.
    """
    savings = [float(d["savings_percentage"]) for d in scored]
    tokens = [int(d["original_tokens"]) for d in scored]
    total = total_original or 1
    mean_s = statistics.mean(savings) if savings else 0.0
    median_s = statistics.median(savings) if savings else 0.0
    return {
        "n_docs": len(scored),
        "top_doc_token_share": round(max(tokens) / total, 4) if tokens else 0.0,
        "mean_savings_pct": round(mean_s, 4),
        "median_savings_pct": round(median_s, 4),
        "mean_median_divergence_pp": round(abs(mean_s - median_s), 4),
        "trimmed_mean_savings_pct": round(_trimmed_mean(savings), 4),
    }


def measure_optimizer(
    config: "ConfigSchema", model: str, docs: Sequence["Document"]
) -> Dict[str, Any]:
    """Per-document lossless-ish compression -- the only savings headline.

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
    """
    optimizer = PromptOptimizer(
        model=model,
        max_tokens=None,
        target_reduction=config.optimizer.target_reduction,
        min_quality_score=config.optimizer.min_quality_score,
        use_cache=False,
        track_costs=False,
    )

    per_document: List[Dict[str, Any]] = []
    latencies_ms: List[float] = []
    for doc in docs:
        start = time.perf_counter()
        result = optimizer.optimize(doc.text)
        latencies_ms.append((time.perf_counter() - start) * 1000)
        per_document.append(
            {
                "source": doc.source,
                "original_tokens": result["original_tokens"],
                "optimized_tokens": result["optimized_tokens"],
                "savings_percentage": result["savings_percentage"],
                "quality_score": result["quality_score"],
            }
        )

    scored = [d for d in per_document if d["original_tokens"] > 0]
    savings = [float(d["savings_percentage"]) for d in scored]
    quality = [float(d["quality_score"]) for d in scored]
    total_original = sum(int(d["original_tokens"]) for d in per_document)
    total_optimized = sum(int(d["optimized_tokens"]) for d in per_document)

    return {
        "n": len(savings),
        "mean_savings_pct": round(statistics.mean(savings), 4) if savings else 0.0,
        "median_savings_pct": round(statistics.median(savings), 4) if savings else 0.0,
        "std_savings_pct": round(statistics.stdev(savings), 4) if len(savings) > 1 else 0.0,
        "ci95_savings_pct": _bootstrap_ci(savings, seed=0),
        "mean_quality_score": round(statistics.mean(quality), 4) if quality else 0.0,
        "quality_note": "lexical heuristic (_estimate_quality), not semantic fidelity",
        "total_original_tokens": total_original,
        "total_optimized_tokens": total_optimized,
        "aggregate_savings_pct": (
            round((1 - total_optimized / total_original) * 100, 4) if total_original else 0.0
        ),
        "mean_latency_ms": round(statistics.mean(latencies_ms), 4) if latencies_ms else 0.0,
        "p95_latency_ms": round(_percentile(latencies_ms, 95), 4),
        "tiktoken_active": optimizer.token_counter.use_tiktoken,
        "corpus_composition": _corpus_composition(scored, total_original),
        "per_document": per_document,
    }


def measure_cache(
    config: "ConfigSchema",
    docs: Sequence["Document"],
    repeat_rate: float = DEFAULT_CACHE_REPEAT_RATE,
    seed: int = 0,
) -> Dict[str, Any]:
    """Recompute-avoidance under a workload with a *disclosed* repeat rate.

    A cache hit avoids 100% of recompute, so the aggregate number is a property
    of how repetitive the request stream is -- not of the system. We replay a
    synthetic stream where each request repeats an already-seen document with
    probability ``repeat_rate``, and report the realised hit rate alongside that
    rate so the two can never be confused.
    """
    cache = build_cache(config.cache)
    rng = random.Random(seed)
    unique = list(docs)
    if not unique:
        return {
            "requested_repeat_rate": repeat_rate,
            "actual_repeat_fraction": 0.0,
            "requests": 0,
            "hits": 0,
            "hit_rate_pct": 0.0,
            "note": "workload-dependent; NOT a system property; excluded from the savings headline",
        }

    # Emit each unique doc once (warms the cache -- every first touch misses),
    # then inject repeat requests so the *realised* repeat fraction matches the
    # requested rate: R / (N + R) = repeat_rate. Reporting the realised fraction
    # alongside the hit rate keeps the disclosed workload honest (hit rate then
    # tracks the repeat fraction -- which is exactly the point: cache "savings"
    # is a property of workload repetition, not of the system).
    n = len(unique)
    repeats = round(n * repeat_rate / (1 - repeat_rate)) if repeat_rate < 1 else n * 10
    stream: List["Document"] = list(unique)
    for _ in range(repeats):
        stream.append(unique[rng.randrange(n)])
    rng.shuffle(stream)

    hits = 0
    for doc in stream:
        if cache.get(doc.text) is not None:
            hits += 1
        else:
            cache.set(doc.text, doc.source)

    requests = len(stream)
    return {
        "requested_repeat_rate": repeat_rate,
        "actual_repeat_fraction": round(repeats / requests, 4) if requests else 0.0,
        "requests": requests,
        "hits": hits,
        "hit_rate_pct": round(hits / requests * 100, 4) if requests else 0.0,
        "note": "workload-dependent; NOT a system property; excluded from the savings headline",
    }


def measure_truncation(
    model: str,
    docs: Sequence["Document"],
    budget: int = DEFAULT_TRUNCATION_BUDGET,
) -> Dict[str, Any]:
    """Lossy budget-fit reduction -- reported, but EXCLUDED from savings.

    Truncation deletes content to fit ``budget`` and there is no fidelity gate,
    so removed tokens are not "saved" in any lossless sense. Reported here for
    completeness with an explicit lossy label.
    """
    truncator = build_truncator(model=model)
    per_document: List[Dict[str, Any]] = []
    for doc in docs:
        result = truncator.truncate(doc.text, budget)
        per_document.append(
            {
                "source": doc.source,
                "original_tokens": result["original_tokens"],
                "truncated_tokens": result["truncated_tokens"],
                "tokens_removed": result["tokens_removed"],
                "removal_percentage": result.get("removal_percentage", 0.0),
                "was_truncated": result["was_truncated"],
            }
        )

    truncated = [d for d in per_document if d["was_truncated"]]
    removals = [float(d["removal_percentage"]) for d in truncated]
    return {
        "budget_tokens": budget,
        "documents": len(per_document),
        "documents_truncated": len(truncated),
        "mean_removal_pct_when_truncated": (
            round(statistics.mean(removals), 4) if removals else 0.0
        ),
        "lossy": True,
        "note": "lossy deletion, no fidelity guarantee; NOT counted as savings",
        "per_document": per_document,
    }


def run_null_test(
    config: "ConfigSchema",
    model: str,
    null_docs: Sequence["Document"],
    threshold: float = NULL_MAX_SAVINGS_PCT,
) -> Dict[str, Any]:
    """Optimizer over the shuffled null corpus -- real savings must be < threshold."""
    result = measure_optimizer(config, model, null_docs)
    mean_savings = float(result["mean_savings_pct"])
    return {
        "n": result["n"],
        "mean_savings_pct": mean_savings,
        "aggregate_savings_pct": result["aggregate_savings_pct"],
        "threshold_pct": threshold,
        "passed": mean_savings < threshold,
        "rationale": (
            "shuffled/high-entropy input has no compressible redundancy; "
            "material 'savings' here would mean the measurement is an artefact"
        ),
    }
