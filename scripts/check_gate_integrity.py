#!/usr/bin/env python3
"""Gate-integrity check (ATK-GATE-07 / C3): forbid weakening a gate and planting a
claim in the SAME pull request.

One actor authoring the code, the gates that check it, and the claims those gates
guard is bus-factor 1. Absent a second human reviewer, this structural check
mechanically blocks the single-PR "weaken the gate + plant the overclaim" attack:
a PR whose diff touches BOTH a gate definition AND a claim surface fails.

- GATE definitions:  ``config/gates/**``, ``scripts/check_*.py``, ``src/validation/**``,
  ``.github/workflows/**``
- CLAIM surfaces:     ``STATUS.md``, ``README.md``, ``AGENTS.md``, ``INTEGRATIONS.md``,
  ``SECURITY.md``, ``docs/**`` (except ``docs/api/**``),
  ``2026_IBMer_Watsonx_Challenge/**``

``.github/workflows/**`` and the extra claim surfaces were added 2026-07-25 by the
full-project audit (findings G-1/G-2). A gate is only a gate if CI invokes it, so a PR
could previously delete a gate's CI step and plant a claim in the same change and pass —
the precise attack this check exists to block, through a path it was not watching. The
audit demonstrated the failure mode concretely: ``tests/performance/test_dos_hardening.py``
sat in no CI job at all and nothing noticed.

``docs/api/**`` is excluded because it is generated from ``src/`` docstrings and
pinned to them by the API-doc freshness gate — it is not a hand-authored claim
surface, and including it would contradict the mandatory API-doc regeneration that
accompanies a ``src/validation/**`` change.

A gate-only PR (tightening a check) and a claim-only PR (updating a doc) both pass;
only their combination in one PR is blocked. Split such a change into two PRs so the
gate change lands and is independently reviewable BEFORE any claim relies on it.
This is disclosed in ``SECURITY.md`` §Gate Independence as the honest substitute for
a second required human reviewer.

Usage::

    check_gate_integrity.py <changed_file> [<changed_file> ...]
    check_gate_integrity.py --base origin/main      # diff against a base ref
    git diff --name-only main...HEAD | check_gate_integrity.py --stdin
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Iterable, List

# One-home constants so the tests and the doc can reference the same definitions.
#
# ``.github/workflows/`` added 2026-07-25 (audit finding G-2). A gate is only a gate if
# CI invokes it, so the workflow file is a gate *definition* in every meaningful sense —
# deleting a step disables a check exactly as surely as weakening the script it runs.
# Before this, a single PR could remove a gate's CI step and plant a claim in README.md
# and pass, which is the precise attack ATK-GATE-07 exists to block, through a path it
# was not watching. Demonstrated by the audit: the DoS-hardening suite sat in no CI job
# at all for weeks without any gate noticing.
GATE_DIR_PREFIXES = ("config/gates/", "src/validation/", ".github/workflows/")

# Claim surfaces. AGENTS.md / INTEGRATIONS.md / SECURITY.md added 2026-07-25: each
# carries published maturity or savings claims (AGENTS.md was found asserting a ~51%
# savings figure and a 4.8x-understated LOC count), so a gate change must not ride
# alongside an edit to them either.
CLAIM_FILES = frozenset({"STATUS.md", "README.md", "AGENTS.md", "INTEGRATIONS.md", "SECURITY.md"})
CLAIM_DIR_PREFIX = "docs/"
CLAIM_DIR_EXCLUDE = "docs/api/"  # generated reference, pinned by the freshness gate

# The outward-facing competition pack: 13 tracked files written for external judges,
# previously outside every gate's scope (audit finding G-1). Treated as a claim surface
# so a gate weakening cannot land beside a submission edit.
CLAIM_DIR_EXTRA_PREFIXES = ("2026_IBMer_Watsonx_Challenge/",)


def _normalise(path: str) -> str:
    """Strip a leading ``./`` and normalise separators to forward slashes."""
    p = path.strip().replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def is_gate_file(path: str) -> bool:
    """True if *path* is a gate definition (config, gate script, or validation)."""
    p = _normalise(path)
    if any(p.startswith(prefix) for prefix in GATE_DIR_PREFIXES):
        return True
    # scripts/check_*.py — the honesty gate scripts themselves.
    return (
        p.startswith("scripts/") and p.rsplit("/", 1)[-1].startswith("check_") and p.endswith(".py")
    )


def is_claim_surface(path: str) -> bool:
    """True if *path* is a hand-authored claim surface (status/readme/docs/submission)."""
    p = _normalise(path)
    if p in CLAIM_FILES:
        return True
    if p.startswith(CLAIM_DIR_EXTRA_PREFIXES):
        return True
    return p.startswith(CLAIM_DIR_PREFIX) and not p.startswith(CLAIM_DIR_EXCLUDE)


def check(changed_files: Iterable[str]) -> List[str]:
    """Return a list of problems (empty == OK) for a set of changed files.

    A single problem is reported when the diff touches both a gate and a claim
    surface, naming the offending files on each side.
    """
    files = [_normalise(f) for f in changed_files if f.strip()]
    gates = sorted({f for f in files if is_gate_file(f)})
    claims = sorted({f for f in files if is_claim_surface(f)})
    if gates and claims:
        return [
            "This PR modifies BOTH a gate definition and a claim surface, which the "
            "single-owner gate-integrity rule forbids (ATK-GATE-07). Split it into two "
            "PRs: land the gate change first (independently reviewable), then the claim.\n"
            f"  gate files:  {', '.join(gates)}\n"
            f"  claim files: {', '.join(claims)}"
        ]
    return []


def _selftest() -> int:
    """Prove the classifier separates gate definitions from claim surfaces.

    Added 2026-07-25: this was the one gate of eleven with no ``--selftest``, which is
    an odd omission for the gate whose whole job is to be trusted about what counts as
    a gate. It has always had a dedicated tests/gates/ module; this makes it provable
    from the command line too, the way the others are.
    """
    cases_gate = [
        "config/gates/gate-config.yaml",
        "src/validation/corpus.py",
        "scripts/check_savings_claims.py",
        ".github/workflows/ci.yml",
    ]
    cases_claim = [
        "STATUS.md",
        "README.md",
        "AGENTS.md",
        "docs/architecture/ARCHITECTURE.md",
        "2026_IBMer_Watsonx_Challenge/03-solution-impact.md",
    ]
    cases_neutral = [
        "src/optimizer/token_counter.py",
        "tests/gates/test_gate_integrity.py",
        ".github/CODEOWNERS",
        "docs/api/root/facade.md",  # generated, pinned by the freshness gate
    ]
    failures: list[str] = []
    for p in cases_gate:
        if not is_gate_file(p):
            failures.append(f"NOT CLASSIFIED AS GATE: {p}")
    for p in cases_claim:
        if not is_claim_surface(p):
            failures.append(f"NOT CLASSIFIED AS CLAIM: {p}")
    for p in cases_neutral:
        if is_gate_file(p) or is_claim_surface(p):
            failures.append(f"SHOULD BE NEUTRAL: {p}")
    # The rule itself: the combination is what is forbidden, not either half.
    if not check(["scripts/check_savings_claims.py", "STATUS.md"]):
        failures.append("MISSED: a gate + claim co-modification must be blocked")
    if check(["scripts/check_savings_claims.py", "config/gates/gate-config.yaml"]):
        failures.append("FALSE POSITIVE: a gate-only change must pass")
    if check(["STATUS.md", "docs/README.md"]):
        failures.append("FALSE POSITIVE: a claim-only change must pass")
    if check(["src/validation/measure.py", "docs/api/root/facade.md"]):
        failures.append("FALSE POSITIVE: validation + its regenerated api docs must pass")

    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(
        f"Self-test passed: {len(cases_gate)} gate / {len(cases_claim)} claim / "
        f"{len(cases_neutral)} neutral paths classified correctly, and the "
        "co-modification rule fires only on the combination."
    )
    return 0


def _changed_files_from_base(base: str) -> List[str]:
    """Return files changed between *base* and HEAD (three-dot / merge-base diff)."""
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Changed file paths to classify.")
    parser.add_argument("--base", help="Diff against this git ref (base...HEAD).")
    parser.add_argument("--stdin", action="store_true", help="Read file paths from stdin.")
    parser.add_argument("--selftest", action="store_true", help="verify the classifier")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    if args.base:
        changed = _changed_files_from_base(args.base)
    elif args.stdin:
        changed = [line for line in sys.stdin.read().splitlines() if line.strip()]
    else:
        changed = args.files

    problems = check(changed)
    if problems:
        print("❌ Gate-integrity check failed (ATK-GATE-07):\n")
        for p in problems:
            print(p)
        print(
            "\nSee SECURITY.md §Gate Independence. If the co-change is genuinely "
            "atomic, land the gate change in its own PR first."
        )
        return 1
    print("✅ Gate-integrity check passed: no gate + claim co-modification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
