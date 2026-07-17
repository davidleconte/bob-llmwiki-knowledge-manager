# AI-Assisted Pipeline Recovery

A self-healing pipeline demonstration that uses IBM Bob CLI to automatically recover from common production errors.

## Quick Start

```bash
# 1. Ensure IBM Bob CLI is installed
# See: https://internal.bob.ibm.com/docs/shell

# 2. Run the demo pipeline (will fail and attempt recovery)
./ai_pipeline.sh scenarios/data_issues/pipeline.txt

# 3. Or run in dry-run mode to see what would happen
./ai_pipeline.sh --dry-run scenarios/data_issues/pipeline.txt
```

## How It Works

1. **Pipeline Execution**: `ai_pipeline.sh` runs commands sequentially
2. **Failure Detection**: Captures exit codes, stdout, and stderr
3. **AI Recovery**: On failure, sends error context to IBM Bob CLI
4. **Fix Application**: Extracts and applies suggested fixes
5. **Retry**: Re-runs the failed step (up to 3 attempts)

## Project Structure

```
ai-pipeline-recovery/
├── ai_pipeline.sh              # Main orchestrator
├── ai_recover.sh               # AI recovery module
├── prompts/                    # Prompt templates by error type
│   ├── data_error.txt
│   ├── import_error.txt
│   ├── permission_error.txt
│   ├── sql_error.txt
│   └── config_error.txt
├── scenarios/
│   ├── data_issues/            # CSV schema mismatch demo
│   │   ├── data_processor.py
│   │   ├── sample_data_valid.csv
│   │   ├── sample_data_broken.csv
│   │   └── pipeline.txt
│   └── migrations/             # Database migration demos
│       ├── part1_sqlite_to_json/
│       ├── part2_schema_evolution/
│       └── part3_full_etl/
├── logs/                       # Execution logs
└── tests/                      # Test scripts
```

## Available Scenarios

### 1. Data Issues (CSV Schema Mismatch)

Basic demo showing recovery from column name mismatches in CSV files.

```bash
./ai_pipeline.sh scenarios/data_issues/pipeline.txt
```

### 2. Migration Scenarios

Three production-realistic database migration demos:

| Scenario | Description | Command |
|----------|-------------|---------|
| **Part 1: SQLite → JSON** | Export relational data to data lake format | See below |
| **Part 2: Schema Evolution** | Migrate V1 → V2 with table/column renames | See below |
| **Part 3: Full ETL** | CSV → SQLite → JSON complete pipeline | See below |

#### Part 1: SQLite → JSON Data Lake

```bash
# Setup databases
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_source_db.py
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py

# Run with broken DB (triggers AI recovery)
SOURCE_DB=scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db \
./ai_pipeline.sh scenarios/migrations/part1_sqlite_to_json/pipeline.txt
```

#### Part 2: Schema Evolution (V1 → V2)

```bash
# Setup databases
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_v1_database.py
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py

# Run with drifted DB (triggers AI recovery)
SOURCE_DB=scenarios/migrations/part2_schema_evolution/data/app_v1_broken.db \
./ai_pipeline.sh scenarios/migrations/part2_schema_evolution/pipeline.txt
```

#### Part 3: Full ETL (CSV → SQLite → JSON)

```bash
# Run with broken CSV (triggers AI recovery)
CSV_INPUT=scenarios/migrations/part3_full_etl/data/sales_data_broken.csv \
./ai_pipeline.sh scenarios/migrations/part3_full_etl/pipeline.txt
```

## Usage

### Run a Pipeline

```bash
./ai_pipeline.sh <pipeline_file>
```

### Pipeline File Format

```
# Comments start with #
step_name: command to execute
another_step: another command
```

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show AI suggestions without applying fixes |
| `--retries N` | Set max retry attempts (default: 3) |
| `--step NAME` | Run a single command with step name |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | 3 | Maximum recovery attempts |
| `DRY_RUN` | false | Preview mode (no changes) |
| `BOB_TIMEOUT` | 60 | AI API timeout in seconds |
| `SOURCE_DB` | (varies) | Override source database path |
| `CSV_INPUT` | (varies) | Override CSV input path |

## Safety Features

- **Blocked Commands**: Dangerous patterns (`rm -rf /`, etc.) are blocked
- **Dry-Run Mode**: Preview fixes before applying
- **Audit Logging**: All recovery actions logged to `logs/`
- **Max Retries**: Prevents infinite recovery loops
- **Backup Files**: AI-suggested fixes create `.bak` backups

## Logs

- Human-readable: `logs/pipeline_YYYYMMDD_HHMMSS.log`
- JSON audit trail: `logs/pipeline_audit.jsonl`

## Workshops

This project includes two hands-on workshops:

| Workshop | File | Duration | Focus |
|----------|------|----------|-------|
| Part 1 | [WORKSHOP.md](./WORKSHOP.md) | 15-20 min | Data issues, schema mismatch |
| Part 2 | [WORKSHOP-part2.md](./WORKSHOP-part2.md) | 20-30 min | Database migrations |

## Requirements

- Bash 4+
- Python 3.8+
- SQLite 3
- [IBM Bob CLI](https://internal.bob.ibm.com/docs/shell)

## License

Internal use only.
