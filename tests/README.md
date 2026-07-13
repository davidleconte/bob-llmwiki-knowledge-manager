# Test Suite Documentation

**Last Updated:** 2026-07-13  
**Test Framework:** pytest  
**Python Version:** 3.8+

---

## Test Statistics

Snapshot from CI, 2026-07-13 (point-in-time; the authoritative status is
[`STATUS.md`](../STATUS.md)):

```
Total Tests:    676 (641 passed, 23 skipped, 12 xfailed)
Coverage:       82.5%  (gate: >=80%, enforced by pyproject.toml fail_under)
```

The `xfailed` tests are strict-xfail markers for known gaps (config not yet wired
to runtime, etc.), so they fail loudly if they start passing. Skips are the
flag-gated e2e/real-LLM suites and optional-dependency smoke tests.

---

## Test Organization

### Directory Structure

```
tests/
├── README.md                    # This file
├── __init__.py
├── test_mode_config.py         # Bob Shell mode tests
├── test_templates.py           # Template validation tests
├── test_workflows.py           # Workflow tests
├── cache/                      # Cache system tests (72 tests)
│   ├── test_base.py
│   ├── test_exact_cache.py
│   ├── test_semantic_cache.py
│   ├── test_multi_level_cache.py
│   └── test_embeddings.py
├── optimizer/                  # Optimizer tests (38 tests)
│   ├── test_token_counter.py
│   └── test_prompt_optimizer.py
├── truncation/                 # Truncation tests (32 tests)
│   ├── test_strategies.py
│   └── test_truncator.py
└── monitoring/                 # Monitoring tests (28 tests)
    ├── test_logger.py
    ├── test_metrics.py
    └── test_health.py          # Health checker tests
```

### Test Categories

| Category | Tests | Status | Coverage |
|----------|-------|--------|----------|
| Cache (L1/L2) | 72 | ✅ 100% Pass | Excellent |
| Optimizer | 38 | ✅ 100% Pass | Excellent |
| Truncation | 32 | ✅ 100% Pass | Excellent |
| Monitoring | 28 | ✅ Pass | Good |
| Integration | 18 | ✅ 100% Pass | Excellent |
| Performance | 15 | ✅ 100% Pass | Excellent |
| Batch | 15 | ✅ 100% Pass | Excellent |
| Formatter | 12 | ✅ 100% Pass | Excellent |
| E2E | 10 | ✅ 100% Pass | Excellent |
| Mode Config | 3 | ✅ 100% Pass | Good |
| Templates | 2 | ✅ 100% Pass | Good |
| Workflows | 2 | ✅ 100% Pass | Good |

---

## Skipped Tests (5 Total)

### 1. Timing-Based Tests (2 skipped)

**Location:** `tests/monitoring/test_health.py`

**Tests:**
- `test_check_cache_health_high_latency`
- `test_check_optimizer_health_high_latency`

**Skip Reason:**
```python
pytest.skip("Time mocking in health checks needs refactoring")
```

**Explanation:**
Mock-based timing tests are unreliable because:
- Time mocking with `unittest.mock` is complex and brittle
- Mock timing doesn't reflect real-world latency behavior
- Tests would require significant refactoring to use proper time mocking libraries

**Impact:** **Low**
- Latency is tested in integration tests with real components
- Performance tests validate actual timing behavior
- Health checks work correctly in production

**Future Work:**
- Refactor to use `freezegun` or similar time mocking library
- Or convert to integration tests with real timing measurements

---

### 2. psutil-Dependent Tests (3 skipped)

**Location:** `tests/monitoring/test_health.py`

**Tests:**
- `test_check_system_resources_healthy`
- `test_check_system_resources_degraded`
- `test_check_system_resources_unhealthy`

**Skip Reason:**
```python
pytest.skip("psutil is optional dependency - test requires psutil installed")
```

**Explanation:**
`psutil` is an **optional dependency** for system resource monitoring:
- Not required for core functionality
- System works perfectly without it
- Graceful degradation when psutil is unavailable

**Code Behavior Without psutil:**
```python
# From src/monitoring/health.py
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def check_system_resources(self) -> ComponentHealth:
    if not PSUTIL_AVAILABLE:
        return ComponentHealth(
            name="system_resources",
            status=HealthStatus.DEGRADED,
            message="psutil not available - system monitoring disabled"
        )
```

**Impact:** **Low**
- System monitoring is an optional feature
- Core caching, optimization, and truncation work without psutil
- Production deployments can choose to install psutil or not

**Running These Tests:**
```bash
# Install psutil
pip install psutil

# Run the tests
python3 -m pytest tests/monitoring/test_health.py -v
```

---

## Running Tests

### Run All Tests

```bash
# Standard run
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=src --cov-report=html

# Fast run (parallel)
python3 -m pytest tests/ -n auto
```

### Run Specific Test Categories

```bash
# Cache tests only
python3 -m pytest tests/cache/ -v

# Optimizer tests only
python3 -m pytest tests/optimizer/ -v

# Truncation tests only
python3 -m pytest tests/truncation/ -v

# Monitoring tests only
python3 -m pytest tests/monitoring/ -v
```

### Run Without Skipped Tests

```bash
# Exclude monitoring tests (contains skips)
python3 -m pytest tests/ -v --ignore=tests/monitoring/test_health.py

# Or run only passing tests
python3 -m pytest tests/ -v -k "not (high_latency or system_resources)"
```

### Run With psutil Tests

```bash
# Install psutil first
pip install psutil

# Run all monitoring tests
python3 -m pytest tests/monitoring/ -v
```

---

## Test Coverage

Coverage is enforced by a single gate — `fail_under` in
`pyproject.toml` (`[tool.coverage.report]`) — **not** by hand-maintained numbers
in this file. Per-package floors (e.g. `monitoring`, `delegation`) live in
`scripts/check_coverage_by_package.py`. Measured total was **82.5%** as of
2026-07-13; regenerate with:

```bash
pytest --cov=src --cov-report=term-missing
python scripts/check_coverage_by_package.py coverage.json
```

---

## Test Types

### 1. Unit Tests (250+ tests)

**Purpose:** Test individual components in isolation

**Characteristics:**
- Use mocks for dependencies
- Fast execution (<1s)
- Contribute to the enforced coverage gate (see Test Coverage above)

**Example:**
```python
def test_exact_cache_get_hit(self):
    cache = ExactCache()
    cache.set("key", "value")
    assert cache.get("key") == "value"
```

### 2. Integration Tests (40+ tests)

**Purpose:** Test component interactions

**Characteristics:**
- Real components (no mocks)
- Medium execution time (1-2s)
- Tests realistic scenarios

**Example:**
```python
def test_multi_level_cache_promotion(self):
    l1 = ExactCache()
    l2 = SemanticCache()
    cache = MultiLevelCache(l1, l2)
    
    # L2 hit should promote to L1
    cache.set("query", "response")
    result = cache.get("similar query")  # L2 hit
    result = cache.get("similar query")  # Now L1 hit
```

### 3. Performance Tests (15+ tests)

**Purpose:** Validate latency targets

**Characteristics:**
- Measure actual timing
- Assert performance requirements
- Detect regressions

**Example:**
```python
def test_l1_cache_latency(self):
    cache = ExactCache()
    cache.set("key", "value")
    
    start = time.perf_counter()
    cache.get("key")
    latency = (time.perf_counter() - start) * 1000
    
    assert latency < 1.0  # <1ms requirement
```

### 4. End-to-End Tests (10+ tests)

**Purpose:** Test complete workflows

**Characteristics:**
- Full system integration
- Real-world scenarios
- Comprehensive validation

**Example:**
```python
def test_complete_optimization_pipeline(self):
    # Initialize system
    cache = MultiLevelCache(...)
    optimizer = PromptOptimizer(...)
    truncator = Truncator(...)
    
    # Process request
    result = cache.get(query)
    if not result:
        optimized = optimizer.optimize(query)
        truncated = truncator.truncate(context)
        # ... complete workflow
```

---

## Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def exact_cache():
    """Provide clean ExactCache instance."""
    return ExactCache(max_size=100)

@pytest.fixture
def semantic_cache():
    """Provide clean SemanticCache instance."""
    return SemanticCache(max_size=50, threshold=0.85)

@pytest.fixture
def multi_level_cache(exact_cache, semantic_cache):
    """Provide complete multi-level cache."""
    return MultiLevelCache(exact_cache, semantic_cache)
```

---

## Continuous Integration

### CI Pipeline

```yaml
# .github/workflows/tests.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src
```

### Test Requirements

**Minimum:**
- All tests must pass (excluding intentional skips)
- Coverage must stay at or above the gate (`fail_under` in `pyproject.toml`, currently >=80%), and per-package floors (`scripts/check_coverage_by_package.py`) must hold
- No new skipped tests without justification

**Recommended:**
- Add tests for new features
- Update tests when refactoring
- Document skip reasons clearly

---

## Troubleshooting

### Common Issues

#### Issue 1: Import Errors

**Symptom:**
```
ImportError: No module named 'src'
```

**Solution:**
```bash
# Run from repository root
cd /path/to/bob-llmwiki-knowledge-manager
python3 -m pytest tests/ -v
```

#### Issue 2: psutil Tests Failing

**Symptom:**
```
ModuleNotFoundError: No module named 'psutil'
```

**Solution:**
```bash
# Option 1: Install psutil
pip install psutil

# Option 2: Skip these tests (they're optional)
python3 -m pytest tests/ -v --ignore=tests/monitoring/test_health.py
```

#### Issue 3: Slow Test Execution

**Symptom:**
Tests take >10 seconds to run

**Solution:**
```bash
# Run in parallel
pip install pytest-xdist
python3 -m pytest tests/ -n auto
```

---

## Contributing

### Adding New Tests

1. **Choose appropriate location:**
   - Unit tests: `tests/<component>/test_<module>.py`
   - Integration tests: `tests/integration/test_<feature>.py`
   - E2E tests: `tests/e2e/test_<workflow>.py`

2. **Follow naming conventions:**
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

3. **Write clear test names:**
   ```python
   # Good
   def test_cache_returns_none_on_miss(self):
   
   # Bad
   def test_cache(self):
   ```

4. **Add docstrings:**
   ```python
   def test_cache_hit_rate_calculation(self):
       """Test that hit rate is calculated correctly."""
   ```

5. **Use fixtures for setup:**
   ```python
   @pytest.fixture
   def cache(self):
       return ExactCache(max_size=100)
   
   def test_something(self, cache):
       # Use cache fixture
   ```

### Skipping Tests

**Only skip tests if:**
1. Feature is optional (like psutil)
2. Test requires refactoring (document why)
3. Test is platform-specific

**Always:**
- Use `pytest.skip()` with clear reason
- Document in this README
- Assess impact (Low/Medium/High)
- Plan future work

**Example:**
```python
def test_optional_feature(self):
    """Test optional feature - skipped if dependency missing."""
    pytest.skip("Requires optional dependency X - install with pip install X")
```

---

## Future Improvements

### Planned Enhancements

1. **E2E Tests with Real LLM** (P0)
   - Add `tests/e2e/test_real_llm.py`
   - Test with actual Bob Shell API
   - Measure real token savings
   - Validate performance claims

2. **Refactor Timing Tests** (P2)
   - Use `freezegun` for time mocking
   - Or convert to integration tests
   - Remove current skips

3. **Property-Based Testing** ✅ DONE
   - `hypothesis` is wired in (see `tests/property/`)
   - Cache round-trip invariant: `tests/property/test_cache_roundtrip.py`
   - Truncation budget invariant: `tests/property/test_truncation.py`

4. **Load Testing** (P3)
   - Add `locust` for load tests
   - Test under sustained load
   - Measure scalability

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Project Status](../docs/project-management/PROJECT_STATUS.md)
- [Honest Assessment](../evaluation/HONEST_ASSESSMENT.md)

---

**Maintained by:** Bob Shell Knowledge Manager Team  
**Questions?** See [AGENTS.md](../AGENTS.md) for contribution guidelines
