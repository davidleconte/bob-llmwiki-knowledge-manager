# Week 2 Daily Checklist - Baseline Data Collection

**Goal**: Complete 30 control tasks over 6 days (5 tasks per day)  
**Mode**: Normal Bob Shell (NO knowledge-manager mode)  
**Location**: `~/Projects/bob-llmwiki-knowledge-manager/evaluation/`

## Daily Workflow

### Morning Setup (5 minutes)
```bash
# 1. Navigate to evaluation directory
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts

# 2. Check yesterday's progress
conda run -n hcd-at-its-core python3 -c "
from collect_metrics import MetricsCollector
collector = MetricsCollector()
tasks = collector.load_all_tasks()
control = [t for t in tasks if t['condition'] == 'control']
print(f'✅ Completed: {len(control)}/30')
print(f'📋 Today: {min(5, 30 - len(control))} tasks')
print(f'🎯 Remaining: {max(0, 30 - len(control))} tasks')
"

# 3. Prepare timer
START_TIME=$(date +%s)
```

### For Each Task (repeat 5 times)

#### Step 1: Choose Task (1 min)
Pick from your daily task list below. Use task IDs in order.

#### Step 2: Execute Task (10-20 min)
```bash
# Start Bob Shell (normal mode)
bob

# Complete your documentation task
# Note the "task costs" value when done
```

#### Step 3: Record Metrics (2 min)
```bash
# Calculate time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Record interactively (use wrapper to fix EOFError)
bash ~/Documents/Work/Labs/hcd-at-its-core/docs/knowledge-base/scripts/record_task_wrapper.sh

# Enter:
# - Task ID (e.g., DC_C_001)
# - Tokens (from "task costs" × 1000)
# - Cost (from "task costs")
# - Time in seconds
# - Quality scores (0-25 each)

# Reset timer for next task
START_TIME=$(date +%s)
```

## 6-Day Schedule

### Day 1: Document Creation (5 tasks)
**Focus**: Create new documentation from scratch

- [ ] **DC_C_001**: Write API documentation for an endpoint
- [ ] **DC_C_002**: Create a design document for a feature
- [ ] **DC_C_003**: Document a troubleshooting procedure
- [ ] **DC_C_004**: Write a technical specification
- [ ] **DC_C_005**: Create a user guide for a tool

**End of Day Check**:
```bash
conda run -n hcd-at-its-core python3 -c "
from collect_metrics import MetricsCollector
collector = MetricsCollector()
tasks = collector.load_all_tasks()
control = [t for t in tasks if t['condition'] == 'control']
print(f'Day 1 Complete: {len(control)}/5 tasks')
"
```

### Day 2: Document Creation (5 tasks)
**Focus**: Continue creating documentation

- [ ] **DC_C_006**: Document a configuration process
- [ ] **DC_C_007**: Write release notes for a version
- [ ] **DC_C_008**: Create onboarding documentation
- [ ] **DC_C_009**: Document a deployment procedure
- [ ] **DC_C_010**: Write architecture documentation

**End of Day Check**: Should have 10/30 tasks complete

### Day 3: Retrieval (5 tasks)
**Focus**: Search and retrieve information

- [ ] **RT_C_001**: Find configuration settings for a service
- [ ] **RT_C_002**: Locate error code explanations
- [ ] **RT_C_003**: Search for API usage examples
- [ ] **RT_C_004**: Find deployment procedures
- [ ] **RT_C_005**: Retrieve architecture diagrams

**End of Day Check**: Should have 15/30 tasks complete

### Day 4: Retrieval (5 tasks)
**Focus**: Continue information retrieval

- [ ] **RT_C_006**: Find security best practices
- [ ] **RT_C_007**: Locate performance tuning guides
- [ ] **RT_C_008**: Search for integration examples
- [ ] **RT_C_009**: Find troubleshooting guides
- [ ] **RT_C_010**: Retrieve testing procedures

**End of Day Check**: Should have 20/30 tasks complete

### Day 5: Maintenance (5 tasks)
**Focus**: Update existing documentation

- [ ] **MT_C_001**: Update outdated version numbers
- [ ] **MT_C_002**: Fix broken links in documentation
- [ ] **MT_C_003**: Correct technical inaccuracies
- [ ] **MT_C_004**: Add missing information to docs
- [ ] **MT_C_005**: Improve clarity of existing documentation

**End of Day Check**: Should have 25/30 tasks complete

### Day 6: Synthesis (5 tasks)
**Focus**: Combine information from multiple sources

- [ ] **SY_C_001**: Create summary from multiple documents
- [ ] **SY_C_002**: Compare different technical approaches
- [ ] **SY_C_003**: Consolidate scattered information
- [ ] **SY_C_004**: Create overview from detailed docs
- [ ] **SY_C_005**: Build decision matrix from options

**End of Day Check**: Should have 30/30 tasks complete ✅

## Quality Scoring Quick Reference

### Completeness (0-25)
- **20-25**: All sections present, comprehensive
- **15-19**: Most sections present, minor gaps
- **10-14**: Some sections missing
- **5-9**: Many sections missing
- **0-4**: Minimal content

### Accuracy (0-25)
- **20-25**: All information correct
- **15-19**: Mostly correct, minor errors
- **10-14**: Some errors present
- **5-9**: Multiple errors
- **0-4**: Mostly incorrect

### Consistency (0-25)
- **20-25**: Perfect consistency
- **15-19**: Good consistency
- **10-14**: Some inconsistencies
- **5-9**: Multiple inconsistencies
- **0-4**: No consistency

### Usability (0-25)
- **20-25**: Excellent structure
- **15-19**: Good structure
- **10-14**: Adequate structure
- **5-9**: Poor structure
- **0-4**: Unusable

## Tips for Success

### Time Management
- **Morning**: 2-3 tasks (fresh mind for complex work)
- **Afternoon**: 2-3 tasks (routine documentation)
- **Break**: 5-10 minutes between tasks

### Task Selection
- Choose real work tasks when possible
- Mix complexity levels throughout the day
- Use similar tasks to your actual work

### Consistency
- Same environment for all tasks
- Same Bob Shell setup
- Same quality standards
- Same time of day (if possible)

### Common Issues

**Forgot to track time?**
- Estimate based on similar tasks
- Note as estimate in comments

**Task costs not showing?**
- Check Bob Shell output carefully
- May need to enable cost display

**Quality scoring unclear?**
- Use the rubric above
- When in doubt, score conservatively
- Be consistent across all tasks

## Progress Tracking

### Quick Status Check
```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 -c "
from collect_metrics import MetricsCollector
import json

collector = MetricsCollector()
tasks = collector.load_all_tasks()
control = [t for t in tasks if t['condition'] == 'control']

print(f'\n📊 Week 2 Progress Report')
print(f'=' * 50)
print(f'Total Completed: {len(control)}/30 ({len(control)/30*100:.1f}%)')
print(f'Remaining: {30 - len(control)} tasks')
print(f'\nBy Category:')

categories = {}
for task in control:
    cat = task['scenario']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f'  {cat}: {count} tasks')

if control:
    avg_tokens = sum(t['metrics']['tokens_used'] for t in control) / len(control)
    avg_time = sum(t['metrics']['time_seconds'] for t in control) / len(control)
    avg_quality = sum(t['metrics']['quality_score']['total'] for t in control) / len(control)
    print(f'\nAverages:')
    print(f'  Tokens: {avg_tokens:.0f}')
    print(f'  Time: {avg_time:.0f}s ({avg_time/60:.1f}m)')
    print(f'  Quality: {avg_quality:.1f}/100')
"
```

### Daily Summary
At end of each day, run:
```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts
conda run -n hcd-at-its-core python3 -c "
from collect_metrics import MetricsCollector
collector = MetricsCollector()
tasks = collector.load_all_tasks()
control = [t for t in tasks if t['condition'] == 'control']
today = len(control) % 5 or 5
print(f'✅ Day {(len(control)-1)//5 + 1} Complete: {today}/5 tasks')
print(f'📈 Total Progress: {len(control)}/30 tasks')
print(f'🎯 Next: Day {(len(control)//5) + 1}')
"
```

## Week 2 Completion

After completing all 30 tasks:

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager/evaluation/scripts

# Generate preliminary analysis
conda run -n hcd-at-its-core python3 analyze_results.py

# Review baseline metrics
cat ../reports/analysis_report.txt
```

**Next**: Proceed to Week 3 (Treatment condition with knowledge-manager mode)

---

**Daily Time Commitment**: ~2 hours (5 tasks × 20 min + recording)  
**Total Week 2 Time**: ~12 hours over 6 days  
**Flexibility**: Can adjust to 3-4 tasks/day over 8-10 days if needed
