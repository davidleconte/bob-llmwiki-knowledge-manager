# AI use cases, inventories & model factsheets — `ibm-aigov-facts-client`

> **Different SDK.** AI use case inventory, factsheets, and model lifecycle are
> **not** in `ibm-watsonx-gov` (that package is evaluation-only). They live in the
> companion **`ibm-aigov-facts-client`** (a.k.a. AI Factsheets). Verified live
> against `ibm-aigov-facts-client` 1.0.105 on watsonx.governance SaaS (Dallas),
> 2026-06-12.

```bash
pip install -U ibm-aigov-facts-client
# heavy transitive deps; also needs setuptools (<81 to silence pkg_resources) and
# IPython at import time in some envs
```

## Connect (`AIGovFactsClient`)

The client **must** be initialized with a **project or space** container — *not* a
catalog/inventory. The inventory (catalog) is then passed per call as `catalog_id`.

```python
from ibm_aigov_facts_client import AIGovFactsClient

client = AIGovFactsClient(
    api_key="...",                       # IBM Cloud API key (read from env!)
    container_type="project",            # "project" or "space" — NOT "catalog"
    container_id="<PROJECT_ID or SPACE_ID>",
    region="dallas",                     # enum NAME, not "us-south": dallas |
                                         # frankfurt | london | tokyo | sydney |
                                         # toronto | aws_mumbai | aws_govcloud
    disable_tracing=True,                # skip experiment autolog for admin tasks
)
```
Cloud Pak for Data: pass `cloud_pak_for_data_configs=CloudPakforDataConfig(url=...,
username=..., api_key=...)` instead of `api_key`/`region`.

> Gotchas learned the hard way: `region` is the enum **name** (`"dallas"`), not the
> service region (`"us-south"`). `container_type="catalog"` raises *"Only project
> and space context supported when initiating client"*.

## Inventories

`client.assets` is the entry point for governance assets.

```python
client.assets.list_inventories()                      # all inventories you can see
client.assets.get_default_inventory_details()
inv = client.assets.create_inventory(name="My Inventory", description="...",
                                     cloud_object_storage_name="<COS instance>")
client.assets.get_inventory("<inventory_id>")
```
An *inventory* is a governed catalog (its id is a `catalog_id`).

## AI use cases (model use cases)

`create_ai_usecase` and `create_model_usecase` are equivalent (use-case = model
entry). Live-verified signatures:

```python
# CREATE
uc = client.assets.create_ai_usecase(
    catalog_id="<inventory_id>",
    name="Telecom GenAI",
    description="GenAI use in Telecom Customer Care",
    status=None,                 # e.g. draft
    risk=None,                   # e.g. "High" / "Medium" / "Low"
    tags=["genai"],
)  # -> AIUsecaseUtilities

# LIST / GET
ucs = client.assets.get_ai_usecases(catalog_id="<inventory_id>",
                                    limit_to_apikey_account=True)   # -> list
uc  = client.assets.get_ai_usecase("<ai_usecase_id>", catalog_id="<inventory_id>")
uc2 = client.assets.get_ai_usecases_by_name(...)
client.assets.list_model_usecases(catalog_id="<inventory_id>")     # pretty table

# REMOVE
client.assets.remove_asset(asset_id="<id>", catalog_id="<inventory_id>")
```

### What you can do with a use case (`AIUsecaseUtilities`)
`get_id`, `get_name`, `get_description`, `get_info`, `to_dict` ·
`get_all_facts`, `get_facts_by_type`, `get_custom_facts`, `set_custom_fact(s)`,
`remove_custom_fact(s)` · `set_attachment_fact`, `list_attachments`,
`remove_attachment`/`remove_all_attachments`, `get_download_URL` ·
**approaches** (lifecycle branches): `create_approach`, `get_approach(es)`,
`remove_approach` · **tracked models**: `relate_models`, `get_tracked_models`,
`get_grc_model(s)` (Governance Console / OpenPages link) · **workspaces**:
`add_workspaces_associations`, `list_all_associated_workspaces`,
`list_associated_workspaces_by_phase`, `remove_workspace_associations` ·
**collaborators**: `set_asset_collaborator`, `remove_asset_collaborator`,
`set_new_owner`.

A use case tracks models across lifecycle **phases** (Develop → Validate →
Operate); each phase associates a project/space *workspace*, and you `relate_models`
to register the actual model/prompt assets being governed.

## Model factsheets

```python
model = client.assets.get_model(model_id="<id>", container_type="space",
                                container_id="<SPACE_ID>")
# factsheet ops on the model object: get/set custom facts, attachments,
# track in a use case, etc.
```
For **external models** (not in watsonx.ai), use
`client.external_model_facts.save_external_model_asset(...)` to register them so
they can be tracked in a use case.

## Custom fact definitions
Define the schema of custom facts a use case/model can carry:
`client.assets.create_custom_facts_definitions(...)`,
`get_facts_definitions`, `reset_custom_facts_definitions`.

## Verified live example (what this looked like on a real instance)
- Connected with `container_type="project"`, `region="dallas"`.
- `list_inventories()` → *Default Inventory* + *GenAI Risks*.
- `get_ai_usecases(catalog_id="<GenAI Risks>")` → existing *Telecom GenAI*
  (status `draft`, tracked in the *DACH - DS Prod - GenAI* space).
- `create_ai_usecase(...)` → new use case created and confirmed by re-listing.

## How this relates to the rest of the skill
- **Evaluation results** (from `ibm-watsonx-gov`) describe *how good/safe* a model
  is; **factsheets/use cases** (here) record *what models exist, who owns them, and
  where they are in their lifecycle*. They're complementary halves of governance.
- **Production monitoring** of deployed models (drift/fairness/quality) is yet a
  third SDK — see [openscale-monitoring.md](openscale-monitoring.md).
- **Model-risk** PDF reports from `ModelRiskEvaluator` can be synced to the
  Governance Console; use-case `get_grc_model(s)` is the reverse link. See
  [model-risk-and-providers.md](model-risk-and-providers.md).

> 🔒 API key is a secret — read from env, never hardcode/commit.
