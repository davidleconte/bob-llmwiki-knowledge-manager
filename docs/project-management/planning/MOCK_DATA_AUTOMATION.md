---
title: "Mock Data Automation Guide (Historical)"
date: 2026-07-12
status: historical
category: planning
note: "Automation plan based on mock data. Superseded by Phase 5 manifest-backed harness."
---

# Mock Data Automation Guide

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


⚠️ **WARNING: MOCK DATA IS NOT VALID FOR RESEARCH** ⚠️

This guide documents the complete automation of the adversarial review framework using simulated data for **TESTING PURPOSES ONLY**.

## Overview

The mock data automation generates realistic-looking data to test the analysis pipeline without requiring 8 weeks of manual data collection. This is useful for:

- Testing the analysis scripts
- Verifying the statistical methods
- Demonstrating the complete workflow
- Training on the tools

**CRITICAL**: Mock data invalidates the research. Real human usage data is required for scientifically valid results.

## Quick Start

```bash
# 1. Generate complete mock dataset (60 tasks)
cd ~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/scripts
echo "yes" | bash generate_mock_data_wrapper.sh

# 2. Move files to correct location (if needed)
cp ../data/*.json ~/Projects/bob-llmwiki-knowledge-manager/evaluation/data/

# 3. Run analysis
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 analyze_results.py

# 4. View results
open ../results/comparison.png
cat ../reports/analysis_report.md
```

## Generated Data Characteristics

### Control Condition (Baseline)
- **Tokens**: 400-600 per task
- **Time**: 3-5 minutes per task
- **Quality**: 75-90/100
- **No treatment features**: 0 cross-references, 0 searches, 0 recalls

### Treatment Condition (Knowledge Manager)
- **Tokens**: 40-70% reduction (120-360 per task)
- **Time**: 30% faster (2-3.5 minutes)
- **Quality**: 85-98/100 (higher than control)
- **Treatment features**: 2-8 cross-refs, 1-5 searches, 1-4 recalls

### Scenario Adjustments
- **Document Creation**: +20% tokens, +30% time
- **Retrieval**: -30% tokens, -40% time
- **Maintenance**: -20% tokens, -20% time
- **Synthesis**: +10% tokens, +20% time

## Expected Results

Based on the mock data generation algorithm:

```
Token Savings: ~55% (statistically significant, p < 0.0001)
Quality Improvement: ~10% (85 → 93)
Time Savings: ~30% (4 min → 2.7 min)
Effect Size: Large (Cohen's d > 2.5)
```

## File Locations

### Mock Data Files
```
~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/data/
├── DC_C_001.json ... DC_C_010.json  (Document Creation - Control)
├── DC_T_001.json ... DC_T_010.json  (Document Creation - Treatment)
├── RT_C_001.json ... RT_C_010.json  (Retrieval - Control)
├── RT_T_001.json ... RT_T_010.json  (Retrieval - Treatment)
├── MT_C_001.json ... MT_C_005.json  (Maintenance - Control)
├── MT_T_001.json ... MT_T_005.json  (Maintenance - Treatment)
├── SY_C_001.json ... SY_C_005.json  (Synthesis - Control)
└── SY_T_001.json ... SY_T_005.json  (Synthesis - Treatment)
```

### Analysis Output
```
~/Projects/bob-llmwiki-knowledge-manager/evaluation/
├── results/comparison.png           (Visualization)
└── reports/analysis_report.md       (Statistical report)
```

## Scripts

### 1. generate_mock_data.py
Main mock data generator with realistic metrics.

**Usage:**
```bash
cd ~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/scripts
python3 generate_mock_data.py
```

**Features:**
- Generates 60 tasks (30 control + 30 treatment)
- Realistic token/time/quality distributions
- Scenario-specific adjustments
- Marks all data as mock with metadata

### 2. generate_mock_data_wrapper.sh
Wrapper script that fixes conda stdin issues.

**Usage:**
```bash
echo "yes" | bash generate_mock_data_wrapper.sh
```

### 3. complete_mock_dataset.py
Ensures all 60 tasks exist, filling gaps if needed.

**Usage:**
```bash
python3 complete_mock_dataset.py
```

### 4. week2_progress.py
Shows progress through mock dataset.

**Usage:**
```bash
python3 week2_progress.py
```

## Troubleshooting

### Issue: Files not in correct location
**Symptom**: Analysis shows "Loaded 1 tasks" instead of 60

**Solution:**
```bash
# Copy from generation location to analysis location
cp ~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/data/*.json \
   ~/Projects/bob-llmwiki-knowledge-manager/evaluation/data/
```

### Issue: EOFError with conda run
**Symptom**: `EOFError: EOF when reading a line`

**Solution**: Use wrapper script instead of direct conda run:
```bash
bash generate_mock_data_wrapper.sh
```

### Issue: Analysis shows NaN or no significance
**Symptom**: P-value is NaN, no statistical significance

**Solution**: Ensure all 60 tasks are present:
```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/data
ls -1 *.json | wc -l  # Should show 61 (60 tasks + test_001.json)
```

## Validation Checklist

Before running analysis, verify:

- [ ] 60 task JSON files exist (30 control + 30 treatment)
- [ ] Files are in `~/Projects/bob-llmwiki-knowledge-manager/evaluation/data/`
- [ ] Each file has `"mock_data": true` in metadata
- [ ] Conda environment `hcd-at-its-core` is activated
- [ ] Analysis scripts are in `evaluation/scripts/`

## Real Data Collection

To replace mock data with real data:

1. **Delete all mock files:**
   ```bash
   cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/data
   rm DC_*.json RT_*.json MT_*.json SY_*.json
   ```

2. **Follow Week 2 manual process:**
   ```bash
   cd ~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/scripts
   bash start_week2.sh
   ```

3. **Record each task manually:**
   ```bash
   bash record_task_wrapper.sh
   ```

4. **Track progress:**
   ```bash
   python3 week2_progress.py
   ```

## Limitations

Mock data **CANNOT** replace real data because:

1. **No learning curve**: Real users improve over time
2. **No variability**: Real tasks have unpredictable complexity
3. **No context**: Real usage reveals edge cases
4. **No validation**: Cannot verify actual productivity gains
5. **No scientific validity**: Simulated data invalidates research

## Use Cases

Mock data is appropriate for:

- ✅ Testing analysis pipeline
- ✅ Verifying statistical methods
- ✅ Training on tools
- ✅ Demonstrating workflow
- ✅ Debugging scripts

Mock data is **NOT** appropriate for:

- ❌ Research publication
- ❌ Decision making
- ❌ Validating hypotheses
- ❌ Measuring real productivity
- ❌ Adversarial review conclusions

## Summary

The mock data automation provides a complete end-to-end test of the adversarial review framework. It demonstrates:

- Data generation (60 tasks)
- Progress tracking
- Statistical analysis
- Visualization
- Report generation

However, it **MUST** be replaced with real human usage data for valid research results.

---

**Next Steps:**

1. Test the complete pipeline with mock data
2. Verify all tools work correctly
3. Replace with real data collection (8 weeks)
4. Run final analysis on real data
5. Draw conclusions from actual measurements
