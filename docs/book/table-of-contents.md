# Mnemox — The Complete Guide

**A long-form narrative on giving IBM Bob a memory: token optimization, a
git-versioned knowledge base, and the measurement discipline that keeps both honest.**

**Status:** Live · **Last updated:** 2026-07-25 · Maturity: [`STATUS.md`](../../STATUS.md)

---

## How to read this

This guide is the *narrative* layer. It explains why the system is shaped the way it
is, in the order a newcomer would want it. It is not the system of record:

| For… | Go to |
|---|---|
| The authoritative architecture | [`docs/architecture/ARCHITECTURE.md`](../architecture/ARCHITECTURE.md) |
| Precise API signatures | [`docs/api/`](../api/README.md) — generated from source, CI-pinned |
| Current maturity, coverage, grades | [`STATUS.md`](../../STATUS.md) — the single home |
| A specific task | [`docs/README.md`](../README.md) — the Diátaxis index |

Where this guide and any of those disagree, **they win** and this is the bug.

> **Provenance note (2026-07-25).** This guide previously lived under `docs/archive/`
> and shipped a table of contents promising **34 chapters and 8 appendices** — a
> writing plan that was never executed. Nine chapters and three appendices were
> actually written; from chapter 5 onward the promised titles did not match the files,
> so the book contained two contradictory tables of contents. It also carried figures
> the project had already retracted. This page now describes **what exists**. The
> abandoned outline is preserved in git history
> (`git show 5d7b799:docs/archive/book-table-of-contents.md`).

---

## Part I — The problem and the pattern

### [Chapter 1: The Problem We're Solving](chapter-01.md)
Why re-derivation, not prompt length, is the recurring cost. What a finite shared
budget does to the questions a team is willing to ask.

### [Chapter 2: What Mnemox Is](chapter-02.md)
The two independently-operable systems in this repository — the Bash knowledge
manager and the Python token-optimization sidecar — and why they are not one system.

## Part II — The token-optimization system

### [Chapter 3: Understanding Token Optimization](chapter-03.md)
Compression, cache recompute-avoidance and truncation as three *separately measured*
mechanisms, and why blending them is how a fabricated headline gets made.

### [Chapter 4: Multi-Level Caching Architecture](chapter-04.md)
L1 exact, L2 semantic, optional L3 persistent. Why L3 hits are not promoted into L2.

## Part III — The knowledge base

### [Chapter 5: Knowledge Base Framework](chapter-05.md)
Document types, templates, cross-referencing, and the index that ties them together.

### [Chapter 6: Real-World Example — HCD Repository Analysis](chapter-06.md)
The first production use, and what it did and did not demonstrate.

## Part IV — Evidence and honesty

### [Chapter 7: Test Results and Validation](chapter-07.md)
The manifest-backed harness, the null test, and the held-out corpus.

### [Chapter 8: Getting Started Guide](chapter-08.md)
Installation, first session, and the daily loop.

### [Chapter 9: Honest Assessment and Production Readiness](chapter-09.md)
What is claimed, what is not, and the retraction record.

## Part V — The modern system *(added 2026-07-25)*

### [Chapter 10: Retrieval — Embeddings, Graph, and What It Actually Buys](chapter-10.md)
The P2 embedding index and P3 knowledge graph, and the honest result: at keyword
parity on the shipped backend.

### [Chapter 11: Trust at the Read Boundary](chapter-11.md)
Provenance signing, trust tiers, input bounds, and path containment — what each
control does and what it deliberately does not do.

### [Chapter 12: The Honesty Gates](chapter-12.md)
The gate system, why every gate carries a test that proves it can fail, and the blind
spots a 2026-07-25 audit found in gates that were passing green.

---

## Appendices

### [Appendix A: API Reference](appendix-a.md)
Redirect. The API reference is generated from source and CI-pinned at
[`docs/api/`](../api/README.md).

### [Appendix B: Configuration Reference](appendix-b.md)
Configuration schema and precedence.

### [Appendix C: Template Reference](appendix-c.md)
The four KB document templates.

---

## Scope, stated plainly

- **12 chapters, 3 appendices** — roughly 60–70 printed pages. Earlier drafts claimed
  "400+ pages"; that was an 8–10× overstatement of a document that has never been
  that long.
- Chapters 1–9 were written mid-2026 and describe the system as it stood then;
  chapters 10–12 cover the subsystems added since. Where an older chapter is
  superseded, it says so inline rather than being silently patched.
- Every number in this guide either cites a manifest or is labelled as unbacked. The
  savings and metric gates scan `docs/**`, so this directory is now in their scope —
  which is the point of moving it out of `docs/archive/`.
