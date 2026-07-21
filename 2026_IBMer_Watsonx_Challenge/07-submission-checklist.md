# Submission Checklist

> Work through this list top-to-bottom before clicking final submit.
> **Deadline: July 22, 2026 at 10 a.m. ET**
> Only the last submission counts as final — you can resubmit.

---

## Eligibility (non-negotiable — a miss here zeroes the score)

- [ ] Team registered (1–10 members) on the challenge platform.
- [ ] **All** members completed the required Bob education (`Get started with IBM Bob`, ~40 min) by July 22, 10:00 ET.
- [ ] Submission foregrounds **IBM Bob** (this project is Bob-native — keep it that way).
- [ ] If submitting for judging, judging committee selected → **Software**.
- [ ] You can resubmit; only the **last** submission counts.

---

## Required for All Submissions

### Field 1 — Solution Statement
- [ ] Drafted in [`01-solution-statement.md`](./01-solution-statement.md)
- [ ] **Under the 500-word limit** — verified **483 words** (`awk 'f;/^---$/{f=1}' 01-solution-statement.md | wc -w`)
- [ ] Remove everything above the `---` line before pasting into the form
- [ ] Reads clearly to a non-technical judge in under 30 seconds
- [ ] Contains no unverified statistics (qualitative only in this field; ~60% is labelled "session cost readout")
- [ ] Pasted into the submission form

### Field 2 — Technical Statement
- [ ] Drafted in [`02-technical-statement.md`](./02-technical-statement.md)
- [ ] **Under the 500-word limit** — verified **478 words**
- [ ] Remove everything above the `---` line before pasting into the form
- [ ] Token-economy table present — maps IBM principles to concrete mode behaviours
- [ ] "Provenance discipline" close present — Beta label stated, no SLA claim, **no self-awarded grade**
- [ ] Pasted into the submission form

### Field 3 — Solution Impact
- [ ] Drafted in [`03-solution-impact.md`](./03-solution-impact.md)
- [ ] **FORM ENTRY block used** — categories selected + hours (2.0→0.8) + frequency (multiple/day)
- [ ] **20.0% figure** cites N=183, CI [18.9%, 21.2%], null test 0.73%, provenance `evaluation/results/validation-2026-07-14/`
- [ ] **51% figure** cites "N=10 well-formed summary pairs out of 19 total measured" — not presented as universal
- [ ] **~60% hcd figure** labelled "single-project observation, practitioner-measured"
- [ ] The three figures are kept separate (not blended into a single headline)
- [ ] No claim of enterprise SLA or production readiness for the Python TOS layer
- [ ] Pasted into the submission form

---

## Required for Judged Submissions

### Pitch File
- [x] **PDF built: [`08-pitch-deck.pdf`](./08-pitch-deck.pdf)** — 3 pages, ~0.46 MB (limits: ≤3 pages, ≤10 MB). Source: [`08-pitch-deck.html`](./08-pitch-deck.html) → `weasyprint 08-pitch-deck.html 08-pitch-deck.pdf`
- [ ] Verify page count is exactly 3 before upload (`pdfinfo 08-pitch-deck.pdf | grep Pages`)
- [ ] Contains the retraction / honesty story (Page 3) — the unique differentiator
- [ ] Contains the hcd ≈60% personal proof (Page 2) — not just statistics
- [ ] **BobjectifLune arc** bookends it (Page 1 opens, Page 3 closes)
- [ ] No Tintin/Hergé artwork — original moon/rocket motif only ✅ (mission-patch is original SVG)
- [ ] *Optional:* if recording the ≤3-min MP4 instead, build it from [`04-pitch-file-outline.md`](./04-pitch-file-outline.md) + [`06-demo-script.md`](./06-demo-script.md) (add a live Bob IDE mode-picker screenshot)
- [ ] Uploaded to submission form (PDF **or** MP4 — one file)

### Live Demo (if applicable)
- [ ] Rehearsed cold from [`06-demo-script.md`](./06-demo-script.md) — exact prompt text memorised
- [ ] Populated KB repo ready before recording
- [ ] Beta Python install path never shown on camera
- [ ] STATUS.md never shown on camera

### Judging Committee Selection
- [ ] **Software** judging committee selected on the submission form

---

## Quality Gates — Read Before Submitting

| Gate | Check |
|---|---|
| **Word limits respected** | Field 1 = 483 words, Field 2 = 478 words — both under the hard 500-word form limit. Re-check after any edit. |
| **No fabricated numbers** | 20.0% cites manifest. 51% cites N=10/19. ~60% cites session readout. All three labelled at their true confidence level. |
| **Bob IDE accessibility is clear** | Submission mentions zero-install mode picker activation — judges must know this is not CLI-only |
| **Personal example is present** | hcd-at-its-core paragraph is in Field 3 and Slide 5 |
| **"Beta" caveat is contextualised** | Beta = Python TOS layer only; Bash KB Manager is stable v1.0 |
| **No claim of external services** | No MCP servers, no plugins, no external APIs — stated explicitly |
| **Honesty dividend named** | The retraction of 68.96% is a feature, not a liability — slide 7 makes this explicit |
| **STATUS.md not shown on camera** | It's an internal self-assessment (shows Beta; the prior A+ self-grade was **withdrawn**). Neither field nor pitch cites a grade — keep it that way; lead with measured numbers. |

---

## Submission Risk Register (know your exposure)

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | No independent velocity/time-saved outcome number → weak on Effectiveness | **High** | hcd ~60% is present and honestly labelled; that is the personal proof — lean on it |
| R2 | A judge probes maturity/readiness | Med | The prior A+ self-grade is **withdrawn** and no longer cited anywhere in the pack; say plainly: "Bash KB Manager is stable v1.0; the Python layer is Beta; every number is measured and labelled." Honesty is on-brand. |
| R3 | Two-system complexity read as hard to adopt | Med | Demo the zero-install IDE path only; frame Python as optional |
| R4 | Judge reads "LLM-Wiki (Karpathy)" as unoriginal | Med | Slide 2 names *our* original contribution: Bob-native modes + Bobcoin-economy framing + cacheable schema layer |
| R5 | Non-Bob build tooling surfaces in the submission | Med | Keep all deliverables Bob-native; scrub the demo recording |
| R6 | Eligibility miss zeroes the score regardless of quality | **High** | Complete the eligibility checklist above before the deadline |

---

## Final Submit

- [ ] All three required fields are filled on the submission form
- [ ] Pitch file is attached (if submitting for judging)
- [ ] You have clicked **Submit** (not just saved a draft)
- [ ] You have noted the confirmation — only the last submission is final

---

> 💡 You can resubmit as many times as you want before the deadline.
> Only the last submission counts. If you improve Field 3 after submitting, resubmit.
