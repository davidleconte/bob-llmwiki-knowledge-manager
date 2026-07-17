# Best Practices for Workshop Facilitators

This guide helps facilitators run the AI-Assisted Pipeline Recovery workshops effectively.

---

## Before the Workshop

### Environment Setup (15 min before)

```bash
# 1. Verify all tools are installed
bash --version      # Need 4+
python3 --version   # Need 3.8+
sqlite3 --version
bob --version       # IBM Bob CLI

# 2. Navigate to project directory
cd ai-pipeline-recovery

# 3. Pre-warm Bob CLI (avoids cold-start delays during demo)
echo "test" | bob "respond with OK"

# 4. Reset test data to broken state
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py

# 5. Clear old logs
rm -f logs/*.log logs/*.jsonl
```

### Pre-flight Checklist

- [ ] Bob CLI authenticated and working
- [ ] All "broken" test files are in broken state
- [ ] Terminal font size readable for audience
- [ ] Screen sharing ready
- [ ] Workshop materials open (WORKSHOP.md or WORKSHOP-part2.md)

---

## During the Workshop

### Pacing Guidelines

| Section | Time | Facilitator Action |
|---------|------|-------------------|
| Introduction | 2-3 min | Explain the problem (3 AM alerts, manual fixes) |
| Show the failure | 2 min | Run command, let it fail visibly |
| AI analysis | 3-5 min | Point out what AI detected, discuss the fix |
| Apply & retry | 2 min | Show successful recovery |
| Q&A / Discussion | 5 min | Address questions, relate to their use cases |

### Key Talking Points

**When showing the error:**
> "Notice how the error message includes both what's missing AND what's available. This context is critical for the AI to suggest an accurate fix."

**When AI suggests a fix:**
> "The AI didn't just identify the problem - it generated a working command. Notice it creates a backup file first."

**When discussing production use:**
> "In production, you'd start with dry-run mode. The AI suggests, humans approve, then you gradually enable auto-fix for low-risk scenarios."

### Handling Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Bob CLI timeout | Run the command again; first call is often slow |
| Metrics forwarder errors | Ignore - cosmetic only, doesn't affect results |
| "Command not found" | Check PATH, re-source shell profile |
| Test data already fixed | Re-run the `setup_broken_*.py` scripts |

### If Something Goes Wrong

1. **Don't panic** - errors during demos are teaching moments
2. **Explain what happened** - transparency builds trust
3. **Show the recovery** - use `--dry-run` to analyze
4. **Have a backup** - keep screenshots of expected output

---

## Workshop-Specific Tips

### Workshop Part 1: Data Issues

**Best demo flow:**
```bash
# 1. Show valid data works
python3 scenarios/data_issues/data_processor.py scenarios/data_issues/sample_data_valid.csv

# 2. Show broken data fails
python3 scenarios/data_issues/data_processor.py scenarios/data_issues/sample_data_broken.csv

# 3. Run with AI recovery (dry-run first)
./ai_pipeline.sh --dry-run scenarios/data_issues/pipeline.txt

# 4. Discuss the suggested fix before applying
```

**Key insight to highlight:**
> "The CSV has columns named `id`, `fullname`, `mail` but the script expects `user_id`, `name`, `email`. The AI mapped these automatically."

### Workshop Part 2: Migrations

**Best demo flow for each part:**

**Part 1 (SQLite → JSON):**
```bash
# Setup
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py

# Show the schema difference
sqlite3 scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db ".tables"
# Shows: inventory, orders, users (but script expects 'products', not 'inventory')

# Run with AI
SOURCE_DB=scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db \
./ai_pipeline.sh --dry-run scenarios/migrations/part1_sqlite_to_json/pipeline.txt
```

**Part 2 (Schema Evolution):**
```bash
# Setup
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py

# Run with AI
SOURCE_DB=scenarios/migrations/part2_schema_evolution/data/app_v1_broken.db \
./ai_pipeline.sh --dry-run scenarios/migrations/part2_schema_evolution/pipeline.txt
```

**Part 3 (Full ETL):**
```bash
# Run with AI
CSV_INPUT=scenarios/migrations/part3_full_etl/data/sales_data_broken.csv \
./ai_pipeline.sh --dry-run scenarios/migrations/part3_full_etl/pipeline.txt
```

---

## Audience Engagement

### Good Questions to Ask

- "Who has been woken up at 3 AM for a pipeline failure?"
- "How long does it typically take to diagnose a schema mismatch?"
- "What would you want the AI to NOT auto-fix?"

### Common Audience Questions (and Answers)

**Q: "Can the AI break things worse?"**
> A: Yes, which is why we have blocklists for dangerous commands and recommend starting with dry-run mode. The AI is a tool, not a replacement for human judgment.

**Q: "What if the AI suggests the wrong fix?"**
> A: It happens. That's why we have max retry limits and audit logging. If the same error occurs after the fix, the pipeline fails rather than looping forever.

**Q: "How much does this cost?"**
> A: Each AI call costs a few cents. With retry limits (default 3), worst case is ~$0.15 per pipeline failure. Compare that to engineer time at 3 AM.

**Q: "Can we use this with [other AI tool]?"**
> A: The architecture is modular. The `ai_recover.sh` script can be adapted to call any CLI-based AI tool.

---

## After the Workshop

### Reset for Next Session

```bash
# Reset all broken test data
python3 scenarios/data_issues/fix_columns.py scenarios/data_issues/sample_data_broken.csv
# Then restore broken state:
cat > scenarios/data_issues/sample_data_broken.csv << 'EOF'
id,fullname,mail,years,created_at
1,Alice Johnson,alice@example.com,28,2023-01-15
2,Bob Smith,bob.smith@company.org,34,2023-02-20
3,Carol Williams,carol.w@email.net,45,2023-03-10
...
EOF

# Or simply re-run setup scripts
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py
```

### Collect Feedback

Key questions to ask:
1. Was the pacing appropriate?
2. Were the examples relevant to your work?
3. What additional scenarios would be useful?
4. Would you use this approach in production?

---

## Troubleshooting Reference

### Bob CLI Issues

```bash
# Check authentication
bob --version

# Test basic functionality
echo "say hello" | bob

# If rate limited, wait and retry
# Error: "exhausted your capacity" → wait 2-3 seconds
```

### Test Data Issues

```bash
# Check current state of broken CSV
head -1 scenarios/data_issues/sample_data_broken.csv
# Should show: id,fullname,mail,years,created_at (broken)
# NOT: user_id,name,email,age,signup_date (fixed)

# Check migration databases
sqlite3 scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db ".tables"
# Should show: inventory (not products)
```

### Log Inspection

```bash
# View latest human-readable log
cat logs/$(ls -t logs/*.log | head -1)

# View audit trail
cat logs/pipeline_audit.jsonl | jq .

# Check what fixes were suggested
grep "FIX:" logs/*.log
```

---

## Quick Reference Card

### Essential Commands

| Action | Command |
|--------|---------|
| Run pipeline | `./ai_pipeline.sh <pipeline.txt>` |
| Dry-run mode | `./ai_pipeline.sh --dry-run <pipeline.txt>` |
| Override source DB | `SOURCE_DB=path/to/db ./ai_pipeline.sh ...` |
| Override CSV input | `CSV_INPUT=path/to/csv ./ai_pipeline.sh ...` |
| Check AI recovery | `./ai_recover.sh --error "..." --command "..."` |

### File Locations

| What | Where |
|------|-------|
| Workshop 1 guide | `WORKSHOP-part1.md` |
| Workshop 2 guide | `WORKSHOP-part2.md` |
| Data issues scenario | `scenarios/data_issues/` |
| Migration scenarios | `scenarios/migrations/part{1,2,3}_*/` |
| Logs | `logs/` |
| Prompt templates | `prompts/` |

---

*Last Updated: 2026-01-28*
