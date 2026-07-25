#!/usr/bin/env python3
"""Pin the hand-written architecture layer to ``src/``, the way the API docs are pinned.

Why this gate exists (2026-07-25 full-project audit, finding A-11)
------------------------------------------------------------------
``docs/api/`` was in perfect sync — 55 generated module docs for 55 modules — while
``docs/architecture/ARCHITECTURE.md``, which calls itself "the single authoritative
architecture document", described **none** of six modules added after its last update:

    attest.py  cold_start.py  kb_paths.py  limits.py  provenance.py  velocity.py

Two of those are security controls: ``provenance.py`` carries the signature check the
verify-at-read fix depends on, and ``limits.py`` is the CODEOWNERS-reviewed single home
for the A7 input-bound caps. ``attest.py``, ``cold_start.py`` and ``kb_paths.py``
appeared in *zero* live documents anywhere.

The difference between the two layers was not care — it was that one had a gate
(``generate_api_docs.py --check``) and the other did not. The generated layer stayed
correct precisely because drift failed CI. This applies the same pin to the layer that
actually drifts, because it is hand-written.

Contract
--------
Every module under ``src/`` (excluding dunder and private modules) must be named by at
least one of:

* ``docs/architecture/ARCHITECTURE.md`` — the authoritative architecture document, or
* any ADR under ``docs/adr/`` — a recorded decision about it.

Naming means the module *path* or its stem appears in the prose. That is a deliberately
low bar: this gate catches "nobody wrote it down at all", not "the description is thin".
Prose quality is a review concern, not a mechanical one.

Usage::

    python scripts/check_architecture_freshness.py
    python scripts/check_architecture_freshness.py --selftest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHITECTURE_DOC = "docs/architecture/ARCHITECTURE.md"
ADR_DIR = "docs/adr"

# Modules that are entry points or plumbing rather than architectural surface. Kept
# short and explicit: every entry is a decision someone can challenge in review.
EXEMPT_STEMS: frozenset[str] = frozenset(
    {
        "__init__",
        "__main__",
    }
)


def source_modules(repo_root: Path | None = None) -> list[str]:
    """Repo-relative paths of every architecturally-relevant module under ``src/``."""
    root = repo_root or REPO_ROOT
    out: list[str] = []
    for path in sorted((root / "src").rglob("*.py")):
        if path.stem in EXEMPT_STEMS or path.stem.startswith("_"):
            continue
        out.append(path.relative_to(root).as_posix())
    return out


def _architecture_corpus(repo_root: Path | None = None) -> str:
    """Concatenated text of the architecture doc plus every ADR."""
    root = repo_root or REPO_ROOT
    parts: list[str] = []
    arch = root / ARCHITECTURE_DOC
    if arch.exists():
        parts.append(arch.read_text(encoding="utf-8", errors="replace"))
    adr_dir = root / ADR_DIR
    if adr_dir.exists():
        for adr in sorted(adr_dir.glob("*.md")):
            parts.append(adr.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def undocumented(repo_root: Path | None = None) -> list[str]:
    """Modules named by neither the architecture doc nor any ADR."""
    corpus = _architecture_corpus(repo_root)
    missing: list[str] = []
    for rel in source_modules(repo_root):
        stem = Path(rel).stem
        # Either the full path or the bare module name counts as "named".
        if rel in corpus or stem in corpus:
            continue
        missing.append(rel)
    return missing


def _selftest() -> int:
    """Prove the gate fails on an undocumented module and passes on a documented one."""
    import tempfile

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "docs/architecture").mkdir(parents=True)
        (root / "docs/adr").mkdir(parents=True)
        (root / "src/documented.py").write_text("x = 1\n", encoding="utf-8")
        (root / "src/undocumented.py").write_text("x = 1\n", encoding="utf-8")
        (root / "src/__init__.py").write_text("", encoding="utf-8")
        (root / "src/by_adr.py").write_text("x = 1\n", encoding="utf-8")
        (root / ARCHITECTURE_DOC).write_text(
            "The facade calls documented for things.\n", encoding="utf-8"
        )
        (root / "docs/adr/001-x.md").write_text("We chose by_adr for reasons.\n", encoding="utf-8")

        missing = undocumented(root)
        if "src/undocumented.py" not in missing:
            failures.append("MISSED: an undocumented module must be reported")
        if "src/documented.py" in missing:
            failures.append("FALSE POSITIVE: a module named in ARCHITECTURE.md must pass")
        if "src/by_adr.py" in missing:
            failures.append("FALSE POSITIVE: a module named in an ADR must pass")
        if "src/__init__.py" in missing:
            failures.append("FALSE POSITIVE: __init__ is exempt")

    if failures:
        print("Self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("Self-test passed: undocumented module caught; documented/ADR/exempt modules clean.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="verify the gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    modules = source_modules()
    missing = undocumented()
    if not missing:
        print(f"All {len(modules)} src/ modules are named by {ARCHITECTURE_DOC} or an ADR.")
        return 0

    print(f"Checking {len(modules)} src/ modules against {ARCHITECTURE_DOC} + {ADR_DIR}/:\n")
    for rel in missing:
        print(f"  MISSING  {rel}")
    print(
        f"\nFAILED: {len(missing)} module(s) appear in neither the authoritative "
        f"architecture document nor any ADR.\n"
        "A module nobody wrote down is a module nobody can review. Describe it in "
        f"{ARCHITECTURE_DOC} (§2 overview / §5 per-component), or record the decision "
        "as an ADR. This is the same pin that keeps docs/api/ correct, applied to the "
        "hand-written layer — which is the layer that actually drifts.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
