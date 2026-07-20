"""MEM-10: the lessons delta is content-hash based, not mtime based.

Locks the property the old ``find -newer`` scan in ``mnemox-lessons.sh`` got wrong:
a file whose mtime moved (``git checkout`` / ``clone`` / ``touch``) but whose bytes
are unchanged must NOT be reported as a new/changed analysis report; a file whose
content changed must be.
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.mnemox_doc_delta import compute_delta, read_manifest, write_manifest


def _seed(research: Path, name: str, body: str) -> Path:
    research.mkdir(parents=True, exist_ok=True)
    p = research / name
    p.write_text(body, encoding="utf-8")
    return p


def test_new_file_is_in_delta(tmp_path):
    research = tmp_path / "research"
    _seed(research, "a.md", "alpha")
    manifest = tmp_path / "hashes"
    assert compute_delta(research, manifest) == [str(research / "a.md")]


def test_mtime_change_without_content_change_is_not_in_delta(tmp_path):
    """The core MEM-10 fix: bump mtime only -> hash unchanged -> not reported."""
    research = tmp_path / "research"
    f = _seed(research, "a.md", "alpha")
    manifest = tmp_path / "hashes"
    write_manifest(research, manifest)  # baseline captured

    # Move mtime far forward WITHOUT touching content (what git checkout / touch do).
    future = f.stat().st_mtime + 10_000
    os.utime(f, (future, future))

    assert compute_delta(research, manifest) == [], (
        "a file with a new mtime but identical content must NOT be a 'new report'"
    )


def test_content_change_is_in_delta(tmp_path):
    research = tmp_path / "research"
    f = _seed(research, "a.md", "alpha")
    manifest = tmp_path / "hashes"
    write_manifest(research, manifest)

    f.write_text("alpha revised", encoding="utf-8")
    assert compute_delta(research, manifest) == [str(f)]


def test_update_makes_next_delta_empty(tmp_path):
    research = tmp_path / "research"
    _seed(research, "a.md", "alpha")
    _seed(research, "b.md", "beta")
    manifest = tmp_path / "hashes"

    assert len(compute_delta(research, manifest)) == 2  # both new
    write_manifest(research, manifest)
    assert compute_delta(research, manifest) == []  # captured -> nothing new


def test_manifest_roundtrip(tmp_path):
    research = tmp_path / "research"
    _seed(research, "a.md", "alpha")
    manifest = tmp_path / "hashes"
    write_manifest(research, manifest)
    parsed = read_manifest(manifest)
    assert str(research / "a.md") in parsed
    assert len(parsed[str(research / "a.md")]) == 64  # sha256 hex
