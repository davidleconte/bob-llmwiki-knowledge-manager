# IBM watsonx.governance Skill

A skill that teaches an AI assistant (e.g. **Bob**) to evaluate, monitor, and
govern AI on **IBM watsonx.governance** correctly, grounded in the real SDK
surface rather than guesswork. watsonx.governance is one product spanning **three
Python SDKs**, and the skill routes between them:

- **`ibm-watsonx-gov`** (core) — evaluation: GenAI/RAG quality & content-safety
  metrics, agentic application evaluation, foundation-model risk.
- **`ibm-aigov-facts-client`** — AI use case inventory, model factsheets, lifecycle.
- **`ibm-watson-openscale`** — production monitoring (drift, fairness, quality,
  explainability, payload logging) of deployed models.

## What it covers

- **Pick the right SDK** — the first decision, since e.g. "list an AI use case" is
  impossible in `ibm-watsonx-gov` and belongs to `ibm-aigov-facts-client`.
- **Connect** — `Credentials`/`APIClient`, SaaS vs Cloud Pak for Data, regions,
  and the all-important **extras matrix** (`[metrics]`, `[agentic]`, `[mre]`, …).
- **Metrics evaluation** — `MetricsEvaluator` over a DataFrame/dict, the
  `GenAIConfiguration` field mapping, computation `method`s, thresholds, results.
- **Metrics catalog** — retrieval quality, answer quality, content safety, tool
  calls, readability, performance, usage, and custom (LLM-as-judge) metrics.
- **Agentic evaluation** — `AgenticEvaluator` with per-node decorators, declarative
  `AgenticApp`/`Node` config, runs, OpenTelemetry tracing, experiment tracking.
- **Model risk** — `ModelRiskEvaluator`, risk dimensions, PDF reports, multi-provider
  foundation models, watsonx Governance Console sync, LLM judges.
- **AI use cases & factsheets** — inventories, use cases, lifecycle (factsheets SDK).
- **Production monitoring** — datamarts, subscriptions, monitor instances (openscale).

## Layout

```
ibm-watsonx.governance/
├── SKILL.md              # the skill (the assistant loads this)
├── README.md             # this file
└── references/           # loaded on demand by the skill
    ├── setup-auth.md
    ├── metrics-evaluator.md
    ├── metrics-catalog.md
    ├── agentic-evaluator.md
    ├── model-risk-and-providers.md
    ├── factsheets-and-usecases.md     # ibm-aigov-facts-client (use cases, factsheets)
    └── openscale-monitoring.md        # ibm-watson-openscale (production monitoring)
```

## Grounding & versions

The core was verified against **`ibm-watsonx-gov` 1.5.0** (installed via pip) and
the SDK docs snapshot (v1.4.1). The factsheets and monitoring references were
**live-verified** against **`ibm-aigov-facts-client` 1.0.105** and
**`ibm-watson-openscale` 3.1.7** on a real watsonx.governance SaaS instance —
including actually listing and creating an AI use case and reading a live
monitoring datamart. Most `ibm-watsonx-gov` capabilities live behind **optional
extras**, so the skill's first rule is *install the right extra*, and its golden
rule is to **verify signatures against the live docs / `help()`** and read each
metric's allowed computation `method`s off the installed class rather than
trusting a hardcoded list.

> 🔒 watsonx.governance credentials (IBM Cloud API key / CPD password / provider
> keys) are secrets — read them from environment variables, never hardcode or
> commit them.

## Related skills

watsonx.governance is the **evaluation / observability layer** on top of the model
layer. Pair it with the **watsonx.ai** skill (which runs the models you're
scoring), the **watsonx Orchestrate** skill (build the agent; govern it here), and
the **TechZone** skill (provision a watsonx.governance instance first).
