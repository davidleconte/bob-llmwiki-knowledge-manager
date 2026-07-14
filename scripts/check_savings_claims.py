#!/usr/bin/env python3
"""Enforce that published savings/cost numbers cite a reproducible manifest.

``STATUS.md`` sets the rule this guard enforces:

    "Every published savings/cost number must cite a reproducible run with a
     manifest (data hash, code SHA, config, seed, library versions, git_dirty).
     Numbers without provenance are not to be published."

Phase 5 replaced the fabricated validator with a real, manifest-backed harness
(:mod:`src.validation`). This guard stops un-provenanced savings claims from
creeping back into live surfaces: it scans a curated set of live docs/code for a
savings/reduction/hit-rate keyword next to a literal percentage, and fails unless
that line either cites a manifest/validation report or is explicitly describing a
retracted/fabricated number.

Scope is deliberately a curated allowlist of the surfaces that actually publish
these numbers -- the *generic* "one home per value" validator is Phase 6. Dated
audit snapshots (``docs/knowledge-base/research/**``, ``evaluation/**``,
``docs/PHASE*_IMPLEMENTATION_COMPLETE.md``) and banner-``DEPRECATED``/``STALE``
docs are frozen point-in-time records and are not scanned.

Usage::

    python scripts/check_savings_claims.py
    python scripts/check_savings_claims.py --selftest   # verify the detector

Exits non-zero (and prints every unbacked claim) on any violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Live surfaces that publish savings/cost/hit-rate numbers. Curated (not a glob)
# so frozen dated snapshots stay out. The two code files carry claim-bearing
# docstrings/comments the institutional audit flagged.
LIVE_SURFACES = (
    "STATUS.md",
    "README.md",
    "AGENTS.md",
    "docs/INDEX.md",
    "docs/REPOSITORY_ANALYSIS_WORKFLOW.md",
    "src/optimizer/prompt_optimizer.py",
    "src/cache/exact_cache.py",
)

# A line is a savings/cost claim when it pairs one of these keywords with a
# literal percentage.
SAVINGS_KEYWORDS = (
    "savings",
    "saved",
    "reduction",
    "reduce",
    "hit rate",
    "hit-rate",
    "compression",
)

PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*%")

# A claim is acceptable if the line cites provenance (a manifest / validation
# report) ...
BACKED_TOKENS = ("manifest", "report.json", "validation-2", "reproducible run")

# ... or is explicitly describing a retracted / non-published number.
RETRACTION_TOKENS = (
    "retract",
    "fabricat",
    "not validated",
    "not_validated",
    "strawman",
    "unearned",
    "do not publish",
    "must cite",
    "superseded",
)

DEPRECATION_MARKERS = ("DEPRECATED", "STALE")
DEPRECATION_SCAN_LINES = 15


def is_deprecated(text: str) -> bool:
    head = "\n".join(text.splitlines()[:DEPRECATION_SCAN_LINES]).upper()
    return any(marker in head for marker in DEPRECATION_MARKERS)


def line_is_unbacked_claim(line: str) -> bool:
    """True if ``line`` publishes a savings/cost percentage without provenance."""
    low = line.lower()
    if not any(keyword in low for keyword in SAVINGS_KEYWORDS):
        return False
    if not PERCENT_RE.search(line):
        return False
    if any(token in low for token in BACKED_TOKENS):
        return False
    if any(token in low for token in RETRACTION_TOKENS):
        return False
    return True


def scan_text(text: str) -> list[tuple[int, str]]:
    """Return ``(line_no, line)`` for every unbacked savings claim in ``text``."""
    if is_deprecated(text):
        return []
    violations: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line_is_unbacked_claim(line):
            violations.append((line_no, line.strip()))
    return violations


def _selftest() -> int:
    """Verify the detector on planted good/bad strings (Phase-5 verification)."""
    bad = [
        "Combined savings: 40-60% in production.",
        "Token savings: 68.96% (95% CI [66.42, 71.51]).",
        "- 89.3% token savings",
        "L1 Cache: 85% hit rate",
    ]
    good = [
        "Optimizer compression: mean 20.0% (manifest: evaluation/results/validation-2026-07-14/manifest.json).",
        'The "68.96% / VALIDATED" figures were fabricated and are retracted.',
        "Every published savings/cost number must cite a reproducible run with a manifest.",
        "target_reduction defaults to 0.3 (a ratio, no percentage).",
        "Coverage gate is >=80% enforced in pyproject.",
    ]
    failures: list[str] = []
    for line in bad:
        if not line_is_unbacked_claim(line):
            failures.append(f"MISSED (should flag): {line!r}")
    for line in good:
        if line_is_unbacked_claim(line):
            failures.append(f"FALSE POSITIVE (should pass): {line!r}")
    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: {len(bad)} flagged, {len(good)} passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    failures: list[str] = []
    print("Checking that published savings/cost numbers cite a manifest:\n")
    for rel in LIVE_SURFACES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"  SKIP {rel}: not found")
            continue
        violations = scan_text(path.read_text(encoding="utf-8"))
        if violations:
            failures.append(rel)
            print(f"  FAIL {rel}:")
            for line_no, line in violations:
                print(f"    L{line_no}: unbacked savings/cost claim\n        {line}")
        else:
            print(f"  OK   {rel}")

    if failures:
        print(
            f"\nFAILED: {len(failures)} live surface(s) publish a savings/cost number "
            f"without a manifest citation: {', '.join(sorted(set(failures)))}\n"
            "Cite the run's manifest (evaluation/results/validation-<date>/manifest.json), "
            "or remove the number. See STATUS.md.",
            file=sys.stderr,
        )
        return 1
    print("\nAll live surfaces cite a manifest for every savings/cost number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
