# Week 2: Baseline Data Collection Guide

## Overview

Execute 30 control tasks WITHOUT using knowledge-manager mode to establish baseline metrics.

## Task Categories

### Document Creation (10 tasks: DC_C_001 to DC_C_010)
Create new documentation from scratch.

**Examples**:
- Write API documentation for a new endpoint
- Create a design document for a feature
- Document a troubleshooting procedure
- Write a technical specification
- Create user guide for a tool

### Retrieval (10 tasks: RT_C_001 to RT_C_010)
Search for and retrieve information from existing documentation.

**Examples**:
- Find configuration settings for a service
- Locate error code explanations
- Search for API usage examples
- Find deployment procedures
- Retrieve architecture diagrams

### Maintenance (5 tasks: MT_C_001 to MT_C_005)
Update or fix existing documentation.

**Examples**:
- Update outdated version numbers
- Fix broken links
- Correct technical inaccuracies
- Add missing information
- Improve clarity of existing docs

### Synthesis (5 tasks: SY_C_001 to SY_C_005)
Combine information from multiple sources.

**Examples**:
- Create summary from multiple docs
- Compare different approaches
- Consolidate scattered information
- Create overview from detailed docs
- Build decision matrix from options

## Recording Metrics

### Method 1: Interactive (Recommended)

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 record_task.py
```

Follow the prompts:
1. Enter task ID (e.g., DC_C_001)
2. Enter tokens used (from Bob Shell output)
3. Enter bobcoin cost (from "task costs" line)
4. Enter time in seconds
5. Score quality (0-25 each category)

### Method 2: Quick Command Line

```bash
# Format: python3 record_task.py TASK_ID TOKENS COST TIME QUALITY
conda run -n hcd-at-its-core python3 record_task.py DC_C_001 450 0.045 120 85
```

### Method 3: Manual Python

```python
from collect_metrics import MetricsCollector, create_task_template

collector = MetricsCollector()
task = create_task_template('DC_C_001', 'document_creation', 'control')
task['metrics']['tokens_used'] = 450
task['metrics']['bobcoin_cost'] = 0.045
task['metrics']['time_seconds'] = 120
task['metrics']['quality_score']['completeness'] = 22
task['metrics']['quality_score']['accuracy'] = 23
task['metrics']['quality_score']['consistency'] = 20
task['metrics']['quality_score']['usability'] = 20
task['metrics']['quality_score']['total'] = 85
collector.record_task(task)
```

## Quality Scoring Guide

### Completeness (0-25 points)
- **20-25**: All required sections present, comprehensive
- **15-19**: Most sections present, minor gaps
- **10-14**: Some sections missing, noticeable gaps
- **5-9**: Many sections missing, significant gaps
- **0-4**: Minimal content, mostly incomplete

### Accuracy (0-25 points)
- **20-25**: All information correct and verified
- **15-19**: Mostly correct, minor inaccuracies
- **10-14**: Some errors, needs verification
- **5-9**: Multiple errors, questionable accuracy
- **0-4**: Mostly incorrect or unverified

### Consistency (0-25 points)
- **20-25**: Perfect consistency with existing docs
- **15-19**: Good consistency, minor deviations
- **10-14**: Some inconsistencies in style/format
- **5-9**: Multiple inconsistencies
- **0-4**: No consistency with existing patterns

### Usability (0-25 points)
- **20-25**: Excellent structure, easy to navigate
- **15-19**: Good structure, mostly clear
- **10-14**: Adequate structure, some confusion
- **5-9**: Poor structure, hard to use
- **0-4**: Unusable, no clear structure

## Token Counting

Bob Shell displays token usage after each interaction:
```
task costs: 0.45
```

**Conversion**: Multiply by 1000
- 0.45 bobcoins = 450 tokens
- 0.12 bobcoins = 120 tokens
- 1.20 bobcoins = 1200 tokens

## Time Tracking

Use a stopwatch or timer:
```bash
# Start timer
time bob

# Or use online stopwatch
# Record total time in seconds
```

## Example Workflow

### 1. Start Task
```bash
# Note start time
START_TIME=$(date +%s)

# Execute task in Bob Shell (normal mode, no knowledge-manager)
bob
```

### 2. Complete Task
```
# In Bob Shell, complete your documentation task
# Note the "task costs" value from output
```

### 3. Record Metrics
```bash
# Calculate time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Record using interactive script
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 record_task.py

# Enter:
# - Task ID: DC_C_001
# - Tokens: 450 (from task costs * 1000)
# - Cost: 0.045 (from task costs)
# - Time: 120 (calculated duration)
# - Quality scores: 22, 23, 20, 20
```

## Progress Tracking

Check your progress:
```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 -c "
from collect_metrics import MetricsCollector
collector = MetricsCollector()
tasks = collector.load_all_tasks()
control = [t for t in tasks if t['condition'] == 'control']
print(f'Control tasks completed: {len(control)}/30')
print(f'Remaining: {30 - len(control)}')
"
```

## Tips for Consistency

1. **Same Environment**: Use same Bob Shell setup for all tasks
2. **Similar Complexity**: Choose tasks of comparable difficulty
3. **No Shortcuts**: Don't use knowledge-manager mode or external tools
4. **Honest Scoring**: Be objective in quality assessment
5. **Document Context**: Note any unusual circumstances

## Common Issues

### Issue: Forgot to track time
**Solution**: Estimate based on similar tasks, note as estimate

### Issue: Task costs not showing
**Solution**: Check Bob Shell output, may need to enable cost display

### Issue: Quality scoring unclear
**Solution**: Use the detailed rubric above, when in doubt score conservatively

### Issue: Task too complex
**Solution**: Break into smaller tasks or choose simpler alternative

## Next Steps

After completing all 30 control tasks:
1. Verify data: `conda run -n hcd-at-its-core python3 analyze_results.py`
2. Review quality: Check for outliers or inconsistencies
3. Proceed to Week 3: Treatment condition (with knowledge-manager mode)

## Support

- **Templates**: `evaluation/data/templates/control_tasks.json`
- **Recording Script**: `evaluation/scripts/record_task.py`
- **Analysis**: `evaluation/scripts/analyze_results.py`
- **Full Guide**: `evaluation/EXECUTION_GUIDE.md`

---
*Week 2 Goal: Complete 30 control tasks with consistent, accurate metrics*
