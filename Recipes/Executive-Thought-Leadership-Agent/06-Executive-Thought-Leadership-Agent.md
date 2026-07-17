# Use Case - Executive Thought Leadership Agent
## Bob MODE: pre-sales-demo-mode.yaml

Why this is a strong test: Senior IBM executives do not need another document summarizer or generic content tool. They need a way to produce authentic, credible, strategically grounded thought leadership that genuinely sounds like them — not like a language model. This recipe demonstrates how an executive can build an AI-powered Article Studio that combines live web research, a personal voice profile encoded in a SOUL.md file, and a LangGraph ReAct agent running on IBM watsonx.ai to generate LinkedIn articles that carry real executive gravitas.

Cluster: Executive Decision Intelligence · Industry: Cross-Industry / Enterprise Leadership / IBM Executive Communications · Output shape: executive LinkedIn article + hashtags + voice alignment insights + research trace

---

### EXEC

Imagine you are a C-level executive at IBM.

You have three speaking engagements this week, a board briefing on Friday, and a request from marketing for a LinkedIn article on responsible AI by tomorrow.

Normally you have two options: spend two hours writing it yourself, or hand it to a ghostwriter who will produce something that sounds like a press release.

Neither is good enough.

The Executive Thought Leadership Agent gives you a third path.

You select a topic — AI Governance, Digital Transformation, or Executive Leadership in the Age of AI — then describe your strategic intent in one paragraph. You optionally upload your SOUL.md, a structured voice profile that captures how you write: your tone, your rhythm, your leadership posture, the phrases you actually use.

The agent does the rest.

It researches the topic through live web signals. It infers the strategic implications that matter to a C-suite audience. It applies your voice profile to produce an article that reads the way you think and write — not the way a language model defaults to sounding.

The result is a title, a full article, and LinkedIn hashtags — ready to copy and post in under three minutes.

Six editing actions let you refine it: make it stronger, more provocative, more concise, more visionary, more data-driven, or more personal.

This is not a content generation toy.

It is a practical demonstration of how agentic AI can compress executive communication work from hours to minutes while preserving authenticity and strategic credibility.

---

### WHY SOUL.md IS CRITICAL TO THIS DEMO

**The SOUL.md file is what separates this application from a generic article generator.**

Every executive has a voice. It is the accumulated product of their career, their values, how they structure arguments, the words they prefer, the rhythm of their sentences, and the leadership posture they project.

Anna Paula Assis, for example, opens with societal or macro shifts. She writes in medium-length sentences with clear contrast structures: *"But the real question is..."*, *"At the same time..."*. She uses "we" far more than "I". She never makes technology the hero — people and outcomes are always the hero. She closes with a reflection on leadership responsibility or long-term value creation.

Without the SOUL.md, the agent produces a competent article. A good article. But not *her* article.

With the SOUL.md, the `SOULParser` service reads the raw content of the uploaded file and extracts a structured `VoiceProfile` dataclass: tone, sentence rhythm, vocabulary level, leadership posture, storytelling tendency, key phrases, and writing patterns. This profile is passed through every node of the LangGraph agent — the title node, the article node — bending the LLM's output toward the executive's authentic style.

The `ExecutiveIntelligenceLayer` also uses the voice profile to adjust how it formats strategic implications and transformation themes — choosing collaborative framing for a collaborative voice, authoritative framing for an authoritative voice.

**This is the architecture of authentic AI.**

The SOUL.md is not a system prompt override. It is a structured voice DNA file that an executive can maintain, evolve, and carry from application to application. In a Client Engineering engagement, we would work with the executive's communications team to build a proper SOUL.md over two or three sessions.

#### Sample SOUL.md excerpt — Anna Paula Assis voice

```markdown
# SOUL.md - Ingrid Stark Executive Voice Profile

We are living through one of the most profound technology shifts in history.
But I believe the most important question is not whether technology will transform
our societies — it already is. The real question is how we choose to shape that
transformation and who we bring along in the process.

## AI Writing Instructions

### Tone
- Visionary but grounded
- Optimistic without hype
- Globally minded
- Responsible, ethical, forward-looking

### Sentence Rhythm
- Medium-length sentences
- Frequent contrast structures:
  - "But the real question is…"
  - "At the same time…"

### Writing Rules
DO:
- Use "we" more than "I"
- Frame topics through societal or business impact
- End with action-oriented leadership reflections

DON'T:
- Sound overly promotional
- Make technology the hero — people and outcomes are the hero
```

When this file is uploaded and parsed, the system detects: tone → `visionary`, leadership posture → `collective_action`, storytelling → `moderate`, vocabulary → `thought_leader`. The article generation prompt is then assembled with these characteristics injected as voice instructions, producing output that a communications professional reviewing Anna Paula's LinkedIn posts would recognize as consistent with her actual public writing.

**That is the business value of SOUL.md.**

---

### USE CASE DESCRIPTION

The pitch in one line:

> "Upload your voice profile, describe your topic, and get a publish-ready LinkedIn article in your authentic executive voice — grounded in live research and powered by IBM watsonx.ai."

The data inputs are things every senior leader already understands:

- A topic or strategic theme
- A paragraph describing what you want to say and why
- An optional SOUL.md voice profile file
- An article size preference (100–200, 300–600, or 700–1200 words)

The demo stays practical because there are zero enterprise integration dependencies for the core flow. The entire demo runs locally or on IBM Code Engine with just three environment variables.

The LangGraph ReAct agent is legible because it uses four kinds of tools with a visible reasoning trace:

- A web research tool (Tavily)
- An executive intelligence analysis tool
- A voice profile alignment tool
- Three watsonx.ai generation tools (title, article, hashtags)

This makes the agent architecture easy to explain to both executives and technical buyers. Each step is shown in the UI as a progress step, with the reasoning trace available in the response.

---

### PRE-LOADED PRESET SCENARIOS

For the live demo, the application ships three preset scenarios so the presenter never types during the demo:

- **AI Governance** — Topic: "AI Governance and Trust in Enterprise Deployment" / Intent: "Position myself as a thought leader on responsible AI adoption, emphasizing the balance between innovation speed and governance frameworks."
- **Digital Transformation** — Topic: "Digital Transformation Beyond Technology" / Intent: "Share insights on why digital transformation is 70% about people and culture, not just technology implementation."
- **Executive Leadership** — Topic: "Leadership in the Age of AI" / Intent: "Discuss how C-level executives should approach AI as augmentation rather than replacement."

Clicking any preset tag instantly populates both fields. The presenter clicks Generate and the agent runs.

---

### PREPARATION

- IBM Bob access with `pre-sales-demo-mode.yaml` MODE active
- Python 3.11+
- Node.js 20+ / npm for React frontend
- IBM watsonx.ai credentials (API key + Project ID)
- Access to `meta-llama/llama-3-3-70b-instruct` on watsonx.ai (primary)
- Access to `ibm/granite-3-8b-instruct` as fallback model
- Tavily API key — get a FREE key at https://app.tavily.com (optional; demo runs in mock without it)
- `SOUL.md` file from this repository for the voice profile upload demo

Environment variables:

```
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://eu-de.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
TAVILY_API_KEY=
DEMO_MODE=live
```

---

### PROMPT #1 — Build the full application

```text
Build an IBM Executive Thought Leadership Studio designed for C-level executives who need to generate authentic, executive-grade LinkedIn articles at speed. The application has a single primary experience: the Article Studio. Backend is FastAPI with a LangGraph ReAct orchestration layer powered by meta-llama/llama-3-3-70b-instruct on watsonx.ai. Frontend is React + Carbon v11 with a polished IBM-inspired dark enterprise interface.

The Article Studio experience generates AI-powered LinkedIn articles for executive thought leadership. The user selects a preset scenario (AI Governance, Digital Transformation, Executive Leadership) or enters a custom topic, chooses an article size (Small 100-200 words / Medium 300-600 words / Large 700-1200 words), and writes their executive intent. They optionally upload a SOUL.md voice profile file.

The backend uses a LangGraph ReAct agent with five nodes:
1. research — Tavily web research on the topic (mock mode supported)
2. analyze_voice — parse and apply SOUL.md voice profile via SOULParser
3. strategic_inference — ExecutiveIntelligenceLayer analyzes research through executive lens (strategic implications, executive concerns, transformation themes, industry shifts, leadership lessons, future outlook)
4. generate_title — watsonx.ai generates executive-level title (8-12 words, no clickbait)
5. generate_article — watsonx.ai generates the full article incorporating voice profile instructions and strategic intelligence synthesis
6. generate_hashtags — watsonx.ai generates 5-7 optimized LinkedIn hashtags

Results are displayed with: Executive Title tile, LinkedIn Hashtags tile, Article Preview tile with Copy and Download buttons, Voice Alignment Insights tile (tone, rhythm, posture, storytelling), and Refine Your Article tile with six editing actions: Rewrite Stronger, More Provocative, More Concise, More Visionary, More Data-Driven, More Personal.

Research Sources are shown at the bottom as a trace of what the agent used. Ship with full mock-mode support, progressive ProgressIndicator during generation, and dual-mode (mock/live) operation. Include SOUL.md file in the repo root that encodes the IBM executive voice profile.
```

---

### PROMPT A — Start locally with credentials

```text
Start the application for me on the local laptop, without containers, using those credentials stored in the .env file.

WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://eu-de.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
TAVILY_API_KEY=your_tavily_key_here
DEMO_MODE=live
```

---

### PROMPT #2 — Polish the intelligence layer and UX

```text
Enhance the intelligence layer and UI so the output feels genuinely executive-grade rather than AI-generated. The ExecutiveIntelligenceLayer should analyze research through six lenses: strategic_implications (competitive advantage, risk management, operational excellence, innovation imperative, customer centricity, talent strategy), executive_concerns (board-level, financial impact, market dynamics, regulatory compliance, reputation trust, execution risk), transformation_themes (digital maturity, AI adoption, data-driven, agile operating, ecosystem thinking, sustainability), industry_shifts (percentage change signals from research content), leadership_lessons (content that references leaders, success patterns, key factors), and future_outlook (forward-looking temporal signals).

The voice profile should bend the LLM output for all three generation steps: title generation, article generation, and hashtag generation. Include the intelligence synthesis in the article generation prompt as strategic context the LLM must weave naturally into the writing.

The UI should show a five-step ProgressIndicator during generation: Researching Industry Signals → Understanding Writing DNA → Structuring Thought Leadership → Writing Executive Content → Optimizing for LinkedIn. Each step advances with a ~1.2 second interval. After generation completes, show the Voice Alignment Insights tile only when a SOUL.md was uploaded, showing Tone Match, Rhythm, Leadership Posture, and Storytelling level as a metrics grid.

Make the article preview render markdown bold markers (**text**) as actual bold HTML, not raw asterisks.
```

---

### PROMPT B — Start and test end-to-end

```text
Start the application on the local laptop and run an end-to-end test: generate one article for each of the three preset scenarios in both mock mode and live mode. Verify the ProgressIndicator steps complete, the article content renders with proper markdown, the hashtags appear as Carbon Tags, and the Copy and Download buttons work. Confirm the SOUL.md upload flow parses the voice profile and shows the Voice Alignment Insights tile after generation.
```

---

### PROMPT #3 — Editing actions and refinement loop

```text
Implement the Refine Your Article editing loop. After article generation, show six ghost buttons: Rewrite Stronger, Make More Provocative, Make More Concise, More Visionary, More Data-Driven, More Personal. Each sends the current article content and title to a POST /api/article/edit endpoint along with the selected action and voice profile. The editing prompt should direct watsonx.ai to apply the specific refinement while preserving the executive voice. The response is parsed for TITLE: and CONTENT: sections. On success, update the article in place without resetting other UI state. Show a spinner on the active edit button during processing.
```

---

### EXPECTED OUTPUT

- Carbon React IBM Style executive application — dark g90 theme
- Single-page Article Studio with split left/right layout (lg=8 / lg=8 columns)
- FastAPI backend with lifespan context manager
- LangGraph ReAct agent with 6 nodes and visible reasoning trace
- watsonx.ai integration using meta-llama/llama-3-3-70b-instruct
- Tavily live web research with graceful mock fallback
- SOUL.md parser (SOULParser) extracting VoiceProfile dataclass
- ExecutiveIntelligenceLayer with 6 analytical lenses
- Three article sizes with word count targets
- Six editing/refinement actions
- Left column:
  - Quick Start Scenario Tags (3 presets)
  - Article Topic TextInput
  - Article Size Select (small/medium/large)
  - Executive Intent TextArea
  - SOUL.md FileUploader with parsed voice profile display
  - Generate Article button + Reset button
- Right column (progressive):
  - ProgressIndicator (5 steps) during generation
  - Executive Title tile
  - LinkedIn Hashtags tile
  - Article Preview tile (markdown rendered, Copy + Download)
  - Voice Alignment Insights tile (when SOUL uploaded)
  - Refine Your Article tile (6 ghost action buttons)
  - Research Sources list with URLs
- Mock-mode support with realistic synthetic responses
- DemoBanner sticky disclaimer
- README, ARCHITECTURE.md with Mermaid diagram, PILOT_PLAN.md, DEMO_SCRIPT.md
- SOUL.md in repo root with IBM executive voice profile

---

### DEMO SCRIPT

**Pre-Demo Setup (5 minutes before):**
```
./start.sh   # or: podman-compose up -d
open http://localhost:3000
```
Verify the Article Studio loads, backend health check returns OK.

**Step 1 — Open the application (30 seconds)**

Show the Article Studio. Point to the IBM Carbon dark theme, the DemoBanner disclaimer, and the clean two-column layout. This is built with IBM Carbon Design System v11 — the same design language used across the IBM product portfolio.

**Step 2 — Show the SOUL.md concept (2 minutes)**

Before generating anything, explain what SOUL.md is:

> "What makes this different from ChatGPT is the voice profile. Every executive sounds different. The SOUL.md file captures that — tone, rhythm, how they structure arguments, the words they use. When we upload it, the AI doesn't just generate an article, it generates *their* article."

Upload the `SOUL.md` from the repo root. Show the parsed voice profile that appears: `visionary` tone, `medium_balanced` rhythm, `collective_action` posture. Point to the Tags.

**Step 3 — Select AI Governance preset (30 seconds)**

Click the **AI Governance** blue Tag. Watch both fields populate instantly. This is the first preset scenario. Note how the Executive Intent is already a full strategic paragraph — the presenter never types.

**Step 4 — Generate the article (3 minutes)**

Click **Generate Article**. Walk through the five ProgressIndicator steps as they advance:
- *Researching Industry Signals* — "The agent is running live web research right now"
- *Understanding Writing DNA* — "It's reading the SOUL.md voice profile"
- *Structuring Thought Leadership* — "The intelligence layer is inferring strategic implications"
- *Writing Executive Content* — "watsonx.ai with Llama 3.3 70B is writing the article"
- *Optimizing for LinkedIn* — "Generating hashtags optimized for reach"

**Step 5 — Walk the output (3 minutes)**

- **Title** — "That's an executive-level title. No clickbait, no hype."
- **Hashtags** — "These are already optimized for LinkedIn reach."
- **Article Preview** — Read the opening sentence. Note how it sounds — visionary, contrast structure, "we" not "I", societal framing. "That's the voice profile working."
- **Voice Alignment Insights** — "You can see exactly how the voice profile was applied: visionary tone, medium-balanced rhythm, collective-action posture."

**Step 6 — Demonstrate the editing loop (1 minute)**

Click **More Provocative**. Show the article update in place. Click **More Data-Driven**. Note the metrics and statistics that appear. This is the refinement loop — the executive stays in control.

**Step 7 — Copy and ship (30 seconds)**

Click **Copy to Clipboard**. Open LinkedIn. Paste. Point out that the title, body, and hashtags are all there, formatted correctly.

**Step 8 — Close (1 minute)**

> "An executive just went from blank page to publish-ready LinkedIn article in under three minutes. Not because the AI wrote it for them — but because the AI understood who they are, researched what matters today, and expressed it in their voice. That is the difference between AI as a tool and AI as a genuine executive capability."

Close with the pilot offer: "We can build a version of this tuned to your specific executive voice, connected to your internal research sources, and deployed on IBM Cloud, in three to four weeks with Client Engineering."

---

### SAMPLE EXECUTIVE INTENT INPUTS

Use these during a live demo when showing the Manual Entry flow (not the presets):

```text
Share my perspective on why AI governance is not a compliance burden but a competitive differentiator — and why the companies building trust today will win the next decade.
```

```text
Explain why digital transformation keeps failing and what the 30% of organizations that actually succeed are doing differently — it starts with people, not technology.
```

```text
Offer my view on what it means to lead in an era when AI can draft faster, analyze deeper, and process more — but still cannot replace judgment, context, or accountability.
```

```text
Make the case for why sustainability and AI are not separate strategic priorities but two sides of the same transformation — and why executives who treat them separately are missing the point.
```

---

### WHAT GOOD LOOKS LIKE

A strong generated article should feel like something an IBM Senior Vice President would actually post on LinkedIn.

It should be:
- Written in the first person or collective voice consistent with the SOUL.md
- Grounded in a specific industry signal or data point from the research
- Structured with a provocative opening, three clear points, and a leadership reflection close
- Free from marketing language, startup hype, and generic AI filler
- Between 400 and 600 words for the medium format (the most common demo size)

The output should answer:

> "What would this executive say about this topic, in their voice, to their audience, today?"

Not a summary. Not a listicle. An executive perspective.

---

### TECHNICAL ARCHITECTURE NOTES

The six-node LangGraph graph follows this topology:

```
research → analyze_voice → strategic_inference → generate_title → generate_article → generate_hashtags → END
```

All nodes are `async`. The `AgentState` TypedDict carries all state between nodes: topic, article_size, executive_intent, voice_profile (VoiceProfile dataclass), research_results (List[ResearchResult]), strategic_insights (Dict[str, List[StrategicInsight]]), intelligence_synthesis (str), article_title, article_content, hashtags, reasoning_steps, current_step, error.

The `SOULParser` uses regex and keyword frequency scoring to extract tone (authoritative / collaborative / visionary / analytical / empathetic), sentence rhythm (short_punchy / medium_balanced / long_flowing), vocabulary level (executive / technical / business / thought_leader), leadership posture (personal_conviction / collective_action / data_driven / balanced_authority), and storytelling tendency (high / moderate / low).

The `ExecutiveIntelligenceLayer` is pure Python — no LLM calls. It uses keyword pattern matching against the combined research corpus to surface insights categorized across six dimensions. This keeps the intelligence layer fast, deterministic, and explainable.

The `WatsonxService` wraps `ibm-watsonx-ai` SDK with graceful fallback to mock mode. The live path uses `GenParams.DECODING_METHOD=greedy`, `MAX_NEW_TOKENS` tuned per generation node (50 for title, 1500 for large article, 100 for hashtags), and `REPETITION_PENALTY=1.0`. All SDK calls are wrapped in `loop.run_in_executor` to avoid blocking the async event loop.

Article editing uses the same `WatsonxService.generate_text` call with an action-specific editing prompt and a structured `TITLE: / CONTENT:` response format parsed by simple line splitting.

---

### EXECUTIVE TAKEAWAY

At the end of this demo, the executive takeaway should be simple:

> "AI can help me produce authentic thought leadership at the pace my communications calendar demands — without sounding like a language model."

This is not about replacing executive thinking.

It is about giving executives a way to express what they already think — faster, more consistently, and at scale — while preserving the credibility and authenticity that make thought leadership actually worth reading.
