# ODCS Generator & Data Product Recommender

Two standalone modules (SKILL.md §7–§8).

---

# Part A — ODCS Generator

Generate **ODCS v3.1.0** (Open Data Contract Standard) YAML from a catalog asset.
Sources: **Collibra** and **Informatica CDGC**. Only **table/view** assets.

## CLI

```bash
python -m wxdi.odcs_generator.generate_odcs_from_collibra   <asset_id> [-o out.yaml]
python -m wxdi.odcs_generator.generate_odcs_from_informatica <asset_id> [-o out.yaml]
```
Default output: `<asset-name>-odcs.yaml` in the current directory.

Credentials via env vars or flags:
- Collibra: `COLLIBRA_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD` (or `--url`, `-u`, `-p`).
- Informatica: `INFORMATICA_CDGC_URL`, `INFORMATICA_USERNAME`, `INFORMATICA_PASSWORD` (or `--cdgc-url`, `-u`, `-p`).

## Programmatic (Collibra)

```python
from wxdi.odcs_generator import CollibraClient, ODCSGenerator
client = CollibraClient(base_url="https://…collibra.com", username="…", password="…")
odcs = ODCSGenerator(client).generate_odcs("asset_id")
```

## How it works

1. **Auth** — Collibra: basic auth. Informatica: session id → JWT (cached).
2. **Asset metadata** — name, description, domain, type, tags/classifications.
3. **Column discovery** — Collibra via asset *relations*; Informatica via asset
   *hierarchy* (columns fetched concurrently, up to 10 parallel).
4. **Type mapping** — to ODCS logical/physical types (tables below).
5. **Server type** — Informatica auto-detects from resource type; Collibra does
   **not** (manual).
6. **Emit** ODCS v3.1.0 YAML with `⚠️ MANUAL CONFIGURATION REQUIRED` comments.

## Type mapping (Collibra logical → ODCS)

| Collibra | ODCS |
|---|---|
| text | string |
| whole number | integer |
| decimal number | number |
| date time | timestamp |
| true/false | boolean |
| geographical | string |

Physical types carry size/precision/scale: `VARCHAR(255)`, `DECIMAL(10,2)`,
`NUMBER(18,4)`.

## Informatica resource type → ODCS server type

`SqlServer→sqlserver`, `Oracle→oracle`, `PostgreSQL→postgresql`, `MySQL→mysql`,
`Snowflake→snowflake`, `Redshift→redshift`, `BigQuery→bigquery`,
`Databricks→databricks`, `Synapse→synapse`, `DB2→db2`, `Hive→hive`,
`Impala→impala`, `Teradata→custom`.

## Output shape (abridged)

```yaml
id: <asset-id>
kind: DataContract
apiVersion: v3.1.0
domain: <domain>
dataProduct: <product>
version: 1.0.0
name: <contract>
status: active
contractCreatedTs: <iso>
description:
  authoritativeDefinitions:
    - type: collibra-asset | informatica-asset
      url: <source-url>
schema:
  - id: <id>
    name: <table>
    physicalType: table|view
    properties:
      - name: <column>
        logicalType: string|integer|number|...
        physicalType: VARCHAR(255)|DECIMAL(10,2)|...
        required: true|false
        primaryKey: true|false
servers:
  - id: <id>
    server: CONFIGURE_SERVER_HOSTNAME   # ⚠️ fill in
    type: DEFINE_SERVER_TYPE            # ⚠️ Collibra: fill in; Informatica: auto-detected
```

## Must-do / limitations

- **Always review and complete the `servers` block** — catalogs don't store real
  hostnames; never ship the placeholders.
- Quality rules, SLA terms, stakeholder info, and contract metadata
  (dataProduct/version/name) are not extracted — defaults are emitted; edit them.
- Column discovery depends on correct relations (Collibra) / hierarchy
  (Informatica). Validate the YAML against the ODCS v3.1.0 spec before finalizing.

---

# Part B — Data Product Recommender

Analyze **pre-exported** query-log files (CSV/JSON — no DB connection) to rank
high-value tables and table groups as data-product candidates.

## CLI

```bash
python -m wxdi.data_product_recommender.cli \
  --platform snowflake --input-file query_logs.csv \
  --output output --num-recommendations 20 [--min-score 60] [--output-format markdown|json]
```

## Python

```python
from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
from wxdi.data_product_recommender.recommender import DataProductRecommender

rec = DataProductRecommender(SnowflakeQueryParser())   # or Databricks/BigQuery/WatsonxData parser
rec.load_query_logs_from_csv_file("query_logs.csv")
rec.calculate_metrics()
recs = rec.recommend_data_products(num_recommendations=20)
rec.export_recommendations_markdown(recs, "output/recommendations.md")
rec.export_recommendations_json(recs, "output/recommendations.json")
```

Parsers: `SnowflakeQueryParser`, `DatabricksQueryParser`, `BigQueryQueryParser`,
`WatsonxDataQueryParser`.

## Scoring

**Individual table (0–100):** Query Count 37.5% · User Diversity 37.5% · Recency
15% · Consistency 10%.
**Table group (0–100):** Cohesion 30% · Usage 20% · User Reach 15% · Recency 20% ·
Consistency 10% · Size 5%.
**Ratings:** ⭐⭐⭐⭐⭐ 80–100 (implement now) · ⭐⭐⭐⭐ 60–79 · ⭐⭐⭐ 40–59 ·
⭐⭐ 20–39 · ⭐ 0–19 (don't).

## Input requirements & export SQL

Required columns (names normalized by the parser): `query_text`, `user`,
`start_time`.

- **Snowflake:** `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- **Databricks:** `system.query.history` (Unity Catalog)
- **BigQuery:** `INFORMATION_SCHEMA.JOBS_BY_PROJECT`
- **watsonx.data:** `system.runtime.queries` (Presto)

## Notes

- Markdown output = human-readable (tables, stars, query examples); JSON =
  agent-consumable (numeric metrics, rating labels).
- **Query logs are sensitive** (user identities, table names, query text) — handle
  and store securely.
