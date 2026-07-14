# Contributing

Thanks for your interest in improving `bob-llmwiki-knowledge-manager`. This
project is under an audit-driven remediation program, so it holds a high bar
for correctness, honest measurement, and CI-enforced invariants. This guide
tells you how to work with those gates rather than against them.

## Ground rules

- **No fabricated numbers.** Every performance, savings, or coverage figure in
  a doc must trace to a real artifact (a manifest under `evaluation/results/`,
  a test, or `STATUS.md`). The `check_savings_claims.py` gate enforces this;
  see the retraction history in `CHANGELOG.md` for why.
- **One home per value.** A value duplicated across ≥2 hand-maintained files
  needs a machine check. Add it to `scripts/check_value_homes.py` rather than
  copy-pasting a literal.
- **Don't edit frozen audit trail.** Dated files (`*-2026-07-*.md`),
  `PHASE*_IMPLEMENTATION_COMPLETE.md`, and superseded/deprecated docs are
  point-in-time records. Add new docs instead of rewriting history.

## Development setup

The project uses a `pyproject.toml`-only layout (no `requirements.txt`) and a
virtual environment. [`uv`](https://github.com/astral-sh/uv) is recommended:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,monitoring]"
```

Plain `pip` works too: `pip install -e ".[dev,monitoring]"`.

Supported Python: **3.11 and 3.12** (the runtime floor is 3.11; CI tests both).

## The gate suite (run before you push)

CI runs these on every PR. Run them locally first — they are fast and have no
external dependencies:

```bash
# Lint / format / static gates (single Python)
ruff check .
ruff format --check .
python scripts/check_layering.py src
python scripts/check_savings_claims.py
python scripts/check_value_homes.py
python scripts/check_community_health.py
python scripts/generate_api_docs.py --check
bandit -r src/ -ll

# Type gate
mypy

# Tests + coverage (must stay >= 80%)
pytest --cov=src
python scripts/check_coverage_by_package.py coverage.json
python scripts/check_status_consistency.py
```

A few reminders these gates encode:

- **Touched a `src/` docstring or signature?** Regenerate the API docs
  (`python scripts/generate_api_docs.py`) and commit `docs/api/`, or
  `--check` fails.
- **Added a governance/community-health file?** `check_community_health.py`
  tracks the required set — keep it in sync.
- **Added a security-sensitive code path?** `bandit` runs on `src/`; justify
  any unavoidable finding with a scoped `# nosec` and a reason, never a blanket
  disable.

## Commits and pull requests

- Branch off `main`; keep each PR focused (the repo works in small, reviewable
  commits grouped into one phase PR).
- Write descriptive commit messages explaining the *why*. Co-authored commits
  should keep their trailers.
- Fill in the pull-request template checklist. A PR is ready when every gate is
  green and the change is verified end-to-end (see the `verify` discipline in
  the docs), not just when tests compile.

## Reporting security issues

Do **not** file security reports as public issues. Follow
[`SECURITY.md`](SECURITY.md) (GitHub Private Vulnerability Reporting).
