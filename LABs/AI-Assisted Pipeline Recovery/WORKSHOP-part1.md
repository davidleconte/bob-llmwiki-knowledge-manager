# WORKSHOP - AI-Assisted Pipeline Recovery
## Self-Healing Pipelines with IBM Bob CLI - 15-20 minutes

This workshop demonstrates how to build **self-healing data pipelines** using AI-powered error recovery. You'll see how an AI agent can automatically diagnose pipeline failures, suggest fixes, and apply them — turning manual incident response into automated remediation.

**Key idea:** Production pipelines fail for predictable reasons (schema changes, permission issues, version mismatches). Instead of waking up engineers at 3 AM, we let an AI agent diagnose and fix these issues automatically.

---

## Learning Objectives

By the end of this workshop, you will:
1. Understand the architecture of AI-assisted pipeline recovery
2. See how Bob CLI analyzes errors and suggests contextual fixes
3. Run a self-healing pipeline that recovers from data schema mismatches
4. Understand the safety mechanisms that prevent dangerous auto-fixes

---

## Prerequisites

### Required Tools
- Bash 4+
- Python 3.8+
- IBM Bob CLI installed and configured

### Quick Environment Check (30 seconds)
```bash
# Verify tools are available
bash --version | head -1
python3 --version
bob --version 2>/dev/null || echo "Bob CLI not found - please install"

# Navigate to workshop directory
cd ai-pipeline-recovery
ls -la
```

---

## Part 1: Understanding the Problem (3 minutes)

### The Scenario
You have a data processing pipeline that reads CSV files and generates reports. One day, an upstream system changes its export format — column names are different. Your pipeline breaks at 2 AM.

**Traditional approach:**
1. Alert fires → PagerDuty wakes engineer
2. Engineer SSHs into server, reads logs
3. Engineer identifies schema mismatch
4. Engineer writes a fix (sed command, Python script, etc.)
5. Engineer deploys fix, reruns pipeline
6. Total time: 30-60 minutes (plus lost sleep)

**AI-assisted approach:**
1. Pipeline fails → AI agent receives error context
2. AI analyzes error, identifies root cause
3. AI suggests fix (validated for safety)
4. Fix is applied automatically
5. Pipeline retries and succeeds
6. Total time: < 1 minute (no human involved)

### Examine the Data Files

```bash
# Look at what valid data looks like
echo "=== Valid Data (expected schema) ==="
head -5 scenarios/data_issues/sample_data_valid.csv

# Look at what broken data looks like
echo -e "\n=== Broken Data (schema mismatch) ==="
head -5 scenarios/data_issues/sample_data_broken.csv
```

**What you'll see:**

| Valid CSV | Broken CSV |
|-----------|------------|
| user_id | id |
| name | fullname |
| email | mail |
| age | years |
| signup_date | created_at |

The data is the same, but the column names changed. This is a common production issue when:
- Upstream systems upgrade their export format
- Different vendors use different naming conventions
- Database migrations rename columns

---

## Part 2: See the Failure (2 minutes)

### Run the Data Processor Manually

```bash
# This should succeed
echo "=== Processing valid data ==="
python3 scenarios/data_issues/data_processor.py scenarios/data_issues/sample_data_valid.csv

# This should fail
echo -e "\n=== Processing broken data ==="
python3 scenarios/data_issues/data_processor.py scenarios/data_issues/sample_data_broken.csv
```

**Expected failure output:**
```
Loading CSV file: scenarios/data_issues/sample_data_broken.csv
Loaded 10 records
Validating schema...
Schema validation passed
Validating data...
Warning: Extra columns found (will be ignored): {'id', 'mail', 'created_at', 'fullname', 'years'}
Validation Error: Row 1: missing user_id
```

The processor found columns it doesn't recognize and couldn't find `user_id`.

---

## Part 3: The Self-Healing Pipeline (5 minutes)

### Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ai_pipeline.sh │────▶│  Your Command   │────▶│  Success?       │
│  (orchestrator) │     │  (data_processor)│     │                 │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                                │
         │ On failure                                     │ Yes → Done
         ▼                                                │
┌─────────────────┐     ┌─────────────────┐              │
│  ai_recover.sh  │────▶│  IBM Bob CLI    │              │
│  (recovery)     │     │  (AI analysis)  │              │
└────────┬────────┘     └────────┬────────┘              │
         │                       │                        │
         │◀──────────────────────┘                        │
         │ Fix suggestion                                 │
         ▼                                                │
┌─────────────────┐                                       │
│  Apply Fix      │───────────────────────────────────────┘
│  & Retry        │
└─────────────────┘
```

### Run the Pipeline in Dry-Run Mode

First, let's see what the AI would suggest without actually applying fixes:

```bash
./ai_pipeline.sh --dry-run scenarios/data_issues/pipeline.txt
```

**Watch for:**
1. Pipeline starts, attempts the data processing step
2. Step fails with validation error
3. AI recovery is invoked
4. Bob CLI analyzes the error context
5. Bob CLI suggests a fix (e.g., `sed` command to rename columns)
6. Dry-run mode prevents the fix from being applied

### Examine Bob CLI's Analysis

The AI will output something like:

```
=== AI Analysis ===

## Analysis
The data processor expects specific column names but the CSV file has different column names:

**Current columns:** id, fullname, mail, years, created_at
**Expected columns:** user_id, name, email, age, signup_date

## Root Cause
The column names don't match the expected schema.

## Fix
FIX:
sed -i.bak '1s/id,fullname,mail,years,created_at/user_id,name,email,age,signup_date/' scenarios/data_issues/sample_data_broken.csv
```

**Discussion points:**
- The AI read the error message and understood the context
- It examined the actual data file to see current column names
- It proposed a targeted fix (only the header row)
- It created a backup (`.bak`) for safety

---

## Part 4: Live Recovery (5 minutes)

### Reset the Test Data

```bash
# Ensure the broken file has wrong column names
cat scenarios/data_issues/sample_data_broken.csv | head -1
# Should show: id,fullname,mail,years,created_at
```

If the file was already fixed by a previous run, restore it:
```bash
cat > scenarios/data_issues/sample_data_broken.csv << 'EOF'
id,fullname,mail,years,created_at
1,Alice Johnson,alice@example.com,28,2023-01-15
2,Bob Smith,bob.smith@company.org,34,2023-02-20
3,Carol Williams,carol.w@email.net,45,2023-03-10
4,David Brown,david.brown@work.com,29,2023-04-05
5,Eva Martinez,eva.m@startup.io,31,2023-05-12
6,Frank Lee,frank.lee@tech.co,42,2023-06-18
7,Grace Chen,grace@domain.com,26,2023-07-22
8,Henry Wilson,henry.w@mail.org,38,2023-08-30
9,Ivy Thompson,ivy.t@example.com,33,2022-09-14
10,Jack Davis,jack.davis@company.com,27,2022-10-25
EOF
```

### Run the Full Self-Healing Pipeline

```bash
./ai_pipeline.sh scenarios/data_issues/pipeline.txt
```

**What you should see:**
1. Pipeline starts
2. First attempt fails (schema mismatch)
3. AI recovery kicks in
4. Bob CLI analyzes and suggests fix
5. Fix is applied (columns renamed)
6. Pipeline retries
7. **Success!** Data is processed correctly

### Verify the Recovery

```bash
# Check the output file was created
cat scenarios/data_issues/output.json

# Check the backup was created
ls -la scenarios/data_issues/*.bak 2>/dev/null

# Check the CSV was fixed
head -1 scenarios/data_issues/sample_data_broken.csv
# Should now show: user_id,name,email,age,signup_date
```

---

## Part 5: Safety Mechanisms (3 minutes)

### Blocked Commands

The recovery system blocks dangerous commands. Try this:

```bash
./ai_recover.sh --error "Permission denied" --command "cat /etc/passwd" --work-dir "/"
```

Even if the AI suggested `rm -rf /` or `chmod -R 777 /`, these patterns are blocked:

```python
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "mkfs",
    "dd if=",
    "chmod -R 777 /",
    "chown -R",
    "curl.*| *sh",
    "wget.*| *sh",
]
```

### Retry Limits

The pipeline has a maximum retry count (default: 3) to prevent infinite loops:

```bash
# Set a lower retry limit
MAX_RETRIES=1 ./ai_pipeline.sh scenarios/data_issues/pipeline.txt
```

### Audit Trail

All recovery actions are logged for compliance and debugging:

```bash
# Human-readable logs
ls -la logs/*.log

# JSON audit trail (machine-parseable)
cat logs/pipeline_audit.jsonl | head -3
```

---

## Part 6: Hands-On Challenge (Optional, 5 minutes)

### Create Your Own Failure Scenario

1. Create a new broken data file with a different schema issue:

```bash
cat > scenarios/data_issues/challenge_data.csv << 'EOF'
ID,full_name,email_address,user_age,registration_date
101,Test User,test@example.com,25,2024-01-01
102,Another User,another@test.com,30,2024-02-15
EOF
```

2. Update the pipeline to process this file:

```bash
cat > scenarios/data_issues/challenge_pipeline.txt << 'EOF'
# Challenge pipeline
process_challenge: python3 scenarios/data_issues/data_processor.py scenarios/data_issues/challenge_data.csv
EOF
```

3. Run the self-healing pipeline:

```bash
./ai_pipeline.sh scenarios/data_issues/challenge_pipeline.txt
```

**Challenge question:** Did the AI successfully fix the schema? What fix did it suggest?

---

## Key Takeaways

### Why This Matters

| Traditional Ops | AI-Assisted Ops |
|-----------------|-----------------|
| Manual log analysis | Automated root cause analysis |
| Copy-paste fixes from runbooks | Context-aware fix generation |
| Wake up engineers at 3 AM | Autonomous recovery |
| 30-60 min MTTR | < 1 min MTTR |
| Human error in fixes | Validated, safe fixes |

### When to Use AI-Assisted Recovery

**Good candidates:**
- Schema/format mismatches
- Permission issues (within allowed scope)
- Missing dependencies
- Configuration drift
- Encoding problems

**Not recommended:**
- Data corruption (needs human judgment)
- Security incidents (needs investigation)
- Business logic errors (needs domain expertise)

### Production Considerations

1. **Approval Mode**: In sensitive environments, have AI suggest fixes but require human approval
2. **Rate Limiting**: Avoid excessive AI API calls in retry loops
3. **Monitoring**: Alert on recovery actions for post-incident review
4. **Scope Limits**: Restrict what the AI can modify (specific directories, file types)

---

## Quick Reference

### Commands Used

```bash
# Run pipeline with auto-recovery
./ai_pipeline.sh <pipeline_file>

# Dry-run (show fixes without applying)
./ai_pipeline.sh --dry-run <pipeline_file>

# Custom retry limit
./ai_pipeline.sh --retries 5 <pipeline_file>

# Run single command with recovery
./ai_pipeline.sh --step "my_step" "python3 script.py"

# Test recovery module directly
./ai_recover.sh --error "KeyError: 'user_id'" --command "python3 test.py" --work-dir "."
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | 3 | Maximum recovery attempts |
| `DRY_RUN` | false | Preview mode (no changes) |
| `BOB_TIMEOUT` | 60 | AI API timeout in seconds |

### Project Structure

```
ai-pipeline-recovery/
├── ai_pipeline.sh          # Main orchestrator
├── ai_recover.sh           # AI recovery module
├── prompts/                # Error-specific prompt templates
│   ├── data_error.txt
│   ├── import_error.txt
│   ├── permission_error.txt
│   └── sql_error.txt
├── scenarios/
│   └── data_issues/
│       ├── data_processor.py
│       ├── sample_data_valid.csv
│       └── sample_data_broken.csv
└── logs/                   # Execution logs & audit trail
```

---

## Next Steps (you can explore on your own)

1. **Phase 2**: Add permission recovery scenarios
2. **Phase 3**: Add package version mismatch scenarios
3. **Advanced**: Integrate with CI/CD pipelines
4. **Production**: Add Slack/PagerDuty notifications for recovery events

---

## Resources

- [IBM Bob CLI Documentation](https://internal.bob.ibm.com/docs/shell)
- [Project Repository](./README.md)

---

*Workshop created for AI Engineers and Developers exploring agentic DevOps patterns.*
