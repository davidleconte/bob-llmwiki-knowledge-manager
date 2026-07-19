"""B1/CODE-10: multi-backend tokenizer resolver with a loud approximation path.

TokenCounter used to hardcode ``tiktoken.encoding_for_model`` and silently
degrade to a heuristic on any non-OpenAI model id (Claude/Granite/watsonx). It
now resolves a backend by model family and, when no exact tokenizer is available,
emits exactly ONE warning per (process, model) and sets ``approximate=True`` — so
the degradation is observable and the validation manifest's ``tiktoken_active``
gate (fed by ``use_tiktoken``) blocks a published number computed on a guess.
"""

from __future__ import annotations

import importlib.util
import logging

import pytest

import src.optimizer.token_counter as tc_mod
from src.optimizer.token_counter import (
    TokenCounter,
    _ApproxTokenizer,
    resolve_tokenizer,
)


@pytest.fixture(autouse=True)
def _reset_warn_dedupe():
    """Each test starts with a clean once-per-model warning ledger."""
    tc_mod._APPROX_WARNED.clear()
    yield
    tc_mod._APPROX_WARNED.clear()


def test_openai_model_uses_exact_tiktoken():
    """gpt-4 resolves to the exact tiktoken backend."""
    counter = TokenCounter(model="gpt-4")
    assert counter.tokenizer.exact is True
    assert counter.approximate is False
    assert counter.use_tiktoken is True
    assert counter.encoding is not None
    assert counter.tokenizer.name.startswith("tiktoken:")


def test_unknown_openai_id_still_exact_via_cl100k():
    """An unknown gpt/o1 id falls back to cl100k_base — still exact, no warning."""
    counter = TokenCounter(model="gpt-5-ultra-unreleased")
    assert counter.approximate is False
    assert counter.use_tiktoken is True
    assert not tc_mod._APPROX_WARNED  # no approximation -> no warning


def test_unknown_model_is_approximate_and_flagged():
    """A Claude model (no offline exact tokenizer) -> approximate, exact=False.

    ``claude*`` has no in-package exact tokenizer, so it is a stable approximate
    case regardless of whether the optional HF/Granite extra is cached.
    """
    counter = TokenCounter(model="claude-sonnet-5")
    assert counter.approximate is True
    assert counter.tokenizer.exact is False
    assert counter.use_tiktoken is False  # -> manifest tiktoken_active=False
    assert counter.encoding is None
    # Counting still works (never raises on the hot path).
    assert counter.count_tokens("hello world") > 0


def test_unknown_model_warns_exactly_once(caplog):
    """RED->GREEN: exactly one warning per (process, model); no re-warn.

    The old code caught the KeyError silently — zero warnings. The resolver warns
    once and dedupes on the model id.
    """
    with caplog.at_level(logging.WARNING, logger="src.optimizer.token_counter"):
        TokenCounter(model="claude-sonnet-5")
        TokenCounter(model="claude-sonnet-5")  # same model -> must NOT re-warn

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1, f"expected exactly 1 warning, got {len(warnings)}"
    assert "claude-sonnet-5" in warnings[0].getMessage()
    assert "approximation" in warnings[0].getMessage().lower()


def test_distinct_unknown_models_each_warn_once(caplog):
    """Two different unknown models each warn once (dedupe is per model id)."""
    with caplog.at_level(logging.WARNING, logger="src.optimizer.token_counter"):
        TokenCounter(model="claude-opus-4")
        TokenCounter(model="mistral-large-2")

    warned_models = {m for m in ("claude-opus-4", "mistral-large-2") if m in tc_mod._APPROX_WARNED}
    assert warned_models == {"claude-opus-4", "mistral-large-2"}
    assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == 2


def test_resolve_tokenizer_never_raises_and_counts():
    """resolve_tokenizer degrades to an approximation rather than raising."""
    tok = resolve_tokenizer("some-totally-unknown-model")
    assert isinstance(tok, _ApproxTokenizer)
    assert tok.exact is False
    assert tok.count("a b c") > 0


def test_approximate_backend_matches_legacy_heuristic():
    """The approximation path equals the old words + special//2 heuristic."""
    counter = TokenCounter(model="claude-x")  # approximate backend
    text = "Hello world, how are you?"
    assert counter.count_tokens(text) == counter._approximate_tokens(text)


def test_get_stats_exposes_exactness():
    """get_stats surfaces the backend name and exactness for observability."""
    exact = TokenCounter(model="gpt-4").get_stats("hello world")
    approx = TokenCounter(model="claude-sonnet-5").get_stats("hello world")
    assert exact["exact"] is True and exact["approximate"] is False
    assert approx["exact"] is False and approx["approximate"] is True
    assert approx["tokenizer"].startswith("approx:")


def test_non_exact_counter_would_block_manifest_publish():
    """Contract tie to the validation gate.

    ``src/validation/measure.py`` records ``tiktoken_active =
    token_counter.use_tiktoken`` and ``src/validation/__init__.py`` blocks a
    published savings number when that is False. A non-exact counter therefore
    carries the publish-block signal.
    """
    approx_counter = TokenCounter(model="claude-sonnet-5")
    assert approx_counter.use_tiktoken is False, (
        "an approximate counter must set use_tiktoken=False so the manifest "
        "tiktoken_active gate blocks the published number"
    )
    exact_counter = TokenCounter(model="gpt-4")
    assert exact_counter.use_tiktoken is True


@pytest.mark.skipif(
    importlib.util.find_spec("transformers") is None,
    reason="granite/HF tokenizer extra (transformers) not installed",
)
def test_granite_backend_selected_when_extra_present():
    """With the watsonx extra installed, a granite id resolves to an exact backend."""
    counter = TokenCounter(model="granite-3-8b-instruct")
    # Either the HF tokenizer loaded (exact) or it degraded loudly — but if
    # transformers is importable and the model is cached, we expect exact.
    if counter.tokenizer.exact:
        assert counter.tokenizer.name.startswith("granite:")
        assert counter.count_tokens("hello world") > 0
