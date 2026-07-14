"""Tests for the measurement core (optimizer / cache / truncation / null)."""

from __future__ import annotations

from src.config.schema import CacheConfig, ConfigSchema, MonitoringConfig, OptimizerConfig
from src.validation.corpus import Document, make_null_corpus
from src.validation.measure import (
    measure_cache,
    measure_optimizer,
    measure_truncation,
    run_null_test,
)

PARA = (
    "The token optimization system reduces prompt size by normalizing "
    "whitespace and removing redundant repeated phrases while preserving the "
    "structure of the original document as much as is reasonably possible.\n\n\n"
    "It measures savings honestly by counting real tokens before and after the "
    "transformation rather than simulating a result that was never computed."
)


def _schema() -> ConfigSchema:
    return ConfigSchema(CacheConfig(), OptimizerConfig(), MonitoringConfig())


def _docs(n: int = 4) -> list[Document]:
    return [Document(f"doc{i}.md", PARA + f" variant {i}") for i in range(n)]


def test_measure_optimizer_reports_headline_fields():
    result = measure_optimizer(_schema(), "gpt-4", _docs())
    assert result["n"] == 4
    assert 0.0 <= result["mean_savings_pct"] <= 100.0
    assert len(result["ci95_savings_pct"]) == 2
    assert result["tiktoken_active"] is True
    assert len(result["per_document"]) == 4


def test_measure_optimizer_does_not_truncate_large_docs():
    # A long doc of DISTINCT words (no repeated phrases, single-spaced) has
    # nothing to compress, so it exposes truncation cleanly: with the config's
    # max_tokens cap (4096) disabled, optimized tokens must stay above it.
    # If the cap were active, lossy truncation would masquerade as compression.
    incompressible = " ".join(f"token{i}" for i in range(5000))
    big = Document("big.md", incompressible)
    result = measure_optimizer(_schema(), "gpt-4", [big])
    doc = result["per_document"][0]
    assert doc["original_tokens"] > 4096
    assert doc["optimized_tokens"] > 4096, "cap must be disabled -> no truncation"


def test_null_test_passes_on_shuffled_prose():
    docs = _docs(6)
    null = run_null_test(_schema(), "gpt-4", make_null_corpus(docs, seed=0))
    assert null["passed"] is True
    assert null["mean_savings_pct"] < null["threshold_pct"]


def test_measure_cache_hit_rate_tracks_repeat_fraction():
    result = measure_cache(_schema(), _docs(10), repeat_rate=0.5, seed=0)
    assert result["requested_repeat_rate"] == 0.5
    # Realised repeat fraction ~ requested; hit rate tracks it (allow slack for
    # the L2 fuzzy-match on similar synthetic docs).
    assert 0.4 <= result["actual_repeat_fraction"] <= 0.6
    assert result["hit_rate_pct"] >= 40.0


def test_measure_cache_empty_docs():
    result = measure_cache(_schema(), [], repeat_rate=0.3, seed=0)
    assert result["requests"] == 0
    assert result["hit_rate_pct"] == 0.0


def test_measure_truncation_is_labelled_lossy_and_excluded():
    result = measure_truncation("gpt-4", _docs(3), budget=32)
    assert result["lossy"] is True
    assert "NOT counted as savings" in result["note"]
    assert result["documents_truncated"] >= 1
