# Transfers, Multipart & Presigned URLs

Large-file handling and credential-free access (SKILL.md §5).

## Managed transfers (preferred for files)

`upload_file` / `download_file` / `upload_fileobj` / `download_fileobj` handle
multipart, retries, and concurrency automatically — use them instead of
`put_object`/`get_object` for anything large.

```python
from ibm_boto3.s3.transfer import TransferConfig

cfg = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,   # start multipart above 8 MiB
    multipart_chunksize=8 * 1024 * 1024,   # 8 MiB parts
    max_concurrency=10,                     # parallel parts
    use_threads=True,
)
cos.upload_file("big.bin", "b", "key", Config=cfg, ExtraArgs={"ContentType": "application/octet-stream"})
cos.download_file("b", "key", "out.bin", Config=cfg)

# Streams (no temp file):
with open("big.bin", "rb") as f:
    cos.upload_fileobj(f, "b", "key", Config=cfg)
```
Progress callback: pass `Callback=lambda n: ...` (bytes transferred, cumulative).

## Manual multipart (full control)

Use only when you need part-level control; otherwise prefer `upload_file`.

```python
mpu = cos.create_multipart_upload(Bucket="b", Key="big")
upload_id = mpu["UploadId"]
parts = []
for i, chunk in enumerate(chunks, start=1):           # each part ≥5 MiB except the last
    p = cos.upload_part(Bucket="b", Key="big", PartNumber=i, UploadId=upload_id, Body=chunk)
    parts.append({"PartNumber": i, "ETag": p["ETag"]})
cos.complete_multipart_upload(Bucket="b", Key="big", UploadId=upload_id,
                              MultipartUpload={"Parts": parts})
# On any failure:
cos.abort_multipart_upload(Bucket="b", Key="big", UploadId=upload_id)
```

**Clean up orphans** — failed uploads leave billable parts:
```python
for u in cos.list_multipart_uploads(Bucket="b").get("Uploads", []):
    cos.abort_multipart_upload(Bucket="b", Key=u["Key"], UploadId=u["UploadId"])
```
A lifecycle rule with `AbortIncompleteMultipartUpload` can auto-clean these.

## Presigned URLs (temporary, credential-free access)

> **Presigning requires an HMAC client.** Verified live: with an IAM (oauth)
> client, `generate_presigned_url` raises
> `UnsupportedSignatureVersionError: oauth-query` (oauth can't sign query strings).
> Use a client built with `aws_access_key_id`/`aws_secret_access_key`.

```python
# Download link (anyone with the URL can GET until it expires)
url = cos.generate_presigned_url("get_object",
        Params={"Bucket": "b", "Key": "k"}, ExpiresIn=3600)        # seconds
# Upload link (client PUTs directly to COS)
put_url = cos.generate_presigned_url("put_object",
        Params={"Bucket": "b", "Key": "k", "ContentType": "image/png"}, ExpiresIn=900)
```

### Presigned POST (browser form uploads)
```python
post = cos.generate_presigned_post(Bucket="b", Key="uploads/${filename}",
        Fields={"acl": "private"}, Conditions=[{"acl": "private"}], ExpiresIn=600)
# post["url"], post["fields"] -> use as an HTML multipart/form-data POST
```

## Notes

- Presigned URLs require **HMAC** (see callout above); they inherit the signer's
  permissions and are valid until `ExpiresIn` elapses (HMAC v4: up to 7 days).
- Generate the URL with an endpoint reachable by the consumer (public vs
  private/direct).
- For very large objects, tune `multipart_chunksize`/`max_concurrency` to balance
  throughput vs memory (each concurrent part holds a chunk in memory).
