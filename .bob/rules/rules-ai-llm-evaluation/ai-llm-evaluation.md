# LLM Evaluation Gate
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: AI Engineer -->

- A prompt/model/RAG change is not "done" until a golden-set evaluation passes.
  Keep the golden set in-repo and version-controlled.
- Define explicit success criteria per task (exact match, schema-valid, rubric score)
  — no "looks good to me" sign-off.
- No silent model or prompt swaps: changes that affect output go through the eval.
- Track regressions; a change that drops a metric is a failure, not a trade-off to ignore.
- Evaluate on synthetic data only (per the data-handling rule), never real client data.
