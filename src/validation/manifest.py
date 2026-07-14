"""Reproducibility manifest for validation runs.

Every validation run writes a manifest capturing enough provenance to reproduce
it: the code SHA + working-tree dirty flag, a hash of the exact input corpus,
the resolved config, the RNG seed, tracked library versions, and whether real
``tiktoken`` counting was in effect (as opposed to the ``chars/4`` fallback).

This is the artefact ``STATUS.md`` requires ("Every published savings/cost
number must cite a reproducible run with a manifest") and whose absence the
institutional audit flagged (A3). No number is publishable without one.
"""

from __future__ import annotations

import dataclasses
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

# Fields a complete manifest must carry, each non-empty. The CI validation gate
# fails the run if any is missing/empty -- an incomplete manifest is exactly the
# un-reproducible state Phase 5 exists to prevent.
REQUIRED_FIELDS: tuple[str, ...] = (
    "code_sha",
    "git_dirty",
    "data_hash",
    "config",
    "seed",
    "library_versions",
    "tiktoken_active",
    "model",
    "python_version",
    "platform",
    "timestamp",
)

# Libraries whose versions materially affect a token/savings measurement.
TRACKED_LIBRARIES: tuple[str, ...] = ("tiktoken", "scikit-learn", "numpy")


def _git(args: Sequence[str], repo_root: Path) -> Optional[str]:
    """Run a git command in ``repo_root``; return stdout, or ``None`` on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return result.stdout.strip()


def code_sha(repo_root: Path) -> Optional[str]:
    """Return the current ``HEAD`` commit SHA, or ``None`` outside a git repo."""
    return _git(["rev-parse", "HEAD"], repo_root)


def git_dirty(repo_root: Path) -> Optional[bool]:
    """Return whether the working tree has uncommitted changes.

    ``None`` when git is unavailable (so the manifest gate treats provenance as
    incomplete rather than silently claiming a clean tree).
    """
    status = _git(["status", "--porcelain"], repo_root)
    if status is None:
        return None
    return bool(status)


def library_versions(libraries: Sequence[str] = TRACKED_LIBRARIES) -> Dict[str, Optional[str]]:
    """Resolve installed versions of the tracked libraries (``None`` if absent)."""
    versions: Dict[str, Optional[str]] = {}
    for lib in libraries:
        try:
            versions[lib] = metadata.version(lib)
        except metadata.PackageNotFoundError:
            versions[lib] = None
    return versions


def build_manifest(
    *,
    config: Any,
    data_hash: str,
    seed: int,
    model: str,
    tiktoken_active: bool,
    repo_root: Path,
    timestamp: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble a reproducibility manifest.

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
    """
    if dataclasses.is_dataclass(config) and not isinstance(config, type):
        config_dict: Any = dataclasses.asdict(config)
    else:
        config_dict = config

    manifest: Dict[str, Any] = {
        "code_sha": code_sha(repo_root),
        "git_dirty": git_dirty(repo_root),
        "data_hash": data_hash,
        "config": config_dict,
        "seed": seed,
        "library_versions": library_versions(),
        "tiktoken_active": bool(tiktoken_active),
        "model": model,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        manifest["extra"] = extra
    return manifest


def missing_fields(manifest: Dict[str, Any]) -> list[str]:
    """Return the required fields that are absent or empty.

    ``git_dirty`` may legitimately be ``False`` (a clean tree) and ``seed`` may be
    ``0``; both are present, so only ``None`` / missing / empty-container values
    count as missing.
    """
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = manifest.get(field, None)
        if value is None:
            missing.append(field)
    # config and library_versions must be non-empty containers.
    for field in ("config", "library_versions"):
        value = manifest.get(field)
        if field not in missing and not value:
            missing.append(field)
    return missing


def write_manifest(path: Path, manifest: Dict[str, Any]) -> Path:
    """Write ``manifest`` to ``path`` as pretty JSON; return the path."""
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path
