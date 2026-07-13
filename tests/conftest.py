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
