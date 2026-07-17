# IBM watsonx.data — Agent Skill

Equip any skills-compatible iBob AI agent to manage and query the **IBM watsonx.data** lakehouse with the
**`ibm-watsonxdata` Python SDK** (`WatsonxDataV3`).

> A Python SDK over the IBM Cloud watsonx.data APIs. Built on the verified SDK
> source (`ibm_watsonxdata/watsonx_data_v3.py`, 0.8.x) and the watsonx.data labs.

## What it does

| Capability | Use it for |
|------------|------------|
| **Engines** | Create / scale / pause / govern Presto, Prestissimo, Spark, Db2, Netezza engines; attach catalogs; run explains |
| **Storage & data** | Register buckets & external databases, define catalogs/schemas/Iceberg tables/columns, snapshots & rollback, ingestion |
| **Vector / RAG** | Manage Milvus vector services + semantic search; do vector work with the `pymilvus` client |
| **Enrichment** | SAL semantic enrichment & glossary over lakehouse metadata |
| **Governance** | Resource access policies and row/column data policies (RBAC) |
| **Query plane** | Presto SQL, federated querying, Spark, GraphQL — the right way to actually read data |

## Why it's reliable

- **Auth + region + instance on every call.** The skill makes the three
  non-negotiables explicit: IAM authenticator, **regional** service URL, and the
  `auth_instance_id` (CRN/GUID) — the top cause of 404s.
- **Typed model objects, not raw dicts.** Methods take `EngineDetails`,
  `*Prototype`, `*Patch`, … and return a `DetailedResponse` (`.get_result()`);
  `update_*` is JSON-Patch.
- **Manage vs query.** Clearly separates the management SDK from the data plane
  (Presto/Spark/Milvus) so you don't try to SELECT through the management API.
- **Pre-release discipline.** The SDK is 0.8.x and drifts (the README even says
  "v2" while the class is `WatsonxDataV3`) — the skill says to introspect the
  installed module when a name is uncertain.

## Install

```bash
cp -r watsonx-data ~/.bob/skills/
pip install --upgrade ibm-watsonxdata     # Python 3.7+
```

## Structure

```
watsonx-data/
├── SKILL.md                              # the skill — 11 sections, loaded by the agent
├── README.md                             # this listing
└── references/                           # loaded on demand
    ├── authentication.md                  # IAM/bearer/CP4D, regions, instance id
    ├── sdk-tools-reference.md             # full WatsonxDataV3 method catalog + models
    ├── engines.md                         # Presto/Prestissimo/Spark/Db2/Netezza lifecycles
    ├── storage-catalogs-tables.md         # buckets, DBs, catalogs/schemas/tables, ingestion
    ├── milvus-and-search.md               # Milvus services + pymilvus client + RAG
    ├── sal-and-governance.md              # SAL enrichment/glossary + access/data policies
    └── query-and-tools.md                 # Presto SQL, federation, Spark, GraphQL, ibm-lh-client
```

## Requirements

- Python 3.7+; `ibm-watsonxdata` (pulls `ibm-cloud-sdk-core`). `pymilvus` for vector work.
- A watsonx.data instance and IAM credentials (or CP4D/bearer for software).

## License

Adapted from IBM's `ibm-watsonxdata` Python SDK (Apache License 2.0).
