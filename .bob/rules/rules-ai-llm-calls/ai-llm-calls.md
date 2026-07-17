# LLM Call Discipline
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: AI Engineer -->

- Pin the model ID explicitly; never rely on a provider "latest" alias in a demo.
- Every call has a timeout, a retry policy (exponential backoff, capped attempts),
  and a token/cost budget. No silent infinite retries.
- Validate structured output against a schema before use; on parse failure, retry
  or fail loudly — never pass through unvalidated model output.
- Pin temperature/seed where the demo must be reproducible.
- Log prompt + response for evaluation; never log secrets or real PII.
