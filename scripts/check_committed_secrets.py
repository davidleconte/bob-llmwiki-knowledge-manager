#!/usr/bin/env python3
"""No live credential may be committed to a tracked file (ATK-SUP-09).

Why this replaced an inline shell grep
--------------------------------------
The previous form of this gate lived inline in ``ci.yml`` as::

    git ls-files | xargs grep -Pn 'PASSWORD=[A-Za-z0-9!@#$%^&*]{3,}' \\
      | grep -v ".example" | grep -v "knowledge-base/research" | ...

It had three defects, and the first one hid the other two for months.

1. **It never ran.** The job carries ``needs: [test]``, and the coverage job was
   hanging until GitHub's 6-hour ceiling and being cancelled. Across the last six
   runs on ``main`` the secrets scan was ``skipped`` or ``cancelled`` every single
   time. A gate that cannot be reached is not a control; it is a comment.

2. **It exempted a live surface wholesale.** ``grep -v "knowledge-base/research"``
   is the ATK-GATE-04 pattern this repo has already been bitten by: a blanket
   directory exemption over prose that STATUS.md cites as its audit basis. Anything
   at all could be parked there.

3. **`grep -P` is not portable.** BSD grep has no ``-P``, and the ``2>/dev/null``
   swallowed the usage error, so running the same command on macOS printed nothing
   and looked clean. Same family as the case-sensitivity defects: a check that is
   silently inert on the maintainer's machine and live only on CI.

What replaces them
------------------
An explicit allowlist keyed on ``(path, sha256(matched line))``. Every currently
known hit is documentation *about* a resolved finding, not a live secret, and each
one is enumerated below with its reason. Because the key includes a hash of the
line, editing an allowlisted line — or adding a new credential anywhere, including
to an allowlisted file — produces an entry the allowlist does not cover and the gate
fires. That is the property a directory exemption cannot give you.

Ground truth at the time of writing: five tracked lines match, all markdown, and
``git ls-files | grep -v '\\.md$' | xargs grep -En 'PASSWORD=...'`` returns nothing.
The credential named in the findings is absent from code and config.

Usage::

    python scripts/check_committed_secrets.py
    python scripts/check_committed_secrets.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# A credential assignment: an uppercase *_PASSWORD (or bare PASSWORD) key set to a
# value that looks real. Deliberately narrow -- this gate is about the ATK-SUP-09
# class (a committed lab credential), not general secret scanning.
SECRET_RE = re.compile(r"(?:^|[^A-Za-z0-9_])([A-Z][A-Z0-9_]*PASSWORD)=([A-Za-z0-9!@#$%^&*]{3,})")

# Values that are obviously not credentials. Kept short and literal: a clever
# placeholder detector is a way to talk yourself out of a finding.
PLACEHOLDER_VALUES = frozenset(
    {
        "changeme",
        "your",
        "yourpassword",
        "xxx",
        "xxxx",
        "todo",
        "none",
        "null",
        "redacted",
        "placeholder",
        "example",
    }
)
PLACEHOLDER_PREFIXES = ("your-", "your_", "<", "${", "$(")

# Paths whose *content* is a template by construction.
TEMPLATE_SUFFIXES = (".example", ".template", ".sample")


class Hit(NamedTuple):
    path: str
    lineno: int
    key: str
    value: str
    digest: str


def line_digest(line: str) -> str:
    """Stable short hash of a matched line, used as the allowlist key."""
    return hashlib.sha256(line.strip().encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# The allowlist. Each entry is a *documented finding*, not a live secret.
# Keyed on (path, digest-of-line) so an edit to the line revokes the exemption.
# ---------------------------------------------------------------------------
ALLOWLIST: dict[tuple[str, str], str] = {
    (
        "docs/knowledge-base/research/adversarial-audit-2026-07-19.md",
        "c1f04765b408ee31",
    ): "Frozen dated audit snapshot; names the ATK-SUP-09 credential as a finding.",
    (
        "docs/knowledge-base/research/security-scan-2026-07-12.md",
        "a1c12ea52544b16b",
    ): "Verbatim published CVE-2026-28684 advisory text (DB_PASSWORD in the upstream PoC).",
    (
        "docs/knowledge-base/research/security-scan-2026-07-13.md",
        "a1c12ea52544b16b",
    ): "Verbatim published CVE-2026-28684 advisory text (DB_PASSWORD in the upstream PoC).",
    (
        "docs/project-management/plans/adversarial-remediation-plan.md",
        "b821ee81c94473ee",
    ): "Remediation instruction to rotate the credential; naming it is the instruction.",
    (
        "evaluation/regrade/regrade-kit-2026-07.md",
        "d3fcdc8570b8d0be",
    ): "Re-grade finding register; the grader greps for this literal to verify absence.",
}


def tracked_files(repo_root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def _is_placeholder(value: str) -> bool:
    low = value.lower()
    return low in PLACEHOLDER_VALUES or low.startswith(PLACEHOLDER_PREFIXES)


def scan_text(path: str, text: str) -> list[Hit]:
    """Every credential-shaped assignment in one file's text."""
    if path.endswith(TEMPLATE_SUFFIXES):
        return []
    hits: list[Hit] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for key, value in SECRET_RE.findall(line):
            if _is_placeholder(value):
                continue
            hits.append(Hit(path, lineno, key, value, line_digest(line)))
    return hits


def scan(repo_root: Path | None = None, paths: Iterable[str] | None = None) -> list[Hit]:
    root = repo_root or REPO_ROOT
    candidates = list(paths) if paths is not None else tracked_files(root)
    hits: list[Hit] = []
    for rel in candidates:
        full = root / rel
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except (OSError, IsADirectoryError):
            continue
        hits.extend(scan_text(rel, text))
    return hits


def unexplained(hits: Iterable[Hit]) -> list[Hit]:
    """Hits with no allowlist entry for this exact (path, line)."""
    return [h for h in hits if (h.path, h.digest) not in ALLOWLIST]


def credential_probe(value: str, key: str = "MQ_PASSWORD") -> str:
    """Assemble a credential-shaped line at runtime, for tests and the self-test.

    Never write ``SOMEKEY=<value>`` as a source literal in this file or its tests.
    This gate scans *tracked* files, and these files are tracked -- a literal here
    makes the gate flag its own fixtures. That is not hypothetical: the first CI run
    after these files were committed failed on ten of them. They had been untracked
    when the gate was validated, so ``git ls-files`` never showed the gate to itself.
    Assembling the string at call time keeps the source clean while the value under
    test is byte-identical.
    """
    return f"{key}=" + value


def _selftest() -> int:
    """Prove the gate can fail, and that the allowlist cannot be used as a skeleton key."""
    failures: list[str] = []

    real = scan_text("src/config.py", credential_probe("passw0rd") + "\n")
    if not real:
        failures.append("MISSED: a real credential assignment must be flagged")

    for placeholder in (
        "MQ_PASSWORD=<your-password-here>",
        "MQ_PASSWORD=your-password",
        "MQ_PASSWORD=changeme",
        "MQ_PASSWORD=${SECRET}",
    ):
        if scan_text("config/app.yaml", placeholder + "\n"):
            failures.append(f"FALSE POSITIVE: placeholder flagged: {placeholder}")

    if scan_text("config/app.yaml.example", credential_probe("passw0rd") + "\n"):
        failures.append("FALSE POSITIVE: a .example template must not be flagged")

    # The allowlist must be scoped to one exact line in one exact file.
    allow_path, allow_digest = next(iter(ALLOWLIST))
    same_line = next(
        line
        for line in (REPO_ROOT / allow_path)
        .read_text(encoding="utf-8", errors="replace")
        .splitlines()
        if line_digest(line) == allow_digest
    )
    if unexplained(scan_text(allow_path, same_line + "\n")):
        failures.append("the known documentation line should be allowlisted")
    # Same content, different file -> still a finding.
    if not unexplained(scan_text("src/leaked.py", same_line + "\n")):
        failures.append("ESCAPE: the allowlist must not exempt the same text in another file")
    # Same file, altered line -> still a finding.
    if not unexplained(scan_text(allow_path, same_line + " " + credential_probe("hunter2") + "\n")):
        failures.append("ESCAPE: editing an allowlisted line must revoke its exemption")
    # The gate must see its own source. This is the miss that shipped: these files
    # were untracked when the gate was first validated, so it never scanned itself.
    if unexplained(scan(paths=["scripts/check_committed_secrets.py"])):
        failures.append("this gate's own source must not contain a credential literal")

    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(
        "Self-test passed: real credential caught; placeholders and templates clean; "
        "allowlist is scoped to one exact line in one exact file."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan tracked files for committed credentials.")
    parser.add_argument("--selftest", action="store_true", help="verify the gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    hits = scan()
    bad = unexplained(hits)
    if not bad:
        print(
            f"OK: no unexplained credentials in tracked files "
            f"({len(hits)} known documentation reference(s) allowlisted by exact line)."
        )
        return 0

    print("ERROR: potential committed credential in tracked files:\n", file=sys.stderr)
    for h in bad:
        print(
            f"  {h.path}:{h.lineno}  {h.key}=<redacted>  (line digest {h.digest})", file=sys.stderr
        )
    print(
        "\nIf this is a live credential, rotate it out-of-band and remove it — note that "
        "rewriting history does not un-leak it.\n"
        "If it is prose *documenting* a finding, add an entry to ALLOWLIST in "
        "scripts/check_committed_secrets.py keyed on (path, digest) with the reason. "
        "The digest is printed above.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
