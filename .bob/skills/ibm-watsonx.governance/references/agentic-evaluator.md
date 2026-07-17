# `AgenticEvaluator` — evaluating agentic applications

> Verified against `ibm-watsonx-gov` 1.5.0. Needs the `[agentic]` extra (pulls in
> `nbformat`, `IPython`, OpenTelemetry, etc.).

`from ibm_watsonx_gov.evaluators import AgenticEvaluator`

Pydantic model fields: `api_client`, `agentic_app`, `tracing_configuration`,
`ai_experiment_client`, `max_concurrency`.

Evaluation happens **around a run**. You always:
```python
agentic_evaluator.start_run()        # open the run
# ... invoke your agent / graph ...
agentic_evaluator.end_run()          # close it
result = agentic_evaluator.get_result()
```
With **no configuration**, you still get performance (latency, duration) and usage
(cost, input/output token counts) metrics for free.

## Three levels of metrics

1. **Agent / message level** — over the whole interaction. Configured via
   `AgenticApp.metrics_configuration`.
2. **Node level** — per graph node. Configured via `AgenticApp.nodes[].metrics_configurations`,
   or via decorators on the node functions.
3. **Real-time vs post-hoc** — decorators with `compute_real_time=True` (default)
   compute during graph execution; declarative node config computes at `end_run()`.

## Style A — decorators on node functions

One `evaluate_*` decorator per metric/group. Apply to the function implementing a
graph node; it computes that node's metric(s) when the node runs.

```python
from ibm_watsonx_gov.evaluators import AgenticEvaluator
from ibm_watsonx_gov.config import AgenticAIConfiguration

agentic_evaluator = AgenticEvaluator()

@agentic_evaluator.evaluate_retrieval_quality(
    configuration=AgenticAIConfiguration(input_fields=["input_text"],
                                         context_fields=["local_context"]))
@agentic_evaluator.evaluate_content_safety()        # default field mapping
def local_search_node(state, config):
    return {"local_context": [...]}
```

Every decorator has the signature:
`evaluate_X(func=None, *, configuration: AgenticAIConfiguration = None,
metrics: list[GenAIMetric] = [], compute_real_time: bool = True) -> dict`.

**Available decorators** (mirror the metric catalog):
`evaluate_retrieval_quality`, `evaluate_answer_quality`, `evaluate_content_safety`,
`evaluate_readability`, `evaluate_answer_relevance`, `evaluate_answer_similarity`,
`evaluate_faithfulness`, `evaluate_context_relevance`, `evaluate_average_precision`,
`evaluate_ndcg`, `evaluate_hit_rate`, `evaluate_reciprocal_rank`,
`evaluate_retrieval_precision`, `evaluate_unsuccessful_requests`,
`evaluate_hap`, `evaluate_pii`, `evaluate_harm`, `evaluate_harm_engagement`,
`evaluate_jailbreak`, `evaluate_prompt_safety_risk`, `evaluate_profanity`,
`evaluate_sexual_content`, `evaluate_social_bias`, `evaluate_violence`,
`evaluate_unethical_behavior`, `evaluate_evasiveness`, `evaluate_topic_relevance`,
`evaluate_text_grade_level`, `evaluate_text_reading_ease`,
`evaluate_tool_call_accuracy`, `evaluate_tool_call_parameter_accuracy`,
`evaluate_tool_call_relevance`, `evaluate_tool_call_syntactic_accuracy`,
`evaluate_keyword_detection`, `evaluate_regex`,
`evaluate_general_quality_with_llm` (LLM-as-judge custom quality).

## Style B — declarative `AgenticApp`

```python
from ibm_watsonx_gov.entities.agentic_app import AgenticApp, Node, MetricsConfiguration
from ibm_watsonx_gov.metrics import AnswerRelevanceMetric, ContextRelevanceMetric
from ibm_watsonx_gov.entities.enums import MetricGroup

agentic_app = AgenticApp(
    name="My Agent",
    metrics_configuration=MetricsConfiguration(           # agent/message level
        metrics=[AnswerRelevanceMetric()],
        metric_groups=[MetricGroup.CONTENT_SAFETY]),
    nodes=[Node(name="Retrieval Node",
                metrics_configurations=[MetricsConfiguration(
                    configuration=...,                    # optional AgenticAIConfiguration
                    metrics=[ContextRelevanceMetric()],
                    metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])],
)
agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app, api_client=api_client)
```

- **`AgenticApp`** fields: `name`, `message_io_mapping`, `metrics_configuration`,
  `nodes`.
- **`Node`** fields: `name`, `func_name`, `metrics_configurations`,
  `foundation_models`.
- **`MetricsConfiguration`** fields: `configuration` (an `AgenticAIConfiguration`),
  `metrics`, `metric_groups`.

## `AgenticAIConfiguration`

`from ibm_watsonx_gov.config import AgenticAIConfiguration`. Same field set as
`GenAIConfiguration` (see `metrics-evaluator.md`) **plus** two agent fields:
`message_id_field`, `conversation_id_field`. Use it to map a node's/graph's state
attribute names to metric roles when they aren't the defaults.

## The result

`get_result(run_name=None) -> AgenticEvaluationResult`. Plus:
- `get_metric_result(metric_name, node_name) -> AgentMetricResult` — one metric on
  one node.
- `get_nodes() -> list[Node]` — discovered nodes.
- `generate_insights()` / `log_custom_metrics(custom_metrics)` — visualize / push
  your own metric values into the run.

## Experiment tracking & tracing

Track runs as **AI experiments** and emit **OpenTelemetry** traces.

```python
from ibm_watsonx_gov.config.agentic_ai_configuration import TracingConfiguration
from ibm_watsonx_gov.entities.ai_experiment import AIExperimentRunRequest

tracing = TracingConfiguration(project_id="PROJECT_ID")   # or space_id=...
agentic_evaluator = AgenticEvaluator(tracing_configuration=tracing, api_client=api_client)

agentic_evaluator.track_experiment(name="my_experiment")      # use_existing=True by default
agentic_evaluator.start_run(AIExperimentRunRequest(name="run1"))
# ... invoke agent ...
agentic_evaluator.end_run()
result = agentic_evaluator.get_result()

# Compare multiple runs of the experiment
agentic_evaluator.compare_ai_experiments(...)
```
- **`TracingConfiguration`** fields: `project_id`, `space_id`,
  `resource_attributes`, `otlp_collector_config` (export to your own OTLP
  collector), `log_traces_to_file`.
- **`track_experiment(name, description=None, use_existing=True) -> str`** —
  creates/attaches an experiment, returns its id.
- **`start_run(run_request=AIExperimentRunRequest(...)) -> AIExperimentRun`**.
  `AIExperimentRunRequest` fields: `name`, `description`, `source_name`,
  `source_url`, `custom_tags`, `agent_method_name`.
- **`end_run(track_notebook=False)`**.

## Gotchas
- Forgetting `start_run()`/`end_run()` → empty result.
- Decorator `configuration` must map the **node's state attribute names** (e.g.
  `local_context`) — not the global defaults — or the metric reads nothing.
- `compute_real_time=True` runs the metric inside graph execution (adds latency
  to that node); set `False` to defer to `end_run()`.
- Judge-based decorators (`evaluate_general_quality_with_llm`, any `llm_as_judge`
  method) invoke a model — configure an `llm_judge` and expect cost.
