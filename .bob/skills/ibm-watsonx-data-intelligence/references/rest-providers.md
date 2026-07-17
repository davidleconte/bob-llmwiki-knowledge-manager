# REST Providers — Cloud Pak for Data integration

The providers (`wxdi.dq_validator.provider`) read/write live DQ metadata on IBM
Cloud Pak for Data (SKILL.md §5). Configure once with `ProviderConfig`, then use
each provider. Thread-safe (thread-local sessions).

## ProviderConfig

```python
from wxdi.dq_validator.provider import ProviderConfig
from wxdi.common.auth import AuthConfig, EnvironmentType

# Recommended: AuthConfig for automatic token refresh
cfg = ProviderConfig(
    url="https://<instance>.cloud.ibm.com",
    auth_config=AuthConfig(environment_type=EnvironmentType.IBM_CLOUD, api_key="…"),
    project_id="…",        # or catalog_id
)
token = cfg.auth_token     # calls AuthProvider.get_token() internally

# Alternative: static token (no auto-refresh)
cfg = ProviderConfig(url="…", auth_token="Bearer …", project_id="…")
```
If both `auth_token` and `auth_config` are set, **`auth_config` wins**. Verify the
`AuthConfig` field name against the installed SDK (`environment_type` vs
`environment` differs by version — see `references/authentication.md`).

## Providers

### GlossaryProvider — glossary terms / DQ constraints
```python
from wxdi.dq_validator.provider import GlossaryProvider
g = GlossaryProvider(cfg)
term = g.get_published_artifact_by_id("term-id")
term = g.get_term_by_version_id("version-id")
```

### CamsProvider — a data asset (+ columns) from CAMS
```python
from wxdi.dq_validator.provider import CamsProvider
c = CamsProvider(cfg)
asset = c.get_asset_by_id(asset_id="…", options={"hide_deprecated_response_fields": "false"})
for col in asset.column_info:
    print(col.name, col.data_type)
```

### DQAssetsProvider — list assets (filter + paginate)
```python
from wxdi.dq_validator.provider import DQAssetsProvider
a = DQAssetsProvider(cfg)
a.get_assets(project_id="…", include_children=True, asset_type="table")
a.get_assets(catalog_id="…", limit=100, start_token="next-page-token")
```

### ChecksProvider — create / list DQ checks
```python
from wxdi.dq_validator.provider import ChecksProvider
ch = ChecksProvider(cfg)
check_id = ch.create_check(name="Format Check", native_id="asset-id/column-name",
                           check_type="format", dimension_id="…", project_id="…",
                           parent_id=None)              # returns check id (str)
ch.get_checks(dq_asset_id="…", check_type="format", project_id="…")
```

### DimensionsProvider — resolve a dimension id by name
```python
from wxdi.dq_validator.provider import DimensionsProvider
d = DimensionsProvider(cfg)
dim_id = d.search_dimension("Completeness")   # case-insensitive
```

### IssuesProvider — report DQ issues
```python
from wxdi.dq_validator.provider import IssuesProvider
iss = IssuesProvider(cfg)
issue_id = iss.create_issue(dq_check_id="…", reported_for_id="asset-id",
                            number_of_occurrences=10, number_of_tested_records=100,
                            project_id="…")
iss.create_issues_bulk(payload={"issues":[...], "assets":[...], "existing_checks":[...]},
                       project_id="…", incremental_reporting=False)
iss.update_issue_values(issue_id="…", occurrences=10, tested_records=100, project_id="…")
```

### DQSearchProvider — find a check/asset by native id
```python
from wxdi.dq_validator.provider import DQSearchProvider
s = DQSearchProvider(cfg)
s.search_dq_check(native_id="asset-id/check-id", check_type="format", project_id="…")
s.search_dq_asset(native_id="asset-id/column-name", asset_type="column", project_id="…")
```

## Typical workflow

Resolve the asset (`CamsProvider` / `DQAssetsProvider`) → resolve the dimension id
(`DimensionsProvider`) → create the check (`ChecksProvider`) → run the in-memory
validator (§3/§4) → report occurrences (`IssuesProvider`). See
`examples/dq_workflow_usage.py`.

## Notes

- Always pass `project_id` **or** `catalog_id` consistently.
- Prefer `auth_config=` for long-running jobs so tokens refresh.
- Providers are thread-safe — safe to share `cfg` across threads.
