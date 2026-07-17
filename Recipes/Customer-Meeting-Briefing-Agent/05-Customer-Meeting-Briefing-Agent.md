# Use Case - Customer Meeting Briefing Agent
## Bob MODE: pre-sales-demo-mode.yaml

Why this is a strong test: Senior customer-facing executives do not need another generic chatbot or document summary demo. They need fast, credible meeting intelligence before a high-stakes customer engagement. This recipe demonstrates how an executive can build a customer briefing agent that combines public financial signals, uploaded company filings, and meeting context into a concise executive briefing suitable for account planning, board-level customer conversations, and strategic client preparation.

Cluster: Executive Decision Intelligence · Industry: Cross-Industry / Enterprise Sales / Consulting · Output shape: customer briefing + financial KPI snapshot + PDF-derived executive insights + meeting-specific talking points

### EXECUTIVE NARRATIVE

Imagine you are preparing for a strategic customer meeting tomorrow morning.

The customer is a large enterprise.
The meeting is with a CFO, CTO, business unit leader, or transformation executive.
The topic may be cloud modernization, ERP transformation, AI strategy, cost optimization, operational efficiency, or growth.

Normally, preparation is fragmented.

Someone reviews the annual report.
Someone checks the stock price.
Someone scans recent financial performance.
Someone looks for risks and strategic priorities.
Someone turns all of this into a briefing deck.

The Customer Meeting Briefing Agent compresses that process into a few minutes.

An executive selects a company scenario such as IBM, SAP, or Microsoft — or enters a public ticker — then provides meeting context. The agent retrieves financial signals, analyzes company materials, and produces a meeting-ready briefing with:

- Current financial snapshot
- Strategic priorities
- Customer business pressures
- Three executive talking points
- Recommended questions
- Risks, opportunities, and transformation themes
- Meeting-specific insights and recommended posture

The goal is not to replace account teams.

The goal is to give senior leaders a faster way to prepare for high-value conversations with sharper context, better questions, and more strategic relevance.

### USE CASE DESCRIPTION

Revised pick: Customer Meeting Briefing Agent — PDF + yfinance only

The pitch in one line:

> “Drop in their latest 10-K or analyst report, type their ticker, get a briefing with financial snapshot, strategic priorities, and three talking points — in under a minute.”

This has the same WOW factor as more complex agentic demos but with much less integration risk.

The data inputs are things every general manager, account executive, or consulting leader already understands:

- A public company ticker
- A 10-K, 20-F, annual report, investor report, or analyst report
- A meeting context

The demo remains practical because it avoids heavy enterprise integration dependencies. It can use ALPHA VANTAGE or an equivalent free market data library for the financial snapshot, and uploaded PDFs for document intelligence.

The ReAct / agent loop is still legible because the agent uses different kinds of tools:

- A numeric market data tool
- A document analysis tool
- A synthesis tool

This makes it easier for executives to understand what the agent is doing and why the output is useful.

### PRE-LOADED PRESET SCENARIOS

For the live demo, Bob ships three preset PDFs in the repo so the presenter does not have to upload files or type during the demo:

- IBM 10-K excerpt + ticker IBM
- SAP 20-F excerpt + ticker SAP
- Microsoft 10-K excerpt + ticker MSFT

These are public documents, so there is no compliance issue.

The executive selects one from a Carbon dropdown, hits Run, and watches the trace stream.

### PREPARATION
- IBM Bob access
- Python 3.11+
- Node.js / npm for React frontend
- IBM watsonx.ai credentials
- Access to meta-llama/llama-3-3-70b-instruct on watsonx.ai
- Alpha Vantage API key - get your FREE key from here: https://www.alphavantage.co/support/#api-key
- yfinance or equivalent free financial market data source
- Sample public PDF excerpts for IBM, SAP, and Microsoft
- Local demo laptop setup without containers if needed

Environment variables:

WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
ALPHA_VANTAGE_API_KEY= (optional)

### PROMPT #1

```text
Build an IBM Customer Briefing Agent designed for executive customer preparation and financial intelligence. The application has two business-facing experiences: Customer Briefing and Executive Insights. Backend is FastAPI with a LangGraph orchestration layer powered by
meta-llama/llama-3-3-70b-instruct on watsonx.ai. Frontend is React + Carbon v11 with a polished IBM-inspired dark enterprise interface and a
persistent top navigation containing Customer Briefing and Executive Insights.

The Customer Briefing experience generates AI-powered meeting preparation for enterprise customer engagements. The user selects a preset
scenario (SAP, IBM, Microsoft) or enters a custom public stock ticker, then provides a meeting context (for example: Executive briefing
with CFO – Cloud transformation and ERP modernization). The backend uses a fetch_market_snapshot(ticker) capability powered by live market
data (Alpha Vantage or equivalent) to retrieve market signals, valuation metrics, analyst sentiment, and company context.
A synthesize_briefing(market, meeting_context) workflow generates structured JSON rendered in the UI.

The briefing page should display executive KPI cards including Current Price, Market Cap, P/E Ratio, and Analyst Rating, followed by
Strategic Priorities, Three Key Talking Points, and Recommended Questions tailored to the meeting scenario. The tone should feel like
an enterprise consulting briefing created for senior account executives preparing for a customer conversation.

The Executive Insights experience analyzes uploaded financial documents. The user uploads a PDF (10-K, 20-F, Annual Report,
Investor Report - max 10 MB) and optionally provides a company name and meeting context. A document analysis pipeline (analyze_uploaded_document(path)) chunks the PDF and extracts strategic priorities, business risks, financial trends, competitive positioning, growth opportunities,
and executive signals. A structured synthesis workflow (generate_executive_insights(doc_analysis, meeting_context)) produces
executive-level JSON for rendering.

Results are displayed in a polished executive report layout beginning with an Executive Summary, followed by expandable accordion sections including Strategic Positioning, Financial Health, Risk Assessment, Growth Opportunities, Executive Actions, and Meeting-Specific Insights. The experience
 should feel premium, structured, and executive-facing rather than technical or experimental. Ship demo-ready operation with preconfigured
sample scenarios and graceful mock-mode support for live demonstrations.
```

### PROMPT A - Start locally with credentials

```text
Start the application for me on the local laptop, without containers by using thouse credentials you can store in the .env file.

WATSONX_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
WATSONX_PROJECT_ID=zzzzzzzzzzzzzzzzzzzzzzzzz
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

### PROMPT #2

```text
Make the application feel polished and executive-grade with progressive system feedback and structured insight rendering. When a document is uploaded and Generate Executive Insights is triggered, display a multi-step analysis experience showing progress through Extracting Text, Strategic Analysis, and Generating Insights, with subtle enterprise animations, progress indicators, and loading states. The interface should reassure the user that analysis is actively happening rather than freezing or waiting silently.

After generation completes, render insights in expandable executive accordions instead of long text blocks. Strategic Positioning should summarize competitive moat, value creation model, strategic bets, and disruption vulnerability. Financial Health should include revenue quality, profitability trends, cash generation, capital efficiency, and balance sheet signals. Risk Assessment should surface critical risks with impact and likelihood indicators, emerging risks, and overall risk appetite. Growth Opportunities should distinguish organic levers, inorganic opportunities, digital transformation, and sustainability themes. Executive Actions should produce immediate recommendations, expected impact, key management questions, red flags, and quick wins.

The Customer Briefing experience should feel immediate and concise, rendering executive insights in a meeting-ready format with financial KPI cards, strategic priorities, talking points, and recommended questions. Use clean enterprise spacing, muted dark visuals, IBM blue accents, Carbon styling, accordion sections, and executive typography throughout.
```

### PROMPT B - Start and test

```text
Start the application for me on the local laptop and test it.
```

### PROMPT #3

```text
Enhance the intelligence layer so outputs feel tailored to executive customer engagements instead of generic AI summaries. The Customer Briefing
experience should synthesize market signals, analyst sentiment, strategic positioning, and meeting context into highly contextual executive
 preparation material. Three Key Talking Points should explicitly connect the customer’s current priorities, transformation themes, and
business pressures to likely executive interests for the meeting. The Recommended Questions section should generate thoughtful,
commercially relevant questions that an enterprise account executive or consulting leader would realistically ask during a senior customer conversation.

For Executive Insights, use uploaded financial documents to infer business strategy, investment themes, operational pressures, and
transformation priorities. When a meeting context is provided (for example: Meeting with the R&D CTO on Agentic AI lead research),
generate Meeting-Specific Insights including tailored talking points, anticipated executive questions, likely objections or concerns,
and a recommended meeting posture. Include Immediate Decisions (Next 90 Days), Quick Wins (30–60 Days), and Red Flags in a format
suitable for executive preparation.

The overall experience should feel like an internal IBM executive briefing platform — premium, credible, concise, strategically useful,
and optimized for live demonstrations with realistic enterprise outputs rather than generic AI-generated prose.
```

### EXPECTED OUTPUT
- Carbon React IBM Style executive application
- Persistent top navigation with Customer Briefing and Executive Insights
- FastAPI backend
- LangGraph orchestration layer
- watsonx.ai integration using meta-llama/llama-3-3-70b-instruct
- Market data capability using yfinance, Alpha Vantage, or equivalent
- PDF upload and document analysis pipeline
- Preconfigured sample scenarios for IBM, SAP, and Microsoft
- Customer Briefing page with KPI cards:
  - Current Price
  - Market Cap
  - P/E Ratio
  - Analyst Rating
- Strategic Priorities section
- Three Key Talking Points section
- Recommended Questions section
- Executive Insights page with:
  - Executive Summary
  - Strategic Positioning
  - Financial Health
  - Risk Assessment
  - Growth Opportunities
  - Executive Actions
  - Meeting-Specific Insights
- Progressive analysis feedback:
  - Extracting Text
  - Strategic Analysis
  - Generating Insights
- Expandable executive accordions
- Mock-mode support for live demonstrations
- README, Architecture, PILOT Plan and setup guide

### DEMO SCRIPT

1. Open the IBM Customer Briefing Agent.
2. Select a preset scenario from the dropdown:
   - IBM
   - SAP
   - Microsoft
3. Confirm or edit the meeting context, for example:
   - Executive briefing with CFO – Cloud transformation and ERP modernization
   - Meeting with CTO – Agentic AI and research productivity
   - Strategic account review – Cost optimization and platform modernization
4. Click Run / Generate Briefing.
5. Show the financial KPI cards.
6. Walk through Strategic Priorities.
7. Highlight the Three Key Talking Points.
8. Show Recommended Questions as the executive-ready output.
9. Navigate to Executive Insights.
10. Use the preloaded PDF or upload a sample public filing.
11. Trigger Generate Executive Insights.
12. Let the progress states appear:
   - Extracting Text
   - Strategic Analysis
   - Generating Insights
13. Open the accordions:
   - Strategic Positioning
   - Financial Health
   - Risk Assessment
   - Growth Opportunities
   - Executive Actions
   - Meeting-Specific Insights
14. Close with the point that the executive now has a customer-ready briefing in under a minute.

### SAMPLE MEETING CONTEXTS

Use these during a live demo:

```text
Executive briefing with CFO – Cloud transformation, ERP modernization, and cost optimization.
```

```text
Meeting with CTO – Agentic AI, research productivity, and software engineering transformation.
```

```text
Strategic account review with CEO – Growth strategy, operational resilience, and digital platform modernization.
```

```text
Meeting with Chief Procurement Officer – Vendor consolidation, long-term platform value, and business case discipline.
```

```text
Board-level customer conversation – AI adoption, risk governance, productivity, and enterprise transformation.
```

### WHAT GOOD LOOKS LIKE

A strong generated briefing should feel like something a senior IBM account executive or consulting partner would use before a customer meeting.

It should be:
- concise
- commercially useful
- tied to financial signals
- grounded in the customer context
- specific to the meeting objective
- written in executive language
- free from generic AI filler

The output should not simply summarize a company.

It should answer:

> “What should I know, say, ask, and watch for in this customer conversation?”

### EXECUTIVE TAKEAWAY

At the end of this lab, the executive takeaway should be simple:

> “AI can help me prepare for high-stakes customer meetings by combining financial context, public company documents, and meeting objectives into a concise executive briefing.”

This is not a toy application.

It is a practical example of how agentic AI can improve preparation quality, commercial relevance, and decision speed for enterprise customer engagements.
