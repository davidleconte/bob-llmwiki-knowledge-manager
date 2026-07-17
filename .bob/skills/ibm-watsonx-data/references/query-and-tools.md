# Query / Data Plane & Adjacent Tools

The management SDK creates resources; **querying happens through an engine**
(SKILL.md §3). This reference covers the data-plane surfaces and the adjacent
tooling from the watsonx.data labs.

## Presto / Prestissimo SQL

The primary query interface. Connect any Presto/Trino-compatible client to the
engine endpoint:

- **JDBC / DBeaver / BI tools** — use the engine's host/port + your IAM credentials;
  query across all catalogs attached to the engine (federated joins across
  Iceberg, Hive, Db2, PostgreSQL, …).
- **`presto-run`** (developer edition utility) — run a `.sql` file against an engine.
- **Python** — `prestodb`/`trino` client, or `sqlalchemy-trino`.
- **From the SDK**, only *plan* inspection: `run_explain_statement` /
  `run_explain_analyze_statement` (no row results) — see engines.md.

SQL surface: standard ANSI SQL; create schemas/tables (Iceberg by default),
`INSERT`/`CTAS`, federated `JOIN`s across catalogs, `EXPLAIN`.

## Federated querying

watsonx.data's hallmark: register external databases (storage-catalogs-tables.md)
and query them **in place** through Presto — join lakehouse Iceberg tables with a
PostgreSQL/Db2 table in one statement, no copy.

## Spark (analytics & ML)

For ETL/analytics/ML, submit **Spark applications** via the SDK
(`create_spark_engine_application`, see engines.md) or run external Spark against
watsonx.data catalogs. Use for large transforms, ML feature pipelines, and writing
Iceberg tables. The labs include external-Spark and Databricks integration
examples.

## GraphQL (StepZen)

watsonx.data can expose data as a **GraphQL API** (powered by StepZen) for app
developers — a read API over lakehouse tables without writing SQL in the app layer.
See the labs `GraphQL.md`.

## Vector / RAG (Milvus)

Similarity/semantic search and RAG use the managed **Milvus** service via the
`pymilvus` client — see milvus-and-search.md.

## `ibm-lh-client` and developer edition utilities

- **`ibm-lh-client`** — CLI utilities to administer a watsonx.data instance
  (buckets, catalogs, presto-run, etc.), useful for scripting outside Python.
- **Developer Edition** — a local containerized watsonx.data (Presto + MinIO S3 +
  PostgreSQL) for offline iteration; the TechXchange labs (`tx3509-labs/`) walk
  through catalogs/schemas/tables, DBeaver, federation, Spark, GraphQL, and RBAC.

## Which surface for what

| Goal | Use |
|------|-----|
| Create/scale/govern resources | `WatsonxDataV3` SDK (this skill) |
| Interactive / federated SQL | Presto/Prestissimo client (JDBC/DBeaver/`prestodb`) |
| Inspect a query plan | `run_explain_statement` (SDK) |
| Batch ETL / ML | Spark applications |
| Vector search / RAG | `pymilvus` client against the Milvus service |
| GraphQL data API | StepZen-powered GraphQL endpoint |
| CLI administration | `ibm-lh-client` |
