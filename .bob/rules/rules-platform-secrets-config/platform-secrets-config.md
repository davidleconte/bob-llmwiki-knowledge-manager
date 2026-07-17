# Secrets & Configuration (12-Factor)
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: Platform Engineer / AI Engineer -->

- All config and secrets come from the environment / a secret manager — never
  hardcoded, never committed. Provide a `.env.example` with no real values.
- Mock mode runs with ZERO credentials; missing secrets degrade to mock, never crash.
- Fail fast and clearly on missing *required* config at startup — no silent defaults
  that mask misconfiguration.
- Separate config (per-environment) from code (same across environments).
- Rotate keys after exposure; least-privilege scopes for every token and DB role.
