---
slug: wxdata-report-dashboard
name: watsonx.data Report & Dashboard
description: Chart generation, executive reports, and column tagging for IBM watsonx.data query results.
category: product
tags:
  - watsonx.data
  - Reporting
  - Visualization
  - Data Governance
related_modes:
  - watsonx
  - databricks-to-watsonx-data
  - smart-data-platform
  - jupyter
---

# watsonx.data Report & Dashboard

A skill for transforming watsonx.data query results into charts, executive Markdown reports, and governance-ready column tags.

## Included capabilities

### Chart Generation
- Accept tabular query results and generate interactive HTML charts
- Chart types: bar, line, scatter, pie, histogram, heatmap, and area
- Auto-select chart type based on data shape: time series → line, categorical breakdown → bar, distribution → histogram
- Self-contained HTML output: single file with embedded JavaScript (no CDN dependency)
- Download link generation: `POST /wxdata/chart` → returns chart HTML file path
- Chart customisation: title, axis labels, color scheme, and legend position

### Chart Selection Logic
| Data Pattern | Recommended Chart |
|---|---|
| Time dimension + metric | Line chart (trend over time) |
| Category + single metric | Bar chart (comparison) |
| Two numeric dimensions | Scatter plot (correlation) |
| Part-of-whole proportions | Pie/donut chart |
| Frequency distribution | Histogram |
| Category × category matrix | Heatmap |

### Executive Report Generation
- Accept query results and generate structured Markdown executive summaries
- Report sections: executive summary → key findings → data tables → recommendations
- Plain-language interpretation: translate numbers into business narrative
- Insight generation: identify top/bottom performers, trends, and anomalies
- Download as `.md` file: `POST /wxdata/report` → returns Markdown file
- Audience-appropriate language: technical detail filtered for executive audience

### Report Structure Template
```markdown
# [Report Title]

## Executive Summary
[2–3 sentence high-level finding]

## Key Findings
- Finding 1: [metric] [direction] [magnitude] [context]
- Finding 2: ...

## Data Summary
[Formatted table from query results]

## Recommendations
1. [Actionable recommendation based on finding]
```

### Column Tagging for Data Governance
- Accept a table and column list from schema explorer
- Auto-suggest tags: PII detection (name, email, SSN, DOB patterns), sensitivity classification, domain tags
- Tag output format: JSON array for IBM Knowledge Catalog API import
- `POST /wxdata/tag-columns` → returns tagged column JSON
- Manual override: accept user corrections before committing tags

### Column Tag Categories
- **PII**: PERSON_NAME, EMAIL, PHONE, ADDRESS, SSN, DATE_OF_BIRTH, FINANCIAL_ACCOUNT
- **Sensitivity**: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- **Domain**: CUSTOMER, PRODUCT, FINANCIAL, OPERATIONAL, REFERENCE

## Usage

Install this skill with:

```bash
bobmodes install-skill wxdata-report-dashboard
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Turn the sales query results into a bar chart showing top 10 products, then generate an executive summary report."

Bob will generate a self-contained bar chart HTML file, then produce a Markdown executive summary with plain-language interpretation of the sales data.
