# Setup & Authentication — `Credentials`, `APIClient`, extras

> Verified against `ibm-watsonx-gov` 1.5.0. When a field is in doubt, check the
> live docs (https://ibm.github.io/ibm-watsonx-gov/) or `help()`.

## The extras matrix (install what you use)

The base `ibm-watsonx-gov` package only gives you auth + entities. **Every
evaluator and the metric computations live behind optional extras.** A missing
extra surfaces as a `ModuleNotFoundError` at *import* time (e.g. `jsonschema`,
`nbformat`, `IPython`, `pkg_resources`).

| Extra | Enables | Install |
|---|---|---|
| `metrics` | `MetricsEvaluator` + metric computation | `pip install "ibm-watsonx-gov[metrics]"` |
| `agentic` | `AgenticEvaluator`, tracing, experiment tracking | `pip install "ibm-watsonx-gov[agentic]"` |
| `mre` | `ModelRiskEvaluator` | `pip install "ibm-watsonx-gov[mre]"` |
| `local-evals` | run certain metrics with local models (no judge call) — pairs with `metrics`/`agentic` | `pip install "ibm-watsonx-gov[local-evals]"` |
| `llmaj` | LLM-as-a-judge metric methods | `pip install "ibm-watsonx-gov[llmaj]"` |
| `tools` | tools while building agentic apps | `pip install "ibm-watsonx-gov[tools]"` |
| `visualization` | `Model Insights` / `display_insights()` | `pip install "ibm-watsonx-gov[visualization]"` |

Combine: `pip install "ibm-watsonx-gov[metrics,agentic]"`. `local-evals` requires
PyTorch-class deps and is heavy — only install when you need a local metric method.

`local-evals` metric methods (compute without a remote/judge call):

| Metric | Local method(s) |
|---|---|
| Answer Similarity | `bert_score_recall`, `sentence_bert_mini_lm` |
| Faithfulness | `sentence_bert_mini_lm` |
| Context Relevance | `sentence_bert_bge`, `sentence_bert_mini_lm` |

## `Credentials` — the full surface

`from ibm_watsonx_gov.entities.credentials import Credentials`
(also re-exported as `ibm_watsonx_gov.config.Credentials`).

Fields: `api_key`, `region`, `url`, `service_instance_id`, `username`,
`password`, `token`, `version`, `disable_ssl`, `scope_id`, `scope_collection_type`.

### SaaS (watsonx.governance as a Service)
- Auth with **`api_key`** (an IBM Cloud API key). Get it from the IBM Cloud
  console → API keys.
- **Region** defaults to Dallas (`us-south`). For another region pass
  `region=Region.<X>.value` or set `WATSONX_REGION`. Valid: `us-south`, `eu-de`,
  `au-syd`, `ca-tor`, `jp-tok`, `eu-gb` (the `Region` enum,
  `from ibm_watsonx_gov.entities.enums import Region`).
- If you have **multiple** governance instances, disambiguate with
  `service_instance_id` (or `WXG_SERVICE_INSTANCE_ID`).

```python
import os
from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import Region

os.environ["WATSONX_APIKEY"] = "..."        # never hardcode in source
credentials = Credentials(api_key=os.environ["WATSONX_APIKEY"])           # Dallas
# credentials = Credentials(region=Region.EU_DE.value, api_key=os.environ["WATSONX_APIKEY"])
api_client = APIClient(credentials=credentials)
```

### Cloud Pak for Data (software / on-prem)
- Auth with **`url`** (your CPD cluster host) + **`username`** + (`api_key` **or**
  `password`) + **`version`** (the two-digit CPD release, e.g. `"5.2"`).

```python
credentials = Credentials(
    url="https://<cpd_cluster_host>",
    username=os.environ["WATSONX_USERNAME"],
    api_key=os.environ["WATSONX_APIKEY"],   # or password=os.environ["WATSONX_PASSWORD"]
    version="5.2",
)
api_client = APIClient(credentials=credentials)
# disable_ssl=True only for non-production clusters with self-signed certs
```

## Environment variables

`APIClient` reads these **once** at first initialization. Change one afterward →
restart the Python process / notebook kernel for it to take effect.

| Variable | Purpose |
|---|---|
| `WATSONX_APIKEY` | API key (SaaS and CPD) |
| `WATSONX_REGION` | SaaS region (e.g. `Region.AU_SYD.value`); default Dallas |
| `WXG_SERVICE_INSTANCE_ID` | pick a specific governance instance (SaaS, optional) |
| `WATSONX_URL` | CPD cluster base URL |
| `WATSONX_USERNAME` | CPD username |
| `WATSONX_VERSION` | CPD release version (e.g. `5.2`) |
| `WATSONX_PASSWORD` | CPD password (alternative to `WATSONX_APIKEY`) |

If you only set `WATSONX_APIKEY` and pass no `api_client`, the evaluators build a
default SaaS client themselves — convenient for quick SaaS scripts.

## `APIClient`

`from ibm_watsonx_gov.clients.api_client import APIClient`

- `APIClient(credentials=Credentials(...))` — the object you pass into every
  evaluator as `api_client=...`.
- Exposes `.credentials`. Internally wraps the watsonx.governance (OpenScale /
  `WOSClient`) and watsonx.ai clients; you rarely touch those directly.

## Related credential classes

- **`WxAICredentials`** (`from ibm_watsonx_gov.config import WxAICredentials`) —
  credentials for a **watsonx.ai** model used *by* governance (e.g. an LLM judge
  or a model under risk test). Fields: `url`, `api_key`, `version`, `username`,
  `password`, `instance_id`.
- **`WxGovConsoleCredentials`** — for syncing model-risk results to the watsonx
  **Governance Console** (formerly OpenPages). Fields: `url`, `username`,
  `password`, `api_key`. See `model-risk-and-providers.md`.

> 🔒 Read every secret from an environment variable. Never hardcode or commit
> keys/passwords; don't print tokens; rotate if exposed.
