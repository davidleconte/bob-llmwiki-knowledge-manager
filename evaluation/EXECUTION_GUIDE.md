# Adversarial Review Execution Guide

## Quick Start

This guide walks you through executing the 8-week adversarial review of the Bob Shell Knowledge Manager.

## Prerequisites

- Bob Shell Knowledge Manager installed (`~/.bob/custom_modes.yaml`)
- Python 3.11+ with dependencies: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`
- Access to Bob Shell for task execution

## Phase 1: Setup (Week 1)

### 1.1 Install Dependencies

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation
pip install pandas numpy scipy matplotlib seaborn
```

### 1.2 Verify Scripts

```bash
cd scripts
python3 collect_metrics.py  # Should create test_001.json
python3 analyze_results.py  # Should generate report (with test data)
python3 feature_audit.py    # Should generate feature audit
python3 redteam_scenarios.py # Should generate test plan
```

### 1.3 Review Test Plan

```bash
cat redteam_test_plan.md
cat ../reports/feature_audit.md
```

## Phase 2: Baseline Collection (Week 2)

### 2.1 Control Condition Tasks

Execute 30 tasks WITHOUT using knowledge-manager mode:

**Document Creation (10 tasks)**
```bash
# For each task, record metrics manually
python3 -c "
from scripts.collect_metrics import MetricsCollector, create_task_template
collector = MetricsCollector()
task = create_task_template('DC_C_001', 'document_creation', 'control')
# Fill in metrics after task completion
task['metrics']['tokens_used'] = YOUR_TOKEN_COUNT
task['metrics']['bobcoin_cost'] = YOUR_COST
task['metrics']['time_seconds'] = YOUR_TIME
task['metrics']['quality_score']['total'] = YOUR_QUALITY_SCORE
collector.record_task(task)
"
```

**Retrieval (10 tasks)**
- Search for information across multiple documents
- Record: tokens, time, quality of results

**Maintenance (5 tasks)**
- Update existing documentation
- Record: tokens, time, consistency maintained

**Synthesis (5 tasks)**
- Combine information from multiple sources
- Record: tokens, time, completeness

### 2.2 Quality Scoring

For each task, score 0-100 on:
- **Completeness** (25 points): All required information included
- **Accuracy** (25 points): Information is correct and up-to-date
- **Consistency** (25 points): Follows established patterns
- **Usability** (25 points): Easy to find and understand

## Phase 3: Treatment Collection (Weeks 3-4)

### 3.1 Treatment Condition Tasks

Execute same 30 tasks WITH knowledge-manager mode:

```bash
# Switch to knowledge-manager mode in Bob Shell
bob --mode knowledge-manager

# For each task, record metrics
python3 -c "
from scripts.collect_metrics import MetricsCollector, create_task_template
collector = MetricsCollector()
task = create_task_template('DC_T_001', 'document_creation', 'treatment')
# Fill in metrics after task completion
task['metrics']['tokens_used'] = YOUR_TOKEN_COUNT
task['metrics']['bobcoin_cost'] = YOUR_COST
task['metrics']['time_seconds'] = YOUR_TIME
task['metrics']['quality_score']['total'] = YOUR_QUALITY_SCORE
task['metrics']['cross_references'] = COUNT_OF_REFS_USED
task['metrics']['search_queries'] = COUNT_OF_SEARCHES
task['metrics']['memory_recalls'] = COUNT_OF_MEMORY_USES
collector.record_task(task)
"
```

## Phase 4: Red Team Testing (Week 5)

### 4.1 Execute Adversarial Scenarios

```bash
# Review test plan
cat redteam_test_plan.md

# For each scenario, document results
# Example: Token Bloat Attack
# 1. Try to create verbose documentation
# 2. Observe if KB prevents or warns
# 3. Record: Pass/Partial/Fail
```

### 4.2 Document Findings

Create `redteam_results.md`:
```markdown
# Red Team Results

## TB-001: Excessive Context
- Status: [Pass/Partial/Fail]
- Observation: [What happened]
- Evidence: [Screenshots, logs, etc.]
- Recommendation: [If applicable]
```

## Phase 5: Analysis (Week 6)

### 5.1 Generate Statistical Analysis

```bash
cd scripts
python3 analyze_results.py
```

This generates:
- `../results/comparison.png` - Visualizations
- `../reports/analysis_report.md` - Statistical report

### 5.2 Review Results

```bash
cat ../reports/analysis_report.md
open ../results/comparison.png  # macOS
# or
xdg-open ../results/comparison.png  # Linux
```

### 5.3 Check Success Criteria

- [ ] Token savings ≥30% (H1 hypothesis)
- [ ] Quality maintained or improved
- [ ] p-value < 0.05 (statistical significance)
- [ ] 80%+ red team tests pass
- [ ] Feature completion ≥80%

## Phase 6: Documentation (Week 7)

### 6.1 Generate Review Package

```bash
cd scripts
python3 << 'PYTHON'
from pathlib import Path
import shutil
from datetime import datetime

# Create review package
package_dir = Path("../review_packages") / f"review_{datetime.now().strftime('%Y%m%d')}"
package_dir.mkdir(parents=True, exist_ok=True)

# Copy all reports
shutil.copytree("../reports", package_dir / "reports")
shutil.copytree("../results", package_dir / "results")
shutil.copytree("../data", package_dir / "data")

# Copy test plans
shutil.copy("../redteam_test_plan.md", package_dir)
shutil.copy("../feature_comparison.csv", package_dir)

print(f"✅ Review package created: {package_dir}")
PYTHON
```

### 6.2 Write Executive Summary

Create `review_packages/review_YYYYMMDD/EXECUTIVE_SUMMARY.md`:

```markdown
# Adversarial Review Executive Summary

## Key Findings
- Token Savings: X%
- Quality Impact: +Y%
- Statistical Significance: p=Z
- Red Team Pass Rate: W%

## Recommendations
1. [Primary recommendation]
2. [Secondary recommendation]
3. [Tertiary recommendation]

## Conclusion
[Overall assessment]
```

## Phase 7: Iteration (Week 8)

### 7.1 Address Findings

Based on analysis results:
1. Fix any red team failures
2. Improve features with "Partial" status
3. Document token optimization strategies
4. Update templates based on learnings

### 7.2 Re-test Critical Items

```bash
# Re-run failed red team tests
# Re-measure token usage for improved features
# Update analysis with new data
```

## Metrics Reference

### Token Counting

Bob Shell displays token usage after each interaction:
```
task costs: 0.45  # This is your bobcoin cost
```

To get token count, multiply by 1000:
- 0.45 bobcoins ≈ 450 tokens

### Time Tracking

Use a stopwatch or:
```bash
time bob --mode knowledge-manager
# Record the "real" time in seconds
```

### Quality Scoring Template

```
Completeness (0-25): ___
- All sections present: 10
- All details included: 10
- No gaps: 5

Accuracy (0-25): ___
- Factually correct: 15
- Up-to-date: 10

Consistency (0-25): ___
- Follows templates: 10
- Matches style: 10
- Proper cross-refs: 5

Usability (0-25): ___
- Easy to find: 10
- Clear structure: 10
- Good examples: 5

TOTAL: ___ / 100
```

## Troubleshooting

### Issue: Not enough data for analysis

**Solution**: Need at least 10 tasks per condition (control/treatment) per scenario.

### Issue: Statistical test shows "not significant"

**Solution**: 
1. Increase sample size (more tasks)
2. Ensure proper pairing (same person, same task type)
3. Check for outliers in data

### Issue: Red team tests unclear

**Solution**: Refer to `redteam_test_plan.md` for detailed expected behaviors.

## Support

For questions or issues:
1. Review `docs/knowledge-base/guides/adversarial-review-implementation-guide.md`
2. Check `docs/knowledge-base/research/adversarial-review-design-2026-07.md`
3. Open an issue in the project repository

---
*Last Updated: 2026-07-12*
