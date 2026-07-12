# Adversarial Review Framework

Comprehensive evaluation framework for the Bob Shell Knowledge Manager, designed to validate token efficiency, quality maintenance, and robustness against industry best practices.

## Overview

This framework implements an 8-week adversarial review process based on:
- **Karpathy's LLM Optimization Principles**: Token efficiency, context optimization
- **IBM Bob Best Practices**: Native tool usage, context management
- **LLM-Wiki Reference**: Knowledge management patterns
- **McKinsey MECE Principles**: Mutually Exclusive, Collectively Exhaustive analysis

## Directory Structure

```
evaluation/
├── README.md                    # This file
├── EXECUTION_GUIDE.md          # Step-by-step execution instructions
├── feature_comparison.csv      # Feature matrix (auto-generated)
├── redteam_test_plan.md       # Red team test scenarios (auto-generated)
├── scripts/                    # Analysis and collection scripts
│   ├── collect_metrics.py     # Metrics collection
│   ├── analyze_results.py     # Statistical analysis
│   ├── feature_audit.py       # Feature comparison audit
│   └── redteam_scenarios.py   # Adversarial test generation
├── data/                       # Collected metrics (JSON)
│   ├── test_001.json          # Example task data
│   └── redteam/               # Red team scenario data
├── results/                    # Analysis outputs
│   └── comparison.png         # Visualization (auto-generated)
├── reports/                    # Generated reports
│   ├── analysis_report.md     # Statistical analysis
│   └── feature_audit.md       # Feature audit results
└── review_packages/           # Complete review packages
    └── review_YYYYMMDD/       # Dated review package
```

## Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy scipy matplotlib seaborn
```

### 2. Verify Setup

```bash
cd scripts
python3 collect_metrics.py
python3 analyze_results.py
python3 feature_audit.py
python3 redteam_scenarios.py
```

### 3. Start Evaluation

Follow the detailed instructions in `EXECUTION_GUIDE.md`.

## Key Components

### Metrics Collection (`collect_metrics.py`)

Collects and stores task metrics:
- Token usage
- Bobcoin costs
- Time taken
- Quality scores (completeness, accuracy, consistency, usability)
- Cross-references, searches, memory recalls

**Usage:**
```python
from scripts.collect_metrics import MetricsCollector, create_task_template

collector = MetricsCollector()
task = create_task_template('TASK_001', 'document_creation', 'control')
task['metrics']['tokens_used'] = 450
task['metrics']['bobcoin_cost'] = 0.045
collector.record_task(task)
```

### Statistical Analysis (`analyze_results.py`)

Performs comprehensive statistical analysis:
- Token savings calculation
- Paired/independent t-tests
- Effect size (Cohen's d)
- Quality analysis
- Cost-benefit analysis
- Visualization generation

**Usage:**
```bash
python3 analyze_results.py
# Generates: ../results/comparison.png, ../reports/analysis_report.md
```

### Feature Audit (`feature_audit.py`)

Compares implementation against references:
- LLM-Wiki features
- Karpathy principles
- Bob best practices
- Gap analysis

**Usage:**
```bash
python3 feature_audit.py
# Generates: ../reports/feature_audit.md, ../feature_comparison.csv
```

### Red Team Scenarios (`redteam_scenarios.py`)

Generates adversarial test scenarios:
- Token bloat attacks
- Quality degradation tests
- Context overflow scenarios
- Cross-reference chaos
- Memory pollution tests

**Usage:**
```bash
python3 redteam_scenarios.py
# Generates: ../redteam_test_plan.md, ../data/redteam/*.json
```

## Evaluation Phases

### Phase 1: Setup (Week 1)
- Install dependencies
- Verify scripts
- Review test plans

### Phase 2: Baseline (Week 2)
- Execute 30 control tasks
- Record metrics without KB

### Phase 3: Treatment (Weeks 3-4)
- Execute 30 treatment tasks
- Record metrics with KB

### Phase 4: Red Team (Week 5)
- Execute adversarial scenarios
- Document vulnerabilities

### Phase 5: Analysis (Week 6)
- Generate statistical reports
- Validate hypotheses

### Phase 6: Documentation (Week 7)
- Create review packages
- Write executive summary

### Phase 7: Iteration (Week 8)
- Address findings
- Re-test improvements

## Success Criteria

- ✅ Token savings ≥30% (H1 hypothesis)
- ✅ Quality maintained or improved
- ✅ Statistical significance (p < 0.05)
- ✅ 80%+ red team tests pass
- ✅ Feature completion ≥80%

## Hypotheses

**H1 (Primary)**: Knowledge Manager reduces token usage by ≥30%
- Null: No significant difference
- Alternative: ≥30% reduction
- Significance: p < 0.05

**H2 (Quality)**: Quality maintained or improved
- Null: Quality degrades
- Alternative: Quality ≥ baseline

**H3 (ROI)**: Positive return on investment
- Break-even: <100 tasks
- Target: 300-600% ROI

## Data Format

### Task Data Structure

```json
{
  "task_id": "DC_C_001",
  "scenario": "document_creation",
  "condition": "control",
  "participant": "user1",
  "timestamp": "2026-07-12T08:00:00Z",
  "metrics": {
    "tokens_used": 450,
    "bobcoin_cost": 0.045,
    "time_seconds": 120,
    "quality_score": {
      "completeness": 22,
      "accuracy": 23,
      "consistency": 20,
      "usability": 20,
      "total": 85
    },
    "cross_references": 3,
    "search_queries": 2,
    "memory_recalls": 1
  },
  "artifacts": {
    "input": "Task description",
    "output": "Result",
    "transcript": "Full interaction log"
  }
}
```

## Troubleshooting

### Not Enough Data
Need ≥10 tasks per condition per scenario for valid analysis.

### Non-Significant Results
- Increase sample size
- Ensure proper pairing
- Check for outliers

### Script Errors
- Verify Python 3.11+
- Check all dependencies installed
- Review error messages in output

## References

- **Research Design**: `docs/knowledge-base/research/adversarial-review-design-2026-07.md`
- **Implementation Guide**: `docs/knowledge-base/guides/adversarial-review-implementation-guide.md`
- **Execution Guide**: `EXECUTION_GUIDE.md`

## Support

For questions or issues:
1. Review documentation in `docs/knowledge-base/`
2. Check `EXECUTION_GUIDE.md` for detailed instructions
3. Open an issue in the project repository

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-12  
**Status**: Production Ready
