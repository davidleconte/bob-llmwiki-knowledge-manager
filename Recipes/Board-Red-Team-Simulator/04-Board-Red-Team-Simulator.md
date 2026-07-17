# Use Case - Board Red Team Simulator
## Bob MODE: pre-sales-demo-mode.yaml

Why this is a strong test: Executive leaders do not need another chatbot demo. They need to experience AI as a strategic thinking partner. This lab demonstrates how an executive can build a board-level “red team” that pressure-tests strategy before major investment or organizational commitment.

Cluster: Executive Decision Intelligence · Industry: Cross-Industry · Output shape: multi-agent board critique + executive memo + optional live market signals

### EXECUTIVE NARRATIVE

Imagine you are about to present a major strategic initiative to your Board.

A €20M GenAI investment.
A market expansion.
A reorganization.
A new platform bet.

Normally, the difficult questions arrive in the boardroom.

The Board Red Team Simulator brings those questions forward — before the meeting happens.

Executives paste a strategy and receive structured challenges from:
- CFO
- Activist Investor
- Regulator
- Competitor
- Independent Board Member

Optional external enrichment uses Tavily search to bring current market/company context.

### PREPARATION
- IBM Bob access
- Python 3.11+
- IBM watsonx.ai credentials
- Optional Tavily API key

Environment variables:

WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
TAVILY_API_KEY= (optional)

### PROMPT 1 - Build the core app

```text
Create a serious executive demo app called “Board Red Team Simulator”.

The user should paste a strategic proposal, for example:
“We will invest €20M into GenAI services over 18 months.” for Comoany X

The app should send the proposal to a LangGraph workflow where 5 personas critique it:

1. CFO
2. Activist Investor
3. Regulator
4. Competitor
5. Independent Board Member

Use IBM watsonx.ai as the LLM provider through LangChain.
The UI should look executive-grade: clean, minimal, boardroom style.

Each persona should return:
- Core objection
- Evidence needed
- Hidden assumption
- Risk severity: Low / Medium / High
- One question the board should ask

Do not hardcode fake responses. If watsonx credentials are missing, show a clear setup error.
```

### PROMPT A - Build the core app
```text
Start the application for me on the local laptop, without containers by using thouse credentials you can store in the .env file.

WATSONX_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
WATSONX_PROJECT_ID=zzzzzzzzzzzzzzzzzzzzzzzzz
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

### PROMPT 2 - Refactor into LangGraph

```text
Refactor the app so the red-team process is implemented as a proper LangGraph StateGraph.

Create separate graph nodes for:
- CFO critique
- Activist Investor critique
- Regulator critique
- Competitor critique
- Board Member critique
- Synthesis

Each critique node should call watsonx.ai using ChatWatsonx with model_id="openai/gpt-oss-120b".

The synthesis node should combine the five critiques into an executive board memo with:

1. Overall recommendation:
   - Proceed
   - Proceed with conditions
   - Pause
   - Reject

2. Top 3 strategic risks
3. Top 3 missing facts
4. Strongest challenge from the red team
5. What would make the proposal board-ready
6. A 90-day validation plan

Use structured prompts and return clean Markdown.
Add visible progress in UI while each persona runs.
Keep the implementation simple enough for a 30-minute executive lab.
```

### PROMPT B - Build the core app
```text
Start the application for me on the local laptop and test it.
```

### PROMPT 3 - Executive polish

```text
Add optional external market-signal enrichment before the red-team critique.
Use a free external source that does not require authentication if possible.
Add a text input called “Company / Market / Sector”.

When provided, fetch public context from one or more free sources such as:
- Wikipedia REST API
- Wikidata
- SEC company facts if relevant
- public RSS feeds
- other no-auth public APIs

Summarize the external context into:
- market context
- recent signals
- regulatory considerations
- competitive pressure
- uncertainty / data gaps

Pass this context into every LangGraph persona node.
In the UI, show a collapsible “External signals used” section so executives can see what informed the critique.
Add graceful fallback behavior:
- if the external API fails, continue with the user’s proposal only
- clearly label the output as “not enriched with external signals”

Finally, improve README.md with:
- setup instructions for watsonx.ai
- required .env variables
- how to run the app
- suggested executive demo script
- 3 sample strategy proposals to test
```

### EXPECTED OUTPUT
- Carbon React IBM Style executive application
- LangGraph multi-agent orchestration
- watsonx.ai integration using meta-llama/llama-3-3-70b-instruct
- Optional Tavily enrichment
- Board-ready memo
- Executive UI
- README, Architecture, PILOT Plan and setup guide
