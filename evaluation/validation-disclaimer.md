# Validation Disclaimer

⚠️ **CRITICAL: Metrics in this directory require validation**

## Status: Synthetic Simulation - NOT Real-World Validation

The token savings metrics and validation results in this directory are based on **synthetic simulations** and **do not represent real-world performance**.

### What This Means

**Files Affected:**
- `results/validation_report.json` - Synthetic data
- `scripts/run_token_validation.py` - Hardcoded simulation
- All "68.96% savings" claims - Not validated
- All "95% CI" claims - Fabricated precision
- All "52/73/81% scaling" claims - Artifact of design

### Critical Findings from External Audit (2026-07-12)

**Finding #1: Circular Simulation**
- Location: `scripts/run_token_validation.py:38-141`
- Problem: Hardcodes both baseline and "optimized" token counts as magic literals
- Reality: `PromptOptimizer()` instantiated but **never invoked**
- Impact: Headline "68.96% savings" is arithmetic difference between two hand-written functions

**Finding #2: Fabricated Precision**
- Location: `results/validation_report.json`
- Problem: Shows `"std": 0.0` for every scenario (min = max = mean)
- Reality: Treats 90 identical, deterministic duplicates as independent samples
- Impact: "95% CI [66.42, 71.51]" and "p<0.05" are meaningless

**Finding #3: Strawman Baseline**
- Location: `scripts/run_token_validation.py:98`
- Problem: Baseline reads all files while optimized path capped at first 10 files
- Reality: Savings that rise with repo size are **guaranteed by construction**
- Impact: "52/73/81% scaling trend" is an artifact, not a measurement

**Finding #4: Undisclosed Result**
- Problem: Same run recorded `time_savings_pct = -13093.9` (130× slower)
- Reality: "Optimized" path was actually much slower
- Impact: Number never surfaced in any prose

### What Actually Works

**E2E Tests (Real Token Counting):**
- Prompt optimization: 10-20% measured savings ✓
- Cache hits: 100% savings when applicable ✓
- Combined realistic: 40-60% in controlled tests ✓

**Real Example:**
- HCD analysis: 0.36 Bobcoins for structured analysis ✓
- Script-assisted digestion works ✓
- Knowledge base pattern is sound ✓

### Expected Real-World Performance

Based on E2E tests with real token counting:
- **First-time analysis:** 5-15% savings (cold cache)
- **Repetitive tasks:** 20-40% savings (warm cache)
- **Cache hit rate:** 10-20% realistic (not 23.33% theoretical)

### What Needs to Happen

**Phase 6 of Remediation Plan:**
1. Fix `run_token_validation.py` to call real optimizer
2. Test on 10+ diverse real repositories
3. Measure actual token usage vs baseline
4. Document real savings honestly
5. Replace all fabricated metrics

**Timeline:** Week 6-7 of remediation plan

### How to Use This Directory

**DO NOT:**
- ❌ Cite "68.96% savings" as validated
- ❌ Use "95% CI" as evidence
- ❌ Reference "52/73/81% scaling" as real
- ❌ Claim these results are production-validated

**DO:**
- ✓ Acknowledge these are synthetic simulations
- ✓ Use E2E test results (10-20% optimization, 40-60% combined)
- ✓ Reference the 0.36 BC example as a real data point
- ✓ Wait for Phase 6 validation before making claims

### References

- [External Audit Findings](../docs/knowledge-base/research/external-audit-2026-07-12.md)
- [Remediation Action Plan](../docs/knowledge-base/guides/audit-remediation-action-plan.md)
- [Project Status](../docs/project-management/PROJECT_STATUS.md)

---

**Created:** 2026-07-13  
**Purpose:** Prevent misuse of synthetic validation data  
**Status:** Active warning until Phase 6 validation complete
