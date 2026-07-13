"""Performance tests for Token Optimization System.

This package contains performance benchmarks using pytest-benchmark.
Tests measure latency, throughput, and resource usage for critical components.

Test Categories:
- Cache performance (L1, L2, multi-level)
- Token counting performance
- Optimizer performance
- End-to-end system performance

Usage:
    # Run all performance tests
    pytest tests/performance/ -v --benchmark-only

    # Run specific test group
    pytest tests/performance/ -v --benchmark-only --benchmark-group=cache

    # Generate HTML report
    pytest tests/performance/ --benchmark-only --benchmark-autosave

    # Compare with baseline
    pytest tests/performance/ --benchmark-only --benchmark-compare=0001
"""
