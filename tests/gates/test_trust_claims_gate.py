"""Audit-2026-07-25: a claimed `trust_tier: verified` must carry a signature.

ATK-MEM-02's forgery is not cryptographic — it is typing four words into a document's
frontmatter to borrow authority the document was never granted. The read path was fixed
to verify signatures, but nothing stopped an unsigned tier claim from being *written*,
and `attest` reported exactly one such document sitting in the tree.

These tests pin the keyless structural check. They deliberately do **not** test
signature validity: that is HMAC-keyed on a gitignored secret, so it is verifiable
where the key lives and nowhere else — see the module docstring of
`scripts.check_trust_claims` for why that split is the honest one.
"""

from scripts.check_trust_claims import claims_verified, frontmatter, has_signature

SIG = "a" * 64


def _doc(front: str, body: str = "\nbody text\n") -> str:
    return f"---\n{front}\n---\n{body}"


# ── The forgery the gate exists to catch ─────────────────────────────────────────


def test_unsigned_verified_claim_is_a_forgery():
    doc = _doc("title: x\ntrust_tier: verified")
    assert claims_verified(doc) and not has_signature(doc)


def test_signed_verified_claim_passes():
    doc = _doc(f"title: x\ntrust_tier: verified\nprovenance_sig: {SIG}")
    assert claims_verified(doc) and has_signature(doc)


def test_quoted_tier_value_is_still_a_claim():
    """`trust_tier: "verified"` must not slip past on quoting alone."""
    assert claims_verified(_doc('trust_tier: "verified"'))


# ── Things that must never be flagged ────────────────────────────────────────────


def test_other_tiers_are_not_claims():
    for tier in ("generated", "quarantined", "archived"):
        assert not claims_verified(_doc(f"trust_tier: {tier}"))


def test_document_without_frontmatter_is_ignored():
    assert frontmatter("just prose\n") == ""
    assert not claims_verified("just prose\n")


def test_fenced_example_in_the_body_is_not_a_claim():
    """Documentation showing the syntax must not trip the gate — the check is scoped
    to the frontmatter block, not the whole file."""
    doc = _doc("title: x", "\n```yaml\ntrust_tier: verified\n```\n")
    assert not claims_verified(doc)


def test_malformed_signature_does_not_count():
    """A short or non-hex value is not a signature; accepting it would make the gate
    satisfiable by typing `provenance_sig: yes`."""
    for bad in ("abc", "not-a-signature", "", "zzzz" * 16):
        assert not has_signature(_doc(f"trust_tier: verified\nprovenance_sig: {bad}"))


# NOTE: the assertion that the *live tree* has no unsigned trust claims lives in
# the claim-surface PR — that is the PR which promotes (and thereby signs) the one
# document `attest` was withholding. This file tests the detector.


# ── The live tree (this PR promotes the one document that was withheld) ──────────


def test_live_tree_has_no_unsigned_trust_claims():
    """The condition the audit found violated: one document claimed the verified tier
    with nothing backing it, and `attest` withheld it at read. This PR promotes it
    through `kb-promote`, which signs it — so the claim is now backed rather than the
    tier being hand-edited away."""
    from scripts.check_trust_claims import unsigned_trust_claims

    bad = unsigned_trust_claims()
    assert bad == [], "unsigned `trust_tier: verified` claims: " + ", ".join(bad)
