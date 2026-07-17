# Buckets & Objects

Core CRUD and listing (SKILL.md §3–§4). `cos` = an `ibm_boto3.client("s3", …)`;
`res` = an `ibm_boto3.resource("s3", …)`.

## Buckets

```python
cos.create_bucket(Bucket="my-bucket",
    CreateBucketConfiguration={"LocationConstraint": "eu-de-smart"})   # region+class fixed here
cos.list_buckets()                       # IAM requires ibm_service_instance_id
cos.head_bucket(Bucket="my-bucket")      # 200 if exists & accessible; 404/403 otherwise
cos.get_bucket_location(Bucket="my-bucket")
cos.delete_bucket(Bucket="my-bucket")    # bucket must be EMPTY
```
- Names are **globally unique** across all of COS; lowercase, 3–63 chars,
  DNS-style.
- Region + storage class are set **once** via `LocationConstraint` and cannot
  change — copy to a new bucket to "move".
- Empty a bucket before delete (objects, versions if any, and aborted multipart
  parts).

## Objects — put / get / head / copy / delete

```python
cos.put_object(Bucket="b", Key="docs/readme.txt", Body=b"hello",
               ContentType="text/plain", Metadata={"team": "data"})
r = cos.get_object(Bucket="b", Key="docs/readme.txt")
body = r["Body"].read()                  # StreamingBody — for large objects read in chunks
size = cos.head_object(Bucket="b", Key="docs/readme.txt")["ContentLength"]
cos.copy_object(Bucket="b", Key="docs/readme-copy.txt",
                CopySource={"Bucket": "b", "Key": "docs/readme.txt"})
cos.delete_object(Bucket="b", Key="docs/readme.txt")
```
`Body` accepts bytes or a file-like object. For files prefer `upload_file` /
`download_file` (managed multipart — see transfers-and-presigned.md).

### Streaming a large body without loading it all
```python
r = cos.get_object(Bucket="b", Key="big.csv")
for chunk in r["Body"].iter_chunks(chunk_size=1024*1024):
    process(chunk)
```

## Batch delete (≤1000 keys per call)

```python
cos.delete_objects(Bucket="b", Delete={"Objects": [{"Key": "a"}, {"Key": "b/c"}], "Quiet": True})
```

## Listing — always paginate (1000/page cap)

```python
for page in cos.get_paginator("list_objects_v2").paginate(Bucket="b", Prefix="logs/2026/"):
    for o in page.get("Contents", []):
        print(o["Key"], o["Size"], o["LastModified"])
```
- Use `Delimiter="/"` to get `CommonPrefixes` (folder-like grouping).
- Manual loop: while `page["IsTruncated"]`, pass `ContinuationToken=page["NextContinuationToken"]`.

## Resource interface (ergonomic)

```python
bucket = res.Bucket("b")
for o in bucket.objects.filter(Prefix="logs/"):   # auto-paginates
    print(o.key, o.size)
res.Object("b", "k").upload_file("local.bin")
res.Object("b", "k").download_file("out.bin")
bucket.objects.filter(Prefix="tmp/").delete()      # bulk-delete a prefix
res.Bucket("b").objects.all().delete()             # empty a bucket before delete_bucket
```

## Metadata & tagging

```python
cos.put_object_tagging(Bucket="b", Key="k",
    Tagging={"TagSet": [{"Key": "env", "Value": "prod"}]})
cos.get_object_tagging(Bucket="b", Key="k")
```
Custom metadata goes in `Metadata={...}` at put time (returned by `head_object`
under `Metadata`). Metadata is immutable — to change it, copy the object onto
itself with `MetadataDirective="REPLACE"`.

## Conventions

- Keys are flat strings; `/` is a display convention. `Prefix` + `Delimiter` give
  folder-like browsing.
- There's no atomic rename — `copy_object` then `delete_object`.
- Overwriting a key with `put_object` replaces it (no versioning unless enabled on
  the bucket).
