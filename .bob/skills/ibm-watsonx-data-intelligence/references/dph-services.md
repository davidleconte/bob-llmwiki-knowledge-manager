# Data Product Hub (DphV1) Reference

Python client for the IBM Data Product Hub API (SKILL.md §6). Import
`from wxdi.dph_services import DphV1`. Requires Python 3.10+ and
`ibm-cloud-sdk-core>=3.16.7`.

## Setup (auth differs from the rest of wxdi)

```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from wxdi.dph_services import DphV1

svc = DphV1(authenticator=IAMAuthenticator("your-api-key"))
svc.set_service_url("https://<dph-instance>")
```

## Lifecycle

```
initialize container → create data product (with a draft) → edit draft
   → publish draft → manage releases (update / retire)
```

### Container
```python
svc.initialize(include=["delivery_methods", "data_product_samples", "domains_multi_industry"])
svc.get_initialize_status()
svc.get_service_id_credentials(); svc.manage_api_keys()
```

### Data products
```python
dp = svc.create_data_product(drafts=[{
    "version": "1.0.0", "name": "Customer Analytics",
    "description": "…",
    "asset": {"id": "asset-123", "container": {"id": "container-456"}},
    "domain": {"id": "domain-789", "name": "Customer Analytics"},
}])
svc.list_data_products(limit=50)
svc.get_data_product(data_product_id="…")
svc.update_data_product(data_product_id="…",
    json_patch_instructions=[{"op": "replace", "path": "/description", "value": "…"}])
svc.delete_data_product(data_product_id="…")
```

### Drafts
```python
svc.create_data_product_draft(data_product_id="…",
    asset={"id": "asset-123", "container": {"id": "container-456"}},
    version="1.1.0", name="Updated Version")
svc.list_data_product_drafts(data_product_id="…")
svc.get_data_product_draft(data_product_id="…", draft_id="…")
svc.update_data_product_draft(data_product_id="…", draft_id="…", json_patch_instructions=[...])
svc.delete_data_product_draft(data_product_id="…", draft_id="…")
svc.publish_data_product_draft(data_product_id="…", draft_id="…")
```

### Contract terms & documents
```python
svc.create_draft_contract_terms_document(data_product_id="…", draft_id="…",
    contract_terms_id="…", type="terms_and_conditions", name="…", url="…")
svc.get_data_product_draft_contract_terms(data_product_id="…", draft_id="…")
svc.update_draft_contract_terms_document(..., document_id="…", json_patch_instructions=[...])
svc.delete_draft_contract_terms_document(..., document_id="…")
```

### Releases
```python
svc.list_data_product_releases(data_product_id="…")
svc.get_data_product_release(data_product_id="…", release_id="…")
svc.update_data_product_release(data_product_id="…", release_id="…", json_patch_instructions=[...])
svc.retire_data_product_release(data_product_id="…", release_id="…")
```

### Domains & subdomains
```python
svc.list_data_product_domains(limit=50)
svc.create_data_product_domain(name="…", description="…", container={"id": "…"})
svc.create_data_product_subdomain(domain_id="…", name="…", description="…")
svc.get_domain(domain_id="…")
svc.update_data_product_domain(domain_id="…", json_patch_instructions=[...])
svc.delete_domain(domain_id="…")
```

### Contract templates
```python
svc.create_contract_template(name="…", description="…", contract_terms_documents=[...])
svc.list_data_product_contract_template(limit=50)
svc.get_contract_template(contract_template_id="…")
svc.update_data_product_contract_template(contract_template_id="…", json_patch_instructions=[...])
svc.delete_data_product_contract_template(contract_template_id="…")
```

### Asset visualization
```python
svc.create_data_asset_visualization(container={"id": "…"},
    assets=[{"id": "asset-1", "container": {"id": "…"}}])
svc.reinitiate_data_asset_visualization(container={"id": "…"}, assets=[...])
```

## Cross-cutting

- **Updates are JSON-Patch:** `json_patch_instructions=[{"op": "replace"|"add"|"remove", "path": "/field", "value": …}]`.
- **Pagination:** `list_*_with_pager(limit=…)` yields pages:
  ```python
  all_products = []
  for page in svc.list_data_products_with_pager(limit=50):
      all_products.extend(page["data_products"])
  ```
- **Custom headers:** pass `headers={...}` to any call.
- **Errors:** `from ibm_cloud_sdk_core import ApiException` → `.code`, `.message`.
- Responses expose `.result` (dict). Models include `DataProduct`,
  `DataProductDraft`, `ContractTerms`, `Domain`.
