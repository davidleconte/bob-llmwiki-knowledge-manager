# Storage Classes, Lifecycle & Archive

How COS tiers cost vs access, and how to archive/restore (SKILL.md §6).

## Storage classes (set at bucket creation)

A bucket's class is chosen once via `LocationConstraint = "<location>-<class>"`:

| Class token | Tier | Best for |
|-------------|------|----------|
| `standard` | Standard | Frequently accessed (hot) data |
| `vault` | Vault | Infrequent access (~monthly) |
| `cold` | Cold Vault | Rarely accessed (cold) |
| `smart` | **Smart Tier** | Mixed/unknown patterns — auto cost-optimization, no retrieval fees |
| `onerate_active` | One Rate | Flat per-GB price incl. operations/egress allowance |

```python
cos.create_bucket(Bucket="hot", CreateBucketConfiguration={"LocationConstraint": "eu-de-standard"})
cos.create_bucket(Bucket="mixed", CreateBucketConfiguration={"LocationConstraint": "us-south-smart"})
```

## `LocationConstraint` value matrix

`<location>` follows the resiliency of the bucket:
- **Regional:** `us-south`, `us-east`, `eu-de`, `eu-gb`, `eu-es`, `jp-tok`,
  `jp-osa`, `au-syd`, `ca-tor`, `br-sao`, …
- **Cross-region:** `us`, `eu`, `ap`.
- **Single-site:** `ams03`, `mil01`, `che01`, `mon01`, `par01`, `sjc04`, `sng01`, …

Combine `<location>-<class>` → e.g. `us-standard` (cross-region Standard),
`eu-de-vault`, `ap-cold`, `jp-tok-smart`, `us-south-onerate_active`. The endpoint
you connect to must match the location's resiliency (see
authentication-and-endpoints.md).

## Lifecycle rules (`put_bucket_lifecycle_configuration`)

Transition objects to **archive** and/or **expire** them automatically. Rules
apply to objects created **after** the rule is set.

```python
cos.put_bucket_lifecycle_configuration(Bucket="b", LifecycleConfiguration={"Rules": [
  {"ID": "archive-30d", "Status": "Enabled", "Filter": {"Prefix": "logs/"},
   "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]},          # standard archive
  {"ID": "accel-archive", "Status": "Enabled", "Filter": {"Prefix": "media/"},
   "Transitions": [{"Days": 0, "StorageClass": "ACCELERATED"}]},        # accelerated archive
  {"ID": "expire-1y", "Status": "Enabled", "Filter": {"Prefix": "tmp/"},
   "Expiration": {"Days": 365}},
  {"ID": "abort-mpu", "Status": "Enabled", "Filter": {"Prefix": ""},
   "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}},
]})
cos.get_bucket_lifecycle_configuration(Bucket="b")
cos.delete_bucket_lifecycle(Bucket="b")
```
- `StorageClass` for archive transitions: **`GLACIER`** (standard archive) or
  **`ACCELERATED`** (Accelerated Archive).
- Use `Date` instead of `Days` for an absolute transition/expiration date.

## Restore an archived object (`restore_object`)

Archived objects can't be read directly (`InvalidObjectState`) — request a
temporary restored copy first.

```python
cos.restore_object(Bucket="b", Key="logs/old.gz", RestoreRequest={
    "Days": 5,                                   # how long the restored copy stays available
    "GlacierJobParameters": {"Tier": "Bulk"},    # restore speed tier
})
# Poll head_object(...)["Restore"] / ["StorageClass"]; read the object once restore completes.
```
Restore times:
- **Standard archive (`GLACIER`):** up to ~15 hours.
- **Accelerated Archive (`ACCELERATED`):** **2 hours or 12 hours** depending on the
  requested tier.

After restore, the object is temporarily readable for `Days`; the archived copy
remains. Re-restore if it lapses.

## Notes

- A lifecycle archive policy affects **new** objects after it's applied, not
  existing ones (re-put or copy to apply).
- Smart Tier vs lifecycle archive: Smart Tier auto-moves data between hot/cool with
  no retrieval fees and no restore step; archive (`GLACIER`/`ACCELERATED`) is
  cheapest but needs `restore_object` before reads.
