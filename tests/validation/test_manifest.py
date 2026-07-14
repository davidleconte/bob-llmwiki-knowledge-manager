"""Tests for the reproducibility manifest writer."""

from __future__ import annotations

import json
from pathlib import Path

from src.config.schema import CacheConfig, ConfigSchema, MonitoringConfig, OptimizerConfig
from src.validation.manifest import (
    REQUIRED_FIELDS,
    build_manifest,
    code_sha,
    git_dirty,
    library_versions,
    missing_fields,
    write_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _schema() -> ConfigSchema:
    return ConfigSchema(CacheConfig(), OptimizerConfig(), MonitoringConfig())


def test_build_manifest_has_all_required_fields():
    manifest = build_manifest(
        config=_schema(),
        data_hash="abc123",
        seed=0,
        model="gpt-4",
        tiktoken_active=True,
        repo_root=REPO_ROOT,
    )
    for field in REQUIRED_FIELDS:
        assert field in manifest, f"missing {field}"
    # config is serialized from the dataclass into a nested dict.
    assert manifest["config"]["optimizer"]["max_tokens"] == 4096
    assert manifest["seed"] == 0
    assert manifest["tiktoken_active"] is True


def test_missing_fields_empty_for_complete_manifest():
    manifest = build_manifest(
        config=_schema(),
        data_hash="abc123",
        seed=7,
        model="gpt-4",
        tiktoken_active=True,
        repo_root=REPO_ROOT,
    )
    assert missing_fields(manifest) == []


def test_missing_fields_detects_none_and_empty():
    manifest = build_manifest(
        config=_schema(),
        data_hash="abc",
        seed=0,
        model="gpt-4",
        tiktoken_active=True,
        repo_root=REPO_ROOT,
    )
    manifest["code_sha"] = None
    manifest["config"] = {}
    missing = missing_fields(manifest)
    assert "code_sha" in missing
    assert "config" in missing


def test_seed_zero_and_clean_tree_are_not_missing():
    # seed=0 (falsy) and git_dirty=False (falsy) must count as present.
    manifest = build_manifest(
        config=_schema(),
        data_hash="abc",
        seed=0,
        model="gpt-4",
        tiktoken_active=True,
        repo_root=REPO_ROOT,
    )
    manifest["git_dirty"] = False
    assert "seed" not in missing_fields(manifest)
    assert "git_dirty" not in missing_fields(manifest)


def test_library_versions_reports_tiktoken():
    versions = library_versions()
    assert "tiktoken" in versions
    assert versions["tiktoken"] is not None


def test_git_provenance_available_in_repo():
    sha = code_sha(REPO_ROOT)
    assert sha is not None and len(sha) == 40
    assert isinstance(git_dirty(REPO_ROOT), bool)


def test_git_provenance_none_outside_repo(tmp_path):
    # A bare temp dir is not a git repo; provenance must degrade to None, not lie.
    assert code_sha(tmp_path) is None
    assert git_dirty(tmp_path) is None


def test_write_manifest_round_trips(tmp_path):
    manifest = build_manifest(
        config=_schema(),
        data_hash="abc",
        seed=1,
        model="gpt-4",
        tiktoken_active=True,
        repo_root=REPO_ROOT,
    )
    path = write_manifest(tmp_path / "sub" / "manifest.json", manifest)
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["data_hash"] == "abc"
    assert loaded["model"] == "gpt-4"
