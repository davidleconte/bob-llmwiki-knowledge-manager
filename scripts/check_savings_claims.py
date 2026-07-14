#!/usr/bin/env python3
"""Enforce that published savings/cost numbers cite a reproducible manifest.

``STATUS.md`` sets the rule this guard enforces:

    "Every published savings/cost number must cite a reproducible run with a
     manifest (data hash, code SHA, config, seed, library versions, git_dirty).
     Numbers without provenance are not to be published."

Phase 5 replaced the fabricated validator with a real, manifest-backed harness
(:mod:`src.validation`). This guard stops un-provenanced savings claims from
creeping back into live surfaces.

Scope (Phase 8): the scan is now **tree-wide**, not a five-file allowlist. The
old allowlist could not see the ``docs/BOOK_*`` / ``docs/adr/*`` / guide files
where the fabricated ``68.96% / 89.3% / 91.80%`` figures survived unretracted, so
a green gate did not prove a clean tree. It now scans every markdown surface
under ``docs/`` plus the top-level status docs and the two claim-bearing code
files, and a file passes only if each savings/cost percentage either cites a
manifest, is explicitly tagged as retracted/fabricated on its own line, **or**
the file carries a retraction/deprecation *banner* in its head.

The **banner exception** is how frozen planning/audit-trail docs
(``docs/project-management/**``, ``docs/architecture/deprecated/**``) stay in the
tree unedited: a one-line banner that names the numbers as retracted annotates
the whole file, so historical snapshots are preserved verbatim below the banner
without re-asserting fabricated results as current fact.

Only genuinely frozen dated records are exempt from scanning entirely:
``docs/knowledge-base/research/**`` (dated audit snapshots) and
``PHASE*_IMPLEMENTATION_COMPLETE.md``.

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

# Top-level markdown status surfaces outside docs/.
TOP_LEVEL_DOCS = ("README.md", "STATUS.md", "AGENTS.md", "CHANGELOG.md")

# Code is scanned tree-wide (all of ``src/**/*.py``), not via an allowlist: the
# Phase-8 sign-off found a fabricated "89.3% savings" docstring in
# ``src/optimizer/__init__.py`` that a hardcoded 2-file list (formerly just
# prompt_optimizer.py + exact_cache.py) never scanned. A claim-bearing line in any
# source file must cite a manifest or carry a retraction marker, same as the docs.

# Frozen dated records: not scanned at all (preserved verbatim, reflect what was
# believed at their date). Everything else under docs/ is scanned; frozen
# planning/audit-trail docs stay clean via the banner exception, not exclusion.
EXCLUDED_DIR_PARTS = ("knowledge-base/research",)
EXCLUDED_NAME_RE = re.compile(r"PHASE.*_IMPLEMENTATION_COMPLETE", re.IGNORECASE)

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
    "withdrawn",
    "manufactured",
)

# A file whose head carries one of these markers is treated as fully annotated
# (the "banner exception"). Uppercased comparison, so "retracted"/"Fabricated"
# etc. all match. Deprecation markers are included so already-deprecated docs
# (docs/architecture/deprecated/**) need no second banner.
BANNER_MARKERS = (
    "RETRACT",
    "FABRICAT",
    "DEPRECATED",
    "STALE",
    "SUPERSEDED",
    "WITHDRAWN",
    "HISTORICAL SNAPSHOT",
    "MANUFACTURED",
)
BANNER_SCAN_LINES = 20


def has_banner(text: str) -> bool:
    """True if the file's head carries a retraction/deprecation banner."""
    head = "\n".join(text.splitlines()[:BANNER_SCAN_LINES]).upper()
    return any(marker in head for marker in BANNER_MARKERS)


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
    """Return ``(line_no, line)`` for every unbacked savings claim in ``text``.

    A file-head retraction/deprecation banner annotates the whole file, so a
    frozen snapshot preserved verbatim below the banner does not trip the gate.
    """
    if has_banner(text):
        return []
    violations: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line_is_unbacked_claim(line):
            violations.append((line_no, line.strip()))
    return violations


def _is_excluded(rel: str) -> bool:
    if any(part in rel for part in EXCLUDED_DIR_PARTS):
        return True
    if EXCLUDED_NAME_RE.search(Path(rel).name):
        return True
    return False


def iter_surfaces() -> list[str]:
    """Every repo-relative surface to scan: docs/**.md + top-level docs + code."""
    surfaces: list[str] = []
    for name in TOP_LEVEL_DOCS:
        if (REPO_ROOT / name).exists():
            surfaces.append(name)
    for md in sorted((REPO_ROOT / "docs").rglob("*.md")):
        rel = md.relative_to(REPO_ROOT).as_posix()
        if not _is_excluded(rel):
            surfaces.append(rel)
    for code in sorted((REPO_ROOT / "src").rglob("*.py")):
        rel = code.relative_to(REPO_ROOT).as_posix()
        if not _is_excluded(rel):
            surfaces.append(rel)
    return surfaces


def _selftest() -> int:
    """Verify the detector on planted good/bad strings (Phase-5/8 verification)."""
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

    # Banner exception: a fabricated number under a retraction banner passes.
    bannered = (
        "> **RETRACTED METRICS.** The 89.3% figure was fabricated.\n\n- 89.3% token savings\n"
    )
    if scan_text(bannered):
        failures.append("BANNER EXCEPTION BROKEN: bannered file still flagged")
    # ... but the same content WITHOUT a banner must be flagged.
    if not scan_text("# Results\n\n- 89.3% token savings\n"):
        failures.append("TREE SCAN BROKEN: un-bannered fabricated number not flagged")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: {len(bad)} flagged, {len(good)} passed, banner exception verified.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    failures: list[str] = []
    surfaces = iter_surfaces()
    print(
        f"Checking that published savings/cost numbers cite a manifest ({len(surfaces)} surfaces):\n"
    )
    for rel in surfaces:
        path = REPO_ROOT / rel
        violations = scan_text(path.read_text(encoding="utf-8"))
        if violations:
            failures.append(rel)
            print(f"  FAIL {rel}:")
            for line_no, line in violations:
                print(f"    L{line_no}: unbacked savings/cost claim\n        {line}")

    if failures:
        print(
            f"\nFAILED: {len(failures)} surface(s) publish a savings/cost number "
            f"without a manifest citation:\n  {chr(10).join('  ' + f for f in sorted(set(failures)))}\n"
            "Cite the run's manifest (evaluation/results/validation-<date>/manifest.json), "
            "remove the number, or (for a frozen snapshot) add a retraction banner. See STATUS.md.",
            file=sys.stderr,
        )
        return 1
    print(f"\nAll {len(surfaces)} scanned surfaces cite a manifest for every savings/cost number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
