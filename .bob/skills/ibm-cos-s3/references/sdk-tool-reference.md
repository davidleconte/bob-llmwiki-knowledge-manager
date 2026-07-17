# `ibm_boto3` SDK — Interfaces, Methods & Patterns

`ibm-cos-sdk` = `ibm_boto3` (high-level: resource, transfers) + `ibm_botocore`
(low-level core). It's a boto3 fork — standard boto3 S3 patterns apply except for
the IBM auth/storage-class/archive/protection/SSE-KP extensions.

## Client vs resource

```python
client = ibm_boto3.client("s3", …)        # low-level, 1:1 with S3 API; returns dicts
resource = ibm_boto3.resource("s3", …)    # high-level OO: Bucket / Object / ObjectSummary
session = ibm_boto3.session.Session(…)    # explicit session; .client(...) / .resource(...)
```
Use **client** for full control and IBM-specific ops; **resource** for ergonomic
iteration and file transfers. Both accept the same auth kwargs (§authentication).

## Key client methods

**Buckets:** `create_bucket`, `list_buckets`, `head_bucket`, `delete_bucket`,
`get_bucket_location`.
**Objects:** `put_object`, `get_object`, `head_object`, `copy_object` (or
`copy` for managed multipart copy), `delete_object`, `delete_objects` (≤1000),
`list_objects_v2`.
**Transfers (managed, auto-multipart):** `upload_file`, `download_file`,
`upload_fileobj`, `download_fileobj`.
**Multipart (manual):** `create_multipart_upload`, `upload_part`,
`complete_multipart_upload`, `abort_multipart_upload`, `list_multipart_uploads`,
`list_parts`.
**Presigned:** `generate_presigned_url`, `generate_presigned_post`.
**Tagging/ACL/metadata:** `put_object_tagging`/`get_object_tagging`,
`get_bucket_acl`/`put_bucket_acl`, `put_bucket_cors`/`get_bucket_cors`.
**IBM extensions:** `put_bucket_lifecycle_configuration` /
`get_bucket_lifecycle_configuration` / `delete_bucket_lifecycle`, `restore_object`,
`put_bucket_protection_configuration` / `get_bucket_protection_configuration`,
SSE-KP params on `create_bucket`. (Verify exact names on your version with
`[m for m in dir(client) if "protection" in m]`.)

## Resource interface

```python
bucket = resource.Bucket("my-bucket")
for obj in bucket.objects.filter(Prefix="logs/"):     # auto-paginates
    print(obj.key, obj.size)
resource.Object("my-bucket", "k").download_file("out.bin")
resource.Object("my-bucket", "k").put(Body=b"...")
bucket.objects.filter(Prefix="tmp/").delete()         # bulk delete a prefix
```

## Pagination (lists cap at 1000/page)

```python
paginator = client.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="b", Prefix="data/", PaginationConfig={"PageSize": 1000}):
    for o in page.get("Contents", []):
        ...
```
Or manual: pass `ContinuationToken=page["NextContinuationToken"]` while
`page["IsTruncated"]`.

## Waiters

```python
client.get_waiter("bucket_exists").wait(Bucket="b")
client.get_waiter("object_exists").wait(Bucket="b", Key="k")
```

## Config

```python
from ibm_botocore.client import Config
Config(signature_version="oauth",          # IAM; omit for HMAC (defaults to v4)
       retries={"max_attempts": 5, "mode": "standard"},
       max_pool_connections=20)
```

## Error handling

```python
from ibm_botocore.exceptions import ClientError
try:
    client.head_object(Bucket="b", Key="missing")
except ClientError as e:
    code = e.response["Error"]["Code"]      # e.g. "404", "NoSuchKey", "AccessDenied"
    msg  = e.response["Error"]["Message"]
```
Common codes: `NoSuchBucket`, `NoSuchKey`, `AccessDenied`, `SignatureDoesNotMatch`,
`PermanentRedirect`, `BucketAlreadyExists`, `BucketNotEmpty`, `InvalidObjectState`
(archived — restore first), `EntityTooLarge`.

## Version

`ibm_boto3.__version__` (this skill verified against 2.16.x). Surface tracks boto3;
when unsure of an op or param, introspect (`dir(client)`, `help(client.put_object)`)
or consult the boto3 S3 docs for non-IBM behavior.
