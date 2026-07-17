# Container & Image Discipline
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: Platform Engineer -->

- Run as non-root; set a `USER`. No privileged containers.
- Pin base images by digest (or explicit tag) — never `:latest`.
- Multi-stage builds; no build secrets or credentials in any layer or `ENV`.
- Every workload declares resource requests/limits and liveness/readiness probes.
- Default-deny NetworkPolicies; expose only what the demo needs.
