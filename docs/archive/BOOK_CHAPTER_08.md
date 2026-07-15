# Chapter 8: Getting Started Guide

> ⚠️ **Metrics correction (2026-07-14).** Earlier drafts of this document cited fabricated token-savings/quality figures — "68.96%", "89.3%", "91.80%" — produced by a simulation that never invoked the optimizer. **Those figures are retracted.** The honest, measured figure is **~20% mean optimizer compression** on real prose (manifest-backed: `evaluation/results/validation-2026-07-14/`; see `STATUS.md` and `CHANGELOG.md`). Inline numbers below have been corrected where they appeared.


## 8.1 System Requirements

### Minimum Requirements

**For Token Optimization System:**
- Python 3.11 or higher
- 2GB RAM
- 100MB disk space
- Internet connection (for pip install)

**For Knowledge Base Framework:**
- Bash shell (Linux, macOS, WSL on Windows)
- Git (for version control)
- Text editor or IDE
- Bob Shell 1.0.6+

**Optional:**
- psutil (for system monitoring)
- pandoc (for export to HTML/PDF)

### Supported Platforms

✅ **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+)
✅ **macOS** (11.0 Big Sur or later)
✅ **Windows** (via WSL2)

## 8.2 Installation Steps

### Step 1: Clone the Repository

```bash
cd ~/Projects
git clone https://github.com/davidleconte/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**Required packages:**
- tiktoken (token counting)
- scikit-learn (TF-IDF, cosine similarity)
- numpy (numerical operations)
- pytest (testing)

**Optional packages:**
```bash
pip install psutil  # For system monitoring
```

### Step 3: Verify Installation

```bash
# Run tests to verify everything works
python3 -m pytest tests/ -v

# Expected output:
# ====== 310 passed in 4.23s ======
```

### Step 4: Install Knowledge Base Framework

```bash
# Run installation script
./scripts/install.sh

# This will:
# 1. Verify Bob Shell is installed
# 2. Copy templates to Bob Shell config
# 3. Set up automation scripts
# 4. Create example knowledge bases
```

### Step 5: Initialize Your First Knowledge Base

```bash
# Navigate to your project
cd ~/Projects/your-project

# Initialize knowledge base structure
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh

# This creates:
# docs/knowledge-base/
# ├── INDEX.md
# ├── concepts/
# ├── guides/
# ├── references/
# └── research/
```

## 8.3 Quick Start (5 Minutes)

### Task 1: Create Your First Concept Document (2 minutes)

**Using Bob Shell:**
```bash
# Start Bob Shell in plan mode
bob --mode=plan

# Ask Bob to create a concept document
"Create a concept document about multi-level caching 
using the concept template in docs/knowledge-base/concepts/"
```

**Bob will:**
1. Read the concept template
2. Fill in the structure
3. Create `concepts/multi-level-caching.md`
4. Update `INDEX.md`

**Manual alternative:**
```bash
# Copy template
cp config/templates/concept.md docs/knowledge-base/concepts/my-concept.md

# Edit the file
vim docs/knowledge-base/concepts/my-concept.md

# Update INDEX.md
echo "- [My Concept](concepts/my-concept.md)" >> docs/knowledge-base/INDEX.md
```

### Task 2: Test Token Optimization (2 minutes)

**Create test script:**
```python
# test_optimization.py
from src.cache import MultiLevelCache
from src.optimizer import PromptOptimizer

# Initialize components
cache = MultiLevelCache()
optimizer = PromptOptimizer()

# Test query
query = "Could you please explain to me how the authentication system works?"
print(f"Original: {query} ({optimizer.count_tokens(query)} tokens)")

# Optimize
optimized = optimizer.optimize(query)
print(f"Optimized: {optimized} ({optimizer.count_tokens(optimized)} tokens)")

# Calculate savings
savings = (1 - optimizer.count_tokens(optimized) / optimizer.count_tokens(query)) * 100
print(f"Savings: {savings:.1f}%")
```

**Run it:**
```bash
python3 test_optimization.py

# Expected output:
# Original: Could you please explain... (15 tokens)
# Optimized: Explain authentication system (4 tokens)
# Savings: 73.3%
```

### Task 3: Run Repository Analysis (1 minute)

```bash
# Analyze your project
./scripts/scan-repository.sh

# View results
cat reports/repository-scan.txt

# Generate full report
./scripts/generate-analysis-report.sh
```

## 8.4 Configuration

### Cache Configuration

**File:** `src/cache/config.py`

```python
# L1 Cache settings
L1_MAX_SIZE = 10000  # Maximum entries
L1_TTL = 3600        # Time-to-live (seconds)

# L2 Cache settings
L2_MAX_SIZE = 5000   # Maximum entries
L2_TTL = 86400       # Time-to-live (seconds)
L2_SIMILARITY_THRESHOLD = 0.85  # Minimum similarity for match
```

**Tuning recommendations:**
- **High cache hit rate:** Increase TTL, increase max size
- **Low memory:** Decrease max size
- **More semantic matches:** Lower similarity threshold (0.80)
- **Fewer false positives:** Raise similarity threshold (0.90)

### Optimizer Configuration

**File:** `src/optimizer/config.py`

```python
# Optimization settings
MIN_OPTIMIZATION_THRESHOLD = 0.10  # Minimum 10% savings to apply
PRESERVE_QUALITY = True            # Maintain intent and context
MAX_PROMPT_LENGTH = 1000           # Maximum tokens in prompt
```

### Truncation Configuration

**File:** `src/truncation/config.py`

```python
# Truncation settings
DEFAULT_STRATEGY = "auto"          # Auto-select best strategy
MAX_CONTEXT_LENGTH = 2000          # Maximum context tokens
PRESERVE_RATIO = 0.80              # Preserve 80% of content quality
```

### Bob Shell Settings

**File:** `~/.bob/config/settings.json`

```json
{
  "knowledge_base": {
    "templates_path": "~/Projects/bob-llmwiki-knowledge-manager/config/templates",
    "default_location": "docs/knowledge-base",
    "auto_update_index": true,
    "validate_on_save": true
  }
}
```

## 8.5 First Real Task

### Scenario: Analyze and Document Your Project

**Goal:** Create a complete knowledge base for your project

**Steps:**

**1. Analyze project structure (5 minutes)**
```bash
cd ~/Projects/your-project
~/Projects/bob-llmwiki-knowledge-manager/scripts/scan-repository.sh
~/Projects/bob-llmwiki-knowledge-manager/scripts/analyze-dependencies.sh
~/Projects/bob-llmwiki-knowledge-manager/scripts/generate-analysis-report.sh
```

**2. Review analysis results (5 minutes)**
```bash
cat reports/repository-scan.txt
cat reports/dependency-analysis.txt
cat reports/full-analysis-report.txt
```

**3. Create concept documents (15 minutes)**

Using Bob Shell:
```bash
bob --mode=plan

"Based on the repository analysis, create concept documents for:
1. Project architecture
2. Core components
3. Key design patterns"
```

**4. Create guide documents (20 minutes)**

```bash
bob --mode=plan

"Create guide documents for:
1. Getting started
2. Development workflow
3. Testing procedures"
```

**5. Create reference documents (15 minutes)**

```bash
bob --mode=plan

"Create reference documents for:
1. API documentation
2. Configuration options
3. CLI commands"
```

**6. Validate knowledge base (2 minutes)**
```bash
~/Projects/bob-llmwiki-knowledge-manager/scripts/validate-kb.sh
```

**Total time: ~60 minutes for complete knowledge base**

## 8.6 Common First-Time Issues

### Issue 1: Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'tiktoken'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue 2: Bob Shell Not Found

**Problem:**
```
bash: bob: command not found
```

**Solution:**
```bash
# Install Bob Shell
# Follow instructions at: https://bob-shell.dev/install

# Verify installation
bob --version
```

### Issue 3: Permission Denied

**Problem:**
```
bash: ./scripts/install.sh: Permission denied
```

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run again
./scripts/install.sh
```

### Issue 4: Tests Failing

**Problem:**
```
====== 5 failed, 305 passed ======
```

**Solution:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run tests with verbose output
python3 -m pytest tests/ -v --tb=short
```

### Issue 5: Cache Not Working

**Problem:**
Cache hit rate is 0%

**Solution:**
```python
# Check cache initialization
from src.cache import MultiLevelCache

cache = MultiLevelCache()
print(cache.get_stats())  # Should show cache info

# Verify cache is being used
cache.set("test", "value")
result = cache.get("test")
print(result)  # Should print "value"
```

## 8.7 Next Steps

### Learn More

**Read these chapters next:**
- Chapter 9: Honest Assessment (understand limitations)
- Chapter 21: Advanced Caching Strategies
- Chapter 23: Monitoring and Observability

### Explore Examples

```bash
cd examples/

# Personal wiki example
cd personal-wiki/
cat README.md

# Research project example
cd ../research-project/
cat README.md

# Software project example
cd ../software-project/
cat README.md
```

### Join the Community

- GitHub: https://github.com/davidleconte/bob-llmwiki-knowledge-manager
- Documentation: https://docs.bob-llmwiki-km.dev
- Issues: https://github.com/davidleconte/bob-llmwiki-knowledge-manager/issues

### Contribute

```bash
# Fork the repository
# Create a feature branch
git checkout -b feature/my-improvement

# Make changes
# Run tests
python3 -m pytest tests/ -v

# Submit pull request
```

---

**Next Chapter:** Honest Assessment and Production Readiness
