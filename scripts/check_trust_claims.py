#!/usr/bin/env python3
"""Every ``trust_tier: verified`` document must carry a provenance signature field.

Why this gate exists, and why it is *not* ``attest --strict``
-------------------------------------------------------------
The provenance scheme is HMAC-SHA256 keyed on ``.bob/provenance.key``, which is
gitignored because it is a secret. That has a consequence worth stating plainly rather
than discovering later: **cryptographic verification is impossible on a CI runner**
without provisioning the key as a CI secret, which would spread it to every job and
every fork. ``bob-optimize attest --strict`` therefore belongs on a developer machine
or a trusted release host, not in this workflow — running it in CI would report every
signed document as forged, because CI cannot recompute the MAC.

What *is* checkable without the key is the structural half, and it happens to be the
half that catches the actual attack. The threat (ATK-MEM-02) is someone typing
``trust_tier: verified`` into a document's frontmatter to borrow authority they were
never granted. That forgery is visible with no secret at all: the tier is claimed and
no ``provenance_sig`` accompanies it. Only *tamper-after-sign* — editing a document
that was legitimately signed — needs the key to detect, and that is caught at read time
in the process that holds it.

So this gate is deliberately the weaker of the two checks, run where it can actually
run, and it says so rather than implying CI is verifying signatures.

Usage::

    python scripts/check_trust_claims.py
    python scripts/check_trust_claims.py --selftest
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = "docs/knowledge-base"

# Frontmatter only: a fenced example inside the body must not trip the gate.
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TRUSTED_TIER_RE = re.compile(r"^trust_tier:\s*[\"']?verified\b", re.MULTILINE)
SIGNATURE_RE = re.compile(r"^provenance_sig:\s*[0-9a-fA-F]{32,}\s*$", re.MULTILINE)


def frontmatter(text: str) -> str:
    """The YAML frontmatter block, or '' when the document has none."""
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def claims_verified(text: str) -> bool:
    return bool(TRUSTED_TIER_RE.search(frontmatter(text)))


def has_signature(text: str) -> bool:
    return bool(SIGNATURE_RE.search(frontmatter(text)))


def unsigned_trust_claims(repo_root: Path | None = None) -> list[str]:
    """Documents claiming the verified tier with no signature field to back it."""
    root = repo_root or REPO_ROOT
    kb = root / KB_ROOT
    if not kb.exists():
        return []
    bad: list[str] = []
    for path in sorted(kb.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if claims_verified(text) and not has_signature(text):
            bad.append(path.relative_to(root).as_posix())
    return bad


def _selftest() -> int:
    """Prove the detector separates a forged tier claim from a signed one."""
    signed = "---\ntitle: x\ntrust_tier: verified\nprovenance_sig: " + "a" * 64 + "\n---\n\nbody\n"
    forged = "---\ntitle: x\ntrust_tier: verified\n---\n\nbody\n"
    plain = "---\ntitle: x\ntrust_tier: generated\n---\n\nbody\n"
    none = "no frontmatter here\n"
    # A fenced code sample showing the syntax must not count as a claim.
    in_body = "---\ntitle: x\n---\n\n```yaml\ntrust_tier: verified\n```\n"

    failures: list[str] = []
    if not (claims_verified(signed) and has_signature(signed)):
        failures.append("signed document should read as claimed+signed")
    if not (claims_verified(forged) and not has_signature(forged)):
        failures.append("MISSED: a forged tier claim must be detected")
    if claims_verified(plain) or claims_verified(none):
        failures.append("FALSE POSITIVE: non-verified tiers must not be flagged")
    if claims_verified(in_body):
        failures.append("FALSE POSITIVE: a fenced example is not a frontmatter claim")
    # A too-short/garbage signature must not satisfy the check.
    if has_signature("---\ntrust_tier: verified\nprovenance_sig: abc\n---\n"):
        failures.append("FALSE NEGATIVE: a malformed signature must not count")

    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("Self-test passed: forged tier claim caught; signed/plain/fenced cases clean.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="verify the detector can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    bad = unsigned_trust_claims()
    if not bad:
        print(
            "Every 'trust_tier: verified' document carries a provenance signature.\n"
            "NOTE: this is the keyless structural check. Cryptographic verification "
            "needs .bob/provenance.key and runs as `bob-optimize attest --strict` where "
            "the key exists — not in CI."
        )
        return 0

    print("Checking that every claimed 'verified' trust tier is backed by a signature:\n")
    for rel in bad:
        print(f"  UNSIGNED  {rel}")
    print(
        f"\nFAILED: {len(bad)} document(s) claim `trust_tier: verified` with no "
        "`provenance_sig` to back it.\n"
        "Typing the tier into frontmatter is how a document borrows authority it was "
        "never granted (ATK-MEM-02). Promote it properly instead — "
        "`bob-optimize kb-promote <doc> --to verified` signs it — or drop the claim.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
