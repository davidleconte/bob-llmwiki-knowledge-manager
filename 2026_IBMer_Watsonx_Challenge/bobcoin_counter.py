#!/usr/bin/env python3
"""Live Bobcoin counter for the compound-loop demo — real token counts.

Shows the tokens Bob would spend **re-deriving** an answer from source vs.
**retrieving** the compact KB summary that already captured it: the
re-derivation mechanism, made visible. Counts come from the real tokenizer (the
same one the 20% compression harness uses), not an estimate — so the number on
screen is one a judge could reproduce with ``bob-optimize count``.

It animates a meter counting down from the re-derivation cost to the retrieval
cost. The figure is per-document (it depends on which source and summary you
pick); it illustrates the *mechanism*, and is deliberately NOT presented as the
headline savings metric or a velocity number.

Usage::

    python 2026_IBMer_Watsonx_Challenge/bobcoin_counter.py \\
        --source src/cache/multi_level_cache.py src/cache/semantic_cache.py \\
        --summary docs/knowledge-base/references/<compact-summary>.md
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence


def _read(paths: Sequence[str]) -> List[str]:
    texts: List[str] = []
    for path in paths:
        texts.append(Path(path).read_text(encoding="utf-8", errors="replace"))
    return texts


def _count_tokens(texts: Sequence[str]) -> int:
    """Real token count via the shipped tokenizer (BPE with documented fallback)."""
    from src import TokenOptimizer
    from src.monitoring import configure_logging

    configure_logging(log_level="WARNING")  # keep the demo output clean (as the CLI does)
    optimizer = TokenOptimizer.from_config("dev")
    return sum(int(optimizer.count(text)) for text in texts)


def _bar(value: int, ceiling: int, width: int = 40) -> str:
    filled = 0 if ceiling <= 0 else int(width * value / ceiling)
    return "█" * filled + "░" * (width - filled)


def _animate(rederive: int, retrieve: int, *, steps: int = 40, delay: float = 0.03) -> None:
    for i in range(steps + 1):
        current = int(rederive - (rederive - retrieve) * i / steps)
        sys.stdout.write(
            f"\r  Bobcoins to answer:  {current:>7,}  {_bar(current, rederive)} "
        )
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bobcoin_counter",
        description="Live re-derivation-vs-retrieval Bobcoin counter (real token counts).",
    )
    parser.add_argument(
        "--source", nargs="+", required=True, help="Source file(s) Bob would re-read to re-derive"
    )
    parser.add_argument(
        "--summary", required=True, help="The compact KB summary that replaces re-reading the source"
    )
    parser.add_argument("--no-animate", action="store_true", help="Print the summary without the meter")
    args = parser.parse_args(argv)

    rederive = _count_tokens(_read(args.source))
    retrieve = _count_tokens(_read([args.summary]))
    saved = rederive - retrieve
    pct = (saved / rederive * 100.0) if rederive else 0.0

    print("Compound loop — re-derivation vs retrieval (real token counts)\n")
    print(f"  RE-DERIVE from source ({len(args.source)} file(s)): {rederive:>7,} Bobcoins")
    print(f"  RETRIEVE the KB summary                     : {retrieve:>7,} Bobcoins")
    print()
    if not args.no_animate and sys.stdout.isatty():
        _animate(rederive, retrieve)
    print(f"\n  Avoided this turn: {saved:,} Bobcoins ({pct:.0f}% of the re-derivation cost) — for THIS document.")
    print("  Mechanism: retrieval, not re-derivation. Not the headline 20% compression; not a velocity claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
