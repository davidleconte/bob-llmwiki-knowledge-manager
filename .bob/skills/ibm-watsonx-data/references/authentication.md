# Authentication & Connection

`WatsonxDataV3` is an IBM Cloud SDK service client (built on `ibm_cloud_sdk_core`).
Three things every session needs: an **authenticator**, the **regional service
URL**, and the **instance id** (`auth_instance_id`) per call (SKILL.md §2).

## Install

```bash
pip install --upgrade ibm-watsonxdata     # Python 3.7+
```

## IAM (IBM Cloud SaaS)

```python
from ibm_watsonxdata.watsonx_data_v3 import WatsonxDataV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

client = WatsonxDataV3(authenticator=IAMAuthenticator("YOUR_API_KEY"))
client.set_service_url("https://eu-de.lakehouse.cloud.ibm.com/lakehouse/api")
```
Generate an API key at https://cloud.ibm.com/iam/apikeys.

## Bearer token / CP4D (software / on-prem)

```python
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
client = WatsonxDataV3(authenticator=BearerTokenAuthenticator("TOKEN"))
client.set_service_url("https://<cpd-host>/lakehouse/api")   # cluster route
```
For Cloud Pak for Data use the CP4D authenticator from `ibm_cloud_sdk_core`
(`CloudPakForDataAuthenticator(username=…, apikey=…/password=…, url=…)`).

## `new_instance` from environment

```python
client = WatsonxDataV3.new_instance(service_name="watsonx_data")
```
Reads the authenticator + URL from environment / `ibm-credentials.env`
(`WATSONX_DATA_AUTH_TYPE`, `WATSONX_DATA_APIKEY`, `WATSONX_DATA_URL`, …). Then still
pass `auth_instance_id=` per call.

## Regions & service URL

`https://<region>.lakehouse.cloud.ibm.com/lakehouse/api` — set the region of your
instance: `us-south`, `eu-de`, `eu-gb`, `jp-tok`, `au-syd`, … The class default URL
(`https://region.lakehouse…`) is a placeholder — **always call `set_service_url`**.

## Instance id (`auth_instance_id`)

Every method takes `auth_instance_id=`: the target instance's **CRN** (preferred)
or **GUID**, e.g.
`crn:v1:bluemix:public:lakehouse:eu-de:a/<account>:<guid>::`. Find it in the
resource's IBM Cloud page (CRN/GUID). Wrong/missing instance id → 404 or wrong
lakehouse.

## Security

Keep API keys/tokens in env vars or a secret store, never in code or chat. Tokens
expire — IAM authenticators refresh automatically; bearer tokens you supply do not.
