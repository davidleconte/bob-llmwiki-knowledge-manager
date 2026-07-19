"""Attestable provenance for pipeline-generated KB documents (ATK-MEM-06).

The delegation pipeline stamps ``trust_tier``/``generated_by``/``source`` into a
document's frontmatter — but plaintext frontmatter is *forgeable*: any
hand-written document can claim ``generated_by: delegation-pipeline`` and be
indistinguishable from a genuine pipeline artifact. This module signs the
provenance with an HMAC-SHA256 over the document's provenance fields plus a
digest of its body, and stores the signature as a ``provenance_sig`` field, so a
forged or tampered document fails verification.

Key resolution (first hit wins):
  1. env var ``MNEMOX_PROVENANCE_KEY`` (used verbatim, UTF-8 encoded)
  2. ``<repo-root>/.bob/provenance.key`` (auto-created 0600, gitignored)

This is a *local integrity* secret, not a public-key identity: it proves a
document was produced by (something holding the key of) this repo's pipeline and
detects tampering. Keep ``.bob/provenance.key`` out of version control.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.kb_paths import repo_root_for

SIG_FIELD = "provenance_sig"
# Provenance fields covered by the signature. ``provenance_sig`` itself is never
# in this list (it would be self-referential); the body is covered via a digest.
_SIGNED_FIELDS = ("trust_tier", "generated_by", "source", "target", "task_id", "type", "status")
_ENV_KEY = "MNEMOX_PROVENANCE_KEY"
_KEY_FILE = "provenance.key"

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_FM_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def key_path(repo_root: Path) -> Path:
    """Location of the repo-local provenance key (``<root>/.bob/provenance.key``)."""
    return repo_root / ".bob" / _KEY_FILE


def load_or_create_key(start_path: Optional[Path] = None) -> bytes:
    """Return the provenance key, creating a repo-local one if none exists.

    ``MNEMOX_PROVENANCE_KEY`` takes precedence so CI / multi-host setups can pin
    a shared key. Otherwise a 256-bit key is generated once at
    ``<repo-root>/.bob/provenance.key`` (mode 0600).
    """
    env = os.environ.get(_ENV_KEY)
    if env:
        return env.encode("utf-8")
    root = repo_root_for(start_path or Path.cwd())
    kp = key_path(root)
    if kp.exists():
        return kp.read_bytes()
    kp.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    kp.write_bytes(key)
    try:
        os.chmod(kp, 0o600)
    except OSError:  # pragma: no cover - best-effort on non-POSIX
        pass
    return key


def _split(markdown: str) -> Tuple[Dict[str, str], str]:
    """Return ``(frontmatter_fields, body)``; empty fields when no frontmatter."""
    m = _FM_RE.match(markdown)
    if not m:
        return {}, markdown
    fields: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        fm = _FM_FIELD_RE.match(line)
        if fm:
            fields[fm.group(1)] = fm.group(2).strip().strip('"').strip("'")
    return fields, m.group(2)


def _canonical_message(fields: Dict[str, str], body: str) -> bytes:
    parts = [f"{k}={fields.get(k, '')}" for k in _SIGNED_FIELDS]
    parts.append("body=" + hashlib.sha256(body.encode("utf-8")).hexdigest())
    return "\n".join(parts).encode("utf-8")


def sign_fields(fields: Dict[str, str], body: str, key: bytes) -> str:
    """HMAC-SHA256 hex signature over the signed provenance fields + body digest."""
    return hmac.new(key, _canonical_message(fields, body), hashlib.sha256).hexdigest()


def attach_signature(markdown: str, key: bytes) -> str:
    """Return *markdown* with a ``provenance_sig`` field added to its frontmatter.

    No-op (returns the input unchanged) if the document has no frontmatter block,
    so an unsignable document is left unsigned rather than silently corrupted.
    """
    fields, body = _split(markdown)
    if not fields:
        return markdown
    sig = sign_fields(fields, body, key)
    # Inject as the last frontmatter field, before the closing fence.
    return markdown.replace("\n---\n", f"\n{SIG_FIELD}: {sig}\n---\n", 1)


_PROMOTED_BY_FIELD = "promoted_by"


def promote_document(markdown: str, to_tier: str, promoter: str, key: bytes) -> str:
    """Promote *markdown* to ``trust_tier: to_tier``, record the promoter, re-sign.

    The ``generated → verified`` path (D2/MEM): flips the tier, records
    ``promoted_by: <promoter>``, strips the now-stale ``provenance_sig``, and
    re-signs so :func:`verify_document` passes for the promoted tier. A forged
    promotion (editing the tier by hand) fails verification because it lacks a
    signature over the new signed fields.

    Raises:
        ValueError: If the document has no frontmatter to promote.
    """
    fields, _ = _split(markdown)
    if not fields:
        raise ValueError("document has no frontmatter to promote")

    md = re.sub(r"^%s:.*\n" % SIG_FIELD, "", markdown, count=1, flags=re.MULTILINE)

    if re.search(r"^trust_tier:.*$", md, flags=re.MULTILINE):
        md = re.sub(r"^trust_tier:.*$", f"trust_tier: {to_tier}", md, count=1, flags=re.MULTILINE)
    else:
        md = md.replace("\n---\n", f"\ntrust_tier: {to_tier}\n---\n", 1)

    if re.search(r"^%s:.*$" % _PROMOTED_BY_FIELD, md, flags=re.MULTILINE):
        md = re.sub(
            r"^%s:.*$" % _PROMOTED_BY_FIELD,
            f"{_PROMOTED_BY_FIELD}: {promoter}",
            md,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        md = md.replace("\n---\n", f"\n{_PROMOTED_BY_FIELD}: {promoter}\n---\n", 1)

    return attach_signature(md, key)


def verify_document(markdown: str, key: bytes) -> bool:
    """True iff *markdown* carries a ``provenance_sig`` that matches its content."""
    fields, body = _split(markdown)
    claimed = fields.get(SIG_FIELD)
    if not claimed:
        return False
    expected = sign_fields(fields, body, key)
    return hmac.compare_digest(claimed, expected)


def authentic_provenance(markdown: str, start_path: Optional[Path] = None) -> bool:
    """High-level check: does this document carry authentic pipeline provenance?

    Resolves the repo-local key and verifies the embedded signature. A forged or
    tampered document — including one that merely *claims*
    ``generated_by: delegation-pipeline`` — returns ``False``.
    """
    return verify_document(markdown, load_or_create_key(start_path))
