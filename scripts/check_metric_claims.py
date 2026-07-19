#!/usr/bin/env python3
"""C2: enforce that published retrieval/accuracy metric claims cite a report.

The savings gate (:mod:`scripts.check_savings_claims`) only fires on *savings*
keywords, so a retrieval-precision or accuracy overclaim — e.g. the withdrawn
"p@3 44% -> 88%" — is structurally invisible to it (a p@3 figure carries no savings
keyword). This sibling gate closes that blind spot: a line that pairs a metric
keyword (precision, recall, p@N, accuracy, uplift, nDCG, MRR) with a *percentage* on
a live surface must co-locate a report/manifest citation or a retraction token,
exactly like the savings-line contract.

It reuses the savings gate's surface list and banner logic, so the same frozen
records are exempt on the same terms (dated research snapshots; non-outward-facing
bannered docs). An outward-facing live claim surface is scanned regardless of any
banner (C1), so a stale retrieval-lift narrative can no longer hide in a submission.

Usage::

    python scripts/check_metric_claims.py
    python scripts/check_metric_claims.py --selftest
"""

from __future__ import annotations

import sys

try:
    # Package import: works under pytest / an editable install (repo root on path).
    from scripts.check_savings_claims import (
        BACKED_TOKENS,
        PERCENT_RE,
        REPO_ROOT,
        RETRACTION_TOKENS,
        _is_backed_by_manifest_path,
        _scan_despite_banner,
        has_banner,
        iter_surfaces,
    )
except ModuleNotFoundError:
    # Direct-script run (`python scripts/check_metric_claims.py`, as in CI's ruff
    # job): only scripts/ is on sys.path[0], not the repo root, so the `scripts`
    # package is not importable. Fall back to the sibling-module import. This is
    # the exact condition that failed CI (no `pip install -e .` in the lint job).
    from check_savings_claims import (  # type: ignore[no-redef]
        BACKED_TOKENS,
        PERCENT_RE,
        REPO_ROOT,
        RETRACTION_TOKENS,
        _is_backed_by_manifest_path,
        _scan_despite_banner,
        has_banner,
        iter_surfaces,
    )

# Retrieval-ranking-quality metric keywords, deliberately scoped to the named
# retrieval metrics so ordinary English ("recall that…", "with precision") and
# unrelated engineering accuracy (code-block detection, shell-command matching,
# similarity thresholds) do NOT false-positive. Bare "recall"/"accuracy" are
# excluded for exactly that reason; the demonstrated hole ("p@3 precision uplift
# 44% → 88%") is caught by "p@"/"precision"/"uplift".
METRIC_KEYWORDS = (
    "p@",
    "recall@",
    "ndcg",
    "mrr",
    "map@",
    "precision",
    "uplift",
)

# A metric claim is backed by a report/manifest citation on (or just after) the
# line. Reuse the savings backing tokens plus the retrieval report path shapes.
METRIC_BACKED_TOKENS = BACKED_TOKENS + ("retrieval-2", "golden set", "golden_set")


def line_is_unbacked_metric(line: str) -> bool:
    """True if ``line`` publishes a retrieval/accuracy metric percentage without a report."""
    low = line.lower()
    if not any(k in low for k in METRIC_KEYWORDS):
        return False
    if not PERCENT_RE.search(line):
        return False
    if any(token in low for token in METRIC_BACKED_TOKENS):
        return False
    if any(token in low for token in RETRACTION_TOKENS):
        return False
    if _is_backed_by_manifest_path(line):
        return False
    return True


def scan_text_metrics(text: str) -> list[tuple[int, str]]:
    """Return ``(line_no, line)`` for every unbacked metric claim in ``text``.

    Honours the savings gate's banner/frozen logic: a genuinely frozen record is
    exempt, but an outward-facing live claim surface is scanned per line (C1). The
    same next-line look-ahead handles a citation wrapped onto the continuation line.
    """
    if has_banner(text) and not _scan_despite_banner(text):
        return []
    violations: list[tuple[int, str]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line_is_unbacked_metric(line):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            next_line = lines[j] if j < len(lines) else ""
            low_next = next_line.lower()
            if _is_backed_by_manifest_path(next_line) or any(
                token in low_next for token in METRIC_BACKED_TOKENS
            ):
                i += 1
                continue
            violations.append((i + 1, line.strip()))
        i += 1
    return violations


def _selftest() -> int:
    """Verify the detector on planted good/bad metric strings (C2)."""
    bad = [
        "Retrieval precision uplift: 44% -> 88% (validated configuration).",
        "Semantic index lifts p@3 to 88% correct in top 3.",
        "nDCG jumps to 95% with the embedding index.",
    ]
    good = [
        "p@3 = 0.84 in top 3 (manifest: evaluation/results/retrieval-2026-07-19/report.json).",
        'The "p@3 88%" claim was unverified and is retracted.',
        "Code Block Detection: 98% accuracy.",  # 'accuracy' is out of scope, not a retrieval metric
        "recall that 80% of teams adopt it.",  # bare 'recall' English verb is out of scope
        "target_reduction defaults to 0.3 (a ratio, no metric).",
    ]
    failures: list[str] = []
    for line in bad:
        if not line_is_unbacked_metric(line):
            failures.append(f"MISSED (should flag): {line!r}")
    for line in good:
        if line_is_unbacked_metric(line):
            failures.append(f"FALSE POSITIVE (should pass): {line!r}")

    # A frozen record's banner suppresses the metric scan; a live outward-facing
    # doc is scanned despite the banner (C1 parity).
    frozen = "---\nstatus: superseded\n---\n\n> **HISTORICAL SNAPSHOT.**\n\n- p@3 uplift to 88%\n"
    if scan_text_metrics(frozen):
        failures.append("BANNER: frozen record's banner should suppress the metric scan")
    live = (
        "---\nstatus: active\naudience: [challenge-judges]\n---\n\n"
        "> **HISTORICAL SNAPSHOT.**\n\n- p@3 uplift to 88%\n"
    )
    if not scan_text_metrics(live):
        failures.append("C1 PARITY: outward-facing live doc must be scanned despite banner")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"SELFTEST OK: {len(bad)} flagged, {len(good)} passed, banner parity verified.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    failures: list[str] = []
    surfaces = iter_surfaces()
    print(
        f"Checking that published retrieval/accuracy metrics cite a report "
        f"({len(surfaces)} surfaces):\n"
    )
    for rel in surfaces:
        path = REPO_ROOT / rel
        violations = scan_text_metrics(path.read_text(encoding="utf-8"))
        if violations:
            failures.append(rel)
            print(f"  FAIL {rel}:")
            for line_no, line in violations:
                print(f"    L{line_no}: unbacked retrieval/accuracy metric claim\n        {line}")

    if failures:
        print(
            f"\nFAILED: {len(failures)} surface(s) publish a retrieval/accuracy metric "
            "without a report citation:\n  "
            + "\n  ".join(sorted(set(failures)))
            + "\nCite the run's report (evaluation/results/retrieval-<date>/report.json), "
            "retract the figure, or reframe it. See STATUS.md.",
            file=sys.stderr,
        )
        return 1
    print(
        f"\nAll {len(surfaces)} scanned surfaces cite a report for every retrieval/accuracy metric."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
