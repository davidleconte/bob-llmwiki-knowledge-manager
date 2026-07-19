"""ATK-GATE-07 regression: gate independence — config file exists and is consistent.

Tests:
  1. config/gates/gate-config.yaml must exist.
  2. The fail_under value in gate-config.yaml must match pyproject.toml.
  3. The live_docs list in gate-config.yaml must match LIVE_DOCS in the gate script.
"""

from pathlib import Path

import pytest

try:
    import yaml  # optional — PyYAML
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GATE_CONFIG = REPO_ROOT / "config" / "gates" / "gate-config.yaml"


def test_gate_config_exists():
    """config/gates/gate-config.yaml must exist (ATK-GATE-07)."""
    assert GATE_CONFIG.exists(), (
        f"config/gates/gate-config.yaml not found at {GATE_CONFIG}. "
        "Gate configuration must be externalized."
    )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed — skipping value cross-checks")
def test_fail_under_matches_pyproject():
    """coverage_gate.fail_under in gate-config.yaml must match pyproject.toml."""
    import re
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r"^\s*fail_under\s*=\s*(\d+)", pyproject, re.MULTILINE)
    assert m, "fail_under not found in pyproject.toml"
    expected = int(m.group(1))

    config = yaml.safe_load(GATE_CONFIG.read_text(encoding="utf-8"))
    actual = config["coverage_gate"]["fail_under"]
    assert actual == expected, (
        f"config/gates/gate-config.yaml coverage_gate.fail_under={actual} "
        f"!= pyproject.toml fail_under={expected}"
    )


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed — skipping value cross-checks")
def test_live_docs_matches_gate_script():
    """status_gate.live_docs in gate-config.yaml must match LIVE_DOCS in the gate script."""
    from scripts.check_status_consistency import LIVE_DOCS as SCRIPT_LIVE_DOCS

    config = yaml.safe_load(GATE_CONFIG.read_text(encoding="utf-8"))
    config_docs = set(config["status_gate"]["live_docs"])
    script_docs = set(SCRIPT_LIVE_DOCS)

    extra_in_config = config_docs - script_docs
    extra_in_script = script_docs - config_docs

    assert not extra_in_config and not extra_in_script, (
        f"LIVE_DOCS mismatch between gate-config.yaml and check_status_consistency.py:\n"
        f"  only in config: {extra_in_config}\n"
        f"  only in script: {extra_in_script}"
    )
