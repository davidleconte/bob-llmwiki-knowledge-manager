"""Input corpora for validation.

The only honest basis for a savings measurement is real prose. Measuring on the
repeated-word test fixtures or the Lorem-ipsum data under ``evaluation/data``
inflates optimizer savings (the redundancy pass deletes near-everything) -- that
is precisely the artefact Phase 5 undoes, so those sources are excluded here.

Two tiers are provided:

* :func:`load_repo_prose` -- the committed, CI-runnable tier: real technical
  markdown from ``examples/*/docs/knowledge-base`` and the repo's own ``docs/``.
* :func:`load_session_transcripts` -- the optional higher-credibility tier: real
  prompts captured from live sessions. Skipped gracefully when absent.

:func:`make_null_corpus` builds the shuffled/high-entropy null on which real
compression must collapse to near zero (the "shuffled-labels" analogue).
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Document:
    """A single real text input to measure against."""

    source: str
    text: str


# Glob patterns (relative to repo root) for the committed real-prose corpus.
REPO_PROSE_GLOBS: tuple[str, ...] = (
    "examples/*/docs/knowledge-base/**/*.md",
    "docs/**/*.md",
)

# The frozen hold-out slice (corpus B, C4/ATK-GATE-01): a fixed i.i.d. subset of the
# real repo prose, held out from corpus A. Because B is drawn from the SAME
# distribution as A, an honest headline reproduces on B within sampling error (~0.5pp
# measured), while a cherry-picked A diverges (~9pp measured). The path list is FROZEN
# in this manifest so a cherry-pick cannot pre-arrange B.
HOLDOUT_MANIFEST: str = "evaluation/holdout/holdout-manifest.json"


def load_holdout_paths(repo_root: Path) -> set[str]:
    """Return the frozen set of hold-out relative paths (empty if the manifest absent)."""
    manifest = repo_root / HOLDOUT_MANIFEST
    if not manifest.exists():
        return set()
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return set()
    return {str(p) for p in data.get("paths", [])}


# Path fragments that mark synthetic / mock / invalid inputs. Any candidate whose
# path contains one of these is dropped -- measuring there is the fraud undone.
EXCLUDE_FRAGMENTS: tuple[str, ...] = (
    "evaluation/data",
    "/node_modules/",
    "/.venv/",
)

# Minimum token-ish length (in whitespace words) for a file to count as real
# prose worth measuring; skips near-empty stubs.
MIN_WORDS: int = 20


def _is_excluded(path: Path) -> bool:
    posix = path.as_posix()
    return any(fragment in posix for fragment in EXCLUDE_FRAGMENTS)


def load_repo_prose(
    repo_root: Path,
    globs: Iterable[str] = REPO_PROSE_GLOBS,
    min_words: int = MIN_WORDS,
) -> List[Document]:
    """Load the committed real-prose corpus (the CI tier).

    Deterministic: files are returned sorted by relative path so the corpus hash
    and per-document ordering are stable across runs. The frozen hold-out slice
    (corpus B, C4) is **excluded** so A and B are disjoint — a headline measured
    here must reproduce on the held-out prose it never saw.
    """
    holdout = load_holdout_paths(repo_root)
    seen: dict[str, Document] = {}
    for pattern in globs:
        for path in repo_root.glob(pattern):
            if not path.is_file() or _is_excluded(path):
                continue
            rel = path.relative_to(repo_root).as_posix()
            if rel in seen or rel in holdout:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if len(text.split()) < min_words:
                continue
            seen[rel] = Document(source=rel, text=text)
    return [seen[key] for key in sorted(seen)]


def load_holdout(
    repo_root: Path,
    min_words: int = MIN_WORDS,
) -> List[Document]:
    """Load the frozen hold-out slice (corpus B, C4) named in the manifest.

    Loads exactly the paths frozen in
    ``evaluation/holdout/holdout-manifest.json`` that still exist. Deterministic
    (sorted). Returns ``[]`` when the manifest is absent (e.g. a synthetic test
    root), so a corpus-B-less run degrades gracefully — :func:`src.validation.holdout_ok`
    then treats the check as not-applicable.
    """
    holdout_paths = load_holdout_paths(repo_root)
    docs: dict[str, Document] = {}
    for rel in holdout_paths:
        path = repo_root / rel
        if not path.is_file():
            continue  # frozen path since removed/renamed -> skip (graceful)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if len(text.split()) < min_words:
            continue
        docs[rel] = Document(source=rel, text=text)
    return [docs[key] for key in sorted(docs)]


def _extract_prompt(payload: object) -> Optional[str]:
    """Pull a prompt string out of a captured-session JSON record, tolerantly."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("prompt", "query", "input", "content", "text", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None


def load_session_transcripts(
    sessions_dir: Path,
    min_words: int = MIN_WORDS,
) -> List[Document]:
    """Load the optional higher-credibility tier: real captured-session prompts.

    Returns ``[]`` when the directory is absent. Files whose names start with
    ``test_`` are skipped -- those are the random mock records the analysis tools
    generate, not real captures.
    """
    if not sessions_dir.exists():
        return []
    docs: dict[str, Document] = {}
    for path in sorted(sessions_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("test_"):
            continue
        source = path.name
        text: Optional[str] = None
        if path.suffix == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(payload, list):
                parts = [p for p in (_extract_prompt(item) for item in payload) if p]
                text = "\n\n".join(parts) if parts else None
            else:
                text = _extract_prompt(payload)
        elif path.suffix in (".md", ".txt"):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
        if text and len(text.split()) >= min_words:
            docs[source] = Document(source=f"session:{source}", text=text)
    return [docs[key] for key in sorted(docs)]


def hash_corpus(docs: Iterable[Document]) -> str:
    """sha256 over the corpus contents (order-independent), for the manifest."""
    hasher = hashlib.sha256()
    for doc in sorted(docs, key=lambda d: d.source):
        hasher.update(doc.source.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(doc.text.encode("utf-8"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def make_null_corpus(docs: Iterable[Document], seed: int) -> List[Document]:
    """Build the null corpus: each document's words shuffled, single-spaced.

    Shuffling destroys repeated phrases and collapses whitespace, so a correct
    optimizer should achieve near-zero real reduction here. The ``seed`` (recorded in
    the manifest) makes the shuffle reproducible.
    """
    rng = random.Random(seed)
    null_docs: List[Document] = []
    for doc in docs:
        words = doc.text.split()
        rng.shuffle(words)
        null_docs.append(Document(source=f"null:{doc.source}", text=" ".join(words)))
    return null_docs
