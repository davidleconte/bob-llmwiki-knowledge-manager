---
name: kb-optimizer-integration
description: >
  Opt-in Token Optimization System compression for Knowledge Base context
  assembled in the knowledge-manager mode. Provides the exact subprocess
  pattern, fallback contract, and preserve_structure requirement.
---

# KB Optimizer Integration Skill

## Purpose

When the `knowledge-manager` mode assembles a KB context block for LLM injection,
this skill describes how to optionally compress it using the Token Optimization
System CLI (`bob-optimize`). This is purely opt-in: if `bob-optimize` is not in
`PATH`, skip silently. KB retrieval is **never blocked** by compression failure.

## Prerequisites

- `bob-optimize` installed: `pip install -e ".[dev,monitoring]"` from repo root
- Installed at: `/path/to/bob-llmwiki-knowledge-manager`
- Verify: `bob-optimize --help` should print usage without error

## Subprocess Pattern

```bash
# Compress KB context (opt-in; skip silently if bob-optimize unavailable)
KB_CONTEXT="... assembled retrieval context ..."

if command -v bob-optimize &>/dev/null; then
  compressed=$(echo "$KB_CONTEXT" \
    | bob-optimize optimize - --json \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['optimized_text'])" \
    2>/dev/null)
  # Fall back to original if compression fails or returns empty
  KB_CONTEXT="${compressed:-$KB_CONTEXT}"
fi
```

## Rules

1. **preserve_structure is implicit** — the optimizer's default `semantic` strategy
   preserves document structure. Do NOT pass `--strategy lossy` on KB content.
2. **Failure is silent** — a non-zero exit from `bob-optimize` or a parse error in
   the JSON must not propagate. Always fall back to `$KB_CONTEXT`.
3. **Never compress individual KB documents** — only compress assembled *context
   blocks* that will be injected into a prompt. Compressing the stored document
   corrupts the knowledge base.
4. **Expected benefit** — ~20% token reduction on retrieved context
   (manifest-backed: `evaluation/results/validation-2026-07-14/`).

## When NOT to Use

- When `bob-optimize` is not installed (skip silently, as above)
- When the context block is already under 200 tokens (not worth the subprocess overhead)
- When the retrieval result is a code snippet that must be reproduced verbatim

## Related

- ADR-014: `docs/adr/014-kb-query-embedding-scorer.md`
- Integration roadmap P1-3: `docs/knowledge-base/guides/kb-tos-integration-roadmap.md`
- INTEGRATIONS.md §4: `INTEGRATIONS.md`
