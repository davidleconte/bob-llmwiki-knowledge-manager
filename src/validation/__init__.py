"""Real, manifest-backed validation of the token-optimization system (Phase 5).

This package replaces the retracted, fabricated validator (which never invoked
the optimizer) with a harness that measures the *real* product through the
Phase-4 :class:`~src.facade.TokenOptimizer` facade, writes a reproducibility
manifest per run, keeps the three savings mechanisms separate and labelled, and
proves the measurement is not an artefact via a null test.

Entry points: :func:`run_validation` (programmatic) and ``python -m src.validation``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.facade import TokenOptimizer

from .corpus import (
    Document,
    hash_corpus,
    load_repo_prose,
    load_session_transcripts,
    make_null_corpus,
)
from .manifest import build_manifest, missing_fields, write_manifest
from .measure import (
    DEFAULT_CACHE_REPEAT_RATE,
    DEFAULT_TRUNCATION_BUDGET,
    NULL_MAX_SAVINGS_PCT,
    measure_cache,
    measure_optimizer,
    measure_truncation,
    run_null_test,
)
from .report import build_report, human_summary, write_report

__all__ = [
    "Document",
    "hash_corpus",
    "load_repo_prose",
    "load_session_transcripts",
    "make_null_corpus",
    "build_manifest",
    "missing_fields",
    "write_manifest",
    "measure_optimizer",
    "measure_cache",
    "measure_truncation",
    "run_null_test",
    "build_report",
    "human_summary",
    "write_report",
    "run_validation",
    "validation_ok",
    "default_out_dir",
    "DEFAULT_CACHE_REPEAT_RATE",
    "DEFAULT_TRUNCATION_BUDGET",
    "NULL_MAX_SAVINGS_PCT",
]


class EmptyCorpusError(RuntimeError):
    """Raised when the selected corpus contains no measurable documents."""


def repo_root() -> Path:
    """Repository root (two levels up from this file: ``src/validation/``)."""
    return Path(__file__).resolve().parents[2]


def default_out_dir(root: Optional[Path] = None) -> Path:
    """Dated output directory: ``evaluation/results/validation-<YYYY-MM-DD>``."""
    root = root or repo_root()
    return root / "evaluation" / "results" / f"validation-{date.today().isoformat()}"


def _select_corpus(corpus: str, root: Path, sessions_dir: Optional[Path]) -> List[Document]:
    sessions_dir = sessions_dir or (root / "evaluation" / "data" / "sessions")
    if corpus == "repo":
        return load_repo_prose(root)
    if corpus == "sessions":
        return load_session_transcripts(sessions_dir)
    if corpus == "both":
        return load_repo_prose(root) + load_session_transcripts(sessions_dir)
    raise ValueError(f"unknown corpus tier: {corpus!r} (expected repo|sessions|both)")


def run_validation(
    *,
    environment: str = "dev",
    corpus: str = "repo",
    sessions_dir: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    seed: int = 0,
    repeat_rate: float = DEFAULT_CACHE_REPEAT_RATE,
    truncation_budget: int = DEFAULT_TRUNCATION_BUDGET,
    null_threshold: float = NULL_MAX_SAVINGS_PCT,
    root: Optional[Path] = None,
    write: bool = True,
) -> Dict[str, Any]:
    """Run the full validation and return the report dict.

    Measures the real product through the facade, assembles a manifest, and (when
    ``write``) writes ``report.json`` + ``manifest.json`` under ``out_dir``.
    """
    root = root or repo_root()
    facade = TokenOptimizer.from_config(environment)

    docs = _select_corpus(corpus, root, sessions_dir)
    if not docs:
        raise EmptyCorpusError(
            f"corpus {corpus!r} is empty -- refusing to publish a number with no basis"
        )

    null_docs = make_null_corpus(docs, seed)

    optimizer = measure_optimizer(facade.config, facade.model, docs)
    cache = measure_cache(facade.config, docs, repeat_rate, seed)
    truncation = measure_truncation(facade.model, docs, truncation_budget)
    null_test = run_null_test(facade.config, facade.model, null_docs, null_threshold)

    manifest = build_manifest(
        config=facade.config,
        data_hash=hash_corpus(docs),
        seed=seed,
        model=facade.model,
        tiktoken_active=optimizer["tiktoken_active"],
        repo_root=root,
        extra={
            "corpus": corpus,
            "n_docs": len(docs),
            "environment": environment,
            "cache_repeat_rate": repeat_rate,
            "truncation_budget": truncation_budget,
        },
    )
    report = build_report(manifest, optimizer, cache, truncation, null_test)

    if write:
        write_report(out_dir or default_out_dir(root), report, manifest)
    return report


def validation_ok(report: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Gate a report: null passed, manifest complete, tiktoken active.

    Returns ``(ok, reasons)`` where ``reasons`` lists every failed check.
    Deliberately does **not** gate on savings magnitude -- gating a measurement
    re-incentivises fabrication; these three are the honest regression guards.
    """
    reasons: List[str] = []
    if not report["null_test"]["passed"]:
        reasons.append(
            f"null test FAILED: mean savings {report['null_test']['mean_savings_pct']:.2f}% "
            f">= threshold {report['null_test']['threshold_pct']:.1f}%"
        )
    missing = missing_fields(report["manifest"])
    if missing:
        reasons.append(f"manifest incomplete: missing/empty {missing}")
    if not report["manifest"].get("tiktoken_active"):
        reasons.append("tiktoken not active: token counts would be a chars/4 approximation")
    return (not reasons, reasons)
