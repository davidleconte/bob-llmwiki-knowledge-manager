---
name: cts-creation
description: Generate a Client Technical Strategy (CTS) for an IBM account
---

# Creating a Client Technical Strategy (CTS)

A Client Technical Strategy (CTS) is the ATL's primary work product. It is a comprehensive strategy and plan to advance a client's business and technology objectives through IBM technology, driving near-, mid-, and long-term opportunities, revenue, and deployments. Refer to the `cts.md` rule for the canonical definition of CTS components.

## Step 1: Gather Client Information

Before drafting anything, assemble as complete a picture of the client as possible. Use all available sources:

**Public sources**
- Client website (annual reports, press releases, investor relations pages, strategy presentations)
- Industry and financial analysts (Gartner, Forrester, IDC, S&P, sector-specific reports)
- News articles, earnings calls, regulatory filings
- Client's published technology roadmaps, job postings (reveal technology investments), and conference presentations
- Use only recent sources (within 2 years of current year). I you do not know the current year, ask the user.

**Internal IBM sources**
- IBM Sales Cloud (ISC): existing Strategic Initiatives, Opportunities, Success Plans, Technical Sales Activities, and the Relationship Barometer
- Software installation records and entitlement data (what the client already owns and is licensed for)
- Support ticket history (reveals pain points and operational friction)
- Prior CTS documents, briefing notes, and account plans
- Input from the extended technical team: CSEs, PTAs, CE, Z Architects, CSMs

**Contextual knowledge**
- Industry trends, competitive landscape, and regulatory environment relevant to the client's sector
- IBM Sales Plays applicable to the client's industry and stated priorities
- IBM platform adoption patterns in comparable accounts

**Ask the IBM account team:**
- Who are the key business and IT stakeholders? What are their priorities and concerns?
- What is the client's IT spend profile and where is budget being allocated?
- What is the existing IBM install base and where are there known gaps or renewal risks?
- What are the current active and stalled opportunities, and why?
- What is the relationship health (supporters, detractors, neutrals)?
- What is the client's "propensity to modernize" — are they early adopters or risk-averse?

## Step 2: Conduct an AS-IS / TO-BE Assessment

Before drafting SIs, establish a baseline and a vision:

**AS-IS Assessment**
- Document the client's current IBM Platform adoption across the five platforms: Data, Automation, Hybrid Cloud (Red Hat), Transaction Processing (IBM Z), and Infrastructure.
- Map which IBM products the client owns, is actively using, and is entitled to but not consuming.
- Identify the client's existing technology architecture (business, application, data, and technology layers).
- Note key competitors' technologies deployed in the account and areas of IBM "white space."

**TO-BE Vision**
- Based on the client's stated business priorities, define the target-state IBM Platform architecture.
- Identify which IBM platforms and products are most relevant to the client's strategic direction.
- Assess which IBM Sales Plays are most applicable.

This AS-IS / TO-BE framing is the foundation of the CTS and every SI within it.

## Step 3: Define Strategic Initiatives (SIs)

Strategic Initiatives are the core of the CTS. Each SI represents a significant client-driven priority that IBM technology can address. Draft them following these rules:

**SI quality criteria — every SI must be:**
1. **Client-driven.** Aligned to an executive-visible business or technology priority. A good test: would the client quote this SI in a press interview or board presentation? "Reduce operational costs by automating IT lifecycle management" is an SI. "Purchase the IBM ELA" is not.
2. **Material to IBM.** Driving meaningful revenue and/or software consumption; involving multiple IBM products and/or platforms; worth IBM investment.
3. **Linked to milestones.** Each SI must have at least one associated ISC Opportunity (for new acquisitions) or Success Plan (for consumption of already-entitled software).

**SI framing guidance:**
- Write the SI name and description from the client's perspective, in their voice.
- The description should capture the client's business objective and why it matters to their executive team.
- Map the client objective to IBM technology capabilities — not the other way around.
- A client priority may need to be decomposed into multiple SIs. For example, "Become the #1 digital bank in the region" might yield SIs for "Drive cross-sell and upsell with customer data", "Secure digital services and data infrastructure", and "Modernize application delivery for digital channels."

**For each SI, document:**
- **Name:** A client-perspective label for the initiative.
- **Description:** The client business objective and its strategic significance.
- **Estimated value:** A rough US dollar estimate (ISC will refine this as opportunities are linked).
- **IBM approach / Comment:** The high-level IBM technology and solution approach.
- **IBM and client leaders:** The IBM leader (typically the ATL) and the highest client owner with day-to-day accountability.
- **IBM Sales Plays:** All applicable Sales Plays.
- **IBM Technology Platforms:** All relevant platforms (Data, Automation, Hybrid Cloud, Transaction Processing, Infrastructure).
- **Linked Opportunities and Success Plans:** The ISC milestones associated with this SI.

**Breadth check:** Across all SIs, does the CTS cover an appropriate breadth of IBM platforms? A good CTS should not be concentrated in a single platform unless the account genuinely has no footprint elsewhere.

## Step 4: Develop Initiative Architectures

For each Strategic Initiative, create at least one conceptual or logical architecture diagram. Use the `draw-io` skill to generate draw.io XML. Follow the `architecture-diagrams.md` rule for visual standards.

Each initiative architecture should show:
- Key **existing IBM components** in the client's environment relevant to the SI.
- Key **new IBM components** being introduced or expanded.
- Non-IBM components where relevant to show integration and context.
- **Key user communities** and how they interact with the solution in the context of key business processes.
- **High-level placement** within the client's IT infrastructure and business locations (e.g., on-premises, cloud, edge).
- **Key implementation phases or milestones** in the transition from the client's current (AS-IS) architecture to the future-state (TO-BE) solution.

Avoid over-indexing on the AS-IS in early design stages — focus on the TO-BE and work backwards. Too much AS-IS analysis early tends to bake in current constraints.

## Step 5: Build the Technical Sales Activity Plan (TSAP)

For each SI, document the major milestones and technical sales activities required to achieve it. The TSAP bridges strategy and execution. For each milestone:

- **Milestone description:** What must be achieved (e.g., "Complete executive AI briefing with CTO", "Deliver watsonx Orchestrate pilot").
- **Activity type:** Architecture, Demo, Pilot, Briefing, Workshop, etc.
- **Owner:** Which team member is responsible.
  - ATL: Architecture activities, executive engagements, SI management.
  - CSEs / BTS: Demo activities, product-level technical battles, Success Plans.
  - Client Engineering (CE): Pilot activities exclusively — ATLs do not own or create Pilot TSAs.
  - PTAs: Deep platform-level technical design and briefings.
  - CSMs: Post-sale deployment and consumption tracking.
- **Target date / next action date:** When will this occur.

Log all Technical Sales Activities in ISC at the lowest meaningful level of the hierarchy: Opportunity > Strategic Initiative > Account.

## Step 6: Add Supporting Documentation (as required)

Your geography or market leadership may require additional CTS documents. Templates are available at the WW ATL site (https://w3.ibm.com/w3publisher/ww-sales-engineering/atl). These may include:

| Document | Purpose |
|---|---|
| **Client Profile** | Key facts about the client, their industry, and organizational structure. |
| **Client Technology Landscape** | IBM and competitor technologies in the client's enterprise; white space and unknown areas. |
| **Client Technology Roadmap** | A multi-year plan to evolve the client's technology architecture to an IBM-enabled future state. |
| **Deployment Plan** | A multi-year plan to implement and maximize value from IBM technologies the client already owns (e.g., via ELA). |
| **Strategic IBM Platform Growth Ambition Assessment** | Assessment of opportunities to grow IBM Platform presence in the client's IT landscape. |

## Step 7: Enter and Maintain in ISC

Once the CTS is drafted, ensure all components are captured in IBM Sales Cloud:

1. Create or update **Strategic Initiatives** in the Account's Planning section.
2. Create **placeholder Opportunities** (nominally valued, Engage stage) for products in the notional solution; transfer ownership to the appropriate seller.
3. **Link Opportunities and Success Plans** to their parent SIs.
4. Log an initial **Technical Status TSA** for each SI summarizing the current state and next action with a target date.

**Good ISC hygiene from day one:**
- Every active SI must have at least one linked open Opportunity or Success Plan.
- Status updates must be current — stale next-action dates are a red flag.
- Use Technical Status TSAs to communicate SI progression to the team and leadership.

## CTS Output Format

Present the CTS as a structured document with the following sections:

1. **Executive Summary** — A one-page summary of the client, their strategic priorities, and IBM's overall approach. Written for a senior IBM or client executive audience.
2. **Client Overview** — Key facts about the client's business, industry, and technology environment.
3. **Strategic Initiatives** — One section per SI, each containing: SI name, description, business objective, IBM approach, initiative architecture diagram, and linked milestones.
4. **Technical Sales Activity Plan** — The consolidated activity plan across all SIs.
5. **Supporting Documentation** — Any additional documents required by geography/market leadership.

Ensure the CTS is grounded in data. Business metrics, targets, and expected outcomes must be supported by client, industry, or third-party data. Decisions, assumptions, and product recommendations must be supported by logical rationale — not supposition.
