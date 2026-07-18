# Appendix B: Configuration Reference

## B.1 Cache Configuration

### L1 Cache Settings

**File:** `src/cache/l1_cache.py`

```python
# Maximum number of entries in L1 cache
L1_MAX_SIZE = 10000

# Time-to-live for L1 cache entries (seconds)
L1_TTL = 3600  # 1 hour

# Enable/disable L1 cache
L1_ENABLED = True
```

**Tuning Guidelines:**
- **High hit rate needed:** Increase `L1_MAX_SIZE` to 20000+
- **Low memory:** Decrease `L1_MAX_SIZE` to 5000
- **Stable codebase:** Increase `L1_TTL` to 7200 (2 hours)
- **Rapidly changing code:** Decrease `L1_TTL` to 1800 (30 minutes)

### L2 Cache Settings

**File:** `src/cache/l2_cache.py`

```python
# Maximum number of entries in L2 cache
L2_MAX_SIZE = 5000

# Time-to-live for L2 cache entries (seconds)
L2_TTL = 86400  # 24 hours

# Similarity threshold for semantic matching (0.0-1.0)
L2_SIMILARITY_THRESHOLD = 0.85

# Enable/disable L2 cache
L2_ENABLED = True
```

**Tuning Guidelines:**
- **More semantic matches:** Lower threshold to 0.80
- **Fewer false positives:** Raise threshold to 0.90
- **Long-term caching:** Increase `L2_TTL` to 172800 (48 hours)
- **Frequent updates:** Decrease `L2_TTL` to 43200 (12 hours)

## B.2 Optimizer Configuration

### Prompt Optimization Settings

**File:** `src/optimizer/config.py`

```python
# Minimum optimization threshold (0.0-1.0)
# Only optimize if savings >= this threshold
MIN_OPTIMIZATION_THRESHOLD = 0.10  # 10%

# Preserve quality during optimization
PRESERVE_QUALITY = True

# Maximum prompt length (tokens)
MAX_PROMPT_LENGTH = 1000

# Model for token counting
TOKEN_MODEL = "gpt-4"

# Enable/disable optimization
OPTIMIZATION_ENABLED = True
```

**Tuning Guidelines:**
- **Aggressive optimization:** Lower threshold to 0.05 (5%)
- **Conservative optimization:** Raise threshold to 0.15 (15%)
- **Quality critical:** Keep `PRESERVE_QUALITY = True`
- **Maximum savings:** Set `PRESERVE_QUALITY = False` (not recommended)

## B.3 Truncation Configuration

### Truncation Strategy Settings

**File:** `src/truncation/config.py`

```python
# Default truncation strategy
# Options: "auto", "simple", "priority", "semantic", "sliding"
DEFAULT_STRATEGY = "auto"

# Maximum context length (tokens)
MAX_CONTEXT_LENGTH = 2000

# Preserve ratio (0.0-1.0)
# Aim to preserve this much of original content quality
PRESERVE_RATIO = 0.80  # 80%

# Enable/disable truncation
TRUNCATION_ENABLED = True
```

**Strategy Selection:**
- **"auto":** Let system choose best strategy (recommended)
- **"simple":** Fast, basic truncation (use for speed)
- **"priority":** Keep important sections (use for code)
- **"semantic":** Preserve meaning (use for documentation)
- **"sliding":** Keep context (use for conversations)

**Tuning Guidelines:**
- **Quality critical:** Increase `PRESERVE_RATIO` to 0.90
- **Maximum savings:** Decrease `PRESERVE_RATIO` to 0.70
- **Large files:** Decrease `MAX_CONTEXT_LENGTH` to 1000
- **Small files:** Increase `MAX_CONTEXT_LENGTH` to 3000

## B.4 Monitoring Configuration

### Logging Settings

**File:** `src/monitoring/logger.py`

```python
# Log level
# Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"

# Log format
# Options: "json", "text"
LOG_FORMAT = "json"

# Log file path
LOG_FILE = "logs/bob-km.log"

# Enable console logging
CONSOLE_LOGGING = True

# Enable file logging
FILE_LOGGING = True
```

### Metrics Settings

**File:** `src/monitoring/metrics.py`

```python
# Enable metrics collection
METRICS_ENABLED = True

# Metrics aggregation interval (seconds)
METRICS_INTERVAL = 60

# Metrics export format
# Options: "json", "prometheus"
METRICS_FORMAT = "json"

# Metrics file path
METRICS_FILE = "metrics/bob-km-metrics.json"
```

### Health Check Settings

**File:** `src/monitoring/health.py`

```python
# Health check interval (seconds)
HEALTH_CHECK_INTERVAL = 300  # 5 minutes

# Component timeout (seconds)
COMPONENT_TIMEOUT = 10

# Enable health checks
HEALTH_CHECKS_ENABLED = True
```

## B.5 Bob Shell Integration

### Knowledge Base Settings

**File:** `~/.bob/config/settings.json`

```json
{
  "knowledge_base": {
    "templates_path": "~/Projects/bob-llmwiki-knowledge-manager/config/templates",
    "default_location": "docs/knowledge-base",
    "auto_update_index": true,
    "validate_on_save": true,
    "cross_reference_format": "relative"
  }
}
```

### Template Settings

```json
{
  "templates": {
    "concept": {
      "filename_pattern": "{name}.md",
      "directory": "concepts"
    },
    "guide": {
      "filename_pattern": "{name}-guide.md",
      "directory": "guides"
    },
    "reference": {
      "filename_pattern": "{name}-reference.md",
      "directory": "references"
    },
    "research": {
      "filename_pattern": "{name}-{date}.md",
      "directory": "research"
    }
  }
}
```

## B.6 Environment Variables

### Required Variables

```bash
# Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/bob-llmwiki-knowledge-manager"

# Bob Shell path
export BOB_SHELL_PATH="/path/to/bob-shell"
```

### Optional Variables

```bash
# Cache directory
export BOB_KM_CACHE_DIR="/tmp/bob-km-cache"

# Log directory
export BOB_KM_LOG_DIR="/var/log/bob-km"

# Metrics directory
export BOB_KM_METRICS_DIR="/var/metrics/bob-km"

# Enable debug mode
export BOB_KM_DEBUG=true

# Disable caching (for testing)
export BOB_KM_DISABLE_CACHE=false
```

## B.7 Performance Tuning

### For High Cache Hit Rate

```python
# Increase cache sizes
L1_MAX_SIZE = 20000
L2_MAX_SIZE = 10000

# Increase TTL
L1_TTL = 7200  # 2 hours
L2_TTL = 172800  # 48 hours

# Lower similarity threshold
L2_SIMILARITY_THRESHOLD = 0.80
```

### For Low Memory Usage

```python
# Decrease cache sizes
L1_MAX_SIZE = 5000
L2_MAX_SIZE = 2000

# Decrease TTL
L1_TTL = 1800  # 30 minutes
L2_TTL = 43200  # 12 hours
```

### For Maximum Token Savings

```python
# Aggressive optimization
MIN_OPTIMIZATION_THRESHOLD = 0.05

# Aggressive truncation
PRESERVE_RATIO = 0.70
MAX_CONTEXT_LENGTH = 1000
```

### For Maximum Quality

```python
# Conservative optimization
MIN_OPTIMIZATION_THRESHOLD = 0.15
PRESERVE_QUALITY = True

# Conservative truncation
PRESERVE_RATIO = 0.90
MAX_CONTEXT_LENGTH = 3000
```

## B.8 Production Configuration

### Recommended Production Settings

```python
# Cache
L1_MAX_SIZE = 10000
L1_TTL = 3600
L2_MAX_SIZE = 5000
L2_TTL = 86400
L2_SIMILARITY_THRESHOLD = 0.85

# Optimizer
MIN_OPTIMIZATION_THRESHOLD = 0.10
PRESERVE_QUALITY = True
MAX_PROMPT_LENGTH = 1000

# Truncation
DEFAULT_STRATEGY = "auto"
MAX_CONTEXT_LENGTH = 2000
PRESERVE_RATIO = 0.80

# Monitoring
LOG_LEVEL = "INFO"
METRICS_ENABLED = True
HEALTH_CHECKS_ENABLED = True
```

### High-Availability Configuration

```python
# Shorter TTL for faster updates
L1_TTL = 1800  # 30 minutes
L2_TTL = 43200  # 12 hours

# More aggressive health checks
HEALTH_CHECK_INTERVAL = 60  # 1 minute
COMPONENT_TIMEOUT = 5

# Enhanced monitoring
LOG_LEVEL = "DEBUG"
METRICS_INTERVAL = 30  # 30 seconds
```

---

**See also:**
- Appendix A: API Reference
- Appendix C: Template Reference
