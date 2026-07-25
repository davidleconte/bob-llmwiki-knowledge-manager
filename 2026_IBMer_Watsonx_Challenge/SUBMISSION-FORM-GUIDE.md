# Submission Form Guide — do the whole form from here

> ✅ **SUBMITTED — frozen 2026-07-25.** This pack was submitted to the 2026 IBMer
> watsonx Challenge before the **22 July 2026, 10:00 ET** deadline, as a zip of the
> repository at that release. It is preserved as the record of what was entered and is
> **no longer a working document**: unchecked boxes below are the state at submission,
> not outstanding work, and the deadline references are historical.
>
> Numbers here were correct against the evidence available on 22 July. Two have since
> been superseded and are **not** retro-edited, because this is a submission record:
>
> * **Compression.** The pack cites ~20% mean. A 2026-07-25 re-measurement puts the
>   current system at **6.8%** — the optimizer was made structure-preserving, trading
>   ~12pp of compression for fidelity (0.798 → 0.995). See [`STATUS.md`](../STATUS.md).
> * **The ≈60% Bobcoin figure.** A single-project practitioner observation with **no
>   repo artifact**, as `09-compound-loop-demo.md` in this same pack says of it. It was
>   labelled as an observation rather than a measurement, which was the right call, but
>   it is not reproducible and should not be repeated as one.

> Platform: `compete.ibmer.watsonx-challenge.ibm.com` → **Submissions** tab. **Deadline: July 22, 10:00 ET.**
> You can resubmit; only the **last** submission counts.

---

## 0 — Eligibility (a miss here zeroes the score — do first)
- [ ] You're in a **registered team (1–10 people)** on the platform
- [ ] **Every** team member finished the required **IBM Bob education** (~40 min)
- [ ] Path = **Path 1 – Built during the challenge**
- [ ] Judging = **Yes** → committee = **Software**

## 1 — Field 1 (Solution statement)
Copy everything below the `---` in **`01-solution-statement.md`** → paste into the form. (483 words ≤ 500.) *A `paste-field1.txt` scratch file was used at submission time; it was never committed, so this step now names the tracked source instead of a file a fresh clone would not have.*

## 2 — Field 2 (Technical statement)
Copy everything below the `---` in **`02-technical-statement.md`** → paste. (478 words ≤ 500.)

> **Plain-text caveat:** if the form box shows literal `**` / backticks, the field is plain-text — ask me for
> a de-formatted version and I'll strip the markdown in ~30 seconds.

## 3 — Field 3 (Solution impact) — STRUCTURED, not pasted
Tick these **5 categories**:
- [x] Reduce time to complete routine task(s)
- [x] Reduce time spent searching for information
- [x] Speed up product/offering development, innovation and exploration of new features
- [x] Improve the accuracy and consistency of output(s)
- [x] Improve code quality / maintenance

**Hours before / after — choose ONE basis** (this is the number 3 jurors scrutinised):

| | Task entered | Before | After | Basis | Trade-off |
|---|---|---|---|---|---|
| **A — Confident** *(current)* | one Bob iteration cycle on a complex module | **2.0 hr** | **0.8 hr** | ≈60% hcd single-project token readout | More impressive; the ≈60% has **no repo manifest** → the jurors' target |
| **B — Conservative** *(fallback, bulletproof)* | recover prior context at session start (retrieve from KB vs re-read source) | **0.5 hr** | **0.1 hr** | the **measured** 51% re-derivation saving (N=10, manifest `tests/validation/test_km_savings.py`) + 20% compression (N=183) | Less punchy, but **every input is manifest-backed** → closes the objection |
| **C — Measured** *(best)* | one Bob iteration cycle | *from A/B run* | *from A/B run* | the **controlled A/B** (`AB-velocity-measurement-protocol.md`) | Strongest; needs ~4–8 hr before the deadline |

Frequency: **Multiple times per day.**

> Recommendation: if you can spare 4–8 hours, run **C** (`AB-velocity-measurement-protocol.md`) — it converts
> the weakest criterion into the winning signal. If not, use **B** — it removes the single sharpest criticism
> at zero data cost. **A** is fine too (it's honestly labelled), but leaves the ≈60% exposed to a probing juror.
>
> **Note — the pitch is the *other* ≈60% surface.** Page 2 of `08-pitch-deck.pdf` has a "≈60% fewer Bobcoins /
> iteration" stat card. If you go with **B** (or can't run **C**), tell me and I'll re-cut page 2 to lead with
> the reproducible 20% and demote ≈60% to a labelled single-project note — keeping the pitch consistent with
> whichever Field-3 basis you pick.

## 4 — Pitch file
Upload **`08-pitch-deck.pdf`** (3 pages, 0.46 MB — within the ≤3-page / ≤10 MB limit).

## 5 — Submit
- [ ] Click **Submit** (not just Save draft)
- [ ] Confirmation email received (includes the AI advisor's spot-check — you can revise & resubmit)

---

### Files in this folder
- `01-solution-statement.md`, `02-technical-statement.md` — the tracked sources; paste the body below the `---` (the untracked `paste-field*.txt` scratch files are not part of the pack)
- `08-pitch-deck.pdf` — the judged pitch (source: `08-pitch-deck.html`)
- `AB-velocity-measurement-protocol.md` — how to get the measured velocity number (Field 3 Option C)
- `01`–`03` — the field sources · `04`/`06`/`07`/`README` — internal working notes (not submitted)
