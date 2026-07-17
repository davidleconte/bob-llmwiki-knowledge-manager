---
name: ai-pilot-risks
description: >
  Use this skill when a user is planning, evaluating, or documenting an AI pilot project,
  Proof of Concept (PoC), or AI pilot study — especially when addressing risks around
  resources, product knowledge, missing technology, budget, scaling, data, organisation,
  GDPR, or the EU AI Act. Also triggered by questions like
  "What can go wrong in an AI pilot?" or "How do I de-risk a PoC?".
---

# Skill: AI Pilot & Proof-of-Concept Risk Assessment

This skill guides through a structured risk analysis for AI pilot projects and PoCs.
The goal is to surface typical pitfalls — from the "science experiment trap" to GDPR gaps —
early enough to anchor them in project documents before they become blockers.

This skill is aligned with the **IBM Client Engineering (CE) methodology**: time-boxed,
outcome-driven engagements that move through **Discover → Envision → Empower** phases
and conclude with a clear Go/No-Go decision before any production investment.

---

## Background: Why Do AI Pilots Fail?

Up to **95 % of all AI pilot projects** never reach production.
The root causes cluster into four categories:

| # | Category | Core Problem |
|---|---|---|
| 1 | Data & Technology | Sanitised sandbox data ≠ production data; integration complexity underestimated |
| 2 | Organisation & Strategy | No ROI / business case; no scale-up plan after the pilot |
| 3 | People & Culture | Skills gap; missing change management; unclear ownership |
| 4 | Compliance & Governance | GDPR, EU AI Act, hallucination and bias addressed too late |

**Guiding principle:** "Organisation-First, not Tool-First" — technology follows the need,
not the other way around.

**IBM CE principle:** A pilot that cannot show a path to production value on day one
is a science experiment, not a business engagement.

---

## IBM Client Engineering Phase Model

Every AI pilot assessment must be mapped to the CE phase it belongs to.
Use this mapping throughout Steps 1–6 to frame findings and recommendations.

| CE Phase | What happens | Key output | Typical duration |
|---|---|---|---|
| **Discover** | Understand the as-is process, pain points, stakeholders, data landscape | Problem statement, success criteria, blockers list | 1–5 days |
| **Envision** | Design the to-be solution, validate technical feasibility, agree on scope | Architecture sketch, PoC scope doc, Go/No-Go criteria | 3–10 days |
| **Empower** | Build a working PoC / MVP on real data, measure against success criteria | Runnable demo, recommendation report, scale-up roadmap | 2–8 weeks |

> **CE rule:** Do not enter "Empower" without documented Go/No-Go criteria from "Envision".
> Every open blocker identified in Discover or Envision is a risk until resolved.

---

## Step 1 — Understand the Context

Read all available project documents (analysis, requirements, risk list, architecture).
Use `read_file` and `list_files` on the relevant directories.

Identify:
- **Project name and goal** of the pilot / PoC
- **Current CE phase** (Discover / Envision / Empower / Post-Pilot)
- **Involved stakeholders** (customer, IBM CE, partners)
- **Current maturity level** (idea / concept / running pilot / production preparation)
- **Existing risk documents** — to avoid duplication

> **CE alignment:** In the Discover phase the goal is a validated problem statement,
> not a solution. If the project has jumped straight to building, flag it as RD-01.

---

## Step 1b — Capture the As-Is Process and Backend Systems

Before a To-Be concept can be evaluated, the **current state** must be fully understood.
Without this baseline a gap analysis is impossible and integration risks remain invisible.
This maps directly to the **Discover phase** deliverable in IBM CE.

### 1b.1 Document the As-Is Process

Determine (by reading existing documents or by asking targeted questions) the
**current manual or partly-automated process**:

| Question | Goal |
|---|---|
| How are incoming messages / data processed today? | Understand process steps |
| Who performs which step manually? | Quantify manual effort |
| Which decisions does a human make today — and what criteria do they use? | Understand classification logic |
| How long does the current process take per unit (email, document, request)? | Baseline for ROI measurement |
| Where do errors, delays, or escalations occur today? | Identify pain points |
| How are exceptions and edge cases handled? | Understand fallback logic |

Record the result as a **process description in text or table form** — no diagram required,
but structured enough for the delta comparison in Step 1c.

### 1b.2 Inventory Backend Systems and Data Sources

Create an inventory of all **systems that the AI pilot must connect to or replace**:

| System | Type | Current interface | Relevance to pilot |
|---|---|---|---|
| [System name] | e.g. email server, CRM, ERP, DMS | e.g. IMAP, REST API, CSV export, manual | Data source / target system / both |

For each system ask:
- **Is a technical interface (API, webhook, queue) available** — or only manual export?
- **Who is the technical owner** of the system on the customer side?
- **Which data** flows through this system that is relevant to the AI pilot?
- **Are there access restrictions** (firewall, VPN, role concept, GDPR restrictions)?
- **Is the system legacy / end-of-life** — or will it be replaced during the pilot?

> ⚠️ **Critical risk:** If no technical interface exists and only manual data export is possible,
> a productive integration is not feasible.
> This must be recorded as a **blocker risk** in the risk list (score 🔴 High).

> **CE alignment:** IBM CE requires a "Definition of Done" for the Empower phase.
> If system access is not confirmed by end of Discover, the PoC scope must be reduced.

### 1b.3 Checklist: AI System Access and Data Availability

| # | Question | Status |
|---|---|---|
| S-01 | Is an AI-ready interface to the source system (e.g. email system, CRM) already available? | |
| S-02 | Which specific system is used (e.g. Microsoft Exchange, Google Workspace, SAP)? | |
| S-03 | Is there a documented API or existing connector (e.g. IBM App Connect)? | |
| S-04 | What data will be extracted — structured text only, or also attachments, images, metadata? | |
| S-05 | Will processed data be persisted in a RAG system or vector store? | |
| S-06 | Who has access to the raw data today — and who is authorised to grant the AI service access? | |
| S-07 | Is data access documented and approved as GDPR-compliant? | |

---

## Step 1c — Delta Analysis: As-Is vs. To-Be

Create a structured **gap table** that shows what changes through the AI pilot.
This table is the central communication artefact for stakeholders and sponsors.
In IBM CE terms, this is a core **Envision phase** output.

### Gap Table (template)

| Dimension | As-Is (today) | To-Be (after pilot / rollout) | Delta / Effort |
|---|---|---|---|
| **Process** | Manual, step X takes Y minutes | Automated, decision in < Z seconds | Process change + change management |
| **Systems** | System A delivers data via daily CSV export | Real-time integration via API / queue | API development or connector needed |
| **Data** | Only the email body text is processed | Text + attachment type + sender metadata | Parsing logic for attachments required |
| **Roles** | Clerk classifies manually | Clerk reviews exceptions only | Role description + training |
| **Quality** | Error rate unknown / estimated X % | Target: error rate < Y % (measurable) | Measure baseline before pilot starts |
| **Compliance** | No AI documentation obligation | EU AI Act / GDPR requirements apply | DPIA + AI Act classification required |
| **Infrastructure** | No GPU server available | L40S / cloud GPU required | Hardware procurement or cloud licence |
| **Skills** | No ML/AI knowledge in the team | MLOps fundamentals required | Enablement plan needed |

### Interpretation Rules for the Gap Table

- **Delta = empty or trivial** → no risk, no effort
- **Delta = "API development needed"** → check whether resources and time are available in the pilot
- **Delta = "Change management"** → add RD-07 to the risk list
- **Delta = "Hardware procurement"** → check lead time and budget (RT-10)
- **Delta = "DPIA required"** → add RT-08 to the risk list, set deadline
- **More than 4 high-effort deltas** → reduce pilot scope or extend duration

> **CE alignment:** IBM CE pilots are time-boxed. If the gap table reveals more work than fits
> in the agreed window, scope must be cut — not the timeline extended indefinitely.
> Present the gap table in the Envision readout before entering Empower.

### Typical As-Is / To-Be Patterns in AI Pilots

These patterns appear regularly — check whether they apply to the current project:

| Pattern | As-Is | To-Be | Common Risk |
|---|---|---|---|
| Manual inbox | Employee reads and sorts emails | AI classifies, human reviews exceptions | Change management, acceptance |
| No API access | Data available only via Excel export | Real-time processing expected | Integration not feasible (blocker) |
| Legacy system without connector | ERP from 2008 without REST API | AI should read ERP data | Middleware / IBM App Connect required |
| Data in silos | Email, CRM, and DMS are separate | AI should combine all three sources | Data access, GDPR, complexity |
| No RAG / knowledge store | Knowledge resides with employees | AI answers should be based on company knowledge | RAG build-out, vector store, data maintenance |
| Paper or PDF process | Documents exist as scans | AI should extract structured data | OCR quality, hallucination risk |

---

## Step 2 — Checklist: 15 Pilot-Specific Risk Questions

Answer or mark each question with ✅ (resolved), ⚠️ (open), ❌ (not addressed):

> **CE alignment:** All ❌ items are blockers for the current phase gate.
> Resolve them before declaring the current CE phase complete.

### A · Resources (Customer & IBM)

| # | Question | Status |
|---|---|---|
| A-01 | Are the required customer resources (data, domain experts, IT access) formally committed? | |
| A-02 | Is IBM CE staffing (Technical Seller, Architect, Data Scientist) secured for the entire pilot duration? | |
| A-03 | Is there a defined timeline with milestones and Go/No-Go criteria? | |
| A-04 | Is a dedicated customer contact (Product Owner / Sponsor) nominated? | |

### B · Product Knowledge & Skills

| # | Question | Status |
|---|---|---|
| B-01 | Does the project team have sufficient knowledge of the IBM products in use (e.g. watsonx.ai, WML, Orchestrate)? | |
| B-02 | Is an enablement plan for the customer in place (training, workshops, documentation)? | |
| B-03 | Is there a knowledge-transfer strategy for the handover from pilot to operations? | |
| B-04 | Are the required skills available in the customer's operations team after the pilot ends? | |

### C · Technology & Integration

| # | Question | Status |
|---|---|---|
| C-01 | Are all required technologies (licences, APIs, hardware) available in the pilot? | |
| C-02 | Has integration into existing systems (CRM, ERP, email bridge, data sources) been prototypically tested? | |
| C-03 | Are production data (not just sanitised sandbox data) used in the pilot? | |
| C-04 | Have latency and scalability requirements for production been tested? | |

### D · Budget & Scale-Up

| # | Question | Status |
|---|---|---|
| D-01 | Is there an approved budget for the rollout **after** the pilot? | |
| D-02 | Is a business case with measurable ROI documented and signed off by management? | |
| D-03 | Is there an operational roadmap (Pilot → MVP → Production) with realistic timelines? | |
| D-04 | Is it clear which team will take over ongoing operations after the pilot (including MLOps)? | |

---

## Step 3 — Formulate Pilot-Specific Risks

> **Separation principle:** Pilot risks are divided into **two separate categories**.
> Delivery risks concern whether the pilot succeeds as a project (organisation, resources, process).
> Technical risks concern the feasibility and quality of the AI solution.
> Both categories receive their own codes and their own sections in the risk list.

> **CE alignment:** Delivery risks (RD) are owned by the **Engagement Lead / Client Executive**.
> Technical risks (RT) are owned by the **CE Architect / Data Scientist**.
> IBM CE phase gates require sign-off on both categories before moving to the next phase.

Create or extend the project risk list. Every new risk follows the standard schema:

```markdown
### R-XX · [Risk title] [traffic-light emoji]

| Attribute | Value |
|---|---|
| **Category** | AI Pilot / Delivery  OR  AI Pilot / Technical |
| **Probability** | H / M / L |
| **Impact** | L / M / H |
| **Risk score** | 🔴 High / 🟠 Medium-High / 🟡 Medium / 🟢 Low |

**Description:**
[Concrete description related to this project]

**Impact if it occurs:**
[What happens concretely?]

**Recommendation:**
[Action with owner and timeline]

**CE phase gate:** [Discover / Envision / Empower — by when must this be resolved?]
```

---

### 3A · Delivery Risks (RD codes)

> These risks threaten the **success of the pilot as a project** — regardless of whether
> the technology works. They arise from missing resources, unclear ownership, missing strategy,
> or insufficient acceptance. They are generally resolved **before pilot start** and sit in the
> responsibility of the project lead and management sponsor.
>
> **CE alignment:** All RD-01 to RD-03 items are **hard blockers** for entering the Empower phase.
> IBM CE engagements require a nominated sponsor and defined success criteria before work begins.

| Code | Delivery Risk | Typical Score | Who must act |
|---|---|---|---|
| RD-01 | No nominated management sponsor — decisions are delayed | 🔴 High | Management / Project Lead |
| RD-02 | No budget / no roadmap for rollout after pilot | 🔴 High | Management / Sponsor |
| RD-03 | Customer resources (domain experts, data, IT access) not formally committed | 🔴 High | Customer Project Lead |
| RD-04 | IBM CE staffing not secured for the entire pilot duration | 🟠 Medium-High | IBM Account / Delivery |
| RD-05 | Missing skills at the customer for operations after pilot end | 🟠 Medium-High | IBM Enablement / Customer IT |
| RD-06 | Unclear ownership after go-live (no operations team nominated) | 🟠 Medium-High | Customer Project Lead |
| RD-07 | Change management missing — end users do not accept the system | 🟠 Medium-High | Project Lead / HR |
| RD-08 | Go/No-Go criteria not defined — pilot ends without a clear outcome | 🟠 Medium-High | Project Lead (both sides) |
| RD-09 | Pilot duration too short for a valid statement on production quality | 🟡 Medium | Project Planning |
| RD-10 | Technology available in pilot, but production licences not planned / too expensive | 🔴 High | IBM Commercial / Customer |

---

### 3B · Technical Risks (RT codes)

> These risks concern the **technical feasibility and quality** of the AI solution.
> They arise from data gaps, integration hurdles, model weaknesses, or compliance requirements.
> They are generally addressed **during the pilot** and sit in the responsibility of
> architecture, data science, and IT operations.
>
> **CE alignment:** RT-01 and RT-02 must be resolved by end of **Envision** (before Empower).
> A PoC built on sandbox data that does not reflect production is not a valid CE deliverable.

| Code | Technical Risk | Typical Score | Who must act |
|---|---|---|---|
| RT-01 | Production data deviates significantly from pilot data (sanitised sandbox ≠ reality) | 🔴 High | Data Engineer / Architect |
| RT-02 | No technical access to the source system (no API, only manual export) | 🔴 High | Customer IT / Architect |
| RT-03 | Integration into legacy systems technically not feasible within the pilot scope | 🔴 High | Architect / IBM App Connect |
| RT-04 | Extraction scope unclear — what is read from the source object? (text, attachments, images, metadata) | 🟠 Medium-High | Data Engineer / Business |
| RT-05 | RAG system / vector store missing — knowledge base not available in structured form | 🟠 Medium-High | Architect / Data Engineer |
| RT-06 | Latency and scalability requirements under production load not tested | 🟠 Medium-High | Architect / DevOps |
| RT-07 | AI bias or hallucinations not detected in pilot — only visible in production | 🟡 Medium | Data Scientist / QA |
| RT-08 | GDPR / EU AI Act requirements technically not fulfillable with the planned stack | 🟠 Medium-High | Architect / Data Protection Officer |
| RT-09 | Model quality not measurable — no test dataset with ground truth available | 🟡 Medium | Data Scientist |
| RT-10 | Infrastructure (GPU, cloud, storage) not budgeted or not deliverable for production | 🔴 High | IT Operations / Procurement |

---

## Step 4 — Document Open Items

Add to the existing "Open Items" table in the requirements document these
pilot-specific clarification needs (only if not already present):

| Code | Topic | Question |
|---|---|---|
| OP-P01 | Rollout budget | Is a budget for production approved after pilot completion? Who decides? |
| OP-P02 | Operations ownership | Which team takes over operations? When does the handover begin? |
| OP-P03 | Production data | When will real production data be included in the pilot? |
| OP-P04 | Licensing | Are production licences for all technologies in use planned and budgeted? |
| OP-P05 | Enablement | What training is planned for the operations team? |
| OP-P06 | Go/No-Go criteria | Which measurable criteria decide whether the pilot continues or stops? |
| OP-P07 | EU AI Act | Which risk category does the system fall into under the EU AI Act? Who is responsible? |
| OP-P08 | CE phase gate | Which CE phase is the engagement currently in, and are all gate criteria for the next phase met? |

---

## Step 5 — Create the Output

Choose the appropriate output format based on context:

### Option A — Extend Existing Documents
If analysis / requirements / risk list files are present:
- Extend the risk list with the relevant risks as R-XX entries
- Add a new section **"Pilot Risks"** to the analysis file
- Add new open items OP-Pxx to the requirements file
- Update the summary overview table in the risk list
- Add a **CE Phase Gate Status** section showing current phase and unresolved blockers

Use `insert_content` for targeted additions — do not overwrite entire files.

### Option B — New Standalone Document
If no project context exists, create:
```
documents/analysis/[projectname]_pilot_risk_list.md
```
With sections: Assessment schema → Checklist result → Risk list → Open items →
Immediate actions → **CE Phase Gate Status**.

---

## Step 6 — Prioritise Immediate Actions

Always at the end: list of items to be resolved **before pilot start** (score 🔴 High),
mapped to the CE phase gate they block:

```markdown
## Immediate Actions — Pilot (before start)

### Discover → Envision gate blockers
1. **RD-01** — Nominate management sponsor and document commitment
2. **RD-03** — Obtain formal commitment of customer resources (data, experts, IT access)
3. **RT-02** — Confirm technical system access (API / connector) or declare integration out of scope

### Envision → Empower gate blockers
4. **RD-02** — Have sponsor approve rollout budget and roadmap  ← resolves OP-P01
5. **RD-08** — Define and document Go/No-Go criteria with measurable thresholds  ← resolves OP-P06
6. **RT-01** — Obtain production data sample and include it in the pilot test run  ← resolves OP-P03

### Empower → Production gate blockers (plan now, execute later)
7. **RD-10** — Calculate and approve production licence costs  ← resolves OP-P04
8. **RT-08** — Conduct EU AI Act risk classification and GDPR / DPIA review with Data Protection Officer  ← resolves OP-P07
9. **RT-10** — Confirm CE phase gate criteria are met and document current phase status  ← resolves OP-P08
```

---

## Quality Assurance

Before delivering the output, verify:
- [ ] Every new risk has a unique ID (no duplicates with existing R-xx entries)
- [ ] **Delivery risks (RD)** and **technical risks (RT)** are documented in separate sections in the risk list
- [ ] All RD codes (01–10) have been assessed — even if classified as "not applicable"
- [ ] All RT codes (01–10) have been assessed — even if classified as "not applicable"
- [ ] The category field of every risk contains either "AI Pilot / Delivery" or "AI Pilot / Technical" — never both
- [ ] Open items are phrased as questions, not as statements
- [ ] Recommendations name a concrete action **and** an owner
- [ ] Immediate actions (Delivery) are marked as "before pilot start"
- [ ] Immediate actions (Technical) are marked as "during pilot" or "before go-live"
- [ ] Every risk is mapped to a **CE phase gate** (Discover / Envision / Empower)
- [ ] The output includes a **CE Phase Gate Status** table showing which gates are cleared and which are blocked
- [ ] The CE Phase Gate Status table is **populated** — each phase row has a Cleared/Blocked status and lists the blocking RD/RT codes (not left blank)
- [ ] All OP-P01 through OP-P08 open items appear in the output document (or are explicitly marked as not applicable with a reason)
