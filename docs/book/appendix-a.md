# Appendix A: API Reference

> **This appendix is a redirect, deliberately.**
>
> The API reference is **generated from source docstrings** and pinned to `src/` by a
> CI gate (`scripts/generate_api_docs.py --check`). It cannot drift without failing the
> build.
>
> **→ [`docs/api/`](../api/README.md)** — 55 module documents, one per module.

## Why this appendix no longer contains an API reference

It used to. Until 2026-07-25 this file hand-maintained class signatures alongside the
generated reference, and the 2026-07-25 audit found the predictable result: **every
documented import was wrong.**

```python
from src.cache import L1Cache   # ImportError: cannot import name 'L1Cache'
from src.cache import L2Cache   # ImportError
```

The real exports are `CacheEntry`, `CacheInterface`, `ExactCache`, `MultiLevelCache`,
`SemanticCache`. The classes had been renamed; the generated reference followed
automatically, and this hand-written copy did not — because nothing checked it.

That is the whole argument for the redirect. Two references to the same API, one
generated and gated and one written by hand, is not redundancy — it is a guarantee that
a reader will eventually trust the wrong one. The audit's broader finding had the same
shape: `docs/api/` was in perfect sync at 55/55 modules while the hand-written
architecture document had silently lost six of them, and the difference was not care but
the presence of a gate.

## Where to find what this appendix used to promise

| You want… | Go to |
|---|---|
| Class and function signatures | [`docs/api/`](../api/README.md) — generated, CI-pinned |
| Which component does what, and why | [`docs/architecture/ARCHITECTURE.md`](../architecture/ARCHITECTURE.md) §5 |
| The facade's public surface | [`docs/api/root/facade.md`](../api/root/facade.md) |
| Cache internals | [`docs/api/cache/multi_level_cache.md`](../api/cache/multi_level_cache.md) · [Chapter 4](chapter-04.md) |
| CLI subcommands | `bob-optimize --help`, or [`docs/README.md`](../README.md) |
| Configuration | [Appendix B](appendix-b.md) · [`src/config/schema.py`](../../src/config/schema.py) |

The previous hand-written content is in git history:
`git show 5d7b799:docs/archive/book-appendix-a.md`.
