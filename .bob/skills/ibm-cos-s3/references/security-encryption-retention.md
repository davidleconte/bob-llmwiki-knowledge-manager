# Security, Encryption & Retention

Encryption, Immutable Object Storage (WORM), and access control (SKILL.md §7).

## Access control

- **IAM roles** on the COS instance: Reader (read), Writer (read/write objects),
  Manager (full incl. buckets). Prefer least privilege.
- **Bucket-scoped IAM policies** and **service IDs** for app credentials.
- **HMAC keys** carry the rights of the credential they were created under.
- Public access is off by default; expose data via presigned URLs
  (transfers-and-presigned.md), not by making buckets public.

## Encryption at rest

All COS data is encrypted at rest by default (IBM-managed keys). For
customer-managed keys:

### SSE-KP — Key Protect / Hyper Protect Crypto Services (bucket-level)
Set the root key at **bucket creation**:
```python
cos.create_bucket(Bucket="secure",
    CreateBucketConfiguration={"LocationConstraint": "eu-de-standard"},
    IBMSSEKPCustomerRootKeyCrn="crn:v1:bluemix:public:kms:eu-de:a/<acct>:<instance>:key:<key-id>",
    IBMSSEKPEncryptionAlgorithm="AES256")
```
All objects in the bucket are then wrapped by that root key; rotating/revoking the
key in Key Protect controls access to the data.

### SSE-C — customer-provided key (per request)
```python
key = b"32-byte-key-...."   # you hold the key; COS never stores it
cos.put_object(Bucket="b", Key="k", Body=data,
    SSECustomerAlgorithm="AES256", SSECustomerKey=key)
cos.get_object(Bucket="b", Key="k",
    SSECustomerAlgorithm="AES256", SSECustomerKey=key)   # same key required to read
```
Lose the SSE-C key → the object is unrecoverable.

## Immutable Object Storage (WORM / retention)

Prevents objects from being modified or deleted for a retention period — meets SEC
record-retention rules; **even IBM Cloud admins cannot bypass it.**

### Enable bucket protection
```python
cos.put_bucket_protection_configuration(Bucket="vault-bucket", ProtectionConfiguration={
    "Status": "Retention",                       # enable retention on the bucket
    "MinimumRetention": {"Days": 30},
    "DefaultRetention": {"Days": 90},            # applied when an upload omits a period
    "MaximumRetention": {"Days": 365},
})
cos.get_bucket_protection_configuration(Bucket="vault-bucket")
```

### Per-object retention at upload
Objects in a protected bucket inherit `DefaultRetention`, or set a period/expiry on
the upload (within the bucket's min/max). Supported per-object controls:
- a **retention period** (length) or **retention expiration date**,
- **legal holds** — an object under any legal hold can't be deleted until all
  holds are removed, regardless of retention expiry,
- **permanent / open-ended** retention for indefinite holds.

> Exact method/param names for per-object retention and legal hold are IBM
> extensions and vary by SDK version — verify on your install:
> `[m for m in dir(cos) if "legal" in m or "retention" in m]`, or consult the COS
> Python docs. Don't guess the spelling.

## Be conservative — retention is irreversible

You **cannot** shorten an object's retention or delete it before expiry (that's the
point of WORM). Before enabling protection or uploading with a retention period:
- confirm the retention durations with the user,
- double-check the bucket (a too-long `MaximumRetention` can lock data for years),
- prefer a short test on a throwaway bucket first.

Treat enabling protection, setting retention, and adding legal holds as
**destructive/irreversible** actions requiring explicit confirmation.
