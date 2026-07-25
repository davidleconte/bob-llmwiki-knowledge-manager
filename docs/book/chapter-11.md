# Chapter 11: Trust at the Read Boundary

> **Live document.** This chapter is part of [Mnemox — The Complete Guide](table-of-contents.md). Numbers here cite a manifest or say they do not; [`STATUS.md`](../../STATUS.md) is the single home for maturity, coverage and test counts. Chapters 1–9 were written mid-2026 — where a chapter predates a subsystem, chapters 10–12 cover it.

*Added 2026-07-25. Chapters 1–9 predate every control in this chapter.*

A git-versioned Markdown knowledge base has an obvious property: anything that can write
a file can write a *memory*. That is the substrate's great strength — it is reviewable,
diffable, and yours — and it is also the attack surface. This chapter covers what the
project does about it, and is equally careful about what it does not.

## 11.1 The threat, stated plainly

The knowledge base is auto-loaded into sessions. So a document is not inert data; it is
text that will be read by a model and acted on. Three consequences:

- **Indirect prompt injection.** A KB document containing instructions is a way to
  address the model without going through the user (ATK-MEM-01).
- **Forged authority.** If the retrieval layer trusts a `trust_tier: verified` field,
  then writing that field *is* becoming trusted (ATK-MEM-02).
- **Path escape.** A retrieval path that resolves caller-supplied paths can be walked
  outside the KB to read arbitrary files (ATK-FS-01).

The full analysis is [`docs/security/threat-model.md`](../security/threat-model.md).

## 11.2 Verify at read, not at write

The control that matters most is the smallest to state:

> The retrieval read path verifies a provenance signature **before** honouring
> `trust_tier: verified`. A document that claims the tier without a valid signature is
> **withheld** — its content is not returned.

`src/provenance.py` implements HMAC-SHA256 signing and `verify_document`; the read path
in `src/tools/kb_query.py` calls it.

The interesting part is the bug this replaced. Verification *existed* before — but it
was wired only into the **promotion** path, the moment a document was blessed. The read
path took `trust_tier` straight from frontmatter. So the check ran at the one moment a
human was already involved, and never at the moment it mattered. Writing seven characters
into a YAML block was enough to be trusted.

That is a general lesson worth more than the specific fix: **a control placed where the
honest path flows is not a control.** It has to sit where the attack lands.

## 11.3 What `attest` reports today

`bob-optimize attest` makes the trust posture inspectable in one command:

```
documents attested                              : 118
authentic  (trusted tier, signature verified)   : 1
untrusted  (not a 'verified' claim; retrievable): 117
WITHHELD   (claims 'verified', signature fails) : 0
```

Read the 117 honestly: `untrusted` is not a failure state, it is the **default**. Those
documents make no trust claim, and they remain retrievable on their own merits. The tier
is for content someone deliberately vouched for.

For most of this project's life the first line read `0 authentic` and the last read
`1 WITHHELD` — the control was enforced while governing nothing, because one document had
simply had `trust_tier: verified` typed into its frontmatter. The fix was to promote it
through `kb-promote`, which signs it, rather than to delete the claim: deleting would have
made the number look right without making anything true.

Two things still worth saying plainly. **The signature detects tampering; it does not
vouch for content** — review every KB document like code. And **CI cannot verify
signatures at all**: the scheme is HMAC-keyed on a local secret, so a runner without the
key would report every signed document as forged. CI runs the keyless structural check
instead — that a claimed tier carries a signature — which is exactly the forgery that
matters. A security control described by its design rather than its current effect is how
a project ends up believing it is protected.

## 11.4 Input bounds

`src/limits.py` is the single home for four ceilings:

| Constant | Bounds |
|---|---|
| `MAX_FILE_BYTES` | index ingest — skip files larger than this |
| `MAX_CHUNKS_PER_DOC` | chunker — cap chunks from one document |
| `MAX_QUERY_CHARS` | query entry — truncate longer queries |
| `MAX_GRAPH_NODES` | graph builder — stop admitting nodes past this |

They are *imported* at every enforcement point and never re-declared as literals, and
their values are restated in the CODEOWNERS-reviewed `config/gates/gate-config.yaml` so
that weakening one is conspicuous in review. `scripts/check_value_homes.py` fails CI if
the two ever disagree.

This is the "one home per value" discipline applied to a security parameter: the risk is
not that someone lowers a cap maliciously, it is that a cap gets duplicated and the two
copies drift until nobody knows which one is live.

## 11.5 Path containment

`src/tools/safe_paths.py:resolve_within` is the single place the tool layer resolves a
caller-supplied path against an allowed root. `batch_file_reader` and
`component_analyzer` both route through it.

Note the shape of `analyze --allow-external`: it **rebases** the containment root rather
than disabling the check. There is no code path where containment is off — only paths
where the root is different. A flag that turns a security control off tends to end up on.

## 11.6 What this is *not*

Stated as flatly as the rest, because the gap between a control and its marketing is
where security debt accumulates:

- **The provenance key is a local integrity secret** (`.bob/provenance.key`, gitignored).
  It proves a document came from something holding this repository's key and detects
  tampering afterwards. It is **not** a public-key identity, and it does not tell you
  *which* person or process signed.
- **This is not a multi-tenant trust boundary.** Do not run Mnemox against secrets, or
  as the isolation layer between mutually distrusting users.
- **A reviewed pull-request workflow is still the primary control** for KB changes. The
  signature detects tampering; human review is what decides whether the content should
  have been written at all.

---

**Next:** [Chapter 12 — The Honesty Gates](chapter-12.md)
