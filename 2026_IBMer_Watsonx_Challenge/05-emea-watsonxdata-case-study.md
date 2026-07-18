# Case Study — hcd-at-its-core: **BobjectifLune**'s First Production Use

> **Status:** This case study documents the first real, measured production use of
> Mnemox, by **BobjectifLune**. Numbers are practitioner-measured from session cost readouts.
> Provenance: single-project observation, labelled as such throughout.

---

## 1. The scenario

**hcd-at-its-core** is a training platform built to bring business owners, enterprise and
data architects, DBAs, SREs, operators, and Kubernetes engineers into the world of **HCD**
— the IBM/DataStax Hyper-Converged Database built on Apache Cassandra. HCD addresses the
most complex data problem in the real-time world: *the economy of the now* — the class of
operational data scenarios where latency, consistency, partition tolerance, and failure
resilience must all be solved simultaneously, under live load, at scale.

The platform comprises:
- **94 interactive demos** — each running against real clusters that mimic real-world
  topologies and data-entropic scenarios
- **15 masterclasses** — structured deep-dives on operational patterns, failure modes, and
  architectural decisions that practitioners face in production
- All modules interactive, all clusters live, all scenarios chosen for their difficulty:
  the scenarios that are *hard to face and hard to solve*

**The pain without KB Manager:** Every demo iteration session required Bob to re-derive
the same cluster topology context, replication strategy rationale, consistency model
trade-offs, and failure mode taxonomy from raw source — paying full re-derivation cost
on every module, every time. Knowledge from session N was invisible to session N+1.
Iteration cycles were shallower than the subject demanded.

---

## 2. What the KB Manager changed

Using the `knowledge-manager` mode, the team filed cluster topology patterns, replication
strategy decisions, consistency trade-off rationale, and failure mode classifications into
the shared KB once. Each subsequent iteration session **retrieved** those foundations
instead of re-deriving them.

The freed Bobcoin budget was reinvested directly into the work that actually required
depth: richer failure modes, more entropic data scenarios, more realistic multi-datacenter
topologies across the 94 demo modules. The sessions became more ambitious, not just cheaper.

---

## 3. Measurement

| Metric | Observation | Provenance |
|---|---|---|
| Bobcoin reduction per iteration cycle | **~60%** | Session cost readout, practitioner-measured |
| Sample | Single project, multiple iteration sessions | Labelled as single-project observation |
| What the savings funded | Deeper failure mode coverage, broader scenario topology, richer data-entropic cases | Qualitative, observed across modules |

> **Honesty note:** This is a single-project observation measured from session cost
> readouts by the practitioner. It is not a controlled experiment with a held-out
> baseline. It is reported at exactly that confidence level — because one honest
> practitioner measurement, clearly labelled, is more credible than a larger
> unverifiable claim.

---

## 4. The result, in the submission's own words

> *"On hcd-at-its-core — 94 interactive demos, 15 masterclasses on real clusters —
> the KB Manager cut Bobcoin spend per iteration cycle by ~60% (session cost readout,
> single-project observation). Every Bobcoin recovered was reinvested into deeper
> failure modes, richer topologies, and more entropic scenarios that would otherwise
> have been unaffordable to build."*

---

## 5. Why this matters beyond the number

**The scenario is uniquely hard.** HCD/Cassandra at enterprise scale — multi-datacenter
replication, tunable consistency, partition tolerance under failure, compaction strategies,
token-aware routing, data-entropic load scenarios — is exactly the class of problem that
exhausts a Bob session's context budget fastest. Re-derivation cost is highest precisely
where the technical depth is greatest. The KB Manager's structural savings are largest
precisely where the subject demands the most.

**The reinvestment story is the real result.** The 60% reduction is not the impact — it
is the mechanism. The impact is 94 demo modules that are richer, harder, and more
realistic than they would have been if every session had paid the re-derivation tax. The
economy of the now, taught by a platform that could only afford to go that deep because
the Bobcoin budget was freed.

**Generalisable to any complex, iterative IBM technical project.** Any team building a
platform, product, or training asset with Bob across multiple sessions faces the same
re-derivation tax. hcd-at-its-core is the existence proof that the KB Manager converts
that recurring cost into a one-time investment — and that the compound interest on that
investment is paid in ambition, not just efficiency.
