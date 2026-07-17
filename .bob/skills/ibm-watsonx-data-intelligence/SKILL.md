---
name: watsonx-data-intelligence
description: >-
  Use the IBM watsonx.data intelligence Python SDK (`wxdi`, package
  `data-intelligence-sdk`) for data-quality validation, data products, data
  contracts, and recommendations. Use this whenever the user mentions
  watsonx.data intelligence, watsonx DI intelligence, the `wxdi` SDK, data
  quality / DQ validation, validating records / Pandas / PySpark DataFrames,
  validation checks (length, valid values, comparison, case, completeness,
  range, regex, format, datatype) or CEL expressions, data quality dimensions,
  IBM Data Product Hub (DPH) / data products / drafts / releases / contract
  terms / domains, generating an ODCS / Open Data Contract Standard file from
  Collibra or Informatica, recommending data products from query logs, or the
  CAMS / glossary / issues / DQ-checks REST providers. Covers SDK install,
  multi-environment authentication, the validation framework, DataFrame
  integration, the REST providers, the Data Product Hub client, ODCS generation,
  and the data-product recommender.
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.0.0"
---

# IBM watsonx.data intelligence — DQ · Data Products · Contracts · Recommendations

Authoritative, end-to-end guide for the **IBM watsonx.data intelligence SDK**
(`wxdi`, package `data-intelligence-sdk`, 2.1.x). This is a **Python SDK**, not an
MCP/CLI service — you help by writing correct `wxdi` code across its four modules.
Grounded in the real SDK source and docs, not guesswork.

> **Golden rule #1 — define the asset metadata once, exactly.** Validation hangs
> off an `AssetMetadata` (table name + typed `ColumnMetadata`). **Column names are
> case-sensitive everywhere** — in rules, in `ValidValuesCheck`, and especially in
> CEL expressions (`salary` ≠ `Salary`). A name mismatch silently validates the
> wrong column or errors at runtime. Keep one metadata definition and reuse it for
> array, Pandas, and Spark validation.
>
> **Golden rule #2 — verify identifiers against the installed SDK, don't trust
> memory.** Class names, enum members, and constructor field names (e.g. the
> `AuthConfig` signature, provider method names) have evolved across versions.
> When unsure, introspect: `python -c "import wxdi.dq_validator as m; print(dir(m))"`,
> `help(wxdi.dq_validator.checks.LengthCheck)`, or read the module's `__init__`.
> Treat code in this skill as the *pattern*; confirm exact symbols live.

---

## 1. Mental model — four modules + shared auth

`wxdi` is modular. One shared auth layer; four independent capability modules.

| Module | Import root | What it does |
|--------|------------|--------------|
| **Common / Auth** | `wxdi.common.auth` | Bearer-token auth across IBM Cloud, AWS (MCSP), Gov Cloud, on-prem |
| **DQ Validator** | `wxdi.dq_validator` | In-memory data-quality validation: 9 checks + CEL, DQ dimensions, results; array / Pandas / PySpark |
| **DPH Services** | `wxdi.dph_services` | Python client for the IBM **Data Product Hub** API (data products, drafts, releases, contract terms, domains, templates) |
| **ODCS Generator** | `wxdi.odcs_generator` | Generate **ODCS v3.1.0** data-contract YAML from Collibra / Informatica catalogs |
| **Data Product Recommender** | `wxdi.data_product_recommender` | Analyze query logs to rank high-value tables / groupings as data products |

The DQ Validator also ships **REST providers** (`wxdi.dq_validator.provider`) that
read/write live metadata in IBM Cloud Pak for Data (glossary terms, CAMS assets,
DQ checks/dimensions/issues). These connect the in-memory validator to the
platform (§5).

Route the user's request:

| If the user wants to… | Go to | Reference |
|------------------------|-------|-----------|
| Validate records / DataFrames against rules | §3 DQ, §4 DataFrames | `references/dq-checks-reference.md`, `references/dataframe-integration.md` |
| Write custom / cross-column rules | §3 (CEL) | `references/cel-expressions.md` |
| Read/write platform DQ metadata (glossary, CAMS, checks, issues) | §5 Providers | `references/rest-providers.md` |
| Manage data products in Data Product Hub | §6 DPH | `references/dph-services.md` |
| Generate a data contract (ODCS) from a catalog | §7 ODCS | `references/odcs-and-recommender.md` |
| Find candidate data products from query logs | §8 Recommender | `references/odcs-and-recommender.md` |

---

## 2. Install & authenticate

**Install** (Python 3.8–3.12; core deps `pydantic>=2.12`, `requests`, `regex`):
```bash
pip install data-intelligence-sdk
# extras: ".[pandas]"  ".[spark]"  ".[dataframes]"  ".[all]"   (DataFrame support)
# CEL rules also need:  pip install "cel-python>=0.5.0"
```
The import root is `wxdi`. Confirm: `python -c "import wxdi; print(wxdi.__version__)"`.

**Authentication** — the SDK supports four environments. Full matrix and the
on-prem/Gov specifics: **[references/authentication.md](references/authentication.md)**.

| Environment | `EnvironmentType` | Credentials |
|-------------|-------------------|-------------|
| IBM Cloud (standard) | `IBM_CLOUD` | API key |
| AWS Cloud (MCSP) | `AWS_CLOUD` | API key |
| IBM Government Cloud | `GOV_CLOUD` | API key |
| On-Premises (CP4D) | `ON_PREM` | user id + password |

```python
from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType
# AuthConfig and EnvironmentType are also re-exported from wxdi.dq_validator.

config = AuthConfig(
    environment_type=EnvironmentType.IBM_CLOUD,        # first positional arg
    url="https://iam.cloud.ibm.com/identity/token",
    api_key="…",
)
token = AuthProvider(config).get_token()               # -> JWT string (prefix with "Bearer " for headers)
```

> **Verified against `wxdi` 2.1.0** (live): the token entry point is
> **`AuthProvider(config).get_token()`** — there is **no `TokenGenerator`** in this
> version (the README's quick-start is stale). `AuthConfig`'s first parameter is
> **`environment_type=`** (not `environment=`); `url` is optional. This is exactly
> the kind of drift golden rule #2 guards against — if you're on a different
> version, re-introspect `wxdi.common.auth` (`inspect.signature(AuthConfig.__init__)`).
> For providers, prefer passing `auth_config=` so tokens refresh automatically (§5).

**DPH Services authenticate differently** — they use the IBM Cloud SDK core
authenticator, not `wxdi` auth:
```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from wxdi.dph_services import DphV1
svc = DphV1(authenticator=IAMAuthenticator("…")); svc.set_service_url("https://<dph-instance>")
```

> Keep API keys/passwords in env vars or a secret store — never in code or chat.

---

## 3. DQ Validator — the validation framework

Three steps: **define metadata → build a validator with rules → validate**. Full
per-check parameter reference: **[references/dq-checks-reference.md](references/dq-checks-reference.md)**.

```python
from wxdi.dq_validator import (
    AssetMetadata, ColumnMetadata, DataType,
    Validator, ValidationRule,
    LengthCheck, ValidValuesCheck, ComparisonCheck, ComparisonOperator,
)

metadata = AssetMetadata(table_name="employees", columns=[
    ColumnMetadata("emp_id", DataType.INTEGER),
    ColumnMetadata("name", DataType.STRING, length=100),
    ColumnMetadata("department", DataType.STRING, length=50),
    ColumnMetadata("age", DataType.INTEGER),
])

validator = Validator(metadata)
validator.add_rule(ValidationRule("name").add_check(LengthCheck(min_length=2, max_length=100)))
validator.add_rule(ValidationRule("department").add_check(
    ValidValuesCheck(["Engineering", "Sales", "HR"], case_sensitive=False)))
validator.add_rule(ValidationRule("age").add_check(
    ComparisonCheck(operator=ComparisonOperator.GREATER_THAN_OR_EQUAL, target_value=18)))

result  = validator.validate(record)          # single record (array of values)
results = validator.validate_batch(records)   # list of records
```

**The 9 checks** (params in the reference): `LengthCheck`, `ValidValuesCheck`,
`ComparisonCheck`, `CaseCheck`, `CompletenessCheck`, `RangeCheck`, `RegexCheck`,
`FormatCheck`, `DataTypeCheck`. Plus **CEL** checks for custom logic.

**Records are arrays** — a record is a list of values in **column order** from the
metadata, not a dict. Order matters.

**Data Quality Dimensions** — every check carries one of 8 dimensions (Accuracy,
Completeness, Conformity, Consistency, Coverage, Timeliness, Uniqueness,
Validity), used for dimension-level reporting. Defaults are sensible
(`CompletenessCheck`→COMPLETENESS, `CaseCheck`→CONSISTENCY, most others→VALIDITY);
override with `check.set_dimension(DataQualityDimension.CONFORMITY)`.

**Results** — `ValidationResult`: `.is_valid`, `.score` ("5/5"), `.pass_rate`,
`.total_checks`, `.passed_checks`, `.failed_checks`, `.errors` (list of
`ValidationError` with `.column_name`, `.check_name`, `.message`, `.value`,
`.expected`). `.to_dict()` on both.

### CEL — custom and cross-column rules

For logic the built-in checks can't express, use **CEL** (Common Expression
Language — safe, non-Turing-complete). Two flavors; full cheatsheet:
**[references/cel-expressions.md](references/cel-expressions.md)**.

- **Column-level** `CELCheck('value > min_salary')` on a `ValidationRule(col)` —
  has the `value` variable (the current column) plus direct access to other
  columns by name.
- **Table-level** `TableCELCheck('start_date < end_date')` on a
  `TableValidationRule(name)` via `validator.add_table_rule(...)` — validates the
  **whole record**, **no `value` variable**.

CEL **column names are case-sensitive**; expressions must return boolean; max 1000
chars; needs `cel-python`. Validate references early with
`check.validate_column_references([c.name for c in metadata.columns])`.

---

## 4. DataFrame integration — Pandas & PySpark

Same validator, wrapped for DataFrames (extras `[pandas]` / `[spark]`). Full method
list: **[references/dataframe-integration.md](references/dataframe-integration.md)**.

```python
from wxdi.dq_validator.integrations import PandasValidator   # or SparkValidator
pv = PandasValidator(validator, chunk_size=10000)            # SparkValidator(validator)
summary  = pv.get_summary_statistics(df)                     # {'pass_rate': …, …}
df2      = pv.add_validation_column(df)                       # adds dq_validation_result struct
invalid  = pv.get_invalid_rows(df)
expanded = pv.expand_validation_column(df2)                   # dq_is_valid, dq_score, dq_pass_rate, …
```

- **Pandas** = chunked, memory-efficient (O(chunk_size)); **Spark** = distributed
  UDFs, scales to billions of rows, plus `write_validation_report(...)` and
  `get_error_sample(...)`.
- The result struct column (`dq_` prefix, configurable) holds `is_valid`, `score`,
  `pass_rate`, `total_checks`, `passed_checks`, `failed_checks`, `error_count`,
  `errors`.

---

## 5. REST providers — connect to Cloud Pak for Data

The providers (`wxdi.dq_validator.provider`) read/write live DQ metadata on the
platform. Configure once with `ProviderConfig`, then use each provider. Full
catalog + methods: **[references/rest-providers.md](references/rest-providers.md)**.

```python
from wxdi.dq_validator.provider import ProviderConfig
from wxdi.common.auth import AuthConfig, EnvironmentType

cfg = ProviderConfig(
    url="https://<cpd-instance>.cloud.ibm.com",
    auth_config=AuthConfig(environment_type=EnvironmentType.IBM_CLOUD, api_key="…"),
    project_id="…",          # or catalog_id
)
```

| Provider | Purpose |
|----------|---------|
| `GlossaryProvider` | Fetch glossary terms / DQ constraints |
| `CamsProvider` | Fetch a data asset (+ column info) from CAMS |
| `DQAssetsProvider` | List assets with filtering + pagination |
| `ChecksProvider` | Create / list DQ checks |
| `DimensionsProvider` | Resolve a dimension id by name |
| `IssuesProvider` | Create single/bulk DQ issue occurrences; update metrics |
| `DQSearchProvider` | Find a DQ check / asset by native id |

Pass `auth_config=` (not a static `auth_token`) so tokens refresh automatically;
if both are given, `auth_config` wins. Providers are thread-safe (thread-local
sessions). A typical loop: resolve asset (CAMS) → resolve dimension → create check
→ report issues from a validation run (see `examples/dq_workflow_usage.py`).

---

## 6. Data Product Hub (DPH Services)

`DphV1` is the Python client for the IBM Data Product Hub API — manage data
products through their lifecycle. Full method list + JSON-patch update pattern:
**[references/dph-services.md](references/dph-services.md)**.

```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from wxdi.dph_services import DphV1

svc = DphV1(authenticator=IAMAuthenticator("…"))
svc.set_service_url("https://<dph-instance>")
svc.initialize(include=["delivery_methods", "data_product_samples", "domains_multi_industry"])

dp = svc.create_data_product(drafts=[{
    "version": "1.0.0", "name": "Customer Analytics",
    "asset": {"id": "asset-123", "container": {"id": "container-456"}},
}])
```

Lifecycle: **initialize container → create data product (with a draft) → edit
draft → publish draft → manage releases (update / retire)**. Also: contract terms
& documents, domains/subdomains, contract templates, asset visualizations.
**Updates use JSON-Patch** (`json_patch_instructions=[{"op":"replace","path":…,"value":…}]`).
List endpoints have `_with_pager` variants for pagination. Errors raise
`ibm_cloud_sdk_core.ApiException` (`.code`, `.message`).

---

## 7. ODCS Generator — data contracts from catalogs

Generate **ODCS v3.1.0** (Open Data Contract Standard) YAML from a catalog asset,
as a CLI module or programmatically. Full options, type mappings, and field
mappings: **[references/odcs-and-recommender.md](references/odcs-and-recommender.md)**.

```bash
# Collibra
python -m wxdi.odcs_generator.generate_odcs_from_collibra <asset_id> -o contract.yaml
# Informatica CDGC
python -m wxdi.odcs_generator.generate_odcs_from_informatica <asset_id> -o contract.yaml
```

Credentials via env vars (`COLLIBRA_URL/USERNAME/PASSWORD`,
`INFORMATICA_CDGC_URL/USERNAME/PASSWORD`) or `-u/-p/--url`. Output is
`<asset-name>-odcs.yaml`.

**Always review the generated YAML before use.** The generators **cannot infer
server connection details** — `server: CONFIGURE_SERVER_HOSTNAME` and (for
Collibra) `type: DEFINE_SERVER_TYPE` are placeholders flagged with `⚠️ MANUAL
CONFIGURATION REQUIRED` comments that you must complete. Informatica auto-detects
the server `type` from the resource type; Collibra does not. Only **table/view**
assets are supported.

---

## 8. Data Product Recommender — mine query logs

Analyze **pre-exported** query-log files (no DB connection) to rank high-value
tables and table groups as data-product candidates. CLI or Python; full scoring
methodology and per-platform export SQL:
**[references/odcs-and-recommender.md](references/odcs-and-recommender.md)**.

```python
from wxdi.data_product_recommender.platforms import SnowflakeQueryParser
from wxdi.data_product_recommender.recommender import DataProductRecommender

rec = DataProductRecommender(SnowflakeQueryParser())
rec.load_query_logs_from_csv_file("query_logs.csv")
rec.calculate_metrics()
recs = rec.recommend_data_products(num_recommendations=20)
rec.export_recommendations_markdown(recs, "output/recommendations.md")   # or _json
```

Platforms: Snowflake, Databricks, BigQuery, watsonx.data (Presto). Input needs at
least `query_text`, `user`, `start_time`. Output: Markdown (human) or JSON
(agent-consumable) with 0–100 scores and ⭐ ratings. **Query logs are sensitive**
(user identities, table names) — handle securely.

---

## 9. Critical constraints (these cause silent failures — internalize them)

- ✅ **Records are arrays in metadata column order** — not dicts. Wrong order =
  wrong column validated.
- ✅ **Column names are case-sensitive everywhere** — rules, `ValidValuesCheck`,
  and CEL. `salary` ≠ `Salary`.
- ✅ **CEL expressions must return boolean**, ≤1000 chars, need `cel-python`;
  reserved names (`value`, `record`, `column_name`, `record_index`) require the
  `record.` prefix to access a same-named column.
- ✅ **`LengthCheck` stringifies first** — `12345` → `"12345"` (length 5). None
  fails most checks; allow it explicitly with `CompletenessCheck(missing_values_allowed=True)`.
- ✅ **DataFrame support is an extra** — `pip install ".[pandas]"` / `".[spark]"`;
  importing `integrations` without it fails.
- ✅ **DPH auth ≠ wxdi auth** — DPH uses `ibm_cloud_sdk_core` `IAMAuthenticator`
  and `set_service_url`; the rest use `wxdi.common.auth`.
- ✅ **DPH updates are JSON-Patch**, not full objects.
- ✅ **ODCS output needs manual server config** — never ship the
  `CONFIGURE_SERVER_HOSTNAME` / `DEFINE_SERVER_TYPE` placeholders.
- ✅ **Recommender needs exported files**, not a live DB; required columns
  `query_text`, `user`, `start_time`.
- ✅ **Verify symbols against the installed SDK** when a class/enum/field is in
  doubt (golden rule #2).

---

## 10. Debugging playbook

| Symptom | Likely cause → fix |
|---------|--------------------|
| Validation passes/fails the wrong field | Record array out of metadata order, or case-mismatched column name. Align the array to `metadata.columns`; use exact names. |
| `CELCompilationError` at check creation | Bad CEL syntax. Fix the expression; it compiles eagerly. |
| CEL "column not found" | Case mismatch or missing column. `check.validate_column_references([c.name for c in metadata.columns])`. |
| Can't access a column named `value`/`record` | Reserved CEL name. Use `record.value`. |
| `ImportError` on `integrations` / CEL | Missing extra. `pip install ".[pandas]"`/`".[spark]"` / `"cel-python>=0.5.0"`. |
| `AuthConfig` TypeError on a field | Field name differs by version (`environment` vs `environment_type`). Introspect `wxdi.common.auth.AuthConfig`. |
| Provider 401/403 | Stale/missing token or wrong `project_id`/`catalog_id`. Use `auth_config=` for auto-refresh; verify scope. |
| DPH `ApiException` | Inspect `.code`/`.message`; for updates ensure JSON-Patch shape; confirm `set_service_url`. |
| ODCS has no columns | Catalog relations/hierarchy incomplete, or asset isn't a table/view. Check the source catalog. |
| ODCS server block has placeholders | Expected — fill `CONFIGURE_SERVER_HOSTNAME`/`DEFINE_SERVER_TYPE` before use. |
| Recommender empty / errors | Missing required columns or wrong `--platform`. Ensure `query_text`/`user`/`start_time` and the matching parser. |

Diagnose and propose a fix — never pass a raw stack trace through. When a symbol
is uncertain, introspect the installed SDK rather than guessing.

---

## 11. References (load on demand)

| File | Contents |
|------|----------|
| [references/authentication.md](references/authentication.md) | All 4 environments, `AuthConfig`/`AuthProvider.get_token()`, on-prem/Gov specifics, using tokens, DPH auth |
| [references/dq-checks-reference.md](references/dq-checks-reference.md) | The 9 checks (params, edge cases), DQ dimensions, `ValidationResult`/`ValidationError`, metadata/`DataType` |
| [references/cel-expressions.md](references/cel-expressions.md) | Column- vs table-level CEL, variables, operators, ternaries, reserved names, limits, worked examples |
| [references/dataframe-integration.md](references/dataframe-integration.md) | `PandasValidator` / `SparkValidator` methods, result struct, memory/scaling notes |
| [references/rest-providers.md](references/rest-providers.md) | `ProviderConfig` + every provider (Glossary, CAMS, Assets, Checks, Dimensions, Issues, DQSearch) with signatures |
| [references/dph-services.md](references/dph-services.md) | `DphV1` full method catalog, lifecycle, JSON-Patch updates, pagination, error handling |
| [references/odcs-and-recommender.md](references/odcs-and-recommender.md) | ODCS generation (Collibra/Informatica: options, type/field mappings, manual config) + recommender (scoring, platforms, export SQL) |

### Canonical external resources (you have internet access — use them)
- **SDK source & examples:** the `data-intelligence-sdk` repo (`examples/` has runnable scripts per module: `basic_usage`, `cel_usage`, `pandas/spark_dataframe_usage`, `dq_workflow_usage`, `glossary/checks/issues/dimensions_usage`, `odcs_generator_example`, `data_product_recommender_example`)
- **ODCS spec v3.1.0:** https://github.com/bitol-io/open-data-contract-standard
- **CEL spec:** https://github.com/google/cel-spec

When a class, enum, or field name is uncertain, **introspect the installed SDK**
(`dir(...)`, `help(...)`) rather than guessing — the surest source of truth.
