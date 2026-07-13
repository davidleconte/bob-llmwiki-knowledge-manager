"""
Pytest configuration and fixtures for Bob Shell Knowledge Manager tests.

This file ensures proper PYTHONPATH setup and provides common fixtures
for all test modules.
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
from hypothesis import HealthCheck, settings

# Deterministic hypothesis profile: the example stream is a pure function of the
# test (derandomize=True) with no persisted database, so property tests are
# reproducible across runs and machines — the suite's determinism guarantee is
# load-bearing. deadline=None disables per-example wall-clock deadlines (avoids
# flaky timing failures); the global pytest ``timeout=60`` still bounds each test.
settings.register_profile(
    "ci",
    derandomize=True,
    deadline=None,
    max_examples=200,
    database=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
settings.load_profile("ci")


@pytest.fixture(autouse=True)
def _reset_monitoring_singletons():
    """Isolate every test from the process-global monitoring singletons.

    ``get_metrics_collector`` / ``get_health_checker`` / ``get_cost_tracker``
    return module-level singletons that otherwise accumulate state across tests
    (recorded cache hits, registered health checks), coupling test ordering and
    masking bugs. Reset them before and after each test so each starts clean.
    Lazy imports keep a monitoring import error from breaking unrelated tests.
    """
    def _reset():
        from src.monitoring.metrics import reset_metrics
        from src.monitoring.health import reset_health_checker
        from src.monitoring.cost_tracker import reset_cost_tracker
        reset_metrics()
        reset_health_checker()
        reset_cost_tracker()

    _reset()
    yield
    _reset()


@pytest.fixture
def sample_prompt():
    """Fixture providing a sample prompt for testing."""
    return "Analyze this codebase and create documentation"


@pytest.fixture
def sample_text():
    """Fixture providing sample text for truncation testing."""
    return "This is a sample text for testing truncation strategies. " * 100


@pytest.fixture
def mock_cache_data():
    """Fixture providing mock cache data."""
    return {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Fixture providing a temporary directory for cache testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
