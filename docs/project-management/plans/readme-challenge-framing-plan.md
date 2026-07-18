# Plan: README Challenge Framing Improvement

## Goal

Reshape the README's framing so it communicates the full value proposition for the
IBM watsonx Challenge judges and any IBMer reading it — without changing what is already
accurate and working. This is a documentation change only. No code changes.

## Scope

- `README.md` — two targeted additions (new section + expanded opening)
- No changes to `STATUS.md`, `INTEGRATIONS.md`, or any source file
- No fabricated metrics — all additions must be grounded in what the system actually does

## The Core Framing Gap

The README currently reads: *"here is how you save tokens"* (defensive, cost-reduction posture).

The correct reading is: *"token economy is the lever that makes ambitious agentic research
affordable"* (offensive, value-expansion posture).

The difference: cost reduction is the mechanism; expanded research scope and agentic depth
are the payoff. The payoff is what judges score.

---

## Sub-Task 1 — Rewrite the opening section (§1 and the tagline)

**Intent:** Replace the defensive "you're overpaying" framing with the expansive "you can now
afford to go deeper" framing. The tagline and §1 are the first things judges read.

**Expected Outcomes:**
- Tagline and §1 lead with the value (deeper research, agentic scope) not the cost
- The Bobcoin/token economy story is kept — repositioned as the *enabler*, not the *goal*
- Karpathy LLM-Wiki reference is preserved (it is the creative anchor)

**Todo List:**
1. Revise the `###` tagline under the title from *"paying to rediscover"* to something that
   leads with research depth and agentic ambition
2. Revise §1 body to open with *what you can now do* before explaining *what you were
   losing* — flip the narrative order
3. Keep the Bobcoin economy table in §4 unchanged — it is accurate and credible

**Relevant Context:** `README.md` lines 3, 39–49

**Status:** [ ] pending

---

## Sub-Task 2 — Add a "Who this is for" section between §3 and §4

**Intent:** Give judges and IBMers concrete personas and use cases so they can immediately
see where this applies to their work. Right now there are no personas — the README reads as
a generic developer tool.

**Expected Outcomes:**
- 3–4 concrete IBMer personas, one of which is explicitly the watsonx.data / Tiger Team /
  Global Product Specialist scenario
- Each persona maps to: the problem they had → what the KB makes possible → the scale of
  work they can now tackle
- The agentic deployment angle (real-time agent teams on large business scopes) appears here
  as a concrete use case, not an abstract claim
- Section is visually scannable (short table or bullet blocks, not long prose)

**Todo List:**
1. Write a `## 3b. Who this is for` section (inserted between §3 and §4 in README.md)
2. Include 3–4 personas: (a) Global Product Specialist / Tiger Team — MEA client research
   and lakehouse PoCs; (b) Software team — SDLC velocity, knowledge that compounds across
   sprints; (c) Researcher — experiment context that survives session boundaries; (d) Agentic
   team lead — economics that make multi-agent deep dives affordable
3. For each persona: 1-sentence problem, 1-sentence what KB enables, 1 concrete example
4. Close the section with the "economy as agentic enabler" thesis in 2 sentences

**Relevant Context:** `README.md` lines 69–97 (§3 and §4)

**Status:** [ ] pending

---

## Sub-Task 3 — Add Bob IDE accessibility callout to §3 (native to Bob Shell)

**Intent:** The README underplays how accessible Bob IDE activation is. Path E (zero-install
mode picker) is mentioned in §6 but not in the opening description of the system. Judges
reading §3 may not reach §6.

**Expected Outcomes:**
- §3 or the "Supported targets" table includes a clear "zero-install in Bob IDE: mode
  picker → 🧠 Mnemox Knowledge Builder" statement near the top
- The Bob IDE user is a first-class target in the opening, not a footnote

**Todo List:**
1. Add a one-line callout in §3 (after the bullet list) confirming Bob IDE zero-install:
   *"Bob IDE users: activate from the mode picker — no installation required"*
2. Optionally add a ✅ Bob IDE column note to the opening description paragraph

**Relevant Context:** `README.md` lines 69–83, lines 154–164

**Status:** [ ] pending

---

## Validation Checklist

Before finalising:
- [ ] No number in any new text lacks a source (no ungrounded claims)
- [ ] The Karpathy LLM-Wiki credit is still prominent
- [ ] The "Beta — Not Production Ready" status is not contradicted
- [ ] The watsonx.data / MEA example is described as a *use case pattern*, not a claim
      of deployed results
- [ ] All three additions are coherent with the existing §4 Bobcoin table (which stays)
