# Authentication & Endpoints

Two auth modes, and a mandatory regional endpoint (SKILL.md §2).

## Install

```bash
pip install ibm-cos-sdk        # provides ibm_boto3 (resource/transfer) + ibm_botocore (core)
```

## IAM (oauth) — recommended

```python
import ibm_boto3
from ibm_botocore.client import Config

cos = ibm_boto3.client("s3",
    ibm_api_key_id="YOUR_API_KEY",
    ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/<acct>:<guid>::",
    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    config=Config(signature_version="oauth"),        # REQUIRED — without it IAM fails
    endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud",
)
```
- `ibm_api_key_id` — an IAM API key (Writer+ role on the instance).
- `ibm_service_instance_id` — the COS instance CRN. **Required** for IAM
  `create_bucket` / `list_buckets`; optional for object ops.
- `ibm_auth_endpoint` — `https://iam.cloud.ibm.com/identity/token` (public);
  `https://private.iam.cloud.ibm.com/identity/token` for private network.

## HMAC (S3-style keys)

```python
cos = ibm_boto3.client("s3",
    aws_access_key_id="HMAC_ACCESS_KEY_ID",
    aws_secret_access_key="HMAC_SECRET_ACCESS_KEY",  # signature v4 (boto3 default) — no oauth config
    endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud",
)
```
HMAC keys come from a service credential created with
`{"HMAC": true}` (the `cos_hmac_keys` block). Don't pass `Config(signature_version="oauth")`
with HMAC.

## Service-credential file (`~/.bluemix/cos_credentials`)

Save a COS **service credential** JSON there; the SDK auto-sources it unless you
pass explicit credentials. If it contains `cos_hmac_keys` → HMAC signature; else
the `apikey` is used as a bearer token (still requires `Config(signature_version="oauth")`).

## Resource interface

Same kwargs, object-oriented surface:
```python
cos_r = ibm_boto3.resource("s3", ibm_api_key_id=…, ibm_service_instance_id=…,
                           ibm_auth_endpoint=…, config=Config(signature_version="oauth"),
                           endpoint_url=…)
```

## Endpoints

`endpoint_url` is **mandatory** and must match the bucket's region. Pattern:
```
https://s3.<location>.cloud-object-storage.appdomain.cloud
```
Variants per network path:
- **Public:** `s3.<location>.cloud-object-storage.appdomain.cloud`
- **Private** (IBM Cloud private network): `s3.private.<location>.cloud-object-storage.appdomain.cloud`
- **Direct** (high-throughput from IBM Cloud compute): `s3.direct.<location>.cloud-object-storage.appdomain.cloud`

`<location>` depends on **resiliency**:
- **Regional:** `us-south`, `us-east`, `eu-de`, `eu-gb`, `jp-tok`, `jp-osa`,
  `au-syd`, `ca-tor`, `br-sao`, `eu-es`, …
- **Cross-region:** `us`, `eu`, `ap` (e.g. `s3.us.cloud-object-storage.appdomain.cloud`).
- **Single-site:** `ams03`, `mil01`, `che01`, `mon01`, `par01`, `sjc04`, `sng01`, …

The bucket's `LocationConstraint` (`<region>-<class>`) must use a location that
matches the endpoint you connect to. Full list:
https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-endpoints

## Security

Keep API keys / HMAC secrets in env vars or a secret store, never in code or chat.
IAM tokens auto-refresh; HMAC keys are long-lived — rotate periodically.
