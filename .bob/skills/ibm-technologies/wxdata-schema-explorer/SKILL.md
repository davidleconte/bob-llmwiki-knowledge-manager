---
slug: wxdata-schema-explorer
name: watsonx.data Schema Explorer
description: Catalog browsing, table DDL retrieval, column profiling, and schema context for IBM watsonx.data.
category: product
tags:
  - watsonx.data
  - Schema
  - Data Catalog
  - Metadata
related_modes:
  - watsonx
  - databricks-to-watsonx-data
  - smart-data-platform
  - ibm-knowledge-catalog
---

# watsonx.data Schema Explorer

A skill for navigating IBM watsonx.data catalogs, discovering tables, retrieving DDL, and building schema context for query generation.

## Included capabilities

### Catalog Browsing
- List available catalogs: `GET /wxdata/schema` → catalogs array
- List schemas within a catalog: drill down to namespace level
- List tables within a schema: full table inventory with row counts and last-modified
- Filter by name pattern: wildcard search across catalogs and schemas
- Display catalog hierarchy: catalog → schema → table → column tree

### Table Metadata Retrieval
- Full DDL generation: `CREATE TABLE` statement with column names, types, partitioning, and file format
- Column inventory: name, data type, nullable, comment, and partition key indicator
- Iceberg metadata: snapshot count, table format version, and file count
- Statistics: approximate row count, data size, and last analyzed timestamp
- Table properties: file format (Parquet/ORC/Avro), compression codec, location

### Column Profiling
- Distinct value count via `approx_distinct()` query
- NULL percentage and completeness score
- Min/max values for numeric and date columns
- Top-N most frequent values for categorical columns
- Data type distribution for JSON or mixed-type columns

### Schema Context for NL2SQL
- Build compact schema summaries for injection into SQL generation prompts
- Identify primary key candidates: columns with high cardinality and no NULLs
- Detect foreign key patterns: column name similarity across tables (e.g., `customer_id`)
- Summarise table relationships: join paths inferred from naming conventions
- Format schema context as concise DDL excerpts for token efficiency

### Governance Metadata Integration
- Retrieve IBM Knowledge Catalog tags applied to tables and columns
- Display data classification labels: PII, sensitive, public, restricted
- Show data owner and steward information from catalog metadata
- Link to data lineage: upstream sources for each table

## Usage

Install this skill with:

```bash
bobmodes install-skill wxdata-schema-explorer
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "What tables are available in the `sales` schema? Show me the DDL for the `transactions` table."

Bob will call `GET /wxdata/schema`, display the table list, then retrieve and format the full DDL with column types, partitioning, and Iceberg properties.
