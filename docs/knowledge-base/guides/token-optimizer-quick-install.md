---
title: "Token Optimizer Quick Install Guide"
category: guide
date: 2026-07-14
type: guide
status: complete
tags: [installation, token-optimizer, quick-start, setup]
related:
  - setup-token-optimization.md
  - ../concepts/token-optimization.md
  - ../references/cache-api.md
created: 2026-07-14
updated: 2026-07-14

---

# Token Optimizer Quick Install Guide
## Get Started in 5 Minutes

**Purpose:** Fast installation and verification of the Token Optimization System  
**Time Required:** 5 minutes  
**Prerequisites:** Python 3.8+, pip

---

## Quick Install (3 Steps)

### 1. Clone & Navigate

```bash
git clone https://github.com/davidleconte/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with all extras
pip install -e ".[dev,monitoring]"
```

**Installation time:** ~2-3 minutes

### 3. Verify Installation

```bash
# Run tests to verify
python3 -m pytest tests/ -v

# Expected: 213 tests passed
```

---

## Quick Usage Example

```python
from src.facade import TokenOptimizer

# Initialize (one-liner)
optimizer = TokenOptimizer()

# Optimize a prompt
result = optimizer.optimize_prompt("Your prompt text here")

print(f"Original: {result['original_tokens']} tokens")
print(f"Optimized: {result['optimized_tokens']} tokens")
print(f"Savings: {result['savings_percent']:.1f}%")
```

---

## CLI Usage

```bash
# Optimize a prompt via CLI
bob-optimize "Your prompt text here"

# Or using Python module
python -m src "Your prompt text here"
```

---

## What You Get

**Measured Savings:**
- **6.8% compression** (95% CI [6.2%, 7.4%], N=265 in-repo docs; provenance: `evaluation/results/validation-2026-07-25/manifest.json`)
- **Near-lossless** (whitespace + redundant phrase removal)
- **Manifest-backed** reproducibility

**Components:**
- ✅ L1 Cache (exact match, <1ms)
- ✅ L2 Cache (semantic similarity, <100ms)
- ✅ Optimizer (compression, <50ms)
- ✅ Truncation (lossy budget-fitting)
- ✅ Monitoring (metrics, logging, health checks)

---

## Troubleshooting

### Tests Fail?

```bash
# Reinstall dependencies
pip uninstall -y numpy scikit-learn tiktoken
pip install -e ".[dev,monitoring]"

# Clear cache
find . -type d -name "__pycache__" -exec rm -r {} +

# Try again
python3 -m pytest tests/ -v
```

### ImportError for tiktoken?

```bash
# Install separately
pip install tiktoken

# System gracefully degrades to fallback if unavailable
```

### Slow Performance?

```python
# Reduce cache sizes in your config
from src.config import Config

config = Config()
config.cache.l1_max_size = 500  # Default: 1000
config.cache.l2_max_size = 250  # Default: 500
```

---

## Next Steps

**For Detailed Setup:**
- See [Complete Setup Guide](./setup-token-optimization.md) for 7-step walkthrough

**For Understanding:**
- [Token Optimization Concept](../concepts/token-optimization.md)
- [Multi-Level Caching](../concepts/multi-level-caching.md)

**For API Reference:**
- [Cache API Reference](../references/cache-api.md)
- [Architecture Documentation](../../architecture/ARCHITECTURE.md)

**For Integration:**
- [Optimize a Prompt Tutorial](../../tutorials/optimize-a-prompt.md)
- [Bob Shell Integration](./bob-shell-ui-integration.md)

---

## System Requirements

**Minimum:**
- Python 3.8+
- 50MB disk space
- 100MB RAM

**Recommended:**
- Python 3.11+
- 200MB disk space
- 500MB RAM
- Unix-like OS (macOS, Linux)

**Note:** Windows support is experimental (bash scripts not cross-platform).

---

## Important Caveats

⚠️ **Not Production Ready** — See [STATUS.md](../../../STATUS.md) for the current, authoritative grade.

**Status:** **Beta, not production-ready.** No grade is claimed here — the previously stated "A (3.89 / 4.30)" is a superseded value that appears nowhere in the current status.
See [`STATUS.md`](../../../STATUS.md) for full dimension breakdown and roadmap.

**Critical Blockers (for production deployment):**
1. ❌ No external security audit
2. ❌ No penetration testing
3. ❌ No load testing
4. ❌ No disaster recovery plan
5. ❌ No operational runbooks

**Suitable For:**
- ✅ Development and testing
- ✅ Research and experimentation
- ✅ Proof-of-concept deployments

**NOT Suitable For:**
- ❌ Production institutional deployment
- ❌ Mission-critical systems

---

## Support

**Documentation:**
- [Complete Documentation Index](../../INDEX.md)
- [Knowledge Base](../index.md)

**Issues:**
- GitHub Issues (if public repo)
- See [SUPPORT.md](../../../SUPPORT.md)

**Security:**
- Private vulnerability reporting via [SECURITY.md](../../../SECURITY.md)

---

**Last Updated:** 2026-07-14  
**Category:** Guide  
**Difficulty:** Beginner  
**Time to Complete:** 5 minutes
