---
slug: wxdata-adhoc-query
name: watsonx.data Ad-hoc Query
description: Natural language to SQL translation, Presto query execution, and streaming CSV export for IBM watsonx.data lakehouse.
category: product
tags:
  - watsonx.data
  - NL2SQL
  - Analytics
  - SQL
related_modes:
  - watsonx
  - databricks
  - databricks-to-watsonx-data
  - smart-data-platform
---

# watsonx.data Ad-hoc Query

A skill for natural language to SQL translation, Presto query execution, and result delivery from IBM watsonx.data.

## Included capabilities

### Natural Language to SQL (NL2SQL)
- Accept business questions in plain English and generate valid Presto SQL
- Handle multi-table joins: infer join keys from schema metadata
- Aggregate queries: GROUP BY, HAVING, window functions, and ranking
- Date/time handling: watsonx.data Presto date functions and interval arithmetic
- Nested subqueries: CTEs and derived tables for complex analytical patterns
- SQL explanation: translate generated SQL back to plain-English for user validation

### Presto SQL Patterns for watsonx.data
- Catalog/schema/table three-part naming: `catalog.schema.table`
- Iceberg-specific syntax: `FOR TIMESTAMP AS OF`, `FOR VERSION AS OF` for time travel
- Partition pruning: WHERE clauses that exploit Iceberg partition columns
- Approximate functions: `approx_distinct()`, `approx_percentile()` for large-scale analytics
- JSON path extraction: `json_extract_scalar()` for semi-structured data fields

### Query Execution Workflow
1. Receive natural language question or SQL draft
2. Retrieve schema context via `GET /wxdata/schema` (or wxdata-schema-explorer skill)
3. Generate Presto SQL with explanation
4. Submit to watsonx.data via `POST /wxdata/query`
5. Stream results back as tabular output
6. Offer CSV export link or downstream chart generation

### Result Presentation
- Display as formatted Markdown tables for < 100 rows
- Trigger CSV streaming export for large result sets
- Summarise key findings from query results in plain language
- Identify anomalies: unexpected NULLs, extreme values, or zero-row results

### Error Handling
- Parse Presto error messages and suggest fixes: column not found, type mismatch, syntax errors
- Offer query rewrite suggestions when execution fails
- Timeout guidance: suggest partition pruning or LIMIT addition for long-running queries

### Streaming CSV Export
- `GET /wxdata/export?sql=<encoded>&format=csv`
- Include column headers in first row
- Properly escape commas and quotes in string fields
- Report row count on completion

## Usage

Install this skill with:

```bash
bobmodes install-skill wxdata-adhoc-query
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "What were the top 10 products by revenue last quarter, and how does that compare to the same quarter last year?"

Bob will generate the Presto SQL with a year-over-year comparison using CTEs, execute it, and present the results with a plain-language summary.
