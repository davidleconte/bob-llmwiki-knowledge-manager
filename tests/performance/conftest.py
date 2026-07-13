"""Shared fixtures and configuration for performance tests.

Provides common fixtures and pytest configuration for performance benchmarks.
"""

import pytest


@pytest.fixture(scope="session")
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        "min_rounds": 5,
        "max_time": 1.0,
        "warmup": True,
    }


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for validation."""
    return {
        "l1_lookup_ms": 1.0,      # L1 cache lookup <1ms
        "l2_lookup_ms": 100.0,    # L2 cache lookup <100ms
        "token_count_ms": 10.0,   # Token counting <10ms per 1K tokens
        "optimization_ms": 50.0,  # Optimization <50ms
        "pipeline_ms": 100.0,     # Full pipeline <100ms
    }


def pytest_configure(config):
    """Configure pytest for performance tests."""
    config.addinivalue_line(
        "markers",
        "benchmark: mark test as a performance benchmark"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )


def pytest_benchmark_update_json(config, benchmarks, output_json):
    """Update benchmark JSON with custom metadata."""
    output_json["metadata"] = {
        "project": "Token Optimization System",
        "component": "Performance Tests",
        "targets": {
            "l1_cache": "<1ms",
            "l2_cache": "<100ms",
            "token_counting": "<10ms per 1K tokens",
            "optimization": "<50ms",
            "pipeline": "<100ms (p95)",
        }
    }
