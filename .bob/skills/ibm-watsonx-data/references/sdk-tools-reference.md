# `ibm-watsonxdata` SDK — Method Catalog

Every public method of `WatsonxDataV3` (SDK 0.8.x), grouped by area. Import:
`from ibm_watsonxdata.watsonx_data_v3 import WatsonxDataV3`. Model objects (e.g.
`EngineDetails`, `BucketDetails`, `DatabaseCatalogPrototype`, `*Patch`) import from
the same module.

## Call pattern

```python
resp = client.<method>(<typed args>, auth_instance_id=INSTANCE)
result = resp.get_result()      # dict payload
status = resp.get_status_code()
```
- Every method accepts `auth_instance_id=` (the instance CRN/GUID).
- Request bodies are **typed model objects** (build the class or `Model.from_dict({...})`).
- `update_*` takes a `*Patch` object (JSON-Merge/Patch — only changed fields).
- Errors raise `ibm_cloud_sdk_core.ApiException` (`.code`, `.message`).

## Storage & database registrations
`create_hdfs_storage` · `list_storage_registrations` · `create_storage_registration` ·
`get_storage_registration` · `delete_storage_registration` · `update_storage_registration` ·
`add_storage_catalog` · `get_storage_object_properties` · `list_storage_registrations_objects` ·
`list_database_registrations` · `create_database_registration` · `add_database_catalog` ·
`get_database` · `delete_database_catalog` · `update_database`

## Engines — Presto
`list_presto_engines` · `create_presto_engine` · `get_presto_engine` · `update_presto_engine` ·
`delete_engine` · `pause_presto_engine` · `resume_presto_engine` · `restart_presto_engine` ·
`scale_presto_engine` · `update_presto_engine_autoscaling` ·
`list_presto_engine_catalogs` · `create_presto_engine_catalogs` · `delete_presto_engine_catalogs` ·
`get_presto_engine_catalog` · `get_presto_engine_config` · `update_presto_engine_config` ·
`run_explain_statement` · `run_explain_analyze_statement`

## Engines — Prestissimo
`list_prestissimo_engines` · `create_prestissimo_engine` · `get_prestissimo_engine` ·
`update_prestissimo_engine` · `delete_prestissimo_engine` · `pause/resume/restart_prestissimo_engine` ·
`scale_prestissimo_engine` · `list/create/delete_prestissimo_engine_catalogs` ·
`get_prestissimo_engine_catalog` · `run_prestissimo_explain_statement` ·
`run_prestissimo_explain_analyze_statement`

## Engines — Spark
`list_spark_engines` · `create_spark_engine` · `get_spark_engine` · `update_spark_engine` ·
`delete_spark_engine` · `pause/resume_spark_engine` · `scale_spark_engine` ·
`list/create/delete_spark_engine_catalogs` · `get_spark_engine_catalog` ·
`list/create_spark_engine_application` · `get_spark_engine_application_status` ·
`delete_spark_engine_application` · `get_spark_engine_application_ui` ·
`get/start/delete_spark_engine_history_server` · `get_spark_engine_history_server_ui`

## Engines — Db2 / Netezza / other
`list/create/get/update/delete_db2_engine` · `list/create/update/delete_netezza_engine` ·
`list/create/delete_other_engine`

## Integrations
`validate_integration` · `list_all_integrations` · `create_integration` · `get_integrations` ·
`delete_integration` · `update_integration`

## Catalogs, schemas, tables, columns
`list_catalogs` · `get_catalog` · `delete_catalog` · `get_catalog_engine_association` ·
`update_sync_catalog` · `register_table` · `load_table` ·
`list_schemas` · `create_schema` · `delete_schema` ·
`list_tables` · `get_table` · `update_table` · `delete_table` · `rollback_table` ·
`list_table_snapshots` · `list_columns` · `create_columns` · `update_column` · `delete_column`

## Ingestion
`list_ingestion_jobs` · `create_ingestion_job` · `get_ingestion_job`

## Milvus & semantic search
`list/create/get/update/delete_milvus_service` · `create_milvus_service_pause/resume/scale` ·
`list_milvus_service_databases` · `list_milvus_database_collections` ·
`list_milvus_database_partitions` · `update_milvus_service_bucket` ·
`list/create/delete_semantic_search_queries` · `delete_semantic_search_queries_by_id`

## SAL (Semantic Automation Layer)
`get/create/update/delete_sal_integration` · `create_sal_integration_enrichment` ·
`list_sal_integration_enrichment_assets` · `get_sal_integration_enrichment_assets_by_id` ·
`get/replace_sal_integration_enrichment_global_settings` ·
`list_sal_integration_enrichment_jobs` · `list_sal_integration_enrichment_job_runs` ·
`get_sal_integration_enrichment_job_run_logs` ·
`get/replace_sal_integration_enrichment_project_settings` ·
`get_sal_integration_glossary_terms` · `create_sal_integration_upload_glossary` ·
`get_sal_integration_upload_glossary_status` · `list_sal_integration_enrichment_mappings` ·
`delete_sal_metadata`

## Access control & data policies
`list_resource_access_policies` · `bulk_update_resource_access_policies` ·
`revoke_resource_access_policies` · `filter_resource_access_policies_on_users_and_usergroups` ·
`list_data_policies` · `create_data_policy` · `get_data_policy` · `replace_data_policy` ·
`update_data_policy` · `delete_data_policy` · `delete_data_policies`

## Model objects (examples)

Constructed via the class or `from_dict`; every model has `.to_dict()`. A sample of
the many `from_dict`-able models: `EngineDetails`, `EngineProperties`,
`AutoScalingConfig`, `BucketDetails`, `Catalog`/`CatalogCollection`,
`Column`/`ColumnPatch`, `DatabaseCatalog`/`DatabaseCatalogPrototype`,
`DatabaseDetails`/`DatabaseDetailsPrototype`, `DatabaseRegistration`/`…Patch`,
`Db2Engine`/`Db2EngineDetails`/`Db2EnginePatch`, `Driver`, `DbConnectionModel`,
`AccessPolicy`/`AccessPolicies`, plus `*Collection` response wrappers.

Verify the exact model a method wants by reading its signature
(`help(WatsonxDataV3.create_presto_engine)`) — pre-release surface drifts.
