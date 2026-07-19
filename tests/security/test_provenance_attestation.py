"""ATK-MEM-06 regression: attestable (unforgeable) pipeline provenance.

Before the fix the pipeline stamped ``trust_tier``/``generated_by``/``source``
as plaintext frontmatter, so any hand-written document could claim
``generated_by: delegation-pipeline``. The HMAC signature makes a forged or
tampered document detectable: it verifies only if it carries a signature that
matches its provenance fields + body under the repo-local key.
"""

from src.delegation.pipeline import _result_to_markdown
from src.provenance import (
    SIG_FIELD,
    attach_signature,
    authentic_provenance,
    load_or_create_key,
    verify_document,
)

KEY = b"test-key-0123456789abcdef0123456789abcdef"

DOC = (
    "---\n"
    'title: "Research Analysis: x"\n'
    "trust_tier: generated\n"
    "generated_by: delegation-pipeline\n"
    "source: delegation-pipeline\n"
    "target: x\n"
    "task_id: t1\n"
    "type: research\n"
    "status: generated\n"
    "---\n\n"
    "# Body\n\nreal generated content\n"
)


def test_signed_document_verifies():
    signed = attach_signature(DOC, KEY)
    assert SIG_FIELD in signed
    assert verify_document(signed, KEY)


def test_forged_provenance_without_signature_fails():
    # A hand-written doc that merely CLAIMS pipeline provenance, unsigned.
    assert not verify_document(DOC, KEY)


def test_tampered_body_fails():
    signed = attach_signature(DOC, KEY)
    tampered = signed.replace("real generated content", "malicious injected content")
    assert not verify_document(tampered, KEY)


def test_tampered_trust_tier_fails():
    # The key attack: promote generated -> verified AFTER signing.
    signed = attach_signature(DOC, KEY)
    tampered = signed.replace("trust_tier: generated", "trust_tier: verified")
    assert not verify_document(tampered, KEY)


def test_wrong_key_fails():
    signed = attach_signature(DOC, KEY)
    assert not verify_document(signed, b"a-completely-different-key")


def test_pipeline_rendered_doc_roundtrips():
    md = _result_to_markdown("task-9", "research", {"finding": "x"}, "targetdir", "2026-07-19")
    assert not verify_document(md, KEY)  # forgeable until signed
    assert verify_document(attach_signature(md, KEY), KEY)


def test_key_file_created_and_reused(tmp_path):
    (tmp_path / ".bob").mkdir()  # marker so repo_root_for resolves here
    k1 = load_or_create_key(tmp_path)
    k2 = load_or_create_key(tmp_path)
    assert k1 == k2 and len(k1) == 32
    assert (tmp_path / ".bob" / "provenance.key").exists()


def test_env_key_takes_precedence(tmp_path, monkeypatch):
    monkeypatch.setenv("MNEMOX_PROVENANCE_KEY", "env-secret")
    assert load_or_create_key(tmp_path) == b"env-secret"
    assert not (tmp_path / ".bob" / "provenance.key").exists()


def test_authentic_provenance_high_level(tmp_path, monkeypatch):
    monkeypatch.setenv("MNEMOX_PROVENANCE_KEY", "env-secret")
    signed = attach_signature(DOC, b"env-secret")
    assert authentic_provenance(signed, start_path=tmp_path)
    assert not authentic_provenance(DOC, start_path=tmp_path)  # forged
