# IBM watsonx.data intelligence — Agent Skill

Equip any skills-compatible Bob AI agent to use the **IBM watsonx.data intelligence Python SDK** (`wxdi`,
package `data-intelligence-sdk`) correctly — for data-quality validation, data
products, data contracts, and recommendations.

> A Python SDK (not an MCP/CLI service). Built on the verified `wxdi` SDK (2.1.x)
> source and docs.

## What it does

| Capability | Use it for |
|------------|------------|
| **DQ validation** | Validate records, Pandas, and PySpark DataFrames against 9 checks + CEL rules, tracked by 8 DQ dimensions |
| **REST providers** | Read/write live DQ metadata in Cloud Pak for Data (glossary, CAMS assets, checks, dimensions, issues) |
| **Data Product Hub** | Manage data products, drafts, releases, contract terms, domains, and templates via `DphV1` |
| **ODCS generation** | Generate ODCS v3.1.0 data-contract YAML from Collibra / Informatica catalogs |
| **Recommendations** | Rank high-value tables/groups as data products from query logs |

## Why it's reliable

- **Define metadata once, exactly.** Records are arrays in column order; column
  names are case-sensitive everywhere (rules, valid-values, CEL) — the top
  failure mode, called out throughout.
- **Right auth per surface.** Four environments via `wxdi.common.auth`
  (`EnvironmentType` + `AuthConfig`/`AuthProvider`); Data Product Hub uses the
  IBM Cloud SDK `IAMAuthenticator` instead — the skill keeps them distinct.
- **Carries the traps.** DataFrame support is an install extra; CEL must return
  boolean and reserves `value`/`record`; DPH updates are JSON-Patch; ODCS output
  needs manual server config; the recommender needs exported files, not a live DB.
- **Verify-against-installed-SDK discipline.** Where a class/enum/field name has
  drifted across versions (e.g. `AuthConfig`), the skill says to introspect rather
  than guess.

## Install

Copy the `watsonx-data-intelligence/` folder into your agent's skills directory:

```bash
cp -r watsonx-data-intelligence ~/.bob/skills/
```

Then install the SDK in your environment:
```bash
pip install data-intelligence-sdk          # core
pip install "data-intelligence-sdk[all]"   # + Pandas, PySpark, dev
pip install "cel-python>=0.5.0"            # for CEL rules
```

## Structure

```
watsonx-data-intelligence/
├── SKILL.md                              # the skill — 11 sections, loaded by the agent
├── README.md                             # this listing
└── references/                           # loaded on demand
    ├── authentication.md                  # 4 environments + DPH auth
    ├── dq-checks-reference.md             # the 9 checks, dimensions, results
    ├── cel-expressions.md                 # column- & table-level CEL
    ├── dataframe-integration.md           # Pandas / PySpark validators
    ├── rest-providers.md                  # CPD providers + ProviderConfig
    ├── dph-services.md                    # DphV1 full API
    └── odcs-and-recommender.md            # ODCS generation + recommender
```

## Requirements

- Python 3.8–3.12 (DPH module: 3.10+). Core deps `pydantic>=2.12`, `requests`,
  `regex`; optional `pandas`, `pyspark`, `cel-python`.
- For platform features: a watsonx.data intelligence / Cloud Pak for Data instance
  and credentials (IBM Cloud / AWS MCSP / Gov Cloud / on-prem).

## License

Adapted from IBM's `data-intelligence-sdk` (Apache License 2.0).
