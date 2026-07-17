# WORKSHOP Part 2 - Data Migration Scenarios
## AI-Assisted Database Migrations with IBM Bob CLI - 20-30 minutes

This workshop demonstrates **AI-assisted data migrations** — a critical capability for production systems undergoing database upgrades, data lake transitions, or schema evolutions.

**Key idea:** Migrations fail for predictable reasons (schema drift, format changes, missing tables). An AI agent can diagnose these issues and generate the transformation logic needed to complete the migration.

---

## Learning Objectives

By the end of this workshop, you will:
1. Understand common migration failure patterns
2. See how AI analyzes schema mismatches and generates fixes
3. Run three production-realistic migration scenarios
4. Learn best practices for AI-assisted data transformations

---

## Workshop Overview

| Part | Scenario | Description | Duration |
|------|----------|-------------|----------|
| 1 | SQLite → JSON | Export relational data to data lake format | 7 min |
| 2 | Schema Evolution | Migrate V1 → V2 with column/table renames | 7 min |
| 3 | Full ETL | CSV → SQLite → JSON complete pipeline | 7 min |

---

## Prerequisites

```bash
# Verify tools
python3 --version   # 3.8+
sqlite3 --version
bob --version

# Navigate to project
cd ai-pipeline-recovery
```

---

# Part 1: SQLite → JSON Data Lake Migration

## The Scenario

Your company is moving from a traditional SQL database to a data lake architecture. You need to export normalized e-commerce data (users, products, orders) to denormalized JSON files for analytics.

**The problem:** The source database schema has drifted — column names changed, tables renamed.

## Step 1.1: Set Up the Source Database

First, create a "correct" source database:

```bash
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_source_db.py
```

**Expected output:**
```
Database created: .../data/source_ecommerce.db
  Users: 5
  Products: 8
  Orders: 17
```

## Step 1.2: Run the Migration (Success Case)

```bash
python3 scenarios/migrations/part1_sqlite_to_json/scripts/migrate_to_json.py
```

**Expected output:**
```
=== SQLite to JSON Data Lake Migration ===
Schema validation passed
Exported 5 users to .../json_export/users.json
Exported 8 products to .../json_export/products.json
Exported 17 orders to .../json_export/orders_flat.json
```

## Step 1.3: Create the "Broken" Database

Now create a database with schema drift (renamed columns/tables):

```bash
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py
```

**Schema differences introduced:**
| Expected | Actual (Broken) |
|----------|-----------------|
| `products` table | `inventory` table |
| `users.user_id` | `users.id` |
| `users.full_name` | `users.name` |
| `orders.user_id` | `orders.customer_id` |
| Date: `YYYY-MM-DD` | Date: `MM/DD/YYYY` |

## Step 1.4: Run Migration Against Broken DB (Failure)

```bash
SOURCE_DB=scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db \
python3 scenarios/migrations/part1_sqlite_to_json/scripts/migrate_to_json.py
```

**Expected failure:**
```
Schema Validation Error: Missing tables: {'products'}
Available tables: {'users', 'inventory', 'orders'}
```

## Step 1.5: AI-Assisted Recovery

Now run through the self-healing pipeline:

```bash
# Set environment for broken database
export SOURCE_DB=scenarios/migrations/part1_sqlite_to_json/data/source_ecommerce_broken.db

# Run with AI recovery
./ai_pipeline.sh scenarios/migrations/part1_sqlite_to_json/pipeline.txt
```

**Watch the AI:**
1. Detect the schema mismatch
2. Analyze available vs expected tables
3. Suggest SQL views or migration script patches
4. Apply fix and retry

### What Bob CLI Will Suggest

The AI might suggest creating SQL views to map the broken schema:

```sql
-- Create view to map 'inventory' to expected 'products' schema
CREATE VIEW products AS
SELECT
    item_id as product_id,
    item_name as name,
    department as category,
    unit_price as price,
    qty_on_hand as stock_quantity,
    available as is_active
FROM inventory;
```

Or suggest modifying the migration script to handle the alternate column names.

---

# Part 2: Schema Evolution (V1 → V2)

## The Scenario

Your application is upgrading from schema V1 to V2. The changes include:
- Merging `first_name` + `last_name` → `full_name`
- Renaming `addresses` → `customer_addresses`
- Renaming `transactions` → `financial_transactions`
- Changing transaction types: `'credit'/'debit'` → `'CR'/'DR'`

## Step 2.1: Set Up V1 Database

```bash
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_v1_database.py
```

**Expected output:**
```
V1 Database created: .../data/app_v1.db
  Customers: 5
  Addresses: 5
  Transactions: 8
```

## Step 2.2: Run V1 → V2 Migration (Success Case)

```bash
python3 scenarios/migrations/part2_schema_evolution/scripts/migrate_v1_to_v2.py
```

**Expected output:**
```
=== Schema Evolution Migration: V1 → V2 ===
V1 schema validation passed
V2 schema created
Migrated 5 customers
Migrated 5 addresses → customer_addresses
Migrated 8 transactions → financial_transactions
```

## Step 2.3: Create "Drifted" V1 Database

Simulate a production scenario where the V1 database has slight variations:

```bash
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py
```

**Schema drift introduced:**
| Expected V1 | Actual (Drifted) |
|-------------|------------------|
| `customers.customer_id` | `customers.cust_id` |
| `customers.first_name` | `customers.fname` |
| `addresses` table | `addr` table |
| `transactions` table | `txn_history` table |

## Step 2.4: Run Migration Against Drifted DB (Failure)

```bash
SOURCE_DB=scenarios/migrations/part2_schema_evolution/data/app_v1_broken.db \
python3 scenarios/migrations/part2_schema_evolution/scripts/migrate_v1_to_v2.py
```

**Expected failure:**
```
Schema Error: V1 schema validation failed. Missing tables: {'transactions', 'addresses'}
Available tables: {'customers', 'addr', 'txn_history'}
```

## Step 2.5: AI-Assisted Recovery

```bash
export SOURCE_DB=scenarios/migrations/part2_schema_evolution/data/app_v1_broken.db
./ai_pipeline.sh scenarios/migrations/part2_schema_evolution/pipeline.txt
```

**Watch the AI:**
1. Identify missing tables are actually renamed
2. Map `addr` → `addresses`, `txn_history` → `transactions`
3. Generate view creation SQL or script modifications
4. Apply and retry

---

# Part 3: Full ETL Pipeline (CSV → SQLite → JSON)

## The Scenario

You receive daily sales data as CSV files from various vendors. The data needs to be:
1. **Extracted** from CSV
2. **Transformed** and normalized into SQLite
3. **Loaded** as JSON for the data lake

**The problem:** Different vendors use different column names and date formats.

## Step 3.1: View the Expected CSV Format

```bash
head -3 scenarios/migrations/part3_full_etl/data/sales_data.csv
```

**Expected columns:**
```
sale_id,date,customer_name,customer_email,product,category,quantity,unit_price,total,region,sales_rep
```

## Step 3.2: Run ETL Pipeline (Success Case)

```bash
python3 scenarios/migrations/part3_full_etl/scripts/etl_pipeline.py
```

**Expected output:**
```
==================================================
Full ETL Pipeline: CSV → SQLite → JSON
==================================================
EXTRACT: Reading CSV from .../sales_data.csv
  Extracted 15 rows
TRANSFORM: Loading into SQLite
  Created 15 customers
  Created 6 products
  Created 3 sales reps
  Loaded 15 sales records
LOAD: Exporting to JSON
  Exported 15 records to JSON
==================================================
ETL Pipeline Complete!
```

## Step 3.3: View the "Broken" CSV

```bash
head -3 scenarios/migrations/part3_full_etl/data/sales_data_broken.csv
```

**Different column names and date format:**
```
id,sale_date,cust_name,cust_email,item,item_category,qty,price,amount,territory,rep_name
1001,01/15/2024,...
```

| Expected | Actual (Broken) |
|----------|-----------------|
| `sale_id` | `id` |
| `date` | `sale_date` |
| `customer_name` | `cust_name` |
| `product` | `item` |
| `quantity` | `qty` |
| Date: `YYYY-MM-DD` | Date: `MM/DD/YYYY` |

## Step 3.4: Run ETL Against Broken CSV (Failure)

```bash
CSV_INPUT=scenarios/migrations/part3_full_etl/data/sales_data_broken.csv \
python3 scenarios/migrations/part3_full_etl/scripts/etl_pipeline.py
```

**Expected failure:**
```
EXTRACT ERROR: CSV schema validation failed.
Missing columns: {'sale_id', 'date', 'customer_name', 'product', 'quantity', ...}
Found columns: ['id', 'sale_date', 'cust_name', 'cust_email', 'item', ...]
```

## Step 3.5: AI-Assisted Recovery

```bash
export CSV_INPUT=scenarios/migrations/part3_full_etl/data/sales_data_broken.csv
./ai_pipeline.sh scenarios/migrations/part3_full_etl/pipeline.txt
```

**Watch the AI:**
1. Identify column mapping needed
2. Generate sed/awk/Python command to rename headers
3. Handle date format transformation
4. Apply fix and complete the ETL

---

## Key Takeaways

### Common Migration Failure Patterns

| Pattern | Cause | AI Fix Strategy |
|---------|-------|-----------------|
| Missing tables | Table renamed | Create view or modify query |
| Missing columns | Column renamed | Add column mapping |
| Type mismatch | Format changed | Add transformation logic |
| Date format | Different locale | Parse with multiple formats |
| Foreign key | Referenced row deleted | Handle with LEFT JOIN or skip |

### When AI-Assisted Migration Works Best

✅ **Good candidates:**
- Column/table renames (schema drift)
- Date/number format changes
- Encoding issues
- Missing optional fields

⚠️ **Requires human review:**
- Data type changes with potential data loss
- Business logic changes
- Security-sensitive transformations

### Production Best Practices

1. **Always backup** before AI-applied migrations
2. **Dry-run first** to review suggested fixes
3. **Validate output** after migration completes
4. **Log all transformations** for audit trail

---

## Quick Reference

### Part 1: SQLite → JSON
```bash
# Setup
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_source_db.py
python3 scenarios/migrations/part1_sqlite_to_json/scripts/setup_broken_db.py

# Run migration
python3 scenarios/migrations/part1_sqlite_to_json/scripts/migrate_to_json.py

# With AI recovery (broken DB)
SOURCE_DB=.../source_ecommerce_broken.db ./ai_pipeline.sh scenarios/migrations/part1_sqlite_to_json/pipeline.txt
```

### Part 2: Schema Evolution
```bash
# Setup
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_v1_database.py
python3 scenarios/migrations/part2_schema_evolution/scripts/setup_broken_v1.py

# Run migration
python3 scenarios/migrations/part2_schema_evolution/scripts/migrate_v1_to_v2.py

# With AI recovery (drifted DB)
SOURCE_DB=.../app_v1_broken.db ./ai_pipeline.sh scenarios/migrations/part2_schema_evolution/pipeline.txt
```

### Part 3: Full ETL
```bash
# Run ETL
python3 scenarios/migrations/part3_full_etl/scripts/etl_pipeline.py

# With AI recovery (broken CSV)
CSV_INPUT=.../sales_data_broken.csv ./ai_pipeline.sh scenarios/migrations/part3_full_etl/pipeline.txt
```

---

## Next Steps (you can explore on your own)

1. **Combine scenarios**: Chain Part 3 output into Part 1 input
2. **Add validation**: Post-migration data quality checks
3. **Incremental migration**: Handle delta/CDC patterns
4. **Rollback support**: AI-generated rollback scripts

---

## Resources

- [IBM Bob CLI Documentation](https://internal.bob.ibm.com/docs/shell)
- [Workshop Part 1: Data Issues](./WORKSHOP.md)
- [Project README](./README.md)

---

*Workshop created for AI Engineers and Developers exploring AI-assisted data migration patterns.*
