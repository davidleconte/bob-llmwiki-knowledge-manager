---
title: Real-Time Session Monitoring Guide
type: guide
category: validation
tags: [monitoring, sessions, real-time, quality]
created: 2026-07-13
updated: 2026-07-13
status: active
---

# Real-Time Session Monitoring Guide

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Overview

This guide explains how to use the real-time monitoring tools to track session collection progress, validate quality, and ensure successful data collection for Phase 3 validation.

## Tools Available

### 1. Live Session Monitor (`live_session_monitor.py`)

Real-time dashboard that shows:
- Progress toward 20 session target
- Token savings estimates
- Cache hit rates
- Session quality indicators
- Time remaining estimates

### 2. Session Quality Validator (`validate_session_quality.sh`)

Automated quality checker that validates:
- Minimum query count (5+ queries)
- Token count ranges (1,000 - 1,000,000)
- Query diversity (30%+ unique)
- Timestamp validity
- Outlier detection

## Quick Start

### Starting Real-Time Monitoring

**For Baseline Sessions:**
```bash
# Start monitoring baseline sessions
python3 examples/live_session_monitor.py --baseline

# The dashboard will update every 5 seconds
# Press Ctrl+C to stop
```

**For Optimized Sessions:**
```bash
# Start monitoring optimized sessions
python3 examples/live_session_monitor.py --optimized
```

### Running Quality Validation

**Basic Validation:**
```bash
# Validate baseline sessions
./scripts/validate_session_quality.sh --baseline

# Validate optimized sessions
./scripts/validate_session_quality.sh --optimized
```

**Verbose Mode:**
```bash
# Show detailed validation output
./scripts/validate_session_quality.sh --baseline --verbose
```

## Live Session Monitor Features

### Dashboard Layout

```
================================================================================
  📊 REAL-TIME SESSION MONITOR - BASELINE
================================================================================

📈 PROGRESS
--------------------------------------------------------------------------------
  [████████████████████░░░░░░░░░░░░░░░░░░░░] 50.0%
  Sessions: 10/20 completed
  Remaining: 10 sessions
  Estimated time remaining: 1:30:00

✅ QUALITY INDICATORS
--------------------------------------------------------------------------------
  Overall Quality: 🟢 Excellent (95.0%)
  Total Queries: 127
  Avg Queries/Session: 12.7
  Quality Sessions: 10/10

🎯 TOKEN STATISTICS
--------------------------------------------------------------------------------
  Total Tokens: 45,230
  Avg Tokens/Query: 356.1

📝 RECENT SESSIONS (Last 5)
--------------------------------------------------------------------------------
  1. ✅ 15 queries, 5,234 tokens - 10:05:23
  2. ✅ 12 queries, 4,567 tokens - 10:02:15
  3. ✅ 10 queries, 3,890 tokens - 09:58:42
  4. ✅ 13 queries, 4,123 tokens - 09:55:10
  5. ✅ 11 queries, 4,234 tokens - 09:51:33

--------------------------------------------------------------------------------
  Monitoring for: 15m 30s
  Last update: 10:07:45
  Refresh interval: 5s
  Press Ctrl+C to stop
================================================================================
```

### Quality Indicators

| Emoji | Score | Description |
|-------|-------|-------------|
| 🟢 | 90-100% | Excellent - All sessions meet quality standards |
| 🟡 | 70-89% | Good - Most sessions are high quality |
| 🟠 | 50-69% | Fair - Some sessions need improvement |
| 🔴 | 0-49% | Poor - Many sessions have quality issues |

### Warnings

The monitor will display warnings for:
- **Low quality score** (<70%) - Sessions need more queries
- **Low average queries** (<5 per session) - Sessions too short
- **Low cache hit rate** (<50%, optimized only) - Optimization not effective

## Session Quality Validator Features

### Validation Checks

1. **JSON Structure**
   - Validates required fields exist
   - Checks data types
   - Ensures parseable format

2. **Query Count**
   - Minimum: 5 queries per session
   - Flags sessions with fewer queries
   - Recommends longer sessions

3. **Token Count**
   - Minimum: 1,000 tokens
   - Maximum: 1,000,000 tokens
   - Flags outliers

4. **Query Diversity**
   - Minimum: 30% unique queries
   - Detects repetitive queries
   - Recommends varied queries

5. **Timestamp Validity**
   - Checks timestamp exists
   - Flags old sessions (>30 days)
   - Recommends fresh data

6. **Outlier Detection**
   - Tokens per query range: 100-10,000
   - Flags unusual patterns
   - Identifies potential errors

### Validation Output

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                      SESSION QUALITY VALIDATOR                                 ║
╚════════════════════════════════════════════════════════════════════════════════╝

ℹ Session Type: baseline
ℹ Reports Directory: reports
ℹ Fix Mode: false

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ Validating: session_baseline_20260713_100523.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Query count: 15 ✓
  Token count: 5234 ✓
  Query diversity: 87% ✓
  Timestamp: 2026-07-13T10:05:23 ✓
  Tokens per query: 349 ✓
✓ PASSED: All checks passed

╔════════════════════════════════════════════════════════════════════════════════╗
║                           VALIDATION SUMMARY                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

Total Sessions:    10
Passed:            10 (100%)
Warnings:          0 (0%)
Failed:            0 (0%)

✓ All sessions passed validation!
✓ Quality report saved to: reports/quality_report_baseline_20260713_100730.txt
```

### Quality Report

The validator generates a detailed report:

```
SESSION QUALITY VALIDATION REPORT
==================================

Session Type: baseline
Validation Date: Mon Jul 13 10:07:30 CEST 2026

SUMMARY
-------
Total Sessions: 10
Passed: 10 (100%)
Warnings: 0 (0%)
Failed: 0 (0%)

QUALITY CRITERIA
----------------
Minimum Queries: 5
Minimum Tokens: 1000
Maximum Tokens: 1000000
Minimum Diversity: 30%

RECOMMENDATIONS
---------------
- All sessions passed! Ready for analysis
```

## Workflow Integration

### Recommended Workflow

1. **Start Monitoring** (Terminal 1)
   ```bash
   python3 examples/live_session_monitor.py --baseline
   ```

2. **Collect Sessions** (Terminal 2)
   ```bash
   # Run Bob Shell sessions
   # Monitor shows real-time progress
   ```

3. **Validate Quality** (After collection)
   ```bash
   ./scripts/validate_session_quality.sh --baseline --verbose
   ```

4. **Review Report**
   ```bash
   cat reports/quality_report_baseline_*.txt
   ```

### Parallel Monitoring

You can run both tools simultaneously:

```bash
# Terminal 1: Real-time monitoring
python3 examples/live_session_monitor.py --baseline

# Terminal 2: Collect sessions
# (Run your Bob Shell sessions here)

# Terminal 3: Periodic validation
watch -n 60 './scripts/validate_session_quality.sh --baseline'
```

## Troubleshooting

### Monitor Not Updating

**Problem:** Dashboard shows 0 sessions

**Solutions:**
1. Check reports directory exists: `ls -la reports/`
2. Verify session files exist: `ls reports/*baseline*.json`
3. Check file naming matches pattern: `*baseline*.json`
4. Ensure JSON files are valid: `jq . reports/session_baseline_*.json`

### Validation Failures

**Problem:** Sessions fail validation

**Common Issues:**

1. **Low Query Count**
   - Run longer sessions (10+ minutes)
   - Ask more diverse questions
   - Use complex queries

2. **Low Token Count**
   - Use more detailed queries
   - Request comprehensive responses
   - Avoid yes/no questions

3. **Low Diversity**
   - Vary your questions
   - Avoid repetitive queries
   - Cover different topics

4. **Invalid JSON**
   - Check session tracker implementation
   - Verify file write permissions
   - Ensure complete writes (not truncated)

### Performance Issues

**Problem:** Monitor is slow or laggy

**Solutions:**
1. Increase refresh interval (edit `refresh_interval` in code)
2. Reduce number of recent sessions shown
3. Clear old session files
4. Check system resources

## Best Practices

### Session Collection

1. **Quality Over Quantity**
   - Aim for 10+ queries per session
   - Use varied, complex queries
   - Ensure realistic usage patterns

2. **Consistent Environment**
   - Same Bob Shell version
   - Same system configuration
   - Similar time of day

3. **Diverse Queries**
   - Mix simple and complex queries
   - Cover different topics
   - Include various query types

### Monitoring

1. **Start Early**
   - Begin monitoring before first session
   - Catch issues immediately
   - Track progress from start

2. **Check Regularly**
   - Review quality indicators
   - Address warnings promptly
   - Validate periodically

3. **Document Issues**
   - Note any anomalies
   - Record system changes
   - Track environmental factors

## Advanced Usage

### Custom Thresholds

Edit validation script to adjust thresholds:

```bash
# In validate_session_quality.sh
MIN_QUERIES=10        # Increase minimum queries
MIN_TOKENS=2000       # Increase minimum tokens
MIN_DIVERSITY=0.5     # Require 50% diversity
```

### Custom Monitoring

Extend the monitor for custom metrics:

```python
# In live_session_monitor.py
def calculate_custom_metric(self):
    # Add your custom calculation
    return custom_value
```

### Integration with CI/CD

```bash
# Add to your CI pipeline
./scripts/validate_session_quality.sh --baseline
if [ $? -ne 0 ]; then
    echo "Quality validation failed"
    exit 1
fi
```

## Related Documentation

- [Phase 3 Validation User Guide](../phase3-validation-user-guide.md)
- [Phase 3 Testing Plan](../phase3-validation-testing-plan.md)
- [Session Tracking Guide](./session-tracking-guide.md)
- [Analysis and Reporting Guide](./analysis-reporting-guide.md)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review validation output carefully
3. Examine quality report details
4. Verify session file format

---

*Last Updated: 2026-07-13*
*Part of Phase 3 Real-World Validation*
