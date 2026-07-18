# 90-Second Live Demo Script (verbatim)

> The demo is your highest-scoring 90 seconds — it's where "Design & usability" and "Effectiveness" are
> won or lost. Rehearse it cold until it runs without a hitch. Lead with the **zero-install Bob IDE path**;
> never show the Beta Python install on camera. Every spoken line below is a *claim you can back* — no
> improvisation into unverified numbers.

## Setup (before recording — off camera)

- A real repo open in **Bob IDE**, with a **populated** `docs/knowledge-base/` (run `run-full-analysis.sh`
  + a couple of KB sessions beforehand so retrieval has something to return).
- A second, **empty-KB** repo ready, to show the cold-start contrast if you have time.
- Mode picker visible in the status bar.

## The script

**[0:00–0:12] The problem (say to camera, no screen action yet)**
> "Every Bob session starts amnesiac. It re-reads your repo and re-answers last week's question — and you
> pay Bobcoins and your own time to relearn what Bob already knew. We fixed that by giving Bob a memory."

**[0:12–0:25] Zero-install activation (screen: mode picker)**
> "No plugin, no MCP server, no install. I click the mode picker… and select the Knowledge Manager mode."
*(Click mode picker → 🧠 Mnemox Knowledge Builder. The skill auto-loads.)*
> "That's the entire setup. Zero steps."

**[0:25–0:50] Retrieval, not re-derivation (screen: type the resume prompt)**
Type verbatim:
> `What did we document most recently? Summarise the KB and suggest what to work on next.`

As Bob answers:
> "Notice what didn't happen — Bob didn't re-read the source tree. It's retrieving from the knowledge base
> we built in earlier sessions: architecture decisions, design rationale, prior findings. Grounded answer,
> a fraction of the context."

**[0:50–1:10] The compounding proof (screen: show a KB file + INDEX.md)**
> "This is version-controlled Markdown. One teammate writes it once; the whole team retrieves it. The KB
> gets richer every session instead of resetting — so the work stops repeating, and the bill falls with it."

**[1:10–1:25] The numbers, honestly (screen: the impact slide or report.json)**
> "Measured: 20% mean token compression on 183 real documents — manifest-backed, null-tested. With cache
> reuse it climbs with your repetition rate. We publish the model, not a single flattering number."

**[1:25–1:30] The close (to camera)**
> "It's Bob-native, one-click to adopt, and it refuses to overclaim its own savings. That last part is the
> point."

## Optional 20-second extension (if the format allows)

Show the **cold-KB repo**: same resume prompt returns "the KB is empty." Then cut to the populated one.
The contrast *is* the value proposition — the audience sees re-derivation vs retrieval side by side.

## Do / Don't

- **Do** rehearse the exact prompt text; a fumbled live prompt reads as fragility.
- **Do** keep Bob's answer on screen long enough to read — silence is fine.
- **Don't** show `scripts/install.sh`, `.zshrc`, or the Python Beta path on camera.
- **Don't** say any number that isn't in [`03_SOLUTION_IMPACT.md`](./03_SOLUTION_IMPACT.md).
- **Don't** show STATUS.md on camera (self-awarded A+ grade undercuts the honesty brand — see risk register in [`README.md`](./README.md)).
