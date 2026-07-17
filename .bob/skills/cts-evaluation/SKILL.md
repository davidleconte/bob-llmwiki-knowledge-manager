---
name: cts-evaluation
description: Evaluate a Client Technical Strategy and provide recommendations for improvement
---

# Evaluating a Client Technical Strategy (CTS)

Evaluate a supplied CTS along with any supporting documentation (e.g., client financial reports, information on the client's IT environment, organization charts, personal notes on buying behaviours, informal and formal power structures, ISC data, etc.) to test for completeness, challenge unstated assumptions, and identify potential gaps or blind spots. Be critical but constructive.
 
Refer to the `cts.md` rule for the canonical definition of CTS components, and use the criteria below as your evaluation framework.

---

## Evaluation Framework

Assess the CTS across the following six dimensions. Score each dimension from 1–10, then produce a single weighted composite score out of 10 and a prioritized set of recommendations.

---

### Dimension 1: Strategic Grounding (Weight: 25%)

Does the CTS reflect a genuine understanding of the client's business and the external forces acting on it?

**Evaluate:**
- Is each Strategic Initiative clearly aligned to an executive-visible client business priority — not an IBM product priority?
- Do the SIs pass the **"press interview test"** — could the client quote any SI name in a board presentation or press interview without it sounding like an IBM sales pitch?
- Is the CTS grounded in data (financial targets, analyst reports, regulatory requirements, market trends)? Are business metrics, targets, and expected outcomes supported by evidence rather than supposition?
- Does the ATL demonstrate knowledge of the client's industry, competitive landscape, and macro environment?
- Is there a clear AS-IS / TO-BE narrative — does the CTS establish where the client is today on IBM platform adoption and articulate a credible, phased path to the desired future state?

**Red flags:**
- SIs named after IBM products (e.g., "Deploy watsonx") rather than client outcomes.
- No reference to the client's stated business strategy, annual report, or public priorities.
- Unsupported assertions about client needs or expected outcomes.

---

### Dimension 2: Strategic Initiative Quality (Weight: 25%)

Are the SIs well-formed, client-driven, and IBM-material?

**Evaluate each SI against the three mandatory criteria:**
1. **Client-driven:** Aligned to a significant client priority or objective that is visible to the client's executive management team, shareholders, or customers.
2. **Material to IBM:** Drives meaningful revenue and/or software consumption; involves multiple IBM products and/or platforms; justifies IBM investment.
3. **Linked to milestones:** Each active SI has at least one linked ISC Opportunity (new acquisition) or Success Plan (consumption of entitled software). An SI with no linked opportunities should be flagged as a red flag — if the team is not pursuing it, it should be marked inactive.

**Also evaluate:**
- Are the SI names and descriptions written in the client's voice?
- Does each SI include: the client business objective, a stated or implied outcome metric, and a high-level IBM solution approach?
- Is there an appropriate number of SIs? Too few may indicate a shallow strategy; too many (especially if they overlap significantly) may indicate lack of focus.
- Does the set of SIs cover an appropriate breadth of IBM platforms? Or is the CTS over-concentrated in one area while ignoring relevant platform opportunities?
- Has a client priority been over-simplified into one SI when it should be decomposed? Or has it been fragmented unnecessarily?

**Red flags:**
- SIs with no linked Opportunities or Success Plans.
- SI descriptions that read as IBM product pitches.
- All SIs in a single IBM platform with no exploration of adjacent platforms.
- SIs with no stated client business objective or measurable outcome.

---

### Dimension 3: Initiative Architecture Quality (Weight: 15%)

Does each SI have a credible, clearly communicated solution architecture?

**Evaluate:**
- Does each SI have at least one conceptual or logical architecture diagram?
- Does each architecture show: existing IBM components, new IBM components, key integration points with non-IBM systems, key user communities and their interaction with the solution, high-level placement in the client's IT infrastructure, and the transition path from AS-IS to TO-BE?
- Are the architectures consistent with the IBM product portfolio and current best practices for the platforms referenced?
- Are architectures drawn at an appropriate level of abstraction for the stage of the SI (conceptual early, logical/detailed as the SI matures)?
- Do the architectures reflect any stated deployment constraints (on-premises, cloud, hybrid, edge)?

**Red flags:**
- SIs with no architecture.
- Architectures that show only new IBM products with no integration into the client's existing environment.
- Architectures that are inconsistent with the IBM platform capabilities described.

---

### Dimension 4: Execution Plan and ISC Hygiene (Weight: 20%)

Is the CTS backed by a credible, current execution plan with appropriate team alignment?

**Evaluate:**
- Does each SI have a Technical Sales Activity Plan (TSAP) with identified milestones, activity types, owners, and target dates?
- Are activity ownership assignments realistic and appropriate?
  - ATL: Architecture activities, executive engagements, SI-level coordination.
  - CSEs / BTS: Demo and product-level activities, Success Plans.
  - Client Engineering (CE): Pilot activities exclusively.
  - PTAs: Deep platform technical design and briefings.
  - CSMs: Post-sale deployment and consumption.
- Is there evidence of PoX (Proof of eXperience) activities — pilots, workshops, bootcamps, demonstrations — planned or in progress for Priority accounts? PoX coverage is a primary KPI.
- Are ISC records current? Are status updates recent? Are next-action dates in the future and realistic?
- Are all active SIs linked to open Opportunities or Success Plans?
- Are stale or completed SIs marked as inactive?

**Red flags:**
- No Technical Sales Activities logged, or TSAs that are months out of date.
- Next-action dates that have passed with no update.
- Active SIs with only closed opportunities.
- Pilot activities assigned to the ATL (these belong exclusively to CE).
- No PoX activities planned for Priority accounts.

---

### Dimension 5: Team and Stakeholder Coverage (Weight: 10%)

Does the CTS reflect effective orchestration of the IBM technical team and appropriate engagement across client stakeholders?

**Evaluate:**
- Are the right IBM team members (CSEs, PTAs, CE, Z Architects, PTAs, CSMs) engaged and assigned to activities?
- Does the CTS reflect engagement with both business and IT stakeholders at the client? For Priority accounts, is there access to or a plan to develop access to executive and senior business leaders?
- Is the client relationship map reflected? Are there identified supporters, detractors, and neutrals?
- Is the ISC Relationship Barometer current?
- Is the IBM account team aligned — is the TSL/MD co-sponsoring the CTS direction?
- For Squad ATLs: is the account correctly categorized (Priority / Land and Expand / Deployment / Invest) and is the level of CTS investment appropriate for that category?

**Red flags:**
- No business stakeholder engagement — CTS covers only IT contacts.
- No identified executive sponsor on either the IBM or client side for major SIs.
- Account categorization that doesn't match the level of investment or activity.

---

### Dimension 6: Portfolio Breadth and IBM Platform Alignment (Weight: 5%)

Does the CTS advance IBM's technology platform strategy across a healthy breadth of the portfolio?

**Evaluate:**
- Across all SIs, what IBM Technology platforms are represented: Data, Automation, Hybrid Cloud (Red Hat), Transaction Processing (IBM Z), Infrastructure?
- Is there a plausible strategic reason for any platform with no coverage (e.g., no mainframe in a pure cloud-native startup)?
- Are the IBM Sales Plays identified for each SI? Are the right Sales Plays selected?
- Does the CTS contribute to the SI dashboard metrics: account engagement breadth, ATL impact, IBM agenda advancement, and portfolio breadth?

**Red flags:**
- All SIs in a single platform with no rationale for the gap.
- No IBM Sales Plays identified.
- CTS that does not mention Hybrid Cloud / AI strategy at all, given IBM's mission to win Hybrid Cloud and AI.

---

## Scoring and Output

After evaluating all six dimensions:

1. **Score each dimension** from 1–10.
2. **Calculate the weighted composite score:**
   - Strategic Grounding: ×0.25
   - SI Quality: ×0.25
   - Execution Plan and ISC Hygiene: ×0.20
   - Initiative Architecture Quality: ×0.15
   - Team and Stakeholder Coverage: ×0.10
   - Portfolio Breadth and IBM Platform Alignment: ×0.05
3. **Round the composite to one decimal place.**

Present your evaluation in this structure:

### CTS Evaluation Summary

**Client:** [Client name]
**Overall Score: [X.X] / 10**

| Dimension | Score | Weight | Weighted Score |
|---|---|---|---|
| Strategic Grounding | X/10 | 25% | X.XX |
| SI Quality | X/10 | 25% | X.XX |
| Execution Plan and ISC Hygiene | X/10 | 20% | X.XX |
| Initiative Architecture Quality | X/10 | 15% | X.XX |
| Team and Stakeholder Coverage | X/10 | 10% | X.XX |
| Portfolio Breadth and IBM Platform Alignment | X/10 | 5% | X.XX |
| **Composite** | | | **X.XX** |

---

**Strengths**
[Concise bullets on what the CTS does well.]

**Key Findings and Gaps**
[Numbered list of the most significant issues, ordered by impact.]

**Recommendations**
[Numbered, prioritized, actionable recommendations. For each: what to do, why it matters, and who should own it.]

**SI-Level Findings**
[For each SI: a one-line assessment and any specific concerns or recommendations.]

---

Be specific and evidence-based throughout. If a weakness is identified, explain precisely what evidence is missing or what needs to change. If a gap is identified, suggest what a better approach would look like. The goal of the evaluation is to help the ATL strengthen the CTS — not merely to score it.
