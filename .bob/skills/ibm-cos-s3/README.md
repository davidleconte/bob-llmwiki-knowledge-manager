# IBM Cloud Object Storage (COS / S3) — Agent Skill

Equip any skills-compatible Bob AI agent to work with **IBM Cloud Object Storage** — S3-compatible storage — using the **`ibm-cos-sdk`** Python SDK (`ibm_boto3`, a boto3 fork).

> A Python SDK (drop-in S3 with IBM extensions). Built on the verified
> `ibm-cos-sdk-python` source (`ibm_boto3` 2.16.x) and the COS REST API spec.

## What it does

| Capability | Use it for |
|------------|------------|
| **Connect** | IAM (oauth) or HMAC auth, regional endpoints, `cos_credentials` file |
| **Buckets** | Create (region + storage class), list, head, delete |
| **Objects** | Put/get/head/copy/delete, batch delete, paginated listing, streaming |
| **Transfers** | Managed multipart `upload_file`/`download_file`, manual multipart, presigned URLs/POST |
| **Tiering & archive** | Standard/Vault/Cold/Smart Tier/One Rate, lifecycle rules, archive + restore (incl. Accelerated Archive) |
| **Security** | SSE-KP (Key Protect) & SSE-C encryption, Immutable Object Storage / retention / legal hold |

## Why it's reliable

- **Nails the two auth foot-guns.** IAM requires `Config(signature_version="oauth")`
  + `ibm_service_instance_id`; HMAC uses signature v4 — and `endpoint_url` is
  always mandatory and regional. These are the top COS failures, called out up front.
- **It's boto3 — handled correctly.** Client vs resource, paginate lists (1000/page
  cap), stream/`download_file` large objects instead of loading them into memory.
- **IBM extensions covered accurately.** Storage classes via `LocationConstraint`,
  lifecycle/`restore_object` with `GLACIER`/`ACCELERATED` tiers,
  `put_bucket_protection_configuration` (WORM), SSE-KP — grounded in the COS REST API.
- **Safe on irreversible actions.** Retention/WORM and key loss are flagged as
  irreversible, requiring confirmation.

## Install

```bash
cp -r ibm-cos-s3 ~/.bob/skills/
pip install ibm-cos-sdk
```

## Structure

```
ibm-cos-s3/
├── SKILL.md                              # the skill — 10 sections, loaded by the agent
├── README.md                             # this listing
└── references/                           # loaded on demand
    ├── authentication-and-endpoints.md    # IAM/HMAC, cos_credentials, regions, endpoints
    ├── sdk-tool-reference.md              # client vs resource, methods, paginators, errors
    ├── buckets-and-objects.md            # bucket ops + object CRUD + listing + resource API
    ├── transfers-and-presigned.md        # managed/manual multipart + presigned URLs/POST
    ├── storage-classes-and-archive.md    # LocationConstraint matrix, lifecycle, archive/restore
    └── security-encryption-retention.md  # SSE-KP/SSE-C, Immutable Object Storage, access control
```

## Requirements

- Python (current supported releases); `ibm-cos-sdk` (`ibm_boto3` + `ibm_botocore`).
- A COS instance + credentials: an IAM API key (+ instance CRN) or HMAC keys, and
  the bucket's regional endpoint.

## License

Adapted from IBM's `ibm-cos-sdk-python` (Apache License 2.0).
