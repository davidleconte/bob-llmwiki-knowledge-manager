"""``python -m src.validation`` -- run the manifest-backed validation harness.

Builds one :class:`~src.facade.TokenOptimizer` from config, measures the real
product over a real corpus, writes ``report.json`` + ``manifest.json``, prints a
human summary, and exits non-zero if the honest gates fail (null test,
manifest completeness, tiktoken active). It holds no measurement logic itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from src.monitoring import configure_logging

from . import (
    DEFAULT_CACHE_REPEAT_RATE,
    DEFAULT_TRUNCATION_BUDGET,
    NULL_MAX_SAVINGS_PCT,
    EmptyCorpusError,
    default_out_dir,
    human_summary,
    run_validation,
    validation_ok,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.validation",
        description="Real, manifest-backed validation of the token-optimization system.",
    )
    parser.add_argument(
        "--corpus",
        choices=("repo", "sessions", "both"),
        default="repo",
        help="corpus tier: committed repo prose (default), captured sessions, or both",
    )
    parser.add_argument("--environment", default="dev", help="config environment (default: dev)")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output dir (default: evaluation/results/validation-<date>)",
    )
    parser.add_argument("--seed", type=int, default=0, help="RNG seed (recorded in the manifest)")
    parser.add_argument(
        "--cache-repeat-rate",
        type=float,
        default=DEFAULT_CACHE_REPEAT_RATE,
        help="disclosed repeat rate for the cache workload (default: %(default)s)",
    )
    parser.add_argument(
        "--truncation-budget",
        type=int,
        default=DEFAULT_TRUNCATION_BUDGET,
        help="token budget for the truncation measurement (default: %(default)s)",
    )
    parser.add_argument(
        "--null-threshold",
        type=float,
        default=NULL_MAX_SAVINGS_PCT,
        help="max optimizer savings allowed on the null corpus (default: %(default)s%%)",
    )
    parser.add_argument(
        "--sessions-dir",
        type=Path,
        default=None,
        help="directory of captured session transcripts (for --corpus sessions/both)",
    )
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument("--no-write", action="store_true", help="measure but do not write files")
    parser.add_argument("--verbose", action="store_true", help="INFO-level logging (to stderr)")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging("INFO" if args.verbose else "WARNING")

    out_dir = args.out or default_out_dir()
    try:
        report = run_validation(
            environment=args.environment,
            corpus=args.corpus,
            sessions_dir=args.sessions_dir,
            out_dir=out_dir,
            seed=args.seed,
            repeat_rate=args.cache_repeat_rate,
            truncation_budget=args.truncation_budget,
            null_threshold=args.null_threshold,
            write=not args.no_write,
        )
    except EmptyCorpusError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(human_summary(report))
        if not args.no_write:
            print(f"\nwrote: {out_dir / 'report.json'}\n       {out_dir / 'manifest.json'}")

    ok, reasons = validation_ok(report)
    if not ok:
        print("\nVALIDATION GATE FAILED:", file=sys.stderr)
        for reason in reasons:
            print(f"  - {reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
