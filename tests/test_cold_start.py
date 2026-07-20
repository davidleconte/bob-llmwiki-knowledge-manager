"""D1 / MEM-08: the auto-loaded cold-start map stays bounded and budget-gated.

`test_cold_start_map_under_budget` and `test_recent_additions_is_bounded` gate the
REAL repo state in CI (they run in the normal test job): if the cold map bloats or
Recent Additions regrows past 10, CI goes red. `test_cold_start_budget_gate` is the
meta-test proving the measurement flags an over-budget map.
"""

from __future__ import annotations

from pathlib import Path

from scripts.compact_index_recent_additions import compact
from src.cold_start import COLD_START_BUDGET_TOKENS, cold_start_files, cold_start_map_tokens

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = REPO_ROOT / "docs" / "knowledge-base" / "index.md"


def test_cold_start_files_come_from_settings():
    names = {f.name for f in cold_start_files(REPO_ROOT)}
    assert "index.md" in names, "the KB index is part of the auto-loaded cold-start map"


def test_cold_start_map_under_budget():
    """The real auto-loaded map is under budget — this IS the CI regression gate."""
    tokens = cold_start_map_tokens(REPO_ROOT)
    assert tokens <= COLD_START_BUDGET_TOKENS, (
        f"cold-start map {tokens} tokens > budget {COLD_START_BUDGET_TOKENS}; trim Recent "
        "Additions (scripts/compact_index_recent_additions.py) or move bulk content out of "
        "the auto-loaded map"
    )


def test_recent_additions_is_bounded():
    """index.md's Recent Additions is already ≤10 (compact is a no-op on the real file)."""
    idx = INDEX_MD.read_text(encoding="utf-8")
    assert compact(idx, keep=10) == idx, (
        "Recent Additions exceeds 10 entries — run "
        "scripts/compact_index_recent_additions.py docs/knowledge-base/index.md --keep 10"
    )


def test_cold_start_budget_gate(tmp_path):
    """Meta-test: an over-budget map is measured as over budget (the gate would fail)."""
    (tmp_path / ".bob").mkdir()
    (tmp_path / ".bob" / "settings.json").write_text(
        '{"context": {"fileName": ["big.md"]}}', encoding="utf-8"
    )
    (tmp_path / "big.md").write_text("word " * 30000, encoding="utf-8")
    assert cold_start_map_tokens(tmp_path) > COLD_START_BUDGET_TOKENS


def test_missing_settings_falls_back_to_default(tmp_path):
    (tmp_path / "AGENTS.md").write_text("hello cold start\n", encoding="utf-8")
    names = {f.name for f in cold_start_files(tmp_path)}
    assert "AGENTS.md" in names  # documented default when .bob/settings.json is absent


def test_empty_map_is_zero_tokens(tmp_path):
    assert cold_start_map_tokens(tmp_path) == 0  # no files present
