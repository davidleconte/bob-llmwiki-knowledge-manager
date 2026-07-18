---
title: "Phase 3 Validation User Guide"
category: guide
date: 2026-07-13
status: active
tags: [phase3, validation, guide, measurement, best-practices]
related:
  - ../research/phase3-day1-2-validation-framework.md
  - ../research/phase3-day3-4-parallel-work.md
created: 2026-07-13
updated: 2026-07-13

---

# Phase 3 Validation User Guide

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Overview

This guide helps you collect high-quality baseline and optimized measurements for Phase 3 validation. Following these best practices ensures accurate, reliable results that demonstrate real-world token savings.

**Goal:** Collect 20+ sessions in each mode (baseline and optimized) to validate token optimization effectiveness.

**Time Required:** 2-4 hours per mode (40-80 total)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Baseline Collection](#baseline-collection)
3. [Optimized Collection](#optimized-collection)
4. [Best Practices](#best-practices)
5. [Query Examples](#query-examples)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [Analysis](#analysis)

---

## Quick Start

### Prerequisites

**Required:**
- Python 3.11+
- Bob Shell installed and configured
- Project repository cloned

**Optional:**
- matplotlib (for visualizations)
- numpy (for better statistics)

**Install Optional Dependencies:**
```bash
pip install matplotlib numpy
```

### Baseline Collection (Step 1)

```bash
# Start baseline measurement collection
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/run_baseline_measurement.sh 20
```

**What this does:**
- Guides you through 20 sessions
- Tracks token usage WITHOUT optimization
- Saves data to `evaluation/data/sessions/`
- Creates `baseline_sessions.txt` list

### Optimized Collection (Step 2)

```bash
# After baseline complete, collect optimized measurements
./scripts/run_optimized_measurement.sh 20
```

**What this does:**
- Guides you through 20 sessions
- Tracks token usage WITH optimization
- Compares with baseline automatically
- Creates `optimized_sessions.txt` list

### Analysis (Step 3)

```bash
# Generate reports and visualizations
./scripts/analyze_sessions.sh
```

**What this does:**
- Analyzes all sessions
- Generates reports (text, HTML, CSV, JSON)
- Creates visualizations (5 chart types)
- Displays summary and recommendations

---

## Baseline Collection

### Purpose

Baseline measurements establish the "before optimization" benchmark. These sessions run WITHOUT any token optimization to measure natural token usage.

### How to Collect

**1. Start the Script:**
```bash
./scripts/run_baseline_measurement.sh 20
```

**2. For Each Session:**

The script will prompt you to:
- Press Enter to start tracking
- Use Bob Shell normally for your tasks
- Enter queries and responses when prompted
- Type 'done' when session complete

**3. Session Workflow:**

```
Session 1 of 20
--------------
Press Enter to start tracking...

[Use Bob Shell for your task]

Query: [Enter your query to Bob Shell]
Context (optional): [Enter any context, or press Enter to skip]
Response: [Enter Bob's response]

[Repeat for multiple queries in this session]

Type 'done' when finished, or continue with more queries...
Query: done

✓ Session baseline_001 saved
```

### What to Track

**Good Sessions:**
- Real Bob Shell usage (not artificial)
- Complete tasks (not just single queries)
- Diverse query types (code, research, debug, etc.)
- Natural conversation flow
- Multiple queries per session (5-15 typical)

**Avoid:**
- Artificial or contrived queries
- Single-query sessions
- Repetitive queries
- Test queries that don't represent real usage

### Session Length

**Recommended:**
- **Minimum:** 5 queries per session
- **Typical:** 8-12 queries per session
- **Maximum:** 20 queries per session

**Why:** Longer sessions better represent real usage patterns and provide more data points for analysis.

### Query Diversity

**Include a mix of:**
- Code writing/editing
- Code review/analysis
- Debugging/troubleshooting
- Research/documentation
- Architecture/design
- Testing/validation

**Example Distribution:**
- 40% Code-related (write, edit, review)
- 30% Problem-solving (debug, troubleshoot)
- 20% Research (documentation, best practices)
- 10% Other (planning, design, testing)

---

## Optimized Collection

### Purpose

Optimized measurements demonstrate token savings with optimization enabled. These sessions run WITH full optimization (caching, prompt optimization, truncation).

### How to Collect

**1. Start the Script:**
```bash
./scripts/run_optimized_measurement.sh 20
```

**2. Use Similar Queries:**

For best comparison, use similar types of queries as baseline:
- Same task categories (code, research, debug)
- Similar complexity levels
- Similar session lengths
- Natural usage patterns

**Important:** Don't try to "game" the system. Use Bob Shell naturally.

### What's Different

**Optimization Enabled:**
- ✅ L1 Cache (exact match)
- ✅ L2 Cache (semantic similarity)
- ✅ Prompt optimization
- ✅ Context truncation

**You'll Notice:**
- Some queries return faster (cache hits)
- Token counts are lower
- Similar quality responses
- Slight latency increase (5-10ms)

### Comparison Tips

**For Fair Comparison:**
- Use similar query types as baseline
- Maintain similar session lengths
- Don't artificially repeat queries (even though cache would help)
- Focus on natural usage

**Don't:**
- Intentionally repeat queries to boost cache hits
- Use simpler queries than baseline
- Make sessions shorter than baseline
- Try to "optimize" your queries

---

## Best Practices

### Session Quality

**✅ DO:**
- Use Bob Shell for real tasks
- Complete full workflows (not just single queries)
- Include context when relevant
- Use natural language
- Ask follow-up questions
- Let conversations flow naturally

**❌ DON'T:**
- Create artificial test queries
- Use single-word queries
- Skip context when it's relevant
- Rush through sessions
- Use repetitive queries
- Try to "game" the measurements

### Query Quality

**Good Query Examples:**

```
✅ "Review this Python function for security issues and suggest improvements"
✅ "Help me debug why this API call is returning 500 errors"
✅ "Explain the trade-offs between REST and GraphQL for this use case"
✅ "Refactor this code to follow SOLID principles"
```

**Poor Query Examples:**

```
❌ "hi"
❌ "test"
❌ "what is python"
❌ "hello world"
```

### Context Usage

**When to Include Context:**
- Code snippets for review/debugging
- Error messages for troubleshooting
- Documentation for research
- Previous conversation for follow-ups

**When to Skip Context:**
- General questions
- New topics
- Simple queries
- Self-contained questions

**Example with Context:**

```
Query: "Why is this function throwing a TypeError?"
Context: 
def calculate_total(items):
    return sum(item.price for item in items)

# Error: TypeError: 'NoneType' object is not iterable
```

### Session Pacing

**Recommended Pace:**
- **Don't rush:** Take time to formulate good queries
- **Natural flow:** Let conversations develop naturally
- **Complete tasks:** Finish what you start
- **Take breaks:** Between sessions if needed

**Typical Session Duration:**
- 10-20 minutes per session
- 5-15 queries per session
- Natural conversation flow

---

## Query Examples

### Code Writing

**Good:**
```
"Create a Python function that validates email addresses using regex, 
handles edge cases, and includes error handling"

"Write a React component for a user profile card with props for name, 
avatar, bio, and social links"

"Implement a binary search algorithm in TypeScript with proper type 
annotations and comments"
```

**Context:** None needed (self-contained)

### Code Review

**Good:**
```
"Review this authentication middleware for security vulnerabilities 
and suggest improvements"

"Analyze this database query for performance issues and recommend 
optimizations"

"Check this API endpoint implementation for best practices and error 
handling"
```

**Context:** Include the code to review

### Debugging

**Good:**
```
"Help me debug why this React component is re-rendering infinitely"

"This SQL query is running slowly on large datasets. How can I optimize it?"

"My API is returning 401 errors intermittently. What could be causing this?"
```

**Context:** Include error messages, stack traces, or relevant code

### Research

**Good:**
```
"What are the best practices for implementing rate limiting in a REST API?"

"Compare different approaches for handling authentication in microservices"

"Explain the CAP theorem and its implications for distributed systems"
```

**Context:** Optional (background information if relevant)

### Architecture

**Good:**
```
"Design a scalable architecture for a real-time chat application with 
1M+ concurrent users"

"What's the best way to structure a monorepo with multiple TypeScript 
packages?"

"How should I organize a Django project with multiple apps and shared 
utilities?"
```

**Context:** Optional (project requirements if relevant)

### Testing

**Good:**
```
"Write unit tests for this authentication service using pytest"

"Create integration tests for this API endpoint with mock data"

"How should I test this React component that uses external APIs?"
```

**Context:** Include the code to test

---

## Troubleshooting

### Common Issues

#### Issue: Script Won't Start

**Symptoms:**
```
bash: ./scripts/run_baseline_measurement.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/run_baseline_measurement.sh
chmod +x scripts/run_optimized_measurement.sh
```

#### Issue: Python Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'tiktoken'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: Session Data Not Saving

**Symptoms:**
- No files in `evaluation/data/sessions/`
- Session list file empty

**Solution:**
1. Check directory exists: `ls -la evaluation/data/sessions/`
2. Check permissions: `ls -la evaluation/data/`
3. Try manual session tracker:
```bash
python3 examples/bob_shell_session_tracker.py \
  --mode baseline \
  --session-id test_session
```

#### Issue: Can't Enter Multi-line Context

**Symptoms:**
- Context prompt only accepts single line
- Need to paste code with newlines

**Solution:**
Use heredoc syntax:
```bash
Context: <<EOF
def my_function():
    return "multi-line code"
EOF
```

Or paste and press Ctrl+D when done.

#### Issue: Session Tracker Crashes

**Symptoms:**
```
Traceback (most recent call last):
  ...
KeyError: 'queries'
```

**Solution:**
1. Check session file format: `cat evaluation/data/sessions/session_id.json`
2. Delete corrupted session: `rm evaluation/data/sessions/session_id.json`
3. Restart session

#### Issue: Analysis Script Fails

**Symptoms:**
```
Error: No valid sessions found
```

**Solution:**
1. Check session lists exist:
```bash
cat evaluation/data/sessions/baseline_sessions.txt
cat evaluation/data/sessions/optimized_sessions.txt
```

2. Verify session files exist:
```bash
ls -la evaluation/data/sessions/*.json
```

3. Check session file format:
```bash
python3 -m json.tool evaluation/data/sessions/baseline_001.json
```

### Getting Help

**If issues persist:**

1. **Check logs:**
```bash
cat .bob/notes/pending-notes.txt
```

2. **Validate session data:**
```bash
python3 examples/test_analysis_tools.py
```

3. **Run with debug output:**
```bash
python3 examples/bob_shell_session_tracker.py --help
```

4. **Create issue:**
- Include error message
- Include steps to reproduce
- Include session file (if relevant)

---

## FAQ

### General Questions

**Q: How long does collection take?**  
A: 2-4 hours per mode (baseline and optimized), 4-8 hours total. Can be done over multiple days.

**Q: Can I pause and resume?**  
A: Yes! The scripts save progress. You can stop anytime and continue later with the same command.

**Q: How many queries per session?**  
A: Recommended 5-15 queries per session. Longer sessions better represent real usage.

**Q: Can I delete bad sessions?**  
A: Yes! Remove the session file and update the session list:
```bash
rm evaluation/data/sessions/bad_session.json
# Edit baseline_sessions.txt to remove the session ID
```

### Baseline Collection

**Q: What if I accidentally use optimization?**  
A: Delete that session and redo it. Baseline must be WITHOUT optimization.

**Q: Should I use the same queries for all sessions?**  
A: No! Use diverse, realistic queries that represent your actual Bob Shell usage.

**Q: Can I use Bob Shell normally during collection?**  
A: Yes! That's the point. Use Bob Shell for real tasks, not artificial tests.

**Q: What if a session is too short?**  
A: Aim for 5+ queries per session. If shorter, consider combining with another task.

### Optimized Collection

**Q: Should I use the exact same queries as baseline?**  
A: No! Use similar types of queries, but don't copy-paste. Natural usage is key.

**Q: Will cache hits skew results?**  
A: No! Cache hits are part of optimization. They demonstrate real-world savings.

**Q: What if I don't see savings?**  
A: Some queries won't benefit from optimization. That's normal. Overall savings matter.

**Q: Can I repeat queries to boost cache hits?**  
A: No! Don't artificially repeat queries. Use natural, diverse queries.

### Analysis

**Q: When can I run analysis?**  
A: Anytime! Run `./scripts/analyze_sessions.sh --baseline-only` after baseline collection.

**Q: What if results look wrong?**  
A: Check session data quality. Look for:
- Artificial queries
- Single-query sessions
- Repetitive queries
- Incomplete sessions

**Q: How do I interpret results?**  
A: See the generated HTML report (`reports/validation_report.html`) for detailed analysis and recommendations.

**Q: What's a good savings percentage?**  
A: 20-40% is typical. Higher is better, but quality matters more than quantity.

### Technical Questions

**Q: Where is data stored?**  
A: `evaluation/data/sessions/` directory. Each session is a JSON file.

**Q: Can I edit session data?**  
A: Yes, but not recommended. Better to delete and recollect bad sessions.

**Q: What format is session data?**  
A: JSON format. See `examples/bob_shell_session_tracker.py` for schema.

**Q: Can I export data?**  
A: Yes! Use `./scripts/analyze_sessions.sh` to export CSV, JSON, or HTML.

---

## Analysis

### Running Analysis

**Full Analysis:**
```bash
./scripts/analyze_sessions.sh
```

**Baseline Only:**
```bash
./scripts/analyze_sessions.sh --baseline-only
```

**Optimized Only:**
```bash
./scripts/analyze_sessions.sh --optimized-only
```

**Comparison Only:**
```bash
./scripts/analyze_sessions.sh --compare
```

**Visualizations Only:**
```bash
./scripts/analyze_sessions.sh --visualize
```

### Understanding Results

**Key Metrics:**

1. **Token Reduction:** Overall percentage of tokens saved
   - **Good:** 20-40%
   - **Excellent:** 40%+
   - **Poor:** <15%

2. **Cache Hit Rate:** Percentage of queries served from cache
   - **Good:** 20-40%
   - **Excellent:** 40%+
   - **Poor:** <10%

3. **Optimization Rate:** Percentage of queries optimized
   - **Good:** 60-80%
   - **Excellent:** 80%+
   - **Poor:** <50%

4. **Latency Overhead:** Additional time for optimization
   - **Good:** <10ms
   - **Acceptable:** 10-50ms
   - **Poor:** >50ms

**Statistical Significance:**
- **Yes:** Results are reliable (95% confidence)
- **No:** Need more data or results are inconclusive

### Generated Reports

**Text Report:** `reports/validation_report.txt`
- Console-friendly format
- Summary statistics
- Recommendations

**HTML Report:** `reports/validation_report.html`
- Styled, interactive
- Detailed metrics
- Visual presentation
- Open in browser

**CSV Export:** `reports/sessions.csv`
- Spreadsheet-ready
- Per-session data
- Easy analysis in Excel/Sheets

**JSON Export:** `reports/sessions.json`
- Programmatic access
- Complete session data
- Machine-readable

### Visualizations

**Generated Charts:**

1. **savings_comparison.png**
   - Token usage: baseline vs optimized
   - Savings per session

2. **cache_effectiveness.png**
   - Cache hit rate
   - Optimization rate
   - Truncation rate

3. **latency_distribution.png**
   - Latency histogram
   - Box plot comparison

4. **savings_over_time.png**
   - Cumulative savings trend
   - Session-by-session progress

5. **dashboard.png**
   - All metrics in one view
   - Comprehensive overview

**Viewing Charts:**
```bash
open reports/dashboard.png
open reports/validation_report.html
```

### Next Steps

**After Analysis:**

1. **Review Results:**
   - Check HTML report
   - Examine dashboard
   - Verify metrics

2. **Validate Quality:**
   - Check for outliers
   - Verify session quality
   - Look for anomalies

3. **Document Findings:**
   - Summarize results
   - Note key insights
   - Capture lessons learned

4. **Share Results:**
   - Present to stakeholders
   - Update documentation
   - Archive data

---

## Summary

### Quick Reference

**Baseline Collection:**
```bash
./scripts/run_baseline_measurement.sh 20
```

**Optimized Collection:**
```bash
./scripts/run_optimized_measurement.sh 20
```

**Analysis:**
```bash
./scripts/analyze_sessions.sh
```

### Success Criteria

**Good Validation:**
- ✅ 20+ sessions per mode
- ✅ Diverse query types
- ✅ Natural usage patterns
- ✅ Complete sessions (5+ queries)
- ✅ Statistical significance
- ✅ 20%+ token reduction

**Poor Validation:**
- ❌ <10 sessions per mode
- ❌ Artificial queries
- ❌ Single-query sessions
- ❌ Repetitive queries
- ❌ No statistical significance
- ❌ <10% token reduction

### Key Takeaways

1. **Use Bob Shell naturally** - Don't create artificial tests
2. **Diverse queries** - Mix code, research, debug, etc.
3. **Complete sessions** - 5-15 queries per session
4. **Quality over quantity** - Better to have 20 good sessions than 50 poor ones
5. **Follow best practices** - See examples and guidelines above

---

## Additional Resources

**Documentation:**
- [Validation Framework](../research/phase3-day1-2-validation-framework.md)
- [Analysis Tools](../research/phase3-day3-4-parallel-work.md)

**Scripts:**
- `scripts/run_baseline_measurement.sh` - Baseline collection
- `scripts/run_optimized_measurement.sh` - Optimized collection
- `scripts/analyze_sessions.sh` - Analysis automation

**Examples:**
- `examples/bob_shell_session_tracker.py` - Session tracker
- `examples/analysis_and_reporting.py` - Analysis tools
- `examples/visualization.py` - Visualization tools
- `examples/test_analysis_tools.py` - Testing framework

---

**Last Updated:** 2026-07-13  
**Version:** 1.0  
**Status:** Active
