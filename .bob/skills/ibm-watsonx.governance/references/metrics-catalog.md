# Metrics catalog — groups, classes, methods, thresholds

> Verified against `ibm-watsonx-gov` 1.5.0 (`[metrics]` extra). All metric classes
> import from `ibm_watsonx_gov.metrics`. **The allowed computation `method`s are
> a typed `Literal` on each class** — read them off the installed class
> (`Metric.model_fields["method"].annotation`) rather than trusting any list here
> verbatim; they can change between versions.

## Metric groups (`MetricGroup` enum)

`from ibm_watsonx_gov.entities.enums import MetricGroup`

`retrieval_quality`, `answer_quality`, `content_safety`, `performance`, `usage`,
`message_completion`, `tool_call_quality`, `readability`, `custom`.

Pass a whole group to an evaluator (`metric_groups=[MetricGroup.RETRIEVAL_QUALITY]`)
to compute all its metrics, or pass individual metric objects for control.

## Retrieval quality — `MetricGroup.RETRIEVAL_QUALITY`
Needs `context_fields` (and usually `input_fields`). Reference-free.

| Class | Notes |
|---|---|
| `ContextRelevanceMetric` | methods: `token_precision` (default), `sentence_bert_bge`, `sentence_bert_mini_lm`, `llm_as_judge`, `granite_guardian`, `context_relevance_model`. Has `compute_per_context`. |
| `RetrievalPrecisionMetric` | precision of retrieved chunks |
| `NDCGMetric` | normalized discounted cumulative gain |
| `ReciprocalRankMetric` | mean reciprocal rank |
| `HitRateMetric` | hit rate over retrieved set |
| `AveragePrecisionMetric` | average precision |

## Answer quality — `MetricGroup.ANSWER_QUALITY`
Needs `output_fields`; some need `input_fields`/`context_fields`/`reference_fields`.

| Class | Notes |
|---|---|
| `AnswerRelevanceMetric` | relevance of answer to the question |
| `FaithfulnessMetric` | grounding of answer in context. methods: `token_k_precision` (default), `sentence_bert_mini_lm`, `llm_as_judge`, `granite_guardian`, `faithfulness_model` |
| `AnswerSimilarityMetric` | **reference-based** — needs `reference_fields`. methods: `token_recall` (default), `bert_score_recall`, `sentence_bert_mini_lm`, `llm_as_judge` |
| `UnsuccessfulRequestsMetric` | rate of unsuccessful/declined responses |

## Content safety — `MetricGroup.CONTENT_SAFETY`
Guardrail metrics; mostly reference-free, applied to input and/or output text.
Many support a `granite_guardian` method.

`HAPMetric` (+ `InputHAPMetric`, `OutputHAPMetric`) — hate/abuse/profanity ·
`PIIMetric` (+ `InputPIIMetric`, `OutputPIIMetric`) — personally identifiable info ·
`HarmMetric` · `HarmEngagementMetric` · `JailbreakMetric` ·
`PromptSafetyRiskMetric` · `ProfanityMetric` · `SexualContentMetric` ·
`SocialBiasMetric` · `ViolenceMetric` · `UnethicalBehaviorMetric` ·
`EvasivenessMetric`.

The `Input*`/`Output*` variants let you score the user prompt and the model
output separately (vs the combined metric).

## Tool-call quality — `MetricGroup.TOOL_CALL_QUALITY`
For agents that call tools/functions. Needs `tools`, `tool_calls_field`,
`available_tools_field` configured.

`ToolCallAccuracyMetric` · `ToolCallParameterAccuracyMetric` ·
`ToolCallRelevanceMetric` · `ToolCallSyntacticAccuracyMetric`.

## Readability — `MetricGroup.READABILITY`
`TextGradeLevelMetric` · `TextReadingEaseMetric` (Flesch-style scores on output).

## Performance — `MetricGroup.PERFORMANCE`
`DurationMetric` — latency. Needs `start_time_field`/`end_time_field` (or is
captured automatically by `AgenticEvaluator`).

## Usage — `MetricGroup.USAGE`
`CostMetric` · `InputTokenCountMetric` · `OutputTokenCountMetric`. Driven by
`input_token_count_fields` / `output_token_count_fields` /
`model_usage_detail_fields`.

## Message / other
`TopicRelevanceMetric` · `StatusMetric` (`status_field`) · `UserIdMetric`
(`user_id_field`) · `ExecutionStepsMetric` (agentic execution steps).

## Custom metrics — `MetricGroup.CUSTOM`
Define your own checks:

| Class | Use |
|---|---|
| `LLMAsJudgeMetric` | score with an LLM judge against your own criteria/prompt |
| `LLMValidationMetric` | LLM-based pass/fail validation |
| `KeywordDetectionMetric` | flag presence of keywords |
| `RegexDetectionMetric` | flag matches of a regex |

These typically need an `llm_judge` (judge-based) or pattern/keyword args. Inspect
the class fields and docstring for exact parameters.

## Common metric fields (all metrics)
`name`, `display_name`, `method`, `value_type`, `thresholds` (list of
`MetricThreshold`), `tasks` (applicable `TaskType`s), `group`, `is_reference_free`,
`metric_dependencies`, `applies_to`, `target_component`, `mapping`, `llm_judge`.

Choosing a `method`: local methods (`token_*`, `sentence_bert_*`,
`bert_score_*`, `*_model`) compute without an LLM call — fast, cheap, may need the
`[local-evals]` extra. `llm_as_judge` / `granite_guardian` are more accurate but
invoke a model — set `llm_judge` and mind cost/latency.
