# Use Case - Predictive Maintenance Agent (watsonx Orchestrate, embedded in UI)
## Bob MODE: ibm-presales-demo-builder

**Build Path**: Hybrid (watsonx Orchestrate native agent + Carbon UI shell)

Why this is a strong test: Plant and operations leaders do not need another dashboard that shows red and green dots. They need an agent that watches equipment telemetry, tells them what is about to break, and *acts* — raising a maintenance work order with the right parts and the right technician before the line goes down. This recipe demonstrates a **real, deployable watsonx Orchestrate agent** (native agent + tools) that is **embedded directly in a Carbon UI** via Orchestrate's web chat channel. The intelligence lives in watsonx Orchestrate; the UI is a thin, branded presenter shell.

Cluster: Industrial Asset Intelligence · Industry: Manufacturing · Output shape: equipment health snapshot + failure prediction (mode, probability, remaining useful life) + auto-generated maintenance work order with recommended parts and technician

> **Build path = Hybrid (watsonx Orchestrate).** The deliverable is real Orchestrate artifacts — `agents/*.yaml` (`kind: native`), `tools/*.py` (`@tool`), `import-all.sh` — imported and deployed to the user's own Orchestrate instance with the `orchestrate` CLI, then embedded in a Carbon shell via `orchestrate channels webchat`. Bob MUST invoke the `watsonx-orchestrate` skill. If at any point the only Orchestrate touchpoint is a model call behind FastAPI, the build is WRONG — it must be a deployed native agent visible in `orchestrate agents list`.

### EXECUTIVE NARRATIVE

Imagine you run maintenance for a manufacturing plant.

You have CNC machines, hydraulic presses, and conveyor lines.
Each one streams vibration, temperature, motor current, pressure, and RPM.

Normally, failure prevention is reactive and fragmented.

Someone notices a machine sounds wrong.
Someone checks a vibration trend after the fact.
Someone files a maintenance ticket.
Someone hunts for the right spare part.
Someone finds a technician who is actually available.

By then the line is often already down.

The Predictive Maintenance Agent compresses that into a single conversation.

An operator opens the plant console and asks, in plain language:
*"Check the health of the Forge hydraulic press and raise a work order if it needs one."*

The agent reads the live sensor telemetry, predicts the failure mode and how many days of useful life remain, recommends the exact parts (with stock status), finds an available technician with the right skill, and — when risk is high — creates the maintenance work order automatically. The operator sees the whole reasoning trace and the resulting work order, embedded right in the IBM-styled console.

The goal is not to replace maintenance engineers.

The goal is to move the plant from reactive firefighting to proactive, agent-driven maintenance — catching failures days before they happen and turning a prediction into a scheduled, resourced work order in one step.

### USE CASE DESCRIPTION

The pitch in one line:

> "Ask the agent about any machine — it reads the sensors, predicts what will fail and when, and books the parts and the technician before the line goes down."

This is a genuine agentic demo: the agent chooses which tools to call and chains them. The reasoning loop is legible because the tools are distinct and physical:

- A telemetry tool (numeric sensor readings)
- A prediction tool (failure mode, probability, remaining useful life)
- A parts-recommendation tool (catalog + stock)
- A technician-matching tool (skill + availability)
- A work-order tool (the action — a `READ_WRITE` capability)

Because everything runs on synthetic data, the demo needs no plant integration and no real CMMS — but the architecture is exactly what a real Maximo / SAP PM integration would slot into later (land-and-expand).

The agent is built and deployed to watsonx Orchestrate, then embedded in the UI via the Orchestrate web chat channel, so the presenter interacts with the *real deployed agent* — not a mock.

### PRE-LOADED PRESET SCENARIOS

For the live demo, the agent ships with **five synthetic equipment records** so the presenter never has to invent data or type long prompts. The Carbon shell shows them as a fleet of health tiles; clicking one drops a ready-made prompt into the embedded chat:

**Critical (Auto-creates work order):**
- **LINE-CONVEYOR-03** — conveyor drive motor, BlueLine Logistics, Line C — motor current spike + winding overtemp → predicted **motor winding failure, ~3 days (high urgency)**

**Watch (Proactive scheduling):**
- **FORGE-PRESS-12** — hydraulic press, NovaTech Solutions, Line B — pressure drop + seal temperature rising → predicted **hydraulic seal failure, ~10 days**

**Healthy (No action needed):**
- **APEX-CNC-07** — CNC milling machine, Apex Manufacturing, Line A — all sensors normal → **healthy, ~90 days** remaining useful life
- **WELD-ROBOT-05** — welding robot, Apex Manufacturing, Welding Station 2 — healthy, ~85 days
- **PUMP-HYDRAULIC-18** — hydraulic pump, NovaTech Solutions, Hydraulics Bay — healthy, ~80 days

All data is synthetic (Faker seed=42). No real plant, PII, or proprietary telemetry is used.

### PREPARATION

**Required:**
- IBM Bob access with `ibm-presales-demo-builder` mode
- Python 3.11–3.13 (required by the watsonx Orchestrate ADK)
- Node.js 18+ / npm for the React + Carbon frontend shell
- An IBM watsonx Orchestrate instance (SaaS, on-prem, or local Developer Edition)
- Carbon MCP connected (for correct Carbon v11 components + styling in the shell)

**Environment variables** (kept in a gitignored `.env`):

```bash
# watsonx Orchestrate environment (the agent runtime — NOT a watsonx.ai model call)
WXO_INSTANCE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/YOUR_INSTANCE_ID
WXO_API_KEY=YOUR_API_KEY_HERE
DEMO_MODE=mock
```

### PROMPT #1 - Build the embedded Orchestrate agent (mock mode)

```text
Build an IBM Predictive Maintenance Agent for a manufacturing plant. This must be a REAL
watsonx Orchestrate agent embedded in the UI — a Hybrid build, not a LangGraph backend and
not Orchestrate used as a model endpoint. Use the watsonx-orchestrate skill and build
deployable ADK artifacts: a native agent (kind: native, spec_version: v1) plus Python @tool
tools, with an import-all.sh that imports them in dependency order to my Orchestrate
environment.

The agent monitors IoT sensor data from factory equipment, predicts failures before they
happen, and automatically creates maintenance work orders with recommended parts and a
recommended technician. Give it these tools (synthetic data, Faker seed=42, embedded directly
in the tool files for Orchestrate compatibility):

- get_equipment(): list the plant's 5 equipment records with equipment_id, name, type,
  production_line, status (healthy/watch/at_risk), install_date, and last_maintenance.
- get_sensor_readings(equipment_id): recent IoT telemetry — vibration (mm/s), bearing/seal
  temperature (C), motor current (A), hydraulic pressure (bar), and RPM. Return current
  readings plus 7-day trend data.
- predict_failure(equipment_id): returns failure_probability (0.0-1.0), predicted_failure_mode,
  remaining_useful_life_days, confidence, and the contributing signals with their trends.
- recommend_parts(equipment_id, failure_mode): returns 2-4 parts with part_no, name, qty, and
  stock_status (in_stock/low_stock/order_required).
- recommend_technician(equipment_id, failure_mode): returns a technician with name, skill
  (Electrical/Hydraulics/Mechanical), certification_level, and next_availability (date).
- create_work_order(equipment_id, failure_mode, parts, technician_id, priority, description):
  a READ_WRITE action that returns work_order_id (WO-{hex8}), status (open), scheduled_date,
  assigned_technician, estimated_parts, and created_at timestamp.

Agent behavior (instructions): when asked about a machine, call get_sensor_readings then
predict_failure; if failure_probability >= 0.6 (medium to high risk), call recommend_parts
and recommend_technician, then create_work_order with priority "critical" if
remaining_useful_life_days <= 5, "high" if <= 14, otherwise "medium". Summarize the
prediction, cite the contributing signals (e.g. "vibration rose from 2.1 to 6.8 mm/s and
bearing temp is trending up"), state confidence, and confirm the work order was created with
the work order ID, scheduled date, assigned technician, and required parts. If
failure_probability < 0.6 (low risk), report that the equipment is healthy, state the
remaining useful life, and do NOT create a work order. Prioritize by remaining useful life and
production line criticality. Reference tools by their snake_case names.

Ship five synthetic machines with three reproducible preset scenarios:
- LINE-CONVEYOR-03 (motor winding, 87% probability, ~3 days, high urgency — auto-creates work order)
- FORGE-PRESS-12 (hydraulic seal, 64% probability, ~10 days — scheduled proactively)
- APEX-CNC-07 (healthy, 12% probability, ~90 days — no action)
- WELD-ROBOT-05 (healthy, 15% probability, ~85 days)
- PUMP-HYDRAULIC-18 (healthy, 18% probability, ~80 days)

Add starter_prompts to the agent YAML for the three main scenarios so they appear in the
Orchestrate web chat interface.

The frontend is a thin React + Carbon v11 shell with a polished IBM dark (g90) enterprise
look: a plant overview dashboard with equipment health tiles (status color healthy/watch/
at-risk, predicted failure mode, remaining useful life) and KPI cards (Equipment Monitored,
At-Risk Assets, Open Work Orders, Avg Remaining Useful Life) that update from the synthetic
fleet data via a simple FastAPI backend serving the embedded synthetic data. The main feature
is an embedded watsonx Orchestrate web chat panel (orchestrate channels webchat) framed as
the "Predictive Maintenance Agent" with a title bar and a synthetic-data demo banner. The
equipment tiles are clickable and drop ready-made prompts into the chat. Use the Carbon MCP
for every component and the Sass setup. The intelligence stays in Orchestrate — the UI only
embeds and frames it. Keep synthetic-data and credentials-via-env rules; work in mock mode
until I provide the environment.

IMPORTANT: Embed all synthetic data DIRECTLY in the tool files (not in separate JSON/CSV
files) so the tools work when imported to Orchestrate. Use Python dictionaries and lists
defined at module level in each tool file.
```

### PROMPT #2 - Connect my watsonx Orchestrate environment and deploy

```text
I have my own watsonx Orchestrate environment. Connect to it, import the tools and agent,
deploy the agent, and get the web chat integration details. Store credentials in the
gitignored .env — do not hardcode them in any artifact.

WXO_INSTANCE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/ffbc929b-85ab-4e58-8324-de939ca190c2
WXO_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

The watsonx-orchestrate skill will handle: adding the environment, activating it, checking
available models, updating the agent YAML with an available model (prefer
watsonx/meta-llama/llama-3-3-70b-instruct, fallback to groq/openai/gpt-oss-120b or another
available model), importing tools and agent, deploying the agent, and getting the web chat
integration details for the .env file.

Tell me which model you used and confirm the agent is deployed and visible in `orchestrate
agents list`.
```

> ⚠️ **Security:** the API key above is a live IBM Cloud key. It is included only so the demo can be tested end to end. Rotate/revoke it after testing, keep it in `.env` (gitignored), and never commit this file with the key in it.

### PROMPT #3 - Start, deploy, and test end to end

```text
Start the application on my local laptop, make sure the agent is deployed to my Orchestrate
environment, and test it end to end. Run your build verification:

1. Backend: confirm it boots and serves /api/health + /api/data/dashboard (200 OK)
2. Frontend: confirm `npm run build` exits 0, then boot the dev server
3. UI: load http://localhost:3001 (or the port Vite assigns), screenshot the dashboard,
   confirm correctly-styled Carbon (IBM Plex, g90 theme, no missing-token CSS errors) and
   zero console errors (ignore expected font warnings in dev mode)
4. Agent: smoke-test the deployed agent with `orchestrate chat ask` for one read-only prompt
   (APEX-CNC-07 health) and one action prompt (LINE-CONVEYOR-03 raise a work order), show me
   the tool-call trace and the created work order
5. Fix any errors yourself before telling me it's done

If the web chat embed breaks the React app (blank page), remove the embed code and document
that users should test the agent directly in the Orchestrate web console — this is the
standard pattern for Orchestrate agent demos when the embed conflicts with React.
```

### EXPECTED OUTPUT

**Orchestrate Artifacts:**
- Real, deployed watsonx Orchestrate **native agent** (visible in `orchestrate agents list`)
- ADK artifact set: `agents/predictive_maintenance_agent.yaml` (kind: native, spec_version: v1), `tools/equipment_tools.py` + `tools/maintenance_tools.py` (`@tool`), `import-all.sh`, `.env` (gitignored)
- Six `@tool` capabilities: get_equipment, get_sensor_readings, predict_failure, recommend_parts, recommend_technician, create_work_order (READ_WRITE)
- Synthetic data embedded DIRECTLY in tool files (not separate JSON/CSV)
- Agent deployed with `orchestrate agents deploy`

**UI Shell:**
- Carbon React (g90, IBM-styled) **thin shell** with dashboard view
- Plant overview with 5 equipment health tiles (color-coded by status) + 4 KPI cards:
  - Equipment Monitored: 5
  - At-Risk Assets: 1
  - Open Work Orders: 1
  - Avg Remaining Useful Life: ~54 days
- Simple FastAPI backend serving the embedded synthetic data (no Orchestrate calls from backend)
- Embedded agent conversation panel (if embed works) OR instructions to test in Orchestrate console
- Mock-mode support for offline demos

**Documentation:**
- README with setup, deployment, and testing instructions
- ARCHITECTURE showing the Orchestrate agent + tools (not "FastAPI -> model")
- PILOT_PLAN for 3-4 week implementation
- DEMO_SCRIPT with timing and talk track
- VERIFICATION_REPORT with evidence: `npm run build` green, screenshots, `orchestrate chat ask` traces

**Verification Evidence:**
- `orchestrate agents list` output showing the agent
- `orchestrate chat ask` traces for both scenarios (healthy + work order creation)
- Frontend screenshots with styled Carbon and zero console errors
- TEST_REPORT.md or VERIFICATION_REPORT.md

### DEMO SCRIPT

**Setup (before audience arrives):**
1. Ensure backend is running: `cd backend && source venv/bin/activate && uvicorn main:app --port 8000`
2. Ensure frontend is running: `cd frontend && npm run dev`
3. Open http://localhost:3001 in browser (full screen, 1920x1080)
4. Open watsonx Orchestrate console in a second tab (for agent testing)
5. Verify agent is deployed: `orchestrate agents list`

**Demo Flow (10 minutes):**

1. **Open the IBM Plant Maintenance console** (2 min)
   - Point out the fleet health tiles and KPI cards (all synthetic)
   - "This is a manufacturing plant with 5 pieces of equipment. We're monitoring them in real-time."
   - Highlight the color coding: green (healthy), yellow (watch), red (at-risk)

2. **Introduce the agent** (1 min)
   - "The intelligence here is a watsonx Orchestrate agent, deployed to our own instance — not a mock."
   - Switch to the Orchestrate console tab
   - Show the agent in the chat interface

3. **Scenario 1: Critical equipment** (3 min)
   - Click the **LINE-CONVEYOR-03** tile (high urgency) OR use the starter prompt in Orchestrate
   - Prompt: "Check the health of LINE-CONVEYOR-03 and raise a work order if it needs one."
   - Watch the agent's tool trace:
     - reads sensors → predicts failure → recommends parts → matches a technician → creates the work order
   - Show the rendered work-order summary: ID, equipment, failure mode (motor winding), parts, technician, scheduled date, priority = High
   - "The agent just went from prediction to scheduled, resourced work order in one conversation."

4. **Scenario 2: Proactive maintenance** (2 min)
   - Use the starter prompt for **FORGE-PRESS-12** (medium term)
   - Show it schedules a proactive work order ~10 days out
   - "This is the shift from reactive to proactive — we're catching failures before they happen."

5. **Scenario 3: Healthy equipment** (1 min)
   - Use the starter prompt for **APEX-CNC-07** healthy variant
   - Show the agent says no action is needed and does NOT create a work order
   - "The agent reasons — it doesn't just react. It only creates work orders when risk warrants it."

6. **Free-text follow-up** (1 min)
   - Ask: "Which machine should I prioritize this week and why?"
   - Show the agent uses prior context (remaining useful life + line criticality)

7. **Close** (30 sec)
   - "The plant just went from reactive to proactive — a prediction became a resourced, scheduled work order in one conversation."
   - "This agent is deployed in watsonx Orchestrate. The same artifacts promote straight into a real Maximo or SAP PM integration."

### SAMPLE OPERATOR PROMPTS

Use these during a live demo (or as starter prompts in the agent YAML). These are designed to showcase different agent capabilities:

**1. Critical Equipment - Action Required (demonstrates full workflow)**
```text
Check the health of LINE-CONVEYOR-03 and raise a work order if it needs one.
```
*Expected: Agent reads sensors → predicts motor winding failure (87%, 3 days) → recommends parts → finds technician → creates CRITICAL work order*

**2. Fleet Overview (demonstrates multi-equipment analysis)**
```text
What's about to fail in the plant, and how many days do I have on each machine?
```
*Expected: Agent calls get_equipment → lists all 5 machines with failure probabilities and remaining useful life, prioritized by urgency*

**3. Proactive Maintenance (demonstrates medium-term planning)**
```text
Forge-Press-12 — predict the failure mode and schedule maintenance with the right parts and technician.
```
*Expected: Agent predicts hydraulic seal failure (64%, 10 days) → recommends seal parts → finds hydraulics technician → creates HIGH priority work order*

**4. Healthy Equipment Check (demonstrates reasoning - no action)**
```text
Is APEX-CNC-07 healthy, or does it need attention?
```
*Expected: Agent reports healthy status (12% failure, 90 days RUL) → recommends continued monitoring → does NOT create work order*

**5. Prioritization Decision (demonstrates context and reasoning)**
```text
Which machine should I prioritize this week, and why?
```
*Expected: Agent analyzes all equipment → recommends LINE-CONVEYOR-03 (3 days RUL, critical line) → explains reasoning based on urgency and production impact*

**6. Specific Sensor Query (demonstrates telemetry access)**
```text
Show me the current sensor readings for FORGE-PRESS-12. What's trending wrong?
```
*Expected: Agent calls get_sensor_readings → reports pressure drop (180→165 bar) and seal temp rise (45→58°C) → explains these indicate seal wear*

**7. Parts Availability Check (demonstrates inventory awareness)**
```text
If LINE-CONVEYOR-03 fails, do we have the parts in stock to fix it?
```
*Expected: Agent calls recommend_parts for motor winding failure → reports motor winding kit (in stock), bearing set (in stock), motor controller (low stock - order required)*

**8. Technician Availability (demonstrates resource matching)**
```text
Who's available to work on electrical issues this week?
```
*Expected: Agent calls recommend_technician with Electrical skill → reports available technicians with certifications and next availability dates*

**9. Multi-Machine Comparison (demonstrates analytical reasoning)**
```text
Compare the health of LINE-CONVEYOR-03 and FORGE-PRESS-12. Which one needs attention first?
```
*Expected: Agent analyzes both → LINE-CONVEYOR-03 (87%, 3 days, motor winding) vs FORGE-PRESS-12 (64%, 10 days, hydraulic seal) → recommends LINE-CONVEYOR-03 due to shorter RUL and higher probability*

**10. Follow-up Context (demonstrates conversation memory)**
```text
[After creating a work order] When is that work order scheduled, and who's assigned to it?
```
*Expected: Agent references the previously created work order → reports scheduled date, assigned technician name and skill, and estimated completion time*

### WHAT GOOD LOOKS LIKE

A strong run should feel like a maintenance planner's assistant that actually does the work.

It should:
- read the right sensors for the machine in question
- predict a specific failure mode with probability, remaining useful life, and the signals behind it
- recommend concrete parts (with stock status) and an available technician with the right skill
- create a work order only when risk warrants it — and decline when the machine is healthy
- prioritize by urgency and production impact
- show its tool-call reasoning so the audience trusts the result

The output should not just describe a machine.

It should answer:

> "What is going to fail, when, what do I need to fix it, who should fix it — and book it."

### KNOWN ISSUES & WORKAROUNDS

**Issue: Web chat embed breaks React (blank page)**
- **Cause**: The wxoLoader.js script can interfere with React's rendering lifecycle
- **Workaround**: Remove the embedded web chat component and document that users should test the agent directly in the Orchestrate web console
- **Impact**: None. The demo UI shows equipment data and explains how to test the agent in Orchestrate. This is the standard pattern for Orchestrate agent demos.

**Issue: Model not available**
- **Cause**: `watsonx/meta-llama/llama-3-3-70b-instruct` may not be available in all Orchestrate environments
- **Workaround**: The watsonx-orchestrate skill will check `orchestrate models list` and update the agent YAML to use an available model
- **Impact**: None. The agent works with any available model.

### EXECUTIVE TAKEAWAY

At the end of this lab, the takeaway should be simple:

> "A watsonx Orchestrate agent can watch our equipment, predict failures days ahead, and turn that prediction into a scheduled, resourced work order — automatically."

This is not a toy application.

It is a practical example of agentic AI moving a plant from reactive repair to proactive, agent-driven maintenance — and because the agent and its tools are deployed in watsonx Orchestrate, the same artifacts promote straight from this demo into a real Maximo / SAP PM integration.
