# Engines

Engines are the compute that runs queries and jobs (SKILL.md §4). Five families,
parallel lifecycles. All methods take `auth_instance_id=`; results via
`.get_result()`.

## Families & when to use

| Family | Use for |
|--------|---------|
| **Presto** | Interactive + federated SQL across catalogs/sources |
| **Prestissimo** | High-performance (Velox-based) SQL |
| **Spark** | Batch ETL, analytics, ML; long-running applications |
| **Db2 / Netezza** | Connected IBM engines |
| **other** | Other connected engine types |

## Presto lifecycle

```python
from ibm_watsonxdata.watsonx_data_v3 import EngineDetails

client.create_presto_engine(
    configuration=EngineDetails(node_type="starter", number_of_nodes=1),
    display_name="analytics-presto", origin="native",
    associated_catalogs=["iceberg_data"], description="…", tags=["prod"],
    auth_instance_id=INSTANCE,
)
client.list_presto_engines(auth_instance_id=INSTANCE)
client.get_presto_engine(engine_id="…", auth_instance_id=INSTANCE)
client.update_presto_engine(engine_id="…", body=<EnginePatch>, auth_instance_id=INSTANCE)
client.pause_presto_engine(engine_id="…", auth_instance_id=INSTANCE)
client.resume_presto_engine(engine_id="…", auth_instance_id=INSTANCE)
client.restart_presto_engine(engine_id="…", auth_instance_id=INSTANCE)
client.scale_presto_engine(engine_id="…", coordinator=…, worker=…, auth_instance_id=INSTANCE)
client.update_presto_engine_autoscaling(engine_id="…", … , auth_instance_id=INSTANCE)
client.delete_engine(engine_id="…", auth_instance_id=INSTANCE)   # generic delete
```

### Catalogs on an engine
```python
client.create_presto_engine_catalogs(engine_id="…", catalog_names="iceberg_data,hive_data", auth_instance_id=INSTANCE)
client.list_presto_engine_catalogs(engine_id="…", auth_instance_id=INSTANCE)
client.get_presto_engine_catalog(engine_id="…", catalog_id="…", auth_instance_id=INSTANCE)
client.delete_presto_engine_catalogs(engine_id="…", catalog_names="…", auth_instance_id=INSTANCE)
```
An engine can only query catalogs attached to it.

### Config & explain
```python
client.get_presto_engine_config(engine_id="…", auth_instance_id=INSTANCE)
client.update_presto_engine_config(engine_id="…", … , auth_instance_id=INSTANCE)
client.run_explain_statement(engine_id="…", statement="SELECT …", format="json", type="io", auth_instance_id=INSTANCE)
client.run_explain_analyze_statement(engine_id="…", statement="SELECT …", auth_instance_id=INSTANCE)
```

## Prestissimo

Same surface as Presto with `*_prestissimo_*` names:
`create/get/list/update/delete_prestissimo_engine`, `pause/resume/restart/scale`,
`*_prestissimo_engine_catalogs`, `run_prestissimo_explain_statement` /
`…_explain_analyze_statement`.

## Spark

```python
client.create_spark_engine(... , auth_instance_id=INSTANCE)   # create/get/list/update/delete
client.pause_spark_engine(...); client.resume_spark_engine(...); client.scale_spark_engine(...)
client.list/create/delete_spark_engine_catalogs(...); client.get_spark_engine_catalog(...)
```
### Applications & history server
```python
client.create_spark_engine_application(engine_id="…", application_details=…, auth_instance_id=INSTANCE)
client.list_spark_engine_applications(engine_id="…", auth_instance_id=INSTANCE)
client.get_spark_engine_application_status(engine_id="…", application_id="…", auth_instance_id=INSTANCE)
client.get_spark_engine_application_ui(...); client.delete_spark_engine_application(...)
client.start_spark_engine_history_server(...); client.get_spark_engine_history_server(...)
client.get_spark_engine_history_server_ui(...); client.delete_spark_engine_history_server(...)
```

## Db2 / Netezza / other

```python
client.create_db2_engine(... , auth_instance_id=INSTANCE)     # + list/get/update/delete
client.create_netezza_engine(...)                              # + list/update/delete
client.create_other_engine(...)                               # + list/delete
```

## Notes

- `scale`/`pause`/`resume`/`delete` change **running compute** (cost + availability)
  — confirm before destructive or cost-affecting actions.
- A freshly created engine has no catalogs — attach one before querying.
- Build `configuration`/`body` as the typed model the signature names
  (`EngineDetails`, `*Patch`, …); verify with `help(...)`.
