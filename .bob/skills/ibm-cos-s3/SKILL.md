---
name: ibm-cos-s3
description: >-
  Work with IBM Cloud Object Storage (COS) — S3-compatible object storage — using
  the `ibm-cos-sdk` Python SDK (`ibm_boto3`, a boto3 fork). Use this whenever the
  user mentions IBM COS, Cloud Object Storage, `ibm_boto3` / `ibm-cos-sdk`, an S3
  bucket/object on IBM Cloud, COS endpoints, HMAC or IAM (oauth) credentials for
  COS, storage classes (Standard/Vault/Cold/Smart Tier/One Rate), archive &
  restore, Immutable Object Storage / retention / object lock, Key Protect (SSE-KP)
  encryption, presigned URLs, or multipart/large-file transfers to COS. Use for
  "create/list/delete a bucket", "upload/download/copy an object", "list objects",
  "generate a presigned URL", "set a lifecycle/archive rule", "restore an archived
  object", "make a bucket immutable", "encrypt with Key Protect", or "connect to
  IBM COS from Python".
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.0.0"
---

# IBM Cloud Object Storage (COS) — S3 with the `ibm-cos-sdk` for Python

Authoritative, end-to-end guide for IBM Cloud Object Storage through the
**`ibm-cos-sdk`** Python SDK (`ibm_boto3` 2.16.x — a fork of `boto3`). It is a
drop-in S3 API with IBM additions (IAM auth, storage classes, archive, Immutable
Object Storage, Key Protect). Grounded in the real SDK and the COS REST API, not
guesswork.

> **Golden rule #1 — auth mode + endpoint are the two things people get wrong.**
> COS supports **two auth modes** and **always needs an explicit regional
> `endpoint_url`**:
> - **IAM (oauth)** — pass `ibm_api_key_id`, `ibm_service_instance_id`,
>   `ibm_auth_endpoint`, **and** `config=Config(signature_version="oauth")`.
>   Omitting the `oauth` signature version is the #1 IAM failure.
> - **HMAC** — pass `aws_access_key_id` + `aws_secret_access_key` (signature v4,
>   the boto3 default; no `oauth` config).
> There is no global default endpoint — set `endpoint_url` to your bucket's region
> (`https://s3.<region>.cloud-object-storage.appdomain.cloud`).
>
> **Golden rule #2 — it's boto3: client vs resource, paginate, stream.** Use the
> low-level **client** or the high-level **resource**; for large objects use the
> managed `upload_file`/`download_file` (auto-multipart) — never read a whole
> object into memory. **List operations paginate** (1000 keys/page) — use a
> paginator, not a single `list_objects_v2` call. IBM-specific methods
> (`put_bucket_protection_configuration`, `restore_object`, SSE-KP params) extend
> the standard S3 surface.

---

## 1. Mental model

| Object | What it is |
|--------|-----------|
| **Service instance** | A provisioned COS instance (CRN / `resource_instance_id`) — the IAM auth scope; required to create/list buckets with IAM |
| **Bucket** | A container, globally unique name, bound to a **region + storage class** at creation (via `LocationConstraint`) — immutable after creation |
| **Object (key)** | A blob + metadata; keys are flat strings (`/` is convention, not real folders) |
| **Endpoint** | Regional URL the client talks to; public / private / direct variants |
| **Storage class** | Cost/access tier: Standard, Vault, Cold Vault, **Smart Tier**, One Rate (set in `LocationConstraint`) |

Two programming interfaces (§ both work, pick per task):
- **Client** — `ibm_boto3.client("s3", …)`: low-level, 1:1 with S3 API calls.
- **Resource** — `ibm_boto3.resource("s3", …)`: object-oriented (`Bucket`, `Object`).

Full method catalog + the client/resource split:
**[references/sdk-tool-reference.md](references/sdk-tool-reference.md)**.

---

## 2. Install & authenticate

```bash
pip install ibm-cos-sdk          # provides ibm_boto3 + ibm_botocore
```

### IAM (recommended)
```python
import ibm_boto3
from ibm_botocore.client import Config

cos = ibm_boto3.client(
    "s3",
    ibm_api_key_id="YOUR_API_KEY",
    ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/…::",
    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    config=Config(signature_version="oauth"),          # REQUIRED for IAM
    endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud",
)
```

### HMAC (S3-style keys)
```python
cos = ibm_boto3.client(
    "s3",
    aws_access_key_id="HMAC_ACCESS_KEY",
    aws_secret_access_key="HMAC_SECRET_KEY",          # signature v4 (default) — no oauth config
    endpoint_url="https://s3.eu-de.cloud-object-storage.appdomain.cloud",
)
```

### Service-credential file
Save a COS **service credential** JSON to `~/.bluemix/cos_credentials` and the SDK
auto-sources it (HMAC keys → signature; API key → bearer, still needs
`Config(signature_version="oauth")`).

- `ibm_service_instance_id` is **required for IAM** `create_bucket`/`list_buckets`
  (it scopes which instance owns the bucket). Object ops don't need it.
- The **resource** interface takes the same kwargs: `ibm_boto3.resource("s3", …)`.

Endpoints, regions, resiliency (regional / cross-region / single-site), and
public/private/direct URLs: **[references/authentication-and-endpoints.md](references/authentication-and-endpoints.md)**.

---

## 3. Buckets

A bucket's **region + storage class are fixed at creation** via
`CreateBucketConfiguration.LocationConstraint` = `"<region>-<class>"`.

```python
cos.create_bucket(
    Bucket="my-bucket",
    CreateBucketConfiguration={"LocationConstraint": "eu-de-smart"},  # Smart Tier in eu-de
)
cos.list_buckets()                       # IAM needs ibm_service_instance_id
cos.head_bucket(Bucket="my-bucket")      # exists / have access?
cos.get_bucket_location(Bucket="my-bucket")
cos.delete_bucket(Bucket="my-bucket")    # must be empty first
```

`LocationConstraint` classes: `standard`, `vault`, `cold` (Cold Vault), `smart`
(Smart Tier), `onerate_active` (One Rate). Resiliency tiers and the full value
list: **[references/storage-classes-and-archive.md](references/storage-classes-and-archive.md)**.

> Bucket names are **globally unique** across all COS. `delete_bucket` requires an
> **empty** bucket — delete/expire objects first. Region/class can't be changed
> later; to "move" a bucket, create a new one and copy.

---

## 4. Objects

```python
cos.put_object(Bucket="b", Key="path/to/file.txt", Body=b"...", ContentType="text/plain")
obj = cos.get_object(Bucket="b", Key="path/to/file.txt")
data = obj["Body"].read()                # streaming body — read in chunks for large objects
cos.head_object(Bucket="b", Key="...")   # metadata/size without the body
cos.copy_object(Bucket="b", Key="dst", CopySource={"Bucket": "b", "Key": "src"})
cos.delete_object(Bucket="b", Key="...")
cos.delete_objects(Bucket="b", Delete={"Objects": [{"Key": "a"}, {"Key": "b"}]})  # up to 1000
```

**Listing paginates (1000/page) — use a paginator:**
```python
for page in cos.get_paginator("list_objects_v2").paginate(Bucket="b", Prefix="logs/"):
    for o in page.get("Contents", []):
        print(o["Key"], o["Size"])
```

Object CRUD detail, the **resource** interface (`Bucket().objects.filter(...)`,
`Object().download_file(...)`), metadata, tagging, and batch delete:
**[references/buckets-and-objects.md](references/buckets-and-objects.md)**.

---

## 5. Large files, transfers & presigned URLs

Use the **managed transfer** methods — they do multipart + retries automatically:
```python
from ibm_boto3.s3.transfer import TransferConfig
cfg = TransferConfig(multipart_threshold=8*1024*1024, multipart_chunksize=8*1024*1024, max_concurrency=10)
cos.upload_file("big.bin", "b", "big.bin", Config=cfg)
cos.download_file("b", "big.bin", "out.bin", Config=cfg)
```

**Presigned URLs** (temporary access without sharing credentials) — **require an
HMAC client.** Verified live: presigning with an IAM (oauth) client raises
`UnsupportedSignatureVersionError: oauth-query`. Build a client with
`aws_access_key_id`/`aws_secret_access_key` to presign.
```python
hmac = ibm_boto3.client("s3", aws_access_key_id=HMAC_ID, aws_secret_access_key=HMAC_SECRET,
                        endpoint_url="https://s3.<region>.cloud-object-storage.appdomain.cloud")
url = hmac.generate_presigned_url("get_object", Params={"Bucket": "b", "Key": "k"}, ExpiresIn=3600)
put = hmac.generate_presigned_url("put_object", Params={"Bucket": "b", "Key": "k"}, ExpiresIn=900)
```

Manual multipart (`create_multipart_upload` → `upload_part` → `complete…/abort…`),
`TransferConfig` tuning, `upload_fileobj`/`download_fileobj`, and
`generate_presigned_post`: **[references/transfers-and-presigned.md](references/transfers-and-presigned.md)**.

> Never `get_object(...)["Body"].read()` a multi-GB object into memory — use
> `download_file`/`download_fileobj` or read the streaming body in chunks. Always
> `abort_multipart_upload` on failure or you pay for orphaned parts.

---

## 6. Storage classes, lifecycle & archive

- **Tiering at creation:** pick the class in `LocationConstraint` (§3). **Smart
  Tier** auto-optimizes cost by access pattern; **One Rate** is flat-rate.
- **Lifecycle / archive:** `put_bucket_lifecycle_configuration` adds rules to
  transition objects to **archive** (`GLACIER` / `ACCELERATED`) after N days or a
  date, and/or expire them. Applies to *new* objects after the rule is set.
- **Restore:** archived objects need `restore_object` to make a temporary copy
  (standard restore up to ~15h; **Accelerated Archive** restores in 2h or 12h).

```python
cos.put_bucket_lifecycle_configuration(Bucket="b", LifecycleConfiguration={"Rules": [{
    "ID": "archive-after-30d", "Status": "Enabled", "Filter": {"Prefix": ""},
    "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]}]})
cos.restore_object(Bucket="b", Key="k",
    RestoreRequest={"Days": 5, "GlacierJobParameters": {"Tier": "Bulk"}})
```

Full rule shapes, archive vs accelerated-archive tiers, and the `LocationConstraint`
value matrix: **[references/storage-classes-and-archive.md](references/storage-classes-and-archive.md)**.

---

## 7. Security, encryption & retention

- **Auth:** IAM (oauth) vs HMAC (§2). Grant least privilege (Reader/Writer/Manager
  IAM roles, or bucket-scoped policies).
- **Encryption:** all COS data is encrypted at rest by default. For
  customer-managed keys use **SSE-KP (Key Protect / HPCS)** — set
  `IBMSSEKPCustomerRootKeyCrn` + `IBMSSEKPEncryptionAlgorithm` on `create_bucket`.
  **SSE-C** (customer-provided key) sets `SSECustomerKey`/`SSECustomerAlgorithm`
  per object.
- **Immutable Object Storage (WORM):** `put_bucket_protection_configuration` sets
  bucket retention (min/default/max days); objects then can't be deleted/modified
  until expiry. Per-object retention and **legal holds** extend this. Meets SEC
  record-retention rules — even admins can't bypass it.

```python
cos.create_bucket(Bucket="secure", CreateBucketConfiguration={"LocationConstraint": "eu-de-standard"},
    IBMSSEKPCustomerRootKeyCrn="crn:v1:bluemix:public:kms:…:key:…", IBMSSEKPEncryptionAlgorithm="AES256")
cos.put_bucket_protection_configuration(Bucket="secure", ProtectionConfiguration={
    "Status": "Retention",
    "MinimumRetention": {"Days": 30}, "DefaultRetention": {"Days": 90}, "MaximumRetention": {"Days": 365}})
```

Full encryption options, retention/legal-hold workflow, and access control:
**[references/security-encryption-retention.md](references/security-encryption-retention.md)**.

> **Retention is irreversible by design** — you cannot shorten an object's
> retention or delete it early. Confirm retention periods with the user before
> enabling protection or uploading with a retention period.

---

## 8. Critical constraints (these cause silent failures — internalize them)

- ✅ **IAM needs `Config(signature_version="oauth")`** + `ibm_api_key_id` +
  `ibm_service_instance_id` + `ibm_auth_endpoint`. Missing the oauth config →
  signature errors.
- ✅ **`endpoint_url` is mandatory and regional** — must match the bucket's region.
  Wrong region → `PermanentRedirect`/timeouts.
- ✅ **`ibm_service_instance_id` required for IAM `create_bucket`/`list_buckets`.**
- ✅ **Bucket region + storage class are fixed at creation** (`LocationConstraint`).
  No in-place change; copy to a new bucket.
- ✅ **List ops cap at 1000 keys/page** — paginate (`get_paginator("list_objects_v2")`).
- ✅ **Stream large objects** — `download_file`/`download_fileobj`, not `Body.read()`.
- ✅ **`delete_bucket` needs an empty bucket**; `delete_objects` batches ≤1000.
- ✅ **Retention/WORM is irreversible** — confirm before enabling.
- ✅ **HMAC = signature v4 (default); IAM = oauth** — don't mix (no oauth config
  with HMAC keys, and vice-versa).

---

## 9. Debugging playbook

| Symptom | Likely cause → fix |
|---------|--------------------|
| `SignatureDoesNotMatch` / 403 on IAM | Missing `Config(signature_version="oauth")` or wrong API key. Add the oauth config. |
| `AccessDenied` | IAM role/policy too low, or HMAC key lacks rights. Grant Writer/Manager or a bucket policy. |
| `PermanentRedirect` / endpoint errors | `endpoint_url` region ≠ bucket region. Point at the bucket's regional endpoint. |
| `create_bucket` 400 `InvalidLocationConstraint` | Bad `<region>-<class>` value. Use a valid class (`standard/vault/cold/smart/onerate_active`) + region. |
| `create_bucket`/`list_buckets` fails on IAM | Missing `ibm_service_instance_id`. Pass the instance CRN. |
| `BucketAlreadyExists` | Names are global. Pick a unique name. |
| `list_objects_v2` returns only 1000 | That's the page cap. Use a paginator / `ContinuationToken`. |
| OOM on download | Read the whole body into memory. Use `download_file`/chunked reads. |
| `delete_bucket` `BucketNotEmpty` | Empty it first (delete/expire all objects, incl. versions/parts). |
| Archived object read fails / `InvalidObjectState` | Object is in archive — `restore_object` first, then read after the restore completes. |
| Can't delete object | Under retention/legal hold — wait for expiry / remove the legal hold (by design). |
| Orphaned multipart charges | A failed upload left parts. `list_multipart_uploads` → `abort_multipart_upload`. |
| `UnsupportedSignatureVersionError: oauth-query` on presign | `generate_presigned_url` needs query signing → use an **HMAC** client, not IAM/oauth (verified). |

Inspect `ibm_botocore.exceptions.ClientError` → `e.response["Error"]["Code"]` and
`["Message"]` for the real cause; diagnose and propose a fix.

---

## 10. References (load on demand)

| File | Contents |
|------|----------|
| [references/authentication-and-endpoints.md](references/authentication-and-endpoints.md) | IAM vs HMAC, `cos_credentials` file, `Config(signature_version="oauth")`, regions, resiliency, public/private/direct endpoint URLs |
| [references/sdk-tool-reference.md](references/sdk-tool-reference.md) | client vs resource, key method catalog, paginators, waiters, `ClientError` handling, `Config`/`TransferConfig` |
| [references/buckets-and-objects.md](references/buckets-and-objects.md) | Bucket ops, object CRUD, listing/pagination, copy, batch delete, metadata/tagging, the resource interface |
| [references/transfers-and-presigned.md](references/transfers-and-presigned.md) | Managed transfers, `TransferConfig`, manual multipart, presigned URL & POST |
| [references/storage-classes-and-archive.md](references/storage-classes-and-archive.md) | `LocationConstraint` value matrix, storage classes, lifecycle rules, archive & restore (incl. Accelerated Archive tiers) |
| [references/security-encryption-retention.md](references/security-encryption-retention.md) | SSE-KP (Key Protect) & SSE-C encryption, Immutable Object Storage / retention / legal hold, access control |

### Canonical external resources (you have internet access — use them)
- **COS Python docs:** https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python
- **API reference:** https://ibm.github.io/ibm-cos-sdk-python  ·  REST: https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-compatibility-api
- **SDK source:** the `ibm-cos-sdk-python` repo (`ibm_boto3`)

Because `ibm_boto3` is a boto3 fork, standard **boto3 S3 docs and patterns apply**
for anything not IBM-specific — but auth, endpoints, storage classes, archive,
protection, and SSE-KP are IBM extensions covered here.
