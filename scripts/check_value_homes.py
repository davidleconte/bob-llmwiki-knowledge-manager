#!/usr/bin/env python3
"""Enforce "one home per value": a value duplicated across files must not drift.

A value that lives in more than one hand-maintained place (a config field, a
code literal, a doc table) needs a machine check that fails when the copies
disagree -- otherwise it drifts silently. This is the *generic* "one home per
value" validator the institutional audit scoped to Phase 6
(``audit-2026-07-13-institutional.md:188``). It generalises the two
value-specific guards that came before it and stay in place:

* ``check_status_consistency.py`` -- coverage gate + maturity status;
* ``check_savings_claims.py``     -- manifest-backed savings numbers.

Those two encode domain-specific escape rules (a gate-shaped regex, retraction
tokens) that don't generalise. This guard covers the plain case: a literal value
with **one canonical home** that other files merely restate.

The registry below is the single place to declare such a value. Each
:class:`ValueHome` names the canonical source (a file + a capture regex) and its
``mirrors``; a mirror is verified either by

* ``extract`` -- pull a value out of the mirror; it must EQUAL the canonical; or
* ``contains`` -- a template rendered from the canonical value must appear
  verbatim in the mirror (for prose that restates, not re-declares, the value).

Prefer *eliminating* a mirror (reword the prose to point at the home) over
adding one here; register a mirror only when the restatement is worth keeping.

Frozen point-in-time records (dated ``docs/**/research`` snapshots,
``evaluation/**``, ``docs/PHASE*_IMPLEMENTATION_COMPLETE.md``) and any file
banner-marked ``DEPRECATED``/``STALE`` are not authoritative and are skipped.

Usage::

    python scripts/check_value_homes.py
    python scripts/check_value_homes.py --selftest   # verify the engine

Exits non-zero (and prints every divergence) on any drift.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

DEPRECATION_MARKERS = ("DEPRECATED", "STALE")
DEPRECATION_SCAN_LINES = 15

# A reader maps a repo-relative path to its text, or None if it is missing or
# banner-deprecated (i.e. not authoritative). Injected so the engine is testable
# without touching the filesystem (see ``_selftest``).
Reader = Callable[[str], Optional[str]]


@dataclass(frozen=True)
class Mirror:
    """A file that restates a canonical value and must not diverge from it."""

    file: str
    mode: str  # "extract" | "contains"
    pattern: str  # extract: regex w/ group(1); contains: template using {value}
    note: str = ""


@dataclass(frozen=True)
class ValueHome:
    """One canonical value (``file`` + capture ``pattern``) and its mirrors."""

    name: str
    file: str
    pattern: str  # regex whose group(1) is the canonical value
    mirrors: tuple[Mirror, ...] = field(default_factory=tuple)


# --- The registry: one entry per value that lives in more than one place. ------

REGISTRY: tuple[ValueHome, ...] = (
    # Package version. Canonical: pyproject [project] version. src/__init__ had
    # already drifted to "1.0.0-dev" before this guard existed -- exactly the
    # silent divergence this check exists to stop.
    ValueHome(
        name="package_version",
        file="pyproject.toml",
        pattern=r'(?m)^\s*version\s*=\s*"([^"]+)"',
        mirrors=(
            Mirror("src/__init__.py", "extract", r'__version__\s*=\s*"([^"]+)"'),
            Mirror("src/delegation/__init__.py", "extract", r'__version__\s*=\s*"([^"]+)"'),
            # First semver header in the changelog (skips the [Unreleased] section).
            Mirror("CHANGELOG.md", "extract", r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]"),
        ),
    ),
    # Supported-version line published in SECURITY.md. Canonical: the pyproject
    # major.minor -- the "1.0.x" support line tracks the released minor, so this
    # captures major.minor (not the full patch version) and mirrors it as
    # "{value}.x". Its own entry precisely because it mirrors major.minor.
    ValueHome(
        name="security_supported_line",
        file="pyproject.toml",
        pattern=r'(?m)^\s*version\s*=\s*"(\d+\.\d+)',
        mirrors=(Mirror("SECURITY.md", "contains", "{value}.x", "supported-versions table"),),
    ),
    # Supported-Python floor. Canonical: pyproject requires-python. The "kept in
    # sync" claims in CI/README/AGENTS were enforced only by hand until now.
    ValueHome(
        name="python_floor",
        file="pyproject.toml",
        pattern=r'requires-python\s*=\s*">=\s*(\d+\.\d+)"',
        mirrors=(
            Mirror(".github/workflows/ci.yml", "contains", "{value}", "CI matrix floor"),
            Mirror("README.md", "contains", "{value}", 'the "Python 3.11+" line'),
            Mirror("AGENTS.md", "contains", "{value}", 'the "Python 3.11+" line'),
        ),
    ),
    # Model list price (USD per 1K tokens). Canonical: src/pricing.py PRICES table
    # (split into input/output per ModelPrice, B2). One doc restates the gpt-4
    # input/output rates in a worked cost example. Semi-frozen long-form docs
    # (BOOK_*) are deliberately NOT mirrored -- keep the home the live concept doc.
    ValueHome(
        name="price_gpt4_input_per_1k",
        file="src/pricing.py",
        pattern=r'"gpt-4":\s*ModelPrice\(\s*input_per_1k=([\d.]+)',
        mirrors=(
            Mirror(
                "docs/knowledge-base/concepts/token-optimization.md",
                "contains",
                "${value}",
                "1,000 input tokens rate",
            ),
        ),
    ),
    ValueHome(
        name="price_gpt4_output_per_1k",
        file="src/pricing.py",
        pattern=r'"gpt-4":\s*ModelPrice\([^)]*?output_per_1k=([\d.]+)',
        mirrors=(
            Mirror(
                "docs/knowledge-base/concepts/token-optimization.md",
                "contains",
                "${value}",
                "1,000 output tokens rate",
            ),
        ),
    ),
    # A7 input-bound caps. Home: src/limits.py (imported at every enforcement
    # point). Mirror: config/gates/gate-config.yaml restates each for CODEOWNERS-
    # visible review, so weakening a DoS ceiling shows up in the gate-config diff.
    # extract-mode compares the YAML value to the code constant for equality.
    ValueHome(
        name="limit_max_file_bytes",
        file="src/limits.py",
        pattern=r"MAX_FILE_BYTES\s*=\s*(\d+)",
        mirrors=(Mirror("config/gates/gate-config.yaml", "extract", r"max_file_bytes:\s*(\d+)"),),
    ),
    # Audit 2026-07-25 (finding G-4). gate-config.yaml opens by claiming it exists to
    # "externalize thresholds from gate scripts so a PR that weakens a threshold is
    # conspicuous". Four of its six blocks were read by nothing and cross-checked by
    # nothing -- savings_gate and metric_gate in particular restated values that the
    # scripts also hardcoded, so the two could drift and the config would still *look*
    # authoritative. An inert config block that claims to externalize a threshold is
    # worse than no block: it invites a reviewer to check the wrong file.
    #
    # The scripts stay stdlib-only (no YAML parser in a gate), so the fix is the same
    # one the DoS ceilings above use: code is the home, config mirrors it, and a
    # divergence fails here.
    ValueHome(
        name="savings_gate_banner_scan_lines",
        file="scripts/check_savings_claims.py",
        pattern=r"(?m)^BANNER_SCAN_LINES\s*=\s*(\d+)",
        mirrors=(
            Mirror("config/gates/gate-config.yaml", "extract", r"banner_scan_lines:\s*(\d+)"),
        ),
    ),
    ValueHome(
        name="savings_gate_manifest_tolerance_pct",
        file="scripts/check_savings_claims.py",
        pattern=r"(?m)^_MANIFEST_TOLERANCE_PCT\s*=\s*([\d.]+)",
        mirrors=(
            Mirror(
                "config/gates/gate-config.yaml",
                "extract",
                r"magnitude_tolerance_pct:\s*([\d.]+)",
            ),
        ),
    ),
    ValueHome(
        name="limit_max_chunks_per_doc",
        file="src/limits.py",
        pattern=r"MAX_CHUNKS_PER_DOC\s*=\s*(\d+)",
        mirrors=(
            Mirror("config/gates/gate-config.yaml", "extract", r"max_chunks_per_doc:\s*(\d+)"),
        ),
    ),
    ValueHome(
        name="limit_max_query_chars",
        file="src/limits.py",
        pattern=r"MAX_QUERY_CHARS\s*=\s*(\d+)",
        mirrors=(Mirror("config/gates/gate-config.yaml", "extract", r"max_query_chars:\s*(\d+)"),),
    ),
    ValueHome(
        name="limit_max_graph_nodes",
        file="src/limits.py",
        pattern=r"MAX_GRAPH_NODES\s*=\s*(\d+)",
        mirrors=(Mirror("config/gates/gate-config.yaml", "extract", r"max_graph_nodes:\s*(\d+)"),),
    ),
)


def is_deprecated(text: str) -> bool:
    head = "\n".join(text.splitlines()[:DEPRECATION_SCAN_LINES]).upper()
    return any(marker in head for marker in DEPRECATION_MARKERS)


def extract(text: str, pattern: str) -> Optional[str]:
    """Return group(1) of the first match of ``pattern`` in ``text``, or None."""
    m = re.search(pattern, text)
    return m.group(1) if m else None


def check_home(vh: ValueHome, read: Reader) -> list[str]:
    """Return a list of human-readable problems for one value (empty == OK)."""
    canonical_text = read(vh.file)
    if canonical_text is None:
        return [f"canonical source {vh.file} is missing or not authoritative"]
    canonical = extract(canonical_text, vh.pattern)
    if canonical is None:
        return [f"canonical value not found in {vh.file} (pattern {vh.pattern!r})"]

    problems: list[str] = []
    for mirror in vh.mirrors:
        text = read(mirror.file)
        if text is None:
            # Missing/deprecated mirror is not a drift -- just nothing to check.
            continue
        if mirror.mode == "extract":
            found = extract(text, mirror.pattern)
            if found is None:
                problems.append(f"{mirror.file}: no value matched {mirror.pattern!r}")
            elif found != canonical:
                problems.append(
                    f"{mirror.file}: has {found!r}, canonical ({vh.file}) is {canonical!r}"
                )
        elif mirror.mode == "contains":
            needle = mirror.pattern.format(value=canonical)
            if needle not in text:
                where = f" ({mirror.note})" if mirror.note else ""
                problems.append(
                    f"{mirror.file}: does not contain {needle!r}{where}; "
                    f"canonical ({vh.file}) is {canonical!r}"
                )
        else:  # pragma: no cover - guarded by _selftest
            problems.append(f"{mirror.file}: unknown mirror mode {mirror.mode!r}")
    return problems


def _repo_reader() -> Reader:
    def read(rel: str) -> Optional[str]:
        path = REPO_ROOT / rel
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        return None if is_deprecated(text) else text

    return read


def _selftest() -> int:
    """Verify the engine flags a planted divergence and passes a matched one."""
    vh = ValueHome(
        name="selftest",
        file="home",
        pattern=r'version\s*=\s*"([^"]+)"',
        mirrors=(
            Mirror("good", "extract", r'v\s*=\s*"([^"]+)"'),
            Mirror("prose", "contains", "v{value}"),
        ),
    )
    home = 'version = "1.0.0"'
    passing: dict[str, str] = {"home": home, "good": 'v = "1.0.0"', "prose": "release v1.0.0 ships"}
    drifting: dict[str, str] = {
        "home": home,
        "good": 'v = "0.9.9"',  # extract mismatch
        "prose": "release v2.0.0 ships",  # contains miss
    }

    failures: list[str] = []
    if check_home(vh, passing.get):
        failures.append("matched fixture reported a false divergence")
    drift = check_home(vh, drifting.get)
    if len(drift) != 2:
        failures.append(f"planted divergence: expected 2 problems, got {len(drift)}: {drift}")

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("SELFTEST OK: planted divergence flagged (2), matched fixture clean.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()

    read = _repo_reader()
    failures: list[str] = []
    print("Checking 'one home per value' across live files:\n")
    for vh in REGISTRY:
        problems = check_home(vh, read)
        if problems:
            failures.append(vh.name)
            print(f"  FAIL {vh.name} (home: {vh.file}):")
            for problem in problems:
                print(f"    - {problem}")
        else:
            print(f"  OK   {vh.name} (home: {vh.file})")

    if failures:
        print(
            f"\nFAILED: {len(failures)} value(s) have drifted from their home: "
            f"{', '.join(failures)}\n"
            "Update the mirror to match the canonical source, or reword it to stop "
            "restating the value. See the registry in scripts/check_value_homes.py.",
            file=sys.stderr,
        )
        return 1
    print("\nAll registered values agree with their single home.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
