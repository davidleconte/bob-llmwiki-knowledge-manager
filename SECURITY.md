# Security Policy

## Supported versions

This project follows semantic versioning. Security fixes are applied to the
latest released minor line.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

The current version is defined once, in [`pyproject.toml`](pyproject.toml)
(`project.version`), and enforced against its mirrors by
`scripts/check_value_homes.py`.

## What this project is (scope framing)

`bob-llmwiki-knowledge-manager` ships a **local Python library and CLI**
(`bob-optimize` / `python -m src`) for token optimization — caching, prompt
optimization, and truncation — plus a set of local knowledge-base tooling
scripts. It is **not** a hosted or multi-tenant network service: it opens no
listening socket, stores no credentials, and makes no outbound network calls
except two optional first-use downloads:

- **tiktoken BPE vocabulary** (`src/optimizer/token_counter.py:38-46`) — fetched
  on first token-count if absent from the local tiktoken cache.
- **`sentence-transformers/all-MiniLM-L6-v2` model** (`src/cache/embeddings.py:49`)
  — fetched once (~22 MB, cached to `~/.cache/huggingface/`) **only** when
  `EmbeddingGenerator(backend="minilm")` is called with `[mlx]` installed.
  Never triggered by default configuration, by CI, or by any code path that uses
  the default `"hashing"` backend. No API key required; the model is public.

The realistic threat surface is therefore local — see the full analysis in
[`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md).

## Reporting a vulnerability

**Please report security issues privately — do not open a public issue.**

Use GitHub's **Private Vulnerability Reporting**:

1. Go to the repository's **Security** tab:
   <https://github.com/davidleconte/bob-llmwiki-knowledge-manager/security/advisories>
2. Click **Report a vulnerability**.
3. Describe the issue, the affected version/commit, and reproduction steps
   (a minimal proof-of-concept helps a lot).

This routes the report to the maintainers privately and lets us coordinate a
fix and, if warranted, a published advisory.

### In scope

- Path handling in the tool layer (`src/tools/`) and anything reachable
  through the `bob-optimize` / `python -m src` CLI.
- Untrusted-input handling in config loading (`src/config/`) and the
  optimizer/cache/truncation pipeline.
- Dependency vulnerabilities surfaced by our SBOM / `pip-audit` supply-chain
  tooling.

### Out of scope

- Denial of service from deliberately oversized local input (documented as an
  accepted residual risk in the threat model — this is a local CLI).
- The retracted, never-implemented security architecture described in
  `docs/adr/012-security-model.md` (superseded; see its banner). It documents
  no shipping code, so it has no exploitable surface.
- Findings that require the operator to already have shell/filesystem access
  equivalent to the tool's own (the tool runs with the invoking user's
  privileges by design).

## Response targets

These are good-faith targets for a small open-source project, not contractual
guarantees:

| Stage                      | Target                     |
| -------------------------- | -------------------------- |
| Acknowledge receipt        | within 5 business days     |
| Initial assessment / triage| within 10 business days    |
| Fix or mitigation plan     | communicated after triage  |

We practice **coordinated disclosure**: we ask that you give us a reasonable
window to ship a fix before any public write-up, and we will credit reporters
who wish to be named.

## Safe harbor

We will not pursue or support legal action against researchers who, in good
faith, discover and report vulnerabilities in accordance with this policy,
provided they avoid privacy violations, data destruction, and service
disruption, and do not access more data than necessary to demonstrate the
issue.
