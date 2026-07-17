# API & FastAPI Backend Discipline
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: AI Engineer / Platform Engineer -->

- Validate every request at the boundary with explicit schemas (Pydantic models);
  reject unknown/extra fields. Allowlist, don't denylist.
- Deny-by-default authorization; check permissions on every protected route.
- Never return stack traces, secrets, or internal identifiers to clients. Map errors
  to clean status codes with safe messages.
- Idempotency keys for side-effecting / money-moving endpoints; safe retries.
- Paginate list endpoints; select only required fields. No unbounded result sets.
- Use async route handlers for I/O-bound work (see the Python concurrency rule).
