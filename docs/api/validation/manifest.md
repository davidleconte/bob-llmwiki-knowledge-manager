# manifest

Reproducibility manifest for validation runs.

Every validation run writes a manifest capturing enough provenance to reproduce
it: the code SHA + working-tree dirty flag, a hash of the exact input corpus,
the resolved config, the RNG seed, tracked library versions, and whether real
``tiktoken`` counting was in effect (as opposed to the ``chars/4`` fallback).

This is the artefact ``STATUS.md`` requires ("Every published savings/cost
number must cite a reproducible run with a manifest") and whose absence the
institutional audit flagged (A3). No number is publishable without one.

## Functions

### `_git(args: Sequence[str], repo_root: Path) -> Optional[str]`

Run a git command in ``repo_root``; return stdout, or ``None`` on failure.


### `code_sha(repo_root: Path) -> Optional[str]`

Return the current ``HEAD`` commit SHA, or ``None`` outside a git repo.


### `git_dirty(repo_root: Path) -> Optional[bool]`

Return whether the working tree has uncommitted changes.

``None`` when git is unavailable (so the manifest gate treats provenance as
incomplete rather than silently claiming a clean tree).


### `library_versions(libraries: Sequence[str]) -> Dict[str, Optional[str]]`

Resolve installed versions of the tracked libraries (``None`` if absent).


### `build_manifest() -> Dict[str, Any]`

Assemble a reproducibility manifest.

Args:
    config: The resolved config (a dataclass, serialized via ``asdict``, or a
        dict passed through as-is).
    data_hash: sha256 over the exact input corpus (see ``corpus.hash_corpus``).
    seed: RNG seed used for the null shuffle / bootstrap / cache workload.
    model: Model name the token counts were produced for.
    tiktoken_active: Whether real tiktoken counting was in effect.
    repo_root: Repository root, for the git provenance calls.
    timestamp: ISO timestamp; defaults to now (UTC).
    extra: Optional run-scoped metadata (corpus name, doc count, ...).


### `missing_fields(manifest: Dict[str, Any]) -> list[str]`

Return the required fields that are absent or empty.

``git_dirty`` may legitimately be ``False`` (a clean tree) and ``seed`` may be
``0``; both are present, so only ``None`` / missing / empty-container values
count as missing.


### `write_manifest(path: Path, manifest: Dict[str, Any]) -> Path`

Write ``manifest`` to ``path`` as pretty JSON; return the path.

