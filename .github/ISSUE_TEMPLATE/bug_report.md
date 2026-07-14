---
name: Bug report
about: Report a defect so it can be reproduced and fixed
title: "[bug] "
labels: bug
assignees: davidleconte
---

## Summary

A clear, one-sentence description of the bug.

## Reproduction

Steps to reproduce the behavior — include the exact command:

```bash
# e.g. python -m src optimize "..." or bob-optimize ...
```

## Expected vs. actual

- **Expected:** what you thought would happen.
- **Actual:** what actually happened (paste the full error / output).

## Environment

- Package version (`python -c "import src; print(src.__version__)"`):
- Python version (`python --version`): <!-- 3.11 or 3.12 supported -->
- OS:
- Install method (`pip install -e ".[dev,monitoring]"`, etc.):

## Additional context

Anything else that helps — logs, a minimal snippet, related issues.

> Security vulnerability? **Do not file it here.** Follow `SECURITY.md`
> (GitHub Private Vulnerability Reporting).
