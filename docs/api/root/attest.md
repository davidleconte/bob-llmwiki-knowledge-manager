# attest

Governed-memory attestation — the KB's trust posture in one command.

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

## Constants

- `TRUSTED_TIERS`
- `AUTHENTIC`
- `WITHHELD`
- `UNTRUSTED`
- `_HEAD_CHARS`
- `_TRUST_TIER_RE`
- `_FRONTMATTER_RE`
- `_SIG_RE`

## Functions

### `_frontmatter(content: str) -> str`


### `_trust_tier(content: str) -> str`

Trust tier as the read path reads it — head-only scan, kb_query parity.


### `_has_signature(content: str) -> bool`


### `classify_document(content: str, key: bytes, path: str) -> DocAttestation`

Classify one document's read-time trust posture.

A ``verified`` claim is AUTHENTIC only when :func:`verify_document` passes;
otherwise it is WITHHELD (the read path replaces its content). Any other tier
is UNTRUSTED — retrievable and expected, not a security concern.


### `attest_kb(kb_path: Path, key: Optional[bytes]) -> Dict[str, object]`

Attest the trust posture of every Markdown document under ``kb_path``.

Returns a summary: totals per status, the security-relevant list of
*withheld* documents (claim ``verified`` but fail verification), and — unless
``include_documents=False`` — the per-document verdicts.


### `format_attestation(report: Dict[str, object]) -> str`

Human-readable, one-screen attestation summary for the CLI / demo.


## Classes

### `DocAttestation`

The read-time trust verdict for a single KB document.

