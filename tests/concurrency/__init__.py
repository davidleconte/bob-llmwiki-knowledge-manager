"""Concurrency tests for Token Optimization System.

This package contains thread-safety and concurrency tests for cache operations.
Tests validate that components work correctly under concurrent access.

Test Categories:
- Thread-safety tests (concurrent reads/writes)
- Race condition detection
- Deadlock detection
- Stress tests under high concurrency

Usage:
    # Run all concurrency tests
    pytest tests/concurrency/ -v

    # Run with thread sanitizer
    pytest tests/concurrency/ -v --tb=short

    # Run stress tests only
    pytest tests/concurrency/ -v -k stress
"""
