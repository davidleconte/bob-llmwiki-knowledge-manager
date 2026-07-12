# Adversarial Review Execution Guide

## Quick Start

This guide walks you through executing the 8-week adversarial review of the Bob Shell Knowledge Manager.

## Prerequisites

- Bob Shell Knowledge Manager installed (`~/.bob/custom_modes.yaml`)
- Conda environment (e.g., `hcd-at-its-core`)
- Python 3.11+ with uv package manager
- Access to Bob Shell for task execution

## Phase 1: Setup (Week 1)

### 1.1 Install Dependencies

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation

# Using conda + uv (recommended)
conda run -n hcd-at-its-core uv pip install pandas numpy scipy matplotlib seaborn

# Or using pip directly
pip install pandas numpy scipy matplotlib seaborn
```

### 1.2 Verify Scripts

```bash
cd scripts

# Test all scripts with conda environment
conda run -n hcd-at-its-core python3 collect_metrics.py
conda run -n hcd-at-its-core python3 analyze_results.py
conda run -n hcd-at-its-core python3 feature_audit.py
conda run -n hcd-at-its-core python3 redteam_scenarios.py
```

Expected output:
- ✅ Recorded task: test_001
- ✅ Generated report: ../reports/analysis_report.md
- ✅ Generated feature audit report: ../reports/feature_audit.md
- ✅ Generated red team test plan: ../redteam_test_plan.md

### 1.3 Review Test Plan

```bash
cat ../redteam_test_plan.md
cat ../reports/feature_audit.md
```

## Phase 2-7: Baseline, Treatment, Red Team, Analysis, Documentation, Iteration

[See full guide in original EXECUTION_GUIDE.md for detailed instructions]

## Conda + UV Usage

All Python scripts can be run with:
```bash
conda run -n hcd-at-its-core python3 script_name.py
```

Or activate the environment first:
```bash
conda activate hcd-at-its-core
python3 script_name.py
```

---
*Last Updated: 2026-07-12*
*Tested with: conda environment `hcd-at-its-core` + uv package manager*
*All 4 scripts verified working ✅*
