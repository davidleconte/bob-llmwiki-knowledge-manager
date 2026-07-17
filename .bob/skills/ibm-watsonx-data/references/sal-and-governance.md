# SAL Enrichment, Glossary & Governance

Two areas (SKILL.md §7–§8): the **Semantic Automation Layer** (metadata enrichment
+ glossary) and **access/data governance**. All methods take `auth_instance_id=`.

## SAL — Semantic Automation Layer

SAL auto-enriches lakehouse metadata (tags, business terms, descriptions) and runs
enrichment jobs.

```python
client.create_sal_integration(... , auth_instance_id=INSTANCE)     # set up SAL
client.get_sal_integration(...); client.update_sal_integration(...); client.delete_sal_integration(...)

# Enrichment
client.create_sal_integration_enrichment(... , auth_instance_id=INSTANCE)
client.list_sal_integration_enrichment_assets(...)
client.get_sal_integration_enrichment_assets_by_id(...)
client.list_sal_integration_enrichment_jobs(...)
client.list_sal_integration_enrichment_job_runs(...)
client.get_sal_integration_enrichment_job_run_logs(...)
client.list_sal_integration_enrichment_mappings(...)

# Settings (global / project)
client.get_sal_integration_enrichment_global_settings(...)
client.replace_sal_integration_enrichment_global_settings(...)
client.get_sal_integration_enrichment_project_settings(...)
client.replace_sal_integration_enrichment_project_settings(...)

# Glossary
client.get_sal_integration_glossary_terms(...)
client.create_sal_integration_upload_glossary(... , auth_instance_id=INSTANCE)
client.get_sal_integration_upload_glossary_status(...)

client.delete_sal_metadata(...)     # remove SAL-generated metadata
```
Enrichment is asynchronous — kick off with `create_sal_integration_enrichment`,
then poll `list_sal_integration_enrichment_job_runs` /
`get_sal_integration_enrichment_job_run_logs`.

## Access control (resource access policies)

Who can use which engines/catalogs/buckets.

```python
client.list_resource_access_policies(... , auth_instance_id=INSTANCE)
client.bulk_update_resource_access_policies(... , auth_instance_id=INSTANCE)
client.revoke_resource_access_policies(...)
client.filter_resource_access_policies_on_users_and_usergroups(...)
```

## Data policies (row/column governance, RBAC)

```python
client.list_data_policies(... , auth_instance_id=INSTANCE)
client.create_data_policy(... , auth_instance_id=INSTANCE)
client.get_data_policy(policy_name="…", auth_instance_id=INSTANCE)
client.replace_data_policy(...); client.update_data_policy(...)
client.delete_data_policy(...); client.delete_data_policies(...)
```
Build policy bodies as the typed models (`AccessPolicy`, `AccessPolicyBulkUpdate`,
…); read results with `.get_result()`.

## Be conservative

Governance writes change **who can see and query data**. Confirm before:
granting/revoking access, creating/replacing/deleting data policies, or bulk policy
updates. Prefer `list_*` / `get_*` to show the current state before any change.
