---
name: watsonx-data
description: >-
  Manage and query the IBM watsonx.data lakehouse with the `ibm-watsonxdata`
  Python SDK (`WatsonxDataV3`). Use this whenever the user mentions watsonx.data
  (the lakehouse, "wxd"), the `ibm-watsonxdata` SDK, a Presto / Prestissimo /
  Spark / Db2 / Netezza engine, lakehouse catalogs / schemas / Iceberg tables /
  columns / snapshots, storage buckets / database registrations, data ingestion
  jobs, Milvus vector services or semantic search on watsonx.data, SAL semantic
  enrichment / glossary, or lakehouse access / data policies (RBAC). Also covers
  the query/data plane (Presto SQL, federated querying, Spark, GraphQL) and
  adjacent tools (`ibm-lh-client`, the Milvus client for RAG). Use for
  "create/scale/pause an engine", "register a bucket / database", "create a
  catalog / schema / table", "run an explain", "ingest data", "set up Milvus /
  vector search", "manage access policies", or "connect to watsonx.data".
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.0.0"
---

# IBM watsonx.data — Lakehouse Management & Query

Authoritative, end-to-end guide for working with the **IBM watsonx.data** lakehouse
through the **`ibm-watsonxdata` Python SDK** (`WatsonxDataV3`, SDK 0.8.x). Grounded
in the real SDK source and the watsonx.data developer labs, not guesswork.

> **Golden rule #1 — it's an IBM Cloud service client: auth + region URL +
> instance, every call.** `WatsonxDataV3` needs an IAM authenticator, the
> **regional** service URL (`https://<region>.lakehouse.cloud.ibm.com/lakehouse/api`),
> and the target **instance id** (the CRN/GUID), passed as `auth_instance_id=` on
> the method (or via headers). Miss the region or the instance id and calls 404 or
> hit the wrong lakehouse.
>
> **Golden rule #2 — build requests with the SDK's typed model objects, and verify
> names against the installed SDK.** Methods take typed prototypes/patches
> (`EngineDetails`, `BucketDetails`, `DatabaseCatalogPrototype`, `*Patch`, …) and
> return a `DetailedResponse` — read `.get_result()`. The SDK is **pre-release
> (0.8.x)** and its surface drifts; when a class/method name is uncertain,
> introspect: `python -c "import ibm_watsonxdata.watsonx_data_v3 as m; print([n for n in dir(m) if 'Engine' in n])"`
> or `help(WatsonxDataV3.create_presto_engine)`.

---

## 1. Mental model — what the lakehouse is made of

watsonx.data separates **compute (engines)** from **storage (object buckets)**,
with an open **catalog → schema → table** metadata layer (Iceberg/Hive) in between,
plus governance, vector, and enrichment services.

| Object | What it is | SDK area |
|--------|-----------|----------|
| **Instance** | A watsonx.data deployment (identified by CRN/GUID = `auth_instance_id`) | service client |
| **Engine** | Compute that runs queries: **Presto**/**Prestissimo** (SQL), **Spark** (batch/ML), **Db2**/**Netezza**/**other** (connected) | `*_engine*` (§4) |
| **Storage** | Object buckets (S3/MinIO/HDFS) holding the data files | `*_storage*` (§5) |
| **Database registration** | An external DB connected as a source | `*_database*` (§5) |
| **Catalog** | Metadata catalog over storage/DB, attached to engines (Iceberg, Hive, …) | `*_catalog*` (§5) |
| **Schema / Table / Column** | The open metadata hierarchy; tables are usually **Iceberg** (snapshots, rollback) | `*_schema/table/column*` (§5) |
| **Ingestion job** | Loads data files into tables | `*_ingestion_job*` (§5) |
| **Milvus service** | Managed vector DB for similarity/semantic search & RAG | `*_milvus*` (§6) |
| **SAL integration** | Semantic Automation Layer — metadata enrichment & glossary | `*_sal_*` (§7) |
| **Access / Data policy** | RBAC and row/column governance | `*_access_policies` / `*_data_polic*` (§8) |

Two planes (§3):
- **Management plane** — this SDK creates/scales/governs resources.
- **Query/data plane** — you *query* through an engine (Presto SQL via JDBC/DBeaver,
  Spark jobs, GraphQL), not through this SDK's management calls.

---

## 2. Install & connect

```bash
pip install --upgrade ibm-watsonxdata        # Python 3.7+
```

> **Version check first (verified the hard way).** PyPI and the reference source
> drift: as of validation, **PyPI ships 0.4.0 → `watsonx_data_v2` / `WatsonxDataV2`**,
> while the v3 surface this skill targets (scaling, storage registration, ingestion,
> SAL, access policies, …) comes from the **0.8.x source → `watsonx_data_v3` /
> `WatsonxDataV3`**. Pick the class that actually installed:
> ```python
> import ibm_watsonxdata; print(ibm_watsonxdata.__version__)   # 0.4.0? -> v2 ; 0.8.x? -> v3
> ```
> If you need a v3-only capability on a v2 install, install the newer SDK from
> source. On **Python 3.12** the legacy `setup.py` build needs `pkg_resources` —
> `pip install "setuptools<81"` then `pip install --no-build-isolation …`.

```python
# v3 (0.8.x source). On a 0.4.0 PyPI install, use watsonx_data_v2 / WatsonxDataV2 instead.
from ibm_watsonxdata.watsonx_data_v3 import WatsonxDataV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

client = WatsonxDataV3(authenticator=IAMAuthenticator("YOUR_API_KEY"))
client.set_service_url("https://eu-de.lakehouse.cloud.ibm.com/lakehouse/api")  # regional!

# Every call targets a specific instance via auth_instance_id (the CRN or GUID):
INSTANCE = "crn:v1:bluemix:public:lakehouse:eu-de:a/<acct>:<guid>::"   # or the GUID
resp = client.list_presto_engines(auth_instance_id=INSTANCE)
print(resp.get_result())
```

- **Regions:** set the URL to your instance's region (`us-south`, `eu-de`,
  `eu-gb`, `jp-tok`, …). The class default URL is a placeholder (`region.lakehouse…`).
- **`new_instance`**: `WatsonxDataV3.new_instance(service_name="watsonx_data")` reads
  the authenticator from the environment (`WATSONX_DATA_*` config / `ibm-credentials.env`).
- **On-prem / CP4D / software**: point `set_service_url(...)` at the cluster's
  watsonx.data API route and use the appropriate authenticator (IAM / bearer / CP4D).
- Every method accepts `auth_instance_id=` — pass the CRN (or GUID) of the target
  instance. Keep API keys in env/secret stores, never in code.

Full auth/region detail: **[references/authentication.md](references/authentication.md)**.
Full tool catalog + the `DetailedResponse`/model pattern:
**[references/sdk-tools-reference.md](references/sdk-tools-reference.md)**.

---

## 3. Two planes — manage vs query

| Plane | What | How |
|-------|------|-----|
| **Management** | Create/scale/pause engines, register buckets/DBs, define catalogs/schemas/tables, set policies, run ingestion | **this SDK** (`WatsonxDataV3`) |
| **Query / data** | Actually read/write data: SQL, federation, analytics, RAG | **through an engine** — Presto SQL (JDBC/DBeaver/`presto-run`), Spark jobs, GraphQL (StepZen), Milvus client |

The SDK has a couple of bridge calls — `run_explain_statement` /
`run_explain_analyze_statement` (Presto) and the Spark application APIs — but
**routine querying is not done through this SDK.** For SQL, connect a client to the
Presto/Prestissimo engine; for analytics/ML, submit Spark applications; for
vector/RAG, use the Milvus client. See **[references/query-and-tools.md](references/query-and-tools.md)**.

---

## 4. Engines

Engines are compute. The SDK manages five families with parallel lifecycles. Full
signatures, scaling, catalogs-per-engine, explain, and Spark apps:
**[references/engines.md](references/engines.md)**.

| Family | Use for | Lifecycle verbs |
|--------|---------|-----------------|
| **Presto** | Interactive/federated SQL | create · get · list · update · delete · pause · resume · restart · scale · autoscaling · config · explain |
| **Prestissimo** | High-perf (Velox) SQL | same as Presto (+ explain) |
| **Spark** | Batch/ETL/ML; applications & history server | create · get · list · update · delete · pause · resume · scale · applications · history-server |
| **Db2 / Netezza / other** | Connected external engines | create · list · get · update · delete |

```python
from ibm_watsonxdata.watsonx_data_v3 import EngineDetails
client.create_presto_engine(
    configuration=EngineDetails(node_type="starter", number_of_nodes=1),
    display_name="analytics-presto", origin="native",
    associated_catalogs=["iceberg_data"], auth_instance_id=INSTANCE,
)
client.scale_presto_engine(engine_id="...", coordinator=..., worker=..., auth_instance_id=INSTANCE)
client.pause_presto_engine(engine_id="...", auth_instance_id=INSTANCE)
```

Attach catalogs to an engine with `create_presto_engine_catalogs` (and the
Prestissimo/Spark equivalents); query plans via `run_explain_statement`.

---

## 5. Storage, catalogs, and the table hierarchy

Data lives in **buckets**; metadata lives in **catalogs → schemas → tables →
columns** (usually Iceberg). Full request shapes + ingestion:
**[references/storage-catalogs-tables.md](references/storage-catalogs-tables.md)**.

```python
# 1) Register storage (bucket) and expose it as a catalog
client.create_storage_registration(... , auth_instance_id=INSTANCE)
client.add_storage_catalog(... , auth_instance_id=INSTANCE)
# 2) Organize metadata
client.create_schema(engine_id=..., catalog_id="iceberg_data",
                     schema_definition=..., auth_instance_id=INSTANCE)
client.create_columns(...); client.list_tables(...); client.get_table(...)
# 3) Iceberg time-travel
client.list_table_snapshots(...); client.rollback_table(...)
# 4) Load data
client.create_ingestion_job(... , auth_instance_id=INSTANCE)
```

- **Buckets vs catalogs:** a storage registration is the physical bucket; a catalog
  is the metadata layer over it, attached to engines.
- **External databases:** `create_database_registration` + `add_database_catalog`
  connect an external DB (Db2, PostgreSQL, Kafka, …) as a federated source.
- **Iceberg tables** support snapshots and `rollback_table` (time-travel); sync
  external catalog metadata with `update_sync_catalog`.
- **Ingestion jobs** load files into tables; track with `list/get_ingestion_job`.

---

## 6. Milvus vector services & semantic search

watsonx.data hosts **Milvus** for vector similarity / RAG. The SDK manages the
service; the **Milvus client** does the actual vector work. Details + RAG pointer:
**[references/milvus-and-search.md](references/milvus-and-search.md)**.

```python
client.create_milvus_service(... , auth_instance_id=INSTANCE)   # create/get/delete/update
client.create_milvus_service_scale(...); client.create_milvus_service_pause(...)
client.list_milvus_service_databases(...); client.list_milvus_database_collections(...)
# Semantic search registry:
client.create_semantic_search_queries(...); client.list_semantic_search_queries(...)
```

For embeddings, collections, and similarity/hybrid search (RAG), connect with the
`pymilvus` client to the managed service (see the reference).

---

## 7. SAL — semantic enrichment & glossary

The **Semantic Automation Layer** enriches lakehouse metadata (auto-tagging,
glossary terms, business context) and runs enrichment jobs. Full method list:
**[references/sal-and-governance.md](references/sal-and-governance.md)**.

```python
client.create_sal_integration(... , auth_instance_id=INSTANCE)
client.create_sal_integration_enrichment(...)                 # kick off enrichment
client.list_sal_integration_enrichment_jobs(...); client.list_sal_integration_enrichment_job_runs(...)
client.get_sal_integration_glossary_terms(...); client.create_sal_integration_upload_glossary(...)
```

---

## 8. Access control & data policies (governance)

Two mechanisms: **resource access policies** (who can use engines/catalogs/buckets)
and **data policies** (row/column-level rules). Full shapes:
**[references/sal-and-governance.md](references/sal-and-governance.md)**.

```python
client.list_resource_access_policies(... , auth_instance_id=INSTANCE)
client.bulk_update_resource_access_policies(...); client.revoke_resource_access_policies(...)
client.create_data_policy(...); client.replace_data_policy(...); client.get_data_policy(...)
```

> **Governance writes are sensitive.** Confirm before granting/revoking access or
> changing data policies — these affect who can see and query data.

---

## 9. Critical constraints (these cause silent failures — internalize them)

- ✅ **Regional service URL** — `https://<region>.lakehouse.cloud.ibm.com/lakehouse/api`;
  the class default is a placeholder. Wrong region = 404/empty.
- ✅ **`auth_instance_id` on every call** — the CRN (or GUID) of the target
  instance. Omitting it targets nothing / errors.
- ✅ **Typed model objects, not raw dicts** — build `EngineDetails`,
  `*Prototype`, `*Patch`, etc. (importable from `ibm_watsonxdata.watsonx_data_v3`);
  or `from_dict({...})`. Read results with `response.get_result()`.
- ✅ **Pre-release SDK (0.8.x)** — verify class/method names against the installed
  module before relying on memory (golden rule #2). The README still says "v2";
  the shipped service class is `WatsonxDataV3`.
- ✅ **Manage ≠ query** — don't try to SELECT through this SDK; query via an engine
  (Presto SQL / Spark / Milvus client).
- ✅ **`update_*` uses JSON-Merge/Patch bodies** (`*Patch` objects) — send only the
  changed fields, not the whole object.
- ✅ **Engine ops are stateful & costly** — `scale`/`pause`/`resume`/`delete` change
  running compute; confirm before destructive or cost-affecting actions.
- ✅ **Governance writes affect access** — confirm before policy changes (§8).

---

## 10. Debugging playbook

| Symptom | Likely cause → fix |
|---------|--------------------|
| 404 / empty list | Wrong regional URL or missing/incorrect `auth_instance_id`. Set the regional URL; pass the instance CRN/GUID. |
| 401/403 | Bad/expired IAM token, or the identity lacks a watsonx.data role / access policy. Re-auth; check access policies (§8). |
| `ImportError` / name not found | Pre-release surface drift. Introspect the installed module (`dir(ibm_watsonxdata.watsonx_data_v3)`); the class is `WatsonxDataV3`. |
| "expected EngineDetails/…" type error | Passed a dict where a model object is required. Build the model class or use `from_dict({...})`. |
| `update_*` clobbers fields | Sent a full object instead of a `*Patch`. Send only changed fields. |
| Engine create succeeds, queries fail | No catalog attached / engine paused. Attach a catalog (`create_*_engine_catalogs`); `resume_*_engine`. |
| Can't SELECT via the SDK | Wrong plane — query through Presto/Spark, not the management SDK (§3). |
| Ingestion job stuck/failed | Check `get_ingestion_job`; verify bucket access, file format, and target table schema. |
| Milvus search fails | The SDK only manages the service — do vector ops with the `pymilvus` client against the running service (§6). |

Read `DetailedResponse.get_result()` and `ApiException` (`.code`, `.message`) for
the real error; diagnose and propose a fix rather than passing the trace through.

---

## 11. References (load on demand)

| File | Contents |
|------|----------|
| [references/authentication.md](references/authentication.md) | IAM/bearer/CP4D auth, regions & service URLs, `auth_instance_id`/CRN, `new_instance` from env |
| [references/sdk-tools-reference.md](references/sdk-tools-reference.md) | Full `WatsonxDataV3` method catalog grouped by area; model objects; `DetailedResponse`/`get_result()` pattern |
| [references/engines.md](references/engines.md) | Presto/Prestissimo/Spark/Db2/Netezza/other: lifecycle, scaling, autoscaling, catalogs, explain, Spark apps & history server |
| [references/storage-catalogs-tables.md](references/storage-catalogs-tables.md) | Buckets/storage, database registrations, catalogs/schemas/tables/columns, Iceberg snapshots/rollback, sync, ingestion |
| [references/milvus-and-search.md](references/milvus-and-search.md) | Milvus service management + `pymilvus` client for vector/RAG; semantic search query registry |
| [references/sal-and-governance.md](references/sal-and-governance.md) | SAL enrichment/glossary; resource access policies + data policies (RBAC) |
| [references/query-and-tools.md](references/query-and-tools.md) | Query/data plane: Presto SQL (JDBC/DBeaver/`presto-run`), federated querying, Spark, GraphQL (StepZen), `ibm-lh-client` |

### Canonical external resources (you have internet access — use them)
- **API docs:** https://cloud.ibm.com/apidocs/watsonxdata
- **SDK source (ground truth for methods/models):** the `ibm-watsonxdata` Python SDK repo (`ibm_watsonxdata/watsonx_data_v3.py`)
- **Developer labs / tutorials:** the `watsonx-data` samples repo (Presto/Spark/federation/Milvus/RAG, access management, GraphQL)

When a method, model, or field is uncertain, **introspect the installed SDK**
(`dir(...)`, `help(...)`) — the surest source of truth for this pre-release SDK.
