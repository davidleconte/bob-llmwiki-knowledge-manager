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

### `_is_excluded(path: Path) -> bool`


### `load_repo_prose(repo_root: Path, globs: Iterable[str], min_words: int) -> List[Document]`

Load the committed real-prose corpus (the CI tier).

Deterministic: files are returned sorted by relative path so the corpus hash
and per-document ordering are stable across runs.


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

