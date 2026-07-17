---
name: ibm-watsonx-governance
description: >-
  Evaluate, monitor, and govern AI on IBM watsonx.governance. Use this whenever
  the user mentions watsonx.governance, watsonx governance, `ibm-watsonx-gov`,
  AI evaluation, generative-AI / LLM / RAG metrics (answer relevance,
  faithfulness, context relevance, answer similarity, retrieval quality),
  content-safety / guardrail metrics (HAP, PII, harm, jailbreak, prompt-safety,
  social bias), agentic / agent evaluation (LangGraph/CrewAI agents, tool-call
  quality, node-level metrics), foundation-model risk evaluation and risk
  reports, LLM-as-a-judge, metric thresholds, experiment tracking, OpenTelemetry
  tracing of agents — and also the broader governance product: AI use case
  inventory / model factsheets / model lifecycle (`ibm-aigov-facts-client`),
  production model monitoring (drift, fairness, quality, explainability,
  payload logging via watsonx.openscale / `ibm-watson-openscale`), and the
  watsonx Governance Console (OpenPages). Covers three companion SDKs:
  `ibm-watsonx-gov` (evaluation — MetricsEvaluator / AgenticEvaluator /
  ModelRiskEvaluator), `ibm-aigov-facts-client` (use cases & factsheets), and
  `ibm-watson-openscale` (production monitoring).
metadata:
  enabled: true
---

# IBM watsonx.governance — Evaluate · Monitor · Govern AI

Authoritative, end-to-end guide for evaluating and governing AI with IBM
**watsonx.governance**, grounded in the real SDKs (not guesswork). Its core is the
**`ibm-watsonx-gov` Python SDK** — generative-AI/RAG quality metrics,
content-safety guardrails, **agentic** application evaluation, and
**foundation-model risk** assessment. The watsonx.governance *product* spans two
more SDKs this skill also covers (§0): **`ibm-aigov-facts-client`** for AI use
cases / factsheets, and **`ibm-watson-openscale`** for production monitoring.

> **Golden rule:** the SDK moves fast and most capabilities live behind
> **optional extras** (`[metrics]`, `[agentic]`, `[mre]`, …). The class/method
> specifics here were verified against **`ibm-watsonx-gov` 1.5.0** (docs snapshot
> v1.4.1). When a method, parameter, metric name, or method-string is uncertain
> — or you're on a different version — **verify against the live tool**:
> `pip show ibm-watsonx-gov`, `python -c "import ibm_watsonx_gov; help(...)"`,
> and the live docs (§10). Don't assume a metric supports a given computation
> `method` — the allowed methods are a typed `Literal` on each metric class;
> read them off the class rather than trusting a hardcoded list.

---

## 0. Pick the right SDK first (watsonx.governance is three SDKs)

"watsonx.governance" is one product with **three Python SDKs**. Picking the wrong
one is the #1 dead end — e.g. *"list my AI use cases"* is **not** possible in
`ibm-watsonx-gov`. Route the task first:

| The task is about… | SDK | Where |
|---|---|---|
| Scoring an eval set / prompt / RAG **offline**, evaluating an **agent run**, **foundation-model risk** reports | **`ibm-watsonx-gov`** | §1–§9 (this skill's core) |
| **AI use case inventory**, **model factsheets**, model **lifecycle**, inventories, tracking models/prompts | **`ibm-aigov-facts-client`** | [references/factsheets-and-usecases.md](references/factsheets-and-usecases.md) |
| **Continuous monitoring** of a **deployed** model — drift, fairness, quality, explainability, payload logging | **`ibm-watson-openscale`** | [references/openscale-monitoring.md](references/openscale-monitoring.md) |

All three authenticate with the **same IBM Cloud API key** (SaaS) and target the
same governance instance; large projects use all three together. The rule of
thumb: **`ibm-watsonx-gov` measures quality, `ibm-aigov-facts-client` records what
exists and its lifecycle, `ibm-watson-openscale` watches it in production.**
Sections 1–10 below are the `ibm-watsonx-gov` core; jump to the references for the
other two.

> ⚠️ Each SDK has its own quirks. Notably `ibm-aigov-facts-client` wants
> `region="dallas"` (the enum *name*, not `"us-south"`) and must be initialized
> with a **project/space** container, passing the inventory as `catalog_id`
> per-call — see its reference.

---

## 1. Mental model — what you are building

watsonx.governance evaluates **how good / safe / compliant** an AI system is. You
do that through **three evaluator classes**, all driven by one `APIClient` and a
**configuration** that maps your data's column names to roles:

| Evaluator | What it evaluates | When to use | Extra |
|---|---|---|---|
| **`MetricsEvaluator`** | A batch of records (DataFrame / dict) against a chosen set of metrics | Offline / experiment-time quality & safety scoring of a prompt, model, or RAG pipeline | `[metrics]` |
| **`AgenticEvaluator`** | A running **agentic application** — agent-level, message-level, and **per-node** metrics, with tracing | Instrumenting a LangGraph/CrewAI-style agent to measure tool calls, retrieval, latency, cost | `[agentic]` |
| **`ModelRiskEvaluator`** | A **foundation model's risk** across risk dimensions (hallucination, jailbreak, harmful-code, …) → PDF report | Pre-deployment model risk assessment, optionally synced to watsonx Governance Console | `[mre]` |

Three building blocks feed every evaluator:

- **Credentials + `APIClient`** — auth and region/cluster (§2).
- **A configuration** — `GenAIConfiguration` (batch) or `AgenticAIConfiguration`
  (agents) or `ModelRiskConfiguration` (risk). This is the field-name mapping
  (`input_fields`, `context_fields`, `output_fields`, `reference_fields`, …) plus
  `task_type`, `locale`, and an optional `llm_judge`.
- **Metrics** — concrete metric objects (e.g. `AnswerRelevanceMetric()`) or whole
  **metric groups** (`MetricGroup.RETRIEVAL_QUALITY`). The catalog is large (§3.4).

**The one thing that trips people up:** every metric reads its inputs from your
data **by field name**, and the defaults are fixed strings — `input_text`,
`context`, `generated_text`, `ground_truth`. If your columns are named anything
else, you **must** map them in the configuration or the metric silently looks at
the wrong column / errors. Set the configuration once and reuse it.

This SDK is **evaluation/observability**, not inference. It does *not* run your
model — `ibm-watsonx-ai` does that (see the watsonx.ai skill). watsonx.governance
scores the inputs/outputs you give it, and (optionally for some metrics/judges)
calls a judge model on your behalf.

---

## 2. Prerequisites & connect (do this first)

- **Python 3.10–3.12.** Use a real version (`python3.12`), not system `python3`.
  Work in a virtualenv.
- **Install — pick the extras you need.** The base package is small; nearly every
  useful capability needs an extra:

  ```bash
  pip install -U "ibm-watsonx-gov"              # base only (auth, entities)
  pip install -U "ibm-watsonx-gov[metrics]"     # MetricsEvaluator + metric compute
  pip install -U "ibm-watsonx-gov[agentic]"     # AgenticEvaluator + tracing
  pip install -U "ibm-watsonx-gov[mre]"         # ModelRiskEvaluator
  pip install -U "ibm-watsonx-gov[metrics,agentic]"   # combine as needed
  ```
  Other extras: `[local-evals]` (run certain metrics with local models, no judge
  call), `[llmaj]` (LLM-as-a-judge methods), `[tools]`, `[visualization]`.
  Confirm: `pip show ibm-watsonx-gov`. **`ModuleNotFoundError` at import time
  almost always means a missing extra** — see §7.

- You need an **IBM Cloud API key** (SaaS) **or** a Cloud Pak for Data
  URL + credentials (software), and usually a **`project_id` or `space_id`** for
  the asset/experiment you're governing.

**SaaS (watsonx.governance as a Service):**
```python
import os
from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import Region

os.environ["WATSONX_APIKEY"] = "..."            # preferred: read from env, never hardcode
# os.environ["WXG_SERVICE_INSTANCE_ID"] = "..." # only if you have multiple gov instances
# os.environ["WATSONX_REGION"] = Region.AU_SYD.value  # default region is Dallas (us-south)

credentials = Credentials(api_key=os.environ["WATSONX_APIKEY"])      # Dallas default
# Other region: Credentials(region=Region.EU_DE.value, api_key=...)
api_client = APIClient(credentials=credentials)
```
SaaS regions: `us-south`, `eu-de`, `au-syd`, `ca-tor`, `jp-tok`, `eu-gb`
(the `Region` enum).

**Cloud Pak for Data (software / on-prem):**
```python
credentials = Credentials(
    url="https://<cpd_cluster_host>",
    api_key=os.environ["WATSONX_APIKEY"],   # or password=...
    username=os.environ["WATSONX_USERNAME"],
    version="5.2",                          # CPD two-digit release, e.g. "5.2"
)
api_client = APIClient(credentials=credentials)
```
Either way you then pass `api_client=...` into an evaluator. If you skip the
client entirely and just set `WATSONX_APIKEY`, the evaluators construct a default
SaaS client for you. Full credential surface, env-var names, and SaaS-vs-CPD
details are in **[references/setup-auth.md](references/setup-auth.md)**.

> 🔒 **Treat the API key / token as a secret.** Read it from an env var, never
> hardcode it in code, notebooks, or commits. Don't print tokens. Rotate if
> exposed.

---

## 3. The capabilities (SDK-first)

### 3.1 `MetricsEvaluator` — score a batch of records

The workhorse for offline evaluation. Give it a DataFrame (or dict) and a list of
metrics and/or metric groups; get back a result you can render or export.

```python
import pandas as pd
from ibm_watsonx_gov.evaluators import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.metrics import (
    AnswerRelevanceMetric, FaithfulnessMetric, ContextRelevanceMetric,
    AnswerSimilarityMetric, HAPMetric, PIIMetric,
)

# Map YOUR column names to metric roles (skip if your columns already use defaults)
config = GenAIConfiguration(
    task_type=TaskType.RAG,
    input_fields=["question"],
    context_fields=["retrieved_context"],
    output_fields=["answer"],
    reference_fields=["ground_truth"],   # needed by reference-based metrics
)

evaluator = MetricsEvaluator(configuration=config, api_client=api_client)

df = pd.read_csv("eval_set.csv")
result = evaluator.evaluate(
    data=df,
    metrics=[AnswerRelevanceMetric(), FaithfulnessMetric(), AnswerSimilarityMetric()],
    metric_groups=[MetricGroup.CONTENT_SAFETY],   # adds HAP/PII/harm/… in one shot
)

# Consume the result
result.to_df()        # tidy DataFrame of metric values
result.to_json()      # JSON
result.to_dict()      # dict
evaluator.display_table()      # pretty table (needs a notebook / display env)
evaluator.display_insights()   # richer visualization ([visualization] extra)
```

A single-record smoke test works the same with a dict:
`evaluator.evaluate(data={"input_text": "...", "generated_text": "...", "context": ["..."]}, metrics=[HAPMetric()])`.

Full method set, the result objects (`MetricsEvaluationResult`,
`RecordMetricResult`, `AggregateMetricResult`), and per-metric `method` /
`thresholds` tuning are in **[references/metrics-evaluator.md](references/metrics-evaluator.md)**.

### 3.2 `AgenticEvaluator` — instrument an agentic app

For agents (LangGraph, CrewAI, custom graphs) you wrap a **run** around the
invocation and attach metrics at three levels: **agent/message**, and **per-node**.
Two styles:

**A. Decorators (compute node metrics during graph execution):**
```python
from ibm_watsonx_gov.evaluators import AgenticEvaluator
from ibm_watsonx_gov.config import AgenticAIConfiguration

agentic_evaluator = AgenticEvaluator()

@agentic_evaluator.evaluate_retrieval_quality(
    configuration=AgenticAIConfiguration(input_fields=["input_text"],
                                         context_fields=["local_context"]))
@agentic_evaluator.evaluate_content_safety()         # uses default field mapping
def local_search_node(state, config):
    # ... retrieve docs ...
    return {"local_context": [...]}

agentic_evaluator.start_run()
# ... invoke your agent / graph here ...
agentic_evaluator.end_run()
result = agentic_evaluator.get_result()
```
There is one `evaluate_*` decorator per metric/group:
`evaluate_retrieval_quality`, `evaluate_content_safety`, `evaluate_answer_relevance`,
`evaluate_faithfulness`, `evaluate_context_relevance`, `evaluate_tool_call_accuracy`,
`evaluate_hap`, `evaluate_pii`, `evaluate_general_quality_with_llm`, … (full list
in the reference).

**B. Declarative config (compute agent/node metrics after invocation):**
```python
from ibm_watsonx_gov.entities.agentic_app import AgenticApp, Node, MetricsConfiguration
from ibm_watsonx_gov.metrics import AnswerRelevanceMetric, ContextRelevanceMetric
from ibm_watsonx_gov.entities.enums import MetricGroup

agentic_app = AgenticApp(
    name="My Agent",
    metrics_configuration=MetricsConfiguration(           # agent/message level
        metrics=[AnswerRelevanceMetric()],
        metric_groups=[MetricGroup.CONTENT_SAFETY]),
    nodes=[Node(name="Retrieval Node",                    # per-node level
                metrics_configurations=[MetricsConfiguration(
                    metrics=[ContextRelevanceMetric()],
                    metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])],
)
agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app, api_client=api_client)
agentic_evaluator.start_run(); ...; agentic_evaluator.end_run()
result = agentic_evaluator.get_result()
```

With **no config at all**, `AgenticEvaluator` still records performance (latency,
duration) and usage (cost, token counts) for free. It also supports **experiment
tracking** and **OpenTelemetry tracing** (`TracingConfiguration`, `track_experiment`,
`start_run(AIExperimentRunRequest(...))`, `compare_ai_experiments`). All of this —
decorators, node mapping, runs, tracing, experiments, `log_custom_metrics` — is in
**[references/agentic-evaluator.md](references/agentic-evaluator.md)**.

### 3.3 `ModelRiskEvaluator` — foundation-model risk + report

Assess a foundation model against **risk dimensions** and produce a PDF report,
optionally synced to the **watsonx Governance Console**.

```python
from ibm_watsonx_gov.evaluators import ModelRiskEvaluator
from ibm_watsonx_gov.config import ModelRiskConfiguration
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel

model_details = WxAIFoundationModel(
    model_name="my_granite",
    model_id="ibm/granite-3-3-8b-instruct",
    project_id="PROJECT_ID",
)
config = ModelRiskConfiguration(
    model_details=model_details,
    risk_dimensions=["hallucination", "jailbreaking", "harmful-code-generation"],
    max_sample_size=500,
    thresholds=(20, 80),                 # (lower, upper) in 0–100
    pdf_report_output_path="/reports",
)
evaluator = ModelRiskEvaluator(configuration=config, api_client=api_client)
result = evaluator.evaluate()
result.to_json()
evaluator.display_table()
evaluator.download_model_risk_report()
```

The model under test can come from **any supported provider** (not just
watsonx.ai) — `WxAIFoundationModel`, `OpenAIFoundationModel`,
`AzureOpenAIFoundationModel`, `AWSBedrockFoundationModel`,
`VertexAIFoundationModel`, `GoogleAIStudioFoundationModel`, `RITSFoundationModel`,
`CustomFoundationModel`. Provider credentials, `WxGovConsoleConfiguration`, and
the full risk-dimension list are in
**[references/model-risk-and-providers.md](references/model-risk-and-providers.md)**.

### 3.4 The metrics catalog (groups)

Metrics are organized into `MetricGroup`s. Pass whole groups for breadth, or
individual metric classes for control. Groups (`MetricGroup` enum):

| Group | Example metrics |
|---|---|
| `RETRIEVAL_QUALITY` | `ContextRelevanceMetric`, `RetrievalPrecisionMetric`, `NDCGMetric`, `ReciprocalRankMetric`, `HitRateMetric`, `AveragePrecisionMetric` |
| `ANSWER_QUALITY` | `AnswerRelevanceMetric`, `FaithfulnessMetric`, `AnswerSimilarityMetric`, `UnsuccessfulRequestsMetric` |
| `CONTENT_SAFETY` | `HAPMetric`, `PIIMetric` (+`Input/Output` variants), `HarmMetric`, `HarmEngagementMetric`, `JailbreakMetric`, `PromptSafetyRiskMetric`, `ProfanityMetric`, `SexualContentMetric`, `SocialBiasMetric`, `ViolenceMetric`, `UnethicalBehaviorMetric`, `EvasivenessMetric` |
| `TOOL_CALL_QUALITY` | `ToolCallAccuracyMetric`, `ToolCallParameterAccuracyMetric`, `ToolCallRelevanceMetric`, `ToolCallSyntacticAccuracyMetric` |
| `READABILITY` | `TextGradeLevelMetric`, `TextReadingEaseMetric` |
| `PERFORMANCE` | `DurationMetric` (latency) |
| `USAGE` | `CostMetric`, `InputTokenCountMetric`, `OutputTokenCountMetric` |
| `MESSAGE_COMPLETION` / other | `TopicRelevanceMetric`, `StatusMetric`, `UserIdMetric` |
| `CUSTOM` | `LLMAsJudgeMetric`, `LLMValidationMetric`, `KeywordDetectionMetric`, `RegexDetectionMetric` |

The complete catalog with each metric's allowed computation `method`s (e.g.
`ContextRelevanceMetric` supports `token_precision` / `sentence_bert_*` /
`llm_as_judge` / `granite_guardian` / `context_relevance_model`), default
thresholds, required fields, and which `TaskType`s they apply to is in
**[references/metrics-catalog.md](references/metrics-catalog.md)**.

---

## 4. Choosing metrics & methods — be deliberate

- **Pick metrics that match the task.** RAG → retrieval-quality + faithfulness +
  answer-relevance. A bare prompt/model → answer-quality + content-safety. An
  agent with tools → tool-call-quality. Set `task_type` (`TaskType.RAG`,
  `QUESTION_ANSWERING`, `SUMMARIZATION`, `CLASSIFICATION`, `GENERATION`,
  `EXTRACTION`) so metrics interpret data correctly.
- **Reference-based vs reference-free.** Metrics like `AnswerSimilarityMetric`
  need a `reference_fields` (ground-truth) column; many safety/relevance metrics
  are reference-free. Check `metric.is_reference_free`.
- **Computation `method` is a real choice.** Each metric exposes a typed
  `method` (read it off the class). Cheaper/local methods (`token_*`,
  `sentence_bert_*`) avoid an LLM call; `llm_as_judge` and `granite_guardian` are
  more accurate but invoke a model — set an `llm_judge` and mind cost/latency.
- **Thresholds make a metric pass/fail.** Set `thresholds=[MetricThreshold(
  type="lower_limit", value=0.7)]` (or `upper_limit`) to turn a raw score into a
  violation flag.

---

## 5. Critical constraints (these cause silent failures — internalize them)

- ✅ **Extras are mandatory per capability.** `MetricsEvaluator` needs
  `[metrics]`, `AgenticEvaluator` needs `[agentic]`, `ModelRiskEvaluator` needs
  `[mre]`. A bare `pip install ibm-watsonx-gov` imports but can't compute metrics.
- ✅ **Field mapping is everything.** Defaults are `input_text` / `context` /
  `generated_text` / `ground_truth`. If your data differs, set `input_fields`,
  `context_fields`, `output_fields`, `reference_fields` in the configuration —
  otherwise metrics read the wrong column or fail.
- ✅ **Reference-based metrics need a reference column.** No `reference_fields` →
  `AnswerSimilarityMetric` and similar can't compute.
- ✅ **`AgenticEvaluator` requires a run boundary.** Always `start_run()` before
  invoking the agent and `end_run()` after; `get_result()` only has data between/
  after them.
- ✅ **Env vars are read once.** `APIClient` reads `WATSONX_*` env vars at first
  init; changing them later needs a kernel/process restart.
- ✅ **`method` selection changes cost.** `llm_as_judge` / `granite_guardian`
  methods invoke a model (latency + tokens); local methods don't. Choose
  intentionally and configure an `llm_judge` when a method needs one.
- ✅ **SaaS vs CPD auth differ.** SaaS = `api_key` (+ region). CPD = `url` +
  `username` + `api_key`/`password` + `version`. Mixing them → 401/connection
  errors.
- ✅ **Metric ids/methods aren't guaranteed stable across versions.** Read the
  `method` `Literal` and defaults off the installed class, don't hardcode blindly.

---

## 6. Beyond evaluation — the rest of the governance product

### 6a. Still inside `ibm-watsonx-gov`
- **Experiment tracking & tracing** — `track_experiment`, `AIExperimentRunRequest`,
  `TracingConfiguration` (OTel export to a `project_id`/`space_id` or an OTLP
  collector), and `compare_ai_experiments` to diff runs. See the agentic reference.
- **Agent & tool catalog** — `ibm_watsonx_gov.agent_catalog` and
  `ibm_watsonx_gov.tools` register/load governed agents and tools (needs `[tools]`).
- **`PromptEvaluator`** — evaluate a stored watsonx.ai prompt template (needs
  `ibm-watsonx-ai` installed alongside).

### 6b. The other two SDKs (different package — see §0)
- **AI use cases / factsheets / model lifecycle** → **`ibm-aigov-facts-client`**.
  Create/list inventories and AI use cases, attach factsheets, track models across
  Develop→Validate→Operate phases. This is what answers *"list/create an AI use
  case"* — `ibm-watsonx-gov` cannot. Full, live-verified recipe in
  **[references/factsheets-and-usecases.md](references/factsheets-and-usecases.md)**.
- **Production monitoring of deployed models** (drift, fairness, quality,
  explainability, generative-AI quality, payload logging) → **`ibm-watson-openscale`**
  (watsonx.openscale): datamarts, service providers, subscriptions, monitor
  instances. Full map in
  **[references/openscale-monitoring.md](references/openscale-monitoring.md)**.

---

## 7. Debugging playbook

| Symptom | Likely cause → fix |
|---|---|
| `ModuleNotFoundError` on import (`jsonschema`, `nbformat`, `ibm_watsonx_ai`, …) | Missing **extra**. Install the right one: `[metrics]`, `[agentic]`, `[mre]`. `PromptEvaluator` also needs `ibm-watsonx-ai`. |
| Metric returns nothing / wrong values | Field mapping. Your column names ≠ defaults — set `input_fields`/`context_fields`/`output_fields`/`reference_fields` in the configuration. |
| Reference-based metric errors / NaN | No `reference_fields` (ground truth) column provided. |
| `AgenticEvaluator` result empty | Missing `start_run()`/`end_run()` around the agent invocation, or no metrics configured/decorated. |
| 401 / `Unauthorized` | Wrong auth shape: SaaS needs `api_key`(+region); CPD needs `url`+`username`+`version`. Check `WATSONX_*` env vars (read once — restart kernel). |
| Wrong region / connection refused | SaaS default is Dallas; set `Region` / `WATSONX_REGION` or pass `region=`. CPD needs the full cluster `url`. |
| Unexpectedly slow / token spend | A metric `method` is `llm_as_judge`/`granite_guardian` (model call). Switch to a local method or accept the cost; set `llm_judge`. |
| `display_table()` / `display_insights()` show nothing | Not in a notebook/display env, or `[visualization]` extra missing. Use `result.to_df()`/`to_json()` instead. |
| Changed env var has no effect | `APIClient` cached it at init. Restart the process/kernel. |
| "Can't find / list / create an AI use case" | Wrong SDK — use cases are in **`ibm-aigov-facts-client`**, not `ibm-watsonx-gov` (§0). |
| `ibm-aigov-facts-client`: *"Only project and space context supported"* | Init with `container_type="project"`/`"space"`; pass the inventory as `catalog_id` per call, not as the container. |
| `ibm-aigov-facts-client`: `UnexpectedValue` on region | `region` is the enum **name** (`"dallas"`, `"frankfurt"`, …), not the service region (`"us-south"`). |
| "Monitor my deployed model for drift/fairness" returns nothing in this SDK | Production monitoring is **`ibm-watson-openscale`**, not `ibm-watsonx-gov` (§0). |

More failure modes per area are in the referenced files.

---

## 8. Verify before handover

**Code that imports ≠ code that works.** Before reporting an evaluation task as
done, run a tiny real evaluation against the connected instance and show the
output — one `MetricsEvaluator.evaluate(...)` on a 1–2 row DataFrame/dict, or one
agentic `start_run()/end_run()/get_result()` cycle — and print `result.to_df()`.
For **model-risk** runs and any **LLM-as-judge / Granite-Guardian** methods, state
the **cost/runtime implication** before launching (they sample and call models).
Report status honestly: "ran `AnswerRelevanceMetric` on 2 rows → scores X/Y", or
"wrote model-risk report to `<path>`".

---

## 9. Working alongside other skills

watsonx.governance is the **evaluation/observability layer** that sits *on top of*
the model layer:

- **watsonx.ai** runs the models (inference, embeddings, RAG, tuning). If you need
  to *generate* the outputs you're about to score, that's the watsonx.ai skill;
  this skill picks up to evaluate them. `PromptEvaluator` and `WxAIFoundationModel`
  bridge the two.
- **watsonx Orchestrate** agents can be evaluated as agentic apps here; use the
  Orchestrate skill for building the agent, this one for governing it.
- **TechZone** provisions the watsonx.governance instance; this skill picks up
  once you have credentials.

---

## 10. References (load on demand)

| File | Contents |
|------|----------|
| [references/setup-auth.md](references/setup-auth.md) | `Credentials`/`APIClient` full surface, SaaS vs Cloud Pak for Data, regions, `WATSONX_*` env vars, instance ids, the extras matrix |
| [references/metrics-evaluator.md](references/metrics-evaluator.md) | `MetricsEvaluator` methods, `GenAIConfiguration` field-mapping reference, result objects (`to_df`/`to_json`/`to_dict`, record vs aggregate), `MetricThreshold`, single-record smoke tests |
| [references/metrics-catalog.md](references/metrics-catalog.md) | Full metric catalog by `MetricGroup`, each metric's allowed computation `method`s, default thresholds, required fields, applicable `TaskType`s, the custom metrics (`LLMAsJudgeMetric`, `LLMValidationMetric`, `KeywordDetectionMetric`, `RegexDetectionMetric`) |
| [references/agentic-evaluator.md](references/agentic-evaluator.md) | `AgenticEvaluator` full surface: every `evaluate_*` decorator, `AgenticApp`/`Node`/`MetricsConfiguration`, `AgenticAIConfiguration`, runs, `TracingConfiguration`/OTel, experiment tracking, `log_custom_metrics`, `compare_ai_experiments` |
| [references/model-risk-and-providers.md](references/model-risk-and-providers.md) | `ModelRiskEvaluator`, `ModelRiskConfiguration`, risk dimensions, the foundation-model provider classes (watsonx.ai / OpenAI / Azure / Bedrock / Vertex / Google AI Studio / RITS / custom), `WxGovConsoleConfiguration` + `WxGovConsoleCredentials`, `LLMJudge` |
| [references/factsheets-and-usecases.md](references/factsheets-and-usecases.md) | **`ibm-aigov-facts-client`** (different SDK): connect (project/space + `region="dallas"`), inventories, AI use cases (`create_ai_usecase`/`get_ai_usecases`), the `AIUsecaseUtilities` surface (facts, approaches, tracked models, workspaces, collaborators), model factsheets, external models — live-verified |
| [references/openscale-monitoring.md](references/openscale-monitoring.md) | **`ibm-watson-openscale`** (different SDK): production monitoring — datamarts, service providers, subscriptions, the 11 standard monitor types (drift/fairness/quality/explainability/GenAI quality/…), monitor instances, payload logging; the which-SDK decision table |

### Canonical external resources (you have internet access — use them)
- **`ibm-watsonx-gov` SDK docs (ground truth for signatures):** https://ibm.github.io/ibm-watsonx-gov/ (the local `REFERENCE-ibm-watsonx-gov-gh-pages` snapshot mirrors this — fetch the live page when a signature is in doubt). GitHub: https://github.com/IBM/ibm-watsonx-gov
- **`ibm-aigov-facts-client` (AI Factsheets):** PyPI https://pypi.org/project/ibm-aigov-facts-client/ — the dedicated docs site moves; prefer `help()` on the installed package and the IBM docs below. (Confirmed live URLs are flaky; don't hardcode a docs domain — verify before citing.)
- **`ibm-watson-openscale` SDK:** PyPI https://pypi.org/project/ibm-watson-openscale/ — same caveat; use `help()` + IBM docs.
- **watsonx.governance product docs (authoritative for all three):** https://www.ibm.com/docs/en/watsonx (evaluations, monitors, AI use cases / factsheets, model lifecycle, governance console)
- **PyPI / versions:** `pip show ibm-watsonx-gov ibm-aigov-facts-client ibm-watson-openscale`. Verified versions when this skill was written: `ibm-watsonx-gov` 1.5.0, `ibm-aigov-facts-client` 1.0.105, `ibm-watson-openscale` 3.1.7.

**Always prefer the live SDK docs / `help()` over memory when a signature is in
doubt, and read each metric's allowed `method`s and thresholds off the installed
class rather than trusting a hardcoded list.** This skill's core was verified
against `ibm-watsonx-gov` 1.5.0; the factsheets and monitoring references were
live-verified against `ibm-aigov-facts-client` 1.0.105 and `ibm-watson-openscale`
3.1.7 on a watsonx.governance SaaS instance.
