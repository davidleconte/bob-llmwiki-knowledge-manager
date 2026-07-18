## What & why

<!-- What does this change do, and why? Link the issue/ADR if there is one. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactor / tooling / CI
- [ ] Security

## Checklist

Every box should be checked before requesting review (CI enforces most of them):

- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `mypy` passes
- [ ] `pytest --cov=src` passes and coverage stays **≥ 80%**
- [ ] Static gates pass: `check_layering.py`, `check_savings_claims.py`,
      `check_value_homes.py`, `check_status_consistency.py`,
      `check_community_health.py`
- [ ] `bandit -r src/ -ll` is clean (any `# nosec` is scoped and justified)
- [ ] Touched a `src/` docstring/signature? Ran
      `python scripts/generate_api_docs.py` and committed `docs/api/`
- [ ] No fabricated metrics — any savings/coverage/perf figure cites a real
      artifact (manifest, test, or `STATUS.md`)
- [ ] If test count or coverage % changed: **`STATUS.md` Terminology guardrail
      updated** in this same PR (old → new values in commit message)
- [ ] No edits to frozen audit-trail files (dated snapshots, superseded docs)
- [ ] Change verified end-to-end (ran the affected flow), not just compiled

## Notes for the reviewer

<!-- Anything non-obvious: trade-offs, follow-ups, things you're unsure about. -->
