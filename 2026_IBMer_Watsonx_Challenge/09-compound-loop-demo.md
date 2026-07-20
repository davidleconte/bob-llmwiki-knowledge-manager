# Compound-Loop Demo — write once, retrieve forever (with live Bobcoin counter)

> Companion to [`06-demo-script.md`](./06-demo-script.md). That one is the 90-second
> zero-install pitch; **this** is the ~2-minute "compounding proof" cut — the beat that
> shows *why* the bill falls: Bob writes a hard-won insight **once**, and a later cold
> session **retrieves** it instead of re-deriving it. It ends on the governance angle
> (`attest`) — memory you can *prove*, not just store.
>
> **Every number spoken here is one a judge can reproduce on camera.** No ≈60% extrapolation,
> no headline the repo can't back. See the honesty box at the bottom.

## Setup (off camera)

- A repo open in **Bob IDE** with a populated `docs/knowledge-base/`.
- A terminal ready (for the live counter + `attest`), font large enough to read.
- Pick one **compact summary** + the **source it replaces** for the counter, e.g.
  `docs/knowledge-base/concepts/multi-level-caching.md` ← `src/cache/multi_level_cache.py src/cache/semantic_cache.py`.

## The script

**[0:00–0:15] The re-derivation tax (to camera)**
> "Every Bob session starts amnesiac — it re-reads your repo and re-answers last week's
> question, and you pay Bobcoins to relearn what Bob already knew. Watch what memory does to that."

**[0:15–0:35] Session 1 — write the insight once (screen: Knowledge Manager mode)**
> "Session one: Bob works out something non-trivial — how the multi-level cache evicts — and
> instead of letting it evaporate at the end of the thread, it *files* it."
*(Show the KB doc / the commit. One sentence:)*
> "That's a git commit. Version-controlled, diffable, and now shared with the whole team."

**[0:35–1:00] Session 2 — cold, retrieves instead of re-deriving (screen: NEW session)**
Type verbatim:
> `How does the multi-level cache evict, and why is L2 O(1)?`

As Bob answers:
> "Brand-new session — no memory of session one. But notice what *didn't* happen: Bob didn't
> re-read the source tree. It retrieved the summary we filed. Same answer, a fraction of the context."

**[1:00–1:25] The live Bobcoin counter (screen: terminal)**
Run verbatim:
```bash
python 2026_IBMer_Watsonx_Challenge/bobcoin_counter.py \
  --source src/cache/multi_level_cache.py src/cache/semantic_cache.py \
  --summary docs/knowledge-base/concepts/multi-level-caching.md
```
> "These are *real token counts*, from the same tokenizer our measurement harness uses.
> Re-deriving from source costs this many Bobcoins; retrieving the summary costs this many.
> The meter is the gap — for this document. That's the mechanism: retrieval, not re-derivation."

**[1:25–1:45] The honest headline (screen: report.json or the impact slide)**
> "Across 183 real documents, measured, manifest-backed, and null-tested: 20% mean token
> compression. And the developer-velocity number — the controlled before/after — we're
> measuring with a pre-registered A/B harness that refuses to report below five valid tasks.
> We publish the method, not a flattering guess."

**[1:45–2:00] Governance: memory you can prove (screen: terminal)**
Run verbatim:
```bash
bob-optimize attest --kb-path docs/knowledge-base
```
> "Last thing. This memory is an instruction channel, so trust has to be *earned*. `attest`
> checks every document: a fact that merely *claims* to be verified but isn't cryptographically
> signed is **withheld** at read. Governed memory — signed, attributable, verified. That's the
> part that makes it safe to compound."

**[2:00 close, to camera]**
> "Bob-native, one click to adopt, it compounds every session — and it refuses to overclaim its
> own savings. That last part is the point."

## Numbers you may say (and the ones you may not)

| ✅ Say | Basis |
|---|---|
| "20% mean token compression, N=183, 95% CI [18.9, 21.2], null-tested" | `evaluation/results/validation-2026-07-14/report.json` |
| The live counter's re-derive vs retrieve tokens **for the shown document** | `bob-optimize count` reproduces it |
| "a forged 'verified' fact is withheld at read" | `tests/test_attest.py`, `tests/security/` |
| "the velocity number is measured with a pre-registered A/B harness" (in progress) | `evaluation/velocity/`, `src/velocity.py` |

| ❌ Do not say | Why |
|---|---|
| "~60% Bobcoin reduction" | Extrapolation with **no repo artifact** — replace with the measured A/B number once `evaluation/results/velocity-ab-<date>/` exists |
| the counter's % as a **headline** savings figure | It's per-document mechanism illustration, not the aggregate metric |
| any maturity **grade** (A+, etc.) | Withdrawn; lead with measured numbers, not a grade |

## Do / Don't

- **Do** run the counter and `attest` live — reproducibility on camera *is* the pitch.
- **Do** keep Bob's session-2 answer on screen long enough to read.
- **Don't** show the Python install path, `STATUS.md`, or any withdrawn grade.
- **Don't** speak a number that isn't in [`03-solution-impact.md`](./03-solution-impact.md) or reproducible live.
