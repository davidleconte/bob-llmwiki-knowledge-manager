# Observability Baseline
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: Platform Engineer -->

- Emit structured logs (JSON), one event per line; no `print()` debugging left in.
- Propagate a correlation/request ID across services and into logs.
- Expose health (`/healthz`) and readiness endpoints; expose RED metrics for
  services (Rate, Errors, Duration) and USE for resources (Utilization, Saturation, Errors).
- Never log secrets, tokens, or real PII. Set log levels via config, not code edits.
- Errors carry actionable context (what failed, which input, which correlation ID).
