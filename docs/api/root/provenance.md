# provenance

Attestable provenance for pipeline-generated KB documents (ATK-MEM-06).

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

## Constants

- `SIG_FIELD`
- `_SIGNED_FIELDS`
- `_ENV_KEY`
- `_KEY_FILE`
- `_FM_RE`
- `_FM_FIELD_RE`

## Functions

### `key_path(repo_root: Path) -> Path`

Location of the repo-local provenance key (``<root>/.bob/provenance.key``).


### `load_or_create_key(start_path: Optional[Path]) -> bytes`

Return the provenance key, creating a repo-local one if none exists.

``MNEMOX_PROVENANCE_KEY`` takes precedence so CI / multi-host setups can pin
a shared key. Otherwise a 256-bit key is generated once at
``<repo-root>/.bob/provenance.key`` (mode 0600).


### `_split(markdown: str) -> Tuple[Dict[str, str], str]`

Return ``(frontmatter_fields, body)``; empty fields when no frontmatter.


### `_canonical_message(fields: Dict[str, str], body: str) -> bytes`


### `sign_fields(fields: Dict[str, str], body: str, key: bytes) -> str`

HMAC-SHA256 hex signature over the signed provenance fields + body digest.


### `attach_signature(markdown: str, key: bytes) -> str`

Return *markdown* with a ``provenance_sig`` field added to its frontmatter.

No-op (returns the input unchanged) if the document has no frontmatter block,
so an unsignable document is left unsigned rather than silently corrupted.


### `verify_document(markdown: str, key: bytes) -> bool`

True iff *markdown* carries a ``provenance_sig`` that matches its content.


### `authentic_provenance(markdown: str, start_path: Optional[Path]) -> bool`

High-level check: does this document carry authentic pipeline provenance?

Resolves the repo-local key and verifies the embedded signature. A forged or
tampered document — including one that merely *claims*
``generated_by: delegation-pipeline`` — returns ``False``.

