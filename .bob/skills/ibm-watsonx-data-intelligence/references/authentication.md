# Authentication Reference

The `wxdi` SDK generates Bearer tokens across four environments (SKILL.md §2).
Most modules use `wxdi.common.auth`; **DPH Services** use the IBM Cloud SDK core
authenticator instead.

## Supported environments

| Environment | `EnvironmentType` | Auth method | Credentials |
|-------------|-------------------|-------------|-------------|
| IBM Cloud (standard) | `IBM_CLOUD` | POST (form-encoded) | API key |
| AWS Cloud (MCSP) | `AWS_CLOUD` | POST (header-based) | API key |
| IBM Government Cloud | `GOV_CLOUD` | POST (JSON) | API key |
| On-Premises (CP4D) | `ON_PREM` | GET (headers) | user id + password |

## AuthConfig + AuthProvider (verified against wxdi 2.1.0)

```python
from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType
# AuthConfig / EnvironmentType are also re-exported from wxdi.dq_validator.

# IBM Cloud (production)
config = AuthConfig(
    environment_type=EnvironmentType.IBM_CLOUD,        # first positional arg
    url="https://iam.cloud.ibm.com/identity/token",
    api_key="your-api-key",
)
token = AuthProvider(config).get_token()               # -> JWT string
```

Real 2.1.0 signature (introspected live):
```
AuthConfig(environment_type, url=None, api_key=None, username=None,
           password=None, account_id=None, disable_ssl_verification=True)
```
`EnvironmentType` members: `IBM_CLOUD`, `AWS_CLOUD`, `GOV_CLOUD`, `ON_PREM`.

Per-environment `url` values:
- **IBM Cloud:** `https://iam.cloud.ibm.com/identity/token`
- **AWS (MCSP):** `https://account-iam.platform.<...>.ibm.com/api/2.0/accounts/<account-id>/apikeys/token`
- **Gov Cloud:** `https://dai.ibmforusgov.com/api/rest/mcsp/apikeys/token`
- **On-prem:** `https://<host>:<port>/v1/preauth/validateAuth` with
  `user_id=` + `password=` instead of `api_key=`.

```python
# On-prem (CP4D) — username/password instead of api_key
config = AuthConfig(environment_type=EnvironmentType.ON_PREM,
                    url="https://localhost:8443/v1/preauth/validateAuth",
                    username="admin", password="…")
token = AuthProvider(config).get_token()
```

## Using the token

`get_token()` returns the raw JWT string. Add the `Bearer ` prefix for HTTP headers:
```python
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
requests.get("https://api.example.com/endpoint", headers=headers)
```

## Version drift — verify before relying (golden rule #2)

The upstream README's quick-start shows a `TokenGenerator` class and an
`AuthConfig(url=…, environment=…)` shape — **both are stale**; they do not exist in
2.1.0. The verified path is `AuthProvider(AuthConfig(environment_type=…)).get_token()`.
If you're on a different version, introspect before using:
```python
import inspect, wxdi.common.auth as a
print([n for n in dir(a) if not n.startswith("_")])   # AuthConfig, AuthProvider, EnvironmentType, ...
print(inspect.signature(a.AuthConfig.__init__))
```
For providers, prefer `auth_config=` so tokens refresh automatically (see
`references/rest-providers.md`).

## DPH Services auth (different)

Data Product Hub uses `ibm_cloud_sdk_core`, not `wxdi.common.auth`:
```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from wxdi.dph_services import DphV1
svc = DphV1(authenticator=IAMAuthenticator("your-api-key"))
svc.set_service_url("https://<dph-instance>")
```

## Security

Keep API keys / passwords in environment variables or a secret store — never in
source or chat history. SSL verification is configurable for on-prem instances.
