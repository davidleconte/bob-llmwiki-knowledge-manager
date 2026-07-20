"""Governed-memory attestation — the KB's trust posture in one command.

Built directly on the verify-at-read control (ATK-MEM-02): the retrieval read
path (:mod:`src.tools.kb_query`) honours a document's ``trust_tier: verified``
claim *only* when its provenance signature validates
(:func:`src.provenance.verify_document`). This module turns that read-time
decision into an auditable, whole-store report: for every KB document, *would
the read path trust it?* A document that merely **claims** the ``verified`` tier
but whose signature does not validate is **withheld** at read — ``attest``
surfaces exactly those, so the trust layer's posture is provable in one command
rather than inferred from the code.

It is strictly read-only: it never signs, promotes, or edits a document (that is
``kb-promote``'s job). It answers one question — *would retrieval grant this
trust?* — for the whole knowledge base.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.provenance import SIG_FIELD, load_or_create_key, verify_document

# Trust tiers whose trust is load-bearing at read time. Mirrors
# ``src.tools.kb_query._tier_grants_trust``: retrieval grants trust to these
# tiers *only* when the signature verifies; every other tier is served without a
# trust grant (retrievable, but not trusted).
TRUSTED_TIERS = ("verified",)

# Classification outcomes.
AUTHENTIC = "authentic"  # trusted tier + signature verifies  -> honoured at read
WITHHELD = "withheld"  # trusted-tier CLAIM + signature fails -> withheld at read
UNTRUSTED = "untrusted"  # non-trusted tier -> retrievable, not trusted (expected)

# Minimal parse, mirroring kb_query's read-path behaviour EXACTLY so the report
# reflects what retrieval actually sees: a head-only scan (first 4096 chars), the
# same window and strip as ``kb_query._parse_frontmatter_trust_tier``. A whole-body
# scan would false-positive on a ``trust_tier:`` line buried in a doc's prose.
_HEAD_CHARS = 4096
_TRUST_TIER_RE = re.compile(r"^trust_tier:\s*(\S+)", re.MULTILINE)
_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---", re.DOTALL)
_SIG_RE = re.compile(r"^%s:\s*(\S+)" % re.escape(SIG_FIELD), re.MULTILINE)


def _frontmatter(content: str) -> str:
    match = _FRONTMATTER_RE.match(content)
    return match.group(0) if match else ""


def _trust_tier(content: str) -> str:
    """Trust tier as the read path reads it — head-only scan, kb_query parity."""
    match = _TRUST_TIER_RE.search(content[:_HEAD_CHARS])
    return match.group(1).strip().strip('"').strip("'") if match else "unset"


def _has_signature(content: str) -> bool:
    return bool(_SIG_RE.search(_frontmatter(content)))


@dataclass(frozen=True)
class DocAttestation:
    """The read-time trust verdict for a single KB document."""

    path: str
    trust_tier: str
    has_signature: bool
    verified: bool
    status: str  # AUTHENTIC | WITHHELD | UNTRUSTED


def classify_document(content: str, key: bytes, path: str = "") -> DocAttestation:
    """Classify one document's read-time trust posture.

    A ``verified`` claim is AUTHENTIC only when :func:`verify_document` passes;
    otherwise it is WITHHELD (the read path replaces its content). Any other tier
    is UNTRUSTED — retrievable and expected, not a security concern.
    """
    tier = _trust_tier(content)
    verified = verify_document(content, key)
    if tier in TRUSTED_TIERS:
        status = AUTHENTIC if verified else WITHHELD
    else:
        status = UNTRUSTED
    return DocAttestation(
        path=path,
        trust_tier=tier,
        has_signature=_has_signature(content),
        verified=verified,
        status=status,
    )


def attest_kb(
    kb_path: Path, key: Optional[bytes] = None, *, include_documents: bool = True
) -> Dict[str, object]:
    """Attest the trust posture of every Markdown document under ``kb_path``.

    Returns a summary: totals per status, the security-relevant list of
    *withheld* documents (claim ``verified`` but fail verification), and — unless
    ``include_documents=False`` — the per-document verdicts.
    """
    if key is None:
        key = load_or_create_key(kb_path)
    docs: List[DocAttestation] = []
    for markdown in sorted(kb_path.rglob("*.md")):
        try:
            content = markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        docs.append(classify_document(content, key, str(markdown.relative_to(kb_path))))

    withheld = [d.path for d in docs if d.status == WITHHELD]
    summary: Dict[str, object] = {
        "kb_path": str(kb_path),
        "total": len(docs),
        "authentic": sum(1 for d in docs if d.status == AUTHENTIC),
        "withheld": len(withheld),
        "untrusted": sum(1 for d in docs if d.status == UNTRUSTED),
        "withheld_docs": withheld,
        "trusted_tiers": list(TRUSTED_TIERS),
    }
    if include_documents:
        summary["documents"] = [asdict(d) for d in docs]
    return summary


def format_attestation(report: Dict[str, object]) -> str:
    """Human-readable, one-screen attestation summary for the CLI / demo."""
    lines = [
        f"Governed-memory attestation — {report['kb_path']}",
        f"  documents attested                              : {report['total']}",
        f"  authentic  (trusted tier, signature verified)   : {report['authentic']}",
        f"  untrusted  (not a 'verified' claim; retrievable): {report['untrusted']}",
        f"  WITHHELD   (claims 'verified', signature fails)  : {report['withheld']}",
    ]
    withheld = report.get("withheld_docs") or []
    if isinstance(withheld, list) and withheld:
        lines.append("  withheld at read (forged / unsigned 'verified' claims):")
        lines.extend(f"    - {path}" for path in withheld)
    else:
        lines.append("  OK  every 'verified' document is authentically signed — no forged trust claims")
    return "\n".join(lines)
