"""Wave-3 residual NEW-1 — the optimizer cache must key on the token budget.

The re-audit found ``optimize()``'s cache keyed on the prompt alone, so a later
call with a stricter ``max_tokens`` received the earlier *uncapped* cached result
(and vice versa) — a caller fitting a context window could silently get an
over-budget result. Fix: fold the effective budget (and strategy signature) into
the cache key. RED on current main, GREEN after.
"""

from __future__ import annotations

from src.optimizer.prompt_optimizer import PromptOptimizer

_LONG = "alpha beta gamma delta epsilon zeta eta theta " * 400


def test_new1_stricter_max_tokens_not_served_uncapped():
    """A stricter per-call max_tokens must not return an earlier uncapped result."""
    opt = PromptOptimizer(use_cache=True)
    opt.optimize(_LONG)  # no cap -> caches the uncapped result
    capped = opt.optimize(_LONG, max_tokens=5)  # same prompt, strict cap

    tokens = opt.token_counter.count_tokens(capped["optimized"])
    assert tokens <= 5, (
        f"stricter max_tokens=5 returned a {tokens}-token result — the uncapped "
        "cached entry was served instead of recomputing under the cap"
    )


def test_new1_uncapped_not_served_capped():
    """An uncapped call must not receive an earlier capped cached result."""
    opt = PromptOptimizer(use_cache=True)
    prompt = _LONG + " sentinel"
    opt.optimize(prompt, max_tokens=5)  # caps -> caches the 5-token result
    full = opt.optimize(prompt)  # no cap

    tokens = opt.token_counter.count_tokens(full["optimized"])
    assert tokens > 5, (
        "an uncapped call received an earlier capped cached result "
        f"({tokens} tokens) — the budget is missing from the cache key"
    )


def test_new1_same_budget_still_caches():
    """The fix must not disable caching: identical (prompt, budget) hits the cache."""
    opt = PromptOptimizer(use_cache=True)
    r1 = opt.optimize(_LONG, max_tokens=50)
    r2 = opt.optimize(_LONG, max_tokens=50)
    assert r2.get("from_cache") or r2["optimized"] == r1["optimized"], (
        "a repeat call with the same prompt and budget should hit the cache"
    )
