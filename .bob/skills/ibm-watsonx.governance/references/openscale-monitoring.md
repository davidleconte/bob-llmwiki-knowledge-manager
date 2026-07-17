# Production model monitoring — `ibm-watson-openscale`

> **Different SDK.** Continuous monitoring of *deployed* models (drift, fairness,
> quality, explainability, generative-AI quality, payload logging) is **not** in
> `ibm-watsonx-gov`. It's the **watsonx.openscale** capability, driven by the
> **`ibm-watson-openscale`** SDK. Verified live against `ibm-watson-openscale`
> 3.1.7 on a watsonx.governance SaaS instance (Dallas), 2026-06-12 — connected to
> an active datamart with real monitored subscriptions.

```bash
pip install -U ibm-watson-openscale
```

`ibm-watsonx-gov` evaluates a **batch you hand it** (offline / experiment-time).
`ibm-watson-openscale` watches a **running deployment** over time, on a schedule,
against a datamart. Use this when the question is "is my *production* model
drifting / unfair / degrading?", not "score this eval set".

## Connect (`APIClient`)

```python
from ibm_watson_openscale import APIClient
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

client = APIClient(
    authenticator=IAMAuthenticator(apikey="..."),   # IBM Cloud API key (from env!)
    # service_instance_id="<datamart/instance id>", # optional; auto-resolved if 1
)
```
- The same IBM Cloud API key used elsewhere works here; the SDK resolves the
  governance/OpenScale **service_instance_id** automatically when the account has
  one (it equals the datamart id).
- Cloud Pak for Data: use `CloudPakForDataAuthenticator(url, username, apikey/
  password)` and pass `service_url=...`.

## The object model (client accessors)

| Accessor | What it manages |
|---|---|
| `client.data_marts` | the datamart (the store backing all monitoring) — `list/add/get/show/delete` |
| `client.service_providers` | bindings to where models are deployed (watsonx.ai/WML, Azure, SageMaker, custom) |
| `client.subscriptions` | a **monitored deployment** = provider + deployment + payload/feedback schema |
| `client.data_sets` | payload-logging, feedback, and scored data sets per subscription |
| `client.monitor_definitions` | the catalog of monitor *types* (see below) |
| `client.monitor_instances` | a monitor **configured on a subscription** — `add/get/list/run/update/show/delete` |
| `client.integrated_systems` | external integrations (e.g. notification, custom metrics provider) |
| `client.custom_monitor` | user-defined monitors |
| `client.mrm` / `client.mrm_monitoring` | Model Risk Management (campaigns, approvals) |
| `client.ai_metrics`, `client.llm_metrics` | metric computation helpers (incl. GenAI) |

## Standard monitor types (`monitor_definitions`)

Verified present on the live instance:
**Quality** · **AI Service Quality** · **Generative AI Quality** · **Fairness** ·
**Drift** · **Drift v2** · **Explainability** · **Performance** · **Model health** ·
**Data Health** · **Model risk management**.

Each is referenced by a monitor id (e.g. `quality`, `fairness`, `drift`,
`explainability`, `generative_ai_quality`). `monitor_instances.add(...)` attaches
one to a subscription with thresholds and a schedule.

## Typical setup flow

```python
# 1. Datamart (usually already exists)
datamart_id = client.data_marts.list().result.data_marts[0].metadata.id

# 2. Bind where the model is deployed
#    client.service_providers.add(name=..., service_type=..., credentials=...)

# 3. Subscribe a deployment (defines input/output schema, label col, etc.)
#    sub = client.subscriptions.add(data_mart_id=datamart_id,
#                                   service_provider_id=..., deployment_id=...,
#                                   ...).result
#    subscription_id = sub.metadata.id

# 4. Log scoring payloads (so monitors have data)
#    payload_dataset_id = client.data_sets.list(
#        type="payload_logging", target_target_id=subscription_id,
#        target_target_type="subscription").result.data_sets[0].metadata.id
#    client.data_sets.store_records(data_set_id=payload_dataset_id, request_body=[...])

# 5. Configure & run monitors
#    client.monitor_instances.add(data_mart_id=datamart_id,
#        background_mode=False,
#        monitor_definition_id="quality",
#        target=Target(target_type="subscription", target_id=subscription_id),
#        parameters={...}, thresholds=[...])
#    client.monitor_instances.run(monitor_instance_id=..., background_mode=False)
```
(Exact `Target`, `parameters`, and `thresholds` payloads come from
`ibm_watson_openscale.supporting_classes`; check `help()` / the live docs for the
monitor you're configuring — they differ per monitor type.)

## Reading results

```python
client.monitor_instances.show()                      # all monitors + latest status
client.monitor_instances.list().result               # programmatic
client.monitor_instances.get_measurements(...)       # metric time series
```

## When to use which SDK (decision)

| You want to… | SDK |
|---|---|
| Score an eval set / prompt / RAG offline; evaluate an agent run; model-risk report | `ibm-watsonx-gov` (this skill's core) |
| Track models, use cases, lifecycle, factsheets in an inventory | `ibm-aigov-facts-client` ([factsheets-and-usecases.md](factsheets-and-usecases.md)) |
| Continuously monitor a **deployed** model for drift/fairness/quality | `ibm-watson-openscale` (this file) |

These three are the SDK surface of the one watsonx.governance product; large
governance projects use all three together.

> 🔒 API key is a secret — read from env, never hardcode/commit. Production
> payload logging may contain PII; handle the datamart accordingly.
