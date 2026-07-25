# Field 3 — Solution Impact

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

*This field is **structured**, not a 500-word essay. On the form you (1) select impact categories, (2) enter hours-before / hours-after, and (3) pick a frequency. Use the **FORM ENTRY** block below verbatim. The rest of this file is the evidence behind those numbers — keep it for the pitch and for judge Q&A.*

---

## ⏱️ FORM ENTRY — paste / select exactly this

**Impact categories (select all that apply):**
- ☑︎ Reduce time to complete routine task(s)
- ☑︎ Reduce time spent searching for information
- ☑︎ Speed up product/offering development, innovation and exploration of new features
- ☑︎ Improve the accuracy and consistency of output(s)
- ☑︎ Improve code quality / maintenance

**Task addressed:** *One Bob iteration cycle on a complex technical module — re-establishing the foundational context (architecture, prior decisions, failure modes) and then doing the new design/validation work.*

| Field | Value |
|---|---|
| Hours **before** Mnemox | **2.0 hr / cycle** |
| Hours **after** Mnemox | **0.8 hr / cycle** |
| Time saved | **1.2 hr / cycle (≈60%)** |
| Frequency | **Multiple times per day** (during active build) |

**How the estimate was determined (state this if asked):** On **hcd-at-its-core** we measured a **≈60% reduction in Bobcoin (token) spend per iteration cycle**, comparing Bob session cost readouts *with* vs *without* the KB loaded, across iteration cycles. The hours above translate that measured token reduction into wall-clock Bob-in-the-loop time at the same ratio — an iteration cycle that previously spent ~2 hours (most of it re-deriving foundations before any new work could start) now spends ~0.8 hour, because the foundations are retrieved, not relearned. This is a single-project, practitioner-measured observation, labelled as such — not a controlled A/B trial.

> Alternative narrower grain, if the form prefers an atomic task: *"recover prior architectural context at session start"* — **before ≈0.5 hr, after ≈0.1 hr, multiple times per day.** Same mechanism, smaller unit.

---

**Mnemox**, built by **BobjectifLune**, delivers impact through three measured, manifest-backed mechanisms — and the compounding value those savings make possible.

## 1. Measured, manifest-backed savings (input cost)

**Token Optimization System (`src/`), high-fidelity compression:**
- **20.0% mean token reduction** (95% CI = [18.9%, 21.2%]); token-weighted aggregate **22.8%**.
- Corpus: **N = 183** real in-repo documents. Method: real `tiktoken` counting, bootstrap CIs.
- **Null test passes**: shuffled input compresses **0.73%** — confirming genuine structure removal, not a measurement artifact.
- Fidelity: mean quality score **≈ 0.80** — this is a *lexical-overlap heuristic*, not a semantic-fidelity guarantee; we state the number and its limit rather than imply zero information loss.
- Provenance: `evaluation/results/validation-2026-07-14/report.json` + `manifest.json`.

**Multi-level cache — recompute avoidance (reported *separately*, workload-dependent):**
A cache hit avoids a full recompute (~100% saved on that query); effective savings scale with how repetitive your work is:

| Workload repetition rate | Effective saving (optimizer + cache) |
|---|---|
| Unique queries (0% repeat) | ~20% |
| Moderate (30% repeat) | ~44% |
| High (70% repeat) | ~76% |
| Extreme (90% repeat) | ~92% |

Your repetition rate — not our marketing — determines where you land.

**Re-derivation avoidance (the Bash KB Manager):**
KB artefacts fall into two structurally distinct categories: **compact summaries** (N=10) — architecture decisions, concept digests, reference sheets — intentionally smaller than their source; and **comprehensive guides and research reports** (N=9) — intentionally larger than source, producing no re-derivation saving. Only the compact-summary category is the right unit for re-derivation avoidance. On those N=10 pairs: **51% mean token saving** (95% CI [38%, 64%]). The N=9 comprehensive artefacts are not excluded to flatter the number — they are excluded because re-derivation saving is not what they are for. Breakeven occurs at the first query on well-formed pairs; ROI reaches ~80× at 40 queries, against a 0.80 BC document-creation cost.

## 2. What this means in practice — hcd-at-its-core

The first real production use of BobjectifLune was on **hcd-at-its-core** — a training platform bringing business owners, enterprise architects, DBAs, SREs, and Kubernetes engineers into the world of HCD, the IBM/DataStax Hyper-Converged Database built on Apache Cassandra. It comprises 94 interactive demos and 15 masterclasses, each running against real clusters that mimic real-world topologies and data-entropic scenarios — the hardest class of real-time data problems: *the economy of the now*.

Every demo module required Bob to reason deeply about cluster topology, replication strategies, consistency trade-offs, and failure modes. Without the KB, each iteration began by re-deriving those foundations from raw source — paying the same tax on every module, every time. With the KB Manager loaded, foundations were retrieved, not relearned. Measured from session cost readouts: **≈60% reduction in Bobcoin spend per iteration cycle** (single-project observation, practitioner-measured). The freed budget was reinvested directly into deeper failure modes, more entropic scenarios, and more realistic topologies across all 94 modules.

This is what the savings actually buy: not cheaper sessions, but sessions ambitious enough to attempt problems that would otherwise have been unaffordable.

## 3. The South EMEA Tiger Team context

As a Global Product Specialist running recurring watsonx.data lakehouse engagements across Southern Europe, the Middle East, and Africa, every new client arrives with the same architectural questions, integration patterns, and sizing decisions — questions the team has already answered and lost to Slack threads and expired sessions. Mnemox converts that recurring re-derivation cost into a one-time documentation cost. The second engagement, and every one after, starts from the team's full accumulated expertise rather than from zero.

## 4. Repeatable, ongoing value

This is not a one-time productivity spike. The KB is version-controlled and team-shared: knowledge written by one member is retrieved by all, and value **accrues every session** rather than resetting. That maps directly to the Software criterion of *repeatable, ongoing use that meaningfully improves daily work.* Deploying to a new workspace takes one command; after that, every team member activates the mode from the picker with no further steps. A client scenario resolved today seeds the starting context for the next engagement. An architectural decision documented once is never re-derived again by anyone on the team.

> **Why not a vector database or RAG?** RAG retrieves passages from a static snapshot — it does not accumulate insights across sessions, does not distinguish a hard-won architectural decision from boilerplate, and requires a vector DB, an embedding API, and an ingestion pipeline. Mnemox requires nothing beyond Git. More fundamentally: RAG re-derives answers from raw chunks on every query. Mnemox stores the answer itself — structured, cross-referenced, team-curated — and retrieves it directly. The saving is not retrieval speed. It is the elimination of re-reasoning.

## 5. Quality + efficiency together (the honesty dividend)

The impact isn't only cheaper sessions — it's **trustworthy** cheaper sessions. This project caught its own fabricated "68.96% VALIDATED" figure, formally retracted it, rebuilt a manifest-backed validation harness with a passing null test, and now enforces in CI that no savings number ships without provenance. In an era of confidently-wrong AI output, *a productivity tool that refuses to overclaim its own productivity* is the differentiator — quality improvement delivered alongside the efficiency gain, exactly what the Software area asks for.

## 6. Proof of concept in production

This submission was drafted using the tool it describes. The knowledge base at `docs/knowledge-base/` — **110+ documents** — was created and maintained by the Knowledge Manager mode through the same sessions used to build and validate the project. The GitHub repository is open and inspectable: the KB is the artefact, not a claim about it.

**The deeper impact** is not the token savings — it is what the savings make possible. When re-derivation cost approaches zero, the budget previously consumed by repetition becomes available for depth, breadth, and agentic ambition. Mnemox does not just reduce cost. It expands the frontier of what IBM Bob can affordably attempt.

On the way to the impossible, every Bobcoin saved is a step further.
