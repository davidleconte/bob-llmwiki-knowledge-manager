# `ModelRiskEvaluator`, foundation-model providers, LLM judge

> Verified against `ibm-watsonx-gov` 1.5.0. `ModelRiskEvaluator` needs the `[mre]`
> extra.

## `ModelRiskEvaluator`

`from ibm_watsonx_gov.evaluators import ModelRiskEvaluator`

Assesses a foundation model against **risk dimensions**, scores them, and produces
a PDF report — optionally synced to the watsonx **Governance Console**. Pydantic
fields: `api_client`, `configuration` (a `ModelRiskConfiguration`).

```python
from ibm_watsonx_gov.evaluators import ModelRiskEvaluator
from ibm_watsonx_gov.config import ModelRiskConfiguration
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel

model_details = WxAIFoundationModel(
    model_name="my_granite",
    model_id="ibm/granite-3-3-8b-instruct",
    project_id="PROJECT_ID",            # or space_id=...
)
config = ModelRiskConfiguration(
    model_details=model_details,
    risk_dimensions=["hallucination", "jailbreaking", "harmful-code-generation"],
    max_sample_size=500,                # positive int; samples used during eval
    thresholds=(20, 80),                # (lower, upper), each 0–100, lower < upper
    pdf_report_output_path="/reports",
)
evaluator = ModelRiskEvaluator(configuration=config, api_client=api_client)
result = evaluator.evaluate()           # no data arg — it samples/probes the model
result.to_json()
evaluator.display_table()
evaluator.download_model_risk_report()  # write/fetch the PDF
```

### `ModelRiskConfiguration` fields
`model_details` (a `FoundationModel`, required) · `risk_dimensions` (list of risk
category strings, e.g. `hallucination`, `jailbreaking`, `harmful-code-generation`)
· `max_sample_size` (positive int) · `thresholds` (`(lower, upper)` tuple, 0–100,
validated lower < upper) · `pdf_report_output_path` · `wx_gc_configuration`
(optional Governance Console sync).

## Foundation-model providers

The model under test (and judge models) can come from any supported provider.
`from ibm_watsonx_gov.entities.foundation_model import ...`

| Class | Key fields |
|---|---|
| `WxAIFoundationModel` | `model_name`, `model_id`, `project_id`, `space_id`, `provider` |
| `OpenAIFoundationModel` | `model_name`, `model_id`, `parameters`, `provider` |
| `AzureOpenAIFoundationModel` | `model_name`, `model_id`, `provider` |
| `AWSBedrockFoundationModel` | `model_id`, `parameters`, `provider` |
| `VertexAIFoundationModel` | `model_name`, `model_id`, `provider` |
| `GoogleAIStudioFoundationModel` | `model_name`, `model_id`, `provider` |
| `RITSFoundationModel` | IBM Research inference (RITS) |
| `CustomFoundationModel` | `model_name`, `provider` — bring your own |

Each has a matching `*ModelProvider` carrying provider credentials/config
(`WxAIModelProvider`, `OpenAIModelProvider`, `AzureOpenAIModelProvider`,
`AWSBedrockModelProvider`, `VertexAIModelProvider`, `GoogleAIStudioModelProvider`,
`RITSModelProvider`, `PortKeyModelProvider`, `WxoAIGatewayModelProvider`,
`CustomModelProvider`). `ModelProviderType` enum values:
`ibm_watsonx.ai`, `azure_openai`, `rits`, `openai`, `vertex_ai`,
`google_ai_studio`, `aws_bedrock`, `custom`, `portkey`, `wxo_ai_gateway`.

Provider credentials are read from environment variables when you create the
provider from env (e.g. `AWSBedrockCredentials.create_from_env()` reads
`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION`). Inspect the
specific provider's docstring for its env-var names and required fields.

## `LLMJudge` — model-as-a-judge

`from ibm_watsonx_gov.entities.llm_judge import LLMJudge`. Wraps a foundation
model used to *judge* outputs for judge-based metric methods (`llm_as_judge`) and
custom metrics (`LLMAsJudgeMetric`, `LLMValidationMetric`).

```python
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel

judge = LLMJudge(model=WxAIFoundationModel(
    model_id="meta-llama/llama-3-3-70b-instruct", project_id="PROJECT_ID"))
```
Attach it where a judge is needed: on the configuration (`GenAIConfiguration(
llm_judge=judge)` / `AgenticAIConfiguration(llm_judge=judge)`) or on the metric
(`AnswerRelevanceMetric(llm_judge=judge, method="llm_as_judge")`).

> Judge calls cost tokens and add latency. Prefer local methods when accuracy
> allows; use a judge when the metric genuinely needs reasoning.

## Governance Console sync (`WxGovConsoleConfiguration`)

To push model-risk results into the watsonx **Governance Console** (OpenPages):

```python
from ibm_watsonx_gov.config import WxGovConsoleCredentials
from ibm_watsonx_gov.config.model_risk_configuration import WxGovConsoleConfiguration

wx_gc = WxGovConsoleConfiguration(
    model_id="model-abc123",                      # the console's model id
    credentials=WxGovConsoleCredentials(
        url="https://governance.example.com",
        username="admin",
        password=os.environ["WXGC_PASSWORD"],     # or api_key=...
    ),
)
config = ModelRiskConfiguration(..., wx_gc_configuration=wx_gc)
```
- `WxGovConsoleCredentials` fields: `url`, `username`, `password`, `api_key`.
- `WxGovConsoleConfiguration` fields: `model_id`, `credentials`.

## Gotchas
- `[mre]` extra required, or `ModelRiskEvaluator` won't import.
- `evaluate()` here takes **no data** — it samples/probes the configured model, so
  it makes real model calls (cost/runtime scales with `max_sample_size` and the
  number of `risk_dimensions`). State the implication before running.
- `thresholds` must be `(lower, upper)` with `0 <= lower < upper <= 100` or
  validation fails.
- `WxAIFoundationModel` needs `project_id` **or** `space_id`.
