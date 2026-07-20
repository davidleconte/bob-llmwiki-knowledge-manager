# Security Policy

## Supported versions

This project follows semantic versioning. Security fixes are applied to the
latest released minor line.

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |
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
[`docs/security/threat-model.md`](docs/security/threat-model.md).

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

## Program Gate

No Critical or High audit finding is marked closed until:

1. Its adversarial regression test exists in `tests/security/`, `tests/gates/`, or `tests/retrieval/`.
2. The test **passes** on the fixed tree.
3. The test is **verified to fail** on the unfixed tree — revert the fix in a
   throwaway branch and run `uv run pytest tests/security/ -v` to confirm red.

The `adversarial-regression` CI job (`.github/workflows/ci.yml`) runs all security,
gate, and retrieval tests on every PR. Tests marked `@pytest.mark.planted_defect` are
excluded from CI — they serve as proof-of-exploit documentation and are run manually
to demonstrate the red→green transition that closes a finding.

Source audits:
- Red-team adversarial audit: `docs/knowledge-base/research/adversarial-audit-2026-07-19.md`
- Counter-audit (MECE, scored 2.9/5): `docs/knowledge-base/research/counter-audit-2026-07-19-independent.md`
- Remediation plan: `docs/project-management/plans/adversarial-remediation-plan.md`

## Gate Independence

The honesty gates (savings, metric-claim, value-homes, status/grade-provenance,
coverage, API-doc freshness, KB integrity) are authored and maintained by a single
owner (`@davidleconte`), who also authors the code and the claims those gates check.
This is **bus-factor 1**: absent a second reviewer, nothing structurally stops the
same actor from weakening a gate and, in the same change, planting a claim the gate
would otherwise have caught (ATK-GATE-07).

Because a second *required human* reviewer is not currently staffed, the honest
substitute is a **structural CI check** — `scripts/check_gate_integrity.py`, run by
the `gate integrity (ATK-GATE-07)` job on every pull request:

- It **fails any PR whose diff touches BOTH a gate definition and a claim surface.**
  - Gate definitions: `config/gates/**`, `scripts/check_*.py`, `src/validation/**`.
  - Claim surfaces: `STATUS.md`, `README.md`, `docs/**` (except the generated
    `docs/api/**`, which the API-doc freshness gate already pins to `src/`).
- A gate-only PR (tightening a check) and a claim-only PR (updating a doc) each
  pass; only their **combination** in one PR is blocked. To land a change that
  genuinely needs both, split it: land the gate change in its own PR first, where it
  is independently reviewable, then update the claim in a follow-up PR.

This mechanically forbids the single-PR "weaken the gate + plant the overclaim"
attack without a second human. It does **not** eliminate the single-owner risk — a
determined owner can still land two sequential PRs. That residual is **disclosed
here, not silently accepted**; the standing invitation below is the path to closing
it.

**Standing invitation.** An independent reviewer for `config/gates/**` and
`scripts/check_*.py` is welcome. Onboarding one adds a second `CODEOWNERS` entry for
those paths and upgrades this structural check from a *substitute* to a *backstop*.
Contact via the channel in §Reporting a vulnerability.

