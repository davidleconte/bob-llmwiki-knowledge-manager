# Storage, Catalogs, Tables & Ingestion

The data layer: **buckets** (physical) → **catalogs** (metadata) → **schemas →
tables → columns** (open, usually Iceberg), plus **ingestion** (SKILL.md §5). All
methods take `auth_instance_id=`; results via `.get_result()`.

## Storage (buckets)

```python
client.create_storage_registration(... , auth_instance_id=INSTANCE)   # register an object bucket (S3/MinIO)
client.create_hdfs_storage(... , auth_instance_id=INSTANCE)           # HDFS-backed storage
client.list_storage_registrations(auth_instance_id=INSTANCE)
client.get_storage_registration(...); client.update_storage_registration(...); client.delete_storage_registration(...)
client.add_storage_catalog(... , auth_instance_id=INSTANCE)           # expose the bucket as a catalog
client.list_storage_registrations_objects(...); client.get_storage_object_properties(...)
```
A **storage registration** is the physical bucket; `add_storage_catalog` layers an
Iceberg/Hive **catalog** over it so engines can query it.

## Database registrations (external/federated sources)

```python
client.create_database_registration(... , auth_instance_id=INSTANCE)  # connect Db2/PostgreSQL/Kafka/…
client.add_database_catalog(... , auth_instance_id=INSTANCE)
client.list_database_registrations(...); client.get_database(...); client.update_database(...)
client.delete_database_catalog(...)
```
Use these for **federation** — query an external DB through a Presto/Prestissimo
engine without copying data.

## Catalogs

```python
client.list_catalogs(auth_instance_id=INSTANCE)
client.get_catalog(catalog_id="…", auth_instance_id=INSTANCE)
client.get_catalog_engine_association(...)        # which engines see this catalog
client.update_sync_catalog(catalog_id="…", … , auth_instance_id=INSTANCE)   # resync external metadata
client.delete_catalog(...)
```

## Schemas → tables → columns

```python
client.create_schema(engine_id="…", catalog_id="iceberg_data", schema_definition=…, auth_instance_id=INSTANCE)
client.list_schemas(engine_id="…", catalog_id="…", auth_instance_id=INSTANCE)
client.delete_schema(...)

client.list_tables(catalog_id="…", schema_id="…", engine_id="…", auth_instance_id=INSTANCE)
client.get_table(...); client.update_table(...); client.delete_table(...)
client.register_table(... , auth_instance_id=INSTANCE)   # register an existing table
client.load_table(...)

client.list_columns(...); client.create_columns(...); client.update_column(...); client.delete_column(...)
```
`update_table` / `update_column` take `*Patch` objects (only changed fields).

## Iceberg time-travel

```python
client.list_table_snapshots(catalog_id="…", schema_id="…", table_id="…", engine_id="…", auth_instance_id=INSTANCE)
client.rollback_table(... , snapshot_id="…", auth_instance_id=INSTANCE)
```
Iceberg tables keep snapshots; `rollback_table` reverts to a prior snapshot.

## Ingestion

```python
client.create_ingestion_job(... , auth_instance_id=INSTANCE)   # load files (CSV/Parquet) into a table
client.list_ingestion_jobs(auth_instance_id=INSTANCE)
client.get_ingestion_job(job_id="…", auth_instance_id=INSTANCE)
```
Track status via `get_ingestion_job`. Failures are usually bucket-access, file
format, or target-schema mismatches.

## Integrations

```python
client.validate_integration(...); client.create_integration(...); client.list_all_integrations(...)
client.get_integrations(...); client.update_integration(...); client.delete_integration(...)
```
Used to wire watsonx.data to adjacent services (e.g. governance/metadata
integrations); `validate_integration` first to check config.

## Order of operations

Register storage/DB → add catalog → attach catalog to an engine
(`create_*_engine_catalogs`, see engines.md) → create schema → create/register
tables + columns → ingest. Querying then happens through the engine (query-and-tools.md).
