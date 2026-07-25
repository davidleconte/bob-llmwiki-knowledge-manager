# corpus

Input corpora for validation.

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

## Functions

### `load_holdout_paths(repo_root: Path) -> set[str]`

Return the frozen set of hold-out relative paths (empty if the manifest absent).


### `_is_excluded(path: Path) -> bool`


### `load_repo_prose(repo_root: Path, globs: Iterable[str], min_words: int) -> List[Document]`

Load the committed real-prose corpus (the CI tier).

Deterministic: files are returned sorted by relative path so the corpus hash
and per-document ordering are stable across runs. The frozen hold-out slice
(corpus B, C4) is **excluded** so A and B are disjoint — a headline measured
here must reproduce on the held-out prose it never saw.


### `load_holdout(repo_root: Path, min_words: int) -> List[Document]`

Load the frozen hold-out slice (corpus B, C4) named in the manifest.

Loads exactly the paths frozen in ``evaluation/holdout/holdout-manifest.json``.
Deterministic (sorted). Returns ``[]`` when the manifest is absent (e.g. a
synthetic test root), so a corpus-B-less run degrades gracefully —
:func:`src.validation.holdout_ok` then treats the check as not-applicable.

**Fails closed on a missing frozen path** (audit 2026-07-25). This previously
skipped absent paths "gracefully", which quietly defeated the property the frozen
slice exists for. B is the cherry-pick detector precisely because its membership is
fixed in advance; if members can vanish without complaint, then B *can* be
pre-arranged — by deleting the inconvenient ones. It is not hypothetical: pruning
``docs/architecture/deprecated/`` during this audit's own remediation silently took
corpus B from 35 to 33 and every hold-out test still passed green.

A missing member now raises. The manifest's own discipline note already said
"Refresh only in its own PR with a rationale" — this makes that enforceable rather
than advisory.


### `_extract_prompt(payload: object) -> Optional[str]`

Pull a prompt string out of a captured-session JSON record, tolerantly.


### `load_session_transcripts(sessions_dir: Path, min_words: int) -> List[Document]`

Load the optional higher-credibility tier: real captured-session prompts.

Returns ``[]`` when the directory is absent. Files whose names start with
``test_`` are skipped -- those are the random mock records the analysis tools
generate, not real captures.


### `hash_corpus(docs: Iterable[Document]) -> str`

sha256 over the corpus contents (order-independent), for the manifest.


### `make_null_corpus(docs: Iterable[Document], seed: int) -> List[Document]`

Build the null corpus: each document's words shuffled, single-spaced.

Shuffling destroys repeated phrases and collapses whitespace, so a correct
optimizer should achieve near-zero real reduction here. The ``seed`` (recorded in
the manifest) makes the shuffle reproducible.


## Classes

### `Document`

A single real text input to measure against.

