# `MetricsEvaluator` — batch evaluation, configuration, results

> Verified against `ibm-watsonx-gov` 1.5.0. Needs the `[metrics]` extra.

`from ibm_watsonx_gov.evaluators import MetricsEvaluator`
(or `from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator`).

It's a pydantic model with two fields:
- `api_client` — an `APIClient` (optional; a default SaaS client is built from
  `WATSONX_APIKEY` if omitted).
- `configuration` — a `GenAIConfiguration` (optional; a default mapping is used).

## `evaluate()`

```python
result = evaluator.evaluate(
    data,                       # pd.DataFrame | dict
    metrics=[...],              # list[GenAIMetric], e.g. [AnswerRelevanceMetric()]
    metric_groups=[...],        # list[MetricGroup], e.g. [MetricGroup.CONTENT_SAFETY]
    **kwargs,
)  # -> MetricsEvaluationResult
```
- `data` is a `pd.DataFrame` (many records) or a `dict` (one record).
- Pass `metrics`, `metric_groups`, or both. Groups expand to all metrics in the
  group, so you can mix a group with extra individual metrics.
- There is also `evaluate_async(...)` for the same call in an async context.

## `GenAIConfiguration` — the field-name mapping

`from ibm_watsonx_gov.config import GenAIConfiguration`. This is how metrics find
their inputs in your data. **Defaults are fixed strings** — override them when
your columns differ.

| Field | Default | Role |
|---|---|---|
| `input_fields` | `["input_text"]` | the user input / question / prompt |
| `context_fields` | `["context"]` | retrieved context (RAG) |
| `output_fields` | `["generated_text"]` | the model's answer |
| `reference_fields` | `["ground_truth"]` | gold/reference answer (reference-based metrics) |
| `prompt_field` | `"model_prompt"` | full prompt sent to the model |
| `record_id_field` | `"record_id"` | unique row id |
| `record_timestamp_field` | `"record_timestamp"` | row timestamp |
| `task_type` | `None` | a `TaskType` (RAG, QA, summarization, …) |
| `locale` | `None` | language/locale |
| `llm_judge` | `None` | an `LLMJudge` for judge-based metric methods |
| `tools`, `tool_calls_field`, `available_tools_field` | — | tool-call metrics |
| `input_token_count_fields`, `output_token_count_fields`, `model_usage_detail_fields` | — | usage metrics |
| `start_time_field`, `end_time_field` | `None` | latency/performance metrics |
| `status_field`, `user_id_field` | `"status"`, `"user_id"` | message status / user id |

`TaskType` values: `question_answering`, `classification`, `summarization`,
`generation`, `extraction`, `retrieval_augmented_generation`
(`from ibm_watsonx_gov.entities.enums import TaskType`).

```python
config = GenAIConfiguration(
    task_type=TaskType.RAG,
    input_fields=["question"],
    context_fields=["retrieved_context"],
    output_fields=["answer"],
    reference_fields=["ground_truth"],
)
```

## Per-metric tuning: `method` and `thresholds`

Each metric class carries (among others) these fields:
`name`, `method`, `thresholds`, `group`, `tasks`, `is_reference_free`,
`llm_judge`, `mapping`.

- **`method`** — a typed `Literal` per metric controlling *how* the score is
  computed (cheap/local vs LLM-judge). Read the allowed values off the class, e.g.
  `ContextRelevanceMetric.model_fields["method"].annotation`. See
  `metrics-catalog.md`.
- **`thresholds`** — turn a raw score into pass/fail:
  ```python
  from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
  from ibm_watsonx_gov.metrics import AnswerRelevanceMetric
  m = AnswerRelevanceMetric(
      thresholds=[MetricThreshold(type="lower_limit", value=0.7)])
  ```
  `MetricThreshold.type` is `"lower_limit"` or `"upper_limit"`; `value` is a float
  (0–1 for most quality metrics). A score past the limit is flagged a violation.
- **`llm_judge`** — set on the metric (or on the configuration) when its `method`
  is judge-based. See `model-risk-and-providers.md` for `LLMJudge`.

## The result object — `MetricsEvaluationResult`

`from ibm_watsonx_gov.entities.evaluation_result import MetricsEvaluationResult`

Export helpers:
- `result.to_df()` → tidy `pd.DataFrame` of metric values (one row per record ×
  metric, or aggregate, depending on the metric).
- `result.to_json()` → JSON string.
- `result.to_dict()` → dict.

Underlying result classes (you mostly read them via `to_df()`):
`RecordMetricResult` (per-row value), `AggregateMetricResult` (dataset-level
summary), `BaseMetricResult`.

Display (needs a notebook/display env; `display_insights` needs `[visualization]`):
- `evaluator.display_table()` — tabular view.
- `evaluator.display_insights()` — richer visualization.

## Quick single-record smoke test

```python
from ibm_watsonx_gov.evaluators import MetricsEvaluator
from ibm_watsonx_gov.metrics import HAPMetric

evaluator = MetricsEvaluator()             # uses WATSONX_APIKEY + default config
result = evaluator.evaluate(
    data={"input_text": "Tell me something nice.",
          "generated_text": "You are doing great today!"},
    metrics=[HAPMetric()],
)
print(result.to_df())
```

## Gotchas
- Wrong/renamed columns → metric reads the wrong field or errors. Map them.
- Reference-based metrics (e.g. `AnswerSimilarityMetric`) need `reference_fields`.
- `llm_as_judge` / `granite_guardian` methods make model calls — set `llm_judge`
  and expect latency/token cost.
- `display_*` produce no output outside a notebook — use `to_df()`/`to_json()`.
